"""
Facial Rig - A modular facial rigging system for Maya.

Extracted and refactored from AdvancedSkeleton MEL workflow.
Provides a clean, reusable Python API using maya.cmds.

Modules:
    core: Base classes and configuration
    components: Individual facial rig components (eyelid, lip, eyebrow, etc.)
    utils: Utility functions for common operations

Usage:
    # Interactive fitting workflow
    from facial_rig import show_fitting_ui
    show_fitting_ui("head_geo")

    # After fitting, build the rig
    from facial_rig import FacialRigBuilder, FacialRigConfig
    config = FacialRigConfig(geometry="head_geo", ...)
    builder = FacialRigBuilder(config)
    builder.build()
"""

__version__ = "1.0.0"
__author__ = "Facial Rig System"

from . import components, core, utils

# Builder
from .builder import FacialRigBuilder, build_facial_rig

# Convenience exports for components
from .components import (
    ARKitComponent,
    CheekComponent,
    EyeBrowComponent,
    EyeComponent,
    EyeLidComponent,
    ForeheadComponent,
    JawComponent,
    LipComponent,
    NoseComponent,
    TongueComponent,
    connect_arkit_source,
    create_arkit_blendshapes,
)
from .core.advanced_base import ensure_advanced_base
from .core.arise_bridge import apply_options, build_face, delete_face, face_rig_nodes
from .core.arise_naming import arise_name, rename_to_arise
from .core.auto_fitting import (
    AUTO_FIT_SOURCES,
    AutoFitSource,
    auto_face_fitting,
    detect_auto_fit_source,
)
from .core.base import FacialComponent
from .core.build_steps import (
    BUILD_STEPS,
    reset_build_step,
    step_build_complete,
    step_build_prep,
)
from .core.build_utils import (
    as_align,
    as_create_mult_dl,
    as_face_hide_controllers,
    as_lock_attr,
    as_matrix_connect_attr,
    as_opm_scale_reset,
    as_parent_constraint,
    as_parent_constraint_blend,
)

# Core classes
from .core.config import ColorScheme, FacialRigConfig, FitData
from .core.ctrl_box import (
    add_ctrl_box2_shape,
    create_ctrl_box_slider,
    create_face_controller,
    face_control_orient,
    face_ctrl_box,
    place_ctrl_by_projection,
)
from .core.driving_system import (
    ctrl_to_bw,
    ds_sdk,
    ensure_blend_weighted,
    ensure_output_blend_weighted,
    ensure_sdk_curves_named,
    face_ds_finish,
    mirror_connect_ctrls,
    store_as_ds_sdk,
)
from .core.eye_ball import face_eye_ball
from .core.eye_lid import face_eye_lid
from .core.face_arkit import connect_arkit
from .core.face_cage import face_face_cage, guess_cage_smooth
from .core.face_cage_to_skin import (
    face_cage_to_skin,
    face_cage_weights_remove,
    face_cheek_cage_smooth_update,
    face_face_cage_finish,
)
from .core.face_cheek_raiser import face_cheek_finish, face_cheek_raiser, face_cheek_raiser_finish
from .core.face_ctrl_pp import (
    create_pp,
    face_add_constrained,
    face_half_moon_curve,
    set_rgb_override_color,
    weight_hammer_verts_ms,
)
from .core.face_delta_mush import (
    connect_delta_mush_scale,
    create_delta_mush,
    delete_delta_mush,
    delta_mush_zero_weight,
    paint_delta_mush,
)
from .core.face_emotions import face_emotions
from .core.face_eye_aim import face_eye_aim
from .core.face_eye_blink import face_eye_blink, face_eye_blink_finish
from .core.face_eye_brow import face_eye_brow
from .core.face_eye_wide import face_eye_wide, face_eye_wide_finish
from .core.face_finish import FACE_RIG_VERSION, face_ds_sdk, face_finish
from .core.face_frown_pull import (
    face_cheek,
    face_frown_pull,
    face_frown_pull_finish,
    face_narrow_smile_and_frown,
    face_smile_pull_controller,
)
from .core.face_head_squash import (
    add_to_head_squash,
    create_head_squash,
    delete_head_squash,
    optimize_head_squash,
)
from .core.face_jaw_open import face_jaw_open, face_jaw_open_finish
from .core.face_lip_down import face_lip_down, face_lip_down_finish
from .core.face_lip_falloff import face_lip_falloff
from .core.face_lip_side import face_lip_side, face_lip_side_finish
from .core.face_lip_up import face_lip_up, face_lip_up_finish
from .core.face_phonemes import face_phonemes
from .core.face_prep import (
    face_prep,
    get_max_influences,
    include_above_eyes,
    include_below_eyes,
    set_fixed_wrap_options,
)
from .core.face_pupil_iris import face_pupil_iris
from .core.face_rebuild_restore import face_rebuild_restore
from .core.face_regions import face_regions
from .core.face_smile_pull import (
    create_custom_blended_attribute,
    face_smile_pull,
    face_smile_pull_finish,
)
from .core.face_snarl import face_snarl, face_snarl_finish
from .core.face_squint import face_squint, face_squint_finish
from .core.face_tongue import face_tongue, face_tongue_finish
from .core.face_up_mid_lo import face_up_mid_lo
from .core.fit_options import (
    FIT_OPTIONS,
    FitOption,
    get_fit_option,
    get_left_suffix,
    set_fit_option,
)
from .core.fitting import (
    FacialFitting,
    FitRegion,
    FittingUI,
    FitType,
    face_fit_anim,
    face_fit_delete,
    face_fit_hide,
    face_fit_reselect,
    face_fit_swap_upper_lower,
    get_face_fit_selection,
    get_face_fit_selection_other_object,
    remove_fit_anim_from_ctrl_box,
    remove_fit_animations_from_on_face_ctrls,
    toggle_fit_face,
)
from .core.hierarchy import HierarchyManager
from .core.jaw_weighing import (
    face_design_mouth_open,
    face_jaw_weighing,
    face_jaw_weighing_finish,
    face_update_jaw_curves_weights,
    face_weight_lips,
    skin_teeth,
)
from .core.lip import face_lip
from .core.naming import NamingConvention, Side
from .core.shaders import ensure_face_shaders, ensure_fit_shaders
from .core.ui.face_window import show_fitting_ui

__all__ = [
    # Config
    "FacialRigConfig",
    "FitData",
    "ColorScheme",
    # Naming
    "NamingConvention",
    "Side",
    # Core
    "HierarchyManager",
    "FacialComponent",
    # Fitting
    "FacialFitting",
    "FittingUI",
    "FitType",
    "FitRegion",
    "show_fitting_ui",
    "face_fit_reselect",
    "face_fit_swap_upper_lower",
    "face_fit_hide",
    "face_fit_delete",
    "face_fit_anim",
    "toggle_fit_face",
    "remove_fit_anim_from_ctrl_box",
    "remove_fit_animations_from_on_face_ctrls",
    "get_face_fit_selection",
    "get_face_fit_selection_other_object",
    "ensure_fit_shaders",
    "ensure_face_shaders",
    "as_align",
    "as_lock_attr",
    "as_opm_scale_reset",
    "as_parent_constraint",
    "create_pp",
    "face_add_constrained",
    "face_half_moon_curve",
    "set_rgb_override_color",
    "weight_hammer_verts_ms",
    "as_matrix_connect_attr",
    "as_parent_constraint_blend",
    "as_create_mult_dl",
    "as_face_hide_controllers",
    "ensure_advanced_base",
    "face_eye_ball",
    "face_eye_lid",
    "face_eye_blink",
    "face_eye_brow",
    "face_eye_blink_finish",
    "face_eye_wide",
    "face_eye_wide_finish",
    "face_squint",
    "face_squint_finish",
    "face_eye_aim",
    "face_cheek_finish",
    "face_cheek_raiser",
    "face_cheek_raiser_finish",
    "create_custom_blended_attribute",
    "face_cheek",
    "face_frown_pull",
    "face_frown_pull_finish",
    "face_narrow_smile_and_frown",
    "face_smile_pull",
    "face_smile_pull_controller",
    "face_smile_pull_finish",
    "face_jaw_open",
    "face_jaw_open_finish",
    "face_lip_down",
    "face_lip_down_finish",
    "face_cage_to_skin",
    "face_cage_weights_remove",
    "face_cheek_cage_smooth_update",
    "face_face_cage",
    "face_face_cage_finish",
    "face_lip_falloff",
    "guess_cage_smooth",
    "face_lip_side",
    "face_lip_side_finish",
    "face_snarl",
    "face_snarl_finish",
    "face_tongue",
    "face_tongue_finish",
    "face_regions",
    "face_up_mid_lo",
    "face_phonemes",
    "face_emotions",
    "connect_arkit",
    "apply_options",
    "build_face",
    "delete_face",
    "face_rig_nodes",
    "arise_name",
    "rename_to_arise",
    "face_rebuild_restore",
    "face_pupil_iris",
    "face_lip_up",
    "face_lip_up_finish",
    "face_lip",
    "face_design_mouth_open",
    "face_jaw_weighing",
    "face_jaw_weighing_finish",
    "face_update_jaw_curves_weights",
    "face_weight_lips",
    "skin_teeth",
    "face_finish",
    "face_ds_sdk",
    "FACE_RIG_VERSION",
    "face_prep",
    "include_above_eyes",
    "include_below_eyes",
    "get_max_influences",
    "set_fixed_wrap_options",
    "BUILD_STEPS",
    "step_build_prep",
    "step_build_complete",
    "reset_build_step",
    "face_ctrl_box",
    "create_ctrl_box_slider",
    "add_ctrl_box2_shape",
    "create_face_controller",
    "face_control_orient",
    "place_ctrl_by_projection",
    "ds_sdk",
    "ensure_blend_weighted",
    "ensure_output_blend_weighted",
    "ensure_sdk_curves_named",
    "ctrl_to_bw",
    "mirror_connect_ctrls",
    "face_ds_finish",
    "store_as_ds_sdk",
    "AutoFitSource",
    "AUTO_FIT_SOURCES",
    "detect_auto_fit_source",
    "auto_face_fitting",
    "FitOption",
    "FIT_OPTIONS",
    "set_fit_option",
    "get_fit_option",
    "get_left_suffix",
    # DeltaMush
    "create_delta_mush",
    "delete_delta_mush",
    "delta_mush_zero_weight",
    "connect_delta_mush_scale",
    "paint_delta_mush",
    # HeadSquash
    "create_head_squash",
    "delete_head_squash",
    "optimize_head_squash",
    "add_to_head_squash",
    # Builder
    "FacialRigBuilder",
    "build_facial_rig",
    # Components
    "EyeComponent",
    "EyeLidComponent",
    "EyeBrowComponent",
    "LipComponent",
    "JawComponent",
    "CheekComponent",
    "NoseComponent",
    "TongueComponent",
    "ForeheadComponent",
    "ARKitComponent",
    "create_arkit_blendshapes",
    "connect_arkit_source",
]
