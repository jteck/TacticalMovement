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
class UTacticalCharacterMovementComponent;
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

	/** ADS input (primary: Right Mouse Button). Hold-to-ADS: press enters ADS, release restores the previous readiness. */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ADSAction;

	/** Dev-only discrete ADS latch (dev key 4). Calls the discrete SetReadinessADS() (enter-and-stay); exit via readiness keys 1/2/3. Kept separate from ADSAction so RMB can be true hold-to-ADS while key 4 remains a hold-independent test latch. */
	UPROPERTY(EditAnywhere, Category="Input")
	UInputAction* ADSDevLatchAction;

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

	/** Current sprint state — presentation/API mirror of the CMC sprint intent.
	 *  Replicated to simulated proxies only (the owning client predicts it locally). */
	UPROPERTY(ReplicatedUsing=OnRep_IsSprinting, VisibleInstanceOnly, BlueprintReadOnly, Category="Movement|State")
	bool bIsSprinting = false;

	/** Current combat readiness state (default: Low Ready — the practical default firearm posture).
	 *  Presentation/API mirror of the CMC readiness intent; NOT an independent movement source.
	 *  Replicated to simulated proxies only (the owning client predicts it locally). */
	UPROPERTY(ReplicatedUsing=OnRep_CombatReadinessState, EditDefaultsOnly, BlueprintReadOnly, Category="Movement|State")
	ECombatReadinessState CombatReadinessState = ECombatReadinessState::LowReady;

	/** OnRep for the readiness mirror on simulated proxies — refreshes orientation presentation. */
	UFUNCTION()
	void OnRep_CombatReadinessState();

	/** OnRep for the sprint mirror on simulated proxies (presentation hook). */
	UFUNCTION()
	void OnRep_IsSprinting();

	/** Readiness to restore when hold-to-ADS (RMB) is released. Captured only when entering ADS from a non-ADS state; seeded to Low Ready as the fallback. Transient runtime state — never serialized. */
	UPROPERTY(Transient)
	ECombatReadinessState PreviousReadinessBeforeADS = ECombatReadinessState::LowReady;

	/** Initialize input action bindings */
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	/** BeginPlay override to initialize movement profile from DataTable */
	virtual void BeginPlay() override;

		/** Applies movement orientation rules based on the current readiness state (reads the mirror). */
	void UpdateMovementOrientationBehavior();
		/** Central internal function for changing readiness state — routes to CMC intent + mirror. */
	void SetCombatReadinessState(ECombatReadinessState NewState);

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

	// --- Per-weapon ADS duration (D) ---------------------------------------------------------
	//
	// The accepted ADS presentation is the BP_ThirdPersonCharacter `TL_ADS_FOV` timeline plus a
	// fixed AnimBP pose blend. This applies a per-weapon duration to the FOV timeline as a PLAY
	// RATE, so the authored curve shape is preserved and only its duration scales. Nothing here
	// touches movement, readiness, replication, first-person rendering, or any asset.

	/** Scales `TL_ADS_FOV` to the configured duration. No-op when it already matches. */
	void ApplyWeaponADSDuration();

	/** The BP-owned ADS FOV timeline, resolved once at BeginPlay. Transient; never serialized. */
	UPROPERTY(Transient)
	TObjectPtr<class UTimelineComponent> ADSFOVTimeline;

	/** Authored length of `TL_ADS_FOV`, captured before any play-rate change is applied. */
	float AuthoredADSTimelineLength = 0.f;

public:

	/**
	 * Project-wide accepted ADS camera-FOV duration, in seconds.
	 *
	 * This is the default for every weapon and reproduces the currently accepted timing exactly.
	 * It is the fallback whenever no weapon config is assigned.
	 */
	// 0.36 s is the MEASURED authored length of the BP `TL_ADS_FOV` timeline. Keeping the default
	// equal to it makes the play rate exactly 1.0, i.e. the accepted timing byte-for-byte.
	// (The separate ~0.100 s AnimBP ADS pose blend is a different mechanism and is NOT touched.)
	static constexpr float DefaultADSDurationSeconds = 0.36f;

	/**
	 * Optional per-weapon ADS configuration. When unset, DefaultADSDurationSeconds is used and the
	 * ADS timeline runs exactly as authored.
	 */
	UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "Weapon|ADS")
	TObjectPtr<class UTacticalWeaponADSConfig> WeaponADSConfig;

	/** Effective ADS camera-FOV duration for the equipped weapon, in seconds. */
	UFUNCTION(BlueprintPure, Category = "Weapon|ADS")
	float GetADSDurationSeconds() const;


	/** Constructor — installs the custom UTacticalCharacterMovementComponent. */
	ATacticalMovementCharacter(const FObjectInitializer& ObjectInitializer);

	/** Replicated-property setup (readiness/sprint mirror -> simulated proxies only). */
	virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;

	/** Typed accessor for the custom movement component (may be null in early construction). */
	UTacticalCharacterMovementComponent* GetTacticalMovementComponent() const;

	/** Single writer of the readiness/sprint mirror. Updates the mirror fields + orientation.
	 *  Called by the Character setters (owner/authority/tests) and by the CMC (server accept / owner correction). */
	void SyncReadinessMirror(ECombatReadinessState NewReadiness, bool bNewSprint);

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

	/** Hold-to-ADS press handler (RMB down): captures the previous readiness (only when not already ADS), then enters ADS. Public for input binding + automation tests. */
	void EnterADSHold();

	/** Hold-to-ADS release handler (RMB up): if currently in ADS, restores the captured previous readiness (fallback Low Ready). No-op if not in ADS, so a manual readiness change while holding is not clobbered. Public for input binding + automation tests. */
	void ExitADSHold();

	/** Read-only accessor for the current combat readiness state (test/debug; does not change behavior) */
	FORCEINLINE ECombatReadinessState GetCombatReadinessState() const { return CombatReadinessState; }

	/** Read-only accessor for the current sprint state (test/debug; does not change behavior) */
	FORCEINLINE bool IsSprinting() const { return bIsSprinting; }

	/** Returns CameraBoom subobject **/
	FORCEINLINE USpringArmComponent* GetCameraBoom() const { return CameraBoom; }

	/** Returns FollowCamera subobject **/
	FORCEINLINE UCameraComponent* GetFollowCamera() const { return FollowCamera; }
};