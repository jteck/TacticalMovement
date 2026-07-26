// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalEditorAutomationToolset.h"

#include "Editor.h"
#include "Containers/Ticker.h"
#include "HAL/PlatformTime.h"
#include "Subsystems/AssetEditorSubsystem.h"
#include "UObject/Object.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectGlobals.h"

#include "ToolsetRegistry/ToolCallAsyncResultVoid.h"

namespace TacticalEditorAutomation
{
	// Bounded timeouts (seconds) for the deferred open/close confirmation polls.
	static constexpr double OpenTimeoutSeconds = 20.0;
	static constexpr double CloseTimeoutSeconds = 15.0;

	// Resolves a package/object path to a loaded UObject. Loading the asset is safe;
	// it is the asset-editor *window* creation that must be deferred, not the load.
	static UObject* ResolveAsset(const FString& AssetPath)
	{
		return StaticLoadObject(UObject::StaticClass(), nullptr, *AssetPath);
	}

	// True if the given asset currently has an open asset editor.
	static bool IsAssetOpen(UAssetEditorSubsystem* Subsystem, UObject* Asset)
	{
		if (!Subsystem || !Asset)
		{
			return false;
		}
		return Subsystem->GetAllEditedAssets().Contains(Asset);
	}
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::OpenAssetEditorDeferred(const FString& AssetPath)
{
	UToolCallAsyncResultVoid* Result = NewObject<UToolCallAsyncResultVoid>();

	if (!GEditor)
	{
		Result->SetError(TEXT("Editor not found."));
		return Result;
	}

	UObject* Asset = TacticalEditorAutomation::ResolveAsset(AssetPath);
	if (!Asset)
	{
		Result->SetError(FString::Printf(TEXT("%s is not a valid asset path."), *AssetPath));
		return Result;
	}

	// Defer the actual OpenEditorForAsset call and confirmation poll to the core
	// ticker so the window is created on a normal game-thread tick, not inside the
	// MCP tool-call handler (see class comment for the deadlock rationale). A strong
	// reference keeps the loaded asset alive across the deferral so GC cannot reclaim
	// it mid-operation.
	TStrongObjectPtr<UToolCallAsyncResultVoid> StrongResult(Result);
	TStrongObjectPtr<UObject> StrongAsset(Asset);
	FString PathCopy = AssetPath;

	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[StrongResult, StrongAsset, PathCopy, bOpenRequested = false, StartTime = FPlatformTime::Seconds()](float) mutable -> bool
		{
			UAssetEditorSubsystem* Subsystem = GEditor ? GEditor->GetEditorSubsystem<UAssetEditorSubsystem>() : nullptr;
			if (!Subsystem)
			{
				StrongResult->SetError(TEXT("Asset editor subsystem not available."));
				StrongResult.Reset();
				return false;
			}

			// First tick: issue the (deferred) open request exactly once and check its result.
			if (!bOpenRequested)
			{
				bOpenRequested = true;
				if (!Subsystem->OpenEditorForAsset(StrongAsset.Get()))
				{
					StrongResult->SetError(FString::Printf(
						TEXT("OpenEditorForAsset returned false for: %s"), *PathCopy));
					StrongResult.Reset();
					return false;
				}
				return true; // poll for confirmation on subsequent ticks
			}

			// Confirmation: the asset appears in the open-assets list.
			if (TacticalEditorAutomation::IsAssetOpen(Subsystem, StrongAsset.Get()))
			{
				StrongResult->SetCompleted();
				StrongResult.Reset();
				return false;
			}

			if (FPlatformTime::Seconds() - StartTime > TacticalEditorAutomation::OpenTimeoutSeconds)
			{
				StrongResult->SetError(FString::Printf(
					TEXT("Timed out confirming open asset editor for: %s"), *PathCopy));
				StrongResult.Reset();
				return false;
			}

			return true; // keep polling
		}));

	return Result;
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::CloseAssetEditorDeferred(const FString& AssetPath)
{
	UToolCallAsyncResultVoid* Result = NewObject<UToolCallAsyncResultVoid>();

	if (!GEditor)
	{
		Result->SetError(TEXT("Editor not found."));
		return Result;
	}

	UObject* Asset = TacticalEditorAutomation::ResolveAsset(AssetPath);
	if (!Asset)
	{
		Result->SetError(FString::Printf(TEXT("%s is not a valid asset path."), *AssetPath));
		return Result;
	}

	// If nothing is open for this asset, complete immediately (idempotent close).
	UAssetEditorSubsystem* Subsystem = GEditor->GetEditorSubsystem<UAssetEditorSubsystem>();
	if (!TacticalEditorAutomation::IsAssetOpen(Subsystem, Asset))
	{
		Result->SetCompleted();
		return Result;
	}

	// Defer the close to the core ticker, then poll until it leaves the open list.
	// A strong reference keeps the asset alive across the deferral.
	TStrongObjectPtr<UToolCallAsyncResultVoid> StrongResult(Result);
	TStrongObjectPtr<UObject> StrongAsset(Asset);
	FString PathCopy = AssetPath;

	FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
		[StrongResult, StrongAsset, PathCopy, bCloseRequested = false, StartTime = FPlatformTime::Seconds()](float) mutable -> bool
		{
			UAssetEditorSubsystem* Subsystem = GEditor ? GEditor->GetEditorSubsystem<UAssetEditorSubsystem>() : nullptr;
			if (!Subsystem)
			{
				StrongResult->SetError(TEXT("Asset editor subsystem not available."));
				StrongResult.Reset();
				return false;
			}

			// First tick: request the close exactly once. Never saves the asset.
			if (!bCloseRequested)
			{
				bCloseRequested = true;

				// Already gone (e.g. closed elsewhere between request and tick): goal met.
				if (!TacticalEditorAutomation::IsAssetOpen(Subsystem, StrongAsset.Get()))
				{
					StrongResult->SetCompleted();
					StrongResult.Reset();
					return false;
				}

				const int32 NumClosed = Subsystem->CloseAllEditorsForAsset(StrongAsset.Get());
				// Inconsistent: the asset was reported open yet nothing was closed and it
				// is still open. Report rather than polling silently until timeout.
				if (NumClosed == 0 && TacticalEditorAutomation::IsAssetOpen(Subsystem, StrongAsset.Get()))
				{
					StrongResult->SetError(FString::Printf(
						TEXT("CloseAllEditorsForAsset closed 0 editors but asset is still open: %s"), *PathCopy));
					StrongResult.Reset();
					return false;
				}
				return true; // poll for confirmation on subsequent ticks
			}

			// Confirmation: the asset no longer appears in the open-assets list.
			if (!TacticalEditorAutomation::IsAssetOpen(Subsystem, StrongAsset.Get()))
			{
				StrongResult->SetCompleted();
				StrongResult.Reset();
				return false;
			}

			if (FPlatformTime::Seconds() - StartTime > TacticalEditorAutomation::CloseTimeoutSeconds)
			{
				StrongResult->SetError(FString::Printf(
					TEXT("Timed out confirming close of asset editor for: %s"), *PathCopy));
				StrongResult.Reset();
				return false;
			}

			return true; // keep polling
		}));

	return Result;
}
