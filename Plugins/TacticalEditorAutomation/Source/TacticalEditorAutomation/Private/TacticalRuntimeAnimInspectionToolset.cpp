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
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
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
	static const int32  kMaxSocketNames = 256;

	// ---- combined capture + bounded render-liveness pump (Boundary G Phase 1) ----
	static const int32  kMinPumpHz = 1;
	static const int32  kMaxPumpHz = 60;
	static const int32  kMinPumpDim = 64;
	static const int32  kMaxPumpDim = 256;
	static const int32  kDefaultPumpDim = 128;
	// Per-sample cap on serialized scalar READ-ERROR entries (host+layer combined). Unrelated to
	// socket-name introspection; overflow is reported via readErrorsTruncated, never silently dropped.
	static const int32  kMaxReadErrorsPerSample = 32;
	// Object-path bound, enforced BEFORE StaticFindObject/class resolution and before any allocation.
	static const int32  kMaxObjectPathLen = 512;
	// Socket-basis validation tolerances. Values are VALIDATED, never normalized/repaired/substituted.
	static const double kBasisUnitTolerance  = 1.0e-3;  // | |axis| - 1 |
	static const double kBasisOrthoTolerance = 1.0e-3;  // |dot(a,b)| for distinct axes
	// Right-handed check for the socket basis: dot(cross(X,Y),Z) must exceed this.
	static const double kBasisHandednessMin  = 0.5;

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

		// --- combined mode (Boundary G Phase 1): host/layer scalars AND socket transform/basis emitted
		// inside ONE finalized-frame callback, so correlation is structural (never a post-hoc join). ---
		bool bCombinedMode = false;
		// Exact weapon/static-mesh identity pinned at start; revalidated before EVERY combined sample
		// and on every lifecycle tick. A same-component asset swap is drift, not a silent empty field.
		TWeakObjectPtr<UStaticMeshComponent> WeaponComp;
		TWeakObjectPtr<UStaticMesh> ExpectedStaticMesh;
		FString WeaponCompPath, StaticMeshPath;

		// --- bounded render-liveness pump. OBSERVES ONLY: it renders the mesh through a separate
		// transient SceneCapture and never mutates bOwnerNoSee/bOnlyOwnerSee/bVisible/bHiddenInGame/
		// VisibilityBasedAnimTickOption/bNoSkeletonUpdate/tick settings/cameras/possession. ---
		bool bPumpOwned = false;   // true only while this session holds the ONE global pump slot
		FString PumpMode, PumpIsolation;
		int32 PumpHz = 0, PumpW = 0, PumpH = 0;
		int64 PumpRequestCount = 0;
		uint64 PumpFirstFrame = 0, PumpLastFrame = 0;
		double PumpFirstTime = 0.0, PumpLastTime = 0.0;
		TStrongObjectPtr<AActor> PumpActor;
		TStrongObjectPtr<USceneCaptureComponent2D> PumpCapture;
		TStrongObjectPtr<UTextureRenderTarget2D> PumpRT;
		FTSTicker::FDelegateHandle PumpHandle;
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

		// ---- A2 aim-hold extension (unused by DrivePIEInputSequenceDeferred) ----
		bool bAimHold = false;
		TWeakObjectPtr<UInputAction> LookAction;
		TWeakObjectPtr<APlayerController> Controller;
		FString LookActionProperty, ControllerPath, LocalPlayerPath, WorldName;
		double TargetPitch = 0.0, TargetYaw = 0.0, Tolerance = 0.0, HoldSeconds = 0.0;
		int32 MaxIterations = 0, Iterations = 0;
		FRotator InitialAim = FRotator::ZeroRotator, AchievedAim = FRotator::ZeroRotator, FinalAim = FRotator::ZeroRotator;
		bool bConverged = false;
		double ConvergedAt = -1.0, HoldStartAt = -1.0, HoldEndAt = -1.0;
		double MaxPitchErrHold = 0.0, MaxYawErrHold = 0.0;
		bool bTraceTruncated = false;
		TWeakObjectPtr<UWorld> AimWorld;
		TWeakObjectPtr<ULocalPlayer> LocalPlayer;
		FString LookActionPath, MoveActionPath;
		bool bMoveStopCalled = false;   // true ONLY when StopContinuousInputInjectionForAction actually ran
		FString FailureReason;
		// Local-control / role evidence captured under PROVEN identity (registration, then refreshed on each
		// identity-valid tick). The A2 finalizer serializes these and never dereferences the pawn.
		// ---- per-session response calibration state/evidence ----
		bool bCalibrated = false;
		bool bCalibInitialized = false;
		int32 CalAxis = 0;                 // 0 = yaw, 1 = pitch
		bool bAwaitingProbe = false;
		// responseObserved is the ONLY proof a sign was measured; a skipped or unfinished axis keeps a
		// placeholder sign of +1 that must never be used to correct.
		bool bYawResponseObserved = false, bPitchResponseObserved = false;
		bool bYawCalRequired = false, bPitchCalRequired = false;
		bool bYawCalDone = false, bPitchCalDone = false;
		int32 YawProbeAttempts = 0, PitchProbeAttempts = 0;
		double YawResponseSign = 1.0, PitchResponseSign = 1.0;
		double ProbeBaseYaw = 0.0, ProbeBasePitch = 0.0;
		double YawProbeInput = 0.0, PitchProbeInput = 0.0;
		double YawProbeDelta = 0.0, PitchProbeDelta = 0.0;
		bool bAimLocallyControlled = false;
		FString AimLocalRole = TEXT("None"), AimRemoteRole = TEXT("None");
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

	// At most ONE render-pumped session globally (Phase 1 instrument bound). Ordinary A1 view captures
	// are tracked separately in GViewCaptures, so one remains possible alongside a pumped session.
	static bool GPumpActive = false;
	// ---- A2 aim-hold hard bounds ----
	static const int32  kAimMaxPawnPathLen = 512;
	static const int32  kAimMaxActionNameLen = 128;
	static const double kAimMaxAbsPitch = 89.0;
	static const double kAimMaxAbsYaw = 180.0;
	static const double kAimMinTolerance = 0.1;
	static const double kAimMaxTolerance = 10.0;
	static const int32  kAimMaxIterations = 240;
	static const double kAimMinHoldSeconds = 0.1;
	static const double kAimMaxHoldSeconds = 30.0;
	static const double kAimMaxTimeoutSeconds = 60.0;
	// ---- A2 response calibration (empirical; NEVER derived from config or deprecated scales) ----
	static const double kAimProbeMagnitude = 0.25;          // bounded one-tick probe input per axis
	static const double kAimMinMeasurableResponseDeg = 0.05;// minimum |delta| accepted as a real response
	static const int32  kAimMaxProbeAttempts = 2;           // per axis: initial probe + one opposite probe
	static const int32  kAimMaxTraceEntries = 240;
	static const int32  kAimMaxResponseBytes = 1024 * 1024; // complete UTF-8 response

	static TArray<TSharedPtr<FDriveState>> GDrives;
	static TArray<TSharedPtr<FViewCaptureSession>> GViewCaptures;
	static bool GHooksRegistered = false;
	static FDelegateHandle GEndPIEHandle;
	static FDelegateHandle GWorldCleanupHandle;

	// Releases the pump ticker, its transient render objects, and the ONE global pump slot.
	// Idempotent and unconditional, so it is safe on EVERY exit path: start rollback, caller stop,
	// identity drift, timeout, max samples, result-size cap, EndPIE, world cleanup, module shutdown.
	static void DestroyPumpTransients(const TSharedPtr<FCaptureSession>& S)
	{
		if (!S.IsValid()) { return; }
		if (S->PumpHandle.IsValid()) { FTSTicker::GetCoreTicker().RemoveTicker(S->PumpHandle); S->PumpHandle.Reset(); }
		// During EndPIE / world destruction the transients may already be torn down or pending kill,
		// so every engine call is IsValid-gated. Pointers and the global slot are released regardless.
		if (USceneCaptureComponent2D* Cap = S->PumpCapture.Get())
		{
			if (IsValid(Cap))
			{
				Cap->ShowOnlyComponents.Empty();
				Cap->TextureTarget = nullptr;
				Cap->DestroyComponent();
			}
		}
		S->PumpCapture.Reset();
		if (AActor* Actor = S->PumpActor.Get())
		{
			if (IsValid(Actor)) { Actor->Destroy(); }
		}
		S->PumpActor.Reset();
		S->PumpRT.Reset(); // sole strong ref released -> eligible for GC
		if (S->bPumpOwned) { S->bPumpOwned = false; GPumpActive = false; }
	}

	// Teardown ORDER is load-bearing: the session is marked inactive FIRST, so a finalized-frame
	// callback or either ticker that fires during destruction returns immediately and cannot sample
	// a half-destroyed rig. The first stop reason always wins. Idempotent and safe from either
	// ticker, EndPIE, world cleanup, start rollback, or module shutdown.
	static void StopSession(const TSharedPtr<FCaptureSession>& S, const FString& Reason)
	{
		if (!S.IsValid()) { return; }
		const bool bWasActive = S->bActive;
		S->bActive = false;                                             // 1. no further sampling
		if (S->StopReason.IsEmpty() && !Reason.IsEmpty()) { S->StopReason = Reason; }  // 2. first reason wins
		if (bWasActive)
		{
			if (USkeletalMeshComponent* Mesh = S->Mesh.Get())           // 3. finalized-frame delegate
			{ Mesh->UnregisterOnBoneTransformsFinalizedDelegate(S->FinalizeHandle); }
		}
		S->FinalizeHandle.Reset();
		if (S->LifecycleHandle.IsValid())                               // 4. lifecycle ticker
		{ FTSTicker::GetCoreTicker().RemoveTicker(S->LifecycleHandle); S->LifecycleHandle.Reset(); }
		DestroyPumpTransients(S);                                       // 5. pump ticker + transients + slot
	}

	static void StopDriveInjection(const TSharedPtr<FDriveState>& D)
	{
		if (!D.IsValid()) { return; }
		if (UEnhancedInputLocalPlayerSubsystem* Sub = D->Subsystem.Get())
		{
			if (D->bReadinessInjecting) { if (UInputAction* A = D->ReadinessAction.Get()) { Sub->StopContinuousInputInjectionForAction(A); } D->bReadinessInjectionStopped = true; }
			if (D->bMoveInjecting) { if (UInputAction* A = D->MoveAction.Get()) { Sub->StopContinuousInputInjectionForAction(A); D->bMoveStopCalled = true; } D->bMoveInjectionStopped = true; }
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

		if (D->bAimHold)
		{
			// The A2 finalizer NEVER dereferences the pawn: it can run after identity drift, EndPIE or
			// world cleanup. Every feedback value -- aim, local control, and roles -- was captured on a
			// tick whose EXACT identity was proven valid (the success path refreshes them immediately
			// after the hold completes, while that tick's identity is still proven).
			// SIGN CONVENTION: errors are TARGET MINUS CURRENT, matching the corrective-injection and
			// trace convention, so a positive error means the aim must increase along that axis.
			const double FinalPitchErr = D->TargetPitch - D->FinalAim.Pitch;
			const double FinalYawErr = FRotator::NormalizeAxis(D->TargetYaw - D->FinalAim.Yaw);
			const bool bFinalOk = FMath::Abs(FinalPitchErr) <= D->Tolerance && FMath::Abs(FinalYawErr) <= D->Tolerance;
			const bool bHoldDone = D->HoldEndAt >= 0.0;
			const double HoldActual = (D->HoldStartAt >= 0.0 && D->HoldEndAt >= 0.0) ? (D->HoldEndAt - D->HoldStartAt) : 0.0;
			// Injection ownership: "stopped" requires the Stop call to have ACTUALLY run.
			const bool bAllStopped = !D->bMoveInjecting && (!D->bMoveInjectionStarted || D->bMoveStopCalled);
			const bool bSpeedUp = D->bMoveRequested && (D->MaxSpeed > D->SpeedBefore + 1.0);
			const bool bMoveOk = !D->bMoveRequested || (D->bMoveInjectionStarted && D->bMoveStopCalled && bSpeedUp);
			const bool bCompleted = (StopReason == TEXT("completed"));
			// Defense in depth: success additionally requires a fully resolved calibration phase, with an
			// observed response sign for every axis that required one.
			const bool bCalibrationOk = D->bCalibInitialized && D->bCalibrated
				&& (!D->bYawCalRequired || D->bYawResponseObserved)
				&& (!D->bPitchCalRequired || D->bPitchResponseObserved);
			const bool bSuccess = D->bConverged && bHoldDone && bFinalOk && bAllStopped && bMoveOk && bCompleted && bCalibrationOk;

			// A specific failure reason derived from the criterion that actually failed.
			FString FailureReason = D->FailureReason;
			if (!bSuccess && FailureReason.IsEmpty())
			{
				if (!bCompleted)                 { FailureReason = StopReason; }
				else if (!D->bConverged)         { FailureReason = TEXT("did not converge within tolerance"); }
				else if (!bHoldDone)             { FailureReason = TEXT("hold phase did not complete"); }
				else if (!bFinalOk)              { FailureReason = TEXT("final aim outside tolerance"); }
				else if (!bAllStopped)           { FailureReason = TEXT("continuous injection was not verifiably stopped"); }
				else if (!D->bMoveInjectionStarted) { FailureReason = TEXT("movement injection never started"); }
				else if (!D->bMoveStopCalled)    { FailureReason = TEXT("movement injection stop was not called"); }
				else if (!bSpeedUp)              { FailureReason = TEXT("no material 2D speed increase during movement"); }
				else if (!bCalibrationOk)        { FailureReason = TEXT("response calibration incomplete or a required axis sign was never observed"); }
				else                             { FailureReason = TEXT("unknown failure"); }
			}

			FString TraceJson;
			const int32 N = FMath::Min(D->Steps.Num(), kAimMaxTraceEntries);
			for (int32 i = 0; i < N; ++i) { TraceJson += FString::Printf(TEXT("%s%s"), (i ? TEXT(",") : TEXT("")), *JStr(D->Steps[i])); }

			const FString IdentityJson = FString::Printf(
				TEXT("\"pawn\":%s,\"controller\":%s,\"localPlayer\":%s,\"world\":%s,")
				TEXT("\"lookActionProperty\":%s,\"lookAction\":%s,\"moveActionProperty\":%s,\"moveAction\":%s,")
				TEXT("\"isLocallyControlled\":%s,\"localRole\":\"%s\",\"remoteRole\":\"%s\""),
				*JStr(D->PawnPath), *JStr(D->ControllerPath), *JStr(D->LocalPlayerPath), *JStr(D->WorldName),
				*JStr(D->LookActionProperty), *JStr(D->LookActionPath),
				*JStr(D->MoveActionProperty), *JStr(D->MoveActionPath),
				D->bAimLocallyControlled ? TEXT("true") : TEXT("false"),
				*D->AimLocalRole, *D->AimRemoteRole);

			const FString CriteriaJson = FString::Printf(
				TEXT("\"converged\":%s,\"convergedAtSeconds\":%.3f,\"iterations\":%d,")
				TEXT("\"holdSeconds\":%.3f,\"holdActualSeconds\":%.3f,\"holdCompleted\":%s,")
				TEXT("\"finalPitchError\":%.6f,\"finalYawError\":%.6f,\"finalWithinTolerance\":%s,")
				TEXT("\"moveRequested\":%s,\"moveInjectionStarted\":%s,\"moveInjectionStopCalled\":%s,")
				TEXT("\"speedBefore\":%.3f,\"maxSpeed\":%.3f,\"speedIncreased\":%s,\"allInjectionsStopped\":%s"),
				D->bConverged ? TEXT("true") : TEXT("false"), D->ConvergedAt, D->Iterations,
				D->HoldSeconds, HoldActual, bHoldDone ? TEXT("true") : TEXT("false"),
				FinalPitchErr, FinalYawErr, bFinalOk ? TEXT("true") : TEXT("false"),
				D->bMoveRequested ? TEXT("true") : TEXT("false"),
				D->bMoveInjectionStarted ? TEXT("true") : TEXT("false"),
				D->bMoveStopCalled ? TEXT("true") : TEXT("false"),
				D->SpeedBefore, D->MaxSpeed, bSpeedUp ? TEXT("true") : TEXT("false"),
				bAllStopped ? TEXT("true") : TEXT("false"))
				+ FString::Printf(
					TEXT(",\"calibration\":{\"calibrated\":%s,\"calibrationInitialized\":%s,")
					TEXT("\"yaw\":{\"required\":%s,\"responseObserved\":%s,\"probeInput\":%.4f,\"observedDeltaDegrees\":%.4f,\"responseSign\":%.0f,\"probeAttempts\":%d},")
					TEXT("\"pitch\":{\"required\":%s,\"responseObserved\":%s,\"probeInput\":%.4f,\"observedDeltaDegrees\":%.4f,\"responseSign\":%.0f,\"probeAttempts\":%d},")
					TEXT("\"source\":%s,\"limits\":{\"probeMagnitude\":%.3f,\"minMeasurableResponseDegrees\":%.3f,\"maxProbeAttemptsPerAxis\":%d}}"),
					D->bCalibrated ? TEXT("true") : TEXT("false"), D->bCalibInitialized ? TEXT("true") : TEXT("false"),
					D->bYawCalRequired ? TEXT("true") : TEXT("false"), D->bYawResponseObserved ? TEXT("true") : TEXT("false"),
					D->YawProbeInput, D->YawProbeDelta, D->YawResponseSign, D->YawProbeAttempts,
					D->bPitchCalRequired ? TEXT("true") : TEXT("false"), D->bPitchResponseObserved ? TEXT("true") : TEXT("false"),
					D->PitchProbeInput, D->PitchProbeDelta, D->PitchResponseSign, D->PitchProbeAttempts,
					*JStr(TEXT("empirically observed via bounded InjectInputForAction probes; NOT derived from configuration or deprecated controller scales")),
					kAimProbeMagnitude, kAimMinMeasurableResponseDeg, kAimMaxProbeAttempts);

			FString Payload = FString::Printf(
				TEXT("{%s,\"initialAim\":%s,\"targetAim\":{\"pitch\":%.6f,\"yaw\":%.6f},\"achievedAim\":%s,\"finalAim\":%s,")
				TEXT("\"errorSignConvention\":%s,%s,\"maxPitchErrorDuringHold\":%.6f,\"maxYawErrorDuringHold\":%.6f,")
				TEXT("\"success\":%s,\"stopReason\":%s,\"failureReason\":%s,\"trace\":[%s],\"traceTruncated\":%s,")
				TEXT("\"evidenceDropped\":false,\"limits\":{\"maxIterations\":%d,\"maxTraceEntries\":%d,\"maxResponseBytes\":%d}}"),
				*IdentityJson, *RotJson(D->InitialAim), D->TargetPitch, D->TargetYaw,
				*RotJson(D->AchievedAim), *RotJson(D->FinalAim),
				*JStr(TEXT("error = target - current (positive means the aim must increase on that axis)")),
				*CriteriaJson, D->MaxPitchErrHold, D->MaxYawErrHold,
				bSuccess ? TEXT("true") : TEXT("false"), *JStr(StopReason),
				bSuccess ? *JStr(FString()) : *JStr(FailureReason), *TraceJson,
				(D->bTraceTruncated || D->Steps.Num() > kAimMaxTraceEntries) ? TEXT("true") : TEXT("false"),
				kAimMaxIterations, kAimMaxTraceEntries, kAimMaxResponseBytes);

			bool bEvidenceDropped = false;
			if (FTCHARToUTF8(*Payload).Length() > kAimMaxResponseBytes)
			{
				// The full payload does not fit. This is a DELIBERATE EVIDENCE DROP, not ordinary
				// truncation: identity, cleanup proof, success criteria and the failure reason are
				// preserved; the trace is discarded and the drop is reported explicitly.
				bEvidenceDropped = true;
				Payload = FString::Printf(
					TEXT("{%s,%s,\"success\":%s,\"stopReason\":%s,\"failureReason\":%s,\"trace\":[],\"traceTruncated\":true,")
					TEXT("\"evidenceDropped\":true,\"evidenceDropReason\":%s,\"limits\":{\"maxResponseBytes\":%d}}"),
					*IdentityJson, *CriteriaJson, bSuccess ? TEXT("true") : TEXT("false"), *JStr(StopReason),
					*JStr(bSuccess ? FString(TEXT("response exceeded the cap; trace deliberately discarded")) : FailureReason),
					*JStr(TEXT("full payload exceeded maxResponseBytes; trace deliberately discarded to preserve identity, cleanup proof and criteria")),
					kAimMaxResponseBytes);
			}

			// SetValue ONLY when the computed success result is true; every semantic failure -- and any
			// deliberate evidence drop -- returns through SetError with the bounded evidence payload.
			if (D->Result.IsValid())
			{
				if (bSuccess && !bEvidenceDropped) { D->Result->SetValue(Payload); }
				else { D->Result->SetError(Payload); }
			}
			D->Result.Reset();
			GDrives.Remove(D);
			return;
		}

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

	static bool IsFiniteVec(const FVector& V) { return FMath::IsFinite(V.X) && FMath::IsFinite(V.Y) && FMath::IsFinite(V.Z); }
	static bool IsFiniteRot(const FRotator& R) { return FMath::IsFinite(R.Pitch) && FMath::IsFinite(R.Yaw) && FMath::IsFinite(R.Roll); }
	static bool IsFiniteXform(const FTransform& T)
	{
		const FQuat Q = T.GetRotation();
		return IsFiniteVec(T.GetLocation()) && IsFiniteVec(T.GetScale3D())
			&& FMath::IsFinite(Q.X) && FMath::IsFinite(Q.Y) && FMath::IsFinite(Q.Z) && FMath::IsFinite(Q.W);
	}

	// Exact weapon/static-mesh identity. Returns false with a SPECIFIC drift reason; a same-component
	// asset replacement is reported distinctly from an unregistered/reparented/destroyed component.
	static bool ValidateWeaponIdentity(const TSharedPtr<FCaptureSession>& S, FString& OutReason)
	{
		UWorld* World = S->World.Get();
		APawn* Pawn = S->Pawn.Get();
		UStaticMeshComponent* WC = S->WeaponComp.Get();
		if (!IsValid(WC) || WC->IsTemplate()) { OutReason = TEXT("weapon static-mesh component destroyed/invalid"); return false; }
		if (!WC->IsRegistered()) { OutReason = TEXT("weapon static-mesh component unregistered"); return false; }
		if (WC->GetWorld() != World) { OutReason = TEXT("weapon static-mesh component moved to a different world"); return false; }
		if (WC->GetOwner() != Pawn) { OutReason = TEXT("weapon static-mesh component ownership changed"); return false; }
		if (S->TransformSource.Get() != WC) { OutReason = TEXT("transform source no longer the stored weapon component"); return false; }
		if (ResolveSceneComponent(S->TransformSourcePath) != WC) { OutReason = TEXT("stored transform-source path resolves to a different component"); return false; }
		UStaticMesh* Expected = S->ExpectedStaticMesh.Get();
		if (!IsValid(Expected)) { OutReason = TEXT("expected static-mesh asset became invalid"); return false; }
		if (WC->GetStaticMesh() != Expected) { OutReason = TEXT("weapon component static-mesh asset was replaced"); return false; }
		if (!WC->DoesSocketExist(FName(*S->SocketName))) { OutReason = TEXT("explicit socket no longer exists on the weapon component"); return false; }
		return true;
	}

	// Single shared core-identity gate for the combined session. Used by BuildCombinedSample, the
	// combined lifecycle ticker AND ValidatePumpRig, so all three enforce EXACTLY the same contract
	// regardless of renderPumpMode ("none" and "showOnly" alike). Each drift returns ONE specific
	// reason; the pump layers only its rig-specific checks on top of this.
	static bool ValidateCombinedCoreIdentity(const TSharedPtr<FCaptureSession>& S, FString& OutReason)
	{
		UWorld* World = S->World.Get();
		if (!IsPIEWorld(World)) { OutReason = TEXT("stored PIE world is no longer valid"); return false; }

		APawn* Pawn = S->Pawn.Get();
		if (!IsValid(Pawn) || Pawn->IsTemplate()) { OutReason = TEXT("stored pawn invalid or is a CDO/template"); return false; }
		if (Pawn->GetWorld() != World) { OutReason = TEXT("stored pawn is no longer in the stored PIE world"); return false; }
		if (ResolveActor(S->OwnerPath) != Pawn) { OutReason = TEXT("stored pawn path resolves to a different actor"); return false; }

		USkeletalMeshComponent* Mesh = S->Mesh.Get();
		if (!IsUsableMesh(Mesh)) { OutReason = TEXT("stored skeletal mesh component is not live/registered"); return false; }
		if (Mesh->GetWorld() != World) { OutReason = TEXT("stored skeletal mesh is no longer in the stored PIE world"); return false; }
		if (Mesh->GetOwner() != Pawn) { OutReason = TEXT("stored skeletal mesh ownership changed"); return false; }
		if (ResolveMeshComponent(S->MeshPath) != Mesh) { OutReason = TEXT("stored mesh path resolves to a different component"); return false; }

		UAnimInstance* Host = S->Host.Get();
		UAnimInstance* Layer = S->Layer.Get();
		if (!IsUsableAnimInstance(Host)) { OutReason = TEXT("stored host AnimInstance is no longer usable"); return false; }
		if (Mesh->GetAnimInstance() != Host) { OutReason = TEXT("mesh host AnimInstance changed"); return false; }
		if (!IsUsableAnimInstance(Layer)) { OutReason = TEXT("stored linked layer AnimInstance is no longer usable"); return false; }
		if (!LayerStillPresent(Mesh, Layer)) { OutReason = TEXT("linked layer instance removed/replaced"); return false; }

		UClass* ExpHost = S->ExpectedHostClass.Get();
		UClass* ExpLayer = S->ExpectedLayerClass.Get();
		if (!ExpHost || !ExpLayer) { OutReason = TEXT("expected host/layer class became invalid"); return false; }
		if (!Host->GetClass()->IsChildOf(ExpHost)) { OutReason = TEXT("host class no longer matches expected"); return false; }
		if (!Layer->GetClass()->IsChildOf(ExpLayer)) { OutReason = TEXT("layer class no longer matches expected"); return false; }

		USceneComponent* Capsule = S->Capsule.Get();
		if (!IsValid(Capsule) || Capsule->IsTemplate()) { OutReason = TEXT("capsule/root component invalid or is a CDO/template"); return false; }
		if (!Capsule->IsRegistered()) { OutReason = TEXT("capsule/root component unregistered"); return false; }
		if (Capsule->GetWorld() != World) { OutReason = TEXT("capsule/root component is no longer in the stored PIE world"); return false; }
		if (Capsule->GetOwner() != Pawn) { OutReason = TEXT("capsule/root component ownership changed"); return false; }
		if (ResolveSceneComponent(S->CapsulePath) != Capsule) { OutReason = TEXT("stored capsule path resolves to a different component"); return false; }

		return ValidateWeaponIdentity(S, OutReason);
	}

	// Pump framing derived ONLY from the live mesh bounds; every derived value is finite-checked.
	static bool ComputePumpFraming(USkeletalMeshComponent* Mesh, FVector& OutCamPos, FVector& OutLookDir, FString& OutReason)
	{
		const FBoxSphereBounds Bnd = Mesh->Bounds;
		if (!IsFiniteVec(Bnd.Origin) || !FMath::IsFinite((double)Bnd.SphereRadius) || Bnd.SphereRadius <= 0.0f)
		{ OutReason = TEXT("mesh bounds are degenerate or non-finite"); return false; }
		const double Dist = FMath::Max(200.0, (double)Bnd.SphereRadius * 3.0);
		if (!FMath::IsFinite(Dist)) { OutReason = TEXT("computed pump distance is non-finite"); return false; }
		const FVector CamPos = Bnd.Origin + FVector(Dist, Dist, Dist * 0.5);
		if (!IsFiniteVec(CamPos)) { OutReason = TEXT("computed pump camera position is non-finite"); return false; }
		const FVector Look = Bnd.Origin - CamPos;
		if (!IsFiniteVec(Look) || Look.IsNearlyZero()) { OutReason = TEXT("pump look direction is non-finite or degenerate"); return false; }
		OutCamPos = CamPos; OutLookDir = Look;
		return true;
	}

	// Full pump rig + identity revalidation required before EVERY CaptureScene request.
	static bool ValidatePumpRig(const TSharedPtr<FCaptureSession>& S, FVector& OutCamPos, FVector& OutLookDir, FString& OutReason)
	{
		// Shared core-identity contract first; the rig-specific checks below are additive only.
		if (!ValidateCombinedCoreIdentity(S, OutReason)) { return false; }
		UWorld* World = S->World.Get();
		USkeletalMeshComponent* Mesh = S->Mesh.Get();

		AActor* Actor = S->PumpActor.Get();
		USceneCaptureComponent2D* Cap = S->PumpCapture.Get();
		UTextureRenderTarget2D* RT = S->PumpRT.Get();
		if (!IsValid(Actor)) { OutReason = TEXT("pump: transient capture actor invalid"); return false; }
		if (!Actor->HasAnyFlags(RF_Transient)) { OutReason = TEXT("pump: capture actor lost its transient flag"); return false; }
		if (Actor->GetWorld() != World) { OutReason = TEXT("pump: capture actor is in a different world"); return false; }
		if (Actor->GetOwner() != nullptr) { OutReason = TEXT("pump: capture actor acquired an owner (must stay unowned)"); return false; }
		if (!IsValid(Cap)) { OutReason = TEXT("pump: capture component invalid"); return false; }
		if (!Cap->IsRegistered()) { OutReason = TEXT("pump: capture component unregistered"); return false; }
		if (Cap->GetOwner() != Actor) { OutReason = TEXT("pump: capture component no longer owned by the stored capture actor"); return false; }
		if (Cap->GetWorld() != World) { OutReason = TEXT("pump: capture component is in a different world"); return false; }
		if (!IsValid(RT)) { OutReason = TEXT("pump: render target invalid"); return false; }
		if (Cap->TextureTarget != RT) { OutReason = TEXT("pump: capture TextureTarget no longer the stored render target"); return false; }
		if (Cap->bCaptureEveryFrame || Cap->bCaptureOnMovement) { OutReason = TEXT("pump: capture cadence flags were modified"); return false; }
		if (Cap->PrimitiveRenderMode != ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList)
		{ OutReason = TEXT("pump: PrimitiveRenderMode is no longer PRM_UseShowOnlyList"); return false; }
		if (Cap->ShowOnlyComponents.Num() != 1 || Cap->ShowOnlyComponents[0].Get() != Mesh)
		{ OutReason = TEXT("pump: ShowOnlyComponents is not exactly the target skeletal mesh"); return false; }

		return ComputePumpFraming(Mesh, OutCamPos, OutLookDir, OutReason);
	}

	// Combined sampler (Boundary G Phase 1). Host/layer scalars AND the socket world transform/basis
	// are serialized inside ONE finalized-frame callback against ONE GFrameCounter value, so the
	// correlation is STRUCTURAL: there is no post-hoc frame join anywhere in this path. Identity is
	// revalidated to the same standard as transform mode BEFORE anything is read.
	static bool BuildCombinedSample(const TSharedPtr<FCaptureSession>& S, FString& OutSample)
	{
		check(IsInGameThread());
		UWorld* World = S->World.Get();
		APawn* Pawn = S->Pawn.Get();
		USceneComponent* TS = S->TransformSource.Get();
		USceneComponent* Capsule = S->Capsule.Get();
		UAnimInstance* Host = S->Host.Get();
		UAnimInstance* Layer = S->Layer.Get();

		// One shared core-identity gate: world, pawn, mesh, host/layer instances and classes, capsule,
		// and exact weapon/static-mesh identity -- revalidated before EVERY sample.
		FString IdErr;
		if (!ValidateCombinedCoreIdentity(S, IdErr)) { StopSession(S, IdErr); return false; }
		const FName Socket(*S->SocketName);

		// ---- scalars: identical reader/null/error contract to the linked-scalar mode ----
		TArray<FString> ReadErrors;
		bool bErrTruncated = false;
		auto ReadInto = [&ReadErrors, &bErrTruncated](UAnimInstance* Inst, const FString& InstPath, const TArray<FString>& Props) -> FString
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
					if (ReadErrors.Num() < kMaxReadErrorsPerSample)
					{
						ReadErrors.Add(FString::Printf(TEXT("{\"instance\":%s,\"property\":%s,\"error\":%s}"),
							*JStr(InstPath), *JStr(Props[i]), *JStr(Err)));
					}
					else { bErrTruncated = true; }
				}
			}
			return Fields;
		};
		const FString HostFields  = ReadInto(Host, S->HostInstPath, S->HostProps);
		const FString LayerFields = ReadInto(Layer, S->LayerInstPath, S->LayerProps);
		const bool bSampleOk = (ReadErrors.Num() == 0) && !bErrTruncated;
		FString ErrArr;
		for (int32 i = 0; i < ReadErrors.Num(); ++i) { ErrArr += (i ? TEXT(",") : TEXT("")) + ReadErrors[i]; }

		// ---- socket transform + orthonormal basis, raw from Epic APIs (no reconstruction/offsets) ----
		const FTransform SockW = TS->GetSocketTransform(Socket, RTS_World);
		const FVector AxX = SockW.GetUnitAxis(EAxis::X);
		const FVector AxY = SockW.GetUnitAxis(EAxis::Y);
		const FVector AxZ = SockW.GetUnitAxis(EAxis::Z);
		const FTransform SrcW = TS->GetComponentTransform();
		const FTransform ActorW = Pawn->GetActorTransform();
		const FTransform CapsW = Capsule->GetComponentTransform();
		const FRotator BaseAim = Pawn->GetBaseAimRotation();
		const double WorldTime = World->GetTimeSeconds();

		// Values are VALIDATED and never normalized, repaired, wrapped or substituted. Any failure
		// stops the session BEFORE serialization, so NaN/Inf can never reach the JSON.
		if (!FMath::IsFinite(WorldTime)) { StopSession(S, TEXT("non-finite world time")); return false; }
		if (!IsFiniteXform(SockW)) { StopSession(S, TEXT("non-finite socket world transform")); return false; }
		if (!IsFiniteXform(SrcW))  { StopSession(S, TEXT("non-finite transform-source component transform")); return false; }
		if (!IsFiniteXform(ActorW)){ StopSession(S, TEXT("non-finite actor transform")); return false; }
		if (!IsFiniteXform(CapsW)) { StopSession(S, TEXT("non-finite capsule transform")); return false; }
		if (!IsFiniteRot(BaseAim)) { StopSession(S, TEXT("non-finite base aim rotation")); return false; }
		if (!IsFiniteVec(AxX) || !IsFiniteVec(AxY) || !IsFiniteVec(AxZ))
		{ StopSession(S, TEXT("non-finite socket basis vector")); return false; }
		if (FMath::Abs(AxX.Size() - 1.0) > kBasisUnitTolerance
			|| FMath::Abs(AxY.Size() - 1.0) > kBasisUnitTolerance
			|| FMath::Abs(AxZ.Size() - 1.0) > kBasisUnitTolerance)
		{ StopSession(S, TEXT("socket basis axis is not unit length within tolerance")); return false; }
		if (FMath::Abs(FVector::DotProduct(AxX, AxY)) > kBasisOrthoTolerance
			|| FMath::Abs(FVector::DotProduct(AxX, AxZ)) > kBasisOrthoTolerance
			|| FMath::Abs(FVector::DotProduct(AxY, AxZ)) > kBasisOrthoTolerance)
		{ StopSession(S, TEXT("socket basis axes are not mutually orthogonal within tolerance")); return false; }
		if (FVector::DotProduct(FVector::CrossProduct(AxX, AxY), AxZ) <= kBasisHandednessMin)
		{ StopSession(S, TEXT("socket basis handedness is invalid")); return false; }

		// Guaranteed non-empty: identity validation above proves the stored asset is still in use.
		const FString StaticMeshPath = S->StaticMeshPath;
		AController* Ctrl = Pawn->GetController();
		const FString CtrlPath = Ctrl ? Ctrl->GetPathName() : FString();

		OutSample = FString::Printf(
			TEXT("{\"sessionId\":%s,\"mode\":\"combined\",\"frameNumber\":%llu,\"worldTimeSeconds\":%.6f,\"world\":%s,\"owner\":%s,")
			TEXT("\"meshComponent\":%s,\"hostInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,")
			TEXT("\"host\":{%s},\"layer\":{%s},")
			TEXT("\"weaponComponent\":{\"path\":%s,\"class\":%s,\"staticMesh\":%s},")
			TEXT("\"socket\":{\"name\":%s,\"worldLocation\":%s,\"worldRotation\":%s,\"basis\":{\"x\":%s,\"y\":%s,\"z\":%s}},")
			TEXT("\"transformSourceWorldTransform\":%s,\"actorTransform\":%s,\"capsuleTransform\":%s,")
			TEXT("\"baseAimRotation\":%s,\"controller\":%s,\"isLocallyControlled\":%s,\"localRole\":\"%s\",\"remoteRole\":\"%s\",")
			TEXT("\"sampleOk\":%s,\"readErrorsTruncated\":%s,\"readErrors\":[%s]}"),
			*JStr(S->Id), (unsigned long long)GFrameCounter, WorldTime,
			*JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath),
			*JStr(S->HostInstPath), *JStr(S->HostClass), *JStr(S->LayerInstPath), *JStr(S->LayerClass),
			*HostFields, *LayerFields,
			*JStr(S->TransformSourcePath), *JStr(TS->GetClass()->GetPathName()), *JStr(StaticMeshPath),
			*JStr(S->SocketName), *VecJson(SockW.GetLocation()), *RotJson(SockW.Rotator()),
			*VecJson(AxX), *VecJson(AxY), *VecJson(AxZ),
			*XformJson(SrcW), *XformJson(ActorW), *XformJson(CapsW),
			*RotJson(BaseAim), *JStr(CtrlPath),
			Pawn->IsLocallyControlled() ? TEXT("true") : TEXT("false"),
			NetRoleStr(Pawn->GetLocalRole()), NetRoleStr(Pawn->GetRemoteRole()),
			bSampleOk ? TEXT("true") : TEXT("false"), bErrTruncated ? TEXT("true") : TEXT("false"), *ErrArr);
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
		if (S->bCombinedMode)
		{
			// Boundary G Phase 1: scalars + socket evidence in ONE sample; drift stops inside the builder.
			if (!BuildCombinedSample(S, Sample)) { return; }
		}
		else if (S->bTransformMode)
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

		// Combined-mode telemetry is APPENDED ONLY for combined sessions; for linked-scalar and
		// transform sessions this string is empty and the payload is byte-identical to before.
		FString CombinedExtra;
		if (S->bCombinedMode)
		{
			const double Span = (S->PumpRequestCount > 1) ? (S->PumpLastTime - S->PumpFirstTime) : 0.0;
			const double EffHz = (Span > 0.0) ? ((double)(S->PumpRequestCount - 1) / Span) : 0.0;
			CombinedExtra = FString::Printf(
				TEXT(",\"mode\":\"combined\",\"pump\":{\"mode\":%s,\"isolation\":%s,\"requestedHz\":%d,")
				TEXT("\"captureRequestCount\":%lld,\"firstRequestFrame\":%llu,\"lastRequestFrame\":%llu,")
				TEXT("\"firstRequestTime\":%.6f,\"lastRequestTime\":%.6f,\"effectiveRequestHz\":%.6f,")
				TEXT("\"width\":%d,\"height\":%d,\"resultingSampleCount\":%d},")
				TEXT("\"instrumentationQualification\":\"Samples are measurements from a mesh whose bone refresh was ")
				TEXT("induced by rendering through a separate transient SceneCapture. captureRequestCount counts ")
				TEXT("CaptureScene() INVOCATIONS and does not prove completed rendering; the samples produced by ")
				TEXT("OnBoneTransformsFinalized are the only evidence of successful bone refresh. SceneCapture may ")
				TEXT("update the component's recently-rendered state. No visibility, tick, camera, ownership, asset, ")
				TEXT("config or play-setting was mutated.\""),
				*JStr(S->PumpMode), *JStr(S->PumpIsolation), S->PumpHz,
				(long long)S->PumpRequestCount, (unsigned long long)S->PumpFirstFrame, (unsigned long long)S->PumpLastFrame,
				S->PumpFirstTime, S->PumpLastTime, EffHz, S->PumpW, S->PumpH, S->Samples.Num());
		}

		OutValue = FString::Printf(
			TEXT("{\"sessionId\":%s,\"active\":false,\"stopReason\":%s,\"world\":%s,\"owner\":%s,\"meshComponent\":%s,")
			TEXT("\"hostClass\":%s,\"layerClass\":%s,\"sampleCount\":%d,\"maxSamples\":%d,")
			TEXT("\"accumulatedSampleBytes\":%lld,\"limits\":{\"maxSamples\":%d,\"maxTimeoutSeconds\":%.0f,")
			TEXT("\"maxPropertiesPerSide\":%d,\"maxPropertyNameLength\":%d,\"maxSampleBytes\":%lld}%s,\"samples\":[%s]}"),
			*JStr(S->Id), *JStr(S->StopReason), *JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath),
			*JStr(S->HostClass), *JStr(S->LayerClass), S->Samples.Num(), S->MaxSamples,
			(long long)S->AccumBytes, kMaxSamplesLimit, kMaxTimeoutSeconds,
			kMaxPropertiesPerSide, kMaxPropertyNameLen, (long long)kMaxSampleBytes, *CombinedExtra, *SamplesArr);

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
// DrivePIEAimHoldDeferred (A2)
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::DrivePIEAimHoldDeferred(
	const FString& PawnPath, const FString& LookActionProperty, const FString& MoveActionProperty,
	float TargetPitch, float TargetYaw, float ToleranceDegrees, int32 MaxIterations,
	float HoldSeconds, float MoveX, float MoveY, float TimeoutSeconds)
{
	using namespace TacticalRuntimeAnimInspection;

	UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();
	TSharedPtr<FDriveState> D = MakeShared<FDriveState>();
	D->Result = TStrongObjectPtr<UToolCallAsyncResultString>(Result);
	D->bAimHold = true;

	auto Fail = [&Result](const FString& Msg) { Result->SetError(Msg); };

	// ---- scalar / string validation, all BEFORE any resolution or injection ----
	{
		FString Err;
		const bool bMoveRequested = !MoveActionProperty.IsEmpty();
		const FVector2D MoveVec((double)MoveX, (double)MoveY);
		if (PawnPath.IsEmpty() || PawnPath.Len() > kAimMaxPawnPathLen)
			{ Err = FString::Printf(TEXT("PawnPath must be non-empty and <= %d characters."), kAimMaxPawnPathLen); }
		else if (LookActionProperty.IsEmpty() || LookActionProperty.Len() > kAimMaxActionNameLen)
			{ Err = FString::Printf(TEXT("LookActionProperty is required and must be <= %d characters."), kAimMaxActionNameLen); }
		else if (bMoveRequested && MoveActionProperty.Len() > kAimMaxActionNameLen)
			{ Err = FString::Printf(TEXT("MoveActionProperty must be <= %d characters."), kAimMaxActionNameLen); }
		else if (bMoveRequested && MoveActionProperty == LookActionProperty)
			{ Err = TEXT("MoveActionProperty must differ from LookActionProperty."); }
		else if (!FMath::IsFinite(TargetPitch) || FMath::Abs((double)TargetPitch) > kAimMaxAbsPitch)
			{ Err = FString::Printf(TEXT("TargetPitch must be finite and within [-%.0f,%.0f]."), kAimMaxAbsPitch, kAimMaxAbsPitch); }
		else if (!FMath::IsFinite(TargetYaw) || FMath::Abs((double)TargetYaw) > kAimMaxAbsYaw)
			{ Err = FString::Printf(TEXT("TargetYaw must be finite and within [-%.0f,%.0f]."), kAimMaxAbsYaw, kAimMaxAbsYaw); }
		else if (!FMath::IsFinite(ToleranceDegrees) || (double)ToleranceDegrees < kAimMinTolerance || (double)ToleranceDegrees > kAimMaxTolerance)
			{ Err = FString::Printf(TEXT("ToleranceDegrees must be within [%.1f,%.0f]."), kAimMinTolerance, kAimMaxTolerance); }
		else if (MaxIterations < 1 || MaxIterations > kAimMaxIterations)
			{ Err = FString::Printf(TEXT("MaxIterations must be within [1,%d]."), kAimMaxIterations); }
		else if (!FMath::IsFinite(HoldSeconds) || (double)HoldSeconds < kAimMinHoldSeconds || (double)HoldSeconds > kAimMaxHoldSeconds)
			{ Err = FString::Printf(TEXT("HoldSeconds must be within [%.1f,%.0f]."), kAimMinHoldSeconds, kAimMaxHoldSeconds); }
		else if (!FMath::IsFinite(TimeoutSeconds) || (double)TimeoutSeconds <= 0.0 || (double)TimeoutSeconds > kAimMaxTimeoutSeconds)
			{ Err = FString::Printf(TEXT("TimeoutSeconds must be within (0,%.0f]."), kAimMaxTimeoutSeconds); }
		else if ((double)TimeoutSeconds <= (double)HoldSeconds)
			{ Err = TEXT("TimeoutSeconds must be strictly greater than HoldSeconds."); }
		else if (!FMath::IsFinite(MoveX) || !FMath::IsFinite(MoveY)
			|| FMath::Abs((double)MoveX) > 1.0 || FMath::Abs((double)MoveY) > 1.0 || MoveVec.Size() > 1.0 + KINDA_SMALL_NUMBER)
			{ Err = TEXT("MoveX/MoveY must be finite, each within [-1,1], with vector magnitude <= 1."); }
		else if (!bMoveRequested && (MoveX != 0.f || MoveY != 0.f))
			{ Err = TEXT("MoveX and MoveY must both be zero when MoveActionProperty is empty."); }
		else if (bMoveRequested && MoveVec.IsNearlyZero())
			{ Err = TEXT("MoveActionProperty was supplied but the movement vector is zero."); }
		if (!Err.IsEmpty()) { Fail(Err); return Result; }
	}

	// ---- object / subsystem / action resolution ----
	APawn* Pawn = Cast<APawn>(ResolveActor(PawnPath));
	if (!IsValid(Pawn) || Pawn->IsTemplate()) { Fail(FString::Printf(TEXT("Pawn not found or is a CDO/template: %s"), *PawnPath)); return Result; }
	UWorld* World = Pawn->GetWorld();
	if (!IsPIEWorld(World)) { Fail(TEXT("Pawn is not in a PIE world (editor/preview rejected).")); return Result; }
	if (!Pawn->IsLocallyControlled()) { Fail(TEXT("Pawn is not locally controlled; the real input path is unavailable.")); return Result; }

	for (const TSharedPtr<FDriveState>& Existing : GDrives)
	{
		if (Existing.IsValid() && !Existing->bResolved && Existing->Pawn.Get() == Pawn)
			{ Fail(TEXT("A drive sequence is already active on this pawn.")); return Result; }
	}

	APlayerController* PC = Cast<APlayerController>(Pawn->GetController());
	ULocalPlayer* LP = PC ? PC->GetLocalPlayer() : nullptr;
	UEnhancedInputLocalPlayerSubsystem* Sub = LP ? ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LP) : nullptr;
	if (!PC) { Fail(TEXT("Pawn has no APlayerController.")); return Result; }
	if (!LP) { Fail(TEXT("Controller has no ULocalPlayer.")); return Result; }
	if (!Sub) { Fail(TEXT("No EnhancedInput local-player subsystem (real input path unavailable).")); return Result; }

	auto ResolveAction = [Pawn](const FString& PropName) -> UInputAction*
	{
		if (PropName.IsEmpty()) { return nullptr; }
		FObjectProperty* OP = CastField<FObjectProperty>(Pawn->GetClass()->FindPropertyByName(FName(*PropName)));
		if (!OP) { return nullptr; }
		return Cast<UInputAction>(OP->GetObjectPropertyValue_InContainer(Pawn));
	};

	UInputAction* LookAction = ResolveAction(LookActionProperty);
	if (!LookAction) { Fail(FString::Printf(TEXT("Look action property '%s' not found or not a UInputAction."), *LookActionProperty)); return Result; }
	if (LookAction->ValueType != EInputActionValueType::Axis2D)
		{ Fail(FString::Printf(TEXT("Look action '%s' must be Axis2D."), *LookActionProperty)); return Result; }

	const bool bMoveRequested = !MoveActionProperty.IsEmpty();
	UInputAction* MoveAction = bMoveRequested ? ResolveAction(MoveActionProperty) : nullptr;
	if (bMoveRequested && !MoveAction) { Fail(FString::Printf(TEXT("Move action property '%s' not found or not a UInputAction."), *MoveActionProperty)); return Result; }
	if (bMoveRequested && MoveAction->ValueType != EInputActionValueType::Axis2D)
		{ Fail(FString::Printf(TEXT("Move action '%s' must be Axis2D."), *MoveActionProperty)); return Result; }

	// Never stop an injection this tool did not start.
	if (Sub->HasContinuousInputInjectionForAction(LookAction))
		{ Fail(TEXT("A continuous injection is already active for the look action; refusing to interfere.")); return Result; }
	if (MoveAction && Sub->HasContinuousInputInjectionForAction(MoveAction))
		{ Fail(TEXT("A continuous injection is already active for the move action; refusing to interfere.")); return Result; }

	// Reject a session that would share this subsystem AND overlap on either action -- including one
	// still converging before its movement injection starts -- so no session can overwrite or stop
	// another session's injection.
	for (const TSharedPtr<FDriveState>& Existing : GDrives)
	{
		if (!Existing.IsValid() || Existing->bResolved) { continue; }
		if (Existing->Subsystem.Get() != Sub) { continue; }
		// Include the legacy sequence tool's READINESS action too, so A2 can never inject an action
		// already owned by another drive session on this same Enhanced Input subsystem.
		UInputAction* EL = Existing->LookAction.Get();
		UInputAction* EM = Existing->MoveAction.Get();
		UInputAction* ER = Existing->ReadinessAction.Get();
		const bool bOverlap = (EL && (EL == LookAction || EL == MoveAction))
			|| (EM && (EM == LookAction || EM == MoveAction))
			|| (ER && (ER == LookAction || ER == MoveAction));
		if (bOverlap)
			{ Fail(TEXT("Another active drive on this Enhanced Input subsystem already uses one of the requested actions.")); return Result; }
	}

	D->Pawn = Pawn; D->Controller = PC; D->Subsystem = Sub;
	D->AimWorld = World; D->LocalPlayer = LP;
	D->LookActionPath = LookAction->GetPathName();
	D->MoveActionPath = MoveAction ? MoveAction->GetPathName() : FString();
	D->LookAction = LookAction; D->MoveAction = MoveAction;
	D->PawnPath = PawnPath; D->LookActionProperty = LookActionProperty; D->MoveActionProperty = MoveActionProperty;
	D->ControllerPath = PC->GetPathName(); D->LocalPlayerPath = LP->GetPathName(); D->WorldName = World->GetPathName();
	D->TargetPitch = (double)TargetPitch; D->TargetYaw = (double)TargetYaw;
	D->Tolerance = (double)ToleranceDegrees; D->MaxIterations = MaxIterations;
	D->HoldSeconds = (double)HoldSeconds; D->TimeoutSeconds = (double)TimeoutSeconds;
	D->MoveX = MoveX; D->MoveY = MoveY; D->bMoveRequested = bMoveRequested;
	// NOTE ON CONVENTION: the Axis2D COMPONENT mapping (X feeds yaw, Y feeds pitch) is fixed by the
	// project's Look handler, but the DOWNSTREAM RESPONSE SIGN of each path is never assumed -- it is
	// calibrated per session from bounded probes and their observed angular deltas.
	// Reciprocal possession must hold in BOTH directions before anything is captured or injected.
	if (PC->GetPawn() != Pawn) { Fail(TEXT("Controller does not possess the supplied pawn.")); return Result; }

	// One validated read of the runtime feedback, rejected outright if non-finite so NaN/Inf can never
	// reach the error math, the trace, the JSON, or Enhanced Input.
	const FRotator InitialAim = Pawn->GetBaseAimRotation();
	const double InitialSpeed = (double)Pawn->GetVelocity().Size2D();
	if (InitialAim.ContainsNaN() || !FMath::IsFinite(InitialAim.Pitch) || !FMath::IsFinite(InitialAim.Yaw) || !FMath::IsFinite(InitialAim.Roll))
		{ Fail(TEXT("Initial GetBaseAimRotation() is non-finite.")); return Result; }
	if (!FMath::IsFinite(InitialSpeed)) { Fail(TEXT("Initial horizontal speed is non-finite.")); return Result; }

	D->InitialAim = InitialAim;
	D->FinalAim = InitialAim;
	D->SpeedBefore = InitialSpeed;
	D->MaxSpeed = InitialSpeed;
	D->bAimLocallyControlled = Pawn->IsLocallyControlled();
	D->AimLocalRole = NetRoleStr(Pawn->GetLocalRole());
	D->AimRemoteRole = NetRoleStr(Pawn->GetRemoteRole());
	D->T0 = FPlatformTime::Seconds();
	D->Steps.Add(FString::Printf(TEXT("start pitch=%.3f yaw=%.3f target=(%.3f,%.3f) tol=%.3f"),
		D->InitialAim.Pitch, D->InitialAim.Yaw, D->TargetPitch, D->TargetYaw, D->Tolerance));

	// Register the shared lifecycle hooks deterministically: A2 must not depend on another tool
	// having run first to install EndPIE / world-cleanup handling.
	EnsureHooks();

	GDrives.Add(D);
	TWeakPtr<FDriveState> WeakD = D;

	D->TickHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[WeakD](float) -> bool
		{
			check(IsInGameThread());
			TSharedPtr<FDriveState> DS = WeakD.Pin();
			if (!DS.IsValid() || DS->bResolved) { return false; }

			// ---- EXACT identity revalidation, before any feedback read or injection ----
			APawn* P = DS->Pawn.Get();
			UEnhancedInputLocalPlayerSubsystem* SubNow = DS->Subsystem.Get();
			UInputAction* Look = DS->LookAction.Get();
			APlayerController* PCNow = DS->Controller.Get();
			UWorld* WorldNow = DS->AimWorld.Get();
			ULocalPlayer* LPNow = DS->LocalPlayer.Get();

			auto Drift = [&DS](const TCHAR* Why) -> bool
			{
				DS->FailureReason = Why;
				FinalizeDrive(DS, FString::Printf(TEXT("identity drift: %s"), Why));
				return false;
			};

			if (!IsValid(P)) { return Drift(TEXT("pawn invalid")); }
			if (!WorldNow || !IsPIEWorld(WorldNow)) { return Drift(TEXT("original PIE world gone")); }
			if (P->GetWorld() != WorldNow) { return Drift(TEXT("pawn left the original PIE world")); }
			if (!P->IsLocallyControlled()) { return Drift(TEXT("pawn is no longer locally controlled")); }
			if (!PCNow) { return Drift(TEXT("controller invalid")); }
			if (P->GetController() != PCNow) { return Drift(TEXT("pawn controller is not the stored controller")); }
			if (PCNow->GetPawn() != P) { return Drift(TEXT("controller no longer possesses the stored pawn")); }
			if (!LPNow || PCNow->GetLocalPlayer() != LPNow) { return Drift(TEXT("controller local player changed")); }
			if (!SubNow || ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(LPNow) != SubNow)
				{ return Drift(TEXT("enhanced input subsystem changed")); }
			if (!Look) { return Drift(TEXT("look action invalid")); }
			{
				auto ResolveNow = [P](const FString& PropName) -> UInputAction*
				{
					if (PropName.IsEmpty()) { return nullptr; }
					FObjectProperty* OP = CastField<FObjectProperty>(P->GetClass()->FindPropertyByName(FName(*PropName)));
					return OP ? Cast<UInputAction>(OP->GetObjectPropertyValue_InContainer(P)) : nullptr;
				};
				if (ResolveNow(DS->LookActionProperty) != Look) { return Drift(TEXT("look action property no longer resolves to the stored action")); }
				if (DS->bMoveRequested)
				{
					UInputAction* MvNow = DS->MoveAction.Get();
					if (!MvNow || ResolveNow(DS->MoveActionProperty) != MvNow)
						{ return Drift(TEXT("move action property no longer resolves to the stored action")); }
				}
			}

			const double Now = FPlatformTime::Seconds();
			if (Now - DS->T0 >= DS->TimeoutSeconds) { FinalizeDrive(DS, TEXT("timeout")); return false; }

			// 2D speed only: vertical velocity must never be taken as proof of locomotion.
			// Feedback is read ONCE here, after exact identity validation and BEFORE any error math,
			// trace generation, speed accumulation, or injection. Non-finite feedback finalizes
			// immediately without injecting anything.
			const FRotator Aim = P->GetBaseAimRotation();
			const double Speed2D = (double)P->GetVelocity().Size2D();
			if (Aim.ContainsNaN() || !FMath::IsFinite(Aim.Pitch) || !FMath::IsFinite(Aim.Yaw) || !FMath::IsFinite(Aim.Roll))
				{ return Drift(TEXT("GetBaseAimRotation() returned a non-finite rotation")); }
			if (!FMath::IsFinite(Speed2D))
				{ return Drift(TEXT("horizontal speed is non-finite")); }

			// Only now is it safe to record validated evidence.
			DS->MaxSpeed = FMath::Max(DS->MaxSpeed, Speed2D);
			DS->bAimLocallyControlled = P->IsLocallyControlled();
			DS->AimLocalRole = NetRoleStr(P->GetLocalRole());
			DS->AimRemoteRole = NetRoleStr(P->GetRemoteRole());
			DS->FinalAim = Aim;
			const double PitchErr = DS->TargetPitch - Aim.Pitch;
			const double YawErr = FRotator::NormalizeAxis(DS->TargetYaw - Aim.Yaw);
			const bool bWithin = FMath::Abs(PitchErr) <= DS->Tolerance && FMath::Abs(YawErr) <= DS->Tolerance;

			// One bounded, clamped Axis2D correction. The Axis2D COMPONENTS are fixed by the project's
			// Look handler (component X feeds the yaw path, component Y feeds the pitch path), but the
			// DOWNSTREAM RESPONSE SIGN of each path is not assumed: it is the empirically calibrated
			// YawResponseSign / PitchResponseSign measured for this session via bounded probes.
			auto Correct = [&](const TCHAR* Phase) -> bool
			{
				if (DS->Iterations >= DS->MaxIterations) { return false; }

				// Each component is computed INDEPENDENTLY. An axis already within tolerance receives
				// EXACTLY zero, so a skipped axis can never be nudged by the other axis's correction.
				const bool bYawOut = FMath::Abs(YawErr) > DS->Tolerance;
				const bool bPitchOut = FMath::Abs(PitchErr) > DS->Tolerance;

				// Defense in depth: a nonzero correction requires an OBSERVED response sign for that axis.
				// Calibration should already guarantee this; if it somehow does not, fail explicitly rather
				// than drive the axis with the placeholder sign.
				if ((bYawOut && !DS->bYawResponseObserved) || (bPitchOut && !DS->bPitchResponseObserved))
				{
					DS->FailureReason = TEXT("correction attempted on an out-of-tolerance axis with no observed response sign");
					FinalizeDrive(DS, TEXT("response calibration failed"));
					return false;   // FinalizeDrive is idempotent, so the caller's own finalize is a no-op
				}

				const double CX = bYawOut ? FMath::Clamp(YawErr * DS->YawResponseSign, -1.0, 1.0) : 0.0;
				const double CY = bPitchOut ? FMath::Clamp(PitchErr * DS->PitchResponseSign, -1.0, 1.0) : 0.0;
				if (CX == 0.0 && CY == 0.0) { return true; }   // nothing out of tolerance: inject nothing
				SubNow->InjectInputForAction(Look, FInputActionValue(FVector2D(CX, CY)), TArray<UInputModifier*>(), TArray<UInputTrigger*>());
				++DS->Iterations;
				if (DS->Steps.Num() < kAimMaxTraceEntries)
				{
					DS->Steps.Add(FString::Printf(TEXT("%s i=%d pitchErr=%.3f yawErr=%.3f inject=(%.3f,%.3f)"),
						Phase, DS->Iterations, PitchErr, YawErr, CX, CY));
				}
				else { DS->bTraceTruncated = true; }
				return true;
			};

			// ---- ONE calibration step; reachable from BOTH the converge and hold phases ----
			// Returns: 0 = keep ticking (work done this tick), 1 = calibration complete, -1 = finalized/failed.
			auto CalibrateStep = [&]() -> int32
			{
				const bool bYawAxis = (DS->CalAxis == 0);
				int32& Attempts = bYawAxis ? DS->YawProbeAttempts : DS->PitchProbeAttempts;
				double& ProbeIn = bYawAxis ? DS->YawProbeInput : DS->PitchProbeInput;
				double& ProbeDelta = bYawAxis ? DS->YawProbeDelta : DS->PitchProbeDelta;
				double& Sign = bYawAxis ? DS->YawResponseSign : DS->PitchResponseSign;
				bool& AxisDone = bYawAxis ? DS->bYawCalDone : DS->bPitchCalDone;
				bool& Observed = bYawAxis ? DS->bYawResponseObserved : DS->bPitchResponseObserved;
				const TCHAR* AxisName = bYawAxis ? TEXT("yaw") : TEXT("pitch");

				// A pending probe is ALWAYS measured before anything else, even if the probe itself moved
				// the aim into tolerance -- its evidence must never be skipped.
				if (DS->bAwaitingProbe)
				{
					const double Delta = bYawAxis
						? FRotator::NormalizeAxis(Aim.Yaw - DS->ProbeBaseYaw)
						: (Aim.Pitch - DS->ProbeBasePitch);
					if (FMath::IsFinite(Delta) && FMath::Abs(Delta) >= kAimMinMeasurableResponseDeg)
					{
						ProbeDelta = Delta;
						Sign = FMath::Sign(Delta) * FMath::Sign(ProbeIn);
						Observed = true;
						AxisDone = true;
						DS->bAwaitingProbe = false;
						if (DS->Steps.Num() < kAimMaxTraceEntries)
						{
							DS->Steps.Add(FString::Printf(TEXT("calibrate %s: probeIn=%.3f delta=%.4f sign=%+.0f attempts=%d"),
								AxisName, ProbeIn, Delta, Sign, Attempts));
						}
						else { DS->bTraceTruncated = true; }
					}
					else if (Attempts < kAimMaxProbeAttempts)
					{
						// No material response (e.g. axis pinned at a clamp): one bounded opposite probe.
						DS->bAwaitingProbe = false;
						if (DS->Steps.Num() < kAimMaxTraceEntries)
							{ DS->Steps.Add(FString::Printf(TEXT("calibrate %s: no response (delta=%.4f); retrying opposite"), AxisName, Delta)); }
						else { DS->bTraceTruncated = true; }
					}
					else
					{
						DS->FailureReason = FString::Printf(TEXT("%s axis produced no measurable response (>= %.3f deg) in either direction"), AxisName, kAimMinMeasurableResponseDeg);
						FinalizeDrive(DS, TEXT("response calibration failed"));
						return -1;
					}
				}

				if (!AxisDone && !DS->bAwaitingProbe)
				{
					if (Attempts >= kAimMaxProbeAttempts)
					{
						DS->FailureReason = FString::Printf(TEXT("%s axis exhausted %d calibration probe attempts"), AxisName, kAimMaxProbeAttempts);
						FinalizeDrive(DS, TEXT("response calibration failed"));
						return -1;
					}
					if (DS->Iterations >= DS->MaxIterations)
					{
						DS->FailureReason = TEXT("max corrective iterations reached during response calibration");
						FinalizeDrive(DS, TEXT("response calibration failed"));
						return -1;
					}
					// Axes are probed SEPARATELY; direction flips on the second attempt for a clamped axis.
					const double Dir = (Attempts == 0) ? 1.0 : -1.0;
					ProbeIn = Dir * kAimProbeMagnitude;
					DS->ProbeBaseYaw = Aim.Yaw;
					DS->ProbeBasePitch = Aim.Pitch;
					const FVector2D ProbeVec = bYawAxis ? FVector2D(ProbeIn, 0.0) : FVector2D(0.0, ProbeIn);
					SubNow->InjectInputForAction(Look, FInputActionValue(ProbeVec), TArray<UInputModifier*>(), TArray<UInputTrigger*>());
					++Attempts;
					++DS->Iterations;   // probes count against the MaxIterations ceiling
					DS->bAwaitingProbe = true;
					if (DS->Steps.Num() < kAimMaxTraceEntries)
						{ DS->Steps.Add(FString::Printf(TEXT("probe %s attempt=%d input=%.3f"), AxisName, Attempts, ProbeIn)); }
					else { DS->bTraceTruncated = true; }
					return 0;
				}

				// Move to the next unfinished axis, else calibration is complete.
				if (!DS->bYawCalDone) { DS->CalAxis = 0; return 0; }
				if (!DS->bPitchCalDone) { DS->CalAxis = 1; return 0; }

				DS->bCalibrated = true;
				if (DS->Steps.Num() < kAimMaxTraceEntries)
				{
					DS->Steps.Add(FString::Printf(TEXT("calibrated: yaw sign=%+.0f observed=%s | pitch sign=%+.0f observed=%s"),
						DS->YawResponseSign, DS->bYawResponseObserved ? TEXT("true") : TEXT("false"),
						DS->PitchResponseSign, DS->bPitchResponseObserved ? TEXT("true") : TEXT("false")));
				}
				else { DS->bTraceTruncated = true; }
				return 1;
			};

			// Calibration requirements are initialised BEFORE any convergence test, so a probe can never
			// be bypassed by the aim happening to land inside tolerance.
			if (!DS->bCalibInitialized)
			{
				DS->bYawCalRequired = FMath::Abs(YawErr) > DS->Tolerance;
				DS->bPitchCalRequired = FMath::Abs(PitchErr) > DS->Tolerance;
				if (!DS->bYawCalRequired) { DS->bYawCalDone = true; }     // skipped: responseObserved stays false
				if (!DS->bPitchCalRequired) { DS->bPitchCalDone = true; }
				DS->CalAxis = DS->bYawCalDone ? 1 : 0;
				DS->bCalibInitialized = true;
				if (!DS->bYawCalRequired && !DS->bPitchCalRequired)
				{
					DS->bCalibrated = true;   // both axes explicitly skipped / not required
					if (DS->Steps.Num() < kAimMaxTraceEntries)
						{ DS->Steps.Add(TEXT("calibration skipped: both axes already within tolerance (no sign observed)")); }
					else { DS->bTraceTruncated = true; }
				}
			}

			if (!DS->bConverged)
			{
				if (!DS->bCalibrated)
				{
					const int32 CalRes = CalibrateStep();
					if (CalRes < 0) { return false; }
					return true;   // never declare convergence on a calibration tick
				}

				// Defense in depth: convergence requires a fully resolved calibration phase.
				const bool bCalReady = DS->bCalibInitialized && !DS->bAwaitingProbe
					&& DS->bYawCalDone && DS->bPitchCalDone
					&& (!DS->bYawCalRequired || DS->bYawResponseObserved)
					&& (!DS->bPitchCalRequired || DS->bPitchResponseObserved);

				if (bWithin && bCalReady)
				{
					DS->bConverged = true;
					DS->ConvergedAt = Now - DS->T0;
					DS->AchievedAim = Aim;
					DS->HoldStartAt = Now;
					if (DS->bMoveRequested)
					{
						if (UInputAction* Mv = DS->MoveAction.Get())
						{
							SubNow->StartContinuousInputInjectionForAction(Mv, FInputActionValue(FVector2D((double)DS->MoveX, (double)DS->MoveY)), TArray<UInputModifier*>(), TArray<UInputTrigger*>());
							DS->bMoveInjecting = true;
							DS->bMoveInjectionStarted = true;
						}
						else { FinalizeDrive(DS, TEXT("move action became invalid before the hold phase")); return false; }
					}
					if (DS->Steps.Num() < kAimMaxTraceEntries)
						{ DS->Steps.Add(FString::Printf(TEXT("converged at %.3fs after %d iterations; hold begins"), DS->ConvergedAt, DS->Iterations)); }
					return true;
				}

				if (!Correct(TEXT("converge"))) { FinalizeDrive(DS, TEXT("max corrective iterations reached before convergence")); return false; }
				return true;
			}

			// ---- hold phase: keep measuring; re-correct whenever either error leaves tolerance ----
			DS->MaxPitchErrHold = FMath::Max(DS->MaxPitchErrHold, FMath::Abs(PitchErr));
			DS->MaxYawErrHold = FMath::Max(DS->MaxYawErrHold, FMath::Abs(YawErr));
			if (!bWithin)
			{
				// An axis skipped at start has only a PLACEHOLDER sign. If it now needs correcting, it is
				// calibrated on demand first -- a correction is never applied with an unobserved sign.
				const bool bYawNeeds = FMath::Abs(YawErr) > DS->Tolerance;
				const bool bPitchNeeds = FMath::Abs(PitchErr) > DS->Tolerance;
				if ((bYawNeeds && !DS->bYawResponseObserved) || (bPitchNeeds && !DS->bPitchResponseObserved))
				{
					if (bYawNeeds && !DS->bYawResponseObserved) { DS->bYawCalRequired = true; DS->bYawCalDone = false; DS->CalAxis = 0; }
					else { DS->bPitchCalRequired = true; DS->bPitchCalDone = false; DS->CalAxis = 1; }
					DS->bCalibrated = false;
				}
				if (!DS->bCalibrated)
				{
					const int32 CalRes = CalibrateStep();
					if (CalRes < 0) { return false; }
					return true;   // calibrate before correcting this axis
				}
				if (!Correct(TEXT("hold"))) { FinalizeDrive(DS, TEXT("max corrective iterations reached during hold")); return false; }
				// Hold completion is NEVER evaluated on a tick that injected a correction: wait for the
				// next exact-identity-valid, finite-feedback tick so the corrected response is observed.
				// The requested hold is therefore a MINIMUM; a late correction can push holdActualSeconds
				// past it until the response settles or a timeout / iteration bound fails the call.
				return true;
			}
			if ((Now - DS->HoldStartAt) >= DS->HoldSeconds)
			{
				DS->HoldEndAt = Now;
				// No second aim read here: DS->FinalAim already holds this tick's single
				// finite-checked, identity-validated Aim value. Stop movement, then finalize.
				StopDriveInjection(DS);
				FinalizeDrive(DS, TEXT("completed"));
				return false;
			}
			return true;
		}), 0.0f);

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
// StartCombinedAnimSocketCaptureDeferred (Boundary G Phase 1)
// =============================================================================
UToolCallAsyncResultString* UTacticalRuntimeAnimInspectionToolset::StartCombinedAnimSocketCaptureDeferred(
	const FString& PawnPath, const FString& MeshComponentPath, const FString& TransformSourcePath, const FString& SocketName,
	const FString& HostClassPath, const TArray<FString>& HostProperties, const FString& LayerClassPath, const TArray<FString>& LayerProperties,
	int32 MaxSamples, float TimeoutSeconds, const FString& RenderPumpMode, int32 RenderPumpHz, int32 RenderPumpWidth, int32 RenderPumpHeight)
{
	return RunDeferredString([=](FString& OutValue, FString& OutError) -> bool
	{
		check(IsInGameThread());
		EnsureHooks();

		// ---- 1. scalar / string / numeric validation: NOTHING is allocated before this passes ----
		if (MaxSamples < 1 || MaxSamples > kMaxSamplesLimit) { OutError = FString::Printf(TEXT("MaxSamples must be in [1,%d]."), kMaxSamplesLimit); return false; }
		if (!FMath::IsFinite((double)TimeoutSeconds) || TimeoutSeconds <= 0.f || (double)TimeoutSeconds > kMaxTimeoutSeconds)
		{ OutError = FString::Printf(TEXT("TimeoutSeconds must be finite and in (0,%.0f]."), kMaxTimeoutSeconds); return false; }
		if (SocketName.IsEmpty()) { OutError = TEXT("SocketName must be explicit (non-empty)."); return false; }
		if (SocketName.Len() > kMaxPropertyNameLen) { OutError = FString::Printf(TEXT("SocketName exceeds %d characters."), kMaxPropertyNameLen); return false; }

		if (!ValidatePropertyList(HostProperties, TEXT("HostProperties"), OutError)) { return false; }
		if (!ValidatePropertyList(LayerProperties, TEXT("LayerProperties"), OutError)) { return false; }

		// Object-path bounds enforced BEFORE StaticFindObject/class resolution and before allocation.
		auto CheckPath = [](const FString& P, const TCHAR* Which, FString& Err) -> bool
		{
			if (P.IsEmpty()) { Err = FString::Printf(TEXT("%s must be non-empty."), Which); return false; }
			if (P.Len() > kMaxObjectPathLen) { Err = FString::Printf(TEXT("%s is %d characters; the maximum is %d."), Which, P.Len(), kMaxObjectPathLen); return false; }
			return true;
		};
		if (!CheckPath(PawnPath, TEXT("PawnPath"), OutError)) { return false; }
		if (!CheckPath(MeshComponentPath, TEXT("MeshComponentPath"), OutError)) { return false; }
		if (!CheckPath(TransformSourcePath, TEXT("TransformSourcePath"), OutError)) { return false; }
		if (!CheckPath(HostClassPath, TEXT("HostClassPath"), OutError)) { return false; }
		if (!CheckPath(LayerClassPath, TEXT("LayerClassPath"), OutError)) { return false; }

		const bool bPumpNone = RenderPumpMode.Equals(TEXT("none"), ESearchCase::IgnoreCase);
		const bool bPumpShowOnly = RenderPumpMode.Equals(TEXT("showOnly"), ESearchCase::IgnoreCase);
		if (!bPumpNone && !bPumpShowOnly) { OutError = TEXT("RenderPumpMode must be exactly \"none\" or \"showOnly\"."); return false; }
		int32 PumpW = (RenderPumpWidth  == 0) ? kDefaultPumpDim : RenderPumpWidth;
		int32 PumpH = (RenderPumpHeight == 0) ? kDefaultPumpDim : RenderPumpHeight;
		if (bPumpShowOnly)
		{
			if (RenderPumpHz < kMinPumpHz || RenderPumpHz > kMaxPumpHz) { OutError = FString::Printf(TEXT("RenderPumpHz must be in [%d,%d]."), kMinPumpHz, kMaxPumpHz); return false; }
			if (PumpW < kMinPumpDim || PumpW > kMaxPumpDim || PumpH < kMinPumpDim || PumpH > kMaxPumpDim)
			{ OutError = FString::Printf(TEXT("Render pump dimensions must be in [%d,%d] per axis."), kMinPumpDim, kMaxPumpDim); return false; }
		}

		// ---- 2. identity resolution/validation ----
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
		// This tool collects weapon/static-mesh evidence, so the transform source MUST be a live,
		// registered UStaticMeshComponent owned by the exact pawn, carrying a valid UStaticMesh.
		UStaticMeshComponent* WeaponComp = Cast<UStaticMeshComponent>(TS);
		if (!WeaponComp) { OutError = FString::Printf(TEXT("Transform-source component is %s; a UStaticMeshComponent is required."), *TS->GetClass()->GetPathName()); return false; }
		UStaticMesh* ExpectedSM = WeaponComp->GetStaticMesh();
		if (!IsValid(ExpectedSM)) { OutError = TEXT("Transform-source static-mesh component has no valid UStaticMesh asset."); return false; }
		if (!TS->DoesSocketExist(FName(*SocketName))) { OutError = FString::Printf(TEXT("Explicit socket '%s' does not exist on the transform-source component."), *SocketName); return false; }

		USceneComponent* Capsule = nullptr;
		if (ACharacter* Char = Cast<ACharacter>(Pawn)) { Capsule = Char->GetCapsuleComponent(); }
		if (!Capsule) { Capsule = Pawn->GetRootComponent(); }
		if (!IsValid(Capsule) || Capsule->IsTemplate() || !Capsule->IsRegistered() || !IsPIEWorld(Capsule->GetWorld())
			|| Capsule->GetOwner() != Pawn || Capsule->GetWorld() != World)
		{ OutError = TEXT("Capsule/root component missing or failed live/registered/ownership/world validation."); return false; }

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

		// ---- 3. global pumped-session bound, rejected BEFORE any render resource is allocated ----
		if (bPumpShowOnly && GPumpActive)
		{ OutError = TEXT("A render-pumped capture session is already active; at most one is permitted globally."); return false; }

		// ---- 4. session object (not yet registered / not yet in GSessions) ----
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
		S->HostProps = HostProperties;
		S->LayerProps = LayerProperties;
		S->MaxSamples = MaxSamples; S->Timeout = (double)TimeoutSeconds;
		S->StartTime = FPlatformTime::Seconds();
		S->bCombinedMode = true;
		S->Pawn = Pawn;
		S->TransformSource = TS;
		S->TransformSourcePath = TS->GetPathName();
		S->WeaponComp = WeaponComp;
		S->WeaponCompPath = WeaponComp->GetPathName();
		S->ExpectedStaticMesh = ExpectedSM;
		S->StaticMeshPath = ExpectedSM->GetPathName();
		S->SocketName = SocketName;
		S->Capsule = Capsule;
		S->CapsulePath = Capsule->GetPathName();
		S->PumpMode = bPumpShowOnly ? TEXT("showOnly") : TEXT("none");
		S->PumpIsolation = bPumpShowOnly ? TEXT("UseShowOnlyList+ShowOnlyComponents{targetSkeletalMesh}") : TEXT("none");
		S->PumpHz = bPumpShowOnly ? RenderPumpHz : 0;
		S->PumpW = bPumpShowOnly ? PumpW : 0;
		S->PumpH = bPumpShowOnly ? PumpH : 0;

		// ---- 5. render-liveness pump. Observes only; on ANY failure everything is rolled back. ----
		if (bPumpShowOnly)
		{
			GPumpActive = true; S->bPumpOwned = true;   // claimed here so every rollback path releases it

			FVector CamPos = FVector::ZeroVector, LookDir = FVector::ZeroVector;
			FString FrameErr;
			if (!ComputePumpFraming(Mesh, CamPos, LookDir, FrameErr))
			{ DestroyPumpTransients(S); OutError = FString::Printf(TEXT("Render pump cannot be created: %s."), *FrameErr); return false; }

			FActorSpawnParameters SpawnParams;
			SpawnParams.ObjectFlags |= RF_Transient;
			SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

			AActor* Actor = World->SpawnActor<AActor>(AActor::StaticClass(), FTransform(CamPos), SpawnParams);
			if (!Actor) { DestroyPumpTransients(S); OutError = TEXT("Failed to spawn transient render-pump actor."); return false; }
			S->PumpActor = TStrongObjectPtr<AActor>(Actor);

			USceneCaptureComponent2D* Cap = NewObject<USceneCaptureComponent2D>(Actor, NAME_None, RF_Transient);
			if (!Cap) { DestroyPumpTransients(S); OutError = TEXT("Failed to create transient render-pump capture component."); return false; }
			Actor->SetRootComponent(Cap);
			Cap->RegisterComponent();
			S->PumpCapture = TStrongObjectPtr<USceneCaptureComponent2D>(Cap);

			UTextureRenderTarget2D* RT = NewObject<UTextureRenderTarget2D>(Actor, NAME_None, RF_Transient);
			if (!RT) { DestroyPumpTransients(S); OutError = TEXT("Failed to create transient render-pump render target."); return false; }
			RT->RenderTargetFormat = RTF_RGBA8;
			RT->ClearColor = FLinearColor::Black;
			RT->bAutoGenerateMips = false;
			RT->InitCustomFormat(PumpW, PumpH, PF_B8G8R8A8, /*bForceLinearGamma=*/false);
			RT->UpdateResourceImmediate(true);
			S->PumpRT = TStrongObjectPtr<UTextureRenderTarget2D>(RT);

			Cap->TextureTarget = RT;
			Cap->CaptureSource = SCS_FinalColorLDR;
			Cap->bCaptureEveryFrame = false;
			Cap->bCaptureOnMovement = false;
			Cap->bAlwaysPersistRenderingState = true;
			Cap->FOVAngle = 90.f;
			// Exact-component isolation ONLY. Never silently broadened to ShowOnlyActors/full scene.
			Cap->PrimitiveRenderMode = ESceneCapturePrimitiveRenderMode::PRM_UseShowOnlyList;
			Cap->ShowOnlyComponent(Mesh);
			Cap->SetWorldLocationAndRotation(CamPos, LookDir.Rotation());
		}

		// ---- 6. registration: after this point StopSession owns every teardown path ----
		TWeakPtr<FCaptureSession> WeakS = S;
		S->bActive = true;
		S->FinalizeHandle = Mesh->RegisterOnBoneTransformsFinalizedDelegate(
			FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateLambda([WeakS]() { OnBoneTransformsFinalized(WeakS); }));

		S->LifecycleHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[WeakS](float) -> bool
			{
				TSharedPtr<FCaptureSession> Sp = WeakS.Pin();
				if (!Sp.IsValid() || !Sp->bActive) { return false; }
				// Same shared core-identity contract as the sampler and the pump, for BOTH pump modes.
				FString IdErr;
				if (!ValidateCombinedCoreIdentity(Sp, IdErr)) { StopSession(Sp, IdErr); return false; }
				if ((FPlatformTime::Seconds() - Sp->StartTime) >= Sp->Timeout)
				{ StopSession(Sp, TEXT("timeout")); return false; }
				return true;
			}), kLifecycleTickInterval);

		if (bPumpShowOnly)
		{
			S->PumpHandle = FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
				[WeakS](float) -> bool
				{
					TSharedPtr<FCaptureSession> Sp = WeakS.Pin();
					if (!Sp.IsValid() || !Sp->bActive) { return false; }
					// Complete rig + identity + framing revalidation before EVERY request. A failure
					// STOPS the session with a specific structured reason -- never skipped silently
					// until timeout, and CaptureScene is never called with invalid framing.
					FVector CamPos = FVector::ZeroVector, LookDir = FVector::ZeroVector;
					FString PumpErr;
					if (!ValidatePumpRig(Sp, CamPos, LookDir, PumpErr))
					{ StopSession(Sp, PumpErr); return false; }

					USceneCaptureComponent2D* Cap = Sp->PumpCapture.Get();
					Cap->SetWorldLocationAndRotation(CamPos, LookDir.Rotation());
					Cap->CaptureScene();

					const double Now = FPlatformTime::Seconds();
					if (Sp->PumpRequestCount == 0) { Sp->PumpFirstFrame = (uint64)GFrameCounter; Sp->PumpFirstTime = Now; }
					Sp->PumpLastFrame = (uint64)GFrameCounter; Sp->PumpLastTime = Now;
					++Sp->PumpRequestCount;
					return true;
				}), 1.0f / (float)RenderPumpHz);
		}

		GSessions.Add(S->Id, S);

		OutValue = FString::Printf(
			TEXT("{\"sessionId\":%s,\"mode\":\"combined\",\"world\":%s,\"owner\":%s,\"meshComponent\":%s,\"transformSource\":%s,\"staticMesh\":%s,\"socket\":%s,")
			TEXT("\"hostAnimInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,\"capsuleComponent\":%s,")
			TEXT("\"hostProperties\":%d,\"layerProperties\":%d,\"maxSamples\":%d,\"timeoutSeconds\":%.3f,")
			TEXT("\"pump\":{\"mode\":%s,\"isolation\":%s,\"requestedHz\":%d,\"width\":%d,\"height\":%d},")
			TEXT("\"limits\":{\"maxSamples\":%d,\"maxTimeoutSeconds\":%.0f,\"maxPropertiesPerSide\":%d,\"maxPropertyNameLength\":%d,")
			TEXT("\"maxSampleBytes\":%lld,\"maxObjectPathLength\":%d,\"pumpHz\":[%d,%d],\"pumpDim\":[%d,%d],")
			TEXT("\"basisUnitTolerance\":%.6f,\"basisOrthoTolerance\":%.6f,\"basisHandednessMinimum\":%.6f,")
			TEXT("\"maxConcurrentPumpedSessions\":1}}"),
			*JStr(S->Id), *JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath), *JStr(S->TransformSourcePath), *JStr(S->StaticMeshPath), *JStr(S->SocketName),
			*JStr(S->HostInstPath), *JStr(S->HostClass), *JStr(S->LayerInstPath), *JStr(S->LayerClass), *JStr(S->CapsulePath),
			HostProperties.Num(), LayerProperties.Num(), MaxSamples, TimeoutSeconds,
			*JStr(S->PumpMode), *JStr(S->PumpIsolation), S->PumpHz, S->PumpW, S->PumpH,
			kMaxSamplesLimit, kMaxTimeoutSeconds, kMaxPropertiesPerSide, kMaxPropertyNameLen, (long long)kMaxSampleBytes,
			kMaxObjectPathLen, kMinPumpHz, kMaxPumpHz, kMinPumpDim, kMaxPumpDim,
			kBasisUnitTolerance, kBasisOrthoTolerance, kBasisHandednessMin);
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
