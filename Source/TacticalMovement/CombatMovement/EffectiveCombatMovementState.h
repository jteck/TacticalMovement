// EffectiveCombatMovementState.h

#pragma once

#include "CoreMinimal.h"
#include "EffectiveCombatMovementState.generated.h"

UENUM(BlueprintType)
enum class ECombatStance : uint8
{
    Standing    UMETA(DisplayName = "Standing"),
    Crouched    UMETA(DisplayName = "Crouched"),
    Prone       UMETA(DisplayName = "Prone")
};

UENUM(BlueprintType)
enum class EADSState : uint8
{
    Hipfire          UMETA(DisplayName = "Hipfire"),
    TransitioningIn  UMETA(DisplayName = "Transitioning In"),
    ADS              UMETA(DisplayName = "ADS"),
    TransitioningOut UMETA(DisplayName = "Transitioning Out")
};

UENUM(BlueprintType)
enum class EEncumbranceState : uint8
{
    None       UMETA(DisplayName = "None"),
    Overweight UMETA(DisplayName = "Overweight"),
    Heavy      UMETA(DisplayName = "Heavy")
};

/**
 * Runtime combined state used by movement + weapon systems.
 * Filled from MovementProfileRow, WeaponHandlingRow, stance, ADS, etc.
 */
USTRUCT(BlueprintType)
struct FEffectiveCombatMovementState
{
    GENERATED_BODY();

public:

    // --- Context ---

    UPROPERTY(BlueprintReadOnly, Category="Context")
    ECombatStance Stance = ECombatStance::Standing;

    UPROPERTY(BlueprintReadOnly, Category="Context")
    EADSState ADSState = EADSState::Hipfire;

    UPROPERTY(BlueprintReadOnly, Category="Context")
    bool bIsSprinting = false;

    UPROPERTY(BlueprintReadOnly, Category="Context")
    EEncumbranceState Encumbrance = EEncumbranceState::None;

    // --- Movement ---

    /** Max speed along ground, after all modifiers (cm/s). */
    UPROPERTY(BlueprintReadOnly, Category="Movement")
    float EffectiveMaxSpeed = 0.f;

    /** Final acceleration used by movement (cm/s^2). */
    UPROPERTY(BlueprintReadOnly, Category="Movement")
    float EffectiveAcceleration = 0.f;

    /** Final braking deceleration used when stopping (cm/s^2). */
    UPROPERTY(BlueprintReadOnly, Category="Movement")
    float EffectiveBraking = 0.f;

    /** Final friction coefficient (higher = stops faster). */
    UPROPERTY(BlueprintReadOnly, Category="Movement")
    float EffectiveFriction = 0.f;

    /** Yaw rotation rate in deg/sec. */
    UPROPERTY(BlueprintReadOnly, Category="Movement")
    float EffectiveTurnRate = 0.f;

    // --- ADS / Aiming ---

    /** Max movement speed while ADS (cm/s). */
    UPROPERTY(BlueprintReadOnly, Category="Aiming")
    float EffectiveADSSpeed = 0.f;

    // --- Weapon handling modifiers ---

    /** Multiplier for weapon recoil (1.0 = weapon baseline). */
    UPROPERTY(BlueprintReadOnly, Category="Weapon")
    float EffectiveRecoilMultiplier = 1.f;

    /** Multiplier for sway/bob (1.0 = weapon baseline). */
    UPROPERTY(BlueprintReadOnly, Category="Weapon")
    float EffectiveSwayMultiplier = 1.f;
};