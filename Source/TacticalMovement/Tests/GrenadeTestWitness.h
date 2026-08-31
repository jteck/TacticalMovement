// Copyright Epic Games, Inc. All Rights Reserved.
//
// Test-only actor used by the grenade automation tests to observe radial damage.
// AActor::OnTakeAnyDamage is a dynamic delegate and cannot take a lambda, so the witness
// records damage by overriding TakeDamage directly. Nothing in the game references this class.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GrenadeTestWitness.generated.h"

UCLASS(NotBlueprintable, NotPlaceable, Transient, HideDropdown)
class AGrenadeTestWitness : public AActor
{
	GENERATED_BODY()

public:
	AGrenadeTestWitness();

	/** Radial damage is resolved by an overlap query, so the witness needs real collision. */
	UPROPERTY()
	TObjectPtr<class USphereComponent> Collision;

	virtual float TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent,
		AController* EventInstigator, AActor* DamageCauser) override;

	/** Total damage as delivered by the engine (radial damage delivers BaseDamage unscaled). */
	float AccumulatedDamage = 0.0f;

	/**
	 * Damage after applying the radial falloff carried in FRadialDamageEvent::Params.
	 * UGameplayStatics::ApplyRadialDamageWithFalloff deliberately passes BaseDamage to
	 * TakeDamage and leaves the distance scaling to the victim, so this is where the
	 * authored inner/outer radius and falloff exponent actually take effect.
	 */
	float AccumulatedScaledDamage = 0.0f;

	/** How many separate damage events it received. */
	int32 DamageEventCount = 0;

	/** True when the last event was an FRadialDamageEvent. */
	bool bLastEventWasRadial = false;

	/** Radial parameters carried by the last event, for proving what the server emitted. */
	FVector LastOrigin = FVector::ZeroVector;
	float LastInnerRadius = -1.0f;
	float LastOuterRadius = -1.0f;
	float LastFalloff = -1.0f;
	float LastBaseDamage = -1.0f;
	float LastMinimumDamage = -1.0f;
	TSubclassOf<UDamageType> LastDamageType = nullptr;
	TWeakObjectPtr<AActor> LastDamageCauser;
	TWeakObjectPtr<AController> LastInstigatedBy;
};
