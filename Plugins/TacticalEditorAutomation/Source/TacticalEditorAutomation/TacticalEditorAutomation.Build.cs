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
				"RenderCore",
				"RHI",
				"UnrealEd",
				"EditorSubsystem",
				"ToolsetRegistry",
				"Persona",
				"AnimationEditor",
				"AnimationBlueprintEditor",
				"AnimGraph",
				"AnimGraphRuntime",
				"AssetTools",
				"BlueprintGraph",
				"Kismet",
				"EnhancedInput",
				// Grenade automation tests live in this editor-only module so that their
				// test-only UCLASS (AGrenadeTestWitness) is never compiled into game targets.
				// The edge is one-way: TacticalMovement does not reference this plugin, so
				// depending on it here introduces no circular dependency.
				"TacticalMovement",
			}
			);
	}
}
