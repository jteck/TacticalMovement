// Copyright Epic Games, Inc. All Rights Reserved.

#include "TacticalAnimAuthoringToolset.h"

#include "Containers/Ticker.h"
#include "UObject/StrongObjectPtr.h"
#include "UObject/UObjectGlobals.h"
#include "Templates/SubclassOf.h"
#include "Modules/ModuleManager.h"

#include "AssetToolsModule.h"
#include "IAssetTools.h"
#include "Factories/AnimBlueprintFactory.h"
#include "Kismet2/BlueprintEditorUtils.h"
#include "Kismet2/KismetEditorUtilities.h"
#include "Engine/MemberReference.h"
#include "UObject/UnrealType.h"
#include "EdGraph/EdGraph.h"
#include "EdGraph/EdGraphPin.h"
#include "EdGraphSchema_K2.h"

#include "Engine/Blueprint.h"
#include "Animation/AnimBlueprint.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimLayerInterface.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimationAsset.h"

#include "AnimationGraph.h"
#include "AnimationGraphSchema.h"
#include "AnimGraphNode_Base.h"
#include "AnimGraphNode_LinkedInputPose.h"
#include "AnimGraphNode_LinkedAnimLayer.h"
#include "AnimGraphNode_AssetPlayerBase.h"
#include "AnimGraphNode_SaveCachedPose.h"
#include "AnimGraphNode_UseCachedPose.h"

#include "ToolsetRegistry/ToolCallAsyncResultVoid.h"
#include "ToolsetRegistry/ToolCallAsyncResultString.h"

namespace TacticalAnimAuthoring
{
	// Schedules a one-shot game-thread action returning a string result. Keeps authoring
	// (asset/graph edits, compile) off the MCP tool-call (HTTP) tick.
	static UToolCallAsyncResultString* RunDeferredString(TFunction<bool(FString& /*OutValue*/, FString& /*OutError*/)>&& Action)
	{
		UToolCallAsyncResultString* Result = NewObject<UToolCallAsyncResultString>();
		TStrongObjectPtr<UToolCallAsyncResultString> StrongResult(Result);
		FTSTicker::GetCoreTicker().AddTicker(FTickerDelegate::CreateLambda(
			[StrongResult, Action = MoveTemp(Action)](float) mutable -> bool
			{
				FString Value, Error;
				if (Action(Value, Error))
				{
					StrongResult->SetValue(Value);
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

	static UToolCallAsyncResultVoid* RunDeferredVoid(TFunction<bool(FString& /*OutError*/)>&& Action)
	{
		UToolCallAsyncResultVoid* Result = NewObject<UToolCallAsyncResultVoid>();
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
				return false;
			}));
		return Result;
	}

	// Resolves an AnimBlueprint by object/package path (accepts '/Game/Foo/ABP' or full object path).
	static UAnimBlueprint* LoadAnimBlueprint(const FString& Path, FString& OutError)
	{
		UObject* Obj = StaticLoadObject(UAnimBlueprint::StaticClass(), nullptr, *Path);
		UAnimBlueprint* BP = Cast<UAnimBlueprint>(Obj);
		if (!BP)
		{
			OutError = FString::Printf(TEXT("%s is not an AnimBlueprint."), *Path);
		}
		return BP;
	}

	// Finds a graph within a blueprint by name (AnimGraph, layer functions, etc.).
	static UEdGraph* FindGraphByName(UBlueprint* BP, const FString& GraphName)
	{
		TArray<UEdGraph*> AllGraphs;
		BP->GetAllGraphs(AllGraphs);
		for (UEdGraph* G : AllGraphs)
		{
			if (G && G->GetName() == GraphName)
			{
				return G;
			}
		}
		return nullptr;
	}

	// Minimal JSON string escaper for embedding paths/names/cache into a JSON value.
	static FString JsonEscape(const FString& In)
	{
		FString Out;
		Out.Reserve(In.Len() + 8);
		for (TCHAR C : In)
		{
			switch (C)
			{
			case TEXT('\\'): Out += TEXT("\\\\"); break;
			case TEXT('\"'): Out += TEXT("\\\""); break;
			case TEXT('\n'): Out += TEXT("\\n"); break;
			case TEXT('\r'): Out += TEXT("\\r"); break;
			case TEXT('\t'): Out += TEXT("\\t"); break;
			default: Out += C; break;
			}
		}
		return Out;
	}

	// Resolves exactly one node of type T within Graph whose NodeGuid string (preferred), object
	// name, or full object path equals Id. Because the search is scoped to a single graph of a single
	// AnimBlueprint, nodes from other Blueprints/graphs simply do not resolve (rejected as not-found),
	// and an Id belonging to a different node class yields zero matches of T (wrong-class rejection).
	template <typename T>
	static T* ResolveUniqueNodeInGraph(UEdGraph* Graph, const FString& Id, const TCHAR* Label, FString& OutError)
	{
		TArray<T*> Matches;
		for (UEdGraphNode* N : Graph->Nodes)
		{
			T* Typed = Cast<T>(N);
			if (!Typed) { continue; }
			if (Typed->NodeGuid.ToString() == Id || Typed->GetName() == Id || Typed->GetPathName() == Id)
			{
				Matches.Add(Typed);
			}
		}
		if (Matches.Num() == 0)
		{
			OutError = FString::Printf(TEXT("No %s node with id '%s' in graph '%s'."), Label, *Id, *Graph->GetName());
			return nullptr;
		}
		if (Matches.Num() > 1)
		{
			OutError = FString::Printf(TEXT("Ambiguous: %d %s nodes match id '%s' in graph '%s'."), Matches.Num(), Label, *Id, *Graph->GetName());
			return nullptr;
		}
		return Matches[0];
	}
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::CreateAnimBlueprintDeferred(const FString& AssetPath, const FString& SkeletonPath, bool bAsInterface)
{
	FString Path = AssetPath, SkelPath = SkeletonPath;
	return TacticalAnimAuthoring::RunDeferredString(
		[Path, SkelPath, bAsInterface](FString& OutValue, FString& OutError) -> bool
		{
			if (StaticFindObject(nullptr, nullptr, *Path) || StaticLoadObject(UObject::StaticClass(), nullptr, *Path))
			{
				OutError = FString::Printf(TEXT("An asset already exists at: %s"), *Path);
				return false;
			}
			USkeleton* Skeleton = Cast<USkeleton>(StaticLoadObject(USkeleton::StaticClass(), nullptr, *SkelPath));
			if (!Skeleton)
			{
				OutError = FString::Printf(TEXT("%s is not a valid USkeleton."), *SkelPath);
				return false;
			}

			FString PackagePath, AssetName;
			if (!Path.Split(TEXT("/"), &PackagePath, &AssetName, ESearchCase::IgnoreCase, ESearchDir::FromEnd) || AssetName.IsEmpty())
			{
				OutError = FString::Printf(TEXT("Invalid asset path: %s"), *Path);
				return false;
			}

			UAnimBlueprintFactory* Factory = NewObject<UAnimBlueprintFactory>();
			Factory->TargetSkeleton = Skeleton;
			Factory->ParentClass = UAnimInstance::StaticClass();
			Factory->BlueprintType = bAsInterface ? BPTYPE_Interface : BPTYPE_Normal;
			Factory->bTemplate = false;

			IAssetTools& AssetTools = FModuleManager::LoadModuleChecked<FAssetToolsModule>("AssetTools").Get();
			UObject* Created = AssetTools.CreateAsset(AssetName, PackagePath, UAnimBlueprint::StaticClass(), Factory);
			UAnimBlueprint* NewBP = Cast<UAnimBlueprint>(Created);
			if (!NewBP)
			{
				OutError = FString::Printf(TEXT("CreateAsset did not return an AnimBlueprint for: %s"), *Path);
				return false;
			}
			if (NewBP->TargetSkeleton != Skeleton)
			{
				OutError = FString::Printf(TEXT("Created AnimBlueprint target skeleton mismatch for: %s"), *Path);
				return false;
			}
			OutValue = NewBP->GetPathName();
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::AddAnimLayerFunctionDeferred(const FString& BlueprintPath, const FString& FunctionName, const FString& PoseInputName, const TArray<FString>& FloatInputs)
{
	FString BPPath = BlueprintPath, FnName = FunctionName, PoseName = PoseInputName;
	TArray<FString> Floats = FloatInputs;
	return TacticalAnimAuthoring::RunDeferredString(
		[BPPath, FnName, PoseName, Floats](FString& OutValue, FString& OutError) -> bool
		{
			UAnimBlueprint* BP = TacticalAnimAuthoring::LoadAnimBlueprint(BPPath, OutError);
			if (!BP) { return false; }
			if (TacticalAnimAuthoring::FindGraphByName(BP, FnName))
			{
				OutError = FString::Printf(TEXT("A graph named '%s' already exists."), *FnName);
				return false;
			}

			// Create an ANIM graph (pose in/out domain), auto-adds the Output Pose (Root).
			UEdGraph* NewGraph = FBlueprintEditorUtils::CreateNewGraph(
				BP, FName(*FnName), UAnimationGraph::StaticClass(), UAnimationGraphSchema::StaticClass());
			if (!NewGraph)
			{
				OutError = TEXT("CreateNewGraph failed.");
				return false;
			}
			FBlueprintEditorUtils::AddDomainSpecificGraph(BP, NewGraph);

			// Add the Linked Input Pose node carrying the named pose + typed float inputs.
			FGraphNodeCreator<UAnimGraphNode_LinkedInputPose> Creator(*NewGraph);
			UAnimGraphNode_LinkedInputPose* InputNode = Creator.CreateNode(false);
			InputNode->Node.Name = FName(*PoseName);
			InputNode->Inputs.Reset();
			for (const FString& F : Floats)
			{
				FAnimBlueprintFunctionPinInfo Pin;
				Pin.Name = FName(*F);
				Pin.Type.PinCategory = UEdGraphSchema_K2::PC_Real;
				Pin.Type.PinSubCategory = UEdGraphSchema_K2::PC_Float;
				InputNode->Inputs.Add(Pin);
			}
			InputNode->NodePosX = -400;
			InputNode->NodePosY = 0;
			Creator.Finalize();

			FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			OutValue = NewGraph->GetPathName();
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalAnimAuthoringToolset::ImplementAnimInterfaceDeferred(const FString& BlueprintPath, const FString& InterfacePath)
{
	FString BPPath = BlueprintPath, IfacePath = InterfacePath;
	return TacticalAnimAuthoring::RunDeferredVoid(
		[BPPath, IfacePath](FString& OutError) -> bool
		{
			UAnimBlueprint* BP = TacticalAnimAuthoring::LoadAnimBlueprint(BPPath, OutError);
			if (!BP) { return false; }
			UAnimBlueprint* Iface = TacticalAnimAuthoring::LoadAnimBlueprint(IfacePath, OutError);
			if (!Iface) { return false; }

			// ---- Validate before mutating. ----
			// Interface must be an Anim Layer Interface with a generated class.
			if (Iface->BlueprintType != BPTYPE_Interface)
			{
				OutError = FString::Printf(TEXT("%s is not an Anim Layer Interface (BlueprintType is not BPTYPE_Interface)."), *IfacePath);
				return false;
			}
			if (!Iface->GeneratedClass)
			{
				OutError = FString::Printf(TEXT("Interface %s has no generated class (compile it first)."), *IfacePath);
				return false;
			}
			// Both must have non-null, compatible target skeletons.
			if (!BP->TargetSkeleton || !Iface->TargetSkeleton)
			{
				OutError = FString::Printf(TEXT("Missing target skeleton on implementer (%s) or interface (%s); cannot establish compatibility."), *BPPath, *IfacePath);
				return false;
			}
			if (!BP->TargetSkeleton->IsCompatibleForEditor(Iface->TargetSkeleton))
			{
				OutError = FString::Printf(TEXT("Skeleton mismatch: implementer targets %s but interface %s targets %s."),
					*BP->TargetSkeleton->GetPathName(), *IfacePath, *Iface->TargetSkeleton->GetPathName());
				return false;
			}
			// Idempotent: if the blueprint already implements the interface, succeed without re-adding.
			for (const FBPInterfaceDescription& Desc : BP->ImplementedInterfaces)
			{
				if (Desc.Interface.Get() == Iface->GeneratedClass)
				{
					return true; // already implemented; no mutation needed
				}
			}

			if (!FBlueprintEditorUtils::ImplementNewInterface(BP, FTopLevelAssetPath(Iface->GeneratedClass)))
			{
				OutError = FString::Printf(TEXT("ImplementNewInterface failed for %s on %s."), *IfacePath, *BPPath);
				return false;
			}
			FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::SpawnAnimGraphNodeDeferred(const FString& BlueprintPath, const FString& GraphName, const FString& NodeClassPath, int32 PosX, int32 PosY)
{
	FString BPPath = BlueprintPath, GName = GraphName, ClassPath = NodeClassPath;
	return TacticalAnimAuthoring::RunDeferredString(
		[BPPath, GName, ClassPath, PosX, PosY](FString& OutValue, FString& OutError) -> bool
		{
			UAnimBlueprint* BP = TacticalAnimAuthoring::LoadAnimBlueprint(BPPath, OutError);
			if (!BP) { return false; }
			UEdGraph* Graph = TacticalAnimAuthoring::FindGraphByName(BP, GName);
			if (!Graph)
			{
				OutError = FString::Printf(TEXT("Graph '%s' not found in %s."), *GName, *BPPath);
				return false;
			}
			// Enforce the documented contract: an AnimGraph node may only be spawned into an
			// animation graph (animation schema). A name match alone is not sufficient — e.g. an
			// EventGraph resolves by name but uses UEdGraphSchema_K2, and an AnimGraph node dropped
			// into it would be invalid. Reject anything not backed by the animation-graph schema.
			UClass* SchemaClass = Graph->Schema;
			if (!SchemaClass || !SchemaClass->IsChildOf(UAnimationGraphSchema::StaticClass()))
			{
				OutError = FString::Printf(
					TEXT("Graph '%s' in %s is not an Animation Graph (schema '%s'); refusing to spawn an AnimGraph node into it."),
					*GName, *BPPath, SchemaClass ? *SchemaClass->GetName() : TEXT("null"));
				return false;
			}
			UClass* NodeClass = LoadObject<UClass>(nullptr, *ClassPath);
			if (!NodeClass || !NodeClass->IsChildOf(UAnimGraphNode_Base::StaticClass()))
			{
				OutError = FString::Printf(TEXT("%s is not a UAnimGraphNode_Base subclass."), *ClassPath);
				return false;
			}

			FGraphNodeCreator<UAnimGraphNode_Base> Creator(*Graph);
			UAnimGraphNode_Base* NewNode = Creator.CreateNode(false, NodeClass);
			if (!NewNode)
			{
				OutError = FString::Printf(TEXT("Failed to spawn node of class %s."), *ClassPath);
				return false;
			}
			NewNode->NodePosX = PosX;
			NewNode->NodePosY = PosY;
			Creator.Finalize();

			FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			OutValue = NewNode->GetPathName();
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalAnimAuthoringToolset::SetLinkedAnimLayerDeferred(const FString& NodePath, const FString& InterfacePath, const FString& LayerName, const FString& InstanceClassPath)
{
	FString NPath = NodePath, IfacePath = InterfacePath, Layer = LayerName, InstPath = InstanceClassPath;
	return TacticalAnimAuthoring::RunDeferredVoid(
		[NPath, IfacePath, Layer, InstPath](FString& OutError) -> bool
		{
			UAnimGraphNode_LinkedAnimLayer* Node = Cast<UAnimGraphNode_LinkedAnimLayer>(
				StaticFindObject(UAnimGraphNode_LinkedAnimLayer::StaticClass(), nullptr, *NPath));
			if (!Node)
			{
				OutError = FString::Printf(TEXT("%s is not a Linked Anim Layer node."), *NPath);
				return false;
			}
			// ---- Validate ALL inputs before mutating anything (so a failure leaves the node
			//      untouched, including the reflection guard below). ----

			// Interface must be an Anim Layer Interface (BPTYPE_Interface) with a generated class.
			UAnimBlueprint* Iface = nullptr;
			if (!IfacePath.IsEmpty())
			{
				Iface = TacticalAnimAuthoring::LoadAnimBlueprint(IfacePath, OutError);
				if (!Iface) { return false; }
				if (Iface->BlueprintType != BPTYPE_Interface)
				{
					OutError = FString::Printf(TEXT("%s is not an Anim Layer Interface (BlueprintType is not BPTYPE_Interface)."), *IfacePath);
					return false;
				}
				if (!Iface->GeneratedClass)
				{
					OutError = FString::Printf(TEXT("Interface %s has no generated class (compile it first)."), *IfacePath);
					return false;
				}
			}

			// External instance = implementing AnimBlueprint's generated class. Empty = self layer.
			UAnimBlueprint* Ext = nullptr;
			if (!InstPath.IsEmpty())
			{
				Ext = TacticalAnimAuthoring::LoadAnimBlueprint(InstPath, OutError);
				if (!Ext) { return false; }
				if (!Ext->GeneratedClass)
				{
					OutError = FString::Printf(TEXT("Instance class blueprint %s has no generated class (compile it first)."), *InstPath);
					return false;
				}
			}

			// The external AnimBP must actually implement the interface.
			if (Iface && Ext)
			{
				bool bImplements = Ext->GeneratedClass->ImplementsInterface(Iface->GeneratedClass);
				if (!bImplements)
				{
					for (const FBPInterfaceDescription& Desc : Ext->ImplementedInterfaces)
					{
						if (Desc.Interface.Get() == Iface->GeneratedClass) { bImplements = true; break; }
					}
				}
				if (!bImplements)
				{
					OutError = FString::Printf(TEXT("External AnimBlueprint %s does not implement interface %s (implement + compile it first)."), *InstPath, *IfacePath);
					return false;
				}
			}

			// Host and external AnimBPs must share a compatible target skeleton. Reject unknown
			// compatibility (missing host BP / host skeleton / external skeleton) rather than
			// letting it pass as compatible.
			UAnimBlueprint* HostBP = Cast<UAnimBlueprint>(Node->GetBlueprint());
			if (!HostBP)
			{
				OutError = TEXT("Cannot resolve the host AnimBlueprint for the linked-layer node.");
				return false;
			}
			if (Ext)
			{
				if (!HostBP->TargetSkeleton || !Ext->TargetSkeleton)
				{
					OutError = FString::Printf(TEXT("Missing target skeleton on host or external %s; cannot establish skeleton compatibility."), *InstPath);
					return false;
				}
				if (HostBP->TargetSkeleton != Ext->TargetSkeleton)
				{
					OutError = FString::Printf(TEXT("Skeleton mismatch: host targets %s but external %s targets %s."),
						*HostBP->TargetSkeleton->GetPathName(), *InstPath, *Ext->TargetSkeleton->GetPathName());
					return false;
				}
			}

			// The requested layer function must exist on the declaring class (interface if given,
			// else the external instance class, else the host).
			const FName LayerFName(*Layer);
			UClass* FnOwnerClass = nullptr;
			if (Iface)        { FnOwnerClass = Iface->GeneratedClass; }
			else if (Ext)     { FnOwnerClass = Ext->GeneratedClass; }
			else if (HostBP)  { FnOwnerClass = HostBP->GeneratedClass; }
			if (!FnOwnerClass || !FnOwnerClass->FindFunctionByName(LayerFName))
			{
				OutError = FString::Printf(TEXT("Layer function '%s' does not exist on %s."),
					*Layer, FnOwnerClass ? *FnOwnerClass->GetName() : TEXT("<no resolvable class>"));
				return false;
			}

			// Reflection guard: SetLayerName() is not ANIMGRAPH_API-exported (MinimalAPI class) and
			// the FunctionReference member is protected, so we replicate its effect by writing the
			// reflected `FunctionReference` UPROPERTY via FMemberReference's public API. Verify that
			// property is present AND is an FMemberReference (guards a future engine type change).
			// Resolved before mutation so a failure leaves the node untouched.
			FStructProperty* FRProp = FindFProperty<FStructProperty>(Node->GetClass(), TEXT("FunctionReference"));
			if (!FRProp || FRProp->Struct != FMemberReference::StaticStruct())
			{
				OutError = TEXT("The linked-layer node's reflected 'FunctionReference' property is absent or not an FMemberReference (engine version change); node left unmodified.");
				return false;
			}

			// ---- All validation passed; mutate the node. ----
			if (Iface)
			{
				Node->Node.Interface = Iface->GeneratedClass;
			}
			if (Ext)
			{
				Node->Node.InstanceClass = Ext->GeneratedClass;
			}
			else
			{
				Node->Node.InstanceClass = nullptr;
			}
			Node->Node.Layer = LayerFName;

			FMemberReference& Ref = *FRProp->ContainerPtrToValuePtr<FMemberReference>(Node);
			if (UClass* TargetClass = Node->Node.InstanceClass.Get())
			{
				FGuid FunctionGuid;
				FBlueprintEditorUtils::GetFunctionGuidFromClassByFieldName(
					FBlueprintEditorUtils::GetMostUpToDateClass(TargetClass), LayerFName, FunctionGuid);
				Ref.SetExternalMember(LayerFName, TargetClass, FunctionGuid);
			}
			else
			{
				Ref.SetSelfMember(LayerFName);
			}
			Node->ReconstructNode();

			if (UBlueprint* BP = Node->GetBlueprint())
			{
				FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			}
			return true;
		});
}

UToolCallAsyncResultVoid* UTacticalAnimAuthoringToolset::SetAnimGraphNodeAnimationAssetDeferred(const FString& NodePath, const FString& AnimationAssetPath)
{
	FString NPath = NodePath, AssetPath = AnimationAssetPath;
	return TacticalAnimAuthoring::RunDeferredVoid(
		[NPath, AssetPath](FString& OutError) -> bool
		{
			UAnimGraphNode_AssetPlayerBase* Node = Cast<UAnimGraphNode_AssetPlayerBase>(
				StaticFindObject(UAnimGraphNode_AssetPlayerBase::StaticClass(), nullptr, *NPath));
			if (!Node)
			{
				OutError = FString::Printf(TEXT("Wrong node class: %s is not an asset-player AnimGraph node."), *NPath);
				return false;
			}
			UAnimationAsset* Asset = Cast<UAnimationAsset>(StaticLoadObject(UAnimationAsset::StaticClass(), nullptr, *AssetPath));
			if (!Asset)
			{
				OutError = FString::Printf(TEXT("Wrong asset class: %s is not a valid UAnimationAsset."), *AssetPath);
				return false;
			}
			// SetAnimationAsset() primarily checks asset class, NOT skeleton, so enforce skeleton
			// compatibility against the owning AnimBlueprint's target skeleton before assigning.
			UAnimBlueprint* HostBP = Cast<UAnimBlueprint>(Node->GetBlueprint());
			if (!HostBP || !HostBP->TargetSkeleton)
			{
				OutError = FString::Printf(TEXT("Cannot resolve the owning AnimBlueprint's target skeleton for node %s."), *NPath);
				return false;
			}
			USkeleton* AssetSkeleton = Asset->GetSkeleton();
			if (!AssetSkeleton)
			{
				OutError = FString::Printf(TEXT("Animation asset %s has no skeleton."), *AssetPath);
				return false;
			}
			if (!HostBP->TargetSkeleton->IsCompatibleForEditor(AssetSkeleton))
			{
				OutError = FString::Printf(TEXT("Skeleton mismatch: host targets %s but asset %s uses %s."),
					*HostBP->TargetSkeleton->GetPathName(), *AssetPath, *AssetSkeleton->GetPathName());
				return false;
			}

			// Defensively preserve the previous asset: assign, read back, and if the node did not
			// take it, restore the previous asset and verify the restoration before erroring so the
			// "node unchanged" claim holds.
			UAnimationAsset* PrevAsset = Node->GetAnimationAsset();
			Node->SetAnimationAsset(Asset); // public; routes to the private runtime field safely
			if (Node->GetAnimationAsset() != Asset)
			{
				Node->SetAnimationAsset(PrevAsset);
				if (Node->GetAnimationAsset() != PrevAsset)
				{
					OutError = FString::Printf(
						TEXT("Assignment of %s to node %s failed on readback AND restoration of the previous asset failed (node left in an indeterminate state)."),
						*AssetPath, *NPath);
				}
				else
				{
					OutError = FString::Printf(
						TEXT("Assignment/readback failure: node %s did not accept %s; previous asset restored (node unchanged)."),
						*NPath, *AssetPath);
				}
				return false;
			}
			Node->ReconstructNode();
			if (UBlueprint* BP = Node->GetBlueprint())
			{
				FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			}
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::BindUseCachedPoseDeferred(const FString& BlueprintPath, const FString& GraphName, const FString& UseNodeId, const FString& SaveNodeId)
{
	FString BPPath = BlueprintPath, GName = GraphName, UseId = UseNodeId, SaveId = SaveNodeId;
	return TacticalAnimAuthoring::RunDeferredString(
		[BPPath, GName, UseId, SaveId](FString& OutValue, FString& OutError) -> bool
		{
			// ---- Resolve + validate everything BEFORE any mutation. ----
			UAnimBlueprint* BP = TacticalAnimAuthoring::LoadAnimBlueprint(BPPath, OutError);
			if (!BP) { return false; }
			UEdGraph* Graph = TacticalAnimAuthoring::FindGraphByName(BP, GName);
			if (!Graph)
			{
				OutError = FString::Printf(TEXT("Graph '%s' not found in %s."), *GName, *BPPath);
				return false;
			}
			// Conservative scope: both nodes must live in this single animation graph of this AnimBlueprint.
			UClass* SchemaClass = Graph->Schema;
			if (!SchemaClass || !SchemaClass->IsChildOf(UAnimationGraphSchema::StaticClass()))
			{
				OutError = FString::Printf(TEXT("Graph '%s' in %s is not an Animation Graph."), *GName, *BPPath);
				return false;
			}
			UAnimGraphNode_UseCachedPose* UseNode =
				TacticalAnimAuthoring::ResolveUniqueNodeInGraph<UAnimGraphNode_UseCachedPose>(Graph, UseId, TEXT("Use Cached Pose"), OutError);
			if (!UseNode) { return false; }
			UAnimGraphNode_SaveCachedPose* SaveNode =
				TacticalAnimAuthoring::ResolveUniqueNodeInGraph<UAnimGraphNode_SaveCachedPose>(Graph, SaveId, TEXT("Save Cached Pose"), OutError);
			if (!SaveNode) { return false; }

			// Save node CacheName must be nonempty and unique within the graph.
			if (SaveNode->CacheName.IsEmpty())
			{
				OutError = FString::Printf(TEXT("Save Cached Pose node '%s' has an empty CacheName."), *SaveNode->GetName());
				return false;
			}
			int32 SameName = 0;
			for (UEdGraphNode* N : Graph->Nodes)
			{
				if (UAnimGraphNode_SaveCachedPose* S = Cast<UAnimGraphNode_SaveCachedPose>(N))
				{
					if (S->CacheName == SaveNode->CacheName) { ++SameName; }
				}
			}
			if (SameName > 1)
			{
				OutError = FString::Printf(TEXT("Ambiguous CacheName '%s': %d Save Cached Pose nodes share it in graph '%s'."), *SaveNode->CacheName, SameName, *GName);
				return false;
			}
			// Save node pose input must be wired (reject an unlinked/invalid Save).
			bool bSaveWired = false;
			for (UEdGraphPin* Pin : SaveNode->Pins)
			{
				if (Pin && Pin->Direction == EGPD_Input && Pin->LinkedTo.Num() > 0) { bSaveWired = true; break; }
			}
			if (!bSaveWired)
			{
				OutError = FString::Printf(TEXT("Save Cached Pose node '%s' (cache '%s') has no wired pose input."), *SaveNode->GetName(), *SaveNode->CacheName);
				return false;
			}

			// ---- Idempotency (no automatic unbind/rebind). ----
			UAnimGraphNode_SaveCachedPose* Existing = UseNode->SaveCachedPoseNode.Get();
			bool bIdempotent = false;
			if (Existing == SaveNode)
			{
				bIdempotent = true; // already bound to the requested Save node: successful readback, no dirtying
			}
			else if (Existing != nullptr)
			{
				OutError = FString::Printf(
					TEXT("Use Cached Pose node '%s' is already bound to a different Save node '%s' (cache '%s'); refusing to silently rebind."),
					*UseNode->GetName(), *Existing->GetName(), *Existing->CacheName);
				return false;
			}

			// ---- Minimal Epic-aligned mutation (only when not already bound). ----
			if (!bIdempotent)
			{
				UseNode->Modify();
				UseNode->SaveCachedPoseNode = SaveNode; // public UPROPERTY; same assignment Epic's menu action performs
				if (UEdGraph* UG = UseNode->GetGraph()) { UG->NotifyGraphChanged(); }
				FBlueprintEditorUtils::MarkBlueprintAsStructurallyModified(BP);
			}

			OutValue = FString::Printf(
				TEXT("{\"blueprint\":\"%s\",\"graph\":\"%s\",\"useNodeId\":\"%s\",\"useNodePath\":\"%s\",\"saveNodeId\":\"%s\",\"saveNodePath\":\"%s\",\"cacheName\":\"%s\",\"idempotent\":%s}"),
				*TacticalAnimAuthoring::JsonEscape(BP->GetPathName()),
				*TacticalAnimAuthoring::JsonEscape(Graph->GetName()),
				*TacticalAnimAuthoring::JsonEscape(UseNode->NodeGuid.ToString()),
				*TacticalAnimAuthoring::JsonEscape(UseNode->GetPathName()),
				*TacticalAnimAuthoring::JsonEscape(SaveNode->NodeGuid.ToString()),
				*TacticalAnimAuthoring::JsonEscape(SaveNode->GetPathName()),
				*TacticalAnimAuthoring::JsonEscape(SaveNode->CacheName),
				bIdempotent ? TEXT("true") : TEXT("false"));
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::GetUseCachedPoseBinding(const FString& BlueprintPath, const FString& GraphName, const FString& UseNodeId)
{
	FString BPPath = BlueprintPath, GName = GraphName, UseId = UseNodeId;
	return TacticalAnimAuthoring::RunDeferredString(
		[BPPath, GName, UseId](FString& OutValue, FString& OutError) -> bool
		{
			UAnimBlueprint* BP = TacticalAnimAuthoring::LoadAnimBlueprint(BPPath, OutError);
			if (!BP) { return false; }
			UEdGraph* Graph = TacticalAnimAuthoring::FindGraphByName(BP, GName);
			if (!Graph)
			{
				OutError = FString::Printf(TEXT("Graph '%s' not found in %s."), *GName, *BPPath);
				return false;
			}
			UAnimGraphNode_UseCachedPose* UseNode =
				TacticalAnimAuthoring::ResolveUniqueNodeInGraph<UAnimGraphNode_UseCachedPose>(Graph, UseId, TEXT("Use Cached Pose"), OutError);
			if (!UseNode) { return false; }

			UAnimGraphNode_SaveCachedPose* SaveNode = UseNode->SaveCachedPoseNode.Get();
			if (SaveNode)
			{
				OutValue = FString::Printf(
					TEXT("{\"blueprint\":\"%s\",\"graph\":\"%s\",\"useNodeId\":\"%s\",\"useNodePath\":\"%s\",\"bound\":true,\"saveNodeId\":\"%s\",\"saveNodePath\":\"%s\",\"cacheName\":\"%s\"}"),
					*TacticalAnimAuthoring::JsonEscape(BP->GetPathName()),
					*TacticalAnimAuthoring::JsonEscape(Graph->GetName()),
					*TacticalAnimAuthoring::JsonEscape(UseNode->NodeGuid.ToString()),
					*TacticalAnimAuthoring::JsonEscape(UseNode->GetPathName()),
					*TacticalAnimAuthoring::JsonEscape(SaveNode->NodeGuid.ToString()),
					*TacticalAnimAuthoring::JsonEscape(SaveNode->GetPathName()),
					*TacticalAnimAuthoring::JsonEscape(SaveNode->CacheName));
			}
			else
			{
				OutValue = FString::Printf(
					TEXT("{\"blueprint\":\"%s\",\"graph\":\"%s\",\"useNodeId\":\"%s\",\"useNodePath\":\"%s\",\"bound\":false,\"saveNodeId\":null,\"saveNodePath\":null,\"cacheName\":\"\"}"),
					*TacticalAnimAuthoring::JsonEscape(BP->GetPathName()),
					*TacticalAnimAuthoring::JsonEscape(Graph->GetName()),
					*TacticalAnimAuthoring::JsonEscape(UseNode->NodeGuid.ToString()),
					*TacticalAnimAuthoring::JsonEscape(UseNode->GetPathName()));
			}
			return true;
		});
}
