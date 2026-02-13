"""Facial rig test script - Backward-compatible facade.

This module provides backward compatibility for code that imports from
mayaLib.test.facial3. All functionality has been refactored into the
new modular structure at mayaLib.rigLib.face/.

New code should import directly from:
    - mayaLib.rigLib.face.constants
    - mayaLib.rigLib.face.utils
    - mayaLib.rigLib.face.widgets
    - mayaLib.rigLib.face.io
    - mayaLib.rigLib.face.operations
    - mayaLib.rigLib.face.skin

Example:
    # Old (still works via this facade):
    from mayaLib.test.facial3 import PerseusUI, maya_main_window

    # New (recommended):
    from mayaLib.rigLib.face.widgets.perseus_ui import PerseusUI
    from mayaLib.rigLib.face.utils import maya_main_window
"""

# =============================================================================
# Constants
# =============================================================================
# =============================================================================
# Arise Integration
# =============================================================================
from mayaLib.rigLib.face.arise_face_node import (
    AriseFaceNode,
    AriseFaceRig,
    create_arise_face_node,
)
from mayaLib.rigLib.face.constants import (
    DARK_COLOR_A,
    DARK_COLOR_B,
    DARK_COLOR_C,
    DEFAULT_COLOR,
    DEFINE_COLOR,
    DEFINE_COLOR_2,
    EDGE_COLOR,
    EDGE_INDEX_COLOR,
    FILE_EXT,
    LEGACY_COLOR_MAPPING,
    PACK_EXT,
    PROGRESS_COLOR,
    SELECTION_COLOR,
    Colors,
    MayaOverrideColors,
)
from mayaLib.rigLib.face.io.ctrl_shapes_io import (
    export_ctrl_shapes,
    export_ctrl_shapes_no_ui,
    import_ctrl_shapes,
    import_ctrl_shapes_no_ui,
)

# =============================================================================
# File I/O Operations
# =============================================================================
from mayaLib.rigLib.face.io.settings_io import (
    get_associated_curve_path,
    get_default_settings,
    load_settings,
    merge_with_defaults,
    save_settings,
    to_json,
    validate_settings,
)
from mayaLib.rigLib.face.io.skin_io import (
    apply_skin_data,
    collect_blend_weights,
    collect_influence_weights,
    collect_skin_data,
    export_selection,
    export_skin,
    export_skin_pack,
    get_current_weights,
    get_geometry_components,
    import_skin,
    import_skin_pack,
    set_blend_weights,
    set_influence_weights,
)
from mayaLib.rigLib.face.io.skin_io import (
    get_skin_cluster as io_get_skin_cluster,
)

# =============================================================================
# Curve Operations
# =============================================================================
from mayaLib.rigLib.face.operations.curve_operations import (
    CurveDirection,
    calculate_curve_parameter_distances,
    create_locator_on_curve,
    create_mirrored_curve_instance,
    create_point_on_curve_info,
    delete_projected_curve_group,
    ensure_curve_direction,
    get_curve_cv_count,
    get_curve_cv_position,
    get_curve_length,
    parent_curve_to_group,
    project_all_facial_curves,
    project_brow_curve,
    project_cheek_curve,
    project_curve_onto_mesh,
    project_jaw_curve,
    rebuild_facial_curve,
    reconnect_curve_to_poc_nodes,
    rename_curve_after_projection,
    reverse_curve,
    select_frontmost_projected_curve,
    set_curve_display_color,
)

# =============================================================================
# Edge Detection Operations
# =============================================================================
from mayaLib.rigLib.face.operations.edge_detection import (
    Direction,
    convert_to_edge_loop,
    convert_to_edge_ring,
    disable_edge_loop_mode,
    edges_to_vertices,
    enable_edge_loop_mode,
    find_edge_up_down,
    find_edge_up_down_tongue,
    fix_edge_loop_direction,
    get_edge_vertices,
    toggle_edge_loop_mode,
    vertices_to_edges,
)

# =============================================================================
# Geometry Selection Operations
# =============================================================================
from mayaLib.rigLib.face.operations.geometry_selection import (
    SelectionType,
    clear_selection,
    convert_selection_to_contained_edges,
    convert_selection_to_contained_faces,
    convert_selection_to_edges,
    convert_selection_to_faces,
    convert_selection_to_vertices,
    get_component_indices,
    get_current_selection,
    get_foreground_face_selection,
    get_geometry_with_namespace_removal,
    get_mesh_from_component,
    get_selection_center,
    get_vertex_positions,
    get_vertices_excluding_joints,
    grow_polygon_selection,
    invert_selection,
    remove_namespace_from_object,
    restore_selection,
    select_all_vertices,
    set_component_selection_mode,
    shrink_polygon_selection,
    store_edge_selection,
    store_vertex_selection,
    update_selection_mode_icons,
    validate_vertex_selection,
)

# =============================================================================
# Skin Cluster Utilities
# =============================================================================
from mayaLib.rigLib.face.skin.cluster_utils import (
    add_influences,
    bind_skin,
    disable_inherits_transform,
    find_related_skin_cluster,
    get_all_skinned_objects,
    get_influence_count,
    get_influences,
    get_max_influences,
    get_normalize_weights,
    get_skinning_method,
    get_vertex_weights,
    get_weighted_influences,
    has_skin_cluster,
    lock_influence_weights,
    prune_weights,
    rebind_skin,
    remove_influences,
    reset_bind_pose,
    select_skinned_objects,
    set_max_influences,
    set_normalize_weights,
    set_skinning_method,
    set_vertex_weights,
    smooth_weights,
    unbind_skin,
)

# =============================================================================
# Skin Copy Operations
# =============================================================================
from mayaLib.rigLib.face.skin.copy import (
    attach_skin_joint_connection,
    clear_vertex_selections,
    connect_blendshape,
    connect_blendshape_node,
    connect_eye_target_space,
    connect_wrap_deformer,
    copy_pivot,
    copy_skin_global,
    copy_skin_main,
    destination_define,
    detach_skin_joint_connection,
    get_destination_vertices,
    get_skin_cluster,
    get_source_vertices,
    hammer_skin_weights,
    save_facial_skin_set,
    skin_copy,
    source_define,
    transfer_facial_skin_set,
)

# =============================================================================
# Joint Connection Utilities
# =============================================================================
from mayaLib.rigLib.face.skin.joint_connection import (
    attach_bind_joints,
    clear_all_connection_data,
    clear_connection_data,
    decode_data_from_attr,
    detach_bind_joints,
    encode_data_to_attr,
    get_connection_data,
    get_detached_joints,
    has_detached_connections,
)

# =============================================================================
# Utility Functions
# =============================================================================
from mayaLib.rigLib.face.utils import (
    # Legacy function names
    findMainName,
    findMainNameB,
    get_license_string,
    get_short_license_string,
    maya_main_window,
)

# =============================================================================
# Widget Classes
# =============================================================================
from mayaLib.rigLib.face.widgets.head_geo_widget import HeadGeoWidget
from mayaLib.rigLib.face.widgets.perseus_ui import (
    CustomTabWidget,
    PerseusUI,
)
from mayaLib.rigLib.face.widgets.settings_widget import SettingsWidget
from mayaLib.rigLib.face.widgets.skin_widget import SkinWidget

# =============================================================================
# Module Exports
# =============================================================================
__all__ = [
    # Constants
    "FILE_EXT",
    "PACK_EXT",
    "EDGE_COLOR",
    "SELECTION_COLOR",
    "EDGE_INDEX_COLOR",
    "DARK_COLOR_A",
    "DARK_COLOR_B",
    "DARK_COLOR_C",
    "DEFAULT_COLOR",
    "PROGRESS_COLOR",
    "DEFINE_COLOR",
    "DEFINE_COLOR_2",
    "LEGACY_COLOR_MAPPING",
    "Colors",
    "MayaOverrideColors",
    # Utility Functions
    "maya_main_window",
    "get_license_string",
    "get_short_license_string",
    "findMainName",
    "findMainNameB",
    # Widget Classes
    "HeadGeoWidget",
    "SettingsWidget",
    "SkinWidget",
    "CustomTabWidget",
    "PerseusUI",
    # File I/O
    "save_settings",
    "load_settings",
    "get_default_settings",
    "validate_settings",
    "merge_with_defaults",
    "get_associated_curve_path",
    "to_json",
    "io_get_skin_cluster",
    "get_geometry_components",
    "get_current_weights",
    "collect_influence_weights",
    "collect_blend_weights",
    "collect_skin_data",
    "set_influence_weights",
    "set_blend_weights",
    "apply_skin_data",
    "export_skin",
    "export_skin_pack",
    "import_skin",
    "import_skin_pack",
    "export_selection",
    "export_ctrl_shapes",
    "import_ctrl_shapes",
    "export_ctrl_shapes_no_ui",
    "import_ctrl_shapes_no_ui",
    # Edge Detection
    "Direction",
    "fix_edge_loop_direction",
    "find_edge_up_down",
    "find_edge_up_down_tongue",
    "enable_edge_loop_mode",
    "disable_edge_loop_mode",
    "toggle_edge_loop_mode",
    "convert_to_edge_loop",
    "convert_to_edge_ring",
    "get_edge_vertices",
    "edges_to_vertices",
    "vertices_to_edges",
    # Curve Operations
    "CurveDirection",
    "get_curve_cv_position",
    "get_curve_cv_count",
    "calculate_curve_parameter_distances",
    "get_curve_length",
    "project_curve_onto_mesh",
    "select_frontmost_projected_curve",
    "rebuild_facial_curve",
    "ensure_curve_direction",
    "reverse_curve",
    "set_curve_display_color",
    "create_point_on_curve_info",
    "reconnect_curve_to_poc_nodes",
    "create_mirrored_curve_instance",
    "create_locator_on_curve",
    "delete_projected_curve_group",
    "parent_curve_to_group",
    "rename_curve_after_projection",
    "project_brow_curve",
    "project_jaw_curve",
    "project_cheek_curve",
    "project_all_facial_curves",
    # Geometry Selection
    "SelectionType",
    "get_current_selection",
    "convert_selection_to_vertices",
    "convert_selection_to_contained_edges",
    "convert_selection_to_edges",
    "convert_selection_to_faces",
    "convert_selection_to_contained_faces",
    "get_vertices_excluding_joints",
    "grow_polygon_selection",
    "shrink_polygon_selection",
    "invert_selection",
    "remove_namespace_from_object",
    "get_geometry_with_namespace_removal",
    "select_all_vertices",
    "get_foreground_face_selection",
    "validate_vertex_selection",
    "get_vertex_positions",
    "get_selection_center",
    "store_edge_selection",
    "store_vertex_selection",
    "restore_selection",
    "clear_selection",
    "update_selection_mode_icons",
    "set_component_selection_mode",
    "get_mesh_from_component",
    "get_component_indices",
    # Skin Copy
    "get_skin_cluster",
    "skin_copy",
    "source_define",
    "destination_define",
    "copy_skin_global",
    "copy_skin_main",
    "hammer_skin_weights",
    "copy_pivot",
    "connect_blendshape",
    "connect_blendshape_node",
    "connect_wrap_deformer",
    "connect_eye_target_space",
    "save_facial_skin_set",
    "transfer_facial_skin_set",
    "detach_skin_joint_connection",
    "attach_skin_joint_connection",
    "get_source_vertices",
    "get_destination_vertices",
    "clear_vertex_selections",
    # Skin Cluster Utilities
    "find_related_skin_cluster",
    "has_skin_cluster",
    "get_all_skinned_objects",
    "select_skinned_objects",
    "get_influences",
    "get_influence_count",
    "get_max_influences",
    "set_max_influences",
    "get_skinning_method",
    "set_skinning_method",
    "get_normalize_weights",
    "set_normalize_weights",
    "add_influences",
    "remove_influences",
    "lock_influence_weights",
    "get_weighted_influences",
    "prune_weights",
    "smooth_weights",
    "unbind_skin",
    "bind_skin",
    "rebind_skin",
    "reset_bind_pose",
    "disable_inherits_transform",
    "get_vertex_weights",
    "set_vertex_weights",
    # Joint Connection
    "encode_data_to_attr",
    "decode_data_from_attr",
    "detach_bind_joints",
    "attach_bind_joints",
    "has_detached_connections",
    "get_detached_joints",
    "get_connection_data",
    "clear_connection_data",
    "clear_all_connection_data",
    # Arise Integration
    "AriseFaceNode",
    "AriseFaceRig",
    "create_arise_face_node",
]
