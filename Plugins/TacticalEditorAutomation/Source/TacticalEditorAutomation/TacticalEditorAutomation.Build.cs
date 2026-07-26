// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class TacticalEditorAutomation : ModuleRules
{
	public TacticalEditorAutomation(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = ModuleRules.PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(
			new string[]
			{
				"Core",
			}
			);

		PrivateDependencyModuleNames.AddRange(
			new string[]
			{
				"CoreUObject",
				"Engine",
				"UnrealEd",
				"EditorSubsystem",
				"ToolsetRegistry",
				"Persona",
				"AnimationEditor",
				"AnimationBlueprintEditor",
			}
			);
	}
}
