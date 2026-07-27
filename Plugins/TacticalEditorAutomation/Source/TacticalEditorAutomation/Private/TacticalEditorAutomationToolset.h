// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "ToolsetRegistry/ToolsetDefinition.h"

#include "TacticalEditorAutomationToolset.generated.h"

class UToolCallAsyncResultVoid;

/**
 * Editor-only AI toolset for agent-driven asset-editor lifecycle and preview control.
 *
 * Window open/close and preview operations are deferred onto a later editor tick
 * (via FTSTicker) rather than performed synchronously inside the MCP tool-call
 * handler. Synchronous asset-editor window creation from the tool-call tick is the
 * leading explanation for the macOS Slate deadlock observed when calling the stock
 * EditorAppToolset::OpenEditorForAsset (this remains an inference until validated).
 * Deferring the work to the core ticker lets the tool call return immediately and
 * the window/preview op run on a normal game-thread tick.
 *
 * The preview-control tools (Family A) act on an ALREADY-OPEN Persona editor. The
 * cast from the IAssetEditorInstance returned by FindEditorForAsset to the concrete
 * Persona editor interface is guarded by BOTH the expected asset class AND the
 * editor's verified GetEditorName value; the resulting static_cast is only
 * conditionally validated by those guards, never assumed universally type-safe.
 */
UCLASS(MinimalAPI)
class UTacticalEditorAutomationToolset : public UToolsetDefinition
{
	GENERATED_BODY()

public:
	/*
	 * Opens an asset editor for the specified asset without blocking, by scheduling
	 * the open on a later editor tick. Use this instead of the synchronous
	 * OpenEditorForAsset when driving the editor over MCP, to avoid the macOS Slate
	 * window-creation deadlock. Completes once the asset appears in the open-assets
	 * list, or errors on a bounded timeout. Never modifies or saves the asset.
	 * @param AssetPath The package path of the asset to open, e.g. '/Game/Meshes/SM_Cube'.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* OpenAssetEditorDeferred(const FString& AssetPath);

	/*
	 * Closes any open asset editors for the specified asset without blocking, by
	 * scheduling the close on a later editor tick. Completes once the asset no
	 * longer appears in the open-assets list, or errors on a bounded timeout.
	 * Never saves the asset.
	 * @param AssetPath The package path of the asset to close, e.g. '/Game/Meshes/SM_Cube'.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* CloseAssetEditorDeferred(const FString& AssetPath);

	/*
	 * Frames the preview mesh in the open Persona editor's viewport(s) (equivalent to
	 * "focus selected"). Works for AnimSequence, BlendSpace, AimOffset and AnimBlueprint
	 * editors. The editor must already be open. Never modifies or saves the asset.
	 * @param AssetPath The package path of the open asset, e.g. '/Game/Anims/MyAnim'.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* FocusPreviewMesh(const FString& AssetPath);

	/*
	 * Plays or pauses the preview animation in the open Persona editor. Applies to
	 * AnimSequence/BlendSpace/AimOffset editors (single-node preview). Not supported
	 * for AnimBlueprint editors (the preview runs the compiled Anim Blueprint, not a
	 * single-node timeline). The editor must already be open. Never saves the asset.
	 * @param AssetPath The package path of the open asset.
	 * @param bPlaying True to play, false to pause.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetPreviewPlaying(const FString& AssetPath, bool bPlaying);

	/*
	 * Pauses and scrubs the open preview animation to an absolute time in seconds.
	 * Errors if Seconds is outside [0, animation length]. Single-node preview editors
	 * only (not AnimBlueprint). The editor must already be open. Never saves the asset.
	 * @param AssetPath The package path of the open asset.
	 * @param Seconds Absolute preview time in seconds, within [0, length].
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetPreviewTimeSeconds(const FString& AssetPath, float Seconds);

	/*
	 * Pauses and scrubs the open preview animation to a normalized time in [0,1]
	 * (clamped). 0 = start, 1 = end. Single-node preview editors only (not
	 * AnimBlueprint). The editor must already be open. Never saves the asset.
	 * @param AssetPath The package path of the open asset.
	 * @param Alpha Normalized preview time; values outside [0,1] are clamped.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetPreviewTimeNormalized(const FString& AssetPath, float Alpha);

	/*
	 * Sets the BlendSpace/AimOffset preview blend coordinate (X = horizontal axis,
	 * e.g. aim yaw or direction; Y = vertical axis, e.g. aim pitch or speed). Errors
	 * if the asset is not a BlendSpace (AimOffset is a BlendSpace subtype). Single-node
	 * preview editors only. The editor must already be open. Never saves the asset.
	 * @param AssetPath The package path of the open BlendSpace/AimOffset asset.
	 * @param X Horizontal blend-space input value.
	 * @param Y Vertical blend-space input value.
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetPreviewBlendPosition(const FString& AssetPath, float X, float Y);

	/*
	 * Sets how the open Persona preview consumes root motion (preview-only; never modifies
	 * the asset, its root-motion settings, root lock, or import data). Use "Ignore" to keep
	 * the character in place while screening a full gait cycle so root-motion translation
	 * does not carry it out of frame; "Loop" consumes root motion continually; "LoopAndReset"
	 * resets to origin each loop. The editor must already be open.
	 * @param AssetPath The package path of the open asset.
	 * @param Mode One of "Ignore", "Loop", or "LoopAndReset" (case-insensitive).
	 */
	UFUNCTION(meta = (AICallable))
	static UToolCallAsyncResultVoid* SetPreviewRootMotionMode(const FString& AssetPath, const FString& Mode);
};
