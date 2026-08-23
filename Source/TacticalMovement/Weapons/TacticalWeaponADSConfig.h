// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "TacticalWeaponADSConfig.generated.h"

/**
 * Minimal per-weapon ADS configuration.
 *
 * Scope is deliberately one field. The project's accepted ADS presentation is the
 * BP_ThirdPersonCharacter `TL_ADS_FOV` timeline (camera FOV) plus a fixed AnimBP pose blend;
 * this asset lets a weapon state how long the FOV portion should take without editing that
 * timeline, any animation asset, or any Blueprint graph.
 *
 * The value is applied as a timeline PLAY RATE, so the authored curve shape is preserved
 * exactly - only its duration scales.
 */
UCLASS(BlueprintType)
class TACTICALMOVEMENT_API UTacticalWeaponADSConfig : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/**
	 * Seconds for the ADS camera-FOV transition for this weapon.
	 *
	 * Defaults to ATacticalMovementCharacter::DefaultADSDurationSeconds, which is the project's
	 * currently accepted timing. Leaving it at the default is a no-op: the timeline runs at play
	 * rate 1.0 exactly as authored.
	 *
	 * Heavier weapons are expected to raise this. A per-weapon weight modifier, if it is ever
	 * added, multiplies into this value - it does not replace it.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ADS",
		meta = (ClampMin = "0.01", UIMin = "0.05", UIMax = "1.0", ForceUnits = "s"))
	float ADSDurationSeconds = 0.36f;
};
