// Copyright Epic Games, Inc. All Rights Reserved.


#include "TacticalContextEffectComponent.h"

#include "Engine/World.h"
#include "TacticalContextEffectsSubsystem.h"
#include "PhysicalMaterials/PhysicalMaterial.h"

#include UE_INLINE_GENERATED_CPP_BY_NAME(TacticalContextEffectComponent)

class UAnimSequenceBase;
class USceneComponent;



// Sets default values for this component's properties
UTacticalContextEffectComponent::UTacticalContextEffectComponent()
{
	// Disable component tick, enable Auto Activate
	PrimaryComponentTick.bCanEverTick = false;
	bAutoActivate = true;
	// ...
}


// Called when the game starts
void UTacticalContextEffectComponent::BeginPlay()
{
	Super::BeginPlay();

	// ...
	CurrentContexts.AppendTags(DefaultEffectContexts);
	CurrentContextEffectsLibraries = DefaultContextEffectsLibraries;

	// On Begin Play, Load and Add Context Effects pairings
	if (const UWorld* World = GetWorld())
	{
		if (UTacticalContextEffectsSubsystem* TacticalContextEffectsSubsystem = World->GetSubsystem<UTacticalContextEffectsSubsystem>())
		{
			TacticalContextEffectsSubsystem->LoadAndAddContextEffectsLibraries(GetOwner(), CurrentContextEffectsLibraries);
		}
	}
}

void UTacticalContextEffectComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	// On End PLay, remove unnecessary context effects pairings
	if (const UWorld* World = GetWorld())
	{
		if (UTacticalContextEffectsSubsystem* TacticalContextEffectsSubsystem = World->GetSubsystem<UTacticalContextEffectsSubsystem>())
		{
			TacticalContextEffectsSubsystem->UnloadAndRemoveContextEffectsLibraries(GetOwner());
		}
	}

	Super::EndPlay(EndPlayReason);
}

// Implementation of Interface's AnimMotionEffect function
void UTacticalContextEffectComponent::AnimMotionEffect_Implementation(const FName Bone, const FGameplayTag MotionEffect, USceneComponent* StaticMeshComponent,
	const FVector LocationOffset, const FRotator RotationOffset, const UAnimSequenceBase* AnimationSequence,
	const bool bHitSuccess, const FHitResult HitResult, FGameplayTagContainer Contexts,
	FVector VFXScale, float AudioVolume, float AudioPitch)
{
	// Prep Components
	TArray<UAudioComponent*> AudioComponentsToAdd;
	TArray<UNiagaraComponent*> NiagaraComponentsToAdd;

	FGameplayTagContainer TotalContexts;

	// Aggregate contexts
	TotalContexts.AppendTags(Contexts);
	TotalContexts.AppendTags(CurrentContexts);

	// Check if converting Physical Surface Type to Context
	if (bConvertPhysicalSurfaceToContext)
	{
		// Get Phys Mat Type Pointer
		TWeakObjectPtr<UPhysicalMaterial> PhysicalSurfaceTypePtr = HitResult.PhysMaterial;

		// Check if pointer is okay
		if (PhysicalSurfaceTypePtr.IsValid())
		{
			// Get the Surface Type Pointer
			TEnumAsByte<EPhysicalSurface> PhysicalSurfaceType = PhysicalSurfaceTypePtr->SurfaceType;

			// If Settings are valid
			if (const UTacticalContextEffectsSettings* TacticalContextEffectsSettings = GetDefault<UTacticalContextEffectsSettings>())
			{
				// Convert Surface Type to known
				if (const FGameplayTag* SurfaceContextPtr = TacticalContextEffectsSettings->SurfaceTypeToContextMap.Find(PhysicalSurfaceType))
				{
					FGameplayTag SurfaceContext = *SurfaceContextPtr;

					TotalContexts.AddTag(SurfaceContext);
				}
			}
		}
	}

	// Cycle through Active Audio Components and cache
	for (UAudioComponent* ActiveAudioComponent : ActiveAudioComponents)
	{
		if (ActiveAudioComponent)
		{
			AudioComponentsToAdd.Add(ActiveAudioComponent);
		}
	}

	// Cycle through Active Niagara Components and cache
	for (UNiagaraComponent* ActiveNiagaraComponent : ActiveNiagaraComponents)
	{
		if (ActiveNiagaraComponent)
		{
			NiagaraComponentsToAdd.Add(ActiveNiagaraComponent);
		}
	}

	// Get World
	if (const UWorld* World = GetWorld())
	{
		// Get Subsystem
		if (UTacticalContextEffectsSubsystem* TacticalContextEffectsSubsystem = World->GetSubsystem<UTacticalContextEffectsSubsystem>())
		{
			// Set up Audio Components and Niagara
			TArray<UAudioComponent*> AudioComponents;
			TArray<UNiagaraComponent*> NiagaraComponents;

			// Spawn effects
			TacticalContextEffectsSubsystem->SpawnContextEffects(GetOwner(), StaticMeshComponent, Bone, 
				LocationOffset, RotationOffset, MotionEffect, TotalContexts,
				AudioComponents, NiagaraComponents, VFXScale, AudioVolume, AudioPitch);

			// Append resultant effects
			AudioComponentsToAdd.Append(AudioComponents);
			NiagaraComponentsToAdd.Append(NiagaraComponents);
		}
	}

	// Append Active Audio Components
	ActiveAudioComponents.Empty();
	ActiveAudioComponents.Append(AudioComponentsToAdd);

	// Append Active
	ActiveNiagaraComponents.Empty();
	ActiveNiagaraComponents.Append(NiagaraComponentsToAdd);

}

void UTacticalContextEffectComponent::UpdateEffectContexts(FGameplayTagContainer NewEffectContexts)
{
	// Reset and update
	CurrentContexts.Reset(NewEffectContexts.Num());
	CurrentContexts.AppendTags(NewEffectContexts);
}

void UTacticalContextEffectComponent::UpdateLibraries(
	TSet<TSoftObjectPtr<UTacticalContextEffectsLibrary>> NewContextEffectsLibraries)
{
	// Clear out existing Effects
	CurrentContextEffectsLibraries = NewContextEffectsLibraries;

	// Get World
	if (const UWorld* World = GetWorld())
	{
		// Get Subsystem
		if (UTacticalContextEffectsSubsystem* TacticalContextEffectsSubsystem = World->GetSubsystem<UTacticalContextEffectsSubsystem>())
		{
			// Load and Add Libraries to Subsystem                  
			TacticalContextEffectsSubsystem->LoadAndAddContextEffectsLibraries(GetOwner(), CurrentContextEffectsLibraries);
		}
	}
}

