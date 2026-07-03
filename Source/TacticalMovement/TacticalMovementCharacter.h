// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Engine/DataTable.h"
#include "Logging/LogMacros.h"
#include "MovementProfileRow.h"               // <-- KEEPING THIS, AS YOU ALREADY ADDED IT
#include "TacticalMovementCharacter.generated.h" // <-- MUST BE LAST INCLUDE

class USpringArmComponent;
class UCameraComponent;
class UInputAction;
struct FInputActionValue;

DECLARE_LOG_CATEGORY_EXTERN(LogTemplateCharacter, Log, All);

UENUM(BlueprintType)
enum class ECombatReadinessState : uint8
{
	Sul UMETA(DisplayName = "Sul"),
	LowReady UMETA(DisplayName = "Low Ready"),
	MovementReady UMETA(DisplayName = "Movement Ready"),
	ADS UMETA(DisplayName = "ADS")
};
/**
 *  A simple player-controllable third person character
 *  Implements a controllable orbiting camera
 */
UCLASS(abstract)
class ATacticalMovementCharacter : public ACharacter
{
	GENERATED_BODY()

	/** Camera boom positioning the camera behind the character */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	USpringArmComponent* CameraBoom;

	/** Follow camera */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Components", meta = (AllowPrivateAccess = "true"))
	UCameraComponent* FollowCamera;
	
protected:

	/** Jump Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* JumpAction;

	/** Move Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* MoveAction;

	/** Look Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* LookAction;

	/** Mouse Look Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* MouseLookAction;

	/** Sprint Input Action */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* SprintAction;

	// --- Readiness / ADS input (Enhanced Input) ---

	/** Readiness: Sul (dev key 1) */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ReadinessSulAction;

	/** Readiness: Low Ready (dev key 2) */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ReadinessLowReadyAction;

	/** Readiness: Movement Ready (dev key 3) */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ReadinessMovementReadyAction;

	/** ADS input (primary: Right Mouse Button; dev key 4). Temporary discrete-press behavior for this slice — hold-to-ADS / release-to-previous is a later design decision. */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ADSAction;

	// ---------------- Movement Profile (DataTable-driven movement) ----------------

	/** DataTable holding all movement profiles */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement|Data")
	UDataTable* MovementProfileTable;

	/** Which row from the movement profile table to load (e.g. "Infantry_Default") */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement|Data")
	FName MovementProfileRowName = TEXT("Infantry_Default");

	// --- Sprint movement support --- // *** NEW ***

	/** Row to use when sprinting (set in Blueprint defaults) */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement|Data")
	FName SprintMovementProfileRowName; // e.g. "Infantry_Sprint"

	/** Cached "normal" movement row that we started with at BeginPlay */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Movement|Data")
	FName DefaultMovementProfileRowName;

	/** Current sprint state */
	UPROPERTY(VisibleInstanceOnly, BlueprintReadOnly, Category="Movement|State")
	bool bIsSprinting = false;

	/** Current combat readiness state */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category="Movement|State")
	ECombatReadinessState CombatReadinessState = ECombatReadinessState::MovementReady;

	/** Initialize input action bindings */
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	/** BeginPlay override to initialize movement profile from DataTable */
	virtual void BeginPlay() override;

	/** Internal function to read the DataTable row and apply movement settings */
	void ApplyMovementProfileFromDataTable();
		/** Updates current movement speed based on input direction using the active movement profile */
	void UpdateDirectionalMovementSpeed(float Right, float Forward);

		/** Applies movement orientation rules based on the current readiness state */
	void UpdateMovementOrientationBehavior();
		/** Central internal function for changing readiness state */
	void SetCombatReadinessState(ECombatReadinessState NewState);
		/** Returns a movement speed multiplier based on the current readiness state */
	float GetReadinessSpeedMultiplier() const;

		/** Returns whether the current readiness state allows strafing movement */
	bool DoesCurrentReadinessAllowStrafe() const;

	/** Returns whether the current readiness state allows hip fire */
	bool DoesCurrentReadinessAllowHipFire() const;

	/** Returns whether the current readiness state is combat-facing */
	bool IsCurrentReadinessCombatFacing() const;

		/** Returns whether the current readiness state allows sprinting */
	bool DoesCurrentReadinessAllowSprint() const;
		
	/** Returns a hip-fire responsiveness tier for the current readiness state */
	int32 GetCurrentHipFireResponsivenessTier() const;

		/** Returns an engagement readiness tier for the current readiness state */
	int32 GetCurrentReadinessEngagementTier() const;

	/** Called for movement input */
	void Move(const FInputActionValue& Value);

	/** Called for looking input */
	void Look(const FInputActionValue& Value);

		/** Central internal function that cancels active sprint and restores default movement */
	void CancelSprintInternal();

public:

	/** Constructor */
	ATacticalMovementCharacter();

	/** Handles move inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoMove(float Right, float Forward);

	/** Handles look inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoLook(float Yaw, float Pitch);

	/** Handles jump pressed inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpStart();

	/** Handles jump released inputs from either controls or UI interfaces */
	UFUNCTION(BlueprintCallable, Category="Input")
	virtual void DoJumpEnd();

	// Sprint API for Blueprints / input bindings // *** NEW ***

	/** Called when sprint input is pressed */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void StartSprinting();

	/** Called when sprint input is released */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void StopSprinting();

		/** Sets the character to Sul readiness state */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void SetReadinessSul();

	/** Sets the character to Low Ready readiness state */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void SetReadinessLowReady();

	/** Sets the character to Movement Ready readiness state */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void SetReadinessMovementReady();

	/** Sets the character to ADS readiness state */
	UFUNCTION(BlueprintCallable, Category="Movement|State")
	void SetReadinessADS();

	/** Returns CameraBoom subobject **/
	FORCEINLINE USpringArmComponent* GetCameraBoom() const { return CameraBoom; }

	/** Returns FollowCamera subobject **/
	FORCEINLINE UCameraComponent* GetFollowCamera() const { return FollowCamera; }
};