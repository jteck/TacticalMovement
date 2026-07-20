// Copyright Epic Games, Inc. All Rights Reserved.
//
// TacticalCharacterMovementComponent — server-authoritative, client-predicted movement
// for TacticalMovement's readiness / sprint / directional-speed identity.
//
// Design (see the movement-authority spec):
//  - The CMC intent fields (IntentReadiness / bIntentSprint / IntentDirClass) are the single
//    authoritative movement-intent source. The Character's CombatReadinessState / bIsSprinting
//    are a synchronized presentation/API mirror, never an independent movement source.
//  - Per-move readiness/sprint/predicted-direction ride custom FCharacterNetworkMoveData.
//  - The server derives the authoritative direction from the sub-move's standard acceleration
//    + control rotation (MoveAutonomous), clamps readiness/sprint (ServerMove_PerformMovement),
//    and forces a correction (bForceClientUpdate) carrying the final post-NewMove state via a
//    custom FCharacterMoveResponseDataContainer.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/CharacterMovementReplication.h"
#include "MovementProfileRow.h"
#include "TacticalMovementCharacter.h"   // ECombatReadinessState
#include "TacticalCharacterMovementComponent.generated.h"

/** Effective per-move directional class (2 bits). "None" only before any movement. */
UENUM()
enum class ETacticalMoveDir : uint8
{
	None    = 0,
	Forward = 1,
	Back    = 2,
	Strafe  = 3
};

// ---------------------------------------------------------------------------
// Custom network move data — carries readiness / sprint / predicted direction
// per client sub-move (Old/Pending/New).
// ---------------------------------------------------------------------------
struct FTacticalNetworkMoveData : public FCharacterNetworkMoveData
{
	typedef FCharacterNetworkMoveData Super;

	uint8 SavedReadiness = (uint8)ECombatReadinessState::LowReady; // 2 bits
	uint8 bSavedSprint   = 0;                                      // 1 bit
	uint8 SavedDirClass  = (uint8)ETacticalMoveDir::None;          // 2 bits

	virtual void ClientFillNetworkMoveData(const FSavedMove_Character& ClientMove, ENetworkMoveType MoveType) override;
	virtual bool Serialize(UCharacterMovementComponent& CharacterMovement, FArchive& Ar, UPackageMap* PackageMap, ENetworkMoveType MoveType) override;
};

struct FTacticalNetworkMoveDataContainer : public FCharacterNetworkMoveDataContainer
{
	FTacticalNetworkMoveDataContainer();
	FTacticalNetworkMoveData TacticalMoves[3];
};

// ---------------------------------------------------------------------------
// Custom move-response — returns the final post-NewMove authoritative
// readiness / sprint / direction to the owner on a forced correction.
// ---------------------------------------------------------------------------
struct FTacticalMoveResponseDataContainer : public FCharacterMoveResponseDataContainer
{
	typedef FCharacterMoveResponseDataContainer Super;

	uint8 AuthReadiness = (uint8)ECombatReadinessState::LowReady; // 2 bits
	uint8 bAuthSprint   = 0;                                      // 1 bit
	uint8 AuthDirClass  = (uint8)ETacticalMoveDir::None;          // 2 bits

	virtual void ServerFillResponseData(const UCharacterMovementComponent& CharacterMovement, const FClientAdjustment& PendingAdjustment) override;
	virtual bool Serialize(UCharacterMovementComponent& CharacterMovement, FArchive& Ar, UPackageMap* PackageMap) override;
};

// ---------------------------------------------------------------------------
// Saved move — captures/restores custom intent for client prediction & replay.
// ---------------------------------------------------------------------------
class FSavedMove_Tactical : public FSavedMove_Character
{
public:
	typedef FSavedMove_Character Super;

	uint8 SavedReadiness = (uint8)ECombatReadinessState::LowReady;
	uint8 bSavedSprint   = 0;
	uint8 SavedDirClass  = (uint8)ETacticalMoveDir::None;

	virtual void Clear() override;
	virtual void SetMoveFor(ACharacter* C, float InDeltaTime, FVector const& NewAccel, class FNetworkPredictionData_Client_Character& ClientData) override;
	virtual void PrepMoveFor(ACharacter* C) override;
	virtual bool CanCombineWith(const FSavedMovePtr& NewMove, ACharacter* C, float MaxDelta) const override;
	virtual bool IsImportantMove(const FSavedMovePtr& LastAckedMove) const override;
	// NOTE: custom state (5 bits) exceeds the 4 compressed-flag bits, so it rides the
	// custom network move data, NOT GetCompressedFlags().
};

class FNetworkPredictionData_Client_Tactical : public FNetworkPredictionData_Client_Character
{
public:
	FNetworkPredictionData_Client_Tactical(const UCharacterMovementComponent& ClientMovement);
	typedef FNetworkPredictionData_Client_Character Super;
	virtual FSavedMovePtr AllocateNewMove() override;
};

// ---------------------------------------------------------------------------
// The component.
// ---------------------------------------------------------------------------
UCLASS()
class TACTICALMOVEMENT_API UTacticalCharacterMovementComponent : public UCharacterMovementComponent
{
	GENERATED_BODY()

public:
	UTacticalCharacterMovementComponent();

	// --- Intent (authoritative movement-intent source) ---
	/** Set readiness + sprint intent atomically (applies ADS-cancels-sprint). No mirror callback. */
	void SetIntentReadinessAndSprint(ECombatReadinessState NewReadiness, bool bNewSprint);
	ECombatReadinessState GetReadinessIntent() const { return IntentReadiness; }
	bool GetSprintIntent() const { return bIntentSprint; }
	ETacticalMoveDir GetIntentDirClass() const { return IntentDirClass; }

	/** True if the intent readiness permits sprinting (ADS forbids it). */
	bool ReadinessAllowsSprint() const;

	/** Cache the two movement-profile rows once (BeginPlay). Avoids per-getter DataTable lookups. */
	void CacheProfilesFromTable(const class UDataTable* Table, FName DefaultRow, FName SprintRow);
	bool AreProfilesCached() const { return bProfilesCached; }

	/** Restore saved intent onto the CMC before a replayed move (called by FSavedMove_Tactical::PrepMoveFor). */
	void RestoreIntentForReplay(ECombatReadinessState R, bool bSprint, ETacticalMoveDir Dir);

	/** Control-relative direction classification (public for automation tests).
	 *  Matches the original DoMove semantics; returns FallbackWhenZero for ~zero input. */
	ETacticalMoveDir ClassifyDir(const FVector& WorldVec, const FRotator& ControlRotation, ETacticalMoveDir FallbackWhenZero) const;

	// --- Engine overrides ---
	virtual void ControlledCharacterMove(const FVector& InputVector, float DeltaSeconds) override;
	virtual void MoveAutonomous(float ClientTimeStamp, float DeltaTime, uint8 CompressedFlags, const FVector& NewAccel) override;
	virtual void ServerMove_PerformMovement(const FCharacterNetworkMoveData& MoveData) override;
	virtual void ClientHandleMoveResponse(const FCharacterMoveResponseDataContainer& MoveResponse) override;
	virtual float GetMaxSpeed() const override;
	virtual class FNetworkPredictionData_Client* GetPredictionData_Client() const override;

	friend class FSavedMove_Tactical;
	friend struct FTacticalMoveResponseDataContainer;

protected:
	// Intent (movement authority). NOT replicated; the Character mirror carries replication.
	ECombatReadinessState IntentReadiness = ECombatReadinessState::LowReady;
	bool bIntentSprint = false;
	ETacticalMoveDir IntentDirClass = ETacticalMoveDir::None;

	// Retained direction for zero-input deceleration (role-local, never serialized).
	ETacticalMoveDir LastNonZeroDirClass = ETacticalMoveDir::Forward;        // client predict
	ETacticalMoveDir ServerLastNonZeroDirClass = ETacticalMoveDir::Forward;  // server authoritative

	// Cached movement-profile rows.
	FMovementProfileRow ProfileDefault;
	FMovementProfileRow ProfileSprint;
	bool bProfilesCached = false;

	// Helpers
	void ApplyResolvedProfileForCurrentMove();
	const FMovementProfileRow& ActiveProfile() const { return bIntentSprint ? ProfileSprint : ProfileDefault; }
	float ReadinessSpeedMultiplier() const;
	/** Active profile's directional (Forward/Back/Strafe) cap scaled by the readiness multiplier. */
	float ProfileDirectionalCap() const;
	/** Push accepted intent to the owning Character's synchronized mirror (server/authority + owner correction). */
	void SyncMirrorToOwner();

	// Persistent container storage.
	FTacticalNetworkMoveDataContainer TacticalMoveDataContainer;
	FTacticalMoveResponseDataContainer TacticalMoveResponseContainer;
};
