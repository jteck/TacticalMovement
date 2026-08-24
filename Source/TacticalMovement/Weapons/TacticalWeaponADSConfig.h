// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "TacticalWeaponADSConfig.generated.h"

/**
 * Per-weapon ADS configuration.
 *
 * SCOPE: this asset currently carries exactly one value - the duration of the ADS **camera FOV**
 * transition. It does NOT describe total ADS presentation. The AnimBP ADS pose blend is a separate
 * mechanism on a separate timeline and is unaffected by anything here. Weapon weight, fatigue,
 * stamina and injury are not modelled by this asset.
 */
UCLASS(BlueprintType)
class TACTICALMOVEMENT_API UTacticalWeaponADSConfig : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/**
	 * Seconds for this weapon's ADS **camera-FOV** transition.
	 *
	 * Applied as a play rate on the character's ADS FOV timeline, so the authored curve shape is
	 * preserved and only its duration scales. Setting this equal to the timeline's authored length
	 * reproduces the accepted timing exactly (play rate 1.0).
	 *
	 * A value <= 0 is treated as "unset": the timeline's authored duration is used unchanged.
	 */
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "ADS",
		meta = (ClampMin = "0.0", UIMin = "0.05", UIMax = "1.0", ForceUnits = "s"))
	float ADSCameraFOVDurationSeconds = 0.f;
};
