// Copyright Epic Games, Inc. All Rights Reserved.
//
// Lightweight Simple Automation Tests guarding the C++ readiness / sprint / ADS
// rule layer and the shipped BP_ThirdPersonCharacter defaults.
//
// Scope (see docs 10 Decision Log): rule-layer only. These tests call the public
// C++ functions directly (the same ones the Enhanced Input bindings call), so they
// verify the RULES, not the input wiring. Enhanced Input key routing (1/2/3/4/RMB),
// full jump physics / MOVE_Falling, and ADS camera/feel remain MANUAL for now.

#include "CoreMinimal.h"

#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/Package.h"
#include "TacticalMovementCharacter.h"

namespace TacticalMovementTests
{
	// Object path of the shipped playable pawn's generated class. Using the real
	// Blueprint (not a synthetic C++ stub) so these tests guard the actual shipped
	// class defaults and DataTable-driven movement configuration.
	static const TCHAR* BPCharacterClassPath =
		TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C");

	// Loads the BP_ThirdPersonCharacter generated class. Returns nullptr on failure
	// (test reports a clear error).
	static UClass* LoadBPCharacterClass(FAutomationTestBase& Test)
	{
		UClass* BPClass = StaticLoadClass(ATacticalMovementCharacter::StaticClass(), nullptr, BPCharacterClassPath);
		if (!BPClass)
		{
			Test.AddError(FString::Printf(TEXT("Could not load BP class at '%s'"), BPCharacterClassPath));
		}
		return BPClass;
	}

	// Creates a transient instance of the BP character for rule-layer testing.
	// NewObject (not SpawnActor) is sufficient: the readiness/sprint methods only
	// touch member state, the (default-subobject) CharacterMovementComponent, and the
	// CDO-inherited MovementProfileTable — none require world registration or BeginPlay.
	static ATacticalMovementCharacter* MakeCharacter(FAutomationTestBase& Test)
	{
		UClass* BPClass = LoadBPCharacterClass(Test);
		if (!BPClass)
		{
			return nullptr;
		}

		ATacticalMovementCharacter* Character =
			NewObject<ATacticalMovementCharacter>(GetTransientPackage(), BPClass);
		if (!Character)
		{
			Test.AddError(TEXT("NewObject<ATacticalMovementCharacter>() returned null"));
		}
		return Character;
	}

	// Helper for readable enum comparisons in test output.
	static int32 AsInt(ECombatReadinessState State) { return static_cast<int32>(State); }
}

// ---------------------------------------------------------------------------
// 1. Shipped BP default readiness == LowReady (guards the merged Phase H baseline).
//    Reads the class-default object directly; no spawn / world needed.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessBPDefaultIsLowReadyTest,
	"TacticalMovement.Readiness.BPDefaultIsLowReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessBPDefaultIsLowReadyTest::RunTest(const FString& Parameters)
{
	UClass* BPClass = TacticalMovementTests::LoadBPCharacterClass(*this);
	if (!BPClass)
	{
		return false;
	}

	const ATacticalMovementCharacter* CDO = BPClass->GetDefaultObject<ATacticalMovementCharacter>();
	if (!CDO)
	{
		AddError(TEXT("BP class had no class-default object"));
		return false;
	}

	TestEqual(
		TEXT("BP_ThirdPersonCharacter default combat readiness should be LowReady"),
		TacticalMovementTests::AsInt(CDO->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::LowReady));

	return true;
}

// ---------------------------------------------------------------------------
// 2. Each readiness setter produces the expected state.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessSettersProduceExpectedStatesTest,
	"TacticalMovement.Readiness.SettersProduceExpectedStates",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessSettersProduceExpectedStatesTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessSul();
	TestEqual(TEXT("SetReadinessSul() -> Sul"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::Sul));

	Character->SetReadinessLowReady();
	TestEqual(TEXT("SetReadinessLowReady() -> LowReady"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::LowReady));

	Character->SetReadinessMovementReady();
	TestEqual(TEXT("SetReadinessMovementReady() -> MovementReady"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::MovementReady));

	Character->SetReadinessADS();
	TestEqual(TEXT("SetReadinessADS() -> ADS"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::ADS));

	return true;
}

// ---------------------------------------------------------------------------
// 3. ADS blocks a sprint from starting.
//    (StartSprinting() returns at the DoesCurrentReadinessAllowSprint() gate,
//     so this holds even without a DataTable.)
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessADSBlocksSprintTest,
	"TacticalMovement.Readiness.ADSBlocksSprint",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessADSBlocksSprintTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessADS();
	Character->StartSprinting();

	TestFalse(TEXT("StartSprinting() while in ADS should not start a sprint"),
		Character->IsSprinting());

	return true;
}

// ---------------------------------------------------------------------------
// 4. Entering ADS cancels an active sprint.
//    Precondition: sprint must actually start, which relies on the BP's
//    MovementProfileTable + SprintMovementProfileRowName. If the precondition
//    fails the test reports it clearly rather than silently passing.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessADSCancelsActiveSprintTest,
	"TacticalMovement.Readiness.ADSCancelsActiveSprint",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessADSCancelsActiveSprintTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	// A readiness state that allows sprint.
	Character->SetReadinessMovementReady();
	Character->StartSprinting();

	if (!Character->IsSprinting())
	{
		AddError(TEXT("Precondition failed: could not start a sprint from MovementReady. ")
			TEXT("Check BP_ThirdPersonCharacter has MovementProfileTable + SprintMovementProfileRowName set."));
		return false;
	}

	Character->SetReadinessADS();

	TestFalse(TEXT("Entering ADS should cancel the active sprint"), Character->IsSprinting());
	TestEqual(TEXT("State after entering ADS should be ADS"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::ADS));

	return true;
}

#endif // WITH_AUTOMATION_TESTS
