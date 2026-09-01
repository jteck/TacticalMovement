// Editor-only Blueprint authoring helpers.
//
// Exists because UK2Node_CustomEvent::FunctionFlags is a plain UPROPERTY() with no
// BlueprintReadWrite/editor exposure, so the replication specifier of a Blueprint custom
// event (Run on Server / Multicast / Reliable) is unreachable from editor Python. The
// Blueprint editor sets it through FBlueprintGraphActionDetails::SetNetFlags; this library
// performs the identical mutation from script so Blueprint-side networking can be authored
// headlessly instead of by hand.

#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "TacticalBlueprintNetAuthoring.generated.h"

class UBlueprint;

/** Replication specifier applied to a Blueprint custom event. Mirrors the editor's dropdown. */
UENUM(BlueprintType)
enum class ETacticalEventNetMode : uint8
{
	NotReplicated	UMETA(DisplayName = "Not Replicated"),
	Multicast		UMETA(DisplayName = "Multicast"),
	RunOnServer		UMETA(DisplayName = "Run on Server"),
	RunOnOwningClient UMETA(DisplayName = "Run on Owning Client")
};

UCLASS()
class UTacticalBlueprintNetAuthoring : public UBlueprintFunctionLibrary
{
	GENERATED_BODY()

public:
	/**
	 * Sets the replication specifier and reliability of a Blueprint custom event node,
	 * matching what the Blueprint editor's Details panel does.
	 *
	 * @param Blueprint  Blueprint owning the event.
	 * @param EventName  CustomFunctionName of the target UK2Node_CustomEvent.
	 * @param NetMode    Replication specifier to apply.
	 * @param bReliable  Reliable delivery. Ignored (forced false) when NetMode is NotReplicated.
	 * @return true when the node was found and updated.
	 */
	UFUNCTION(BlueprintCallable, Category = "Tactical|Authoring")
	static bool SetCustomEventNetMode(UBlueprint* Blueprint, FName EventName, ETacticalEventNetMode NetMode, bool bReliable);

	/**
	 * Reads back the replication specifier of a custom event as "<mode>|<Reliable|Unreliable>",
	 * or an empty string when the event is not found. Verification aid.
	 */
	UFUNCTION(BlueprintCallable, Category = "Tactical|Authoring")
	static FString GetCustomEventNetMode(UBlueprint* Blueprint, FName EventName);
};
