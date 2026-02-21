"""HumanIK demonstration script.

Provides demo/smoke test functionality for the HumanIK rigging system.
Shows examples of creating HumanIK characters with different configurations.
"""

from . import HumanIK


def demo(character_name="Sylvanas"):
    """Run a quick smoke test demonstration of HumanIK rigging.

    Creates three HumanIK character instances with different configurations
    to demonstrate the various rigging modes: FK-only, IK, and Hybrid.

    This function is useful for:
    - Quick testing of the HumanIK module after refactoring
    - Demonstrating the different rigging modes available
    - Verifying that all components work together correctly

    Args:
        character_name: The base name for the test characters.
            Defaults to "Sylvanas". Each configuration will append
            a suffix (_FK, _IK, _Hybrid) to this name.

    Examples:
        >>> # Run demo with default character name
        >>> demo()

        >>> # Run demo with custom character name
        >>> demo("TestCharacter")
    """
    # Create FK-only configuration
    HumanIK(
        f"{character_name}_FK",
        custom_ctrl_definition=True,
        use_ik=False,
        skip_reference_joint=True,
    )

    # Create IK configuration
    HumanIK(
        f"{character_name}_IK",
        custom_ctrl_definition=True,
        use_ik=True,
        skip_reference_joint=True,
    )

    # Create Hybrid configuration (FK/IK blend)
    HumanIK(
        f"{character_name}_Hybrid",
        custom_ctrl_definition=True,
        use_ik=False,
        use_hybrid=True,
        skip_reference_joint=True,
    )


if __name__ == "__main__":
    # Run demo when executed as a script
    demo()
