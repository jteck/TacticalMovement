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

#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshSocket.h"
#include "ScopedTransaction.h"
#include "UObject/Package.h"
#include "Containers/StringConv.h"
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

// =============================================================================
// Static-mesh socket authoring (Boundary G muzzle reference)
// =============================================================================
namespace TacticalAnimAuthoring
{
	// ---- static-mesh socket hard bounds (mirrored in the header documentation) ----
	static const int32  kMaxSocketNameLen = 128;          // characters
	static const double kMaxSocketLocation = 10000.0;     // cm, per axis, absolute
	static const double kMaxSocketRotationDeg = 360.0;    // degrees, per component, absolute
	static const double kMinSocketScale = 0.001;          // per component, absolute magnitude
	static const double kMaxSocketScale = 100.0;          // per component, absolute magnitude
	static const double kSocketMatchTolerance = 0.001;    // readback / expected-prior-transform tolerance
	static const int32  kMaxSocketsReturned = 256;        // GetStaticMeshSockets: max entries serialized
	static const int32  kMaxSocketsJsonBytes = 256 * 1024;// GetStaticMeshSockets: max serialized socket-array bytes

	// Provenance of sockets THIS tool added during the current editor session, keyed by
	// "<meshPath>|<socketName>" -> the EXACT socket object created. A weak pointer is used
	// deliberately: if the socket is destroyed, replaced, or undone, the entry goes stale and
	// the CAS bypass is refused. A same-named replacement is a DIFFERENT object and is never
	// trusted. Session-scoped only; never persisted.
	static TMap<FString, TWeakObjectPtr<UStaticMeshSocket>> GToolAddedSockets;

	// RAW component-wise rotator comparison. Deliberately NOT FRotator::Equals: that compares
	// orientation and treats wrap-equivalent components (e.g. 0 and 360 degrees) as equal, which
	// would contradict the documented policy that this tool preserves the caller's supplied
	// components verbatim and never normalizes, wraps, or rewrites them.
	static bool RotatorComponentsEqual(const FRotator& A, const FRotator& B, double Tolerance)
	{
		return FMath::Abs(A.Pitch - B.Pitch) <= Tolerance
			&& FMath::Abs(A.Yaw   - B.Yaw)   <= Tolerance
			&& FMath::Abs(A.Roll  - B.Roll)  <= Tolerance;
	}

	static FString SocketKey(const FString& MeshPath, const FString& SocketName)
	{
		return MeshPath + TEXT("|") + SocketName;
	}

	// Drops entries whose weak pointer has gone stale. Keeps the map from growing across a session.
	static void PurgeStaleSocketProvenance()
	{
		for (auto It = GToolAddedSockets.CreateIterator(); It; ++It)
		{
			if (!It.Value().IsValid()) { It.RemoveCurrent(); }
		}
	}

	// True only when this tool added EXACTLY this live socket object in this session.
	static bool IsToolAddedSocket(const FString& MeshPath, const FString& SocketName, const UStaticMeshSocket* Current)
	{
		PurgeStaleSocketProvenance();
		const TWeakObjectPtr<UStaticMeshSocket>* Found = GToolAddedSockets.Find(SocketKey(MeshPath, SocketName));
		if (!Found) { return false; }
		UStaticMeshSocket* Tracked = Found->Get();
		return Tracked != nullptr && Current != nullptr && Tracked == Current;
	}

	static UStaticMesh* LoadStaticMeshAsset(const FString& Path, FString& OutError)
	{
		const FString Trimmed = Path.TrimStartAndEnd();
		if (Trimmed.IsEmpty()) { OutError = TEXT("AssetPath must be non-empty."); return nullptr; }

		UObject* Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *Trimmed);
		if (!Obj)
		{
			FString ObjectName;
			if (Trimmed.Split(TEXT("/"), nullptr, &ObjectName, ESearchCase::CaseSensitive, ESearchDir::FromEnd)
				&& !ObjectName.IsEmpty() && !Trimmed.Contains(TEXT(".")))
			{
				Obj = StaticLoadObject(UObject::StaticClass(), nullptr, *(Trimmed + TEXT(".") + ObjectName));
			}
		}
		if (!Obj) { OutError = FString::Printf(TEXT("Asset not found: %s"), *Trimmed); return nullptr; }

		UStaticMesh* Mesh = Cast<UStaticMesh>(Obj);
		if (!Mesh) { OutError = FString::Printf(TEXT("Asset is %s, not a StaticMesh: %s"), *Obj->GetClass()->GetName(), *Trimmed); return nullptr; }
		if (!IsValid(Mesh)) { OutError = TEXT("StaticMesh is pending kill / invalid."); return nullptr; }
		if (Mesh->IsTemplate()) { OutError = TEXT("Asset is a CDO/template."); return nullptr; }
		if (Mesh->HasAnyFlags(RF_Transient)) { OutError = TEXT("Asset is transient."); return nullptr; }
		return Mesh;
	}

	static bool ValidateSocketName(const FString& Name, FString& OutError)
	{
		if (Name.IsEmpty()) { OutError = TEXT("SocketName must be non-empty."); return false; }
		if (Name.TrimStartAndEnd().IsEmpty()) { OutError = TEXT("SocketName must not be whitespace-only."); return false; }
		if (Name.Len() > kMaxSocketNameLen)
		{ OutError = FString::Printf(TEXT("SocketName is %d characters; the maximum is %d."), Name.Len(), kMaxSocketNameLen); return false; }
		return true;
	}

	static bool ValidateSocketTransform(const FVector& Loc, const FRotator& Rot, const FVector& Scale, FString& OutError)
	{
		if (Loc.ContainsNaN() || !FMath::IsFinite(Loc.X) || !FMath::IsFinite(Loc.Y) || !FMath::IsFinite(Loc.Z))
		{ OutError = TEXT("Relative location must be finite."); return false; }
		if (Rot.ContainsNaN() || !FMath::IsFinite(Rot.Pitch) || !FMath::IsFinite(Rot.Yaw) || !FMath::IsFinite(Rot.Roll))
		{ OutError = TEXT("Relative rotation must be finite."); return false; }
		if (Scale.ContainsNaN() || !FMath::IsFinite(Scale.X) || !FMath::IsFinite(Scale.Y) || !FMath::IsFinite(Scale.Z))
		{ OutError = TEXT("Relative scale must be finite."); return false; }

		if (FMath::Abs(Loc.X) > kMaxSocketLocation || FMath::Abs(Loc.Y) > kMaxSocketLocation || FMath::Abs(Loc.Z) > kMaxSocketLocation)
		{ OutError = FString::Printf(TEXT("Relative location components must be within +/-%.0f cm."), kMaxSocketLocation); return false; }

		// Explicit rotation policy: components are accepted only in [-360,360]. Callers author
		// normalized rotations; the tool never normalizes or rewrites a caller's value.
		if (FMath::Abs(Rot.Pitch) > kMaxSocketRotationDeg || FMath::Abs(Rot.Yaw) > kMaxSocketRotationDeg || FMath::Abs(Rot.Roll) > kMaxSocketRotationDeg)
		{ OutError = FString::Printf(TEXT("Relative rotation components must be within +/-%.0f degrees (author normalized rotations)."), kMaxSocketRotationDeg); return false; }

		const double S[3] = { Scale.X, Scale.Y, Scale.Z };
		for (int32 i = 0; i < 3; ++i)
		{
			if (FMath::Abs(S[i]) < kMinSocketScale || FMath::Abs(S[i]) > kMaxSocketScale)
			{ OutError = FString::Printf(TEXT("Relative scale components must have magnitude within [%.3f, %.0f]."), kMinSocketScale, kMaxSocketScale); return false; }
		}
		return true;
	}

	static FString XformJson(const FVector& Loc, const FRotator& Rot, const FVector& Scale)
	{
		return FString::Printf(
			TEXT("\"relativeLocation\":{\"x\":%.6f,\"y\":%.6f,\"z\":%.6f},")
			TEXT("\"relativeRotation\":{\"pitch\":%.6f,\"yaw\":%.6f,\"roll\":%.6f},")
			TEXT("\"relativeScale\":{\"x\":%.6f,\"y\":%.6f,\"z\":%.6f}"),
			Loc.X, Loc.Y, Loc.Z, Rot.Pitch, Rot.Yaw, Rot.Roll, Scale.X, Scale.Y, Scale.Z);
	}
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::GetStaticMeshSockets(const FString& AssetPath)
{
	return TacticalAnimAuthoring::RunDeferredString(
		[AssetPath](FString& OutValue, FString& OutError) -> bool
		{
			check(IsInGameThread());
			UStaticMesh* Mesh = TacticalAnimAuthoring::LoadStaticMeshAsset(AssetPath, OutError);
			if (!Mesh) { return false; }

			const int32 Total = Mesh->Sockets.Num();
			FString Items;
			int32 Count = 0;
			int32 AccumBytes = 0;      // ACTUAL serialized UTF-8 bytes of the socket array
			bool bTruncated = false;
			for (UStaticMeshSocket* Socket : Mesh->Sockets)
			{
				if (!Socket) { continue; }
				if (Count >= TacticalAnimAuthoring::kMaxSocketsReturned) { bTruncated = true; break; }
				const FString Entry = FString::Printf(TEXT("%s{\"name\":\"%s\",%s}"),
					(Count ? TEXT(",") : TEXT("")),
					*TacticalAnimAuthoring::JsonEscape(Socket->SocketName.ToString()),
					*TacticalAnimAuthoring::XformJson(Socket->RelativeLocation, Socket->RelativeRotation, Socket->RelativeScale));

				// Measure the COMPLETE entry in UTF-8 bytes (FString::Len() counts TCHARs, not bytes)
				// and decide BEFORE appending, so a partial entry is never emitted.
				const int32 EntryBytes = FTCHARToUTF8(*Entry).Length();
				if (AccumBytes + EntryBytes > TacticalAnimAuthoring::kMaxSocketsJsonBytes) { bTruncated = true; break; }

				Items += Entry;
				AccumBytes += EntryBytes;
				++Count;
			}

			OutValue = FString::Printf(
				TEXT("{\"asset\":\"%s\",\"socketCount\":%d,\"returned\":%d,\"truncated\":%s,\"socketsJsonBytes\":%d,")
				TEXT("\"limits\":{\"maxSocketsReturned\":%d,\"maxSocketsJsonBytes\":%d},\"sockets\":[%s]}"),
				*TacticalAnimAuthoring::JsonEscape(Mesh->GetPathName()), Total, Count,
				bTruncated ? TEXT("true") : TEXT("false"), AccumBytes,
				TacticalAnimAuthoring::kMaxSocketsReturned, TacticalAnimAuthoring::kMaxSocketsJsonBytes, *Items);
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::AddStaticMeshSocketDeferred(
	const FString& AssetPath, const FString& SocketName,
	float LocationX, float LocationY, float LocationZ,
	float Pitch, float Yaw, float Roll,
	float ScaleX, float ScaleY, float ScaleZ)
{
	return TacticalAnimAuthoring::RunDeferredString(
		[=](FString& OutValue, FString& OutError) -> bool
		{
			check(IsInGameThread());

			// ---------- validation: ALL of it before any mutation / transaction ----------
			UStaticMesh* Mesh = TacticalAnimAuthoring::LoadStaticMeshAsset(AssetPath, OutError);
			if (!Mesh) { return false; }
			if (!TacticalAnimAuthoring::ValidateSocketName(SocketName, OutError)) { return false; }

			const FVector  NewLoc((double)LocationX, (double)LocationY, (double)LocationZ);
			const FRotator NewRot((double)Pitch, (double)Yaw, (double)Roll);
			const FVector  NewScale((double)ScaleX, (double)ScaleY, (double)ScaleZ);
			if (!TacticalAnimAuthoring::ValidateSocketTransform(NewLoc, NewRot, NewScale, OutError)) { return false; }

			const FName SocketFName(*SocketName);
			if (Mesh->FindSocket(SocketFName) != nullptr)
			{ OutError = FString::Printf(TEXT("Socket '%s' already exists on %s; duplicates are rejected."), *SocketName, *Mesh->GetPathName()); return false; }

			UPackage* Package = Mesh->GetOutermost();
			const bool bWasDirty = Package ? Package->IsDirty() : false;
			const FString MeshPath = Mesh->GetPathName();

			// ---------- mutation + readback + rollback, ALL inside the live transaction ----------
			bool bSucceeded = false;
			FString Payload;
			{
				FScopedTransaction Transaction(NSLOCTEXT("TacticalAnimAuthoring", "AddStaticMeshSocket", "Add Static Mesh Socket"));

				UStaticMeshSocket* NewSocket = NewObject<UStaticMeshSocket>(Mesh);
				if (!NewSocket)
				{
					Transaction.Cancel();
					if (Package && !bWasDirty) { Package->SetDirtyFlag(false); }
					OutError = TEXT("Failed to create UStaticMeshSocket.");
					return false;
				}
				NewSocket->SocketName = SocketFName;
				NewSocket->RelativeLocation = NewLoc;
				NewSocket->RelativeRotation = NewRot;
				NewSocket->RelativeScale = NewScale;
				NewSocket->SetFlags(RF_Transactional);

				Mesh->PreEditChange(nullptr);
				Mesh->AddSocket(NewSocket);
				Mesh->PostEditChange();
				Mesh->MarkPackageDirty();

				// Identity-strict readback: the stored socket must be the EXACT object we created.
				UStaticMeshSocket* Stored = Mesh->FindSocket(SocketFName);
				const bool bOk = (Stored == NewSocket)
					&& Stored->SocketName == SocketFName
					&& Stored->RelativeLocation.Equals(NewLoc, TacticalAnimAuthoring::kSocketMatchTolerance)
					&& TacticalAnimAuthoring::RotatorComponentsEqual(Stored->RelativeRotation, NewRot, TacticalAnimAuthoring::kSocketMatchTolerance)
					&& Stored->RelativeScale.Equals(NewScale, TacticalAnimAuthoring::kSocketMatchTolerance);

				if (!bOk)
				{
					// Remove that exact pointer through the proper mesh edit path, then cancel the
					// transaction so no undo entry can resurrect the failed mutation.
					Mesh->PreEditChange(nullptr);
					Mesh->RemoveSocket(NewSocket);
					Mesh->PostEditChange();
					Transaction.Cancel();
					if (Package && !bWasDirty) { Package->SetDirtyFlag(false); }
					TacticalAnimAuthoring::GToolAddedSockets.Remove(TacticalAnimAuthoring::SocketKey(MeshPath, SocketName));
					OutError = TEXT("Socket readback did not match the requested socket object/values; the socket was removed, the transaction cancelled, and the prior dirty state restored.");
					return false;
				}

				TacticalAnimAuthoring::GToolAddedSockets.Add(
					TacticalAnimAuthoring::SocketKey(MeshPath, SocketName), TWeakObjectPtr<UStaticMeshSocket>(NewSocket));

				Payload = FString::Printf(
					TEXT("{\"asset\":\"%s\",\"socketName\":\"%s\",\"added\":true,%s,\"socketCount\":%d,\"packageDirty\":%s,\"saved\":false}"),
					*TacticalAnimAuthoring::JsonEscape(MeshPath),
					*TacticalAnimAuthoring::JsonEscape(SocketName),
					*TacticalAnimAuthoring::XformJson(Stored->RelativeLocation, Stored->RelativeRotation, Stored->RelativeScale),
					Mesh->Sockets.Num(),
					(Package && Package->IsDirty()) ? TEXT("true") : TEXT("false"));
				bSucceeded = true;
			}

			if (!bSucceeded) { return false; }
			OutValue = Payload;
			return true;
		});
}

UToolCallAsyncResultString* UTacticalAnimAuthoringToolset::SetStaticMeshSocketTransformDeferred(
	const FString& AssetPath, const FString& SocketName,
	float LocationX, float LocationY, float LocationZ,
	float Pitch, float Yaw, float Roll,
	float ScaleX, float ScaleY, float ScaleZ,
	bool bExpectPriorTransform,
	float ExpectLocationX, float ExpectLocationY, float ExpectLocationZ,
	float ExpectPitch, float ExpectYaw, float ExpectRoll,
	float ExpectScaleX, float ExpectScaleY, float ExpectScaleZ)
{
	return TacticalAnimAuthoring::RunDeferredString(
		[=](FString& OutValue, FString& OutError) -> bool
		{
			check(IsInGameThread());

			// ---------- validation: ALL of it before any mutation / transaction ----------
			UStaticMesh* Mesh = TacticalAnimAuthoring::LoadStaticMeshAsset(AssetPath, OutError);
			if (!Mesh) { return false; }
			if (!TacticalAnimAuthoring::ValidateSocketName(SocketName, OutError)) { return false; }

			const FVector  NewLoc((double)LocationX, (double)LocationY, (double)LocationZ);
			const FRotator NewRot((double)Pitch, (double)Yaw, (double)Roll);
			const FVector  NewScale((double)ScaleX, (double)ScaleY, (double)ScaleZ);
			if (!TacticalAnimAuthoring::ValidateSocketTransform(NewLoc, NewRot, NewScale, OutError)) { return false; }

			const FName SocketFName(*SocketName);
			UStaticMeshSocket* Socket = Mesh->FindSocket(SocketFName);
			if (!Socket)
			{ OutError = FString::Printf(TEXT("Socket '%s' does not exist on %s."), *SocketName, *Mesh->GetPathName()); return false; }

			const FString MeshPath = Mesh->GetPathName();

			// Provenance is by EXACT object identity. A same-named replacement is a different
			// object, so it is never trusted and always requires the expected-prior-transform CAS.
			const bool bToolAdded = TacticalAnimAuthoring::IsToolAddedSocket(MeshPath, SocketName, Socket);
			FString MatchedBy;
			if (bToolAdded)
			{
				MatchedBy = TEXT("tool-added-this-session");
			}
			else
			{
				if (!bExpectPriorTransform)
				{
					OutError = FString::Printf(
						TEXT("Socket '%s' was not added by this tool in this session as this exact object; supply bExpectPriorTransform=true with its complete expected prior transform."),
						*SocketName);
					return false;
				}
				const FVector  ExpLoc((double)ExpectLocationX, (double)ExpectLocationY, (double)ExpectLocationZ);
				const FRotator ExpRot((double)ExpectPitch, (double)ExpectYaw, (double)ExpectRoll);
				const FVector  ExpScale((double)ExpectScaleX, (double)ExpectScaleY, (double)ExpectScaleZ);
				if (!TacticalAnimAuthoring::ValidateSocketTransform(ExpLoc, ExpRot, ExpScale, OutError)) { return false; }

				if (!Socket->RelativeLocation.Equals(ExpLoc, TacticalAnimAuthoring::kSocketMatchTolerance)
					|| !TacticalAnimAuthoring::RotatorComponentsEqual(Socket->RelativeRotation, ExpRot, TacticalAnimAuthoring::kSocketMatchTolerance)
					|| !Socket->RelativeScale.Equals(ExpScale, TacticalAnimAuthoring::kSocketMatchTolerance))
				{
					OutError = FString::Printf(
						TEXT("Expected prior transform does not match the stored socket (stale). Stored: loc(%.6f,%.6f,%.6f) rot(%.6f,%.6f,%.6f) scale(%.6f,%.6f,%.6f). No mutation performed."),
						Socket->RelativeLocation.X, Socket->RelativeLocation.Y, Socket->RelativeLocation.Z,
						Socket->RelativeRotation.Pitch, Socket->RelativeRotation.Yaw, Socket->RelativeRotation.Roll,
						Socket->RelativeScale.X, Socket->RelativeScale.Y, Socket->RelativeScale.Z);
					return false;
				}
				MatchedBy = TEXT("expected-prior-transform");
			}

			UPackage* Package = Mesh->GetOutermost();
			const bool bWasDirty = Package ? Package->IsDirty() : false;
			const FVector  OldLoc = Socket->RelativeLocation;
			const FRotator OldRot = Socket->RelativeRotation;
			const FVector  OldScale = Socket->RelativeScale;

			// TRUE NO-OP: if the requested transform already matches component-wise within tolerance,
			// return without opening a transaction and without any edit notification. Nothing is
			// dirtied and NO undo entry is created; the package's prior dirty state is untouched.
			if (Socket->RelativeLocation.Equals(NewLoc, TacticalAnimAuthoring::kSocketMatchTolerance)
				&& TacticalAnimAuthoring::RotatorComponentsEqual(Socket->RelativeRotation, NewRot, TacticalAnimAuthoring::kSocketMatchTolerance)
				&& Socket->RelativeScale.Equals(NewScale, TacticalAnimAuthoring::kSocketMatchTolerance))
			{
				OutValue = FString::Printf(
					TEXT("{\"asset\":\"%s\",\"socketName\":\"%s\",\"updated\":false,\"noOp\":true,\"matchedBy\":\"%s\",")
					TEXT("\"changedProperties\":[],%s,\"packageDirty\":%s,\"saved\":false}"),
					*TacticalAnimAuthoring::JsonEscape(MeshPath),
					*TacticalAnimAuthoring::JsonEscape(SocketName),
					*MatchedBy,
					*TacticalAnimAuthoring::XformJson(Socket->RelativeLocation, Socket->RelativeRotation, Socket->RelativeScale),
					(Package && Package->IsDirty()) ? TEXT("true") : TEXT("false"));
				return true;
			}

			// ---------- mutation + readback + rollback, ALL inside the live transaction ----------
			bool bSucceeded = false;
			FString Payload;
			{
				FScopedTransaction Transaction(NSLOCTEXT("TacticalAnimAuthoring", "SetStaticMeshSocketTransform", "Set Static Mesh Socket Transform"));

				// Notify PER PROPERTY. SSocketManager's listener switches on the changed property name
				// (RelativeLocation vs RelativeRotation), so a location-only event would leave
				// rotation-facing editor state stale. Every transform property that actually changes
				// gets its own PreEditChange / assign / PostEditChangeProperty cycle, all inside this
				// same transaction.
				FProperty* LocProp   = FindFProperty<FProperty>(UStaticMeshSocket::StaticClass(), GET_MEMBER_NAME_CHECKED(UStaticMeshSocket, RelativeLocation));
				FProperty* RotProp   = FindFProperty<FProperty>(UStaticMeshSocket::StaticClass(), GET_MEMBER_NAME_CHECKED(UStaticMeshSocket, RelativeRotation));
				FProperty* ScaleProp = FindFProperty<FProperty>(UStaticMeshSocket::StaticClass(), GET_MEMBER_NAME_CHECKED(UStaticMeshSocket, RelativeScale));

				auto ApplySocketProperty = [Socket](FProperty* Prop, TFunctionRef<void()> Assign)
				{
					Socket->PreEditChange(Prop);
					Socket->Modify();
					Assign();
					if (Prop) { FPropertyChangedEvent Changed(Prop); Socket->PostEditChangeProperty(Changed); }
					else { Socket->PostEditChange(); }
				};

				FString ChangedProps;
				const bool bLocChanged   = !Socket->RelativeLocation.Equals(NewLoc, 0.0);
				const bool bRotChanged   = !TacticalAnimAuthoring::RotatorComponentsEqual(Socket->RelativeRotation, NewRot, 0.0);
				const bool bScaleChanged = !Socket->RelativeScale.Equals(NewScale, 0.0);

				if (bLocChanged)
				{
					ApplySocketProperty(LocProp, [&]() { Socket->RelativeLocation = NewLoc; });
					ChangedProps += TEXT("\"RelativeLocation\"");
				}
				if (bRotChanged)
				{
					ApplySocketProperty(RotProp, [&]() { Socket->RelativeRotation = NewRot; });
					ChangedProps += FString(ChangedProps.IsEmpty() ? TEXT("") : TEXT(",")) + TEXT("\"RelativeRotation\"");
				}
				if (bScaleChanged)
				{
					ApplySocketProperty(ScaleProp, [&]() { Socket->RelativeScale = NewScale; });
					ChangedProps += FString(ChangedProps.IsEmpty() ? TEXT("") : TEXT(",")) + TEXT("\"RelativeScale\"");
				}
				Mesh->MarkPackageDirty();

				// Identity-strict readback: the stored socket must still be the EXACT original object.
				UStaticMeshSocket* Stored = Mesh->FindSocket(SocketFName);
				const bool bOk = (Stored == Socket)
					&& Stored->RelativeLocation.Equals(NewLoc, TacticalAnimAuthoring::kSocketMatchTolerance)
					&& TacticalAnimAuthoring::RotatorComponentsEqual(Stored->RelativeRotation, NewRot, TacticalAnimAuthoring::kSocketMatchTolerance)
					&& Stored->RelativeScale.Equals(NewScale, TacticalAnimAuthoring::kSocketMatchTolerance);

				if (!bOk)
				{
					// Restore that exact object with the SAME per-property notification pattern (so
					// rotation/scale listeners are not left stale by a location-only event), then cancel
					// so no undo entry survives, and drop provenance that can no longer be trusted.
					if (bLocChanged)   { ApplySocketProperty(LocProp,   [&]() { Socket->RelativeLocation = OldLoc; }); }
					if (bRotChanged)   { ApplySocketProperty(RotProp,   [&]() { Socket->RelativeRotation = OldRot; }); }
					if (bScaleChanged) { ApplySocketProperty(ScaleProp, [&]() { Socket->RelativeScale = OldScale; }); }
					Transaction.Cancel();
					if (Package && !bWasDirty) { Package->SetDirtyFlag(false); }
					if (Stored != Socket)
					{
						TacticalAnimAuthoring::GToolAddedSockets.Remove(TacticalAnimAuthoring::SocketKey(MeshPath, SocketName));
					}
					OutError = TEXT("Socket readback did not match the requested socket object/values; the original transform was restored, the transaction cancelled, and the prior dirty state restored.");
					return false;
				}

				Payload = FString::Printf(
					TEXT("{\"asset\":\"%s\",\"socketName\":\"%s\",\"updated\":true,\"noOp\":false,\"matchedBy\":\"%s\",\"changedProperties\":[%s],%s,\"packageDirty\":%s,\"saved\":false}"),
					*TacticalAnimAuthoring::JsonEscape(MeshPath),
					*TacticalAnimAuthoring::JsonEscape(SocketName),
					*MatchedBy, *ChangedProps,
					*TacticalAnimAuthoring::XformJson(Stored->RelativeLocation, Stored->RelativeRotation, Stored->RelativeScale),
					(Package && Package->IsDirty()) ? TEXT("true") : TEXT("false"));
				bSucceeded = true;
			}

			if (!bSucceeded) { return false; }
			OutValue = Payload;
			return true;
		});
}
