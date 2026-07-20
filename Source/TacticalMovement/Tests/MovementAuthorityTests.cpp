// Copyright Epic Games, Inc. All Rights Reserved.
//
// Automation tests for the movement-authority foundation (UTacticalCharacterMovementComponent).
//
// Scope: the deterministic, headless-testable pieces of the design —
//   - the character installs the custom CMC;
//   - the readiness/sprint mirror stays synchronized with CMC intent (local prediction);
//   - ADS cancels sprint through CMC intent;
//   - replay-intent restore round-trips;
//   - control-relative direction classification (the server derives authoritative direction
//     from acceleration+control rotation the same way — a lateral vector must classify Strafe,
//     never Forward);
//   - saved-move reliability short-circuits (CanCombineWith / IsImportantMove) on state change.
//
// Full networked prediction/authority behaviors (per-move transport, forced correction on clamp,
// two-client agreement) are exercised by the CP6 two-client acceptance matrix, not here.

#include "CoreMinimal.h"

#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "UObject/UObjectGlobals.h"
#include "UObject/Package.h"
#include "Engine/DataTable.h"
#include "Components/CapsuleComponent.h"
#include "TacticalMovementCharacter.h"
#include "Movement/TacticalCharacterMovementComponent.h"

namespace TacticalMovementAuthorityTests
{
	static const TCHAR* BPCharacterClassPath =
		TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C");

	static ATacticalMovementCharacter* MakeCharacter(FAutomationTestBase& Test)
	{
		UClass* BPClass = StaticLoadClass(ATacticalMovementCharacter::StaticClass(), nullptr, BPCharacterClassPath);
		if (!BPClass)
		{
			Test.AddError(FString::Printf(TEXT("Could not load BP class at '%s'"), BPCharacterClassPath));
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

	static int32 AsInt(ECombatReadinessState S) { return (int32)S; }
	static int32 AsInt(ETacticalMoveDir D) { return (int32)D; }

	static const TCHAR* MovementProfileTablePath =
		TEXT("/Game/Data/DT_MovementProfiles.DT_MovementProfiles");

	static UDataTable* LoadProfiles(FAutomationTestBase& Test)
	{
		UDataTable* DT = LoadObject<UDataTable>(nullptr, MovementProfileTablePath);
		if (!DT)
		{
			Test.AddError(FString::Printf(TEXT("Could not load DataTable at '%s'"), MovementProfileTablePath));
		}
		return DT;
	}

	// Establish the CMC's CharacterOwner/UpdatedComponent link (as component registration would),
	// so GetMaxSpeed()'s IsCrouching() reflects the character's crouch state.
	static void WireOwner(ATacticalMovementCharacter* Character, UTacticalCharacterMovementComponent* TCMC)
	{
		TCMC->SetUpdatedComponent(Character->GetCapsuleComponent());
	}
}

// ---------------------------------------------------------------------------
// 1. The character installs the custom movement component.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityUsesCustomCMCTest,
	"TacticalMovement.MovementAuthority.UsesCustomCMC",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityUsesCustomCMCTest::RunTest(const FString& Parameters)
{
	ATacticalMovementCharacter* Character = TacticalMovementAuthorityTests::MakeCharacter(*this);
	if (!Character) { return false; }

	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	TestNotNull(TEXT("Character's CharacterMovement should be a UTacticalCharacterMovementComponent"), TCMC);
	return true;
}

// ---------------------------------------------------------------------------
// 2. Local predicted Character readiness mirror stays synchronized with CMC intent.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityReadinessMirrorSyncTest,
	"TacticalMovement.MovementAuthority.ReadinessMirrorSyncsWithIntent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityReadinessMirrorSyncTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }

	const ECombatReadinessState States[] = {
		ECombatReadinessState::Sul, ECombatReadinessState::LowReady,
		ECombatReadinessState::MovementReady, ECombatReadinessState::ADS };

	Character->SetReadinessSul();
	TestEqual(TEXT("Mirror == Sul"), AsInt(Character->GetCombatReadinessState()), AsInt(ECombatReadinessState::Sul));
	TestEqual(TEXT("Intent == Sul"), AsInt(TCMC->GetReadinessIntent()), AsInt(ECombatReadinessState::Sul));

	Character->SetReadinessMovementReady();
	TestEqual(TEXT("Mirror == MovementReady"), AsInt(Character->GetCombatReadinessState()), AsInt(ECombatReadinessState::MovementReady));
	TestEqual(TEXT("Intent == MovementReady"), AsInt(TCMC->GetReadinessIntent()), AsInt(ECombatReadinessState::MovementReady));

	Character->SetReadinessADS();
	TestEqual(TEXT("Mirror == ADS"), AsInt(Character->GetCombatReadinessState()), AsInt(ECombatReadinessState::ADS));
	TestEqual(TEXT("Intent == ADS"), AsInt(TCMC->GetReadinessIntent()), AsInt(ECombatReadinessState::ADS));

	return true;
}

// ---------------------------------------------------------------------------
// 3. Sprint intent + mirror sync (start / stop).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthoritySprintSyncTest,
	"TacticalMovement.MovementAuthority.SprintIntentSyncsWithMirror",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthoritySprintSyncTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }

	Character->SetReadinessMovementReady();
	Character->StartSprinting();
	if (!Character->IsSprinting())
	{
		AddError(TEXT("Precondition failed: could not start sprint (check BP MovementProfileTable + SprintMovementProfileRowName)."));
		return false;
	}
	TestTrue(TEXT("CMC sprint intent true after StartSprinting"), TCMC->GetSprintIntent());

	Character->StopSprinting();
	TestFalse(TEXT("Mirror sprint false after StopSprinting"), Character->IsSprinting());
	TestFalse(TEXT("CMC sprint intent false after StopSprinting"), TCMC->GetSprintIntent());
	return true;
}

// ---------------------------------------------------------------------------
// 4. ADS cancels sprint through CMC intent (mirror + intent both clear).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityADSCancelsSprintIntentTest,
	"TacticalMovement.MovementAuthority.ADSCancelsSprintIntent",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityADSCancelsSprintIntentTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }

	Character->SetReadinessMovementReady();
	Character->StartSprinting();
	if (!Character->IsSprinting())
	{
		AddError(TEXT("Precondition failed: could not start sprint."));
		return false;
	}

	Character->SetReadinessADS();
	TestFalse(TEXT("Mirror sprint cleared by ADS"), Character->IsSprinting());
	TestFalse(TEXT("CMC sprint intent cleared by ADS"), TCMC->GetSprintIntent());
	TestEqual(TEXT("Intent readiness == ADS"), AsInt(TCMC->GetReadinessIntent()), AsInt(ECombatReadinessState::ADS));
	return true;
}

// ---------------------------------------------------------------------------
// 5. Replay intent restore round-trips (PrepMoveFor path exercised via RestoreIntentForReplay).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityReplayIntentRestoreTest,
	"TacticalMovement.MovementAuthority.ReplayIntentRestore",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityReplayIntentRestoreTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }

	// Seed a different live intent, then restore a historical move's intent.
	TCMC->SetIntentReadinessAndSprint(ECombatReadinessState::Sul, false);
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, true, ETacticalMoveDir::Strafe);

	TestEqual(TEXT("Restored readiness"), AsInt(TCMC->GetReadinessIntent()), AsInt(ECombatReadinessState::MovementReady));
	TestTrue(TEXT("Restored sprint"), TCMC->GetSprintIntent());
	TestEqual(TEXT("Restored dir class"), AsInt(TCMC->GetIntentDirClass()), AsInt(ETacticalMoveDir::Strafe));
	return true;
}

// ---------------------------------------------------------------------------
// 6. Server-authoritative direction classification: a lateral vector classifies Strafe
//    (never Forward), so a client claiming Forward while accelerating laterally is corrected.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityDirectionClassificationTest,
	"TacticalMovement.MovementAuthority.DirectionClassification",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityDirectionClassificationTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }

	// Control rotation facing +X (yaw 0): forward = +X, right = +Y.
	const FRotator Control(0.f, 0.f, 0.f);
	const ETacticalMoveDir Fallback = ETacticalMoveDir::Forward;

	// Pure lateral acceleration (+Y) -> Strafe, NOT Forward.
	TestEqual(TEXT("Lateral (+Y) -> Strafe"),
		AsInt(TCMC->ClassifyDir(FVector(0.f, 100.f, 0.f), Control, Fallback)), AsInt(ETacticalMoveDir::Strafe));
	// Forward (+X) -> Forward.
	TestEqual(TEXT("Forward (+X) -> Forward"),
		AsInt(TCMC->ClassifyDir(FVector(100.f, 0.f, 0.f), Control, Fallback)), AsInt(ETacticalMoveDir::Forward));
	// Backward (-X) -> Back.
	TestEqual(TEXT("Back (-X) -> Back"),
		AsInt(TCMC->ClassifyDir(FVector(-100.f, 0.f, 0.f), Control, Fallback)), AsInt(ETacticalMoveDir::Back));
	// Diagonal forward-right -> Forward (any forward component wins).
	TestEqual(TEXT("Diagonal fwd-right -> Forward"),
		AsInt(TCMC->ClassifyDir(FVector(100.f, 100.f, 0.f), Control, Fallback)), AsInt(ETacticalMoveDir::Forward));
	// Zero input -> fallback (retain last non-zero).
	TestEqual(TEXT("Zero -> fallback"),
		AsInt(TCMC->ClassifyDir(FVector::ZeroVector, Control, ETacticalMoveDir::Back)), AsInt(ETacticalMoveDir::Back));
	return true;
}

// ---------------------------------------------------------------------------
// 7. Saved-move reliability short-circuits: differing custom state must not combine,
//    and must be flagged important.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthoritySavedMoveTransitionTest,
	"TacticalMovement.MovementAuthority.SavedMoveTransitionNotCombinedAndImportant",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthoritySavedMoveTransitionTest::RunTest(const FString& Parameters)
{
	// Two moves whose readiness differs must not combine and must be important.
	TSharedRef<FSavedMove_Tactical> A = MakeShared<FSavedMove_Tactical>();
	TSharedRef<FSavedMove_Tactical> B = MakeShared<FSavedMove_Tactical>();
	A->SavedReadiness = (uint8)ECombatReadinessState::LowReady;
	B->SavedReadiness = (uint8)ECombatReadinessState::ADS;

	FSavedMovePtr BPtr = B;
	TestFalse(TEXT("Differing readiness -> cannot combine"),
		A->CanCombineWith(BPtr, nullptr, 1.0f));
	TestTrue(TEXT("Differing readiness -> important move"),
		B->IsImportantMove(A));

	// Differing direction alone is also a transition.
	TSharedRef<FSavedMove_Tactical> C = MakeShared<FSavedMove_Tactical>();
	TSharedRef<FSavedMove_Tactical> D = MakeShared<FSavedMove_Tactical>();
	C->SavedDirClass = (uint8)ETacticalMoveDir::Forward;
	D->SavedDirClass = (uint8)ETacticalMoveDir::Strafe;
	FSavedMovePtr DPtr = D;
	TestFalse(TEXT("Differing direction -> cannot combine"),
		C->CanCombineWith(DPtr, nullptr, 1.0f));
	TestTrue(TEXT("Differing direction -> important move"),
		D->IsImportantMove(C));
	return true;
}

// ---------------------------------------------------------------------------
// 8. Mirror writer (models the server-accept -> proxy-mirror update at unit level).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityMirrorWriterTest,
	"TacticalMovement.MovementAuthority.SyncReadinessMirrorWrites",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityMirrorWriterTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }

	Character->SyncReadinessMirror(ECombatReadinessState::ADS, false);
	TestEqual(TEXT("Mirror readiness updated"),
		AsInt(Character->GetCombatReadinessState()), AsInt(ECombatReadinessState::ADS));

	Character->SyncReadinessMirror(ECombatReadinessState::Sul, true);
	TestEqual(TEXT("Mirror readiness updated to Sul"),
		AsInt(Character->GetCombatReadinessState()), AsInt(ECombatReadinessState::Sul));
	TestTrue(TEXT("Mirror sprint updated"), Character->IsSprinting());
	return true;
}

// ---------------------------------------------------------------------------
// 9. Walking directional + readiness speed: GetMaxSpeed() differentiates
//    Forward/Strafe and scales down for LowReady/ADS vs MovementReady.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityWalkSpeedTest,
	"TacticalMovement.MovementAuthority.WalkDirectionalReadinessSpeed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityWalkSpeedTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }
	UDataTable* DT = LoadProfiles(*this);
	if (!DT) { return false; }

	WireOwner(Character, TCMC);
	TCMC->CacheProfilesFromTable(DT, FName("Infantry_Default"), NAME_None);
	if (!TCMC->AreProfilesCached()) { AddError(TEXT("Default row missing from DataTable")); return false; }
	TCMC->MovementMode = MOVE_Walking;

	// Directional differentiation (forward is the fastest ground direction).
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Forward);
	const float Fwd = TCMC->GetMaxSpeed();
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Strafe);
	const float Strafe = TCMC->GetMaxSpeed();
	TestTrue(TEXT("Forward cap > 0"), Fwd > 0.f);
	TestTrue(TEXT("Strafe cap < Forward cap"), Strafe < Fwd);

	// Readiness scaling (MovementReady 1.00 > LowReady 0.90 > ADS 0.75) at fixed direction.
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Forward);
	const float MR = TCMC->GetMaxSpeed();
	TCMC->RestoreIntentForReplay(ECombatReadinessState::LowReady, false, ETacticalMoveDir::Forward);
	const float LR = TCMC->GetMaxSpeed();
	TCMC->RestoreIntentForReplay(ECombatReadinessState::ADS, false, ETacticalMoveDir::Forward);
	const float ADS = TCMC->GetMaxSpeed();
	TestTrue(TEXT("LowReady < MovementReady"), LR < MR);
	TestTrue(TEXT("ADS < LowReady"), ADS < LR);
	return true;
}

// ---------------------------------------------------------------------------
// 10. Crouched walking honors the profile crouch cap (main's crouch contract).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityCrouchSpeedTest,
	"TacticalMovement.MovementAuthority.CrouchedWalkSpeed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityCrouchSpeedTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }
	UDataTable* DT = LoadProfiles(*this);
	if (!DT) { return false; }

	WireOwner(Character, TCMC);
	if (Character->GetCharacterMovement() != TCMC || TCMC->GetCharacterOwner() != Character)
	{
		AddError(TEXT("CharacterOwner link not established; crouch state would be unreadable."));
		return false;
	}
	TCMC->CacheProfilesFromTable(DT, FName("Infantry_Default"), NAME_None);
	TCMC->MovementMode = MOVE_Walking;
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Forward);

	const float CrouchCap = 77.f;               // distinctive value, distinct from any profile cap
	TCMC->MaxWalkSpeedCrouched = CrouchCap;

	Character->bIsCrouched = false;
	const float Standing = TCMC->GetMaxSpeed();
	Character->bIsCrouched = true;
	const float Crouched = TCMC->GetMaxSpeed();

	TestEqual(TEXT("Crouched returns MaxWalkSpeedCrouched"), Crouched, CrouchCap);
	TestNotEqual(TEXT("Standing does not use the crouch cap"), Standing, CrouchCap);
	return true;
}

// ---------------------------------------------------------------------------
// 11. Falling uses the directional/readiness profile cap, NOT the constructor 500.
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityFallSpeedTest,
	"TacticalMovement.MovementAuthority.FallingDirectionalReadinessSpeed",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityFallSpeedTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }
	UDataTable* DT = LoadProfiles(*this);
	if (!DT) { return false; }

	WireOwner(Character, TCMC);
	TCMC->CacheProfilesFromTable(DT, FName("Infantry_Default"), NAME_None);
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Strafe);

	TCMC->MovementMode = MOVE_Walking;
	const float Walk = TCMC->GetMaxSpeed();
	TCMC->MovementMode = MOVE_Falling;
	const float Fall = TCMC->GetMaxSpeed();

	TestEqual(TEXT("Falling cap == walking directional cap (same intent)"), Fall, Walk);
	TestNotEqual(TEXT("Falling cap is NOT the constructor value 500"), Fall, 500.f);
	TestNotEqual(TEXT("Falling cap is NOT the un-profiled MaxWalkSpeed member"), Fall, TCMC->MaxWalkSpeed);
	return true;
}

// ---------------------------------------------------------------------------
// 12. A missing default row leaves profiles uncached; GetMaxSpeed() falls back
//     to Unreal's base speed (the constructor MaxWalkSpeed).
// ---------------------------------------------------------------------------
IMPLEMENT_SIMPLE_AUTOMATION_TEST(
	FMovementAuthorityMissingRowTest,
	"TacticalMovement.MovementAuthority.MissingDefaultRowFallsBackToBase",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FMovementAuthorityMissingRowTest::RunTest(const FString& Parameters)
{
	using namespace TacticalMovementAuthorityTests;
	ATacticalMovementCharacter* Character = MakeCharacter(*this);
	if (!Character) { return false; }
	UTacticalCharacterMovementComponent* TCMC = Character->GetTacticalMovementComponent();
	if (!TCMC) { AddError(TEXT("No custom CMC")); return false; }
	UDataTable* DT = LoadProfiles(*this);
	if (!DT) { return false; }

	WireOwner(Character, TCMC);

	// Valid table but a non-existent default row -> must not cache.
	TCMC->CacheProfilesFromTable(DT, FName("NoSuchRow_ShouldNotExist"), NAME_None);
	TestFalse(TEXT("Missing default row -> profiles not cached"), TCMC->AreProfilesCached());

	// GetMaxSpeed() falls back to base (constructor MaxWalkSpeed = 500) while walking.
	TCMC->MovementMode = MOVE_Walking;
	TCMC->RestoreIntentForReplay(ECombatReadinessState::MovementReady, false, ETacticalMoveDir::Forward);
	TestEqual(TEXT("Uncached -> base MaxWalkSpeed"), TCMC->GetMaxSpeed(), TCMC->MaxWalkSpeed);

	// A null table must also leave profiles uncached.
	TCMC->CacheProfilesFromTable(nullptr, FName("Infantry_Default"), NAME_None);
	TestFalse(TEXT("Null table -> profiles not cached"), TCMC->AreProfilesCached());
	return true;
}

#endif // WITH_AUTOMATION_TESTS
