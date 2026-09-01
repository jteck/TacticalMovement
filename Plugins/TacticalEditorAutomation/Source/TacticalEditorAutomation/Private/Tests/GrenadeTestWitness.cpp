// Copyright Epic Games, Inc. All Rights Reserved.

#include "GrenadeTestWitness.h"

#include "Components/SphereComponent.h"
#include "Engine/DamageEvents.h"

AGrenadeTestWitness::AGrenadeTestWitness()
{
	PrimaryActorTick.bCanEverTick = false;
	SetCanBeDamaged(true);

	Collision = CreateDefaultSubobject<USphereComponent>(TEXT("Collision"));
	Collision->InitSphereRadius(34.0f);
	Collision->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Collision->SetCollisionObjectType(ECC_Pawn);
	Collision->SetCollisionResponseToAllChannels(ECR_Overlap);
	RootComponent = Collision;
}

float AGrenadeTestWitness::TakeDamage(float DamageAmount, const FDamageEvent& DamageEvent,
	AController* EventInstigator, AActor* DamageCauser)
{
	const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
	AccumulatedDamage += DamageAmount;

	float Scaled = DamageAmount;
	bLastEventWasRadial = DamageEvent.IsOfType(FRadialDamageEvent::ClassID);
	if (bLastEventWasRadial)
	{
		const FRadialDamageEvent& Radial = static_cast<const FRadialDamageEvent&>(DamageEvent);
		const float Distance = FVector::Dist(Radial.Origin, GetActorLocation());
		Scaled = DamageAmount * Radial.Params.GetDamageScale(Distance);

		LastOrigin = Radial.Origin;
		LastInnerRadius = Radial.Params.InnerRadius;
		LastOuterRadius = Radial.Params.OuterRadius;
		LastFalloff = Radial.Params.DamageFalloff;
		LastBaseDamage = Radial.Params.BaseDamage;
		LastMinimumDamage = Radial.Params.MinimumDamage;
		LastDamageType = Radial.DamageTypeClass;
	}
	LastDamageCauser = DamageCauser;
	LastInstigatedBy = EventInstigator;
	AccumulatedScaledDamage += Scaled;

	++DamageEventCount;
	return Applied;
}
