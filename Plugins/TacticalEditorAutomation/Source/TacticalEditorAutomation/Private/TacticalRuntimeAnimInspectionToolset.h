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
 *  - Pre-existing gameplay PIE objects (worlds, pawns, meshes, anim instances) are held ONLY by
 *    WEAK references and are never retained past PIE end. STRONG references are limited to
 *    tool-owned transient objects (the pawn-view capture's transient actor / scene-capture
 *    component / render target) and the pending async result; every such transient reference is
 *    RELEASED on every exit path. The finalize delegate and any continuous input injection are
 *    stopped on every exit path (normal, stop, timeout, PIE end, world/component destruction,
 *    missing/replaced instance, tool failure, module shutdown).
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

	/*
	 * Renders ONE non-owner third-person frame of a specific PIE pawn's skeletal mesh and returns it as a
	 * base64 PNG plus identity metadata. It spawns a SEPARATE transient capture actor + USceneCaptureComponent2D
	 * + UTextureRenderTarget2D in the pawn's own PIE world, aims the capture from (pawn location + CameraOffset)
	 * at (pawn location + LookAtOffset), waits a small bounded number of ticker passes (so the world advances a
	 * frame with the capture rig present), then explicitly calls CaptureScene() and synchronizes the render
	 * commands (FlushRenderingCommands) before the game-thread render-target readback, and destroys every
	 * transient object. Because the capture's view owner is NOT the pawn, the pawn's owner-hidden (bOwnerNoSee)
	 * third-person body renders while its owner-only (bOnlyOwnerSee) first-person arms/weapon do NOT -- WITHOUT
	 * any visibility/camera/asset mutation. It NEVER alters the pawn, mesh visibility flags, gameplay camera,
	 * map, assets, config, or play settings, and NEVER saves anything.
	 *
	 * One frame per call (make an ordered burst by calling repeatedly). At most ONE view-capture session may be
	 * active at a time: an overlapping call is rejected up front, before any session is allocated or scheduled.
	 * Rejects (structured error): a view capture already in progress; no PIE world; editor/preview world;
	 * CDO/template; pending-kill objects; pawn not found; mesh not found; mesh not owned by the supplied pawn;
	 * any non-finite offset/FOV/timeout; a camera-to-look-at distance below the minimum (coincident vectors);
	 * dimensions/FOV/offsets/timeout out of the documented bounds. Immediately before capture the session
	 * revalidates that the pawn and mesh are still in the original PIE world, the mesh is still owned by the
	 * pawn and still registered/live, and the stored paths still resolve to those exact objects. Every transient
	 * actor, component, render target, and ticker is destroyed/unregistered on success, failure, timeout, PIE
	 * end, world destruction, and module shutdown.
	 *
	 * Bounds (hard): at most 1 concurrent session; 64 <= Width,Height <= 1920; Width*Height <= 4,000,000;
	 * 5 <= FOV <= 170; each offset component |v| <= 100000 and finite; camera-to-look-at distance >= 1.0;
	 * 0 < TimeoutSeconds <= 60 and finite. The 12 MiB cap applies to the Base64 image DATA string only (its
	 * Len() equals its UTF-8 byte count because Base64 is ASCII); it is NOT a cap on the whole JSON response.
	 * @param PawnPath Object path of the exact PIE pawn/actor to view.
	 * @param MeshComponentPath Object path of that pawn's exact USkeletalMeshComponent (must be owned by PawnPath).
	 * @param CameraOffsetX Camera position offset from the pawn location, X (cm).
	 * @param CameraOffsetY Camera position offset from the pawn location, Y (cm).
	 * @param CameraOffsetZ Camera position offset from the pawn location, Z (cm).
	 * @param LookAtOffsetX Look-at target offset from the pawn location, X (cm).
	 * @param LookAtOffsetY Look-at target offset from the pawn location, Y (cm).
	 * @param LookAtOffsetZ Look-at target offset from the pawn location, Z (cm, e.g. ~90 for chest height).
	 * @param Width Render width in pixels (64..1920).
	 * @param Height Render height in pixels (64..1920).
	 * @param FOV Horizontal field of view in degrees (5..170).
	 * @param TimeoutSeconds Wall-clock ceiling for the capture (0 < t <= 60).
	 * @return JSON: { pawn, mesh, world, frameNumber, worldTimeSeconds, cameraTransform:{location,rotation}, width, height, fov, image:{ mimeType, data } }.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* CapturePIEPawnViewDeferred(const FString& PawnPath, const FString& MeshComponentPath, float CameraOffsetX, float CameraOffsetY, float CameraOffsetZ, float LookAtOffsetX, float LookAtOffsetY, float LookAtOffsetZ, int32 Width, int32 Height, float FOV, float TimeoutSeconds);

	/*
	 * One-shot, read-only attachment/socket introspection for a PIE pawn's weapon presentation (Boundary G).
	 * Resolves the EXACT PIE pawn, its CharacterMesh0 (skeletal) component, and the weapon component (any USceneComponent,
	 * e.g. a static-mesh WeaponMesh), validating world type, pawn/component ownership, registration, and lifecycle.
	 * Returns, using Epic APIs directly and WITHOUT selecting/creating/modifying any socket: the weapon component
	 * class/path and mesh asset; USceneComponent::GetAttachParent() path; GetAttachSocketName(); GetAllSocketNames()
	 * for BOTH the weapon component and CharacterMesh0 (bounded by kMaxSocketNames with a `truncated` flag);
	 * DoesSocketExist(candidate) on each; candidate GetSocketTransform(RTS_World) from each where it exists; the weapon
	 * component's world transform; and the pawn's controller path, IsLocallyControlled(), local Role and RemoteRole.
	 * Rejects (structured error): pawn/component not found; CDO/template; non-PIE (editor/preview) world; component not
	 * owned by the pawn; unregistered/pending-kill; cross-world component; a CandidateSocketName longer than
	 * kMaxPropertyNameLen characters (checked BEFORE any FName is constructed from it). Never mutates or saves anything.
	 * @param PawnPath Object path of the PIE pawn/actor.
	 * @param MeshComponentPath Object path of that pawn's CharacterMesh0 skeletal-mesh component.
	 * @param WeaponComponentPath Object path of the weapon USceneComponent owned by that pawn.
	 * @param CandidateSocketName Optional socket name to test/measure on each component (empty = skip candidate queries).
	 *        When non-empty it must be at most kMaxPropertyNameLen (128) characters, the same bound the
	 *        transform-capture SocketName uses.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* IntrospectPawnWeaponSockets(const FString& PawnPath, const FString& MeshComponentPath, const FString& WeaponComponentPath, const FString& CandidateSocketName);

	/*
	 * Same-frame ENGINE-OWNED projection with an optional annotated non-owner pawn capture (Boundary G).
	 * REUSES CapturePIEPawnViewDeferred's transient capture actor / USceneCaptureComponent2D / render
	 * target, its deferred lifecycle, the single-active-view-capture guard, the render + readback path,
	 * timeout handling, image-size bound, and DestroyViewTransients cleanup. It adds NO second capture
	 * framework. CapturePIEPawnViewDeferred's PUBLIC SIGNATURE AND OUTPUT CONTRACT are unchanged, but its
	 * implementation now runs through that shared driver, so A1 validation MUST include a plain-capture
	 * regression of CapturePIEPawnViewDeferred.
	 *
	 * FRAME-COHERENT EVIDENCE: every projection target is a (component path, socket name) PAIR that is
	 * re-resolved and re-validated INSIDE the rendered capture frame, and each socket's world transform is
	 * read in that same frame. Caller-supplied world coordinates are deliberately NOT accepted, because a
	 * coordinate supplied from outside the frame is not frame-coherent evidence.
	 *
	 * PROJECTION uses ONLY engine APIs, with no hand-rolled camera math:
	 *   USceneCaptureComponent2D::GetCameraView -> FMinimalViewInfo
	 *   UGameplayStatics::CalculateViewProjectionMatricesFromMinimalView -> view/projection/view-projection
	 *   FSceneView::ProjectWorldToScreen with ViewRect (0,0,Width,Height)
	 * Axis endpoints are derived from the socket's own world transform via FTransform::GetUnitAxis scaled by
	 * the explicit AxisLength. There is NO bone-space reconstruction, inferred offset, correction angle,
	 * socket selection, or acceptance verdict of any kind -- this tool measures and reports, it never judges.
	 *
	 * MATRIX SERIALIZATION CONVENTION (documented, not implied): each matrix is emitted as "rows", an array
	 * of 4 arrays of 4 doubles, where rows[i][j] == FMatrix::M[i][j] in Unreal's row-vector convention (a
	 * point is transformed as v * M, and translation lives in row 3).
	 *
	 * ANNOTATION (optional bAnnotate): draws a marker at each projected socket pixel and RGB X/Y/Z axis
	 * lines through Unreal's supported render-target canvas path (UKismetRenderingLibrary::
	 * BeginDrawCanvasToRenderTarget -> UCanvas::K2_DrawBox/K2_DrawLine -> EndDrawCanvasToRenderTarget).
	 * It draws ONLY from the same projection results returned in the JSON, so image and numbers can never
	 * disagree. Exactly ONE image is returned -- the raw render when bAnnotate is false, the annotated render
	 * when it is true -- reported via the `annotated` flag. The approved 12 MiB bound is enforced on the
	 * COMPLETE returned result (whole payload, UTF-8 bytes), not per image. Annotation draws only
	 * coordinates proven inView: a marker only when the socket point is inView, and an axis only when
	 * BOTH its origin and endpoint are inView -- reported projection coordinates are unaffected. If the
	 * canvas cannot be acquired the call fails with a structured error and never reports annotated:true. It never mutates gameplay cameras, pawn
	 * or component visibility, component transforms, assets, maps, config, or play settings, and never saves.
	 *
	 * HARD BOUNDS (all validated BEFORE any expensive render resource is allocated): at most 32 targets;
	 * ComponentPaths and SocketNames must be equal-length and non-empty; each component path <= 512 and each
	 * socket name <= 128 characters, checked BEFORE object/FName resolution; duplicate (component, socket)
	 * pairs rejected; AxisLength finite and within (0, 200] cm; plus the existing dimension (64..1920,
	 * Width*Height <= 4,000,000), FOV (5..170), offset, coincident-camera, timeout (0 < t <= 60), single
	 * concurrent view capture, and 12 MiB Base64 image-data bounds. Rejects malformed, mismatched-length,
	 * duplicate, missing-socket, cross-world, ownership-mismatch, non-PIE/editor/preview, CDO/template,
	 * stale/pending-kill, and concurrent-call cases up front with a structured error.
	 * @param PawnPath Object path of the exact PIE pawn/actor to view.
	 * @param MeshComponentPath Object path of that pawn's exact USkeletalMeshComponent (must be owned by PawnPath).
	 * @param CameraOffsetX Camera position offset from the pawn location, X (cm).
	 * @param CameraOffsetY Camera position offset from the pawn location, Y (cm).
	 * @param CameraOffsetZ Camera position offset from the pawn location, Z (cm).
	 * @param LookAtOffsetX Look-at target offset from the pawn location, X (cm).
	 * @param LookAtOffsetY Look-at target offset from the pawn location, Y (cm).
	 * @param LookAtOffsetZ Look-at target offset from the pawn location, Z (cm).
	 * @param Width Render width in pixels (64..1920).
	 * @param Height Render height in pixels (64..1920).
	 * @param FOV Horizontal field of view in degrees (5..170).
	 * @param TimeoutSeconds Wall-clock ceiling for the capture (0 < t <= 60).
	 * @param ComponentPaths Object paths of the components owning each projection target; must be owned by the pawn and live in its PIE world.
	 * @param SocketNames Socket names, one per entry in ComponentPaths (equal length); each must exist on its paired component.
	 * @param AxisLength Length in cm of the projected basis-axis segments (0 < AxisLength <= 200).
	 * @param bAnnotate True to return the ANNOTATED image INSTEAD OF the raw image, with the socket marker and RGB X/Y/Z axes drawn.
	 * @return JSON: { pawn, mesh, world, frameNumber, worldTimeSeconds, cameraTransform, width, height, fov,
	 *                 axisLength, matrixConvention, viewMatrix:{rows}, projectionMatrix:{rows},
	 *                 viewProjectionMatrix:{rows}, targets:[ { component, socket, socketWorldTransform,
	 *                 projected:{x,y,ok,finite,inFront,inView}, axes:{ x:{...}, y:{...}, z:{...} } ], limits,
	 *                 annotated, image:{mimeType,data} }. Projected points report the engine return value
	 *                 (`ok`) separately from `finite`, `inFront` and `inView`; `inView` requires
	 *                 0 <= x < Width and 0 <= y < Height. Non-finite points are reported with finite:false
	 *                 and zeroed coordinates -- NaN/Inf never reach the JSON or the canvas.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* CapturePIEPawnViewProjectedDeferred(const FString& PawnPath, const FString& MeshComponentPath, float CameraOffsetX, float CameraOffsetY, float CameraOffsetZ, float LookAtOffsetX, float LookAtOffsetY, float LookAtOffsetZ, int32 Width, int32 Height, float FOV, float TimeoutSeconds, const TArray<FString>& ComponentPaths, const TArray<FString>& SocketNames, float AxisLength, bool bAnnotate);

	/*
	 * Frame-coherent world-transform capture (Boundary G). REUSES the existing capture-session lifecycle and the same
	 * OnBoneTransformsFinalized callback as StartLinkedAnimInstanceCapture (no second session framework); collect and
	 * dispose with StopLinkedAnimInstanceCapture(sessionId). On each completed frame of the named CharacterMesh0 it
	 * serializes RAW values from Epic APIs only: transform-source GetSocketTransform(explicitSocket, RTS_World); the
	 * transform-source component world transform; APawn::GetBaseAimRotation(); the pawn actor rotation; the capsule
	 * component world rotation; the controller path; IsLocallyControlled(); local Role/RemoteRole; plus the existing
	 * frame number and world time. It performs NO bone-space reconstruction, muzzle offsets, axis assumptions,
	 * correction angles, acceptance tolerances, or socket selection. Guards: the explicit socket must exist on the
	 * transform-source component; all components must belong to the supplied pawn; editor/preview worlds, CDOs/templates,
	 * stale/cross-world objects, ownership mismatch, ambiguous/absent linked layer, and host-class mismatch are rejected.
	 * The capsule/root component that supplies capsuleWorldRotation is validated to the SAME standard as the transform
	 * source -- live, non-template, registered, owned by the supplied pawn, and in the same PIE world -- both at session
	 * start and again before every sample. Identity (mesh host, linked layer, transform-source and capsule
	 * ownership/registration/world, socket existence) is revalidated every sampled frame, and any drift stops the session
	 * cleanly with a structured reason BEFORE sampling; the existing sample/timeout/result-size limits and cleanup
	 * behavior apply. Never saves or mutates state.
	 * @param PawnPath Object path of the PIE pawn/actor that owns every component below.
	 * @param MeshComponentPath Object path of the CharacterMesh0 skeletal-mesh component whose finalized frames drive sampling.
	 * @param TransformSourcePath Object path of the component to read the socket/world transform from (weapon component or the mesh itself).
	 * @param SocketName Explicit socket name on the transform-source component (never assumed/selected by the tool).
	 * @param HostClassPath Generated-class or AnimBlueprint path the mesh host AnimInstance must be (or derive from).
	 * @param LayerClassPath Generated-class or AnimBlueprint path selecting the single linked layer instance.
	 * @param MaxSamples Maximum completed-frame samples to record (1..kMaxSamplesLimit).
	 * @param TimeoutSeconds Wall-clock ceiling after which sampling auto-stops (0 < t <= kMaxTimeoutSeconds).
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultString* StartWeaponSocketTransformCapture(const FString& PawnPath, const FString& MeshComponentPath, const FString& TransformSourcePath, const FString& SocketName, const FString& HostClassPath, const FString& LayerClassPath, int32 MaxSamples, float TimeoutSeconds);

	/** Stops and disposes ALL active capture sessions and any continuous input injection they own.
	 *  Called from module shutdown (and usable as a hard reset). Safe to call with no active state. */
	static void ShutdownAllSessions();
};
