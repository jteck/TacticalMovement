// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalCharacterMovementComponent.h"
#include "GameFramework/Character.h"
#include "GameFramework/Controller.h"
#include "Engine/DataTable.h"

// ===========================================================================
// FTacticalNetworkMoveData / Container
// ===========================================================================
void FTacticalNetworkMoveData::ClientFillNetworkMoveData(const FSavedMove_Character& ClientMove, ENetworkMoveType MoveType)
{
	Super::ClientFillNetworkMoveData(ClientMove, MoveType);

	const FSavedMove_Tactical& TacticalMove = static_cast<const FSavedMove_Tactical&>(ClientMove);
	SavedReadiness = TacticalMove.SavedReadiness;
	bSavedSprint   = TacticalMove.bSavedSprint;
	SavedDirClass  = TacticalMove.SavedDirClass;
}

bool FTacticalNetworkMoveData::Serialize(UCharacterMovementComponent& CharacterMovement, FArchive& Ar, UPackageMap* PackageMap, ENetworkMoveType MoveType)
{
	if (!Super::Serialize(CharacterMovement, Ar, PackageMap, MoveType))
	{
		return false;
	}

	// 2 + 1 + 2 bits; the 2-bit fields are inherently within the 4-value enum ranges.
	Ar.SerializeBits(&SavedReadiness, 2);
	Ar.SerializeBits(&bSavedSprint, 1);
	Ar.SerializeBits(&SavedDirClass, 2);

	return !Ar.IsError();
}

FTacticalNetworkMoveDataContainer::FTacticalNetworkMoveDataContainer()
{
	// Point the base's move-data slots at our custom-typed storage (New / Pending / Old).
	NewMoveData     = &TacticalMoves[0];
	PendingMoveData = &TacticalMoves[1];
	OldMoveData     = &TacticalMoves[2];
}

// ===========================================================================
// FTacticalMoveResponseDataContainer
// ===========================================================================
void FTacticalMoveResponseDataContainer::ServerFillResponseData(const UCharacterMovementComponent& CharacterMovement, const FClientAdjustment& PendingAdjustment)
{
	Super::ServerFillResponseData(CharacterMovement, PendingAdjustment);

	// Read the final post-NewMove authoritative state from the server CMC.
	if (const UTacticalCharacterMovementComponent* TCMC = Cast<UTacticalCharacterMovementComponent>(&CharacterMovement))
	{
		AuthReadiness = (uint8)TCMC->GetReadinessIntent();
		bAuthSprint   = TCMC->GetSprintIntent() ? 1 : 0;
		AuthDirClass  = (uint8)TCMC->GetIntentDirClass();
	}
}

bool FTacticalMoveResponseDataContainer::Serialize(UCharacterMovementComponent& CharacterMovement, FArchive& Ar, UPackageMap* PackageMap)
{
	if (!Super::Serialize(CharacterMovement, Ar, PackageMap))
	{
		return false;
	}

	// Only correction responses carry the authoritative state (good-move acks stay tiny).
	if (IsCorrection())
	{
		Ar.SerializeBits(&AuthReadiness, 2);
		Ar.SerializeBits(&bAuthSprint, 1);
		Ar.SerializeBits(&AuthDirClass, 2);
	}

	return !Ar.IsError();
}

// ===========================================================================
// FSavedMove_Tactical
// ===========================================================================
void FSavedMove_Tactical::Clear()
{
	Super::Clear();
	SavedReadiness = (uint8)ECombatReadinessState::LowReady;
	bSavedSprint   = 0;
	SavedDirClass  = (uint8)ETacticalMoveDir::None;
}

void FSavedMove_Tactical::SetMoveFor(ACharacter* C, float InDeltaTime, FVector const& NewAccel, FNetworkPredictionData_Client_Character& ClientData)
{
	Super::SetMoveFor(C, InDeltaTime, NewAccel, ClientData);

	if (const UTacticalCharacterMovementComponent* TCMC = C ? Cast<UTacticalCharacterMovementComponent>(C->GetCharacterMovement()) : nullptr)
	{
		SavedReadiness = (uint8)TCMC->GetReadinessIntent();
		bSavedSprint   = TCMC->GetSprintIntent() ? 1 : 0;
		SavedDirClass  = (uint8)TCMC->GetIntentDirClass();
	}
}

void FSavedMove_Tactical::PrepMoveFor(ACharacter* C)
{
	Super::PrepMoveFor(C);

	if (UTacticalCharacterMovementComponent* TCMC = C ? Cast<UTacticalCharacterMovementComponent>(C->GetCharacterMovement()) : nullptr)
	{
		TCMC->RestoreIntentForReplay((ECombatReadinessState)SavedReadiness, bSavedSprint != 0, (ETacticalMoveDir)SavedDirClass);
	}
}

bool FSavedMove_Tactical::CanCombineWith(const FSavedMovePtr& NewMove, ACharacter* C, float MaxDelta) const
{
	const FSavedMove_Tactical& New = static_cast<const FSavedMove_Tactical&>(*NewMove);
	if (SavedReadiness != New.SavedReadiness || bSavedSprint != New.bSavedSprint || SavedDirClass != New.SavedDirClass)
	{
		// A readiness/sprint/direction transition must not be merged and replayed under a newer state.
		return false;
	}
	return Super::CanCombineWith(NewMove, C, MaxDelta);
}

bool FSavedMove_Tactical::IsImportantMove(const FSavedMovePtr& LastAckedMove) const
{
	const FSavedMove_Tactical& Last = static_cast<const FSavedMove_Tactical&>(*LastAckedMove);
	if (SavedReadiness != Last.SavedReadiness || bSavedSprint != Last.bSavedSprint || SavedDirClass != Last.SavedDirClass)
	{
		// Makes the transition eligible for old-important-move resend (NOT literal RPC reliability).
		return true;
	}
	return Super::IsImportantMove(LastAckedMove);
}

// ===========================================================================
// FNetworkPredictionData_Client_Tactical
// ===========================================================================
FNetworkPredictionData_Client_Tactical::FNetworkPredictionData_Client_Tactical(const UCharacterMovementComponent& ClientMovement)
	: Super(ClientMovement)
{
}

FSavedMovePtr FNetworkPredictionData_Client_Tactical::AllocateNewMove()
{
	return MakeShared<FSavedMove_Tactical>();
}

// ===========================================================================
// UTacticalCharacterMovementComponent
// ===========================================================================
UTacticalCharacterMovementComponent::UTacticalCharacterMovementComponent()
{
	SetNetworkMoveDataContainer(TacticalMoveDataContainer);
	SetMoveResponseDataContainer(TacticalMoveResponseContainer);
}

FNetworkPredictionData_Client* UTacticalCharacterMovementComponent::GetPredictionData_Client() const
{
	if (ClientPredictionData == nullptr)
	{
		UTacticalCharacterMovementComponent* MutableThis = const_cast<UTacticalCharacterMovementComponent*>(this);
		MutableThis->ClientPredictionData = new FNetworkPredictionData_Client_Tactical(*this);
	}
	return ClientPredictionData;
}

float UTacticalCharacterMovementComponent::ReadinessSpeedMultiplier() const
{
	switch (IntentReadiness)
	{
		case ECombatReadinessState::Sul:           return 1.00f;
		case ECombatReadinessState::LowReady:      return 0.90f;
		case ECombatReadinessState::MovementReady: return 1.00f;
		case ECombatReadinessState::ADS:           return 0.75f;
		default:                                   return 1.00f;
	}
}

bool UTacticalCharacterMovementComponent::ReadinessAllowsSprint() const
{
	return IntentReadiness != ECombatReadinessState::ADS;
}

void UTacticalCharacterMovementComponent::SetIntentReadinessAndSprint(ECombatReadinessState NewReadiness, bool bNewSprint)
{
	// ADS cancels sprint.
	if (NewReadiness == ECombatReadinessState::ADS)
	{
		bNewSprint = false;
	}
	IntentReadiness = NewReadiness;
	bIntentSprint = bNewSprint;
}

void UTacticalCharacterMovementComponent::RestoreIntentForReplay(ECombatReadinessState R, bool bSprint, ETacticalMoveDir Dir)
{
	IntentReadiness = R;
	bIntentSprint = bSprint;
	IntentDirClass = Dir;
	if (Dir != ETacticalMoveDir::None)
	{
		LastNonZeroDirClass = Dir;
	}
	// Do NOT touch the Character mirror here: replay re-simulates historical moves;
	// the mirror reflects current predicted state, already set by input / correction.
}

void UTacticalCharacterMovementComponent::CacheProfilesFromTable(const UDataTable* Table, FName DefaultRow, FName SprintRow)
{
	// Require a valid table AND a valid default row before caching. If either is absent,
	// leave profiles uncached so GetMaxSpeed() falls back to the engine base speed rather
	// than silently using struct-default profile values.
	const FMovementProfileRow* DefRow = Table
		? Table->FindRow<FMovementProfileRow>(DefaultRow, TEXT("TacticalCMC:Default"))
		: nullptr;
	if (!DefRow)
	{
		bProfilesCached = false;
		return;
	}
	ProfileDefault = *DefRow;

	// Sprint row is optional; fall back to the default row if absent so sprint is safe.
	if (!SprintRow.IsNone())
	{
		if (const FMovementProfileRow* Row = Table->FindRow<FMovementProfileRow>(SprintRow, TEXT("TacticalCMC:Sprint")))
		{
			ProfileSprint = *Row;
		}
		else
		{
			ProfileSprint = ProfileDefault;
		}
	}
	else
	{
		ProfileSprint = ProfileDefault;
	}

	bProfilesCached = true;
}

ETacticalMoveDir UTacticalCharacterMovementComponent::ClassifyDir(const FVector& WorldVec, const FRotator& ControlRotation, ETacticalMoveDir FallbackWhenZero) const
{
	// Control-relative classification (matches the original DoMove semantics: any forward
	// component wins forward/back by sign; pure-lateral -> strafe). Scale-independent.
	const FVector Flat(WorldVec.X, WorldVec.Y, 0.0f);
	const FVector Dir = Flat.GetSafeNormal();
	if (Dir.IsNearlyZero())
	{
		return FallbackWhenZero;
	}

	const FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);
	const FVector Fwd   = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
	const FVector Right = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

	const float F = FVector::DotProduct(Dir, Fwd);
	const float R = FVector::DotProduct(Dir, Right);

	// ~3 degrees off pure-lateral counts as a forward/back component.
	const float kEps = 0.05f;
	if (FMath::Abs(F) > kEps)
	{
		return (F > 0.0f) ? ETacticalMoveDir::Forward : ETacticalMoveDir::Back;
	}
	if (FMath::Abs(R) > kEps)
	{
		return ETacticalMoveDir::Strafe;
	}
	return FallbackWhenZero;
}

void UTacticalCharacterMovementComponent::ApplyResolvedProfileForCurrentMove()
{
	if (!bProfilesCached)
	{
		return;
	}

	const FMovementProfileRow& P = ActiveProfile();

	// Members consumed DIRECTLY by the engine before / inside PerformMovement (must be set
	// before CheckJumpInput): JumpZVelocity (DoJump), GroundFriction (walking CalcVelocity),
	// AirControl (falling), plus accel/braking/crouch caps.
	JumpZVelocity              = P.JumpZVelocity;
	AirControl                 = P.AirControl;
	GroundFriction             = P.GroundFriction;
	MaxAcceleration            = P.MaxAcceleration;
	BrakingDecelerationWalking = P.BrakingDeceleration;
	MaxWalkSpeedCrouched       = P.MaxWalkSpeedForward * P.CrouchSpeedMultiplier;
	// MaxWalkSpeed is handled per-direction+readiness by GetMaxSpeed().
}

float UTacticalCharacterMovementComponent::ProfileDirectionalCap() const
{
	const FMovementProfileRow& P = ActiveProfile();
	float Base;
	switch (IntentDirClass)
	{
		case ETacticalMoveDir::Forward: Base = P.MaxWalkSpeedForward; break;
		case ETacticalMoveDir::Back:    Base = P.MaxWalkSpeedBack;    break;
		case ETacticalMoveDir::Strafe:  Base = P.MaxWalkSpeedStrafe;  break;
		default:                        Base = P.MaxWalkSpeedForward; break; // None (pre-movement) -> forward cap
	}
	return Base * ReadinessSpeedMultiplier();
}

float UTacticalCharacterMovementComponent::GetMaxSpeed() const
{
	if (!bProfilesCached)
	{
		return Super::GetMaxSpeed();
	}

	switch (MovementMode)
	{
		case MOVE_Walking:
		case MOVE_NavWalking:
			// Preserve main's crouch contract (base returns MaxWalkSpeedCrouched while crouched);
			// otherwise the active directional/readiness profile cap.
			return IsCrouching() ? MaxWalkSpeedCrouched : ProfileDirectionalCap();

		case MOVE_Falling:
			// Preserve main's airborne cap: base GetMaxSpeed returns MaxWalkSpeed while falling,
			// which main kept updated to the directional/readiness profile speed before each move.
			return ProfileDirectionalCap();

		default:
			// Swimming / Flying / Custom / None: unchanged engine behavior.
			return Super::GetMaxSpeed();
	}
}

void UTacticalCharacterMovementComponent::SyncMirrorToOwner()
{
	if (ATacticalMovementCharacter* TC = Cast<ATacticalMovementCharacter>(GetCharacterOwner()))
	{
		TC->SyncReadinessMirror(IntentReadiness, bIntentSprint);
	}
}

void UTacticalCharacterMovementComponent::ControlledCharacterMove(const FVector& InputVector, float DeltaSeconds)
{
	// Covers listen-server/local authority, autonomous-client fresh predict, and server AI.
	// Derive the predicted direction from pre-clamp control-relative input; retain last-nonzero at zero input.
	if (CharacterOwner)
	{
		const ETacticalMoveDir Derived = ClassifyDir(InputVector, CharacterOwner->GetControlRotation(), LastNonZeroDirClass);
		IntentDirClass = Derived;
		if (Derived != ETacticalMoveDir::None)
		{
			LastNonZeroDirClass = Derived;
		}
	}

	ApplyResolvedProfileForCurrentMove();

	Super::ControlledCharacterMove(InputVector, DeltaSeconds);
}

void UTacticalCharacterMovementComponent::MoveAutonomous(float ClientTimeStamp, float DeltaTime, uint8 CompressedFlags, const FVector& NewAccel)
{
	// Server processing a remote autonomous proxy's move: derive the authoritative direction.
	// (Client replay has LocalRole == AutonomousProxy and skips this — it uses the restored intent.)
	const bool bServerRemote = CharacterOwner
		&& CharacterOwner->GetLocalRole() == ROLE_Authority
		&& !CharacterOwner->IsLocallyControlled();

	if (bServerRemote)
	{
		// 1. Sub-move acceleration + already-applied control rotation (set by ServerMove_PerformMovement -> Super).
		const FRotator ControlRot = CharacterOwner->GetControlRotation();
		// 2. Derive authoritative direction (retain server last-nonzero at zero input).
		const ETacticalMoveDir Auth = ClassifyDir(NewAccel, ControlRot, ServerLastNonZeroDirClass);
		// 3. Compare with the submitted prediction hint (currently held in IntentDirClass); force correction on mismatch.
		if (Auth != IntentDirClass)
		{
			if (FNetworkPredictionData_Server_Character* ServerData = GetPredictionData_Server_Character())
			{
				ServerData->bForceClientUpdate = true;
			}
		}
		// 4. Set authoritative intent + update server last-nonzero.
		IntentDirClass = Auth;
		if (Auth != ETacticalMoveDir::None)
		{
			ServerLastNonZeroDirClass = Auth;
		}
	}

	// 5. Apply cached profile members (before CheckJumpInput inside Super).
	ApplyResolvedProfileForCurrentMove();

	// 6. Simulate.
	Super::MoveAutonomous(ClientTimeStamp, DeltaTime, CompressedFlags, NewAccel);
}

void UTacticalCharacterMovementComponent::ServerMove_PerformMovement(const FCharacterNetworkMoveData& MoveData)
{
	// Readiness/sprint extraction + validation + clamp BEFORE Super (per the ordering mandate).
	// The DIRECTION mismatch check lives in MoveAutonomous, where the authoritative direction is derived.
	const FTacticalNetworkMoveData& TD = static_cast<const FTacticalNetworkMoveData&>(MoveData);

	bool bChanged = false;

	// Enum bounds (2 bits is already 0..3, but keep an explicit guard).
	uint8 ReadinessRaw = TD.SavedReadiness;
	if (ReadinessRaw > (uint8)ECombatReadinessState::ADS)
	{
		ReadinessRaw = (uint8)ECombatReadinessState::LowReady;
		bChanged = true;
	}
	ECombatReadinessState ReqReadiness = (ECombatReadinessState)ReadinessRaw;
	bool bReqSprint = TD.bSavedSprint != 0;

	// ADS cancels sprint / sprint eligibility.
	if (bReqSprint && ReqReadiness == ECombatReadinessState::ADS)
	{
		bReqSprint = false;
		bChanged = true;
	}
	// Movement-profile availability.
	if (bReqSprint && !bProfilesCached)
	{
		bReqSprint = false;
		bChanged = true;
	}

	IntentReadiness = ReqReadiness;
	bIntentSprint = bReqSprint;

	// Stash the submitted direction hint (validated bounds) for MoveAutonomous to compare against.
	uint8 DirRaw = TD.SavedDirClass;
	if (DirRaw > (uint8)ETacticalMoveDir::Strafe)
	{
		DirRaw = (uint8)ETacticalMoveDir::None;
	}
	IntentDirClass = (ETacticalMoveDir)DirRaw;

	if (bChanged)
	{
		if (FNetworkPredictionData_Server_Character* ServerData = GetPredictionData_Server_Character())
		{
			ServerData->bForceClientUpdate = true;
		}
	}

	Super::ServerMove_PerformMovement(MoveData);

	// After the NewMove has been fully simulated, sync the accepted authoritative state to the
	// Character mirror (replicated to simulated proxies via COND_SimulatedOnly).
	if (MoveData.NetworkMoveType == FCharacterNetworkMoveData::ENetworkMoveType::NewMove)
	{
		SyncMirrorToOwner();
	}
}

void UTacticalCharacterMovementComponent::ClientHandleMoveResponse(const FCharacterMoveResponseDataContainer& MoveResponse)
{
	// On a correction, apply the final authoritative readiness/sprint/direction to CMC intent +
	// the owner mirror BEFORE the base triggers replay.
	if (MoveResponse.IsCorrection())
	{
		const FTacticalMoveResponseDataContainer& TR = static_cast<const FTacticalMoveResponseDataContainer&>(MoveResponse);

		IntentReadiness = (ECombatReadinessState)TR.AuthReadiness;
		bIntentSprint = TR.bAuthSprint != 0;

		const ETacticalMoveDir AuthDir = (ETacticalMoveDir)TR.AuthDirClass;
		IntentDirClass = AuthDir;
		if (AuthDir != ETacticalMoveDir::None)
		{
			LastNonZeroDirClass = AuthDir;
		}

		SyncMirrorToOwner();
	}

	Super::ClientHandleMoveResponse(MoveResponse);
}
