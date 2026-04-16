// MovementProfileRow.h

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "MovementProfileRow.generated.h"

/**
 * Movement-only tuning for a given "body profile":
 * stance, load, friction, etc. Weapon-specific stuff is separate.
 */
USTRUCT(BlueprintType)
struct FMovementProfileRow : public FTableRowBase
{
    GENERATED_BODY()

public:

    /** Optional logical ID (often the same as row name). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ID")
    FName ProfileId;

    // -------- Base Ground Speeds (Standing, Unencumbered) --------

    /** Max walking speed forwards (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Walk")
    float MaxWalkSpeedForward = 350.f;

    /** Max walking speed strafing left/right (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Walk")
    float MaxWalkSpeedStrafe = 300.f;

    /** Max walking speed backwards (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Walk")
    float MaxWalkSpeedBack = 250.f;

    /** Max sprinting speed forwards (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Sprint")
    float MaxSprintSpeedForward = 600.f;

    /** Max sprinting speed strafing (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Sprint")
    float MaxSprintSpeedStrafe = 520.f;

    /** Max sprinting speed backwards (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Speed|Sprint")
    float MaxSprintSpeedBack = 200.f;

    // -------- Stance Multipliers --------

    /** Walk/sprint speed multiplier when crouched. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stance")
    float CrouchSpeedMultiplier = 0.45f;

    /** Walk/sprint speed multiplier when prone. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stance")
    float ProneSpeedMultiplier = 0.20f;

    /** Speed multiplier while ADS (aiming down sights). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Modifiers")
    float ADSMoveSpeedMultiplier = 0.6f;

    // -------- Condition / Load Multipliers --------

    /** Movement multiplier when injured (0–1 region, applied via InjuryFactor). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Modifiers")
    float InjuredSpeedMultiplier = 0.85f;

    /** Movement multiplier when overweight. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Modifiers")
    float OverweightSpeedMultiplier = 0.75f;

    /** Movement multiplier when heavily overweight. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Modifiers")
    float HeavilyOverweightSpeedMultiplier = 0.55f;

    // -------- Core Physics Coefficients --------

    /** Max acceleration on ground (cm/s^2). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float MaxAcceleration = 2048.f;

    /** Base braking deceleration (cm/s^2) for stopping. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float BrakingDeceleration = 2048.f;

    /** Ground friction coefficient (higher = stops faster). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float GroundFriction = 8.f;

    /** Character rotation rate while moving (deg/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    FRotator RotationRate = FRotator(0.f, 540.f, 0.f);

    /**
     * Multiplier applied to GroundFriction when braking from sprint
     * to tune "slide/brake" feel.
     */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float SprintBrakeFrictionMultiplier = 0.75f;

    /** Air control (0–1). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Air")
    float AirControl = 0.2f;

    /** Jump initial velocity (cm/s). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Air")
    float JumpZVelocity = 420.f;

    /** Step height for walking up small obstacles. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float StepHeight = 45.f;

    // -------- Lean & Slope Handling --------

    /** How fast we can lean (deg per second). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lean")
    float LeanSpeedDegreesPerSecond = 120.f;

    /** Maximum lean angle (deg). */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lean")
    float LeanAngleDegrees = 12.f;

    /** Maximum walkable floor angle (deg) before sliding. */
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Physics")
    float WalkableFloorAngle = 44.f;
};