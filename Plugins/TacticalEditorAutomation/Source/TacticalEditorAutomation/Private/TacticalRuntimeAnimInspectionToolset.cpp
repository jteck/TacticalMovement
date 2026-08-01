// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalRuntimeAnimInspectionToolset.h"

#include "Containers/Ticker.h"
#include "Containers/Set.h"
#include "Containers/StringConv.h"
#include "Misc/Guid.h"
#include "HAL/PlatformTime.h"
#include "Math/Vector2D.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/WeakObjectPtr.h"
#include "UObject/WeakObjectPtrTemplates.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/UnrealType.h"
#include "UObject/UObjectIterator.h"
#include "UObject/Class.h"

#include "Engine/Engine.h"
#include "Engine/World.h"
#include "Engine/EngineTypes.h"
#include "Engine/LocalPlayer.h"
#include "Editor.h"

#include "Engine/Blueprint.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/CapsuleComponent.h"
#include "Animation/AnimInstance.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/Character.h"
#include "GameFramework/Actor.h"
#include "GameFramework/Controller.h"
#include "GameFramework/PlayerController.h"

#include "EnhancedInputSubsystems.h"
#include "EnhancedInputSubsystemInterface.h"
#include "InputAction.h"
#include "InputActionValue.h"

#include "ToolsetRegistry/ToolCallAsyncResultString.h"
#include "ToolsetRegistry/ToolsetImage.h"

#include "Components/SceneCaptureComponent2D.h"
#include "Engine/TextureRenderTarget2D.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetRenderingLibrary.h"
#include "Engine/Canvas.h"
#include "Camera/CameraTypes.h"
#include "SceneView.h"
#include "Engine/Scene.h"
#include "TextureResource.h"
#include "RenderingThread.h"
#include "RHIDefinitions.h"

// =============================================================================
// Internal helpers + module-owned capture/drive state (all game-thread only).
// =============================================================================
namespace TacticalRuntimeAnimInspection
{
	// ---- documented hard bounds (conservative, sufficient for E0) ----
	static const int32  kMaxSamplesLimit = 10000;
	static const double kMaxTimeoutSeconds = 300.0;
	static const int32  kMaxPropertiesPerSide = 64;         // per host / per layer list
	static const int32  kMaxPropertyNameLen = 128;          // characters
	static const int64  kMaxSampleBytes = 8LL * 1024 * 1024; // 8 MiB accumulated sample JSON / session
	static const double kReadinessPressHoldSeconds = 0.1;
	static const float  kLifecycleTickInterval = 0.05f;
	static const int32  kMaxSocketNames = 256;              // introspection: max socket names returned per component

	// ---- deferred one-shot string result (same pattern as the authoring toolset) ----
	static UToolCallAsyncResultString* RunDeferredString(TFunction<bool(FString&, FString&)>&& Action)
	{
		UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();
		TStrongObjectPtr<UToolCallAsyncResultString> StrongResult(Result);
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[StrongResult, Action = MoveTemp(Action)](float) mutable -> bool
			{
				FString Value, Error;
				if (Action(Value, Error)) { StrongResult->SetValue(Value); }
				else { StrongResult->SetError(Error); }
				StrongResult.Reset();
				return false; // one-shot
			}));
		return Result;
	}

	static FString JsonEscape(const FString& In)
	{
		FString Out; Out.Reserve(In.Len() + 8);
		for (TCHAR C : In)
		{
			switch (C)
			{
			case TEXT('\\'): Out += TEXT("\\\\"); break;
			case TEXT('\"'): Out += TEXT("\\\""); break;
			case TEXT('\n'): Out += TEXT("\\n"); break;
			case TEXT('\r'): Out += TEXT("\\r"); break;
			case TEXT('\t'): Out += TEXT("\\t"); break;
			default: Out += C; break;
			}
		}
		return Out;
	}
	static FString JStr(const FString& In) { return FString::Printf(TEXT("\"%s\""), *JsonEscape(In)); }

	static bool NumberToJson(double V, FString& Out)
	{
		if (!FMath::IsFinite(V)) { return false; }
		Out = FString::Printf(TEXT("%.9g"), V);
		return true;
	}

	static bool IsPIEWorld(const UWorld* W) { return W && W->WorldType == EWorldType::PIE; }

	static bool IsUsableMesh(const USkeletalMeshComponent* Mesh)
	{
		return IsValid(Mesh) && !Mesh->IsTemplate() && Mesh->IsRegistered() && IsPIEWorld(Mesh->GetWorld());
	}

	static bool IsUsableAnimInstance(const UAnimInstance* Inst)
	{
		return IsValid(Inst) && !Inst->IsTemplate();
	}

	// PUBLIC const overload of GetLinkedAnimInstances (the non-const overload is private).
	static const TArray<UAnimInstance*>& GetLinkedInstances(const USkeletalMeshComponent* Mesh)
	{
		return Mesh->GetLinkedAnimInstances();
	}

	static bool LayerStillPresent(const USkeletalMeshComponent* Mesh, const UAnimInstance* Layer)
	{
		for (const UAnimInstance* L : GetLinkedInstances(Mesh)) { if (L == Layer) { return true; } }
		return false;
	}

	// Reads a single scalar (double/float/bool) property as a JSON value string.
	static bool ReadScalarJson(UObject* Inst, const FString& PropName, FString& OutJsonValue, FString& OutError)
	{
		check(IsInGameThread());
		FProperty* P = Inst->GetClass()->FindPropertyByName(FName(*PropName));
		if (!P) { OutError = TEXT("missing property"); return false; }
		if (const FDoubleProperty* DP = CastField<FDoubleProperty>(P))
		{
			if (!NumberToJson(DP->GetPropertyValue_InContainer(Inst), OutJsonValue)) { OutError = TEXT("non-finite value"); return false; }
			return true;
		}
		if (const FFloatProperty* FP = CastField<FFloatProperty>(P))
		{
			if (!NumberToJson((double)FP->GetPropertyValue_InContainer(Inst), OutJsonValue)) { OutError = TEXT("non-finite value"); return false; }
			return true;
		}
		if (const FBoolProperty* BP = CastField<FBoolProperty>(P))
		{
			OutJsonValue = BP->GetPropertyValue_InContainer(Inst) ? TEXT("true") : TEXT("false");
			return true;
		}
		OutError = FString::Printf(TEXT("unsupported property type '%s' (only float/double/bool)"), *P->GetClass()->GetName());
		return false;
	}

	static FString ReadPropertyAsText(UObject* Inst, const FString& PropName)
	{
		if (!IsValid(Inst)) { return FString(); }
		FProperty* P = Inst->GetClass()->FindPropertyByName(FName(*PropName));
		if (!P) { return FString(); }
		FString Out;
		const void* ValuePtr = P->ContainerPtrToValuePtr<void>(Inst);
		P->ExportTextItem_Direct(Out, ValuePtr, nullptr, Inst, PPF_None);
		return Out;
	}

	static UClass* ResolveAnimInstanceClass(const FString& Path)
	{
		if (UClass* C = LoadClass<UAnimInstance>(nullptr, *Path)) { return C; }
		if (UObject* Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *Path))
		{
			if (UClass* AsClass = Cast<UClass>(Obj)) { return AsClass->IsChildOf(UAnimInstance::StaticClass()) ? AsClass : nullptr; }
			if (UBlueprint* BP = Cast<UBlueprint>(Obj))
			{
				UClass* Gen = BP->GeneratedClass;
				return (Gen && Gen->IsChildOf(UAnimInstance::StaticClass())) ? Gen : nullptr;
			}
		}
		return nullptr;
	}

	static AActor* ResolveActor(const FString& Path)
	{
		return Cast<AActor>(StaticFindObject(AActor::StaticClass(), nullptr, *Path));
	}

	static USkeletalMeshComponent* ResolveMeshComponent(const FString& Path)
	{
		return Cast<USkeletalMeshComponent>(StaticFindObject(USkeletalMeshComponent::StaticClass(), nullptr, *Path));
	}

	// Generic scene-component resolver (weapon component may be static-mesh or any USceneComponent).
	static USceneComponent* ResolveSceneComponent(const FString& Path)
	{
		return Cast<USceneComponent>(StaticFindObject(USceneComponent::StaticClass(), nullptr, *Path));
	}

	// ---- raw world-transform JSON helpers (Boundary G): serialize Epic values verbatim, no math ----
	static FString VecJson(const FVector& V) { return FString::Printf(TEXT("{\"x\":%.6f,\"y\":%.6f,\"z\":%.6f}"), V.X, V.Y, V.Z); }
	static FString RotJson(const FRotator& R) { return FString::Printf(TEXT("{\"pitch\":%.6f,\"yaw\":%.6f,\"roll\":%.6f}"), R.Pitch, R.Yaw, R.Roll); }
	static FString QuatJson(const FQuat& Q) { return FString::Printf(TEXT("{\"x\":%.9f,\"y\":%.9f,\"z\":%.9f,\"w\":%.9f}"), Q.X, Q.Y, Q.Z, Q.W); }
	static FString XformJson(const FTransform& T)
	{
		return FString::Printf(TEXT("{\"location\":%s,\"rotation\":%s,\"quat\":%s,\"scale\":%s}"),
			*VecJson(T.GetLocation()), *RotJson(T.Rotator()), *QuatJson(T.GetRotation()), *VecJson(T.GetScale3D()));
	}

	static const TCHAR* NetRoleStr(ENetRole R)
	{
		switch (R)
		{
		case ROLE_None:            return TEXT("ROLE_None");
		case ROLE_SimulatedProxy:  return TEXT("ROLE_SimulatedProxy");
		case ROLE_AutonomousProxy: return TEXT("ROLE_AutonomousProxy");
		case ROLE_Authority:       return TEXT("ROLE_Authority");
		default:                   return TEXT("ROLE_Unknown");
		}
	}

	// Rejects: too many names, empty names, over-long names, and duplicates within a single list.
	static bool ValidatePropertyList(const TArray<FString>& Props, const TCHAR* Which, FString& OutError)
	{
		if (Props.Num() > kMaxPropertiesPerSide)
		{
			OutError = FString::Printf(TEXT("%s has %d properties; the maximum is %d."), Which, Props.Num(), kMaxPropertiesPerSide);
			return false;
		}
		TSet<FString> Seen;
		for (const FString& P : Props)
		{
			if (P.IsEmpty()) { OutError = FString::Printf(TEXT("%s contains an empty property name."), Which); return false; }
			if (P.Len() > kMaxPropertyNameLen) { OutError = FString::Printf(TEXT("%s contains a property name of length %d; the maximum is %d."), Which, P.Len(), kMaxPropertyNameLen); return false; }
			if (Seen.Contains(P)) { OutError = FString::Printf(TEXT("%s contains a duplicate property name '%s'."), Which, *P); return false; }
			Seen.Add(P);
		}
		return true;
	}

	// -------------------------------------------------------------------------
	// Capture session (module-owned; weak refs to all PIE UObjects).
	// -------------------------------------------------------------------------
	struct FCaptureSession
	{
		FString Id;
		TWeakObjectPtr<UWorld> World;
		TWeakObjectPtr<USkeletalMeshComponent> Mesh;
		TWeakObjectPtr<UAnimInstance> Host;
		TWeakObjectPtr<UAnimInstance> Layer;
		TWeakObjectPtr<UClass> ExpectedHostClass;
		TWeakObjectPtr<UClass> ExpectedLayerClass;
		FString WorldName, OwnerPath, MeshPath, HostInstPath, HostClass, LayerInstPath, LayerClass;
		TArray<FString> HostProps;
		TArray<FString> LayerProps;
		int32 MaxSamples = 1;
		double Timeout = 0.0;
		double StartTime = 0.0;
		FDelegateHandle FinalizeHandle;
		FTSTicker::FDelegateHandle LifecycleHandle;
		TArray<FString> Samples;
		int64 AccumBytes = 0;   // accumulated serialized sample JSON bytes (UTF-8)
		bool bActive = false;
		FString StopReason;

		// --- transform-capture mode (Boundary G): reuses THIS session + OnBoneTransformsFinalized ---
		bool bTransformMode = false;
		TWeakObjectPtr<APawn> Pawn;
		TWeakObjectPtr<USceneComponent> TransformSource;  // socket/world-transform source (weapon comp or the mesh itself)
		TWeakObjectPtr<USceneComponent> Capsule;          // pawn capsule/root component (world rotation source)
		FString PawnPath, TransformSourcePath, SocketName, CapsulePath;
	};

	// Active input-drive state (module-owned) so the caller is ALWAYS resolved exactly once and any
	// continuous input injection is force-stopped on every path.
	struct FDriveState
	{
		TStrongObjectPtr<UToolCallAsyncResultString> Result;
		bool bResolved = false;

		TWeakObjectPtr<APawn> Pawn;
		TWeakObjectPtr<UEnhancedInputLocalPlayerSubsystem> Subsystem;
		TWeakObjectPtr<UInputAction> ReadinessAction;
		TWeakObjectPtr<UInputAction> MoveAction;

		FString PawnPath, ReadinessActionProperty, MoveActionProperty;
		bool bReadinessRequested = false;
		bool bMoveRequested = false;
		FString ReadinessBefore;
		double SpeedBefore = 0.0;
		double MaxSpeed = 0.0;

		bool bReadinessInjecting = false;
		bool bMoveInjecting = false;
		bool bReadinessInjectionStarted = false;
		bool bReadinessInjectionStopped = false;
		bool bMoveInjectionStarted = false;
		bool bMoveInjectionStopped = false;

		double T0 = 0.0, PressAt = 0.0, ReleaseAt = 0.0, MoveStartAt = 0.0, MoveStopAt = 0.0;
		double TimeoutSeconds = 0.0;
		float MoveX = 0.f, MoveY = 0.f;

		TArray<FString> Steps;
		FTSTicker::FDelegateHandle TickHandle;
	};

	// Non-owner pawn-view capture session (module-owned; separate transient capture actor/component/RT).
	struct FViewCaptureSession
	{
		TStrongObjectPtr<UToolCallAsyncResultString> Result;
		bool bResolved = false;
		FString PawnPath, MeshPath, WorldName;
		FVector CamOffset = FVector::ZeroVector;
		FVector LookAtOffset = FVector::ZeroVector;
		int32 Width = 0, Height = 0;
		double Fov = 90.0;
		double Timeout = 0.0;
		double StartTime = 0.0;
		int32 Phase = 0;            // 0 = validate/spawn, 1 = wait-a-frame then capture
		int32 FramesSinceSpawn = 0;
		TWeakObjectPtr<UWorld> World;
		TWeakObjectPtr<APawn> Pawn;
		TWeakObjectPtr<USkeletalMeshComponent> Mesh;
		TStrongObjectPtr<AActor> CaptureActor;
		TStrongObjectPtr<USceneCaptureComponent2D> Capture;
		TStrongObjectPtr<UTextureRenderTarget2D> RT;
		FTSTicker::FDelegateHandle TickHandle;
		// ---- A1 projection extension (unused by CapturePIEPawnViewDeferred) ----
		bool bProjection = false;
		bool bAnnotate = false;
		double AxisLength = 0.0;
		TArray<FString> TargetComponentPaths;
		TArray<FString> TargetSocketNames;
	};

	// ---- view-capture hard bounds ----
	static const int32  kMaxConcurrentViewCaptures = 1;    // at most one active pawn-view capture session
	static const int32  kViewMinDim = 64;
	static const int32  kViewMaxDim = 1920;
	static const int64  kViewMaxPixels = 4000000;
	static const double kViewFovMin = 5.0;
	static const double kViewFovMax = 170.0;
	static const double kViewOffsetMax = 100000.0;
	static const double kViewMinCamTargetDist = 1.0;       // reject coincident camera/look-at vectors
	static const double kViewTimeoutMax = 60.0;
	static const int32  kMaxProjectionTargets = 32;      // component/socket pairs per projected capture
	static const int32  kMaxComponentPathLen = 512;      // characters, checked BEFORE object resolution
	static const int32  kMaxSocketNameLenProj = 128;     // characters, checked BEFORE FName construction
	static const double kMaxAxisLength = 200.0;          // cm
	// The approved bound is on the COMPLETE returned result: the whole projected response,
	// measured in UTF-8 bytes, must not exceed 12 MiB. (The per-image Base64 precheck above is a
	// cheap early-out; this is the rule that actually governs what may be returned.)
	static const int32  kMaxResponseBytes = 12 * 1024 * 1024;
	static const int32  kMaxProjectionJsonBytes = 256 * 1024; // matrices + targets JSON, UTF-8 bytes
	static const int32  kViewMaxEncodedBytes = 12 * 1024 * 1024; // 12 MiB Base64 image DATA string (ASCII: Len()==UTF-8 bytes)

	static TMap<FString, TSharedPtr<FCaptureSession>> GSessions;
	static TArray<TSharedPtr<FDriveState>> GDrives;
	static TArray<TSharedPtr<FViewCaptureSession>> GViewCaptures;
	static bool GHooksRegistered = false;
	static FDelegateHandle GEndPIEHandle;
	static FDelegateHandle GWorldCleanupHandle;

	static void StopSession(const TSharedPtr<FCaptureSession>& S, const FString& Reason)
	{
		if (!S.IsValid()) { return; }
		if (S->bActive)
		{
			if (USkeletalMeshComponent* Mesh = S->Mesh.Get()) { Mesh->UnregisterOnBoneTransformsFinalizedDelegate(S->FinalizeHandle); }
			S->FinalizeHandle.Reset();
			if (S->LifecycleHandle.IsValid()) { FTSTicker::GetCoreTicker().RemoveTicker(S->LifecycleHandle); S->LifecycleHandle.Reset(); }
			S->bActive = false;
			if (S->StopReason.IsEmpty()) { S->StopReason = Reason; }
		}
	}

	static void StopDriveInjection(const TSharedPtr<FDriveState>& D)
	{
		if (!D.IsValid()) { return; }
		if (UEnhancedInputLocalPlayerSubsystem* Sub = D->Subsystem.Get())
		{
			if (D->bReadinessInjecting) { if (UInputAction* A = D->ReadinessAction.Get()) { Sub->StopContinuousInputInjectionForAction(A); } D->bReadinessInjectionStopped = true; }
			if (D->bMoveInjecting) { if (UInputAction* A = D->MoveAction.Get()) { Sub->StopContinuousInputInjectionForAction(A); } D->bMoveInjectionStopped = true; }
		}
		D->bReadinessInjecting = false;
		D->bMoveInjecting = false;
		if (D->TickHandle.IsValid()) { FTSTicker::GetCoreTicker().RemoveTicker(D->TickHandle); D->TickHandle.Reset(); }
	}

	// Resolves the pending MCP caller EXACTLY once (success or structured error) then disposes the drive.
	static void FinalizeDrive(const TSharedPtr<FDriveState>& D, const FString& StopReason)
	{
		if (!D.IsValid() || D->bResolved) { return; }
		D->bResolved = true;

		StopDriveInjection(D);

		APawn* P = D->Pawn.Get();
		const FString ReadinessAfter = P ? ReadPropertyAsText(P, TEXT("CombatReadinessState")) : FString();
		const double SpeedAfter = D->MaxSpeed;

		const bool bReadinessReadable = (!D->ReadinessBefore.IsEmpty() && !ReadinessAfter.IsEmpty());
		const bool bReadinessChanged = D->bReadinessRequested && bReadinessReadable && (D->ReadinessBefore != ReadinessAfter);
		const bool bSpeedIncreased = D->bMoveRequested && (SpeedAfter > D->SpeedBefore + 1.0);
		const bool bMoveInjectionProven = (!D->bMoveInjectionStarted) || D->bMoveInjectionStopped;

		FString StepsArr;
		for (int32 i = 0; i < D->Steps.Num(); ++i) { StepsArr += (i ? TEXT(",") : TEXT("")) + D->Steps[i]; }

		const FString Evidence = FString::Printf(
			TEXT("{\"pawn\":%s,\"readinessAction\":%s,\"moveAction\":%s,\"readinessRequested\":%s,\"moveRequested\":%s,")
			TEXT("\"readinessBefore\":%s,\"readinessAfter\":%s,\"readinessChanged\":%s,\"speedBefore\":%.4f,\"speedAfter\":%.4f,")
			TEXT("\"speedIncreased\":%s,\"readinessInjectionStopped\":%s,\"moveInjectionStarted\":%s,\"moveInjectionStopped\":%s,")
			TEXT("\"stopReason\":%s,\"steps\":[%s]}"),
			*JStr(D->PawnPath), *JStr(D->ReadinessActionProperty), *JStr(D->MoveActionProperty),
			D->bReadinessRequested ? TEXT("true") : TEXT("false"), D->bMoveRequested ? TEXT("true") : TEXT("false"),
			*JStr(D->ReadinessBefore), *JStr(ReadinessAfter), bReadinessChanged ? TEXT("true") : TEXT("false"),
			D->SpeedBefore, SpeedAfter, bSpeedIncreased ? TEXT("true") : TEXT("false"),
			(!D->bReadinessInjectionStarted || D->bReadinessInjectionStopped) ? TEXT("true") : TEXT("false"),
			D->bMoveInjectionStarted ? TEXT("true") : TEXT("false"), bMoveInjectionProven ? TEXT("true") : TEXT("false"),
			*JStr(StopReason), *StepsArr);

		FString FailReason;
		if (StopReason != TEXT("completed"))
		{
			FailReason = FString::Printf(TEXT("drive did not complete normally: %s"), *StopReason);
		}
		else if (D->bReadinessRequested && !bReadinessReadable)
		{
			FailReason = TEXT("readiness verification failed: CombatReadinessState unreadable (before/after empty)");
		}
		else if (D->bReadinessRequested && !bReadinessChanged)
		{
			FailReason = TEXT("readiness verification failed: state did not change");
		}
		else if (D->bMoveRequested && !bSpeedIncreased)
		{
			FailReason = TEXT("movement verification failed: no CMC-driven speed increase observed");
		}
		else if (!bMoveInjectionProven)
		{
			FailReason = TEXT("movement injection was not proven stopped");
		}

		if (D->Result.IsValid())
		{
			if (FailReason.IsEmpty()) { D->Result->SetValue(Evidence); }
			else { D->Result->SetError(FString::Printf(TEXT("%s | evidence=%s"), *FailReason, *Evidence)); }
			D->Result.Reset();
		}

		GDrives.Remove(D);
	}

	// Destroys every transient object a view-capture session owns (idempotent, game-thread).
	static void DestroyViewTransients(const TSharedPtr<FViewCaptureSession>& V)
	{
		if (!V.IsValid()) { return; }
		if (USceneCaptureComponent2D* Cap = V->Capture.Get())
		{
			Cap->TextureTarget = nullptr;
			Cap->DestroyComponent();
		}
		V->Capture.Reset();
		if (AActor* Actor = V->CaptureActor.Get())
		{
			Actor->Destroy();
		}
		V->CaptureActor.Reset();
		V->RT.Reset(); // sole strong ref released -> eligible for GC
	}

	// Resolves the pending MCP caller EXACTLY once (success or structured error), destroys all transient
	// objects + the ticker, and removes the session. Safe on every exit path.
	static void FinalizeViewCapture(const TSharedPtr<FViewCaptureSession>& V, bool bSuccess, const FString& Payload)
	{
		if (!V.IsValid() || V->bResolved) { return; }
		V->bResolved = true;
		if (V->TickHandle.IsValid()) { FTSTicker::GetCoreTicker().RemoveTicker(V->TickHandle); V->TickHandle.Reset(); }
		DestroyViewTransients(V);
		if (V->Result.IsValid())
		{
			if (bSuccess) { V->Result->SetValue(Payload); }
			else { V->Result->SetError(Payload); }
			V->Result.Reset();
		}
		GViewCaptures.Remove(V);
	}

	static void StopAll(const FString& Reason)
	{
		for (auto& Pair : GSessions) { StopSession(Pair.Value, Reason); }
		// Copy because FinalizeDrive / FinalizeViewCapture mutate their arrays.
		TArray<TSharedPtr<FDriveState>> DrivesCopy = GDrives;
		for (const TSharedPtr<FDriveState>& D : DrivesCopy) { FinalizeDrive(D, Reason); }
		TArray<TSharedPtr<FViewCaptureSession>> ViewsCopy = GViewCaptures;
		for (const TSharedPtr<FViewCaptureSession>& V : ViewsCopy) { FinalizeViewCapture(V, false, FString::Printf(TEXT("capture aborted: %s"), *Reason)); }
	}

	static void OnEndPIE(const bool /*bIsSimulating*/) { StopAll(TEXT("PIE ended")); }

	static void OnWorldCleanup(UWorld* World, bool /*bSessionEnded*/, bool /*bCleanupResources*/)
	{
		for (auto& Pair : GSessions)
		{
			const TSharedPtr<FCaptureSession>& S = Pair.Value;
			if (S.IsValid() && S->bActive && S->World.Get() == World) { StopSession(S, TEXT("world destroyed")); }
		}
		TArray<TSharedPtr<FDriveState>> DrivesCopy = GDrives;
		for (const TSharedPtr<FDriveState>& D : DrivesCopy)
		{
			if (D.IsValid() && (!D->Pawn.IsValid() || D->Pawn->GetWorld() == World)) { FinalizeDrive(D, TEXT("world destroyed")); }
		}
		TArray<TSharedPtr<FViewCaptureSession>> ViewsCopy = GViewCaptures;
		for (const TSharedPtr<FViewCaptureSession>& V : ViewsCopy)
		{
			if (V.IsValid() && (!V->World.IsValid() || V->World.Get() == World)) { FinalizeViewCapture(V, false, TEXT("capture aborted: world destroyed")); }
		}
	}

	static void EnsureHooks()
	{
		if (GHooksRegistered) { return; }
		GHooksRegistered = true;
		GEndPIEHandle = FEditorDelegates::EndPIE.AddStatic(&OnEndPIE);
		GWorldCleanupHandle = FWorldDelegates::OnWorldCleanup.AddStatic(&OnWorldCleanup);
	}

	// Frame-coherent transform sample: revalidates the transform-source/pawn/capsule + explicit socket, then
	// serializes RAW Epic-API world transforms/rotations (no bone-space math, no offsets, no axis assumptions).
	// Returns false (and StopSession's the capture) on any drift.
	static bool BuildTransformSample(const TSharedPtr<FCaptureSession>& S, FString& OutSample)
	{
		check(IsInGameThread());
		UWorld* World = S->World.Get();
		APawn* Pawn = S->Pawn.Get();
		USceneComponent* TS = S->TransformSource.Get();
		USceneComponent* Capsule = S->Capsule.Get();

		if (!IsValid(Pawn) || Pawn->IsTemplate() || !IsPIEWorld(Pawn->GetWorld()) || Pawn->GetWorld() != World)
		{ StopSession(S, TEXT("transform-capture pawn invalid/cross-world")); return false; }
		if (!IsValid(TS) || TS->IsTemplate() || !TS->IsRegistered() || TS->GetWorld() != World || TS->GetOwner() != Pawn)
		{ StopSession(S, TEXT("transform-source component invalid/unregistered/ownership changed")); return false; }
		if (!IsValid(Capsule) || Capsule->IsTemplate() || !Capsule->IsRegistered() || Capsule->GetWorld() != World || Capsule->GetOwner() != Pawn)
		{ StopSession(S, TEXT("capsule component invalid/unregistered/cross-world/ownership changed")); return false; }
		const FName Socket(*S->SocketName);
		if (!TS->DoesSocketExist(Socket))
		{ StopSession(S, TEXT("explicit socket no longer exists on transform-source")); return false; }

		const FTransform SockW  = TS->GetSocketTransform(Socket, RTS_World);
		const FTransform CompW  = TS->GetComponentTransform();
		const FRotator BaseAim  = Pawn->GetBaseAimRotation();
		const FRotator ActorRot = Pawn->GetActorRotation();
		const FRotator CapRot   = Capsule->GetComponentRotation();
		AController* Ctrl = Pawn->GetController();
		const FString CtrlPath = Ctrl ? Ctrl->GetPathName() : FString();
		const bool bLocal = Pawn->IsLocallyControlled();

		OutSample = FString::Printf(
			TEXT("{\"sessionId\":%s,\"mode\":\"transform\",\"frameNumber\":%llu,\"worldTimeSeconds\":%.6f,\"world\":%s,\"owner\":%s,")
			TEXT("\"meshComponent\":%s,\"transformSource\":%s,\"socket\":%s,\"hostInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,")
			TEXT("\"socketWorldTransform\":%s,\"transformSourceWorldTransform\":%s,\"baseAimRotation\":%s,\"actorRotation\":%s,\"capsuleWorldRotation\":%s,")
			TEXT("\"controller\":%s,\"isLocallyControlled\":%s,\"localRole\":\"%s\",\"remoteRole\":\"%s\"}"),
			*JStr(S->Id), (unsigned long long)GFrameCounter, World->GetTimeSeconds(),
			*JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath), *JStr(S->TransformSourcePath), *JStr(S->SocketName),
			*JStr(S->HostInstPath), *JStr(S->HostClass), *JStr(S->LayerInstPath), *JStr(S->LayerClass),
			*XformJson(SockW), *XformJson(CompW), *RotJson(BaseAim), *RotJson(ActorRot), *RotJson(CapRot),
			*JStr(CtrlPath), bLocal ? TEXT("true") : TEXT("false"), NetRoleStr(Pawn->GetLocalRole()), NetRoleStr(Pawn->GetRemoteRole()));
		return true;
	}

	// Per-completed-frame sampler. Runs on the game thread inside FinalizeBoneTransform.
	static void OnBoneTransformsFinalized(TWeakPtr<FCaptureSession> WeakSession)
	{
		check(IsInGameThread());
		TSharedPtr<FCaptureSession> S = WeakSession.Pin();
		if (!S.IsValid() || !S->bActive) { return; }

		USkeletalMeshComponent* Mesh = S->Mesh.Get();
		UAnimInstance* Host = S->Host.Get();
		UAnimInstance* Layer = S->Layer.Get();
		UWorld* World = S->World.Get();
		UClass* ExpHost = S->ExpectedHostClass.Get();
		UClass* ExpLayer = S->ExpectedLayerClass.Get();

		// Revalidate before sampling; any drift stops the session with a structured reason.
		if (!IsPIEWorld(World) || !IsUsableMesh(Mesh) || !IsUsableAnimInstance(Host) || !IsUsableAnimInstance(Layer))
		{
			StopSession(S, TEXT("world/component/host/layer became invalid")); return;
		}
		if (Mesh->GetAnimInstance() != Host)
		{
			StopSession(S, TEXT("mesh host AnimInstance changed")); return;
		}
		if (!LayerStillPresent(Mesh, Layer))
		{
			StopSession(S, TEXT("linked layer instance removed/replaced")); return;
		}
		if (!ExpHost || !Host->GetClass()->IsChildOf(ExpHost) || !ExpLayer || !Layer->GetClass()->IsChildOf(ExpLayer))
		{
			StopSession(S, TEXT("host/layer class no longer matches expected")); return;
		}

		FString Sample;
		if (S->bTransformMode)
		{
			// Boundary G: reuses this session + callback; on any drift BuildTransformSample StopSession's and returns false.
			if (!BuildTransformSample(S, Sample)) { return; }
		}
		else
		{
			TArray<FString> ReadErrors;
			auto ReadInto = [&ReadErrors](UAnimInstance* Inst, const FString& InstPath, const TArray<FString>& Props) -> FString
			{
				FString Fields;
				for (int32 i = 0; i < Props.Num(); ++i)
				{
					FString ValJson, Err;
					if (ReadScalarJson(Inst, Props[i], ValJson, Err))
					{
						Fields += FString::Printf(TEXT("%s%s:%s"), (i ? TEXT(",") : TEXT("")), *JStr(Props[i]), *ValJson);
					}
					else
					{
						Fields += FString::Printf(TEXT("%s%s:null"), (i ? TEXT(",") : TEXT("")), *JStr(Props[i]));
						ReadErrors.Add(FString::Printf(TEXT("{\"instance\":%s,\"property\":%s,\"error\":%s}"),
							*JStr(InstPath), *JStr(Props[i]), *JStr(Err)));
					}
				}
				return Fields;
			};

			const FString HostPath = Host->GetPathName();
			const FString LayerPath = Layer->GetPathName();
			const FString HostFields = ReadInto(Host, HostPath, S->HostProps);
			const FString LayerFields = ReadInto(Layer, LayerPath, S->LayerProps);
			const bool bSampleOk = (ReadErrors.Num() == 0);

			FString ErrArr;
			for (int32 i = 0; i < ReadErrors.Num(); ++i) { ErrArr += (i ? TEXT(",") : TEXT("")) + ReadErrors[i]; }

			Sample = FString::Printf(
				TEXT("{\"sessionId\":%s,\"frameNumber\":%llu,\"worldTimeSeconds\":%.6f,\"world\":%s,\"owner\":%s,\"meshComponent\":%s,")
				TEXT("\"hostInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,")
				TEXT("\"sampleOk\":%s,\"host\":{%s},\"layer\":{%s},\"readErrors\":[%s]}"),
				*JStr(S->Id), (unsigned long long)GFrameCounter, World->GetTimeSeconds(),
				*JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath),
				*JStr(HostPath), *JStr(S->HostClass), *JStr(LayerPath), *JStr(S->LayerClass),
				bSampleOk ? TEXT("true") : TEXT("false"), *HostFields, *LayerFields, *ErrArr);
		}

		// Enforce the serialized-byte cap BEFORE storing; never store a partial/truncated object.
		const int64 SampleBytes = (int64)FTCHARToUTF8(*Sample).Length();
		if (S->AccumBytes + SampleBytes > kMaxSampleBytes)
		{
			StopSession(S, TEXT("result size limit reached"));
			return;
		}
		S->Samples.Add(Sample);
		S->AccumBytes += SampleBytes;

		if (S->Samples.Num() >= S->MaxSamples) { StopSession(S, TEXT("max samples reached")); }
	}
	// Shared view-capture phase driver. BOTH CapturePIEPawnViewDeferred and
	// CapturePIEPawnViewProjectedDeferred run through this SINGLE implementation; projection and
	// annotation are gated on Vp->bProjection, so the original tool's behaviour is unchanged.
	static bool RunViewCaptureTick(const TWeakPtr<FViewCaptureSession>& WeakV)
	{
	check(IsInGameThread());
	TSharedPtr<FViewCaptureSession> Vp = WeakV.Pin();
	if (!Vp.IsValid() || Vp->bResolved) { return false; }

	// ---- Phase 0: resolve pawn/mesh + spawn transient capture rig (numeric bounds already validated) ----
	if (Vp->Phase == 0)
	{
		EnsureHooks();
		APawn* Pawn = Cast<APawn>(ResolveActor(Vp->PawnPath));
		if (!IsValid(Pawn)) { FinalizeViewCapture(Vp, false, FString::Printf(TEXT("Pawn not found: %s"), *Vp->PawnPath)); return false; }
		if (Pawn->IsTemplate()) { FinalizeViewCapture(Vp, false, TEXT("Pawn is a CDO/template.")); return false; }
		UWorld* World = Pawn->GetWorld();
		if (!IsPIEWorld(World)) { FinalizeViewCapture(Vp, false, TEXT("Pawn is not in a PIE world (editor/preview rejected).")); return false; }

		USkeletalMeshComponent* Mesh = ResolveMeshComponent(Vp->MeshPath);
		if (!Mesh) { FinalizeViewCapture(Vp, false, FString::Printf(TEXT("Skeletal-mesh component not found: %s"), *Vp->MeshPath)); return false; }
		if (!IsUsableMesh(Mesh)) { FinalizeViewCapture(Vp, false, TEXT("Mesh is not a live/registered PIE component (editor/preview/template/pending-kill rejected).")); return false; }
		if (Mesh->GetOwner() != Pawn) { FinalizeViewCapture(Vp, false, FString::Printf(TEXT("Mesh not owned by the supplied pawn: owner=%s, expected=%s."), *GetPathNameSafe(Mesh->GetOwner()), *Vp->PawnPath)); return false; }

		// SEPARATE transient capture actor in the pawn's world; deliberately NOT owned by the pawn
		// (so the pawn is not the capture's view owner -> bOwnerNoSee body renders, bOnlyOwnerSee FP hides).
		FActorSpawnParameters SpawnParams;
		SpawnParams.ObjectFlags |= RF_Transient;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		const FVector CamPos = Pawn->GetActorLocation() + Vp->CamOffset;
		AActor* Actor = World->SpawnActor<AActor>(AActor::StaticClass(), FTransform(CamPos), SpawnParams);
		if (!Actor) { FinalizeViewCapture(Vp, false, TEXT("Failed to spawn transient capture actor.")); return false; }

		USceneCaptureComponent2D* Cap = NewObject<USceneCaptureComponent2D>(Actor, NAME_None, RF_Transient);
		Actor->SetRootComponent(Cap);
		Cap->RegisterComponent();

		UTextureRenderTarget2D* RT = NewObject<UTextureRenderTarget2D>(Actor, NAME_None, RF_Transient);
		RT->RenderTargetFormat = RTF_RGBA8;
		RT->ClearColor = FLinearColor::Black;
		RT->bAutoGenerateMips = false;
		RT->InitCustomFormat(Vp->Width, Vp->Height, PF_B8G8R8A8, /*bForceLinearGamma=*/false);
		RT->UpdateResourceImmediate(true);

		Cap->TextureTarget = RT;
		Cap->CaptureSource = SCS_FinalColorLDR;
		Cap->bCaptureEveryFrame = false;
		Cap->bCaptureOnMovement = false;
		Cap->bAlwaysPersistRenderingState = true;
		Cap->FOVAngle = (float)Vp->Fov;

		const FVector Target = Pawn->GetActorLocation() + Vp->LookAtOffset;
		Cap->SetWorldLocationAndRotation(CamPos, (Target - CamPos).Rotation());

		Vp->World = World; Vp->Pawn = Pawn; Vp->Mesh = Mesh;
		Vp->WorldName = World->GetPathName();
		Vp->CaptureActor = TStrongObjectPtr<AActor>(Actor);
		Vp->Capture = TStrongObjectPtr<USceneCaptureComponent2D>(Cap);
		Vp->RT = TStrongObjectPtr<UTextureRenderTarget2D>(RT);
		Vp->StartTime = FPlatformTime::Seconds();
		Vp->Phase = 1;
		Vp->FramesSinceSpawn = 0;
		return true; // keep ticking
	}

	// ---- Phase 1: let the world render one frame with the rig present, then capture + read back ----
	UWorld* World = Vp->World.Get();
	APawn* Pawn = Vp->Pawn.Get();
	USkeletalMeshComponent* Mesh = Vp->Mesh.Get();
	USceneCaptureComponent2D* Cap = Vp->Capture.Get();
	UTextureRenderTarget2D* RT = Vp->RT.Get();
	if (!IsPIEWorld(World) || !IsValid(Pawn) || !IsUsableMesh(Mesh) || !Cap || !RT)
		{ FinalizeViewCapture(Vp, false, TEXT("capture aborted: pawn/mesh/world/target invalidated during capture")); return false; }
	if ((FPlatformTime::Seconds() - Vp->StartTime) >= Vp->Timeout)
		{ FinalizeViewCapture(Vp, false, TEXT("timeout")); return false; }

	if (++Vp->FramesSinceSpawn < 2) { return true; }

	// Full revalidation IMMEDIATELY before capture/readback: pawn & mesh still in the ORIGINAL PIE world,
	// mesh still owned by the pawn and still registered/live, and the stored paths still resolve to these
	// exact objects. Any drift aborts with a structured reason (never captures a wrong/replaced object).
	if (Pawn->GetWorld() != World || Mesh->GetWorld() != World
		|| Mesh->GetOwner() != Pawn || !IsUsableMesh(Mesh)
		|| ResolveActor(Vp->PawnPath) != Pawn || ResolveMeshComponent(Vp->MeshPath) != Mesh)
	{ FinalizeViewCapture(Vp, false, TEXT("capture aborted: pawn/mesh identity, world, ownership, or registration changed before capture")); return false; }

	// Re-aim at the pawn's CURRENT location (it may have moved since spawn), then capture one frame.
	const FVector CamPos = Pawn->GetActorLocation() + Vp->CamOffset;
	const FVector Target = Pawn->GetActorLocation() + Vp->LookAtOffset;
	Cap->SetWorldLocationAndRotation(CamPos, (Target - CamPos).Rotation());
	Cap->CaptureScene();
	FlushRenderingCommands();

	FTextureRenderTargetResource* RTRes = RT->GameThread_GetRenderTargetResource();
	if (!RTRes) { FinalizeViewCapture(Vp, false, TEXT("render target resource unavailable")); return false; }
	TArray<FColor> Bitmap;
	FReadSurfaceDataFlags ReadFlags(RCM_UNorm, CubeFace_MAX);
	if (!RTRes->ReadPixels(Bitmap, ReadFlags) || Bitmap.Num() != Vp->Width * Vp->Height)
		{ FinalizeViewCapture(Vp, false, TEXT("pixel readback failed or size mismatch")); return false; }

	FToolsetImage Img;
	if (!Img.SetFromBitmap(Bitmap, FIntPoint(Vp->Width, Vp->Height), ERGBFormat::BGRA))
		{ FinalizeViewCapture(Vp, false, TEXT("PNG encode failed")); return false; }
	// The cap is on the Base64 image DATA only (ASCII, so Len() == UTF-8 byte count), not the whole JSON.
	if (Img.Data.Len() > kViewMaxEncodedBytes)
		{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("Base64 image data %d bytes exceeds the %d-byte cap."), Img.Data.Len(), kViewMaxEncodedBytes)); return false; }

	// ---- A1: engine-owned projection for this SAME rendered frame -------------------------
	FString ProjectionJson;
	if (Vp->bProjection)
	{
		// Engine view info -> engine matrices. No hand-rolled camera basis, FOV or aspect math.
		FMinimalViewInfo ViewInfo;
		Cap->GetCameraView(0.0f, ViewInfo);
		FMatrix ViewM, ProjM, ViewProjM;
		UGameplayStatics::CalculateViewProjectionMatricesFromMinimalView(ViewInfo, TOptional<FMatrix>(), ViewM, ProjM, ViewProjM);
		const FIntRect ViewRect(0, 0, Vp->Width, Vp->Height);

		auto MatrixRows = [](const FMatrix& M) -> FString
		{
			FString Rows;
			for (int32 R = 0; R < 4; ++R)
			{
				Rows += FString::Printf(TEXT("%s[%.9g,%.9g,%.9g,%.9g]"), (R ? TEXT(",") : TEXT("")),
					M.M[R][0], M.M[R][1], M.M[R][2], M.M[R][3]);
			}
			return Rows;
		};

		// bOk is the ENGINE return value and is kept separate from finiteness / inFront / inView.
		// A non-finite world position, clip W, or projected pixel is never serialized or drawn.
		struct FProjPt { FVector2D Pixel = FVector2D::ZeroVector; bool bOk = false; bool bFinite = false; bool bInFront = false; bool bInView = false; };
		auto ProjectPoint = [&ViewProjM, &ViewRect, Vp](const FVector& WorldPos) -> FProjPt
		{
			FProjPt Out;
			if (WorldPos.ContainsNaN() || !FMath::IsFinite(WorldPos.X) || !FMath::IsFinite(WorldPos.Y) || !FMath::IsFinite(WorldPos.Z))
			{
				return Out; // bOk/bFinite false, zeroed pixel
			}
			FVector2D Pixel = FVector2D::ZeroVector;
			Out.bOk = FSceneView::ProjectWorldToScreen(WorldPos, ViewRect, ViewProjM, Pixel, true);
			const FVector4 Clip = ViewProjM.TransformFVector4(FVector4(WorldPos, 1.0));
			if (!FMath::IsFinite(Clip.W) || !FMath::IsFinite(Pixel.X) || !FMath::IsFinite(Pixel.Y))
			{
				return Out; // engine status preserved in bOk; bFinite stays false, pixel stays zeroed
			}
			Out.bFinite = true;
			Out.Pixel = Pixel;
			Out.bInFront = Clip.W > 0.0;
			// Valid raster rectangle is half-open: 0 <= x < Width and 0 <= y < Height.
			Out.bInView = Out.bInFront && Pixel.X >= 0.0 && Pixel.Y >= 0.0
				&& Pixel.X < (double)Vp->Width && Pixel.Y < (double)Vp->Height;
			return Out;
		};
		auto PtJson = [](const FProjPt& Pt) -> FString
		{
			return FString::Printf(TEXT("{\"x\":%.4f,\"y\":%.4f,\"ok\":%s,\"finite\":%s,\"inFront\":%s,\"inView\":%s}"),
				Pt.Pixel.X, Pt.Pixel.Y, Pt.bOk ? TEXT("true") : TEXT("false"),
				Pt.bFinite ? TEXT("true") : TEXT("false"),
				Pt.bInFront ? TEXT("true") : TEXT("false"), Pt.bInView ? TEXT("true") : TEXT("false"));
		};

		struct FAnn { FProjPt Origin, AxX, AxY, AxZ; };
		TArray<FAnn> Anns;
		FString TargetsJson;
		for (int32 i = 0; i < Vp->TargetComponentPaths.Num(); ++i)
		{
			// Re-resolve and re-validate INSIDE the rendered frame: identity, ownership, world,
			// registration and socket existence must all still hold at capture time.
			const FString& CompPath = Vp->TargetComponentPaths[i];
			const FString& SockName = Vp->TargetSocketNames[i];
			USceneComponent* Comp = ResolveSceneComponent(CompPath);
			if (!Comp || !IsValid(Comp) || Comp->IsTemplate() || !Comp->IsRegistered())
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("projection target component not live/registered at capture time: %s"), *CompPath)); return false; }
			if (Comp->GetOwner() != Pawn)
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("projection target component is not owned by the supplied pawn at capture time: %s"), *CompPath)); return false; }
			if (Comp->GetWorld() != World)
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("projection target component is in a different world at capture time: %s"), *CompPath)); return false; }
			const FName SockFName(*SockName);
			if (!Comp->DoesSocketExist(SockFName))
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("socket '%s' does not exist on %s at capture time."), *SockName, *CompPath)); return false; }

			const FTransform SockW = Comp->GetSocketTransform(SockFName, RTS_World);
			if (SockW.ContainsNaN())
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("socket '%s' on %s produced a non-finite world transform."), *SockName, *CompPath)); return false; }
			const FVector Origin = SockW.GetLocation();
			FAnn A;
			A.Origin = ProjectPoint(Origin);
			A.AxX = ProjectPoint(Origin + SockW.GetUnitAxis(EAxis::X) * Vp->AxisLength);
			A.AxY = ProjectPoint(Origin + SockW.GetUnitAxis(EAxis::Y) * Vp->AxisLength);
			A.AxZ = ProjectPoint(Origin + SockW.GetUnitAxis(EAxis::Z) * Vp->AxisLength);
			Anns.Add(A);

			TargetsJson += FString::Printf(
				TEXT("%s{\"component\":%s,\"socket\":%s,\"socketWorldTransform\":%s,\"projected\":%s,\"axes\":{\"x\":%s,\"y\":%s,\"z\":%s}}"),
				(i ? TEXT(",") : TEXT("")), *JStr(Comp->GetPathName()), *JStr(SockName),
				*XformJson(SockW), *PtJson(A.Origin), *PtJson(A.AxX), *PtJson(A.AxY), *PtJson(A.AxZ));
		}

		ProjectionJson = FString::Printf(
			TEXT(",\"axisLength\":%.4f,\"matrixConvention\":%s,\"viewMatrix\":{\"rows\":[%s]},\"projectionMatrix\":{\"rows\":[%s]},\"viewProjectionMatrix\":{\"rows\":[%s]},\"targets\":[%s]"),
			Vp->AxisLength,
			*JStr(TEXT("rows[i][j] == FMatrix::M[i][j]; Unreal row-vector convention (v * M), translation in row 3")),
			*MatrixRows(ViewM), *MatrixRows(ProjM), *MatrixRows(ViewProjM), *TargetsJson);

		if (FTCHARToUTF8(*ProjectionJson).Length() > kMaxProjectionJsonBytes)
			{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("projection JSON exceeds the %d-byte cap."), kMaxProjectionJsonBytes)); return false; }

		// ---- optional annotation via Unreal's supported render-target canvas path ----
		if (Vp->bAnnotate)
		{
			UCanvas* Canvas = nullptr;
			FVector2D CanvasSize = FVector2D::ZeroVector;
			FDrawToRenderTargetContext Ctx;
			UKismetRenderingLibrary::BeginDrawCanvasToRenderTarget(World, RT, Canvas, CanvasSize, Ctx);
			if (!Canvas)
			{
				// Do NOT call EndDrawCanvasToRenderTarget with an invalid context, and never report
				// annotated:true for an annotation that did not happen.
				FinalizeViewCapture(Vp, false, TEXT("annotation failed: BeginDrawCanvasToRenderTarget returned a null canvas"));
				return false;
			}
			{
				const float Thickness = 2.0f;
				const float Half = 5.0f;
				for (const FAnn& A : Anns)
				{
					// Conservative annotation: only draw coordinates proven to lie inside the raster
					// rectangle. Finiteness alone is not enough -- a near-plane point can project to an
					// enormous finite pixel. Reported projection coordinates are unaffected by this.
					if (!A.Origin.bInView) { continue; }
					Canvas->K2_DrawBox(FVector2D(A.Origin.Pixel.X - Half, A.Origin.Pixel.Y - Half),
						FVector2D(Half * 2.0f, Half * 2.0f), Thickness, FLinearColor::White);
					if (A.AxX.bInView) { Canvas->K2_DrawLine(A.Origin.Pixel, A.AxX.Pixel, Thickness, FLinearColor::Red); }
					if (A.AxY.bInView) { Canvas->K2_DrawLine(A.Origin.Pixel, A.AxY.Pixel, Thickness, FLinearColor::Green); }
					if (A.AxZ.bInView) { Canvas->K2_DrawLine(A.Origin.Pixel, A.AxZ.Pixel, Thickness, FLinearColor::Blue); }
				}
			}
			UKismetRenderingLibrary::EndDrawCanvasToRenderTarget(World, Ctx);
			FlushRenderingCommands();

			TArray<FColor> AnnBitmap;
			if (!RTRes->ReadPixels(AnnBitmap, ReadFlags) || AnnBitmap.Num() != Vp->Width * Vp->Height)
				{ FinalizeViewCapture(Vp, false, TEXT("annotated pixel readback failed or size mismatch")); return false; }
			FToolsetImage AnnImg;
			if (!AnnImg.SetFromBitmap(AnnBitmap, FIntPoint(Vp->Width, Vp->Height), ERGBFormat::BGRA))
				{ FinalizeViewCapture(Vp, false, TEXT("annotated PNG encode failed")); return false; }
			if (AnnImg.Data.Len() > kViewMaxEncodedBytes)
				{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("Base64 annotated image data %d bytes exceeds the %d-byte cap."), AnnImg.Data.Len(), kViewMaxEncodedBytes)); return false; }
			// Exactly ONE image is returned: the annotated render REPLACES the raw one, so the
			// approved 12 MiB Base64 bound applies to the whole payload, not per image.
			Img = AnnImg;
		}
	}

	const FRotator FinalRot = Cap->GetComponentRotation();
	const FVector  FinalLoc = Cap->GetComponentLocation();
	FString Payload = FString::Printf(
		TEXT("{\"pawn\":%s,\"mesh\":%s,\"world\":%s,\"frameNumber\":%llu,\"worldTimeSeconds\":%.6f,")
		TEXT("\"cameraTransform\":{\"location\":{\"x\":%.3f,\"y\":%.3f,\"z\":%.3f},\"rotation\":{\"pitch\":%.3f,\"yaw\":%.3f,\"roll\":%.3f}},")
		TEXT("\"width\":%d,\"height\":%d,\"fov\":%.3f,\"image\":{\"mimeType\":%s,\"data\":%s}}"),
		*JStr(Vp->PawnPath), *JStr(Vp->MeshPath), *JStr(Vp->WorldName),
		(unsigned long long)GFrameCounter, World->GetTimeSeconds(),
		FinalLoc.X, FinalLoc.Y, FinalLoc.Z, FinalRot.Pitch, FinalRot.Yaw, FinalRot.Roll,
		Vp->Width, Vp->Height, Vp->Fov, *JStr(Img.MimeType), *JStr(Img.Data));

	if (Vp->bProjection)
	{
		// Splice the projection block in before the closing brace.
		Payload = Payload.LeftChop(1) + ProjectionJson
			+ FString::Printf(TEXT(",\"annotated\":%s,\"limits\":{\"maxProjectionTargets\":%d,\"maxAxisLength\":%.0f,\"maxProjectionJsonBytes\":%d,\"maxImageBytes\":%d,\"maxResponseBytes\":%d}}"),
				Vp->bAnnotate ? TEXT("true") : TEXT("false"),
				kMaxProjectionTargets, kMaxAxisLength, kMaxProjectionJsonBytes, kViewMaxEncodedBytes, kMaxResponseBytes);

		// Final bounded-response check BEFORE the result is ever set.
		const int32 ResponseBytes = FTCHARToUTF8(*Payload).Length();
		if (ResponseBytes > kMaxResponseBytes)
			{ FinalizeViewCapture(Vp, false, FString::Printf(TEXT("response %d bytes exceeds the %d-byte cap."), ResponseBytes, kMaxResponseBytes)); return false; }
	}

	FinalizeViewCapture(Vp, true, Payload);
	return false;
	}

} // namespace TacticalRuntimeAnimInspection

using namespace TacticalRuntimeAnimInspection;

// =============================================================================
// ListPIEAnimInstancePairs
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::ListPIEAnimInstancePairs()
{
	return RunDeferredString([](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());
		if (!GEngine) { OutError = TEXT("No GEngine."); return false; }

		FString WorldsJson; int32 WorldCount = 0;
		for (const FWorldContext& Ctx : GEngine->GetWorldContexts())
		{
			UWorld* W = Ctx.World();
			if (!IsPIEWorld(W)) { continue; }

			FString MeshesJson; int32 MeshCount = 0;
			for (TObjectIterator<USkeletalMeshComponent> It; It; ++It)
			{
				USkeletalMeshComponent* Mesh = *It;
				if (Mesh->GetWorld() != W || !IsUsableMesh(Mesh)) { continue; }

				UAnimInstance* Host = Mesh->GetAnimInstance();
				const FString OwnerPath = Mesh->GetOwner() ? Mesh->GetOwner()->GetPathName() : FString();

				FString LayersJson; int32 LayerCount = 0;
				for (UAnimInstance* Layer : GetLinkedInstances(Mesh))
				{
					if (!IsUsableAnimInstance(Layer)) { continue; }
					LayersJson += FString::Printf(TEXT("%s{\"instance\":%s,\"class\":%s}"),
						(LayerCount ? TEXT(",") : TEXT("")), *JStr(Layer->GetPathName()), *JStr(Layer->GetClass()->GetPathName()));
					++LayerCount;
				}

				MeshesJson += FString::Printf(
					TEXT("%s{\"owner\":%s,\"meshComponent\":%s,\"hostAnimInstance\":%s,\"hostClass\":%s,\"linkedLayers\":[%s]}"),
					(MeshCount ? TEXT(",") : TEXT("")), *JStr(OwnerPath), *JStr(Mesh->GetPathName()),
					*JStr(IsUsableAnimInstance(Host) ? Host->GetPathName() : FString()),
					*JStr(IsUsableAnimInstance(Host) ? Host->GetClass()->GetPathName() : FString()), *LayersJson);
				++MeshCount;
			}

			WorldsJson += FString::Printf(TEXT("%s{\"world\":%s,\"timeSeconds\":%.6f,\"meshes\":[%s]}"),
				(WorldCount ? TEXT(",") : TEXT("")), *JStr(W->GetPathName()), W->GetTimeSeconds(), *MeshesJson);
			++WorldCount;
		}

		OutValue = FString::Printf(TEXT("{\"pieWorldCount\":%d,\"pieWorlds\":[%s]}"), WorldCount, *WorldsJson);
		return true;
	});
}

// =============================================================================
// StartLinkedAnimInstanceCapture
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::StartLinkedAnimInstanceCapture(
	const FString& MeshComponentPath, const FString& PawnPath, const FString& HostClassPath, const FString& LayerClassPath,
	const TArray<FString>& HostProperties, const TArray<FString>& LayerProperties, int32 MaxSamples, float TimeoutSeconds)
{
	return RunDeferredString([=](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());
		EnsureHooks();

		if (MaxSamples < 1 || MaxSamples > kMaxSamplesLimit) { OutError = FString::Printf(TEXT("MaxSamples must be in [1,%d]."), kMaxSamplesLimit); return false; }
		if (TimeoutSeconds <= 0.f || (double)TimeoutSeconds > kMaxTimeoutSeconds) { OutError = FString::Printf(TEXT("TimeoutSeconds must be in (0,%.0f]."), kMaxTimeoutSeconds); return false; }
		if (HostProperties.Num() == 0 && LayerProperties.Num() == 0) { OutError = TEXT("No properties requested."); return false; }
		if (!ValidatePropertyList(HostProperties, TEXT("HostProperties"), OutError)) { return false; }
		if (!ValidatePropertyList(LayerProperties, TEXT("LayerProperties"), OutError)) { return false; }

		USkeletalMeshComponent* Mesh = ResolveMeshComponent(MeshComponentPath);
		if (!Mesh) { OutError = FString::Printf(TEXT("Skeletal-mesh component not found: %s"), *MeshComponentPath); return false; }
		if (!IsUsableMesh(Mesh)) { OutError = TEXT("Mesh component is not a live/registered PIE-world component (editor/preview/template/pending-kill rejected)."); return false; }

		AActor* Owner = Mesh->GetOwner();
		if (!Owner) { OutError = TEXT("Mesh component has no owner."); return false; }
		if (Owner->GetPathName() != PawnPath) { OutError = FString::Printf(TEXT("Mesh owner mismatch: component owned by %s, expected %s."), *Owner->GetPathName(), *PawnPath); return false; }

		for (auto& Pair : GSessions)
		{
			const TSharedPtr<FCaptureSession>& Existing = Pair.Value;
			if (Existing.IsValid() && Existing->bActive && Existing->Mesh.Get() == Mesh)
			{
				OutError = FString::Printf(TEXT("A capture session (%s) is already active on this mesh."), *Existing->Id); return false;
			}
		}

		UAnimInstance* Host = Mesh->GetAnimInstance();
		if (!IsUsableAnimInstance(Host)) { OutError = TEXT("Mesh has no usable host AnimInstance."); return false; }

		UClass* WantHost = ResolveAnimInstanceClass(HostClassPath);
		if (!WantHost) { OutError = FString::Printf(TEXT("Could not resolve host class: %s"), *HostClassPath); return false; }
		if (!Host->GetClass()->IsChildOf(WantHost)) { OutError = FString::Printf(TEXT("Host class mismatch: instance is %s, expected %s."), *Host->GetClass()->GetPathName(), *WantHost->GetPathName()); return false; }

		UClass* WantLayer = ResolveAnimInstanceClass(LayerClassPath);
		if (!WantLayer) { OutError = FString::Printf(TEXT("Could not resolve layer class: %s"), *LayerClassPath); return false; }

		UAnimInstance* Layer = nullptr; int32 LayerMatches = 0;
		for (UAnimInstance* L : GetLinkedInstances(Mesh))
		{
			if (IsUsableAnimInstance(L) && L->GetClass()->IsChildOf(WantLayer)) { ++LayerMatches; Layer = L; }
		}
		if (LayerMatches == 0) { OutError = FString::Printf(TEXT("No linked layer instance of class %s on this mesh."), *WantLayer->GetPathName()); return false; }
		if (LayerMatches > 1) { OutError = FString::Printf(TEXT("Ambiguous: %d linked layer instances of class %s."), LayerMatches, *WantLayer->GetPathName()); return false; }

		TSharedPtr<FCaptureSession> S = MakeShared<FCaptureSession>();
		S->Id = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
		S->World = Owner->GetWorld();
		S->Mesh = Mesh; S->Host = Host; S->Layer = Layer;
		S->ExpectedHostClass = WantHost; S->ExpectedLayerClass = WantLayer;
		S->WorldName = Owner->GetWorld()->GetPathName();
		S->OwnerPath = Owner->GetPathName();
		S->MeshPath = Mesh->GetPathName();
		S->HostInstPath = Host->GetPathName();
		S->HostClass = Host->GetClass()->GetPathName();
		S->LayerInstPath = Layer->GetPathName();
		S->LayerClass = Layer->GetClass()->GetPathName();
		S->HostProps = HostProperties; S->LayerProps = LayerProperties;
		S->MaxSamples = MaxSamples; S->Timeout = (double)TimeoutSeconds;
		S->StartTime = FPlatformTime::Seconds();
		S->bActive = true;

		TWeakPtr<FCaptureSession> WeakS = S;
		S->FinalizeHandle = Mesh->RegisterOnBoneTransformsFinalizedDelegate(
			FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateLambda([WeakS]() { OnBoneTransformsFinalized(WeakS); }));

		// Independent lifecycle/timeout ticker: guarantees termination even with no further finalized frames.
		S->LifecycleHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[WeakS](float) -> bool
			{
				TSharedPtr<FCaptureSession> Sp = WeakS.Pin();
				if (!Sp.IsValid() || !Sp->bActive) { return false; }
				UWorld* W = Sp->World.Get();
				USkeletalMeshComponent* M = Sp->Mesh.Get();
				UAnimInstance* H = Sp->Host.Get();
				UAnimInstance* L = Sp->Layer.Get();
				if (!IsPIEWorld(W) || !IsUsableMesh(M) || !IsUsableAnimInstance(H) || !IsUsableAnimInstance(L)
					|| M->GetAnimInstance() != H || !LayerStillPresent(M, L))
				{
					StopSession(Sp, TEXT("invalidated (lifecycle)")); return false;
				}
				if ((FPlatformTime::Seconds() - Sp->StartTime) >= Sp->Timeout)
				{
					StopSession(Sp, TEXT("timeout")); return false;
				}
				return true;
			}), kLifecycleTickInterval);

		GSessions.Add(S->Id, S);

		FString HP; for (int32 i = 0; i < HostProperties.Num(); ++i) { HP += (i ? TEXT(",") : TEXT("")) + JStr(HostProperties[i]); }
		FString LP; for (int32 i = 0; i < LayerProperties.Num(); ++i) { LP += (i ? TEXT(",") : TEXT("")) + JStr(LayerProperties[i]); }

		OutValue = FString::Printf(
			TEXT("{\"sessionId\":%s,\"world\":%s,\"owner\":%s,\"meshComponent\":%s,\"hostAnimInstance\":%s,\"hostClass\":%s,")
			TEXT("\"layerInstance\":%s,\"layerClass\":%s,\"hostProperties\":[%s],\"layerProperties\":[%s],\"maxSamples\":%d,\"timeoutSeconds\":%.3f}"),
			*JStr(S->Id), *JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath), *JStr(S->HostInstPath), *JStr(S->HostClass),
			*JStr(S->LayerInstPath), *JStr(S->LayerClass), *HP, *LP, MaxSamples, TimeoutSeconds);
		return true;
	});
}

// =============================================================================
// StopLinkedAnimInstanceCapture
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::StopLinkedAnimInstanceCapture(const FString& SessionId)
{
	return RunDeferredString([=](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());
		TSharedPtr<FCaptureSession> S;
		if (TSharedPtr<FCaptureSession>* Found = GSessions.Find(SessionId)) { S = *Found; }
		if (!S.IsValid()) { OutError = FString::Printf(TEXT("Unknown capture session: %s"), *SessionId); return false; }

		StopSession(S, TEXT("stopped by caller"));

		FString SamplesArr;
		for (int32 i = 0; i < S->Samples.Num(); ++i) { SamplesArr += (i ? TEXT(",") : TEXT("")) + S->Samples[i]; }

		OutValue = FString::Printf(
			TEXT("{\"sessionId\":%s,\"active\":false,\"stopReason\":%s,\"world\":%s,\"owner\":%s,\"meshComponent\":%s,")
			TEXT("\"hostClass\":%s,\"layerClass\":%s,\"sampleCount\":%d,\"maxSamples\":%d,")
			TEXT("\"accumulatedSampleBytes\":%lld,\"limits\":{\"maxSamples\":%d,\"maxTimeoutSeconds\":%.0f,")
			TEXT("\"maxPropertiesPerSide\":%d,\"maxPropertyNameLength\":%d,\"maxSampleBytes\":%lld},\"samples\":[%s]}"),
			*JStr(S->Id), *JStr(S->StopReason), *JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath),
			*JStr(S->HostClass), *JStr(S->LayerClass), S->Samples.Num(), S->MaxSamples,
			(long long)S->AccumBytes, kMaxSamplesLimit, kMaxTimeoutSeconds,
			kMaxPropertiesPerSide, kMaxPropertyNameLen, (long long)kMaxSampleBytes, *SamplesArr);

		GSessions.Remove(SessionId);
		return true;
	});
}

// =============================================================================
// DrivePIEInputSequenceDeferred
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::DrivePIEInputSequenceDeferred(
	const FString& PawnPath, const FString& ReadinessActionProperty, const FString& MoveActionProperty,
	float MoveX, float MoveY, float PreMoveIdleSeconds, float MoveSeconds, float TimeoutSeconds)
{
	UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();
	TStrongObjectPtr<UToolCallAsyncResultString> StrongResult(Result);

	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[=](float) mutable -> bool
	{
		check(IsInGameThread());
		EnsureHooks();
		auto Fail = [&StrongResult](const FString& Err) { StrongResult->SetError(Err); StrongResult.Reset(); };

		if (TimeoutSeconds <= 0.f || (double)TimeoutSeconds > kMaxTimeoutSeconds) { Fail(FString::Printf(TEXT("TimeoutSeconds must be in (0,%.0f]."), kMaxTimeoutSeconds)); return false; }

		APawn* Pawn = Cast<APawn>(ResolveActor(PawnPath));
		if (!Pawn) { Fail(FString::Printf(TEXT("Pawn not found: %s"), *PawnPath)); return false; }
		if (!IsPIEWorld(Pawn->GetWorld())) { Fail(TEXT("Pawn is not in a PIE world.")); return false; }

		for (const TSharedPtr<FDriveState>& Existing : GDrives)
		{
			if (Existing.IsValid() && !Existing->bResolved && Existing->Pawn.Get() == Pawn)
			{
				Fail(TEXT("A drive sequence is already active on this pawn.")); return false;
			}
		}

		APlayerController* PC = Cast<APlayerController>(Pawn->GetController());
		ULocalPlayer* LP = PC ? PC->GetLocalPlayer() : nullptr;
		UEnhancedInputLocalPlayerSubsystem* Sub = LP ? ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP) : nullptr;
		if (!Sub) { Fail(TEXT("No EnhancedInput local-player subsystem on the pawn's controller (real input path unavailable).")); return false; }

		auto ResolveAction = [Pawn](const FString& PropName) -> UInputAction*
		{
			if (PropName.IsEmpty()) { return nullptr; }
			FObjectProperty* OP = CastField<FObjectProperty>(Pawn->GetClass()->FindPropertyByName(FName(*PropName)));
			if (!OP) { return nullptr; }
			return Cast<UInputAction>(OP->GetObjectPropertyValue_InContainer(Pawn));
		};

		const bool bReadinessRequested = !ReadinessActionProperty.IsEmpty();
		const bool bMoveRequested = !MoveActionProperty.IsEmpty();
		if (!bReadinessRequested && !bMoveRequested) { Fail(TEXT("Nothing to drive (both action properties empty).")); return false; }

		UInputAction* ReadinessAction = ResolveAction(ReadinessActionProperty);
		UInputAction* MoveAction = ResolveAction(MoveActionProperty);
		if (bReadinessRequested && !ReadinessAction) { Fail(FString::Printf(TEXT("Readiness action property '%s' not found or not a UInputAction."), *ReadinessActionProperty)); return false; }
		if (bMoveRequested && !MoveAction) { Fail(FString::Printf(TEXT("Move action property '%s' not found or not a UInputAction."), *MoveActionProperty)); return false; }

		// Validate input-action value types before any injection.
		if (bReadinessRequested && ReadinessAction->ValueType != EInputActionValueType::Boolean)
		{ Fail(FString::Printf(TEXT("Readiness action value type must be Boolean (is %d)."), (int32)ReadinessAction->ValueType)); return false; }
		if (bMoveRequested && MoveAction->ValueType != EInputActionValueType::Axis2D)
		{ Fail(FString::Printf(TEXT("Move action value type must be Axis2D (is %d)."), (int32)MoveAction->ValueType)); return false; }

		// Readiness verification requires a readable readiness state up front.
		const FString ReadinessBefore = ReadPropertyAsText(Pawn, TEXT("CombatReadinessState"));
		if (bReadinessRequested && ReadinessBefore.IsEmpty())
		{ Fail(TEXT("Readiness requested but 'CombatReadinessState' property is missing/unreadable on the pawn.")); return false; }

		TSharedPtr<FDriveState> D = MakeShared<FDriveState>();
		D->Result = MoveTemp(StrongResult);
		D->Pawn = Pawn; D->Subsystem = Sub; D->ReadinessAction = ReadinessAction; D->MoveAction = MoveAction;
		D->PawnPath = PawnPath; D->ReadinessActionProperty = ReadinessActionProperty; D->MoveActionProperty = MoveActionProperty;
		D->bReadinessRequested = bReadinessRequested; D->bMoveRequested = bMoveRequested;
		D->ReadinessBefore = ReadinessBefore;
		D->SpeedBefore = Pawn->GetVelocity().Size2D();
		D->MaxSpeed = D->SpeedBefore;
		D->MoveX = MoveX; D->MoveY = MoveY;
		D->TimeoutSeconds = (double)TimeoutSeconds;
		D->T0 = FPlatformTime::Seconds();
		D->PressAt = FMath::Max(0.0, (double)PreMoveIdleSeconds);
		D->ReleaseAt = D->PressAt + kReadinessPressHoldSeconds;
		D->MoveStartAt = D->ReleaseAt;
		D->MoveStopAt = D->MoveStartAt + FMath::Max(0.0, (double)MoveSeconds);
		GDrives.Add(D);

		auto AddStep = [](const TSharedPtr<FDriveState>& DS, const TCHAR* Phase, double AtSec, const FString& Action, const FString& Value)
		{
			DS->Steps.Add(FString::Printf(TEXT("{\"phase\":%s,\"atSeconds\":%.3f,\"action\":%s,\"value\":%s}"),
				*JStr(Phase), AtSec, *JStr(Action), *JStr(Value)));
		};

		TWeakPtr<FDriveState> WeakD = D;
		D->TickHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[WeakD, AddStep](float) -> bool
		{
			check(IsInGameThread());
			TSharedPtr<FDriveState> DS = WeakD.Pin();
			if (!DS.IsValid() || DS->bResolved) { return false; }

			APawn* P = DS->Pawn.Get();
			UEnhancedInputLocalPlayerSubsystem* SubNow = DS->Subsystem.Get();
			if (!IsValid(P) || !IsPIEWorld(P->GetWorld()) || !SubNow)
			{
				FinalizeDrive(DS, TEXT("pawn/subsystem invalid during sequence")); return false;
			}

			const double Elapsed = FPlatformTime::Seconds() - DS->T0;
			if (Elapsed >= DS->TimeoutSeconds) { FinalizeDrive(DS, TEXT("timeout")); return false; }

			DS->MaxSpeed = FMath::Max(DS->MaxSpeed, P->GetVelocity().Size2D());

			if (DS->ReadinessAction.IsValid() && !DS->bReadinessInjectionStarted && Elapsed >= DS->PressAt)
			{
				SubNow->StartContinuousInputInjectionForAction(DS->ReadinessAction.Get(), FInputActionValue(true), TArray<UInputModifier*>{}, TArray<UInputTrigger*>{});
				DS->bReadinessInjecting = true; DS->bReadinessInjectionStarted = true;
				AddStep(DS, TEXT("readiness-press"), Elapsed, DS->ReadinessActionProperty, TEXT("true"));
			}
			if (DS->ReadinessAction.IsValid() && DS->bReadinessInjecting && Elapsed >= DS->ReleaseAt)
			{
				SubNow->StopContinuousInputInjectionForAction(DS->ReadinessAction.Get());
				DS->bReadinessInjecting = false; DS->bReadinessInjectionStopped = true;
				AddStep(DS, TEXT("readiness-release"), Elapsed, DS->ReadinessActionProperty, TEXT("stop"));
			}
			if (DS->MoveAction.IsValid() && !DS->bMoveInjectionStarted && Elapsed >= DS->MoveStartAt)
			{
				SubNow->StartContinuousInputInjectionForAction(DS->MoveAction.Get(), FInputActionValue(FVector2D(DS->MoveX, DS->MoveY)), TArray<UInputModifier*>{}, TArray<UInputTrigger*>{});
				DS->bMoveInjecting = true; DS->bMoveInjectionStarted = true;
				AddStep(DS, TEXT("move-start"), Elapsed, DS->MoveActionProperty, FString::Printf(TEXT("(%.2f,%.2f)"), DS->MoveX, DS->MoveY));
			}
			if (DS->MoveAction.IsValid() && DS->bMoveInjecting && Elapsed >= DS->MoveStopAt)
			{
				SubNow->StopContinuousInputInjectionForAction(DS->MoveAction.Get());
				DS->bMoveInjecting = false; DS->bMoveInjectionStopped = true;
				AddStep(DS, TEXT("move-stop"), Elapsed, DS->MoveActionProperty, TEXT("stop"));
			}

			const bool bReadinessDone = !DS->bReadinessRequested || (DS->bReadinessInjectionStarted && DS->bReadinessInjectionStopped);
			const bool bMoveDone = !DS->bMoveRequested || (DS->bMoveInjectionStarted && DS->bMoveInjectionStopped);
			if (bReadinessDone && bMoveDone && Elapsed >= DS->MoveStopAt)
			{
				FinalizeDrive(DS, TEXT("completed")); return false;
			}
			return true;
		}), 0.0f);

		return false; // setup ticker is one-shot
	}));

	return Result;
}

// =============================================================================
// CapturePIEPawnViewProjectedDeferred (A1)
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::CapturePIEPawnViewProjectedDeferred(
	const FString& PawnPath, const FString& MeshComponentPath,
	float CameraOffsetX, float CameraOffsetY, float CameraOffsetZ,
	float LookAtOffsetX, float LookAtOffsetY, float LookAtOffsetZ,
	int32 Width, int32 Height, float FOV, float TimeoutSeconds,
	const TArray<FString>& ComponentPaths, const TArray<FString>& SocketNames,
	float AxisLength, bool bAnnotate)
{
	using namespace TacticalRuntimeAnimInspection;

	UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();

	// Reject an overlapping call BEFORE any session is allocated or scheduled.
	if (GViewCaptures.Num() >= kMaxConcurrentViewCaptures)
	{
		Result->SetError(FString::Printf(TEXT("A pawn-view capture is already in progress; at most %d concurrent view-capture session(s) allowed."), kMaxConcurrentViewCaptures));
		return Result;
	}

	const FVector CamOffset(CameraOffsetX, CameraOffsetY, CameraOffsetZ);
	const FVector LookAtOffset(LookAtOffsetX, LookAtOffsetY, LookAtOffsetZ);

	// ALL validation happens here, BEFORE any expensive render resource is allocated.
	{
		FString Err;
		if (!FMath::IsFinite(CameraOffsetX) || !FMath::IsFinite(CameraOffsetY) || !FMath::IsFinite(CameraOffsetZ)
			|| !FMath::IsFinite(LookAtOffsetX) || !FMath::IsFinite(LookAtOffsetY) || !FMath::IsFinite(LookAtOffsetZ))
			{ Err = TEXT("Camera/look-at offset components must be finite."); }
		else if (!FMath::IsFinite(FOV)) { Err = TEXT("FOV must be finite."); }
		else if (!FMath::IsFinite(TimeoutSeconds)) { Err = TEXT("TimeoutSeconds must be finite."); }
		else if (!FMath::IsFinite(AxisLength)) { Err = TEXT("AxisLength must be finite."); }
		else if (Width < kViewMinDim || Width > kViewMaxDim || Height < kViewMinDim || Height > kViewMaxDim)
			{ Err = FString::Printf(TEXT("Width/Height must be in [%d,%d]."), kViewMinDim, kViewMaxDim); }
		else if ((int64)Width * (int64)Height > kViewMaxPixels)
			{ Err = FString::Printf(TEXT("Width*Height exceeds %lld pixels."), kViewMaxPixels); }
		else if ((double)FOV < kViewFovMin || (double)FOV > kViewFovMax)
			{ Err = FString::Printf(TEXT("FOV must be in [%.0f,%.0f]."), kViewFovMin, kViewFovMax); }
		else if (CamOffset.GetAbsMax() > kViewOffsetMax || LookAtOffset.GetAbsMax() > kViewOffsetMax)
			{ Err = FString::Printf(TEXT("An offset component exceeds %.0f."), kViewOffsetMax); }
		else if ((LookAtOffset - CamOffset).Size() < kViewMinCamTargetDist)
			{ Err = FString::Printf(TEXT("Camera and look-at are coincident; distance must be >= %.1f."), kViewMinCamTargetDist); }
		else if ((double)TimeoutSeconds <= 0.0 || (double)TimeoutSeconds > kViewTimeoutMax)
			{ Err = FString::Printf(TEXT("TimeoutSeconds must be in (0,%.0f]."), kViewTimeoutMax); }
		else if ((double)AxisLength <= 0.0 || (double)AxisLength > kMaxAxisLength)
			{ Err = FString::Printf(TEXT("AxisLength must be in (0,%.0f] cm."), kMaxAxisLength); }
		else if (ComponentPaths.Num() != SocketNames.Num())
			{ Err = FString::Printf(TEXT("ComponentPaths (%d) and SocketNames (%d) must be the same length."), ComponentPaths.Num(), SocketNames.Num()); }
		else if (ComponentPaths.Num() == 0)
			{ Err = TEXT("At least one projection target (component path + socket name) is required."); }
		else if (ComponentPaths.Num() > kMaxProjectionTargets)
			{ Err = FString::Printf(TEXT("%d projection targets requested; the maximum is %d."), ComponentPaths.Num(), kMaxProjectionTargets); }
		if (!Err.IsEmpty()) { Result->SetError(Err); return Result; }
	}

	// Name/path bounds and duplicate pairs, checked BEFORE any object or FName resolution.
	{
		FString Err;
		TSet<FString> Seen;
		for (int32 i = 0; i < ComponentPaths.Num(); ++i)
		{
			const FString& C = ComponentPaths[i];
			const FString& N = SocketNames[i];
			if (C.TrimStartAndEnd().IsEmpty()) { Err = FString::Printf(TEXT("ComponentPaths[%d] is empty."), i); break; }
			if (C.Len() > kMaxComponentPathLen) { Err = FString::Printf(TEXT("ComponentPaths[%d] is %d characters; the maximum is %d."), i, C.Len(), kMaxComponentPathLen); break; }
			if (N.TrimStartAndEnd().IsEmpty()) { Err = FString::Printf(TEXT("SocketNames[%d] is empty."), i); break; }
			if (N.Len() > kMaxSocketNameLenProj) { Err = FString::Printf(TEXT("SocketNames[%d] is %d characters; the maximum is %d."), i, N.Len(), kMaxSocketNameLenProj); break; }
			const FString Key = C + TEXT("|") + N;
			if (Seen.Contains(Key)) { Err = FString::Printf(TEXT("Duplicate projection target: %s / %s."), *C, *N); break; }
			Seen.Add(Key);
		}
		if (!Err.IsEmpty()) { Result->SetError(Err); return Result; }
	}

	// Fail fast on identity/ownership/world/socket problems before spawning the capture rig.
	// (These are re-validated inside the rendered frame; this pass only avoids wasted work.)
	{
		FString Err;
		APawn* Pawn = Cast<APawn>(ResolveActor(PawnPath));
		if (!IsValid(Pawn) || Pawn->IsTemplate()) { Err = FString::Printf(TEXT("Pawn not found or is a CDO/template: %s"), *PawnPath); }
		else if (!IsPIEWorld(Pawn->GetWorld())) { Err = TEXT("Pawn is not in a PIE world (editor/preview rejected)."); }
		else
		{
			UWorld* World = Pawn->GetWorld();
			for (int32 i = 0; i < ComponentPaths.Num(); ++i)
			{
				USceneComponent* Comp = ResolveSceneComponent(ComponentPaths[i]);
				if (!Comp || !IsValid(Comp) || Comp->IsTemplate() || !Comp->IsRegistered())
					{ Err = FString::Printf(TEXT("Projection target component not found/usable: %s"), *ComponentPaths[i]); break; }
				if (Comp->GetOwner() != Pawn)
					{ Err = FString::Printf(TEXT("Projection target component is not owned by the supplied pawn: %s"), *ComponentPaths[i]); break; }
				if (Comp->GetWorld() != World)
					{ Err = FString::Printf(TEXT("Projection target component is in a different world than the pawn: %s"), *ComponentPaths[i]); break; }
				if (!Comp->DoesSocketExist(FName(*SocketNames[i])))
					{ Err = FString::Printf(TEXT("Socket '%s' does not exist on %s."), *SocketNames[i], *ComponentPaths[i]); break; }
			}
		}
		if (!Err.IsEmpty()) { Result->SetError(Err); return Result; }
	}

	TSharedPtr<FViewCaptureSession> V = MakeShared<FViewCaptureSession>();
	V->Result = TStrongObjectPtr<UToolCallAsyncResultString>(Result);
	V->PawnPath = PawnPath;
	V->MeshPath = MeshComponentPath;
	V->CamOffset = CamOffset;
	V->LookAtOffset = LookAtOffset;
	V->Width = Width; V->Height = Height; V->Fov = (double)FOV;
	V->Timeout = (double)TimeoutSeconds;
	V->bProjection = true;
	V->bAnnotate = bAnnotate;
	V->AxisLength = (double)AxisLength;
	V->TargetComponentPaths = ComponentPaths;
	V->TargetSocketNames = SocketNames;

	GViewCaptures.Add(V);
	TWeakPtr<FViewCaptureSession> WeakV = V;

	// SAME shared phase driver as CapturePIEPawnViewDeferred -- no second capture framework.
	V->TickHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[WeakV](float) -> bool { return TacticalRuntimeAnimInspection::RunViewCaptureTick(WeakV); }), 0.0f);

	return Result;
}

// =============================================================================
// IntrospectPawnWeaponSockets  (one-shot, read-only attachment/socket introspection)
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::IntrospectPawnWeaponSockets(
	const FString& PawnPath, const FString& MeshComponentPath, const FString& WeaponComponentPath, const FString& CandidateSocketName)
{
	return RunDeferredString([=](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());

		// Bound the candidate before any FName is constructed from it. Empty stays allowed
		// (candidate queries are simply skipped); non-empty uses the same length bound as the
		// transform-capture socket name.
		if (CandidateSocketName.Len() > kMaxPropertyNameLen)
		{ OutError = FString::Printf(TEXT("CandidateSocketName is %d characters; the maximum is %d."), CandidateSocketName.Len(), kMaxPropertyNameLen); return false; }

		APawn* Pawn = Cast<APawn>(ResolveActor(PawnPath));
		if (!IsValid(Pawn)) { OutError = FString::Printf(TEXT("Pawn not found: %s"), *PawnPath); return false; }
		if (Pawn->IsTemplate()) { OutError = TEXT("Pawn is a CDO/template."); return false; }
		UWorld* World = Pawn->GetWorld();
		if (!IsPIEWorld(World)) { OutError = TEXT("Pawn is not in a PIE world (editor/preview rejected)."); return false; }

		USkeletalMeshComponent* Mesh = ResolveMeshComponent(MeshComponentPath);
		if (!Mesh) { OutError = FString::Printf(TEXT("Skeletal-mesh component not found: %s"), *MeshComponentPath); return false; }
		if (!IsUsableMesh(Mesh)) { OutError = TEXT("Mesh is not a live/registered PIE component."); return false; }
		if (Mesh->GetOwner() != Pawn) { OutError = FString::Printf(TEXT("Mesh not owned by the supplied pawn: owner=%s."), *GetPathNameSafe(Mesh->GetOwner())); return false; }
		if (Mesh->GetWorld() != World) { OutError = TEXT("Mesh is in a different world than the pawn."); return false; }

		USceneComponent* Weapon = ResolveSceneComponent(WeaponComponentPath);
		if (!Weapon) { OutError = FString::Printf(TEXT("Weapon component not found: %s"), *WeaponComponentPath); return false; }
		if (!IsValid(Weapon) || Weapon->IsTemplate() || !Weapon->IsRegistered() || !IsPIEWorld(Weapon->GetWorld())) { OutError = TEXT("Weapon component is not a live/registered PIE component."); return false; }
		if (Weapon->GetOwner() != Pawn) { OutError = FString::Printf(TEXT("Weapon component not owned by the supplied pawn: owner=%s."), *GetPathNameSafe(Weapon->GetOwner())); return false; }
		if (Weapon->GetWorld() != World) { OutError = TEXT("Weapon component is in a different world than the pawn."); return false; }

		// Mesh asset via reflection (static-mesh or skeletal-mesh component), read-only.
		FString MeshAsset;
		for (const TCHAR* PropName : { TEXT("StaticMesh"), TEXT("SkeletalMeshAsset"), TEXT("SkeletalMesh") })
		{
			if (FObjectProperty* OP = CastField<FObjectProperty>(Weapon->GetClass()->FindPropertyByName(FName(PropName))))
			{
				if (UObject* Asset = OP->GetObjectPropertyValue_InContainer(Weapon)) { MeshAsset = Asset->GetPathName(); break; }
			}
		}

		auto SocketNamesJson = [](USceneComponent* Comp, bool& bTruncated) -> FString
		{
			TArray<FName> Names = Comp->GetAllSocketNames();
			bTruncated = Names.Num() > kMaxSocketNames;
			const int32 N = FMath::Min(Names.Num(), kMaxSocketNames);
			FString Arr;
			for (int32 i = 0; i < N; ++i) { Arr += (i ? TEXT(",") : TEXT("")) + JStr(Names[i].ToString()); }
			return Arr;
		};
		bool bWeaponTrunc = false, bMeshTrunc = false;
		const FString WeaponSockets = SocketNamesJson(Weapon, bWeaponTrunc);
		const FString MeshSockets = SocketNamesJson(Mesh, bMeshTrunc);

		const bool bHasCandidate = !CandidateSocketName.IsEmpty();
		const FName Cand(*CandidateSocketName);
		const bool bWeaponHas = bHasCandidate && Weapon->DoesSocketExist(Cand);
		const bool bMeshHas = bHasCandidate && Mesh->DoesSocketExist(Cand);
		const FString WeaponCandXform = bWeaponHas ? XformJson(Weapon->GetSocketTransform(Cand, RTS_World)) : FString(TEXT("null"));
		const FString MeshCandXform = bMeshHas ? XformJson(Mesh->GetSocketTransform(Cand, RTS_World)) : FString(TEXT("null"));
		const FString CandJson = bHasCandidate ? JStr(CandidateSocketName) : FString(TEXT("null"));

		USceneComponent* AttachParent = Weapon->GetAttachParent();
		const FString AttachParentPath = AttachParent ? AttachParent->GetPathName() : FString();
		const FString AttachSocket = Weapon->GetAttachSocketName().ToString();
		const FString WeaponWorldXform = XformJson(Weapon->GetComponentTransform());

		AController* Ctrl = Pawn->GetController();
		const FString CtrlPath = Ctrl ? Ctrl->GetPathName() : FString();
		const bool bLocal = Pawn->IsLocallyControlled();

		OutValue = FString::Printf(
			TEXT("{\"world\":%s,\"pawn\":%s,\"meshComponent\":%s,")
			TEXT("\"weaponComponent\":{\"path\":%s,\"class\":%s,\"meshAsset\":%s,\"attachParent\":%s,\"attachSocketName\":%s,\"worldTransform\":%s},")
			TEXT("\"candidateSocket\":%s,\"weaponComponentSockets\":{\"names\":[%s],\"truncated\":%s},\"meshComponentSockets\":{\"names\":[%s],\"truncated\":%s},")
			TEXT("\"candidateOnWeapon\":{\"exists\":%s,\"socketWorldTransform\":%s},\"candidateOnMesh\":{\"exists\":%s,\"socketWorldTransform\":%s},")
			TEXT("\"controller\":%s,\"isLocallyControlled\":%s,\"localRole\":\"%s\",\"remoteRole\":\"%s\",\"limits\":{\"maxSocketNames\":%d}}"),
			*JStr(World->GetPathName()), *JStr(Pawn->GetPathName()), *JStr(Mesh->GetPathName()),
			*JStr(Weapon->GetPathName()), *JStr(Weapon->GetClass()->GetPathName()), *JStr(MeshAsset), *JStr(AttachParentPath), *JStr(AttachSocket), *WeaponWorldXform,
			*CandJson, *WeaponSockets, bWeaponTrunc ? TEXT("true") : TEXT("false"), *MeshSockets, bMeshTrunc ? TEXT("true") : TEXT("false"),
			bWeaponHas ? TEXT("true") : TEXT("false"), *WeaponCandXform, bMeshHas ? TEXT("true") : TEXT("false"), *MeshCandXform,
			*JStr(CtrlPath), bLocal ? TEXT("true") : TEXT("false"), NetRoleStr(Pawn->GetLocalRole()), NetRoleStr(Pawn->GetRemoteRole()),
			kMaxSocketNames);
		return true;
	});
}

// =============================================================================
// StartWeaponSocketTransformCapture  (frame-coherent; reuses the capture session + StopLinkedAnimInstanceCapture)
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::StartWeaponSocketTransformCapture(
	const FString& PawnPath, const FString& MeshComponentPath, const FString& TransformSourcePath, const FString& SocketName,
	const FString& HostClassPath, const FString& LayerClassPath, int32 MaxSamples, float TimeoutSeconds)
{
	return RunDeferredString([=](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());
		EnsureHooks();

		if (MaxSamples < 1 || MaxSamples > kMaxSamplesLimit) { OutError = FString::Printf(TEXT("MaxSamples must be in [1,%d]."), kMaxSamplesLimit); return false; }
		if (TimeoutSeconds <= 0.f || (double)TimeoutSeconds > kMaxTimeoutSeconds) { OutError = FString::Printf(TEXT("TimeoutSeconds must be in (0,%.0f]."), kMaxTimeoutSeconds); return false; }
		if (SocketName.IsEmpty()) { OutError = TEXT("SocketName must be explicit (non-empty)."); return false; }
		if (SocketName.Len() > kMaxPropertyNameLen) { OutError = FString::Printf(TEXT("SocketName exceeds %d characters."), kMaxPropertyNameLen); return false; }

		APawn* Pawn = Cast<APawn>(ResolveActor(PawnPath));
		if (!IsValid(Pawn) || Pawn->IsTemplate()) { OutError = FString::Printf(TEXT("Pawn not found or is a CDO/template: %s"), *PawnPath); return false; }
		UWorld* World = Pawn->GetWorld();
		if (!IsPIEWorld(World)) { OutError = TEXT("Pawn is not in a PIE world (editor/preview rejected)."); return false; }

		USkeletalMeshComponent* Mesh = ResolveMeshComponent(MeshComponentPath);
		if (!Mesh || !IsUsableMesh(Mesh)) { OutError = FString::Printf(TEXT("Finalization mesh not found/usable: %s"), *MeshComponentPath); return false; }
		if (Mesh->GetOwner() != Pawn) { OutError = TEXT("Finalization mesh is not owned by the supplied pawn."); return false; }
		if (Mesh->GetWorld() != World) { OutError = TEXT("Finalization mesh is in a different world than the pawn."); return false; }

		USceneComponent* TS = ResolveSceneComponent(TransformSourcePath);
		if (!TS || !IsValid(TS) || TS->IsTemplate() || !TS->IsRegistered() || !IsPIEWorld(TS->GetWorld())) { OutError = FString::Printf(TEXT("Transform-source component not found/usable: %s"), *TransformSourcePath); return false; }
		if (TS->GetOwner() != Pawn) { OutError = TEXT("Transform-source component is not owned by the supplied pawn."); return false; }
		if (TS->GetWorld() != World) { OutError = TEXT("Transform-source component is in a different world than the pawn."); return false; }
		if (!TS->DoesSocketExist(FName(*SocketName))) { OutError = FString::Printf(TEXT("Explicit socket '%s' does not exist on the transform-source component."), *SocketName); return false; }

		// The capsule/root component is a reported transform source (capsuleWorldRotation), so it
		// gets the same full validation as the transform source: live, non-template, registered,
		// owned by the supplied pawn, and in the same PIE world.
		USceneComponent* Capsule = nullptr;
		if (ACharacter* Char = Cast<ACharacter>(Pawn)) { Capsule = Char->GetCapsuleComponent(); }
		if (!Capsule) { Capsule = Pawn->GetRootComponent(); }
		if (!IsValid(Capsule)) { OutError = TEXT("Pawn has no capsule/root component."); return false; }
		if (Capsule->IsTemplate()) { OutError = TEXT("Capsule/root component is a CDO/template."); return false; }
		if (!Capsule->IsRegistered()) { OutError = TEXT("Capsule/root component is not registered."); return false; }
		if (!IsPIEWorld(Capsule->GetWorld())) { OutError = TEXT("Capsule/root component is not in a PIE world."); return false; }
		if (Capsule->GetOwner() != Pawn) { OutError = FString::Printf(TEXT("Capsule/root component is not owned by the supplied pawn: owner=%s."), *GetPathNameSafe(Capsule->GetOwner())); return false; }
		if (Capsule->GetWorld() != World) { OutError = TEXT("Capsule/root component is in a different world than the pawn."); return false; }

		for (auto& Pair : GSessions)
		{
			const TSharedPtr<FCaptureSession>& Existing = Pair.Value;
			if (Existing.IsValid() && Existing->bActive && Existing->Mesh.Get() == Mesh)
			{ OutError = FString::Printf(TEXT("A capture session (%s) is already active on this mesh."), *Existing->Id); return false; }
		}

		UAnimInstance* Host = Mesh->GetAnimInstance();
		if (!IsUsableAnimInstance(Host)) { OutError = TEXT("Finalization mesh has no usable host AnimInstance."); return false; }
		UClass* WantHost = ResolveAnimInstanceClass(HostClassPath);
		if (!WantHost) { OutError = FString::Printf(TEXT("Could not resolve host class: %s"), *HostClassPath); return false; }
		if (!Host->GetClass()->IsChildOf(WantHost)) { OutError = FString::Printf(TEXT("Host class mismatch: instance is %s, expected %s."), *Host->GetClass()->GetPathName(), *WantHost->GetPathName()); return false; }
		UClass* WantLayer = ResolveAnimInstanceClass(LayerClassPath);
		if (!WantLayer) { OutError = FString::Printf(TEXT("Could not resolve layer class: %s"), *LayerClassPath); return false; }
		UAnimInstance* Layer = nullptr; int32 LayerMatches = 0;
		for (UAnimInstance* L : GetLinkedInstances(Mesh)) { if (IsUsableAnimInstance(L) && L->GetClass()->IsChildOf(WantLayer)) { ++LayerMatches; Layer = L; } }
		if (LayerMatches == 0) { OutError = FString::Printf(TEXT("No linked layer instance of class %s on this mesh."), *WantLayer->GetPathName()); return false; }
		if (LayerMatches > 1) { OutError = FString::Printf(TEXT("Ambiguous: %d linked layer instances of class %s."), LayerMatches, *WantLayer->GetPathName()); return false; }

		TSharedPtr<FCaptureSession> S = MakeShared<FCaptureSession>();
		S->Id = FGuid::NewGuid().ToString(EGuidFormats::DigitsWithHyphens);
		S->World = World;
		S->Mesh = Mesh; S->Host = Host; S->Layer = Layer;
		S->ExpectedHostClass = WantHost; S->ExpectedLayerClass = WantLayer;
		S->WorldName = World->GetPathName();
		S->OwnerPath = Pawn->GetPathName();
		S->MeshPath = Mesh->GetPathName();
		S->HostInstPath = Host->GetPathName();
		S->HostClass = Host->GetClass()->GetPathName();
		S->LayerInstPath = Layer->GetPathName();
		S->LayerClass = Layer->GetClass()->GetPathName();
		S->MaxSamples = MaxSamples; S->Timeout = (double)TimeoutSeconds;
		S->StartTime = FPlatformTime::Seconds();
		S->bActive = true;
		S->bTransformMode = true;
		S->Pawn = Pawn;
		S->TransformSource = TS;
		S->TransformSourcePath = TS->GetPathName();
		S->SocketName = SocketName;
		S->Capsule = Capsule;
		S->CapsulePath = Capsule->GetPathName();

		TWeakPtr<FCaptureSession> WeakS = S;
		S->FinalizeHandle = Mesh->RegisterOnBoneTransformsFinalizedDelegate(
			FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateLambda([WeakS]() { OnBoneTransformsFinalized(WeakS); }));

		S->LifecycleHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[WeakS](float) -> bool
			{
				TSharedPtr<FCaptureSession> Sp = WeakS.Pin();
				if (!Sp.IsValid() || !Sp->bActive) { return false; }
				UWorld* W = Sp->World.Get();
				USkeletalMeshComponent* M = Sp->Mesh.Get();
				UAnimInstance* H = Sp->Host.Get();
				UAnimInstance* L = Sp->Layer.Get();
				USceneComponent* TSp = Sp->TransformSource.Get();
				APawn* P = Sp->Pawn.Get();
				if (!IsPIEWorld(W) || !IsUsableMesh(M) || !IsUsableAnimInstance(H) || !IsUsableAnimInstance(L)
					|| M->GetAnimInstance() != H || !LayerStillPresent(M, L)
					|| !IsValid(P) || !IsPIEWorld(P->GetWorld())
					|| !IsValid(TSp) || !TSp->IsRegistered() || TSp->GetOwner() != P)
				{
					StopSession(Sp, TEXT("invalidated (lifecycle)")); return false;
				}
				if ((FPlatformTime::Seconds() - Sp->StartTime) >= Sp->Timeout)
				{
					StopSession(Sp, TEXT("timeout")); return false;
				}
				return true;
			}), kLifecycleTickInterval);

		GSessions.Add(S->Id, S);

		OutValue = FString::Printf(
			TEXT("{\"sessionId\":%s,\"mode\":\"transform\",\"world\":%s,\"owner\":%s,\"meshComponent\":%s,\"transformSource\":%s,\"socket\":%s,")
			TEXT("\"hostAnimInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,\"capsuleComponent\":%s,\"maxSamples\":%d,\"timeoutSeconds\":%.3f}"),
			*JStr(S->Id), *JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath), *JStr(S->TransformSourcePath), *JStr(S->SocketName),
			*JStr(S->HostInstPath), *JStr(S->HostClass), *JStr(S->LayerInstPath), *JStr(S->LayerClass), *JStr(S->CapsulePath), MaxSamples, TimeoutSeconds);
		return true;
	});
}

// =============================================================================
// CapturePIEPawnViewDeferred
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::CapturePIEPawnViewDeferred(
	const FString& PawnPath, const FString& MeshComponentPath,
	float CameraOffsetX, float CameraOffsetY, float CameraOffsetZ,
	float LookAtOffsetX, float LookAtOffsetY, float LookAtOffsetZ,
	int32 Width, int32 Height, float FOV, float TimeoutSeconds)
{
	using namespace TacticalRuntimeAnimInspection;

	UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();

	// Reject an overlapping call BEFORE any session is allocated or scheduled.
	if (GViewCaptures.Num() >= kMaxConcurrentViewCaptures)
	{
		Result->SetError(FString::Printf(TEXT("A pawn-view capture is already in progress; at most %d concurrent CapturePIEPawnViewDeferred session(s) allowed."), kMaxConcurrentViewCaptures));
		return Result;
	}

	// All numeric validation happens up front, BEFORE registering a session (non-finite, bounds, coincident vectors).
	const FVector CamOffset(CameraOffsetX, CameraOffsetY, CameraOffsetZ);
	const FVector LookAtOffset(LookAtOffsetX, LookAtOffsetY, LookAtOffsetZ);
	{
		FString Err;
		if (!FMath::IsFinite(CameraOffsetX) || !FMath::IsFinite(CameraOffsetY) || !FMath::IsFinite(CameraOffsetZ)
			|| !FMath::IsFinite(LookAtOffsetX) || !FMath::IsFinite(LookAtOffsetY) || !FMath::IsFinite(LookAtOffsetZ))
			{ Err = TEXT("Camera/look-at offset components must be finite."); }
		else if (!FMath::IsFinite(FOV)) { Err = TEXT("FOV must be finite."); }
		else if (!FMath::IsFinite(TimeoutSeconds)) { Err = TEXT("TimeoutSeconds must be finite."); }
		else if (Width < kViewMinDim || Width > kViewMaxDim || Height < kViewMinDim || Height > kViewMaxDim)
			{ Err = FString::Printf(TEXT("Width/Height must be in [%d,%d]."), kViewMinDim, kViewMaxDim); }
		else if ((int64)Width * (int64)Height > kViewMaxPixels)
			{ Err = FString::Printf(TEXT("Width*Height exceeds %lld pixels."), kViewMaxPixels); }
		else if ((double)FOV < kViewFovMin || (double)FOV > kViewFovMax)
			{ Err = FString::Printf(TEXT("FOV must be in [%.0f,%.0f]."), kViewFovMin, kViewFovMax); }
		else if (CamOffset.GetAbsMax() > kViewOffsetMax || LookAtOffset.GetAbsMax() > kViewOffsetMax)
			{ Err = FString::Printf(TEXT("An offset component exceeds %.0f."), kViewOffsetMax); }
		else if ((LookAtOffset - CamOffset).Size() < kViewMinCamTargetDist)
			{ Err = FString::Printf(TEXT("Camera and look-at are coincident; distance must be >= %.1f."), kViewMinCamTargetDist); }
		else if ((double)TimeoutSeconds <= 0.0 || (double)TimeoutSeconds > kViewTimeoutMax)
			{ Err = FString::Printf(TEXT("TimeoutSeconds must be in (0,%.0f]."), kViewTimeoutMax); }
		if (!Err.IsEmpty()) { Result->SetError(Err); return Result; }
	}

	TSharedPtr<FViewCaptureSession> V = MakeShared<FViewCaptureSession>();
	V->Result = TStrongObjectPtr<UToolCallAsyncResultString>(Result);
	V->PawnPath = PawnPath;
	V->MeshPath = MeshComponentPath;
	V->CamOffset = CamOffset;
	V->LookAtOffset = LookAtOffset;
	V->Width = Width; V->Height = Height; V->Fov = (double)FOV;
	V->Timeout = (double)TimeoutSeconds;

	GViewCaptures.Add(V);
	TWeakPtr<FViewCaptureSession> WeakV = V;

	// Object resolution, spawn, capture, readback, and cleanup all run on the game thread.
	V->TickHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[WeakV](float) -> bool { return TacticalRuntimeAnimInspection::RunViewCaptureTick(WeakV); }), 0.0f);

	return Result;
}

// =============================================================================
// ShutdownAllSessions
// =============================================================================
void UTacticalRuntimeAnimInspectionToolset::ShutdownAllSessions()
{
	StopAll(TEXT("module shutdown"));
	GSessions.Reset();
	GViewCaptures.Reset();
	if (GHooksRegistered)
	{
		FEditorDelegates::EndPIE.Remove(GEndPIEHandle);
		FWorldDelegates::OnWorldCleanup.Remove(GWorldCleanupHandle);
		GHooksRegistered = false;
	}
}
