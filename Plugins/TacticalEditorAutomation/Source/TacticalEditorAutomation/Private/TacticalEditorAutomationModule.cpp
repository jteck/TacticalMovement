// Copyright Epic Games, Inc. All Rights Reserved.

#include "Modules/ModuleManager.h"
#include "ToolsetRegistry/UToolsetRegistry.h"

#include "TacticalEditorAutomationToolset.h"
#include "TacticalAnimAuthoringToolset.h"

#define LOCTEXT_NAMESPACE "FTacticalEditorAutomationModule"

class FTacticalEditorAutomationModule : public IModuleInterface
{
	virtual void StartupModule() override
	{
		UToolsetRegistry::RegisterToolsetClass(UTacticalEditorAutomationToolset::StaticClass());
		UToolsetRegistry::RegisterToolsetClass(UTacticalAnimAuthoringToolset::StaticClass());
	}

	virtual void ShutdownModule() override
	{
		UToolsetRegistry::UnregisterToolsetClass(UTacticalAnimAuthoringToolset::StaticClass());
		UToolsetRegistry::UnregisterToolsetClass(UTacticalEditorAutomationToolset::StaticClass());
	}
};

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FTacticalEditorAutomationModule, TacticalEditorAutomation)
