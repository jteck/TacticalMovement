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

	/*
	 * Binds a Use Cached Pose node to a Save Cached Pose node in the same animation graph, so the
	 * cached pose (evaluated once at the Save node) is consumed by the Use node. This replicates the
	 * association Epic's editor sets when you pick a cache from the Use Cached Pose menu action -- an
	 * operation the stock MCP toolsets cannot perform (SaveCachedPoseNode is a non-editable UPROPERTY,
	 * so ObjectTools cannot set it, and there is no cache-specific create_node action).
	 *
	 * SCOPE (conservative, first reusable version): both nodes must live in the SAME named graph of
	 * the SAME AnimBlueprint. Cross-subgraph / cross-layer cached-pose arrangements Epic may otherwise
	 * permit are intentionally NOT supported and are rejected.
	 *
	 * Resolves each node by stable identity within the graph: the node's NodeGuid string (preferred),
	 * or its object name / full object path. Requires exactly one match of the correct node class.
	 *
	 * Validation (all before any mutation): AnimBlueprint + graph load; exactly one UseCachedPose and
	 * one SaveCachedPose resolved in that graph; both belong to this AnimBlueprint/graph; the Save
	 * node's CacheName is nonempty and unique within the graph; the Save node's pose input is wired.
	 * Idempotency: if the Use node is already bound to the requested Save node, returns a successful
	 * readback WITHOUT dirtying anything; if it is bound to a DIFFERENT Save node, rejects (no silent
	 * rebind). Mutation is minimal (Modify the use node, assign SaveCachedPoseNode, notify the graph,
	 * mark the Blueprint structurally modified); it never calls ReconstructNode and never mutates the
	 * Save node. Does not save.
	 * @param BlueprintPath Object/package path of the AnimBlueprint owning both nodes.
	 * @param GraphName Name of the animation graph containing both nodes (e.g. 'AnimGraph').
	 * @param UseNodeId NodeGuid / object name / object path of the UAnimGraphNode_UseCachedPose.
	 * @param SaveNodeId NodeGuid / object name / object path of the UAnimGraphNode_SaveCachedPose.
	 * @return JSON: { blueprint, graph, useNodeId, useNodePath, saveNodeId, saveNodePath, cacheName, idempotent }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* BindUseCachedPoseDeferred(const FString& BlueprintPath, const FString& GraphName, const FString& UseNodeId, const FString& SaveNodeId);

	/*
	 * Read-only companion to BindUseCachedPoseDeferred: reports the Save Cached Pose node (if any)
	 * currently associated with a Use Cached Pose node, plus that Save node's CacheName, so a binding
	 * can be verified after save and cold restart. Never mutates, never saves.
	 * @param BlueprintPath Object/package path of the AnimBlueprint owning the node.
	 * @param GraphName Name of the animation graph containing the Use node.
	 * @param UseNodeId NodeGuid / object name / object path of the UAnimGraphNode_UseCachedPose.
	 * @return JSON: { blueprint, graph, useNodeId, useNodePath, bound, saveNodeId, saveNodePath, cacheName }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* GetUseCachedPoseBinding(const FString& BlueprintPath, const FString& GraphName, const FString& UseNodeId);

	/*
	 * Read-only enumeration of a UStaticMesh's sockets. Returns each socket's name and relative
	 * location/rotation/scale, the mesh's total socket count, and how many were serialized.
	 * Never mutates, never dirties, never saves.
	 * Rejects: empty/unresolvable path; an asset that is not exactly a UStaticMesh; CDO/template;
	 * transient or pending-kill objects.
	 * BOUNDED OUTPUT (this is a reusable AICallable tool, so the result can never be unlimited):
	 * at most 256 sockets are serialized AND at most 262144 bytes of socket-array JSON; whichever
	 * bound is reached first stops serialization and sets `truncated` true. `socketCount` always
	 * reports the mesh's true total, and the applied limits are echoed in `limits`.
	 * @param AssetPath Object/package path of the static mesh, e.g. '/Game/Weapons/Rifle/Meshes/SM_Rifle'.
	 * @return JSON: { asset, socketCount, returned, truncated, limits:{ maxSocketsReturned, maxSocketsJsonBytes },
	 *                 sockets:[ { name, relativeLocation, relativeRotation, relativeScale } ] }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* GetStaticMeshSockets(const FString& AssetPath);

	/*
	 * Adds ONE new UStaticMeshSocket to a UStaticMesh, mirroring the editor's own SSocketManager
	 * sequence: FScopedTransaction -> NewObject -> SetFlags(RF_Transactional) -> Mesh->PreEditChange(nullptr)
	 * -> Mesh->AddSocket -> Mesh->PostEditChange() -> Mesh->MarkPackageDirty().
	 *
	 * ALL validation runs BEFORE any mutation and before the transaction opens: the asset must resolve,
	 * load, and be exactly a UStaticMesh (not a CDO/template/transient/pending-kill); the socket name must
	 * be non-empty, trimmed-non-empty, within the name-length bound, and must NOT already exist on the mesh
	 * (duplicates are rejected, never silently rebound); every transform component must be finite and within
	 * the documented bounds. A rejected call mutates nothing and leaves the package's prior dirty state
	 * EXACTLY as it was.
	 *
	 * EXACT LIMITS: socket name <= 128 characters, non-empty after trimming; |relative location| <= 10000 cm
	 * per axis; |relative rotation| <= 360 degrees per component (ROTATION POLICY: callers author normalized
	 * rotations -- the tool validates the supplied value and never normalizes, wraps, or rewrites it.
	 * All rotator comparisons -- CAS, changed-property detection, and both readbacks -- are RAW
	 * COMPONENT-WISE absolute-delta comparisons, never FRotator::Equals, so wrap-equivalent components
	 * such as 0 and 360 degrees are treated as DIFFERENT, consistent with preserving caller values);
	 * |relative scale| per component within [0.001, 100]; readback/expected-transform tolerance 0.001.
	 *
	 * Readback and rollback happen INSIDE the still-live FScopedTransaction. The stored socket must be the
	 * EXACT object this call created (pointer identity), not merely a same-named socket. On any mismatch the
	 * created socket is removed through the mesh's PreEditChange/RemoveSocket/PostEditChange path, the
	 * transaction is CANCELLED so no undo entry can resurrect the failed mutation, the package's prior dirty
	 * state is restored, and provenance for that key is cleared.
	 *
	 * This tool NEVER SAVES. The package is left dirty in memory only; persisting requires a separate
	 * authorized save step. Discarding an unsaved candidate is the approved no-save editor close.
	 * Sockets added by this tool are tracked for the editor session by EXACT OBJECT IDENTITY (a weak
	 * pointer to the created socket), so SetStaticMeshSocketTransformDeferred can distinguish them from
	 * pre-existing sockets. A destroyed, undone, or same-named REPLACEMENT socket is a different object,
	 * goes stale, and is never trusted.
	 * @param AssetPath Object/package path of the static mesh.
	 * @param SocketName Name of the new socket; must not already exist on the mesh.
	 * @param LocationX Relative location X (cm).
	 * @param LocationY Relative location Y (cm).
	 * @param LocationZ Relative location Z (cm).
	 * @param Pitch Relative rotation pitch (degrees).
	 * @param Yaw Relative rotation yaw (degrees).
	 * @param Roll Relative rotation roll (degrees).
	 * @param ScaleX Relative scale X.
	 * @param ScaleY Relative scale Y.
	 * @param ScaleZ Relative scale Z.
	 * @return JSON: { asset, socketName, added, relativeLocation, relativeRotation, relativeScale, socketCount, packageDirty }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* AddStaticMeshSocketDeferred(const FString& AssetPath, const FString& SocketName, float LocationX, float LocationY, float LocationZ, float Pitch, float Yaw, float Roll, float ScaleX, float ScaleY, float ScaleZ);

	/*
	 * Sets the relative transform of an EXISTING UStaticMeshSocket, mirroring the editor's own socket
	 * property-change sequence: FScopedTransaction -> Socket->PreEditChange(property) -> assign ->
	 * Socket->PostEditChangeProperty(...) -> Mesh->MarkPackageDirty().
	 *
	 * Guard against silently overwriting an unexpected socket: the CAS bypass applies ONLY when this tool
	 * added the socket in the CURRENT editor session AND the tracked weak pointer is still valid AND equals
	 * the socket the mesh currently returns for that name. Otherwise the caller MUST supply
	 * bExpectPriorTransform=true together with the socket's COMPLETE expected prior transform, and every
	 * component must match within 0.001. A same-named replacement never inherits trust. A stale or
	 * mismatched expected transform is rejected with ZERO mutation.
	 *
	 * EXACT LIMITS: identical to AddStaticMeshSocketDeferred (name <= 128 chars; |location| <= 10000 cm;
	 * |rotation| <= 360 degrees per component, callers author normalized rotations; |scale| per component
	 * within [0.001, 100]; tolerance 0.001). The expected prior transform is validated to the same bounds.
	 *
	 * TRUE NO-OP: if the requested location, rotation, and scale already match the stored socket
	 * component-wise within 0.001, the call returns updated:false, noOp:true, changedProperties:[] WITHOUT
	 * opening a transaction and without calling PreEditChange/Modify/PostEditChangeProperty/MarkPackageDirty,
	 * so NO undo entry is created and the package's prior dirty state is preserved exactly. The provenance /
	 * expected-prior-transform guard is still enforced before the no-op determination.
	 *
	 * All validation runs before any mutation; a rejected call preserves the package's prior dirty state.
	 * Readback and rollback happen INSIDE the still-live FScopedTransaction and require the stored socket to
	 * be the EXACT original object; on mismatch that object's original transform is restored with proper edit
	 * notification, the transaction is CANCELLED so no undo entry survives, the prior dirty state is restored,
	 * and provenance that can no longer be trusted is cleared. NEVER SAVES.
	 * @param AssetPath Object/package path of the static mesh.
	 * @param SocketName Name of the existing socket to modify.
	 * @param LocationX New relative location X (cm).
	 * @param LocationY New relative location Y (cm).
	 * @param LocationZ New relative location Z (cm).
	 * @param Pitch New relative rotation pitch (degrees).
	 * @param Yaw New relative rotation yaw (degrees).
	 * @param Roll New relative rotation roll (degrees).
	 * @param ScaleX New relative scale X.
	 * @param ScaleY New relative scale Y.
	 * @param ScaleZ New relative scale Z.
	 * @param bExpectPriorTransform True to supply the expected prior transform (required unless this tool added the socket this session).
	 * @param ExpectLocationX Expected prior relative location X.
	 * @param ExpectLocationY Expected prior relative location Y.
	 * @param ExpectLocationZ Expected prior relative location Z.
	 * @param ExpectPitch Expected prior relative rotation pitch.
	 * @param ExpectYaw Expected prior relative rotation yaw.
	 * @param ExpectRoll Expected prior relative rotation roll.
	 * @param ExpectScaleX Expected prior relative scale X.
	 * @param ExpectScaleY Expected prior relative scale Y.
	 * @param ExpectScaleZ Expected prior relative scale Z.
	 * @return JSON: { asset, socketName, updated, matchedBy, relativeLocation, relativeRotation, relativeScale, packageDirty }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* SetStaticMeshSocketTransformDeferred(const FString& AssetPath, const FString& SocketName, float LocationX, float LocationY, float LocationZ, float Pitch, float Yaw, float Roll, float ScaleX, float ScaleY, float ScaleZ, bool bExpectPriorTransform, float ExpectLocationX, float ExpectLocationY, float ExpectLocationZ, float ExpectPitch, float ExpectYaw, float ExpectRoll, float ExpectScaleX, float ExpectScaleY, float ExpectScaleZ);
};
