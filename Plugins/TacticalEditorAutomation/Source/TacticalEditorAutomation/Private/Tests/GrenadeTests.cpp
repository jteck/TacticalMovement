// Copyright Epic Games, Inc. All Rights Reserved.
//
// Automation tests for the grenade slice (B).
//
// Scope: the authored data and the server-authoritative fuse/damage behaviour of
// BP_TacticalGrenade, plus the character-side constants that must stay in step with the
// authored montages. Input, montage playback and replication across a real connection are
// covered by the two-client Standalone gate, not here.

#include "CoreMinimal.h"

#if WITH_AUTOMATION_TESTS

#include "Misc/AutomationTest.h"
#include "Animation/AnimMontage.h"
#include "Animation/AnimNotifies/AnimNotify.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "GameFramework/DamageType.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "Components/StaticMeshComponent.h"
#include "TacticalMovementCharacter.h"
#include "GrenadeTestWitness.h"

namespace TacticalGrenadeTests
{
	static const TCHAR* GrenadeClassPath =
		TEXT("/Game/Weapons/Grenade/BP_TacticalGrenade.BP_TacticalGrenade_C");
	static const TCHAR* CharacterClassPath =
		TEXT("/Game/ThirdPerson/Blueprints/BP_ThirdPersonCharacter.BP_ThirdPersonCharacter_C");
	static const TCHAR* TPMontagePath =
		TEXT("/Game/Characters/Mannequins/Anims/Rifle/Grenade/AM_Rifle_GrenadeToss.AM_Rifle_GrenadeToss");
	static const TCHAR* FPMontagePath =
		TEXT("/Game/FirstPerson/Animations/Montages/AM_TacticalFP_GrenadeThrow.AM_TacticalFP_GrenadeThrow");
	static const TCHAR* GrenadeMeshPath =
		TEXT("/Game/Weapons/Grenade/Mesh/SM_grenade.SM_grenade");

	/** Lyra's authored grenade values, read off B_Grenade / its ProjectileMovement in the audit. */
	static constexpr float LyraFuseSeconds        = 2.0f;
	static constexpr float LyraExplosionRadius    = 450.0f;
	static constexpr float LyraInitialSpeed       = 2500.0f;
	static constexpr float LyraMaxSpeed           = 2550.0f;
	static constexpr float LyraGravityScale       = 1.0f;
	static constexpr float LyraBounciness         = 0.30f;
	static constexpr float LyraFriction           = 0.80f;
	static constexpr float LyraBounceStopThresh   = 25.0f;

	/** Our authored blast damage. Lyra's lives in a GAS CurveTable and is not adoptable no-GAS. */
	static constexpr float AuthoredBaseDamage     = 100.0f;

	/** Release notify name authored into both montages. */
	static const FName GrenadeReleaseNotify(TEXT("GrenadeRelease"));

	struct FScopedWorld
	{
		UWorld* World = nullptr;

		explicit FScopedWorld(FAutomationTestBase& Test)
		{
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
		}

		/** Advances the world (and therefore its timer manager) by RealSeconds in fixed steps. */
		void Advance(float RealSeconds, float Step = 1.0f / 60.0f)
		{
			const int32 Steps = FMath::CeilToInt(RealSeconds / Step);
			for (int32 i = 0; i < Steps && World; ++i)
			{
				World->Tick(LEVELTICK_All, Step);
			}
		}

		~FScopedWorld()
		{
			if (World)
			{
				GEngine->DestroyWorldContext(World);
				World->DestroyWorld(false);
			}
		}
	};

	static UClass* LoadGrenadeClass(FAutomationTestBase& Test)
	{
		UClass* Class = StaticLoadClass(AActor::StaticClass(), nullptr, GrenadeClassPath);
		if (!Class)
		{
			Test.AddError(FString::Printf(TEXT("Could not load grenade class '%s'"), GrenadeClassPath));
		}
		return Class;
	}

	/**
	 * Reads a Blueprint-declared numeric property by name. Blueprint "real" variables are
	 * doubles while older float properties are not, so both are handled explicitly - reading
	 * a double through a float pointer silently yields garbage.
	 */
	static bool ReadNumericProperty(UObject* Object, const TCHAR* PropertyName, double& OutValue)
	{
		if (!Object) { return false; }
		FProperty* Property = Object->GetClass()->FindPropertyByName(FName(PropertyName));
		if (!Property) { return false; }
		if (const FDoubleProperty* AsDouble = CastField<FDoubleProperty>(Property))
		{
			OutValue = AsDouble->GetPropertyValue_InContainer(Object);
			return true;
		}
		if (const FFloatProperty* AsFloat = CastField<FFloatProperty>(Property))
		{
			OutValue = AsFloat->GetPropertyValue_InContainer(Object);
			return true;
		}
		return false;
	}

	static bool ReadBoolProperty(UObject* Object, const TCHAR* PropertyName, bool& OutValue)
	{
		if (!Object) { return false; }
		FBoolProperty* Property = CastField<FBoolProperty>(Object->GetClass()->FindPropertyByName(FName(PropertyName)));
		if (!Property) { return false; }
		OutValue = Property->GetPropertyValue_InContainer(Object);
		return true;
	}

	/**
	 * Finds the first notify with the given name on a montage.
	 *
	 * AnimNotify_PlayMontageNotify carries the author-facing name on the notify object itself
	 * (FAnimNotifyEvent::NotifyName holds the class-derived name), so both are checked. The
	 * notify object is read by reflection to avoid depending on the notify's header.
	 */
	static bool MontageHasNotify(const UAnimMontage* Montage, FName NotifyName, float& OutTime)
	{
		if (!Montage) { return false; }
		for (const FAnimNotifyEvent& Event : Montage->Notifies)
		{
			bool bMatches = (Event.NotifyName == NotifyName);
			if (!bMatches && Event.Notify)
			{
				if (const FNameProperty* NameProperty =
					CastField<FNameProperty>(Event.Notify->GetClass()->FindPropertyByName(TEXT("NotifyName"))))
				{
					bMatches = (NameProperty->GetPropertyValue_InContainer(Event.Notify) == NotifyName);
				}
			}
			if (bMatches)
			{
				OutTime = Event.GetTriggerTime();
				return true;
			}
		}
		return false;
	}
}

// ---------------------------------------------------------------------------------------------
// 1. Authored class defaults
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeDefaultsMatchLyraAuthoredValues,
	"TacticalMovement.Grenade.DefaultsMatchLyraAuthoredValues",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeDefaultsMatchLyraAuthoredValues::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* GrenadeClass = LoadGrenadeClass(*this);
	if (!GrenadeClass) { return false; }

	AActor* CDO = GrenadeClass->GetDefaultObject<AActor>();
	if (!CDO) { AddError(TEXT("Grenade CDO was null")); return false; }

	TestTrue(TEXT("Grenade replicates"), CDO->GetIsReplicated());
	TestTrue(TEXT("Grenade replicates movement"), CDO->IsReplicatingMovement());
	TestEqual(TEXT("InitialLifeSpan is 0 (the fuse owns destruction)"), CDO->InitialLifeSpan, 0.0f);

	double FuseTime = 0.0;
	if (TestTrue(TEXT("FuseTime exists"), ReadNumericProperty(CDO, TEXT("FuseTime"), FuseTime)))
	{
		TestEqual(TEXT("FuseTime matches Lyra TimeBeforeExplode"), (float)FuseTime, LyraFuseSeconds);
	}

	double Radius = 0.0;
	if (TestTrue(TEXT("Explosion Radius exists"), ReadNumericProperty(CDO, TEXT("Explosion Radius"), Radius)))
	{
		TestEqual(TEXT("Explosion Radius matches Lyra"), (float)Radius, LyraExplosionRadius);
	}

	double Damage = 0.0;
	if (TestTrue(TEXT("Damage exists"), ReadNumericProperty(CDO, TEXT("Damage"), Damage)))
	{
		TestEqual(TEXT("Damage matches authored blast damage"), (float)Damage, AuthoredBaseDamage);
	}

	bool bDetonateOnImpact = true;
	if (TestTrue(TEXT("DetonateOnImpact exists"), ReadBoolProperty(CDO, TEXT("DetonateOnImpact"), bDetonateOnImpact)))
	{
		TestFalse(TEXT("Grenade does NOT detonate on impact (it bounces and runs a fuse)"), bDetonateOnImpact);
	}

	return true;
}

// ---------------------------------------------------------------------------------------------
// 2. The base template keeps its own hit-detonation behaviour
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FProjectileBaseStillDetonatesOnImpactByDefault,
	"TacticalMovement.Grenade.ProjectileBaseUnchangedByDefault",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FProjectileBaseStillDetonatesOnImpactByDefault::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* BaseClass = StaticLoadClass(AActor::StaticClass(), nullptr,
		TEXT("/Game/Variant_Shooter/Blueprints/Pickups/Projectiles/BP_ShooterProjectileBase.BP_ShooterProjectileBase_C"));
	if (!BaseClass) { AddError(TEXT("Could not load BP_ShooterProjectileBase_C")); return false; }

	bool bDetonateOnImpact = false;
	if (TestTrue(TEXT("DetonateOnImpact exists on the base"),
		ReadBoolProperty(BaseClass->GetDefaultObject<AActor>(), TEXT("DetonateOnImpact"), bDetonateOnImpact)))
	{
		// The opt-out we added must default to the template's pre-existing behaviour.
		TestTrue(TEXT("Base template still detonates on impact by default"), bDetonateOnImpact);
	}
	return true;
}

// ---------------------------------------------------------------------------------------------
// 3. Construction script applies Lyra's projectile feel
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeProjectileMovementMatchesLyra,
	"TacticalMovement.Grenade.ProjectileMovementMatchesLyra",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeProjectileMovementMatchesLyra::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* GrenadeClass = LoadGrenadeClass(*this);
	if (!GrenadeClass) { return false; }

	FScopedWorld Scoped(*this);
	if (!Scoped.World) { return false; }

	AActor* Grenade = Scoped.World->SpawnActor<AActor>(GrenadeClass, FTransform::Identity);
	if (!Grenade) { AddError(TEXT("SpawnActor for the grenade returned null")); return false; }

	UProjectileMovementComponent* PMC = Grenade->FindComponentByClass<UProjectileMovementComponent>();
	if (!PMC) { AddError(TEXT("Grenade has no ProjectileMovementComponent")); return false; }

	TestEqual(TEXT("InitialSpeed"), PMC->InitialSpeed, LyraInitialSpeed);
	TestEqual(TEXT("MaxSpeed"), PMC->MaxSpeed, LyraMaxSpeed);
	TestEqual(TEXT("ProjectileGravityScale"), PMC->ProjectileGravityScale, LyraGravityScale);
	TestTrue(TEXT("bShouldBounce"), PMC->bShouldBounce);
	TestEqual(TEXT("Bounciness"), PMC->Bounciness, LyraBounciness);
	TestEqual(TEXT("Friction"), PMC->Friction, LyraFriction);
	TestEqual(TEXT("BounceVelocityStopSimulatingThreshold"),
		PMC->BounceVelocityStopSimulatingThreshold, LyraBounceStopThresh);

	UStaticMeshComponent* MeshComp = Grenade->FindComponentByClass<UStaticMeshComponent>();
	if (TestNotNull(TEXT("Grenade has a StaticMeshComponent"), MeshComp))
	{
		UStaticMesh* Expected = LoadObject<UStaticMesh>(nullptr, GrenadeMeshPath);
		TestTrue(TEXT("Grenade uses Lyra's SM_grenade"), MeshComp->GetStaticMesh() == Expected);
	}

	return true;
}

// ---------------------------------------------------------------------------------------------
// 4. Detonation applies radial damage with falloff and tears the grenade down
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeDetonationAppliesRadialDamageWithFalloff,
	"TacticalMovement.Grenade.DetonationAppliesRadialDamageWithFalloff",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeDetonationAppliesRadialDamageWithFalloff::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* GrenadeClass = LoadGrenadeClass(*this);
	if (!GrenadeClass) { return false; }

	FScopedWorld Scoped(*this);
	if (!Scoped.World) { return false; }

	// Three damageable witnesses: blast centre, half the blast radius, and well outside it.
	AGrenadeTestWitness* Near = Scoped.World->SpawnActor<AGrenadeTestWitness>(
		AGrenadeTestWitness::StaticClass(), FTransform(FVector::ZeroVector));
	AGrenadeTestWitness* Far = Scoped.World->SpawnActor<AGrenadeTestWitness>(
		AGrenadeTestWitness::StaticClass(), FTransform(FVector(LyraExplosionRadius * 0.5f, 0.0f, 0.0f)));
	AGrenadeTestWitness* Outside = Scoped.World->SpawnActor<AGrenadeTestWitness>(
		AGrenadeTestWitness::StaticClass(), FTransform(FVector(LyraExplosionRadius * 2.0f, 0.0f, 0.0f)));
	if (!Near || !Far || !Outside) { AddError(TEXT("Could not spawn damage witnesses")); return false; }

	AActor* Grenade = Scoped.World->SpawnActor<AActor>(GrenadeClass, FTransform::Identity);
	if (!Grenade) { AddError(TEXT("SpawnActor for the grenade returned null")); return false; }
	if (!Grenade->HasActorBegunPlay()) { Grenade->DispatchBeginPlay(); }

	TestEqual(TEXT("No damage before detonation"), Near->DamageEventCount, 0);

	// Invoke the authoritative detonation directly. The fuse timer that normally calls this is
	// covered by FGrenadeFuseIsArmedOnAuthority and by the Standalone gate; driving the event
	// here keeps the damage assertions independent of timer plumbing in a bare test world.
	UFunction* Detonate = Grenade->FindFunction(FName(TEXT("Detonate")));
	if (!Detonate) { AddError(TEXT("BP_TacticalGrenade has no 'Detonate' event")); return false; }
	Grenade->ProcessEvent(Detonate, nullptr);

	AddInfo(FString::Printf(
		TEXT("Near: %d event(s), raw %.2f, scaled %.2f | Far: %d event(s), raw %.2f, scaled %.2f | Outside: %d event(s)"),
		Near->DamageEventCount, Near->AccumulatedDamage, Near->AccumulatedScaledDamage,
		Far->DamageEventCount, Far->AccumulatedDamage, Far->AccumulatedScaledDamage,
		Outside->DamageEventCount));

	// Exactly once per eligible actor - a second event would double-damage.
	TestEqual(TEXT("Actor at the blast centre was damaged exactly once"), Near->DamageEventCount, 1);
	TestEqual(TEXT("Actor at half radius was damaged exactly once"), Far->DamageEventCount, 1);
	TestEqual(TEXT("Actor beyond the blast radius was not damaged"), Outside->DamageEventCount, 0);

	// Prove what the server actually emitted, rather than assuming the node was configured right.
	TestTrue(TEXT("Event is an FRadialDamageEvent"), Near->bLastEventWasRadial);
	if (Near->bLastEventWasRadial)
	{
		TestEqual(TEXT("Emitted BaseDamage"), Near->LastBaseDamage, AuthoredBaseDamage, 0.01f);
		TestEqual(TEXT("Emitted MinimumDamage"), Near->LastMinimumDamage, 0.0f, 0.01f);
		TestEqual(TEXT("Emitted inner radius"), Near->LastInnerRadius, 0.0f, 0.01f);
		TestEqual(TEXT("Emitted outer radius"), Near->LastOuterRadius, LyraExplosionRadius, 0.01f);
		TestEqual(TEXT("Emitted linear falloff exponent"), Near->LastFalloff, 1.0f, 0.01f);
		TestTrue(TEXT("Blast origin is the grenade's location"),
			Near->LastOrigin.Equals(FVector::ZeroVector, 1.0f));
		TestTrue(TEXT("A damage type class was supplied"), Near->LastDamageType != nullptr);
		TestTrue(TEXT("The grenade is credited as the damage causer"), Near->LastDamageCauser == Grenade);
	}

	if (Near->DamageEventCount > 0 && Far->DamageEventCount > 0)
	{
		// The engine hands every victim BaseDamage and carries the falloff in the event, so the
		// raw figure is deliberately identical at both distances.
		TestEqual(TEXT("Engine delivers BaseDamage to the victim at the centre"),
			Near->AccumulatedDamage, AuthoredBaseDamage, 1.0f);
		TestEqual(TEXT("Engine delivers BaseDamage to the victim at half radius"),
			Far->AccumulatedDamage, AuthoredBaseDamage, 1.0f);

		// What we author - inner radius 0, outer radius 450, falloff exponent 1 - is what makes
		// the scaled damage fall off linearly with distance.
		TestEqual(TEXT("Centre resolves to full authored damage"),
			Near->AccumulatedScaledDamage, AuthoredBaseDamage, 1.0f);
		TestEqual(TEXT("Half radius resolves to half damage (linear falloff)"),
			Far->AccumulatedScaledDamage, AuthoredBaseDamage * 0.5f, 5.0f);
		TestTrue(TEXT("Resolved damage falls off with distance"),
			Far->AccumulatedScaledDamage < Near->AccumulatedScaledDamage);
	}

	// Detonation must also take the grenade out of the world.
	TestTrue(TEXT("Grenade stops colliding and hides on detonation"),
		!IsValid(Grenade) || Grenade->IsActorBeingDestroyed() || Grenade->IsHidden());

	return true;
}

// ---------------------------------------------------------------------------------------------
// 4b. The fuse is armed on the authority at BeginPlay
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeFuseIsArmedOnAuthority,
	"TacticalMovement.Grenade.FuseIsArmedOnAuthority",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeFuseIsArmedOnAuthority::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* GrenadeClass = LoadGrenadeClass(*this);
	if (!GrenadeClass) { return false; }

	FScopedWorld Scoped(*this);
	if (!Scoped.World) { return false; }

	AActor* Grenade = Scoped.World->SpawnActor<AActor>(GrenadeClass, FTransform::Identity);
	if (!Grenade) { AddError(TEXT("SpawnActor for the grenade returned null")); return false; }
	if (!Grenade->HasActorBegunPlay()) { Grenade->DispatchBeginPlay(); }

	TestTrue(TEXT("Spawned grenade holds authority"), Grenade->HasAuthority());
	TestTrue(TEXT("BeginPlay ran"), Grenade->HasActorBegunPlay());

	// BeginPlay -> HasAuthority -> Set Timer by Event should detonate the grenade once the
	// fuse elapses. Report how far world time actually advanced so a bare-world tick limitation
	// is distinguishable from a wiring defect.
	// Control: prove the world's timer manager runs at all before blaming the Blueprint.
	FTimerHandle ControlHandle;
	bool bControlTimerFired = false;
	Scoped.World->GetTimerManager().SetTimer(ControlHandle,
		FTimerDelegate::CreateLambda([&bControlTimerFired]() { bControlTimerFired = true; }), 0.5f, false);

	const float TimeBefore = Scoped.World->GetTimeSeconds();
	Scoped.Advance(LyraFuseSeconds + 0.5f);
	const float TimeAdvanced = Scoped.World->GetTimeSeconds() - TimeBefore;
	AddInfo(FString::Printf(TEXT("World time advanced %.3fs; control timer fired: %s; grenade hidden: %s, valid: %s"),
		TimeAdvanced,
		bControlTimerFired ? TEXT("yes") : TEXT("NO"),
		Grenade->IsHidden() ? TEXT("yes") : TEXT("no"),
		IsValid(Grenade) ? TEXT("yes") : TEXT("no")));

	if (!bControlTimerFired)
	{
		AddWarning(TEXT("The bare automation world does not run timers; fuse elapse is covered by the Standalone gate."));
		return true;
	}

	if (TimeAdvanced + KINDA_SMALL_NUMBER < LyraFuseSeconds)
	{
		AddWarning(FString::Printf(
			TEXT("Bare automation world only advanced %.3fs; fuse elapse is covered by the Standalone gate."),
			TimeAdvanced));
		return true;
	}

	TestTrue(TEXT("Fuse detonated the grenade without any further input"),
		!IsValid(Grenade) || Grenade->IsActorBeingDestroyed() || Grenade->IsHidden());

	return true;
}

// ---------------------------------------------------------------------------------------------
// 5. Character release timing stays in step with the authored montage notify
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeReleaseTimeMatchesAuthoredNotify,
	"TacticalMovement.Grenade.ReleaseTimeMatchesAuthoredNotify",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeReleaseTimeMatchesAuthoredNotify::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UAnimMontage* TPMontage = LoadObject<UAnimMontage>(nullptr, TPMontagePath);
	if (!TPMontage) { AddError(TEXT("Could not load AM_Rifle_GrenadeToss")); return false; }

	float NotifyTime = -1.0f;
	if (!TestTrue(TEXT("TP montage carries the GrenadeRelease notify"),
		MontageHasNotify(TPMontage, GrenadeReleaseNotify, NotifyTime)))
	{
		return false;
	}

	UClass* CharacterClass = StaticLoadClass(ATacticalMovementCharacter::StaticClass(), nullptr, CharacterClassPath);
	if (!CharacterClass) { AddError(TEXT("Could not load BP_ThirdPersonCharacter_C")); return false; }

	double ReleaseTime = 0.0;
	if (TestTrue(TEXT("GrenadeReleaseTime exists on the character"),
		ReadNumericProperty(CharacterClass->GetDefaultObject<AActor>(), TEXT("GrenadeReleaseTime"), ReleaseTime)))
	{
		// The server spawn timer must fire at the frame the throwing hand releases.
		TestEqual(TEXT("GrenadeReleaseTime matches the authored notify time"), (float)ReleaseTime, NotifyTime, 0.01f);
	}

	// The release timer must land inside the montage, not past its end.
	TestTrue(TEXT("Release happens before the montage ends"), NotifyTime < TPMontage->GetPlayLength());

	// The FP montage carries its own release notify at a different time, because it is a
	// different source animation with different pacing. The authoritative spawn is driven by the
	// TP notify (the spawn transform is read from the TP mesh's hand), so any FP/TP gap is a
	// first-person presentation offset. Surfaced here so it can never drift silently.
	UAnimMontage* FPMontage = LoadObject<UAnimMontage>(nullptr, FPMontagePath);
	float FPNotifyTime = -1.0f;
	if (FPMontage && MontageHasNotify(FPMontage, GrenadeReleaseNotify, FPNotifyTime))
	{
		const float Divergence = FPNotifyTime - NotifyTime;
		AddInfo(FString::Printf(
			TEXT("Release notifies - TP %.4fs (authoritative), FP %.4fs, first-person offset %+.4fs"),
			NotifyTime, FPNotifyTime, Divergence));

		if (FMath::Abs(Divergence) > 0.05f)
		{
			AddWarning(FString::Printf(
				TEXT("KNOWN GAP: the first-person throw releases %+.3fs from the authoritative spawn. ")
				TEXT("Closing it needs the FP montage retimed; tracked, not silently ignored."),
				Divergence));
		}
	}

	return true;
}

// ---------------------------------------------------------------------------------------------
// 5b. Readiness policy: the throw is unconditional
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeReadinessGating,
	"TacticalMovement.Grenade.ReadinessGating",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeReadinessGating::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UClass* CharacterClass = StaticLoadClass(ATacticalMovementCharacter::StaticClass(), nullptr, CharacterClassPath);
	if (!CharacterClass) { AddError(TEXT("Could not load BP_ThirdPersonCharacter_C")); return false; }

	FScopedWorld Scoped(*this);
	if (!Scoped.World) { return false; }

	UFunction* ThrowFn = CharacterClass->FindFunctionByName(FName(TEXT("Server_ThrowGrenade")));
	if (!ThrowFn) { AddError(TEXT("BP_ThirdPersonCharacter has no 'Server_ThrowGrenade' event")); return false; }

	FBoolProperty* BusyProp = CastField<FBoolProperty>(
		CharacterClass->FindPropertyByName(FName(TEXT("bGrenadeThrowInProgress"))));
	FProperty* ReadinessProp = CharacterClass->FindPropertyByName(FName(TEXT("CombatReadinessState")));
	if (!BusyProp || !ReadinessProp) { AddError(TEXT("Missing bGrenadeThrowInProgress or CombatReadinessState")); return false; }
	FByteProperty* ReadinessByte = CastField<FByteProperty>(ReadinessProp);
	FEnumProperty* ReadinessEnum = CastField<FEnumProperty>(ReadinessProp);
	if (!ReadinessByte && !ReadinessEnum) { AddError(TEXT("CombatReadinessState is not an enum property")); return false; }

	// Owner decision (2026-08-31): a grenade throw is ALWAYS available. An earlier build gated Sul
	// out; that was rejected on the visual gate, so no readiness state may block the throw.
	struct FCase { const TCHAR* Name; uint8 Value; bool bAllowed; };
	const FCase Cases[] = {
		{ TEXT("Sul"),           0, true },
		{ TEXT("LowReady"),      1, true },
		{ TEXT("MovementReady"), 2, true },
		{ TEXT("ADS"),           3, true },
	};

	for (const FCase& Case : Cases)
	{
		ATacticalMovementCharacter* Character =
			Scoped.World->SpawnActor<ATacticalMovementCharacter>(CharacterClass, FTransform::Identity);
		if (!Character) { AddError(TEXT("Could not spawn the character")); return false; }
		if (!Character->HasActorBegunPlay()) { Character->DispatchBeginPlay(); }

		if (ReadinessByte) { ReadinessByte->SetPropertyValue_InContainer(Character, Case.Value); }
		else { ReadinessEnum->GetUnderlyingProperty()->SetIntPropertyValue(
			ReadinessEnum->ContainerPtrToValuePtr<void>(Character), (int64)Case.Value); }

		BusyProp->SetPropertyValue_InContainer(Character, false);
		Character->ProcessEvent(ThrowFn, nullptr);
		const bool bAccepted = BusyProp->GetPropertyValue_InContainer(Character);

		TestTrue(FString::Printf(TEXT("%s may throw (throw is unconditional)"), Case.Name), bAccepted);
		(void)Case.bAllowed;

		Character->Destroy();
	}

	return true;
}

// ---------------------------------------------------------------------------------------------
// 6. Both montages are authored on the slots their AnimBPs actually expose
// ---------------------------------------------------------------------------------------------

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGrenadeMontagesUseExpectedSlots,
	"TacticalMovement.Grenade.MontagesUseExpectedSlots",
	EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)

bool FGrenadeMontagesUseExpectedSlots::RunTest(const FString&)
{
	using namespace TacticalGrenadeTests;

	UAnimMontage* TPMontage = LoadObject<UAnimMontage>(nullptr, TPMontagePath);
	UAnimMontage* FPMontage = LoadObject<UAnimMontage>(nullptr, FPMontagePath);
	if (!TPMontage || !FPMontage) { AddError(TEXT("Could not load both grenade montages")); return false; }

	TSet<FName> TPSlots;
	for (const FSlotAnimationTrack& Track : TPMontage->SlotAnimTracks) { TPSlots.Add(Track.SlotName); }

	// Topology F routes both of Lyra's authored slot tracks through ABP_TacticalRifle_UBL.
	TestTrue(TEXT("TP montage drives the UpperBody slot"), TPSlots.Contains(FName(TEXT("UpperBody"))));
	TestTrue(TEXT("TP montage drives the UpperBodyAdditive slot"), TPSlots.Contains(FName(TEXT("UpperBodyAdditive"))));

	TSet<FName> FPSlots;
	for (const FSlotAnimationTrack& Track : FPMontage->SlotAnimTracks) { FPSlots.Add(Track.SlotName); }

	// The FP arms AnimBP already exposes DefaultSlot; no ABP_TacticalFP change was needed.
	TestTrue(TEXT("FP montage drives DefaultSlot"), FPSlots.Contains(FName(TEXT("DefaultSlot"))));

	float FPNotifyTime = -1.0f;
	TestTrue(TEXT("FP montage carries the GrenadeRelease notify"),
		MontageHasNotify(FPMontage, GrenadeReleaseNotify, FPNotifyTime));

	return true;
}

#endif // WITH_AUTOMATION_TESTS
