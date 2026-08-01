"""Shared read-only-first helpers for Operation Sunscar UE editor automation."""

import csv
import json
import os
from datetime import datetime, timezone

import unreal


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(SCRIPT_DIRECTORY, "old_town_automation_config.json")


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as handle:
        return json.load(handle)


def timestamp_utc():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def project_directory():
    return os.path.abspath(unreal.Paths.project_dir())


def project_name():
    return os.path.splitext(os.path.basename(unreal.Paths.get_project_file_path()))[0]


def current_level_path():
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    current_level = level_subsystem.get_current_level()
    if current_level is None:
        return ""
    return current_level.get_outermost().get_name()


def require_safe_context(config, write_requested=False):
    errors = []
    actual_project = project_name()
    actual_directory = project_directory().replace("\\", "/").rstrip("/")
    expected_suffix = config["expected_project_directory_suffix"].replace("\\", "/").rstrip("/")
    actual_level = current_level_path()

    if actual_project != config["expected_project_name"]:
        errors.append("wrong_project:%s" % actual_project)
    if not actual_directory.endswith(expected_suffix):
        errors.append("wrong_project_directory:%s" % actual_directory)
    if actual_level != config["expected_level"]:
        errors.append("wrong_level:%s" % actual_level)

    execution = config.get("execution", {})
    if write_requested:
        if not execution.get("apply_changes", False):
            errors.append("apply_changes_disabled")
        if execution.get("approval_token", "") != execution.get("required_approval_token", ""):
            errors.append("approval_token_missing_or_incorrect")
        if execution.get("save_current_level", False):
            errors.append("automatic_level_save_forbidden_in_v1")

    if errors:
        raise RuntimeError("SUNSCAR_PREFLIGHT_FAILED " + " | ".join(errors))

    return {
        "project": actual_project,
        "project_directory": actual_directory,
        "level": actual_level,
        "write_requested": bool(write_requested),
        "verified_at_utc": timestamp_utc(),
    }


def actor_subsystem():
    return unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def editor_world():
    return unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()


def actor_tags(actor):
    return [str(tag) for tag in actor.tags]


def actor_folder(actor):
    try:
        return str(actor.get_folder_path())
    except Exception:
        return ""


def actor_mesh_path(actor):
    component = getattr(actor, "static_mesh_component", None)
    if component is None:
        try:
            components = actor.get_components_by_class(unreal.StaticMeshComponent)
            component = components[0] if components else None
        except Exception:
            component = None
    if component is None:
        return ""
    try:
        mesh = component.get_editor_property("static_mesh")
    except Exception:
        mesh = None
    return mesh.get_path_name() if mesh else ""


def report_directory(config):
    directory = os.path.join(unreal.Paths.project_saved_dir(), config["report_directory"])
    os.makedirs(directory, exist_ok=True)
    return directory


def write_json_report(config, filename, payload):
    path = os.path.join(report_directory(config), filename)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, sort_keys=False)
        handle.write("\n")
    unreal.log("SUNSCAR_REPORT_JSON=" + path)
    return path


def write_csv_report(config, filename, rows, headers):
    path = os.path.join(report_directory(config), filename)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    unreal.log("SUNSCAR_REPORT_CSV=" + path)
    return path


def planning_file(config, filename_key):
    return os.path.join(project_directory(), config["planning_directory"], config[filename_key])


def read_csv(path):
    with open(path, "r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def read_json(path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def has_any_term(value, terms):
    lowered = str(value).lower()
    return any(str(term).lower() in lowered for term in terms)


def safe_asset_ref_to_path(asset_ref, registry):
    if asset_ref.startswith("project://"):
        return asset_ref[len("project://"):]
    if asset_ref.startswith("/Game/"):
        return asset_ref
    if asset_ref.startswith("source://") or asset_ref.startswith("map-owned://"):
        return registry.get("resolved_refs", {}).get(asset_ref, "")
    return ""


def asset_path_allowed(config, asset_path):
    if not asset_path:
        return False
    if any(asset_path.startswith(prefix) for prefix in config["protected_asset_prefixes"]):
        return False
    return any(asset_path.startswith(prefix) for prefix in config["allowed_asset_prefixes"])


def load_asset_checked(config, asset_path):
    if not asset_path_allowed(config, asset_path):
        raise RuntimeError("SUNSCAR_ASSET_PATH_NOT_ALLOWED " + asset_path)
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset is None:
        raise RuntimeError("SUNSCAR_ASSET_MISSING " + asset_path)
    return asset
