// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class TacticalMovement : ModuleRules
{
	public TacticalMovement(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"TacticalMovement",
			"TacticalMovement/Variant_Platforming",
			"TacticalMovement/Variant_Platforming/Animation",
			"TacticalMovement/Variant_Combat",
			"TacticalMovement/Variant_Combat/AI",
			"TacticalMovement/Variant_Combat/Animation",
			"TacticalMovement/Variant_Combat/Gameplay",
			"TacticalMovement/Variant_Combat/Interfaces",
			"TacticalMovement/Variant_Combat/UI",
			"TacticalMovement/Variant_SideScrolling",
			"TacticalMovement/Variant_SideScrolling/AI",
			"TacticalMovement/Variant_SideScrolling/Gameplay",
			"TacticalMovement/Variant_SideScrolling/Interfaces",
			"TacticalMovement/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
