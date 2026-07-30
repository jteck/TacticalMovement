// Copyright Epic Games, Inc. All Rights Reserved.

#include "Modules/ModuleManager.h"
#include "ToolsetRegistry/UToolsetRegistry.h"

#include "TacticalEditorAutomationToolset.h"
#include "TacticalAnimAuthoringToolset.h"
#include "TacticalRuntimeAnimInspectionToolset.h"

#define LOCTEXT_NAMESPACE "FTacticalEditorAutomationModule"

class FTacticalEditorAutomationModule : public IModuleInterface
{
	virtual void StartupModule() override
	{
		UToolsetRegistry::RegisterToolsetClass(UTacticalEditorAutomationToolset::StaticClass());
		UToolsetRegistry::RegisterToolsetClass(UTacticalAnimAuthoringToolset::StaticClass());
		UToolsetRegistry::RegisterToolsetClass(UTacticalRuntimeAnimInspectionToolset::StaticClass());
	}

	virtual void ShutdownModule() override
	{
		// Ensure no capture delegate or continuous input injection outlives the module.
		UTacticalRuntimeAnimInspectionToolset::ShutdownAllSessions();
		UToolsetRegistry::UnregisterToolsetClass(UTacticalRuntimeAnimInspectionToolset::StaticClass());
		UToolsetRegistry::UnregisterToolsetClass(UTacticalAnimAuthoringToolset::StaticClass());
		UToolsetRegistry::UnregisterToolsetClass(UTacticalEditorAutomationToolset::StaticClass());
	}
};

#undef LOCTEXT_NAMESPACE

IMPLEMENT_MODULE(FTacticalEditorAutomationModule, TacticalEditorAutomation)
