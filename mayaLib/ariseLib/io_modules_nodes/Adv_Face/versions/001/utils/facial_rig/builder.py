"""
Facial Rig Builder - Main orchestrator for building facial rigs.

Orchestratore a step con parita' asBuildAdvancedFace (MEL 27892): la
sequenza BUILD_ORDER e' quella canonica dei 30 step MEL, lo stato di
avanzamento vive in FaceFitSkeleton.buildStep (core/build_steps.py) e
il "Step Builder" manuale passa dal guard di sequenza
(build_component). Gli step gia' a parita' (Prep, CtrlBox) chiamano i
moduli core; gli step con una shell legacy usano i componenti
esistenti in attesa della parita'; gli altri vengono saltati con un
print ma fanno comunque avanzare buildStep.
"""

from typing import Callable, List, Optional

import maya.cmds as cmds

from .core.build_steps import (
    BUILD_STEPS,
    ensure_build_step_attr,
    step_build_complete,
    step_build_prep,
)
from .core.config import FacialRigConfig
from .core.ctrl_box import face_ctrl_box
from .core.eye_ball import face_eye_ball
from .core.eye_lid import face_eye_lid
from .core.face_cage import face_face_cage
from .core.face_cage_to_skin import face_cage_to_skin
from .core.face_cheek_raiser import face_cheek_raiser
from .core.face_emotions import face_emotions
from .core.face_eye_aim import face_eye_aim
from .core.face_eye_blink import face_eye_blink
from .core.face_eye_brow import face_eye_brow
from .core.face_eye_wide import face_eye_wide
from .core.face_finish import face_finish
from .core.face_frown_pull import face_cheek, face_frown_pull
from .core.face_jaw_open import face_jaw_open
from .core.face_lip_down import face_lip_down
from .core.face_lip_falloff import face_lip_falloff
from .core.face_lip_side import face_lip_side
from .core.face_lip_up import face_lip_up
from .core.face_phonemes import face_phonemes
from .core.face_prep import face_prep
from .core.face_rebuild_restore import face_rebuild_restore
from .core.face_regions import face_regions
from .core.face_smile_pull import face_smile_pull
from .core.face_snarl import face_snarl
from .core.face_squint import face_squint
from .core.face_tongue import face_tongue
from .core.face_up_mid_lo import face_up_mid_lo
from .core.fit_options import set_fit_option
from .core.hierarchy import HierarchyManager
from .core.jaw_weighing import face_jaw_weighing
from .core.lip import face_lip

# Step con backend Python a parita' (eseguono davvero in _build_step).
# Gli altri step di BUILD_ORDER avanzano lo stato stampando "skip".
# Mantenere allineato a _build_step quando un componente raggiunge la parita'.
IMPLEMENTED_STEPS = frozenset(
    {
        "Prep",
        "CtrlBox",
        "EyeBall",
        "EyeLid",
        "EyeBlink",
        "EyeWide",
        "Lip",
        "LipFalloff",
        "FaceCage",
        "CageToSkin",
        "EyeBrow",
        "Squint",
        "SmilePull",
        "FrownPull",
        "Cheek",
        "CheekRaiser",
        "JawWeighing",
        "JawOpen",
        "LipUp",
        "LipDown",
        "LipSide",
        "Snarl",
        "Tongue",
        "Regions",
        "EyeAim",
        "UpMidLo",
        "Phonemes",
        "Emotions",
        "Finish",
        "RebuildRestore",
    }
)


class FacialRigBuilder:
    """
    Main facial rig builder class.

    Orchestrates the building of all facial rig components
    in the correct order with proper dependencies.

    Usage:
        config = FacialRigConfig(
            geometry="head_geo",
            all_head_geo=["head_geo"],
            head_joint="Head",
            skin_cluster="skinCluster1",
            right_eye="eye_R_geo",
            left_eye="eye_L_geo"
        )
        builder = FacialRigBuilder(config)
        builder.build()
    """

    # Sequenza canonica MEL (UI 1760-1794): l'indice 1-based di ogni
    # step e' il valore scritto in FaceFitSkeleton.buildStep
    BUILD_ORDER = list(BUILD_STEPS)

    def __init__(self, config: FacialRigConfig):
        """
        Initialize the facial rig builder.

        Args:
            config: Facial rig configuration
        """
        self.config = config
        self.hierarchy = HierarchyManager()

        # Component instances
        self._components = {}
        self._built_components = []

        # Callbacks
        self._on_step_start: Optional[Callable] = None
        self._on_step_complete: Optional[Callable] = None
        self._on_error: Optional[Callable] = None

    def build(
        self, components: Optional[List[str]] = None, manually_run_restore_step: bool = False
    ) -> bool:
        """
        Build the facial rig (parita' asBuildAdvancedFace).

        Args:
            components: Optional list of specific steps to build.
                       If None, builds the full BUILD_ORDER sequence.
            manually_run_restore_step: stop before RebuildRestore so it
                can be run manually (MEL checkbox).

        Returns:
            True if build succeeded
        """
        # Validate config
        if not self.config.is_valid():
            errors = self.config.validate()
            for error in errors:
                cmds.warning(f"Config error: {error}")
            return False

        # Pre-flight checks
        if not self._pre_build_checks():
            return False

        ensure_build_step_attr()

        # Determine steps to build
        build_list = components or self.BUILD_ORDER
        for step in build_list:
            if step not in self.BUILD_ORDER:
                cmds.warning(f"Unknown build step: {step}")
                return False

        # Build each step
        for step in build_list:
            if step == "RebuildRestore" and manually_run_restore_step:
                print("// Manually run the RebuildRestore Step, to apply the Restore.")
                break

            if self._on_step_start:
                self._on_step_start(step)

            try:
                print(f"// Execute Step:{step}")
                success = self._build_step(step)
                if not success:
                    cmds.warning(f"Step '{step}' failed")
                    if self._on_error:
                        self._on_error(step)
                    return False

                step_build_complete(self.BUILD_ORDER.index(step) + 1)
                self._built_components.append(step)

                if self._on_step_complete:
                    self._on_step_complete(step)

            except Exception as e:
                cmds.warning(f"Error in step '{step}': {e}")
                if self._on_error:
                    self._on_error(step, str(e))
                return False

        self._post_build()
        if not manually_run_restore_step:
            print("// Face Build Complete")
        return True

    def build_component(self, step: str) -> bool:
        """
        Build a single step manually (lo "Step Builder" MEL): passa dal
        guard di sequenza su FaceFitSkeleton.buildStep.

        Args:
            step: Step name (es. "EyeBall")

        Returns:
            True if the step succeeded
        """
        if step not in self.BUILD_ORDER:
            cmds.warning(f"Unknown build step: {step}")
            return False
        index = self.BUILD_ORDER.index(step) + 1
        if not step_build_prep(index):
            return False
        if not self._build_step(step):
            return False
        step_build_complete(index)
        return True

    def _pre_build_checks(self) -> bool:
        """
        Run pre-build validation checks.

        Returns:
            True if all checks pass
        """
        # Check geometry exists
        if not cmds.objExists(self.config.geometry):
            cmds.warning(f"Face geometry not found: {self.config.geometry}")
            return False

        # Check head joint exists
        if not cmds.objExists(self.config.head_joint):
            cmds.warning(f"Head joint not found: {self.config.head_joint}")
            return False

        # Check skin cluster exists
        if not cmds.objExists(self.config.skin_cluster):
            cmds.warning(f"Skin cluster not found: {self.config.skin_cluster}")
            return False

        # AdvancedSkeleton richiede i cm (in headless niente dialog:
        # switch con warning)
        current_unit = cmds.currentUnit(query=True, linear=True)
        if current_unit != "cm":
            cmds.warning(
                f"Units are '{current_unit}': AdvancedSkeleton "
                "requires 'cm', switching working units"
            )
            cmds.currentUnit(linear="cm")

        # Check for FaceFitSkeleton and load fit data
        if cmds.objExists("FaceFitSkeleton"):
            if not self.config.fit_data:
                print("// Loading fit data from FaceFitSkeleton...")
                if self.config.load_fit_data():
                    print(f"// Fit data loaded, face scale: {self.config.face_scale}")
                else:
                    cmds.warning("FaceFitSkeleton exists but could not load fit data")
        else:
            cmds.warning("No FaceFitSkeleton found. Run fitting first using show_fitting_ui()")
            return False

        return True

    def _build_step(self, step: str) -> bool:
        """
        Build a single step.

        Args:
            step: Step name (nome canonico MEL)

        Returns:
            True if step succeeded
        """
        if step == "Prep":
            return self._prep()
        elif step == "CtrlBox":
            return face_ctrl_box()
        elif step == "EyeBall":
            return face_eye_ball()
        elif step == "EyeLid":
            return face_eye_lid()
        elif step == "EyeBlink":
            # il finish del blink e' eseguito da EyeWide (asFaceEyeWide chiama
            # asFaceEyeBlinkFinish, MEL:31104) — fedele al MEL
            return face_eye_blink()
        elif step == "EyeWide":
            # il finish lo chiama Lip (asFaceLip, MEL:31170), come nel MEL
            return face_eye_wide()
        elif step == "Lip":
            return face_lip()
        elif step == "LipFalloff":
            return face_lip_falloff()
        elif step == "FaceCage":
            return face_face_cage()
        elif step == "CageToSkin":
            return face_cage_to_skin()
        elif step == "EyeBrow":
            return face_eye_brow()
        elif step == "Squint":
            # il finish lo chiama SmilePull (asFaceSmilePull, MEL:34134)
            return face_squint()
        elif step == "SmilePull":
            # i finish sono chiamati dallo step successivo, come nel MEL:
            # SmilePull da FrownPull, FrownPull da Cheek
            return face_smile_pull()
        elif step == "FrownPull":
            return face_frown_pull()
        elif step == "Cheek":
            return face_cheek()
        elif step == "CheekRaiser":
            # il finish lo chiama JawWeighing (asFaceJawWeighing, MEL:34729)
            return face_cheek_raiser()
        elif step == "JawWeighing":
            # il finish lo chiama JawOpen (asFaceJawOpen, MEL:35232)
            return face_jaw_weighing()
        elif step == "JawOpen":
            # il finish e' eseguito da LipUp (asFaceLipUp chiama
            # asFaceJawOpenFinish, MEL:35279) — fedele al MEL
            return face_jaw_open()
        elif step == "LipUp":
            # il finish e' eseguito da LipDown (asFaceLipDown chiama
            # asFaceLipUpFinish, MEL:35366) — fedele al MEL
            return face_lip_up()
        elif step == "LipDown":
            # il finish e' eseguito da LipSide (asFaceLipSide chiama
            # asFaceLipDownFinish, MEL:35443) — fedele al MEL
            return face_lip_down()
        elif step == "LipSide":
            # il finish lo chiama Snarl (asFaceSnarl, MEL:35601)
            return face_lip_side()
        elif step == "Snarl":
            # il finish lo chiama Tongue (asFaceTongue, MEL:35728)
            return face_snarl()
        elif step == "Tongue":
            # il finish lo chiama Regions (asFaceRegions, MEL:35956)
            return face_tongue()
        elif step == "Regions":
            return face_regions()
        elif step == "EyeAim":
            # step di sola visibilita' (asFaceEyeAim, no finish)
            return face_eye_aim()
        elif step == "UpMidLo":
            return face_up_mid_lo()
        elif step == "Phonemes":
            return face_phonemes()
        elif step == "Emotions":
            return face_emotions()
        elif step == "Finish":
            # il controller ARKit / SnapChat e' collegato da face_finish
            return self._finish()
        elif step == "RebuildRestore":
            return face_rebuild_restore()
        else:
            print(f"// Step:{step} not yet at parity, skipping")
            return True

    def _prep(self) -> bool:
        """Run prep step (parita' asFacePrep via core/face_prep)."""
        # persiste l'input della config sulle opzioni di FaceFitSkeleton
        # (equivalente di asSavePrepInput: face_prep legge dalla scena)
        set_fit_option("Face", self.config.geometry)
        set_fit_option("AllHead", " ".join(self.config.all_head_geo))
        set_fit_option("HeadJoint", self.config.head_joint)
        set_fit_option("SkinCluster", self.config.skin_cluster)
        set_fit_option("RightEye", self.config.right_eye)
        set_fit_option("LeftEye", self.config.left_eye)
        if self.config.upper_teeth:
            set_fit_option("UpperTeeth", self.config.upper_teeth)
        if self.config.lower_teeth:
            set_fit_option("LowerTeeth", self.config.lower_teeth)
        if self.config.tongue:
            set_fit_option("Tongue", self.config.tongue)
        return face_prep()

    def _finish(self) -> bool:
        """Run finish step (parita' asFaceFinish via core/face_finish)."""
        return face_finish()

    def _post_build(self):
        """Run post-build cleanup."""
        cmds.select(clear=True)

    def set_callbacks(
        self,
        on_step_start: Optional[Callable] = None,
        on_step_complete: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """
        Set callback functions for build progress.

        Args:
            on_step_start: Called when step starts (receives step name)
            on_step_complete: Called when step completes (receives step name)
            on_error: Called on error (receives step name, optional error message)
        """
        self._on_step_start = on_step_start
        self._on_step_complete = on_step_complete
        self._on_error = on_error

    def get_component(self, name: str):
        """
        Get a built component by name.

        Args:
            name: Component name

        Returns:
            Component instance or None
        """
        return self._components.get(name)

    @property
    def built_components(self) -> List[str]:
        """Get list of built component names."""
        return self._built_components.copy()


def build_facial_rig(
    geometry: str, head_joint: str, right_eye: str, left_eye: str, **kwargs
) -> bool:
    """
    Convenience function to build a facial rig.

    Args:
        geometry: Face mesh name
        head_joint: Head joint name
        right_eye: Right eye geometry
        left_eye: Left eye geometry
        **kwargs: Additional config options

    Returns:
        True if build succeeded
    """
    from .utils.skinning import SkinningUtils

    # Get skin cluster
    skin_cluster = SkinningUtils.get_skin_cluster(geometry)
    if not skin_cluster:
        cmds.warning(f"No skin cluster found on {geometry}")
        return False

    # Create config
    config = FacialRigConfig(
        geometry=geometry,
        all_head_geo=kwargs.get("all_head_geo", [geometry]),
        head_joint=head_joint,
        skin_cluster=skin_cluster,
        right_eye=right_eye,
        left_eye=left_eye,
        **{k: v for k, v in kwargs.items() if k != "all_head_geo"},
    )

    # Build
    builder = FacialRigBuilder(config)
    return builder.build()
