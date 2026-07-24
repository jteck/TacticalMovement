// Development-only strafe-fix acceptance observer (diagnostic; NEVER shipped).
//
// Measures, on the observed pawn (both net roles): rendered SM_Rifle muzzle-forward vs
// GetBaseAimRotation() (signed horizontal yaw + aim pitch), plus component-space yaw of
// root/pelvis/spine_01 and world yaw of actor/CharacterMesh0, + Direction/speed/readiness.
// Reads untouched production assets/components live. Inert unless launched with -YawTelemetry,
// game/PIE worlds only. Rifle local-forward axis verified from static-mesh bounds and logged.

#pragma once

#include "CoreMinimal.h"
#include "Subsystems/WorldSubsystem.h"
#include "UObject/WeakObjectPtr.h"
#include "YawTelemetryObserver.generated.h"

class USkeletalMeshComponent;
class UStaticMeshComponent;
class UAnimInstance;
class ATacticalMovementCharacter;

UCLASS()
class UYawTelemetryObserver : public UWorldSubsystem
{
	GENERATED_BODY()

public:
	virtual bool ShouldCreateSubsystem(UObject* Outer) const override;
	virtual void OnWorldBeginPlay(UWorld& InWorld) override;
	virtual void Deinitialize() override;

private:
	struct FBoundMesh
	{
		TWeakObjectPtr<USkeletalMeshComponent> Mesh;
		FDelegateHandle Handle;

		TWeakObjectPtr<UAnimInstance> CachedAnimInstance;
		const UClass* CachedAnimClass = nullptr;
		FDoubleProperty* CachedDirProp = nullptr;

		TWeakObjectPtr<UStaticMeshComponent> Weapon;
		bool bWeaponResolved = false;
		FVector RifleLocalForward = FVector::ForwardVector;
		int32 RifleFwdAxis = -1;
		float RifleFwdSign = 1.f;
		FVector RifleExt = FVector::ZeroVector;

		int32 IdxRoot = INDEX_NONE;
		int32 IdxPelvis = INDEX_NONE;
		int32 IdxSpine01 = INDEX_NONE;
		bool bBoneIdxResolved = false;

		int32 CallbackCount = 0;

		// Dev-only mirror-override bookkeeping (apply-once + revert detection).
		bool bMirrorApplied = false;
		bool bMirrorReverted = false;
		bool bBSLogged = false; // one-shot startup Blend Space sample-map dump
	};

	void HandleActorSpawned(AActor* Actor);
	void TryBind(ATacticalMovementCharacter* Char);
	void OnBonesFinalized(TWeakObjectPtr<USkeletalMeshComponent> WeakMesh);
	FBoundMesh* FindBinding(const USkeletalMeshComponent* Mesh);
	void ResolveWeapon(FBoundMesh& B, ATacticalMovementCharacter* Char);
	void EnsureHeaderWritten();
	void FlushRows(bool bForce);

	static float SignedHorizYaw(const FVector& Ref, const FVector& V);
	static float TwistZDeg(const FQuat& Q); // yaw about Z, degrees

	TArray<FBoundMesh> Bindings;
	FDelegateHandle SpawnHandle;

	bool bActive = false;

	// Dev-only runtime AnimClass override (flag: -MirrorFwdLeftTest). Inert without the flag.
	// Applied ONCE per pawn via a delayed/repeating timer (after mesh AnimInstance exists);
	// never reasserted from the finalized-bones callback. Reverts are logged, not fought.
	bool bMirrorOverride = false;
	UPROPERTY()
	TSubclassOf<UAnimInstance> MirrorAnimClass = nullptr;
	FTimerHandle MirrorTimer;
	void MirrorTick();
	void IntrospectBlendSpace(FBoundMesh& B, class UAnimInstance* AI, ATacticalMovementCharacter* Char);

	FString ProcessTag;
	FString OutputPath;
	bool bHeaderWritten = false;

	TArray<FString> RowBuffer;
	double StartTimeSeconds = 0.0;
};
