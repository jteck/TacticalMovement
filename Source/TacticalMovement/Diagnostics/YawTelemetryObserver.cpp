// Development-only strafe-fix acceptance observer. See header for scope.

#include "Diagnostics/YawTelemetryObserver.h"

#include "TacticalMovementCharacter.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Animation/AnimInstance.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/PlayerState.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
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
		B.IdxSpine02 = Mesh->GetBoneIndex(TEXT("spine_02"));
		B.IdxSpine03 = Mesh->GetBoneIndex(TEXT("spine_03"));
		B.IdxSpine04 = Mesh->GetBoneIndex(TEXT("spine_04"));
		B.IdxSpine05 = Mesh->GetBoneIndex(TEXT("spine_05"));
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
	Row += FString::Printf(TEXT(",%.4f,%.4f,%.4f,%.4f"), BoneYaw(B.IdxSpine02), BoneYaw(B.IdxSpine03), BoneYaw(B.IdxSpine04), BoneYaw(B.IdxSpine05));

	RowBuffer.Add(MoveTemp(Row));
	FlushRows(false);
}

void UYawTelemetryObserver::EnsureHeaderWritten()
{
	if (bHeaderWritten) return;
	FString H = TEXT("t_mono_s,frame,process_tag,net_mode,local_role,remote_role,pawn_id,readiness,sprint,bOrient,bUseCtrlYaw,speed,direction,dir_ok,");
	H += TEXT("aim_yaw,aim_pitch,rifle_fx,rifle_fy,rifle_fz,rifle_yaw_vs_aim,rifle_axis,rifle_sign,ext_x,ext_y,ext_z,");
	H += TEXT("actor_yaw,mesh_yaw,root_cs_yaw,pelvis_cs_yaw,spine01_cs_yaw,spine02_cs_yaw,spine03_cs_yaw,spine04_cs_yaw,spine05_cs_yaw\n");
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
