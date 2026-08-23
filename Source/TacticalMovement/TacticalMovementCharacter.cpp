// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalMovementCharacter.h"
#include "Engine/LocalPlayer.h"
#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "GameFramework/Controller.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "Net/UnrealNetwork.h"
#include "Movement/TacticalCharacterMovementComponent.h"
#include "TacticalMovement.h"
#include "Components/TimelineComponent.h"
#include "Weapons/TacticalWeaponADSConfig.h"

ATacticalMovementCharacter::ATacticalMovementCharacter(const FObjectInitializer& ObjectInitializer)
	: Super(ObjectInitializer.SetDefaultSubobjectClass<UTacticalCharacterMovementComponent>(ACharacter::CharacterMovementComponentName))
{
	// Set size for collision capsule
	GetCapsuleComponent()->InitCapsuleSize(42.f, 96.0f);

	// Don't rotate when the controller rotates. Let that just affect the camera.
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	// Configure character movement
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 500.0f, 0.0f);

	// Note: For faster iteration times these variables, and many more, can be tweaked in the Character Blueprint
	// instead of recompiling to adjust them
	GetCharacterMovement()->JumpZVelocity = 500.f;
	GetCharacterMovement()->AirControl = 0.35f;
	GetCharacterMovement()->MaxWalkSpeed = 500.f;
	GetCharacterMovement()->MinAnalogWalkSpeed = 20.f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2000.f;
	GetCharacterMovement()->BrakingDecelerationFalling = 1500.0f;

	// Create a camera boom (pulls in towards the player if there is a collision)
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 400.0f;
	CameraBoom->bUsePawnControlRotation = true;

	// Create a follow camera
	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	// Note: The skeletal mesh and anim blueprint references on the Mesh component (inherited from Character) 
	// are set in the derived blueprint asset named ThirdPersonCharacter (to avoid direct content references in C++)
}
void ATacticalMovementCharacter::GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const
{
	Super::GetLifetimeReplicatedProps(OutLifetimeProps);

	// The owning client predicts these via the CMC intent + move pipeline, so replicate the
	// mirror to simulated proxies only (never fight the owner's prediction).
	DOREPLIFETIME_CONDITION(ATacticalMovementCharacter, CombatReadinessState, COND_SimulatedOnly);
	DOREPLIFETIME_CONDITION(ATacticalMovementCharacter, bIsSprinting, COND_SimulatedOnly);
}

UTacticalCharacterMovementComponent* ATacticalMovementCharacter::GetTacticalMovementComponent() const
{
	return Cast<UTacticalCharacterMovementComponent>(GetCharacterMovement());
}

void ATacticalMovementCharacter::BeginPlay()
{
	Super::BeginPlay();

	DefaultMovementProfileRowName = MovementProfileRowName;

	// Cache the movement-profile rows once; the CMC resolves speed/jump/friction per move from them.
	if (UTacticalCharacterMovementComponent* TCMC = GetTacticalMovementComponent())
	{
		TCMC->CacheProfilesFromTable(MovementProfileTable, MovementProfileRowName, SprintMovementProfileRowName);
		// Seed CMC intent from the shipped default readiness (mirror already holds it).
		TCMC->SetIntentReadinessAndSprint(CombatReadinessState, bIsSprinting);
	}

	UpdateMovementOrientationBehavior();

	ApplyWeaponADSDuration();
}

float ATacticalMovementCharacter::GetADSDurationSeconds() const
{
	// No weapon config -> the project-wide accepted timing.
	if (WeaponADSConfig && WeaponADSConfig->ADSDurationSeconds > 0.f)
	{
		return WeaponADSConfig->ADSDurationSeconds;
	}
	return DefaultADSDurationSeconds;
}

void ATacticalMovementCharacter::ApplyWeaponADSDuration()
{
	// Resolve the BP-owned ADS FOV timeline once. Matching by name keeps this decoupled from the
	// Blueprint graph: no node, pin, or variable in BP_ThirdPersonCharacter is touched.
	if (!ADSFOVTimeline)
	{
		TArray<UTimelineComponent*> Timelines;
		GetComponents<UTimelineComponent>(Timelines);
		for (UTimelineComponent* Timeline : Timelines)
		{
			if (Timeline && Timeline->GetName().Contains(TEXT("TL_ADS_FOV")))
			{
				ADSFOVTimeline = Timeline;
				break;
			}
		}
	}

	if (!ADSFOVTimeline)
	{
		// Nothing to scale (e.g. a derived Blueprint without the FOV timeline). Not an error.
		return;
	}

	if (AuthoredADSTimelineLength <= 0.f)
	{
		AuthoredADSTimelineLength = ADSFOVTimeline->GetTimelineLength();
	}

	const float Desired = GetADSDurationSeconds();
	if (AuthoredADSTimelineLength <= 0.f || Desired <= 0.f)
	{
		return;
	}

	// Play rate scales duration while preserving the authored curve shape.
	// Desired == authored -> rate 1.0, i.e. exactly the accepted timing.
	const float NewRate = AuthoredADSTimelineLength / Desired;
	if (!FMath::IsNearlyEqual(ADSFOVTimeline->GetPlayRate(), NewRate, KINDA_SMALL_NUMBER))
	{
		ADSFOVTimeline->SetPlayRate(NewRate);
	}

	UE_LOG(LogTacticalMovement, Log,
		TEXT("[ADS] TL_ADS_FOV authored=%.4fs desired=%.4fs playRate=%.4f (config=%s)"),
		AuthoredADSTimelineLength, Desired, NewRate,
		WeaponADSConfig ? *WeaponADSConfig->GetName() : TEXT("<none, using default>"));
}

void ATacticalMovementCharacter::OnRep_CombatReadinessState()
{
	// Simulated proxy: readiness mirror changed -> refresh orientation presentation.
	UpdateMovementOrientationBehavior();
}

void ATacticalMovementCharacter::OnRep_IsSprinting()
{
	// Presentation hook for simulated proxies (future proxy anim). No movement authority here.
}

void ATacticalMovementCharacter::SyncReadinessMirror(ECombatReadinessState NewReadiness, bool bNewSprint)
{
	// Single writer of the presentation/API mirror. On the server this is the replicated source;
	// on the owning client it reflects the predicted state.
	CombatReadinessState = NewReadiness;
	bIsSprinting = bNewSprint;
	UpdateMovementOrientationBehavior();
}

// Movement speed / jump / friction are now resolved per-move by
// UTacticalCharacterMovementComponent (server-authoritative + client-predicted).
// The former ApplyMovementProfileFromDataTable() / UpdateDirectionalMovementSpeed()
// imperative writes have been removed.

void ATacticalMovementCharacter::UpdateMovementOrientationBehavior()
{
	UCharacterMovementComponent* MoveComp = GetCharacterMovement();
	if (!MoveComp)
	{
		return;
	}

	switch (CombatReadinessState)
	{
		case ECombatReadinessState::Sul:
			// Sul should remain movement-oriented for now
			bUseControllerRotationYaw = false;
			MoveComp->bOrientRotationToMovement = true;
			break;

		case ECombatReadinessState::LowReady:
		case ECombatReadinessState::MovementReady:
		case ECombatReadinessState::ADS:
			// These states should support combat-facing movement
			bUseControllerRotationYaw = true;
			MoveComp->bOrientRotationToMovement = false;
			break;

		default:
			break;
	}
}

bool ATacticalMovementCharacter::DoesCurrentReadinessAllowStrafe() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::Sul:
		case ECombatReadinessState::LowReady:
		case ECombatReadinessState::MovementReady:
		case ECombatReadinessState::ADS:
			return true;

		default:
			return false;
	}
}

bool ATacticalMovementCharacter::DoesCurrentReadinessAllowHipFire() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::Sul:
		case ECombatReadinessState::LowReady:
		case ECombatReadinessState::MovementReady:
		case ECombatReadinessState::ADS:
			return true;

		default:
			return false;
	}
}

bool ATacticalMovementCharacter::IsCurrentReadinessCombatFacing() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::LowReady:
		case ECombatReadinessState::MovementReady:
		case ECombatReadinessState::ADS:
			return true;

		case ECombatReadinessState::Sul:
		default:
			return false;
	}
}

int32 ATacticalMovementCharacter::GetCurrentReadinessEngagementTier() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::Sul:
			return 1;

		case ECombatReadinessState::LowReady:
			return 2;

		case ECombatReadinessState::MovementReady:
			return 3;

		case ECombatReadinessState::ADS:
			return 4;

		default:
			return 0;
	}
}

int32 ATacticalMovementCharacter::GetCurrentHipFireResponsivenessTier() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::Sul:
			return 1;

		case ECombatReadinessState::LowReady:
			return 2;

		case ECombatReadinessState::MovementReady:
			return 3;

		case ECombatReadinessState::ADS:
			return 4;

		default:
			return 0;
	}
}

bool ATacticalMovementCharacter::DoesCurrentReadinessAllowSprint() const
{
	switch (CombatReadinessState)
	{
		case ECombatReadinessState::ADS:
			return false;

		case ECombatReadinessState::Sul:
		case ECombatReadinessState::LowReady:
		case ECombatReadinessState::MovementReady:
			return true;

		default:
			return false;
	}
}

void ATacticalMovementCharacter::SetCombatReadinessState(ECombatReadinessState NewState)
{
	// Entering ADS cancels an active sprint (identity rule).
	bool bSprint = bIsSprinting;
	if (NewState == ECombatReadinessState::ADS)
	{
		bSprint = false;
	}

	// Authoritative movement-intent source = CMC intent.
	if (UTacticalCharacterMovementComponent* TCMC = GetTacticalMovementComponent())
	{
		TCMC->SetIntentReadinessAndSprint(NewState, bSprint);
	}

	// Synchronized presentation/API mirror (also the replicated source on the server).
	SyncReadinessMirror(NewState, bSprint);
}

void ATacticalMovementCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	// Set up action bindings
	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent)) {

		// Jumping
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::DoJumpStart);
		EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ATacticalMovementCharacter::DoJumpEnd);

				// Moving
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Move);

		// Looking
		EnhancedInputComponent->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Look);
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Look);

		// Sprinting
		EnhancedInputComponent->BindAction(SprintAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::StartSprinting);
		EnhancedInputComponent->BindAction(SprintAction, ETriggerEvent::Completed, this, &ATacticalMovementCharacter::StopSprinting);

		// Readiness / ADS (Enhanced Input -> existing readiness functions; input plumbing only, no rule/value changes)
		EnhancedInputComponent->BindAction(ReadinessSulAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::SetReadinessSul);
		EnhancedInputComponent->BindAction(ReadinessLowReadyAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::SetReadinessLowReady);
		EnhancedInputComponent->BindAction(ReadinessMovementReadyAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::SetReadinessMovementReady);

		// ADS (RMB): hold-to-ADS. Press enters ADS (capturing previous readiness); release restores it.
		EnhancedInputComponent->BindAction(ADSAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::EnterADSHold);
		EnhancedInputComponent->BindAction(ADSAction, ETriggerEvent::Completed, this, &ATacticalMovementCharacter::ExitADSHold);

		// Dev-only discrete ADS latch (dev key 4): enters ADS and stays (exit via readiness keys 1/2/3).
		EnhancedInputComponent->BindAction(ADSDevLatchAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::SetReadinessADS);
	}
	else
	{
		UE_LOG(LogTacticalMovement, Error, TEXT("'%s' Failed to find an Enhanced Input component! This template is built to use the Enhanced Input system. If you intend to use the legacy system, then you will need to update this C++ file."), *GetNameSafe(this));
	}
}

void ATacticalMovementCharacter::Move(const FInputActionValue& Value)
{
	// input is a Vector2D
	FVector2D MovementVector = Value.Get<FVector2D>();

	// route the input
	DoMove(MovementVector.X, MovementVector.Y);
}

void ATacticalMovementCharacter::Look(const FInputActionValue& Value)
{
	// input is a Vector2D
	FVector2D LookAxisVector = Value.Get<FVector2D>();

	// route the input
	DoLook(LookAxisVector.X, LookAxisVector.Y);
}

void ATacticalMovementCharacter::DoMove(float Right, float Forward)
{
	if (GetController() != nullptr)
	{
		// Directional speed is resolved per-move by the CMC (GetMaxSpeed) from the predicted
		// direction class; no imperative MaxWalkSpeed write here anymore.

		// find out which way is forward
		const FRotator Rotation = GetController()->GetControlRotation();
		const FRotator YawRotation(0, Rotation.Yaw, 0);

		// get forward vector
		const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);

		// get right vector 
		const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

		// add movement 
		AddMovementInput(ForwardDirection, Forward);
		AddMovementInput(RightDirection, Right);
	}
}

void ATacticalMovementCharacter::DoLook(float Yaw, float Pitch)
{
	if (GetController() != nullptr)
	{
		// add yaw and pitch input to controller
		AddControllerYawInput(Yaw);
		AddControllerPitchInput(Pitch);
	}
}

void ATacticalMovementCharacter::DoJumpStart()
{
	// signal the character to jump
	Jump();
}

void ATacticalMovementCharacter::DoJumpEnd()
{
	// signal the character to stop jumping
	StopJumping();
}

void ATacticalMovementCharacter::CancelSprintInternal()
{
	if (!bIsSprinting)
	{
		return;
	}

	// Clear sprint intent on the CMC + mirror; the CMC resolves the non-sprint profile per move.
	if (UTacticalCharacterMovementComponent* TCMC = GetTacticalMovementComponent())
	{
		TCMC->SetIntentReadinessAndSprint(CombatReadinessState, false);
	}
	SyncReadinessMirror(CombatReadinessState, false);
}

void ATacticalMovementCharacter::StartSprinting()
{
	if (bIsSprinting)
	{
		return;
	}

	if (!DoesCurrentReadinessAllowSprint())
	{
		return;
	}

	// Must have a sprint row and a valid table (same data gate as before).
	if (!MovementProfileTable || SprintMovementProfileRowName.IsNone())
	{
		return;
	}

	// Set sprint intent on the CMC + mirror; the CMC resolves the sprint profile per move.
	if (UTacticalCharacterMovementComponent* TCMC = GetTacticalMovementComponent())
	{
		TCMC->SetIntentReadinessAndSprint(CombatReadinessState, true);
	}
	SyncReadinessMirror(CombatReadinessState, true);
}

void ATacticalMovementCharacter::StopSprinting()
{
	CancelSprintInternal();
}

void ATacticalMovementCharacter::SetReadinessSul()
{
	SetCombatReadinessState(ECombatReadinessState::Sul);
}

void ATacticalMovementCharacter::SetReadinessLowReady()
{
	SetCombatReadinessState(ECombatReadinessState::LowReady);
}

void ATacticalMovementCharacter::SetReadinessMovementReady()
{
	SetCombatReadinessState(ECombatReadinessState::MovementReady);
}

void ATacticalMovementCharacter::SetReadinessADS()
{
	// SetCombatReadinessState(ADS) already applies the ADS-cancels-sprint rule.
	SetCombatReadinessState(ECombatReadinessState::ADS);
}

void ATacticalMovementCharacter::EnterADSHold()
{
	// Capture the readiness to return to on release, but only when coming from a
	// non-ADS state. This prevents a re-entrant press (e.g. already latched into ADS
	// via the dev key) from overwriting the stored previous readiness with ADS.
	if (CombatReadinessState != ECombatReadinessState::ADS)
	{
		PreviousReadinessBeforeADS = CombatReadinessState;
	}

	// Enter ADS via the existing discrete path (cancels any active sprint + sets ADS).
	SetReadinessADS();
}

void ATacticalMovementCharacter::ExitADSHold()
{
	// Only act if we are actually in ADS. If the player manually changed readiness
	// (keys 1/2/3) while still holding RMB, we are no longer in ADS and release must be
	// a no-op so it does not clobber that explicit choice.
	if (CombatReadinessState != ECombatReadinessState::ADS)
	{
		return;
	}

	// Restore the captured previous readiness. If it is invalid/unclear (somehow ADS),
	// fall back to Low Ready — the default firearm posture. Sprint is intentionally not
	// auto-resumed here (it was cancelled on ADS entry).
	ECombatReadinessState RestoreState = PreviousReadinessBeforeADS;
	if (RestoreState == ECombatReadinessState::ADS)
	{
		RestoreState = ECombatReadinessState::LowReady;
	}

	SetCombatReadinessState(RestoreState);
}