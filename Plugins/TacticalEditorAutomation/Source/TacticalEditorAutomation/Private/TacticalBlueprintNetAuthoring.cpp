#include "TacticalBlueprintNetAuthoring.h"

#include "EdGraph/EdGraph.h"
#include "Engine/Blueprint.h"
#include "K2Node_CustomEvent.h"
#include "Kismet2/BlueprintEditorUtils.h"

namespace
{
	uint32 NetFlagsFor(ETacticalEventNetMode NetMode)
	{
		switch (NetMode)
		{
		case ETacticalEventNetMode::Multicast:			return FUNC_NetMulticast;
		case ETacticalEventNetMode::RunOnServer:		return FUNC_NetServer;
		case ETacticalEventNetMode::RunOnOwningClient:	return FUNC_NetClient;
		default:										return 0;
		}
	}

	UK2Node_CustomEvent* FindCustomEvent(UBlueprint* Blueprint, FName EventName)
	{
		if (!Blueprint)
		{
			return nullptr;
		}

		TArray<UK2Node_CustomEvent*> Events;
		FBlueprintEditorUtils::GetAllNodesOfClass<UK2Node_CustomEvent>(Blueprint, Events);
		for (UK2Node_CustomEvent* Event : Events)
		{
			if (Event && Event->CustomFunctionName == EventName)
			{
				return Event;
			}
		}
		return nullptr;
	}
}

bool UTacticalBlueprintNetAuthoring::SetCustomEventNetMode(UBlueprint* Blueprint, FName EventName, ETacticalEventNetMode NetMode, bool bReliable)
{
	UK2Node_CustomEvent* Event = FindCustomEvent(Blueprint, EventName);
	if (!Event)
	{
		return false;
	}

	// Same mutation the Details panel performs (FBlueprintGraphActionDetails::SetNetFlags):
	// clear every net flag, then set FUNC_Net plus the requested specifier.
	const uint32 Requested = NetFlagsFor(NetMode);
	const uint32 FlagsToClear = FUNC_Net | FUNC_NetMulticast | FUNC_NetServer | FUNC_NetClient | FUNC_NetReliable;
	const uint32 FlagsToSet = Requested ? (FUNC_Net | Requested | (bReliable ? FUNC_NetReliable : 0u)) : 0u;

	Event->Modify();
	Event->FunctionFlags &= ~FlagsToClear;
	Event->FunctionFlags |= FlagsToSet;

	FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(Blueprint);
	return true;
}

FString UTacticalBlueprintNetAuthoring::GetCustomEventNetMode(UBlueprint* Blueprint, FName EventName)
{
	const UK2Node_CustomEvent* Event = FindCustomEvent(Blueprint, EventName);
	if (!Event)
	{
		return FString();
	}

	const uint32 Flags = Event->FunctionFlags;
	FString Mode = TEXT("NotReplicated");
	if (Flags & FUNC_NetMulticast)		{ Mode = TEXT("Multicast"); }
	else if (Flags & FUNC_NetServer)	{ Mode = TEXT("RunOnServer"); }
	else if (Flags & FUNC_NetClient)	{ Mode = TEXT("RunOnOwningClient"); }

	return FString::Printf(TEXT("%s|%s"), *Mode, (Flags & FUNC_NetReliable) ? TEXT("Reliable") : TEXT("Unreliable"));
}
