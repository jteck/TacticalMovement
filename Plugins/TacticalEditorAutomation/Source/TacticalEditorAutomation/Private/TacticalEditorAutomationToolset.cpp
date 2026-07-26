// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalEditorAutomationToolset.h"

#include "Editor.h"
#include "Containers/Ticker.h"
#include "HAL/PlatformTime.h"
#include "Math/UnrealMathUtility.h"
#include "Subsystems/AssetEditorSubsystem.h"
#include "UObject/Object.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectGlobals.h"

// Persona / animation preview API (all public UE 5.8 headers).
#include "IHasPersonaToolkit.h"
#include "IPersonaToolkit.h"
#include "IPersonaPreviewScene.h"
#include "IAnimationEditor.h"
#include "IAnimationBlueprintEditor.h"
#include "Animation/DebugSkelMeshComponent.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimationAsset.h"
#include "Animation/BlendSpace.h"
#include "Animation/BlendSpace1D.h"
#include "Animation/AnimBlueprint.h"

#include "ToolsetRegistry/ToolCallAsyncResultVoid.h"

namespace TacticalEditorAutomation
{
	// Bounded timeouts (seconds) for the deferred open/close confirmation polls.
	static constexpr double OpenTimeoutSeconds = 20.0;
	static constexpr double CloseTimeoutSeconds = 15.0;

	// Editor GetEditorName() values (== FAssetEditorToolkit::GetToolkitFName()).
	static const FName AnimationEditorName(TEXT("AnimationEditor"));
	static const FName AnimationBlueprintEditorName(TEXT("AnimationBlueprintEditor"));

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

	// Resolved handles for an already-open Persona editor.
	struct FPreviewHandles
	{
		UObject* Asset = nullptr;
		IPersonaToolkit* Toolkit = nullptr;
		UDebugSkelMeshComponent* Component = nullptr;
		UAnimSingleNodeInstance* Single = nullptr; // null for AnimBlueprint previews
	};

	// Resolves the Persona toolkit + preview component for an ALREADY-OPEN editor. The
	// cast from IAssetEditorInstance to the concrete Persona editor interface is guarded
	// by BOTH the expected asset class AND the verified GetEditorName value; only then is
	// the static_cast performed (conditionally validated by those guards, not assumed
	// universally type-safe). When bRequireSingleNode is true, also resolves the
	// single-node preview instance (unavailable for AnimBlueprint previews).
	static bool ResolvePreview(const FString& AssetPath, bool bRequireSingleNode, FPreviewHandles& Out, FString& OutError)
	{
		Out = FPreviewHandles();
		Out.Asset = ResolveAsset(AssetPath);
		if (!Out.Asset)
		{
			OutError = FString::Printf(TEXT("%s is not a valid asset path."), *AssetPath);
			return false;
		}
		UAssetEditorSubsystem* Subsystem = GEditor ? GEditor->GetEditorSubsystem<UAssetEditorSubsystem>() : nullptr;
		if (!Subsystem)
		{
			OutError = TEXT("Asset editor subsystem not available.");
			return false;
		}
		IAssetEditorInstance* Instance = Subsystem->FindEditorForAsset(Out.Asset, /*bFocusIfOpen*/ false);
		if (!Instance)
		{
			OutError = FString::Printf(TEXT("Asset editor is not open for: %s (open it first)."), *AssetPath);
			return false;
		}

		const FName EditorName = Instance->GetEditorName();
		IHasPersonaToolkit* HasToolkit = nullptr;
		if (Out.Asset->IsA<UAnimationAsset>() && EditorName == AnimationEditorName)
		{
			HasToolkit = static_cast<IAnimationEditor*>(Instance);
		}
		else if (Out.Asset->IsA<UAnimBlueprint>() && EditorName == AnimationBlueprintEditorName)
		{
			HasToolkit = static_cast<IAnimationBlueprintEditor*>(Instance);
		}
		else
		{
			OutError = FString::Printf(
				TEXT("Cast guard failed: editor '%s' with asset class '%s' is not a supported Persona editor."),
				*EditorName.ToString(), *Out.Asset->GetClass()->GetName());
			return false;
		}

		Out.Toolkit = &HasToolkit->GetPersonaToolkit().Get();
		Out.Component = Out.Toolkit->GetPreviewMeshComponent();
		if (!Out.Component)
		{
			OutError = TEXT("Preview mesh component unavailable.");
			return false;
		}

		if (bRequireSingleNode)
		{
			Out.Single = Out.Component->GetSingleNodeInstance();
			if (!Out.Single)
			{
				OutError = TEXT("Preview single-node instance unavailable (AnimBlueprint preview or non-single-node preview).");
				return false;
			}
		}
		return true;
	}

	// Forces the preview pose to evaluate at its current state and the viewport(s) to
	// redraw, so the change is visibly applied before the async result completes rather
	// than relying on incidental timing of the next request.
	static void RefreshPreview(const FPreviewHandles& H)
	{
		if (H.Component)
		{
			H.Component->TickAnimation(0.f, /*bNeedsValidRootMotion*/ false);
			H.Component->RefreshBoneTransforms();
		}
		if (H.Toolkit)
		{
			H.Toolkit->GetPreviewScene()->InvalidateViews();
		}
	}

	// Schedules a one-shot game-thread action that produces a void async result.
	// Keeps preview/Slate work off the MCP tool-call (HTTP) tick.
	static UToolCallAsyncResultVoid* RunDeferredVoid(TFunction<bool(FString& /*OutError*/)>&& Action)
	{
		UToolCallAsyncResultVoid* Result = NewObject<UToolCallAsyncResultVoid>();
		if (!GEditor)
		{
			Result->SetError(TEXT("Editor not found."));
			return Result;
		}
		TStrongObjectPtr<UToolCallAsyncResultVoid> StrongResult(Result);
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[StrongResult, Action = MoveTemp(Action)](float) mutable -> bool
			{
				FString Error;
				if (Action(Error))
				{
					StrongResult->SetCompleted();
				}
				else
				{
					StrongResult->SetError(Error);
				}
				StrongResult.Reset();
				return false; // one-shot
			}));
		return Result;
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

// ---- Family A: preview control (operates on an already-open Persona editor) ----

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::FocusPreviewMesh(const FString& AssetPath)
{
	FString Path = AssetPath;
	return TacticalEditorAutomation::RunDeferredVoid(
		[Path](FString& OutError) -> bool
		{
			TacticalEditorAutomation::FPreviewHandles H;
			if (!TacticalEditorAutomation::ResolvePreview(Path, /*bRequireSingleNode*/ false, H, OutError))
			{
				return false;
			}
			H.Toolkit->GetPreviewScene()->FocusViews();
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::SetPreviewPlaying(const FString& AssetPath, bool bPlaying)
{
	FString Path = AssetPath;
	return TacticalEditorAutomation::RunDeferredVoid(
		[Path, bPlaying](FString& OutError) -> bool
		{
			TacticalEditorAutomation::FPreviewHandles H;
			if (!TacticalEditorAutomation::ResolvePreview(Path, /*bRequireSingleNode*/ true, H, OutError))
			{
				return false;
			}
			H.Single->SetPlaying(bPlaying);
			TacticalEditorAutomation::RefreshPreview(H);
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::SetPreviewTimeSeconds(const FString& AssetPath, float Seconds)
{
	FString Path = AssetPath;
	return TacticalEditorAutomation::RunDeferredVoid(
		[Path, Seconds](FString& OutError) -> bool
		{
			if (!FMath::IsFinite(Seconds))
			{
				OutError = TEXT("Seconds is not a finite number.");
				return false;
			}
			TacticalEditorAutomation::FPreviewHandles H;
			if (!TacticalEditorAutomation::ResolvePreview(Path, /*bRequireSingleNode*/ true, H, OutError))
			{
				return false;
			}
			const float Length = H.Single->GetLength();
			if (Seconds < 0.f || Seconds > Length)
			{
				OutError = FString::Printf(
					TEXT("Seconds %.4f is out of range [0, %.4f] for: %s"), Seconds, Length, *Path);
				return false;
			}
			H.Single->SetPlaying(false);
			H.Single->SetPosition(Seconds, /*bFireNotifies*/ false);
			TacticalEditorAutomation::RefreshPreview(H);

			// Verify the preview instance actually reached the requested time (wrap-tolerant
			// at the very end of a looping clip where Length may report back as 0).
			const float Actual = H.Single->GetCurrentTime();
			const float Tol = 0.02f + 1e-3f * Length;
			if (FMath::Abs(Actual - Seconds) > Tol && FMath::Abs(Actual - (Seconds - Length)) > Tol)
			{
				OutError = FString::Printf(
					TEXT("Preview did not reach requested time: requested %.4f, reported %.4f (%s)."),
					Seconds, Actual, *Path);
				return false;
			}
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::SetPreviewTimeNormalized(const FString& AssetPath, float Alpha)
{
	FString Path = AssetPath;
	return TacticalEditorAutomation::RunDeferredVoid(
		[Path, Alpha](FString& OutError) -> bool
		{
			if (!FMath::IsFinite(Alpha))
			{
				OutError = TEXT("Alpha is not a finite number.");
				return false;
			}
			TacticalEditorAutomation::FPreviewHandles H;
			if (!TacticalEditorAutomation::ResolvePreview(Path, /*bRequireSingleNode*/ true, H, OutError))
			{
				return false;
			}
			const float ClampedAlpha = FMath::Clamp(Alpha, 0.f, 1.f);
			const float Length = H.Single->GetLength();
			const float Requested = ClampedAlpha * Length;
			H.Single->SetPlaying(false);
			H.Single->SetPosition(Requested, /*bFireNotifies*/ false);
			TacticalEditorAutomation::RefreshPreview(H);

			const float Actual = H.Single->GetCurrentTime();
			const float Tol = 0.02f + 1e-3f * Length;
			if (FMath::Abs(Actual - Requested) > Tol && FMath::Abs(Actual - (Requested - Length)) > Tol)
			{
				OutError = FString::Printf(
					TEXT("Preview did not reach requested time: requested %.4f, reported %.4f (%s)."),
					Requested, Actual, *Path);
				return false;
			}
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalEditorAutomationToolset::SetPreviewBlendPosition(const FString& AssetPath, float X, float Y)
{
	FString Path = AssetPath;
	return TacticalEditorAutomation::RunDeferredVoid(
		[Path, X, Y](FString& OutError) -> bool
		{
			if (!FMath::IsFinite(X) || !FMath::IsFinite(Y))
			{
				OutError = TEXT("X and Y must both be finite numbers.");
				return false;
			}
			UObject* Asset = TacticalEditorAutomation::ResolveAsset(Path);
			UBlendSpace* BlendSpace = Cast<UBlendSpace>(Asset);
			if (!BlendSpace)
			{
				OutError = FString::Printf(
					TEXT("SetPreviewBlendPosition requires a BlendSpace/AimOffset asset: %s"), *Path);
				return false;
			}

			// Validate against the actual configured axis ranges. Handle 1-D explicitly:
			// a 1-D BlendSpace has no meaningful second coordinate, so reject a non-zero Y
			// rather than silently ignoring it.
			const bool bIs1D = Asset->IsA<UBlendSpace1D>();
			const FBlendParameter& AxisX = BlendSpace->GetBlendParameter(0);
			if (!AxisX.bWrapInput && (X < AxisX.Min || X > AxisX.Max))
			{
				OutError = FString::Printf(
					TEXT("X %.4f is outside axis '%s' range [%.4f, %.4f] for: %s"),
					X, *AxisX.DisplayName, AxisX.Min, AxisX.Max, *Path);
				return false;
			}
			if (bIs1D)
			{
				if (Y != 0.f)
				{
					OutError = FString::Printf(
						TEXT("Asset is a 1-D BlendSpace ('%s' only); Y must be 0, got %.4f: %s"),
						*AxisX.DisplayName, Y, *Path);
					return false;
				}
			}
			else
			{
				const FBlendParameter& AxisY = BlendSpace->GetBlendParameter(1);
				if (!AxisY.bWrapInput && (Y < AxisY.Min || Y > AxisY.Max))
				{
					OutError = FString::Printf(
						TEXT("Y %.4f is outside axis '%s' range [%.4f, %.4f] for: %s"),
						Y, *AxisY.DisplayName, AxisY.Min, AxisY.Max, *Path);
					return false;
				}
			}

			TacticalEditorAutomation::FPreviewHandles H;
			if (!TacticalEditorAutomation::ResolvePreview(Path, /*bRequireSingleNode*/ true, H, OutError))
			{
				return false;
			}
			const FVector Requested(X, bIs1D ? 0.f : Y, 0.f);
			H.Single->SetBlendSpacePosition(Requested);
			TacticalEditorAutomation::RefreshPreview(H);

			// Verify the preview instance accepted the requested blend coordinate (target,
			// not the smoothed/filtered value which may lag).
			FVector Target, Filtered;
			H.Single->GetBlendSpaceState(Target, Filtered);
			const float AxisTol = 1e-2f;
			if (FMath::Abs(Target.X - Requested.X) > AxisTol || FMath::Abs(Target.Y - Requested.Y) > AxisTol)
			{
				OutError = FString::Printf(
					TEXT("Preview did not reach requested blend position: requested (%.3f,%.3f), reported (%.3f,%.3f) (%s)."),
					Requested.X, Requested.Y, Target.X, Target.Y, *Path);
				return false;
			}
			return true;
		});
}
