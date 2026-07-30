// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "ToolsetRegistry/ToolsetDefinition.h"

#include "TacticalRuntimeAnimInspectionToolset.generated.h"

class UToolCallAsyncResultString;

/**
 * Editor-only AI toolset for runtime (PIE) animation inspection: it enumerates live
 * Play-In-Editor skeletal-mesh / host-AnimInstance / linked-layer-instance triples, and
 * captures frame-coherent parity samples of named scalar properties from a host AnimInstance
 * and one of its linked anim-layer instances -- read from the SAME skeletal-mesh component,
 * inside a single OnBoneTransformsFinalized callback (i.e. one completed animation frame).
 *
 * It exists because the stock editor MCP surface cannot reach the PIE runtime pawn / anim
 * instances, cannot pause/single-step, and cannot execute console commands (no GetAll). This
 * toolset is the frame-synchronized, unambiguously-paired evidence source the E0 gate needs.
 *
 * INVARIANTS (all tools):
 *  - Read-only w.r.t. UObjects and assets: it NEVER writes a property value (except Enhanced
 *    Input injection, which drives the game's REAL input path -- it never forces readiness
 *    properties or animation variables), and it NEVER saves an asset.
 *  - Editor-only module (compiled only into the editor target; not runtime/shipping).
 *  - All UObject / FProperty access happens on the game thread.
 *  - PIE worlds only: Editor / EditorPreview / GamePreview worlds, CDOs/templates, preview
 *    AnimInstances, unregistered/pending-kill components are rejected.
 *  - Capture state is module-owned and holds only WEAK references to PIE UObjects; it never
 *    retains a PIE object past PIE end. The finalize delegate and any continuous input
 *    injection are stopped on every exit path (normal, stop, timeout, PIE end, world/component
 *    destruction, missing/replaced instance, tool failure, module shutdown).
 *  - This toolset embeds NO E0 tolerances or pass/fail logic; it returns raw paired readings.
 */
UCLASS(MinimalAPI)
class UTacticalRuntimeAnimInspectionToolset : public UToolsetDefinition
{
	GENERATED_BODY()

public:
	/*
	 * Enumerates, across active PIE worlds only, every registered skeletal-mesh component and its
	 * main AnimInstance plus that component's linked anim-layer instances. Read-only; never mutates
	 * or saves. Rejects editor/preview worlds, templates/CDOs, and unregistered/pending-kill
	 * components. Use the returned mesh-component / pawn paths and host/layer classes to drive a
	 * capture with StartLinkedAnimInstanceCapture.
	 * @return JSON: { pieWorlds:[ { world, timeSeconds, meshes:[ { owner, meshComponent,
	 *         hostAnimInstance, hostClass, linkedLayers:[ { instance, class } ] } ] } ] }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* ListPIEAnimInstancePairs();

	/*
	 * Resolves the EXACT PIE-world skeletal-mesh component named by MeshComponentPath, verifies it is
	 * owned by the expected pawn (PawnPath), and pairs its main (host) AnimInstance with the single
	 * linked anim-layer instance of the requested layer class ON THAT SAME COMPONENT. Registers an
	 * OnBoneTransformsFinalized delegate so, on every subsequent completed animation frame, the
	 * requested host and layer scalar properties are sampled together (same frame). ALSO installs an
	 * independent module-owned lifecycle/timeout ticker so the capture terminates and unregisters even
	 * if the component never finalizes another frame. Returns a capture-session id IMMEDIATELY; drive
	 * input with DrivePIEInputSequenceDeferred while it runs, then collect with
	 * StopLinkedAnimInstanceCapture. The pawn is NOT required to have only one skeletal-mesh component:
	 * MeshComponentPath selects the intended one unambiguously.
	 *
	 * Separate host/layer property lists (bHostValid lives only on the layer, so request it only there);
	 * within each list, names must be non-empty and unique. Missing / unsupported / wrong-type
	 * properties produce structured per-property read errors and fail that sample (never coerced/written).
	 *
	 * Rejects (structured error): no PIE world; editor/preview world; CDO/template; unregistered or
	 * pending-kill component; mesh not owned by the expected pawn; missing host; host class mismatch;
	 * zero or more-than-one linked layer of the requested class (ambiguous); empty/duplicate property
	 * names; more than 64 properties per side; a property name longer than 128 characters;
	 * MaxSamples/TimeoutSeconds outside the documented hard bounds; an already-active session on
	 * the same mesh component.
	 *
	 * On each finalized frame the session revalidates: mesh still owns the same host instance; the exact
	 * stored layer pointer is still in the mesh's current GetLinkedAnimInstances(); host and layer still
	 * satisfy the expected classes -- otherwise it stops with a structured reason BEFORE sampling.
	 *
	 * Bounds (hard, documented): 1 <= MaxSamples <= 10000; 0 < TimeoutSeconds <= 300; <= 64 properties
	 * per side; property name <= 128 chars; <= 8 MiB accumulated serialized sample JSON per session.
	 * Sampling stops at MaxSamples, TimeoutSeconds, the byte cap (stopReason 'result size limit
	 * reached' -- no partial/truncated sample is stored), or any invalidation (world/component/instance
	 * gone or replaced, PIE end). The stop result reports the configured limits and the accumulated
	 * sample-byte count; data is never silently truncated.
	 * @param MeshComponentPath Object path of the exact PIE USkeletalMeshComponent to capture.
	 * @param PawnPath Expected owner (pawn/actor) object path; must match the component's owner.
	 * @param HostClassPath Generated-class or AnimBlueprint path the host AnimInstance must be (or derive from).
	 * @param LayerClassPath Generated-class or AnimBlueprint path selecting the linked layer instance.
	 * @param HostProperties Scalar property names to sample on the host (float/double/bool only; non-empty, unique).
	 * @param LayerProperties Scalar property names to sample on the layer (float/double/bool only; non-empty, unique).
	 * @param MaxSamples Maximum completed-frame samples to record (1..10000).
	 * @param TimeoutSeconds Wall-clock ceiling after which sampling auto-stops (0 < t <= 300).
	 * @return JSON: { sessionId, world, owner, meshComponent, hostAnimInstance, hostClass, layerInstance, layerClass, hostProperties, layerProperties, maxSamples, timeoutSeconds }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* StartLinkedAnimInstanceCapture(const FString& MeshComponentPath, const FString& PawnPath, const FString& HostClassPath, const FString& LayerClassPath, const TArray<FString>& HostProperties, const TArray<FString>& LayerProperties, int32 MaxSamples, float TimeoutSeconds);

	/*
	 * Unregisters the capture session's finalize delegate (idempotent) and returns every structured
	 * sample collected so far plus session metadata, then disposes the session. Never mutates/saves.
	 * @param SessionId The id returned by StartLinkedAnimInstanceCapture.
	 * @return JSON: { sessionId, active, stopReason, world, owner, meshComponent, hostClass, layerClass,
	 *         sampleCount, samples:[ { frameNumber, worldTimeSeconds, world, owner, meshComponent,
	 *         hostInstance, hostClass, layerInstance, layerClass, host:{name:value}, layer:{name:value},
	 *         readErrors:[ { instance, property, error } ] } ] }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* StopLinkedAnimInstanceCapture(const FString& SessionId);

	/*
	 * Drives the project's REAL Enhanced Input path on a PIE pawn as a bounded, declared sequence so
	 * a capture session observes idle -> transition -> sustained-movement frames: (1) an idle hold,
	 * (2) a bounded press/release of the readiness input action (the actual UInputAction referenced
	 * by the named pawn property), (3) sustained movement via StartContinuousInputInjectionForAction
	 * on the move action for a bounded duration, then StopContinuousInputInjectionForAction. It reads
	 * the pawn's readiness enum and movement speed BEFORE and AFTER to verify the real input handler
	 * changed readiness and that CMC-driven movement produced genuine speed -- it NEVER writes the
	 * readiness property, teleports, or forces animation values. Injection is stopped on every exit
	 * path. Requires a valid PIE pawn with an EnhancedInput local-player subsystem.
	 * @param PawnPath Object path of the PIE pawn/actor.
	 * @param ReadinessActionProperty Name of the pawn UInputAction* property to press (e.g. 'ReadinessMovementReadyAction' or 'ADSAction'); empty to skip.
	 * @param MoveActionProperty Name of the pawn UInputAction* property for movement (e.g. 'MoveAction'); empty to skip movement.
	 * @param MoveX Movement action X value for continuous injection (e.g. 1.0 forward).
	 * @param MoveY Movement action Y value for continuous injection (e.g. 1.0 right).
	 * @param PreMoveIdleSeconds Idle hold before pressing readiness (lets idle frames capture).
	 * @param MoveSeconds Sustained-movement duration (continuous injection window).
	 * @param TimeoutSeconds Overall wall-clock ceiling for the whole sequence (>0).
	 * @return JSON: { pawn, readinessAction, moveAction, readinessBefore, readinessAfter, readinessChanged, speedBefore, speedAfter, speedIncreased, injectionStopped, steps:[...] }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* DrivePIEInputSequenceDeferred(const FString& PawnPath, const FString& ReadinessActionProperty, const FString& MoveActionProperty, float MoveX, float MoveY, float PreMoveIdleSeconds, float MoveSeconds, float TimeoutSeconds);

	/** Stops and disposes ALL active capture sessions and any continuous input injection they own.
	 *  Called from module shutdown (and usable as a hard reset). Safe to call with no active state. */
	static void ShutdownAllSessions();
};
