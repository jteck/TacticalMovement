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

// ===========================================================================
// Hold-to-ADS rule-layer tests.
//
// These call EnterADSHold() / ExitADSHold() directly (the same handlers the
// IA_ADS Started/Completed bindings call), verifying the RULES of hold-to-ADS,
// not the input wiring. Actual RMB press/release routing stays MANUAL (Slate /
// MCP cannot hold a key).
// ===========================================================================

// ---------------------------------------------------------------------------
// 5. Holding ADS (RMB down) enters ADS.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSEntersADSTest,
	"TacticalMovement.Readiness.HoldADSEntersADS",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSEntersADSTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessLowReady();
	Character->EnterADSHold();

	TestEqual(TEXT("EnterADSHold() should put the character in ADS"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::ADS));

	return true;
}

// ---------------------------------------------------------------------------
// 6. Releasing ADS restores the previous readiness — Low Ready.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSReleaseRestoresLowReadyTest,
	"TacticalMovement.Readiness.HoldADSReleaseRestoresLowReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSReleaseRestoresLowReadyTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessLowReady();
	Character->EnterADSHold();
	Character->ExitADSHold();

	TestEqual(TEXT("Release from ADS (entered from Low Ready) should restore Low Ready"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::LowReady));

	return true;
}

// ---------------------------------------------------------------------------
// 7. Releasing ADS restores the previous readiness — Movement Ready.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSReleaseRestoresMovementReadyTest,
	"TacticalMovement.Readiness.HoldADSReleaseRestoresMovementReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSReleaseRestoresMovementReadyTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessMovementReady();
	Character->EnterADSHold();
	Character->ExitADSHold();

	TestEqual(TEXT("Release from ADS (entered from Movement Ready) should restore Movement Ready"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::MovementReady));

	return true;
}

// ---------------------------------------------------------------------------
// 8. Releasing ADS restores the previous readiness — Sul.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSReleaseRestoresSulTest,
	"TacticalMovement.Readiness.HoldADSReleaseRestoresSul",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSReleaseRestoresSulTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessSul();
	Character->EnterADSHold();
	Character->ExitADSHold();

	TestEqual(TEXT("Release from ADS (entered from Sul) should restore Sul"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::Sul));

	return true;
}

// ---------------------------------------------------------------------------
// 9. Fallback: if the previous readiness is invalid/unclear (already ADS when the
//    hold began, so nothing valid was captured), release resolves to Low Ready.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSFallbackReturnsLowReadyTest,
	"TacticalMovement.Readiness.HoldADSFallbackReturnsLowReady",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSFallbackReturnsLowReadyTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	// Latch into ADS discretely (dev-key path), so the character is already ADS when
	// the hold begins. EnterADSHold() must NOT capture ADS as the "previous" state.
	Character->SetReadinessADS();
	Character->EnterADSHold();
	Character->ExitADSHold();

	TestEqual(TEXT("Release with no valid captured previous readiness should fall back to Low Ready"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::LowReady));

	return true;
}

// ---------------------------------------------------------------------------
// 10. Releasing ADS while not in ADS is a no-op (does not clobber a manual choice).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSExitWhenNotInADSIsNoOpTest,
	"TacticalMovement.Readiness.HoldADSExitWhenNotInADSIsNoOp",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSExitWhenNotInADSIsNoOpTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	// Simulate: entered ADS then the player pressed a readiness key (3) while still
	// holding RMB. The subsequent RMB release must not override that explicit choice.
	Character->SetReadinessMovementReady();
	Character->ExitADSHold();

	TestEqual(TEXT("ExitADSHold() while not in ADS should leave readiness unchanged (Movement Ready)"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::MovementReady));

	return true;
}

// ---------------------------------------------------------------------------
// 11. Holding ADS cancels an active sprint (via the hold enter-path).
//     Precondition: sprint must start (needs BP MovementProfileTable + sprint row).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSCancelsActiveSprintTest,
	"TacticalMovement.Readiness.HoldADSCancelsActiveSprint",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSCancelsActiveSprintTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessMovementReady();
	Character->StartSprinting();

	if (!Character->IsSprinting())
	{
		AddError(TEXT("Precondition failed: could not start a sprint from MovementReady. ")
			TEXT("Check BP_ThirdPersonCharacter has MovementProfileTable + SprintMovementProfileRowName set."));
		return false;
	}

	Character->EnterADSHold();

	TestFalse(TEXT("EnterADSHold() should cancel the active sprint"), Character->IsSprinting());
	TestEqual(TEXT("State after EnterADSHold() should be ADS"),
		TacticalMovementTests::AsInt(Character->GetCombatReadinessState()),
		TacticalMovementTests::AsInt(ECombatReadinessState::ADS));

	return true;
}

// ---------------------------------------------------------------------------
// 12. Holding ADS blocks a sprint from starting (via the hold enter-path).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FReadinessHoldADSBlocksSprintTest,
	"TacticalMovement.Readiness.HoldADSBlocksSprint",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FReadinessHoldADSBlocksSprintTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementTests::MakeCharacter(*this);
	if (!Character)
	{
		return false;
	}

	Character->SetReadinessLowReady();
	Character->EnterADSHold();
	Character->StartSprinting();

	TestFalse(TEXT("StartSprinting() while holding ADS should not start a sprint"),
		Character->IsSprinting());

	return true;
}

#endif // WITH_AUTOMATION_TESTS
