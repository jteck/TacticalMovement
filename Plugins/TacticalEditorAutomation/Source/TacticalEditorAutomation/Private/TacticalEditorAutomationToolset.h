// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"

#include "ToolsetRegistry/ToolsetDefinition.h"

#include "TacticalEditorAutomationToolset.generated.h"

class UToolCallAsyncResultVoid;

/**
 * Editor-only AI toolset for agent-driven asset-editor lifecycle control.
 *
 * Both tools defer the actual asset-editor window open/close onto a later editor
 * tick (via FTSTicker) rather than performing it synchronously inside the MCP
 * tool-call handler. Synchronous asset-editor window creation from the tool-call
 * tick is the leading explanation for the macOS Slate deadlock observed when
 * calling the stock EditorAppToolset::OpenEditorForAsset (this remains an
 * inference until validated). Deferring the window operation to the core ticker
 * lets the tool call return immediately and the window is created/closed on a
 * normal game-thread tick, then the async result is completed once the editor
 * subsystem's open-asset list reflects the change.
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
};
