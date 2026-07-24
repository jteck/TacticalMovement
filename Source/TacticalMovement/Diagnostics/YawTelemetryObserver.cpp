// Development-only strafe-fix acceptance observer. See header for scope.

#include "Diagnostics/YawTelemetryObserver.h"

#include "TacticalMovementCharacter.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimClassInterface.h"
#include "Animation/AnimationAsset.h"
#include "Animation/BlendSpace.h"
#include "Animation/MirrorDataTable.h"
#include "Animation/Skeleton.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "EngineUtils.h"
#include "UObject/UnrealType.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "Misc/DateTime.h"
#include "Misc/FileHelper.h"
#include "HAL/PlatformProcess.h"
#include "HAL/PlatformTime.h"

#include <limits>

namespace
{
	const TCHAR* NetModeStr(ENetMode M) { switch (M) { case NM_Standalone: return TEXT("Standalone"); case NM_DedicatedServer: return TEXT("DedicatedServer"); case NM_ListenServer: return TEXT("ListenServer"); case NM_Client: return TEXT("Client"); default: return TEXT("Unknown"); } }
	const TCHAR* RoleStr(ENetRole R) { switch (R) { case ROLE_None: return TEXT("None"); case ROLE_SimulatedProxy: return TEXT("SimulatedProxy"); case ROLE_AutonomousProxy: return TEXT("AutonomousProxy"); case ROLE_Authority: return TEXT("Authority"); default: return TEXT("Unknown"); } }
	void AppendVec(FString& R, const FVector& V) { R += FString::Printf(TEXT(",%.6f,%.6f,%.6f"), V.X, V.Y, V.Z); }

	// Reflection-only: return the UBlendSpace held by the running BlendSpacePlayer node's
	// BlendSpace property (nodes live as struct properties on the generated anim class,
	// including those inside state-machine states). Avoids an AnimGraphRuntime dependency.
	UBlendSpace* FindRuntimeBlendSpace(UAnimInstance* AI)
	{
		if (!AI) return nullptr;
		IAnimClassInterface* ACI = IAnimClassInterface::GetFromClass(AI->GetClass());
		if (!ACI) return nullptr;
		for (const FStructProperty* Prop : ACI->GetAnimNodeProperties())
		{
			if (!Prop || !Prop->Struct) continue;
			if (!Prop->Struct->GetName().Contains(TEXT("BlendSpacePlayer"))) continue;
			const void* NodePtr = Prop->ContainerPtrToValuePtr<void>(AI);
			if (const FObjectProperty* BSP = CastField<FObjectProperty>(Prop->Struct->FindPropertyByName(TEXT("BlendSpace"))))
				return Cast<UBlendSpace>(BSP->GetObjectPropertyValue_InContainer(NodePtr));
		}
		return nullptr;
	}
}

bool UYawTelemetryObserver::ShouldCreateSubsystem(UObject* Outer) const
{
	if (!FParse::Param(FCommandLine::Get(), TEXT("YawTelemetry"))) return false;
	if (const UWorld* W = Cast<UWorld>(Outer)) return W->IsGameWorld();
	return false;
}

float UYawTelemetryObserver::SignedHorizYaw(const FVector& Ref, const FVector& V)
{
	FVector a(Ref.X, Ref.Y, 0.0), b(V.X, V.Y, 0.0);
	a = a.GetSafeNormal(); b = b.GetSafeNormal();
	if (a.IsNearlyZero() || b.IsNearlyZero()) return 0.f;
	return FMath::RadiansToDegrees(FMath::Atan2(a.X * b.Y - a.Y * b.X, FVector::DotProduct(a, b)));
}

float UYawTelemetryObserver::TwistZDeg(const FQuat& Q)
{
	double z = Q.Z, w = Q.W;
	if (w < 0) { z = -z; w = -w; }
	return FMath::RadiansToDegrees(2.0 * FMath::Atan2(z, w));
}

void UYawTelemetryObserver::OnWorldBeginPlay(UWorld& InWorld)
{
	Super::OnWorldBeginPlay(InWorld);
	bActive = FParse::Param(FCommandLine::Get(), TEXT("YawTelemetry")) && InWorld.IsGameWorld();
	if (!bActive) return;
	if (!FParse::Value(FCommandLine::Get(), TEXT("YawTelemetryTag="), ProcessTag) || ProcessTag.IsEmpty())
		ProcessTag = NetModeStr(InWorld.GetNetMode());
	const FString FileName = FString::Printf(TEXT("strafefix_%s_%s_%s_%u.csv"), *ProcessTag, NetModeStr(InWorld.GetNetMode()),
		*FDateTime::UtcNow().ToString(TEXT("%Y%m%d_%H%M%S")), FPlatformProcess::GetCurrentProcessId());
	OutputPath = FPaths::ProjectSavedDir() / TEXT("YawTelemetry") / FileName;
	StartTimeSeconds = FPlatformTime::Seconds();

	// Dev-only runtime AnimClass override — completely inert unless -MirrorFwdLeftTest is present.
	bMirrorOverride = FParse::Param(FCommandLine::Get(), TEXT("MirrorFwdLeftTest"));
	if (bMirrorOverride)
	{
		MirrorAnimClass = LoadClass<UAnimInstance>(nullptr,
			TEXT("/Game/Characters/Mannequins/Anims/Rifle/ABP_TacticalRifle_MirrorTest.ABP_TacticalRifle_MirrorTest_C"));
		UE_LOG(LogTemp, Warning, TEXT("[MirrorTest] -MirrorFwdLeftTest ON; loaded class=%s"),
			MirrorAnimClass ? *MirrorAnimClass->GetPathName() : TEXT("NULL(FAILED TO LOAD)"));
		if (MirrorAnimClass)
			InWorld.GetTimerManager().SetTimer(MirrorTimer, this, &UYawTelemetryObserver::MirrorTick, 0.5f, true, 0.5f);
	}

	for (TActorIterator<ATacticalMovementCharacter> It(&InWorld); It; ++It) TryBind(*It);
	SpawnHandle = InWorld.AddOnActorSpawnedHandler(FOnActorSpawned::FDelegate::CreateUObject(this, &UYawTelemetryObserver::HandleActorSpawned));
	UE_LOG(LogTemp, Warning, TEXT("[StrafeFix] ACTIVE tag=%s netmode=%s -> %s"), *ProcessTag, NetModeStr(InWorld.GetNetMode()), *OutputPath);
}

void UYawTelemetryObserver::HandleActorSpawned(AActor* Actor) { if (ATacticalMovementCharacter* C = Cast<ATacticalMovementCharacter>(Actor)) TryBind(C); }

void UYawTelemetryObserver::TryBind(ATacticalMovementCharacter* Char)
{
	if (!bActive || !Char) return;
	USkeletalMeshComponent* Mesh = Char->GetMesh();
	if (!Mesh || FindBinding(Mesh) != nullptr) return;
	FBoundMesh B; B.Mesh = Mesh;
	B.Handle = Mesh->RegisterOnBoneTransformsFinalizedDelegate(
		FOnBoneTransformsFinalizedMultiCast::FDelegate::CreateUObject(this, &UYawTelemetryObserver::OnBonesFinalized, TWeakObjectPtr<USkeletalMeshComponent>(Mesh)));
	Bindings.Add(B);
}

// Dev-only. Applies the MirrorTest class ONCE per pawn, only after the mesh AnimInstance exists
// (delayed/repeating timer — NOT the spawn callback, NOT the finalize callback). After applying it
// monitors for reverts: on the first change away from MirrorTest it logs full detail and stops
// watching that pawn — it never reasserts and never reinitializes during pose finalization.
void UYawTelemetryObserver::MirrorTick()
{
	if (!bMirrorOverride || !MirrorAnimClass) return;
	const double T = FPlatformTime::Seconds() - StartTimeSeconds;
	for (FBoundMesh& B : Bindings)
	{
		USkeletalMeshComponent* Mesh = B.Mesh.Get();
		if (!Mesh) continue;
		ATacticalMovementCharacter* Char = Cast<ATacticalMovementCharacter>(Mesh->GetOwner());
		if (!Char) continue;

		if (!B.bMirrorApplied)
		{
			if (!Mesh->GetAnimInstance()) continue; // wait until AnimInstance exists (post-BeginPlay)
			if (Mesh->GetAnimClass() != MirrorAnimClass) Mesh->SetAnimInstanceClass(MirrorAnimClass);
			B.bMirrorApplied = true;
			const UAnimInstance* AI = Mesh->GetAnimInstance();
			const UClass* Now = AI ? AI->GetClass() : nullptr;
			UE_LOG(LogTemp, Warning, TEXT("[MirrorTest] t=%.2f APPLIED %s role=%s -> runtimeAnimClass=%s %s"),
				T, *Char->GetName(), RoleStr(Char->GetLocalRole()),
				Now ? *Now->GetPathName() : TEXT("NULL"), (Now == MirrorAnimClass) ? TEXT("(OK)") : TEXT("(FAILED)"));
		}
		else if (!B.bMirrorReverted)
		{
			const UClass* Cur = Mesh->GetAnimClass();
			if (Cur != MirrorAnimClass)
			{
				B.bMirrorReverted = true;
				UE_LOG(LogTemp, Error, TEXT("[MirrorTest] t=%.2f REVERT %s role=%s remoteRole=%s prev=%s -> new=%s"),
					T, *Char->GetName(), RoleStr(Char->GetLocalRole()), RoleStr(Char->GetRemoteRole()),
					*MirrorAnimClass->GetPathName(), Cur ? *Cur->GetPathName() : TEXT("NULL"));
			}
		}

		if (B.bMirrorApplied && !B.bMirrorReverted)
			if (UAnimInstance* AI = Mesh->GetAnimInstance()) IntrospectBlendSpace(B, AI, Char);
	}
}

// Dev-only. Reads the RUNTIME Blend Space held by the active BlendSpacePlayer of the running
// anim instance: one-shot startup dump of the -45 sample entries + mirror table; plus, while
// moving near dir -45, the active/triangulated sample indices, weights and mirror state. Read-only.
void UYawTelemetryObserver::IntrospectBlendSpace(FBoundMesh& B, UAnimInstance* AI, ATacticalMovementCharacter* Char)
{
	UBlendSpace* BS = FindRuntimeBlendSpace(AI);
	if (!BS) { if (!B.bBSLogged) { B.bBSLogged = true; UE_LOG(LogTemp, Error, TEXT("[MirrorBS] %s: no BlendSpacePlayer/BlendSpace found in %s"), *Char->GetName(), *AI->GetClass()->GetName()); } return; }

	const TArray<FBlendSample>& Samples = BS->GetBlendSamples();

	// current blend input from the observer's own signals (dir = reflected AnimBP Direction, speed = 2D velocity)
	double Dir = 0.0;
	if (const FDoubleProperty* DP = CastField<FDoubleProperty>(AI->GetClass()->FindPropertyByName(TEXT("Direction"))))
		Dir = DP->GetPropertyValue_InContainer(AI);
	const double Speed = Char->GetVelocity().Size2D();
	const FVector Input(Dir, Speed, 0.0);

	if (!B.bBSLogged)
	{
		B.bBSLogged = true;
		UE_LOG(LogTemp, Warning, TEXT("[MirrorBS] %s runtime BlendSpace=%s numSamples=%d"), *Char->GetName(), *BS->GetPathName(), Samples.Num());
		FString MdtPath = TEXT("None"), MdtSkel = TEXT("None"), MdtAxis = TEXT("None");
		if (const FObjectProperty* MP = CastField<FObjectProperty>(BS->GetClass()->FindPropertyByName(TEXT("MirrorDataTable"))))
		{
			if (UMirrorDataTable* MT = Cast<UMirrorDataTable>(MP->GetObjectPropertyValue_InContainer(BS)))
			{
				MdtPath = MT->GetPathName();
				MdtSkel = MT->Skeleton ? MT->Skeleton->GetName() : TEXT("None");
				MdtAxis = FString::FromInt((int32)MT->MirrorAxis.GetValue());
			}
		}
		UE_LOG(LogTemp, Warning, TEXT("[MirrorBS] MirrorDataTable=%s skeleton=%s axisEnum=%s"), *MdtPath, *MdtSkel, *MdtAxis);
		for (int32 i = 0; i < Samples.Num(); ++i)
		{
			const FBlendSample& S = Samples[i];
			if (FMath::Abs(S.SampleValue.X - (-45.0)) < 1.0)
				UE_LOG(LogTemp, Warning, TEXT("[MirrorBS] sample[%d] X=%.0f Y=%.0f anim=%s bMirror=%d"),
					i, S.SampleValue.X, S.SampleValue.Y, S.Animation ? *S.Animation->GetPathName() : TEXT("NULL"), S.bMirror ? 1 : 0);
		}
	}

	// Active/triangulated sample resolution while moving near fwd-left (throttled by the 0.5s timer).
	if (Speed > 40.0 && FMath::Abs(Dir - (-45.0)) < 20.0)
	{
		TArray<FBlendSampleData> ActiveList; int32 TriIdx = INDEX_NONE;
		BS->GetSamplesFromBlendInput(Input, ActiveList, TriIdx, false);
		for (const FBlendSampleData& SD : ActiveList)
		{
			if (SD.TotalWeight < 0.02f) continue;
			const int32 idx = SD.SampleDataIndex;
			const bool bValid = Samples.IsValidIndex(idx);
			UE_LOG(LogTemp, Warning, TEXT("[MirrorBS-active] %s dir=%.1f spd=%.1f tri=%d sample[%d] w=%.2f anim=%s bMirror=%d"),
				*Char->GetName(), Dir, Speed, TriIdx, idx, SD.TotalWeight,
				bValid && Samples[idx].Animation ? *Samples[idx].Animation->GetName() : TEXT("?"),
				bValid ? (Samples[idx].bMirror ? 1 : 0) : -1);
		}
	}
}

UYawTelemetryObserver::FBoundMesh* UYawTelemetryObserver::FindBinding(const USkeletalMeshComponent* Mesh)
{
	for (FBoundMesh& B : Bindings) if (B.Mesh.Get() == Mesh) return &B;
	return nullptr;
}

void UYawTelemetryObserver::ResolveWeapon(FBoundMesh& B, ATacticalMovementCharacter* Char)
{
	B.bWeaponResolved = true;
	TArray<UStaticMeshComponent*> Comps; Char->GetComponents(Comps);
	UStaticMeshComponent* Found = nullptr;
	for (UStaticMeshComponent* C : Comps)
	{
		if (!C || !C->GetStaticMesh()) continue;
		const bool bSocket = C->GetAttachSocketName() == FName(TEXT("HandGrip_R"));
		const bool bRifle = C->GetStaticMesh()->GetName().Contains(TEXT("SM_Rifle"));
		if (bSocket && bRifle) { Found = C; break; }
		if (!Found && bRifle) Found = C;
	}
	if (!Found) return;
	B.Weapon = Found;
	const FBox Box = Found->GetStaticMesh()->GetBoundingBox();
	B.RifleExt = Box.GetExtent();
	const FVector Ctr = Box.GetCenter();
	int32 axis = 0; double m = B.RifleExt.X;
	if (B.RifleExt.Y > m) { m = B.RifleExt.Y; axis = 1; }
	if (B.RifleExt.Z > m) { m = B.RifleExt.Z; axis = 2; }
	const double c = (axis == 0 ? Ctr.X : (axis == 1 ? Ctr.Y : Ctr.Z));
	const float sign = (c >= 0.0) ? 1.f : -1.f;
	B.RifleFwdAxis = axis; B.RifleFwdSign = sign;
	FVector lf = FVector::ZeroVector; if (axis == 0) lf.X = sign; else if (axis == 1) lf.Y = sign; else lf.Z = sign;
	B.RifleLocalForward = lf;
	UE_LOG(LogTemp, Warning, TEXT("[StrafeFix] %s WeaponMesh ext=(%.1f,%.1f,%.1f) -> localFwd axis=%d sign=%.0f"), *Char->GetName(), B.RifleExt.X, B.RifleExt.Y, B.RifleExt.Z, axis, sign);
}

void UYawTelemetryObserver::OnBonesFinalized(TWeakObjectPtr<USkeletalMeshComponent> WeakMesh)
{
	if (!bActive) return;
	USkeletalMeshComponent* Mesh = WeakMesh.Get();
	if (!Mesh) return;
	FBoundMesh* Bp = FindBinding(Mesh);
	if (!Bp) return;
	FBoundMesh& B = *Bp; B.CallbackCount++;
	ATacticalMovementCharacter* Char = Cast<ATacticalMovementCharacter>(Mesh->GetOwner());
	if (!Char) return;

	if (!B.bBoneIdxResolved)
	{
		B.IdxRoot = Mesh->GetBoneIndex(TEXT("root"));
		B.IdxPelvis = Mesh->GetBoneIndex(TEXT("pelvis"));
		B.IdxSpine01 = Mesh->GetBoneIndex(TEXT("spine_01"));
		B.bBoneIdxResolved = true;
	}
	if (!B.bWeaponResolved) ResolveWeapon(B, Char);

	UAnimInstance* AI = Mesh->GetAnimInstance();
	if (AI && (B.CachedAnimInstance.Get() != AI || B.CachedAnimClass != AI->GetClass()))
	{
		B.CachedAnimInstance = AI; B.CachedAnimClass = AI->GetClass();
		B.CachedDirProp = CastField<FDoubleProperty>(AI->GetClass()->FindPropertyByName(TEXT("Direction")));
	}
	double Dir = std::numeric_limits<double>::quiet_NaN(); bool bDirOk = false;
	if (AI && B.CachedDirProp) { Dir = B.CachedDirProp->GetPropertyValue_InContainer(AI); bDirOk = true; }

	const UWorld* W = Char->GetWorld();
	const ENetMode NM = W ? W->GetNetMode() : NM_Standalone;
	APlayerState* PS = Char->GetPlayerState();
	const int32 PawnId = PS ? PS->GetPlayerId() : -1;
	const UCharacterMovementComponent* CMC = Char->GetCharacterMovement();
	const bool bOrient = CMC ? CMC->bOrientRotationToMovement : false;

	const FRotator Aim = Char->GetBaseAimRotation();
	const FVector AimFwd = Aim.Vector();

	FVector RifleFwd = FVector::ZeroVector;
	if (B.Weapon.IsValid())
	{
		const FTransform SockT = Mesh->GetSocketTransform(FName(TEXT("HandGrip_R")), RTS_World);
		const FQuat RifleWorldQ = SockT.GetRotation() * B.Weapon->GetRelativeRotation().Quaternion();
		RifleFwd = RifleWorldQ.RotateVector(B.RifleLocalForward).GetSafeNormal();
	}
	const float RifleYaw = SignedHorizYaw(AimFwd, RifleFwd);

	const float ActorYaw = TwistZDeg(Char->GetActorQuat());
	const float MeshYaw = TwistZDeg(Mesh->GetComponentQuat());
	const TArray<FTransform>& CS = Mesh->GetComponentSpaceTransforms();
	auto BoneYaw = [&](int32 bi) -> float { return CS.IsValidIndex(bi) ? TwistZDeg(CS[bi].GetRotation()) : 0.f; };

	FString Row; Row.Reserve(768);
	Row += FString::Printf(TEXT("%.6f,%llu,%s,%s,%s,%s,%d,%d,%d,%d,%d,%.4f,%.6f,%d"),
		FPlatformTime::Seconds() - StartTimeSeconds, static_cast<uint64>(GFrameCounter), *ProcessTag, NetModeStr(NM),
		RoleStr(Char->GetLocalRole()), RoleStr(Char->GetRemoteRole()), PawnId,
		static_cast<int32>(Char->GetCombatReadinessState()), Char->IsSprinting() ? 1 : 0,
		bOrient ? 1 : 0, Char->bUseControllerRotationYaw ? 1 : 0, Char->GetVelocity().Size2D(), Dir, bDirOk ? 1 : 0);
	Row += FString::Printf(TEXT(",%.4f,%.4f"), Aim.Yaw, Aim.Pitch);
	AppendVec(Row, RifleFwd); Row += FString::Printf(TEXT(",%.4f"), RifleYaw);
	Row += FString::Printf(TEXT(",%d,%.0f,%.2f,%.2f,%.2f"), B.RifleFwdAxis, B.RifleFwdSign, B.RifleExt.X, B.RifleExt.Y, B.RifleExt.Z);
	Row += FString::Printf(TEXT(",%.4f,%.4f,%.4f,%.4f,%.4f"), ActorYaw, MeshYaw, BoneYaw(B.IdxRoot), BoneYaw(B.IdxPelvis), BoneYaw(B.IdxSpine01));
	Row += FString::Printf(TEXT(",%s"), AI ? *AI->GetClass()->GetName() : TEXT("None")); // observation only

	RowBuffer.Add(MoveTemp(Row));
	FlushRows(false);
}

void UYawTelemetryObserver::EnsureHeaderWritten()
{
	if (bHeaderWritten) return;
	FString H = TEXT("t_mono_s,frame,process_tag,net_mode,local_role,remote_role,pawn_id,readiness,sprint,bOrient,bUseCtrlYaw,speed,direction,dir_ok,");
	H += TEXT("aim_yaw,aim_pitch,rifle_fx,rifle_fy,rifle_fz,rifle_yaw_vs_aim,rifle_axis,rifle_sign,ext_x,ext_y,ext_z,");
	H += TEXT("actor_yaw,mesh_yaw,root_cs_yaw,pelvis_cs_yaw,spine01_cs_yaw,anim_class\n");
	IFileManager::Get().MakeDirectory(*FPaths::GetPath(OutputPath), true);
	FFileHelper::SaveStringToFile(H, *OutputPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_None);
	bHeaderWritten = true;
}

void UYawTelemetryObserver::FlushRows(bool bForce)
{
	if (RowBuffer.Num() == 0) return;
	if (!bForce && RowBuffer.Num() < 128) return;
	EnsureHeaderWritten();
	FString Block; Block.Reserve(RowBuffer.Num() * 256);
	for (const FString& R : RowBuffer) { Block += R; Block += TEXT("\n"); }
	FFileHelper::SaveStringToFile(Block, *OutputPath, FFileHelper::EEncodingOptions::ForceUTF8WithoutBOM, &IFileManager::Get(), FILEWRITE_Append);
	RowBuffer.Reset();
}

void UYawTelemetryObserver::Deinitialize()
{
	if (bActive)
	{
		if (UWorld* W = GetWorld()) W->GetTimerManager().ClearTimer(MirrorTimer);
		FlushRows(true);
		if (UWorld* W = GetWorld()) if (SpawnHandle.IsValid()) W->RemoveOnActorSpawnedHandler(SpawnHandle);
		for (FBoundMesh& B : Bindings)
		{
			if (USkeletalMeshComponent* M = B.Mesh.Get()) M->UnregisterOnBoneTransformsFinalizedDelegate(B.Handle);
			UE_LOG(LogTemp, Warning, TEXT("[StrafeFix] mesh callbacks=%d weapon=%d"), B.CallbackCount, B.Weapon.IsValid() ? 1 : 0);
		}
		Bindings.Reset();
		UE_LOG(LogTemp, Warning, TEXT("[StrafeFix] closed %s"), *OutputPath);
	}
	Super::Deinitialize();
}
