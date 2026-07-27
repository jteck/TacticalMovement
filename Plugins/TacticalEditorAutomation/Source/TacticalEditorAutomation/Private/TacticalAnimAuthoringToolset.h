// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "ToolsetRegistry/ToolsetDefinition.h"

#include "TacticalAnimAuthoringToolset.generated.h"

class UToolCallAsyncResultVoid;
class UToolCallAsyncResultString;

/**
 * Editor-only AI toolset providing the reusable AnimBlueprint / AnimGraph authoring
 * operations that the stock Epic MCP toolsets do not expose: creating AnimBlueprints and
 * Anim Layer Interfaces with an explicit target skeleton, adding animation-layer functions
 * (pose input + typed float inputs + pose output), spawning concrete AnimGraph nodes by
 * validated UClass, and setting linked-anim-layer / blend-space references.
 *
 * These are general-purpose tools (no hard-coded asset names or one-off "build X" command).
 * Every operation is deferred onto a later editor tick, validates its inputs, returns an
 * explicit error on failure, and NEVER saves the asset (the caller must invoke a separate,
 * explicit save). Pin discovery/connection, ordinary property setting, compilation and
 * inspection are intentionally left to the stock BlueprintTools/ObjectTools toolsets.
 */
UCLASS(MinimalAPI)
class UTacticalAnimAuthoringToolset : public UToolsetDefinition
{
	GENERATED_BODY()

public:
	/*
	 * Creates an AnimBlueprint (or Anim Layer Interface) asset bound to an explicit target
	 * skeleton, via UAnimBlueprintFactory + IAssetTools::CreateAsset. Does not save.
	 * @param AssetPath Package path for the new asset, e.g. '/Game/Anims/ABP_Foo'.
	 * @param SkeletonPath Path to the target USkeleton, e.g. '/Game/.../SK_Mannequin'.
	 * @param bAsInterface If true, creates an Anim Layer Interface (BPTYPE_Interface); else a normal AnimBlueprint.
	 * @return The object path of the created AnimBlueprint on success.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* CreateAnimBlueprintDeferred(const FString& AssetPath, const FString& SkeletonPath, bool bAsInterface);

	/*
	 * Adds an animation-layer function graph to an AnimBlueprint/interface: an anim graph
	 * (UAnimationGraph) with an auto-created Output Pose (Root), plus a Linked Input Pose
	 * node carrying one named pose input and the requested typed float inputs. Does not save.
	 * @param BlueprintPath Object path of the AnimBlueprint/interface.
	 * @param FunctionName Name of the layer function/graph, e.g. 'WeaponLocomotion'.
	 * @param PoseInputName Name of the input pose, e.g. 'BasePose'.
	 * @param FloatInputs Names of the typed float inputs, e.g. ['Direction','GroundSpeed','PitchN'].
	 * @return The object path of the created layer graph on success.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* AddAnimLayerFunctionDeferred(const FString& BlueprintPath, const FString& FunctionName, const FString& PoseInputName, const TArray<FString>& FloatInputs);

	/*
	 * Implements an anim layer interface on an AnimBlueprint (FBlueprintEditorUtils::
	 * ImplementNewInterface), so the blueprint provides/overrides the interface's layer
	 * functions. Before mutating, validates: the interface asset is an Anim Layer Interface
	 * (BPTYPE_Interface) with a generated class; both the implementer and the interface have
	 * non-null, compatible target skeletons. Idempotent: if the blueprint already implements the
	 * interface, succeeds without re-adding. Does not save.
	 * @param BlueprintPath Object path of the implementing AnimBlueprint.
	 * @param InterfacePath Object path of the Anim Layer Interface asset.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* ImplementAnimInterfaceDeferred(const FString& BlueprintPath, const FString& InterfacePath);

	/*
	 * Spawns a concrete AnimGraph node of the given UClass into a named graph, using
	 * FGraphNodeCreator (no guessed MCP type-ids). Validates the class derives from
	 * UAnimGraphNode_Base and the graph is an animation graph. Does not save.
	 * @param BlueprintPath Object path of the AnimBlueprint.
	 * @param GraphName Name of the target graph, e.g. 'AnimGraph' or a layer function name.
	 * @param NodeClassPath Class path, e.g. '/Script/AnimGraph.AnimGraphNode_BlendSpacePlayer'.
	 * @param PosX Node X position.
	 * @param PosY Node Y position.
	 * @return The object path of the spawned node on success (use it with stock BlueprintTools to wire pins).
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* SpawnAnimGraphNodeDeferred(const FString& BlueprintPath, const FString& GraphName, const FString& NodeClassPath, int32 PosX, int32 PosY);

	/*
	 * Configures a Linked Anim Layer node: sets its Interface, layer/function name and static
	 * InstanceClass, then reconstructs its pins.
	 *
	 * MECHANISM (NOT a call to SetLayerName): UAnimGraphNode_LinkedAnimLayer::SetLayerName is not
	 * ANIMGRAPH_API-exported (MinimalAPI class) and the node's FunctionReference member is protected,
	 * so this tool cannot call/link through SetLayerName. Instead it sets Node.Layer and replicates
	 * SetLayerName's remaining effect by writing the reflected `FunctionReference` UPROPERTY (an
	 * FMemberReference) via reflection + the public FMemberReference API (SetExternalMember/
	 * SetSelfMember). ENGINE-VERSION-SENSITIVE ASSUMPTION: this depends on the node still exposing a
	 * UPROPERTY named `FunctionReference` of struct type FMemberReference. If that property is absent
	 * or its type changes in a future engine version, the tool fails clearly and leaves the node
	 * unmodified (all validation, including the reflection guard, runs before any mutation).
	 *
	 * Before mutating, validates: the node is a Linked Anim Layer node; the interface asset is an
	 * Anim Layer Interface with a generated class; the external AnimBP implements that interface and
	 * shares a compatible target skeleton with the host; and the requested layer function exists.
	 * Pass an empty InstanceClassPath to leave it as a 'self' layer. Does not save.
	 * @param NodePath Object path of the UAnimGraphNode_LinkedAnimLayer node.
	 * @param InterfacePath Object path of the Anim Layer Interface (its generated class is used).
	 * @param LayerName The layer function name, e.g. 'WeaponLocomotion'.
	 * @param InstanceClassPath Object path of the external implementing AnimBlueprint (its generated class), or empty for self.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetLinkedAnimLayerDeferred(const FString& NodePath, const FString& InterfacePath, const FString& LayerName, const FString& InstanceClassPath);

	/*
	 * Sets the animation asset (BlendSpace or AimOffset) on an asset-player AnimGraph node via
	 * the public UAnimGraphNode_AssetPlayerBase::SetAnimationAsset (never writes the private
	 * runtime field), then reconstructs pins. SetAnimationAsset checks asset class but NOT
	 * skeleton, so this first rejects a skeleton mismatch against the owning AnimBlueprint's
	 * target skeleton. It then assigns, reads the value back, and on failure restores the previous
	 * asset (verifying the restoration) so a failed call leaves the node unchanged. Error text
	 * distinguishes wrong node/asset class, skeleton mismatch, assignment/readback failure, and
	 * restoration failure. Does not save.
	 * @param NodePath Object path of a BlendSpace player / RotationOffsetBlendSpace node.
	 * @param AnimationAssetPath Path of the UAnimationAsset (BlendSpace/AimOffset) to assign.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetAnimGraphNodeAnimationAssetDeferred(const FString& NodePath, const FString& AnimationAssetPath);
};
