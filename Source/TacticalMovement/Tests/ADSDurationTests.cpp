// Copyright Epic Games, Inc. All Rights Reserved.
//
// Automation tests for the per-weapon ADS CAMERA-FOV duration (D).
//
// Scope: camera-FOV timeline scaling only. These tests deliberately do not assert anything about
// the AnimBP ADS pose blend, weapon weight, fatigue or injury - none of which this feature models.

#include "CoreMinimal.h"

#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "Components/TimelineComponent.h"
#include "Engine/World.h"
#include "TacticalMovementCharacter.h"
#include "Weapons/TacticalWeaponADSConfig.h"

namespace TacticalADSTests
{
	static const TCHAR* BPCharacterClassPath =
		TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C");
	static const TCHAR* RifleConfigPath =
		TEXT("/Game/Weapons/Rifle/DA_Rifle_ADS.DA_Rifle_ADS");

	/** The accepted authored length of the BP `TL_ADS_FOV` timeline, in seconds. */
	static constexpr float AcceptedAuthoredLength = 0.36f;

	struct FScopedCharacter
	{
		UWorld* World = nullptr;
		ATacticalMovementCharacter* Character = nullptr;

		explicit FScopedCharacter(FAutomationTestBase& Test)
		{
			UClass* BPClass = StaticLoadClass(ATacticalMovementCharacter::StaticClass(), nullptr, BPCharacterClassPath);
			if (!BPClass)
			{
				Test.AddError(FString::Printf(TEXT("Could not load BP class '%s'"), BPCharacterClassPath));
				return;
			}

			// A real world + BeginPlay is required: Blueprint timeline components are created during
			// actor initialisation, not as CDO subobjects.
			World = UWorld::CreateWorld(EWorldType::Game, false);
			if (!World)
			{
				Test.AddError(TEXT("UWorld::CreateWorld returned null"));
				return;
			}
			FWorldContext& Context = GEngine->CreateNewWorldContext(EWorldType::Game);
			Context.SetCurrentWorld(World);
			World->InitializeActorsForPlay(FURL());
			World->BeginPlay();

			Character = World->SpawnActor<ATacticalMovementCharacter>(BPClass, FTransform::Identity);
			if (!Character)
			{
				Test.AddError(TEXT("SpawnActor<ATacticalMovementCharacter>() returned null"));
				return;
			}

			// A bare automation world does not reliably dispatch BeginPlay, so drive the public
			// application funnel directly. It is idempotent, and it is the same function BeginPlay
			// calls. (BeginPlay application itself is evidenced separately by the Standalone log.)
			if (!Character->HasActorBegunPlay())
			{
				Character->DispatchBeginPlay();
			}
			Character->ApplyWeaponADSDuration();

			if (!Character->GetADSFOVTimeline())
			{
				TArray<UActorComponent*> All;
				Character->GetComponents(All);
				FString Names;
				for (const UActorComponent* C : All)
				{
					Names += FString::Printf(TEXT("%s(%s) "), *C->GetName(), *C->GetClass()->GetName());
				}
				Test.AddInfo(FString::Printf(TEXT("Components on spawned pawn: %s"), *Names));
			}
		}

		~FScopedCharacter()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}

		const UTimelineComponent* Timeline() const
		{
			return Character ? Character->GetADSFOVTimeline() : nullptr;
		}
	};

	static UTacticalWeaponADSConfig* MakeConfig(float Seconds)
	{
		UTacticalWeaponADSConfig* Config = NewObject<UTacticalWeaponADSConfig>(GetTransientPackage());
		Config->ADSCameraFOVDurationSeconds = Seconds;
		return Config;
	}
}

// The shipped rifle config must carry the accepted 0.360 s FOV duration, so production behaviour
// is unchanged by this feature existing.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FADSRifleConfigMatchesAcceptedTiming,
	"TacticalMovement.ADS.RifleConfigMatchesAcceptedTiming",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FADSRifleConfigMatchesAcceptedTiming::RunTest(const FString&)
{
	UTacticalWeaponADSConfig* Rifle = LoadObject<UTacticalWeaponADSConfig>(nullptr, TacticalADSTests::RifleConfigPath);
	if (!Rifle)
	{
		AddError(FString::Printf(TEXT("Could not load rifle ADS config '%s'"), TacticalADSTests::RifleConfigPath));
		return false;
	}
	TestEqual(TEXT("Rifle ADS camera-FOV duration"), Rifle->ADSCameraFOVDurationSeconds,
		TacticalADSTests::AcceptedAuthoredLength, KINDA_SMALL_NUMBER);
	return true;
}

// The production pawn ships bound to the rifle config, and that binding reproduces the accepted
// timing exactly (play rate 1.0).
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FADSProductionBindingPreservesAcceptedTiming,
	"TacticalMovement.ADS.ProductionBindingPreservesAcceptedTiming",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FADSProductionBindingPreservesAcceptedTiming::RunTest(const FString&)
{
	TacticalADSTests::FScopedCharacter Scoped(*this);
	if (!Scoped.Character) { return false; }

	if (!TestNotNull(TEXT("ADS FOV timeline resolved"), Scoped.Timeline())) { return false; }

	TestNotNull(TEXT("Production pawn ships with a weapon ADS config"), ToRawPtr(Scoped.Character->WeaponADSConfig));
	TestEqual(TEXT("Effective duration is the accepted authored length"),
		Scoped.Character->GetADSCameraFOVDurationSeconds(),
		TacticalADSTests::AcceptedAuthoredLength, KINDA_SMALL_NUMBER);
	TestEqual(TEXT("Play rate is 1.0 - accepted timing unchanged"),
		Scoped.Timeline()->GetPlayRate(), 1.0f, KINDA_SMALL_NUMBER);
	return true;
}

// A null config must be a true no-op: the authored duration and play rate 1.0 survive.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FADSNullConfigIsNoOp,
	"TacticalMovement.ADS.NullConfigIsNoOp",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FADSNullConfigIsNoOp::RunTest(const FString&)
{
	TacticalADSTests::FScopedCharacter Scoped(*this);
	if (!Scoped.Character) { return false; }
	if (!TestNotNull(TEXT("ADS FOV timeline resolved"), Scoped.Timeline())) { return false; }

	Scoped.Character->SetWeaponADSConfig(nullptr);

	TestEqual(TEXT("Null config falls back to the AUTHORED length, not a hard-coded value"),
		Scoped.Character->GetADSCameraFOVDurationSeconds(),
		TacticalADSTests::AcceptedAuthoredLength, KINDA_SMALL_NUMBER);
	TestEqual(TEXT("Null config leaves play rate at 1.0"),
		Scoped.Timeline()->GetPlayRate(), 1.0f, KINDA_SMALL_NUMBER);
	return true;
}

// The authoritative setter must change the duration immediately, with no respawn, and must be
// reversible on the same instance.
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FADSSetterReappliesWithoutRespawn,
	"TacticalMovement.ADS.SetterReappliesWithoutRespawn",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FADSSetterReappliesWithoutRespawn::RunTest(const FString&)
{
	TacticalADSTests::FScopedCharacter Scoped(*this);
	if (!Scoped.Character) { return false; }
	if (!TestNotNull(TEXT("ADS FOV timeline resolved"), Scoped.Timeline())) { return false; }

	// Twice the authored duration -> half the play rate.
	Scoped.Character->SetWeaponADSConfig(TacticalADSTests::MakeConfig(TacticalADSTests::AcceptedAuthoredLength * 2.f));
	TestEqual(TEXT("Slower weapon halves the play rate"),
		Scoped.Timeline()->GetPlayRate(), 0.5f, KINDA_SMALL_NUMBER);

	// Half the authored duration -> double the play rate, on the SAME instance.
	Scoped.Character->SetWeaponADSConfig(TacticalADSTests::MakeConfig(TacticalADSTests::AcceptedAuthoredLength * 0.5f));
	TestEqual(TEXT("Faster weapon doubles the play rate, no respawn"),
		Scoped.Timeline()->GetPlayRate(), 2.0f, KINDA_SMALL_NUMBER);

	// Back to null -> authored duration restored.
	Scoped.Character->SetWeaponADSConfig(nullptr);
	TestEqual(TEXT("Unequipping restores the authored play rate"),
		Scoped.Timeline()->GetPlayRate(), 1.0f, KINDA_SMALL_NUMBER);
	return true;
}

#endif // WITH_AUTOMATION_TESTS
