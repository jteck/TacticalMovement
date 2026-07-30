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
#include "Animation/AnimInstance.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/Actor.h"
#include "GameFramework/PlayerController.h"

#include "EnhancedInputSubsystems.h"
#include "EnhancedInputSubsystemInterface.h"
#include "InputAction.h"
#include "InputActionValue.h"

#include "ToolsetRegistry/ToolCallAsyncResultString.h"

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

	static TMap<FString, TSharedPtr<FCaptureSession>> GSessions;
	static TArray<TSharedPtr<FDriveState>> GDrives;
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

	static void StopAll(const FString& Reason)
	{
		for (auto& Pair : GSessions) { StopSession(Pair.Value, Reason); }
		// Copy because FinalizeDrive mutates GDrives.
		TArray<TSharedPtr<FDriveState>> DrivesCopy = GDrives;
		for (const TSharedPtr<FDriveState>& D : DrivesCopy) { FinalizeDrive(D, Reason); }
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
	}

	static void EnsureHooks()
	{
		if (GHooksRegistered) { return; }
		GHooksRegistered = true;
		GEndPIEHandle = FEditorDelegates::EndPIE.AddStatic(&OnEndPIE);
		GWorldCleanupHandle = FWorldDelegates::OnWorldCleanup.AddStatic(&OnWorldCleanup);
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

		const FString Sample = FString::Printf(
			TEXT("{\"sessionId\":%s,\"frameNumber\":%llu,\"worldTimeSeconds\":%.6f,\"world\":%s,\"owner\":%s,\"meshComponent\":%s,")
			TEXT("\"hostInstance\":%s,\"hostClass\":%s,\"layerInstance\":%s,\"layerClass\":%s,")
			TEXT("\"sampleOk\":%s,\"host\":{%s},\"layer\":{%s},\"readErrors\":[%s]}"),
			*JStr(S->Id), (unsigned long long)GFrameCounter, World->GetTimeSeconds(),
			*JStr(S->WorldName), *JStr(S->OwnerPath), *JStr(S->MeshPath),
			*JStr(HostPath), *JStr(S->HostClass), *JStr(LayerPath), *JStr(S->LayerClass),
			bSampleOk ? TEXT("true") : TEXT("false"), *HostFields, *LayerFields, *ErrArr);

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
// ShutdownAllSessions
// =============================================================================
void UTacticalRuntimeAnimInspectionToolset::ShutdownAllSessions()
{
	StopAll(TEXT("module shutdown"));
	GSessions.Reset();
	if (GHooksRegistered)
	{
		FEditorDelegates::EndPIE.Remove(GEndPIEHandle);
		FWorldDelegates::OnWorldCleanup.Remove(GWorldCleanupHandle);
		GHooksRegistered = false;
	}
}
