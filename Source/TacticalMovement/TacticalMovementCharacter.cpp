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
#include "TacticalMovement.h"

ATacticalMovementCharacter::ATacticalMovementCharacter()
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
void ATacticalMovementCharacter::BeginPlay()
{
	Super::BeginPlay();

	DefaultMovementProfileRowName = MovementProfileRowName;
	ApplyMovementProfileFromDataTable();
}

void ATacticalMovementCharacter::ApplyMovementProfileFromDataTable()
{
    if (!MovementProfileTable)
    {
        UE_LOG(LogTemp, Warning, TEXT("MovementProfileTable not assigned on %s"), *GetName());
        return;
    }

    FMovementProfileRow* Row = MovementProfileTable->FindRow<FMovementProfileRow>(MovementProfileRowName, TEXT(""));

    if (!Row)
    {
        UE_LOG(LogTemp, Warning, TEXT("MovementProfileRow '%s' not found in table"), *MovementProfileRowName.ToString());
        return;
    }

    // Apply the values from the DataTable row to the CharacterMovement component
    UCharacterMovementComponent* MoveComp = GetCharacterMovement();
    if (!MoveComp) return;

    MoveComp->MaxWalkSpeed            = Row->MaxWalkSpeedForward;
    MoveComp->MaxWalkSpeedCrouched    = Row->MaxWalkSpeedForward * Row->CrouchSpeedMultiplier;
    MoveComp->MaxAcceleration         = Row->MaxAcceleration;
    MoveComp->BrakingDecelerationWalking = Row->BrakingDeceleration;
    MoveComp->GroundFriction          = Row->GroundFriction;
    MoveComp->JumpZVelocity           = Row->JumpZVelocity;
    MoveComp->AirControl              = Row->AirControl;

    UE_LOG(LogTemp, Log, TEXT("Applied movement profile '%s'"), *MovementProfileRowName.ToString());
}

void ATacticalMovementCharacter::UpdateDirectionalMovementSpeed(float Right, float Forward)
{
	if (!MovementProfileTable)
	{
		return;
	}

	FMovementProfileRow* Row = MovementProfileTable->FindRow<FMovementProfileRow>(MovementProfileRowName, TEXT(""));

	if (!Row)
	{
		return;
	}

	UCharacterMovementComponent* MoveComp = GetCharacterMovement();
	if (!MoveComp)
	{
		return;
	}

	// Simple dominant-direction logic:
	// - Forward input > 0 uses forward speed
	// - Forward input < 0 uses backward speed
	// - No forward input but right/left input uses strafe speed
	if (Forward > 0.0f)
	{
		MoveComp->MaxWalkSpeed = Row->MaxWalkSpeedForward;
	}
	else if (Forward < 0.0f)
	{
		MoveComp->MaxWalkSpeed = Row->MaxWalkSpeedBack;
	}
	else if (FMath::Abs(Right) > 0.0f)
	{
		MoveComp->MaxWalkSpeed = Row->MaxWalkSpeedStrafe;
	}
}

void ATacticalMovementCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	// Set up action bindings
	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent)) {
		
				// Moving
		EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Move);

		// Looking
		EnhancedInputComponent->BindAction(MouseLookAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Look);
		EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &ATacticalMovementCharacter::Look);

		// Sprinting
		EnhancedInputComponent->BindAction(SprintAction, ETriggerEvent::Started, this, &ATacticalMovementCharacter::StartSprinting);
		EnhancedInputComponent->BindAction(SprintAction, ETriggerEvent::Completed, this, &ATacticalMovementCharacter::StopSprinting);
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
		UpdateDirectionalMovementSpeed(Right, Forward);
		
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

void ATacticalMovementCharacter::StartSprinting()
{
    if (bIsSprinting)
    {
        return;
    }

    // Must have a sprint row and a valid table
    if (!MovementProfileTable || SprintMovementProfileRowName.IsNone())
    {
        return;
    }

    bIsSprinting = true;

    // Switch to sprint row and re-apply profile
    MovementProfileRowName = SprintMovementProfileRowName;
    ApplyMovementProfileFromDataTable();
}

void ATacticalMovementCharacter::StopSprinting()
{
    if (!bIsSprinting)
    {
        return;
    }

    bIsSprinting = false;

    // Go back to the default (walk) row and re-apply
    if (!MovementProfileTable || DefaultMovementProfileRowName.IsNone())
    {
        return;
    }

    MovementProfileRowName = DefaultMovementProfileRowName;
    ApplyMovementProfileFromDataTable();
}