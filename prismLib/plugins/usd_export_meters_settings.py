# UsdExportMetersSettings.py

name = "UsdExportMetersSettings"
classname = "UsdExportMetersSettings"


class UsdExportMetersSettings:
    """
    Class to customize USD export settings.

    Attributes:
        core (prism_core): PrismCore instance.
        version (str): Plugin version.
    """

    def __init__(self, core):
        """
        Initialize the plugin.

        Args:
            core (prism_core): PrismCore instance.
        """
        self.core = core
        self.version = "v1.0.0"

        self.core.registerCallback(
            "preMayaUSDExport", self.preMayaUSDExport, plugin=self
        )

    def preMayaUSDExport(self, origin, options, outputPath):
        """
        Callback that is called before USD export.

        This callback is used to customize the USD export settings based on the
        current Maya unit setting.

        Args:
            origin (str): The origin of the export.
            options (str): The export settings as a string.
            outputPath (str): The output path of the USD export.

        Returns:
            dict: The modified export settings.
        """
        unit_param = "mayaPrefs"

        # Get the current Maya unit setting
        import maya.cmds as cmds

        current_unit = cmds.currentUnit(query=True, linear=True)

        # Set the 'unit' option based on the current Maya unit setting
        if current_unit == "cm":
            unit_param = "none"

            # cmds.currentUnit(linear="m")
            # cmds.optionVar(category="Settings", stringValue=("workingUnitLinear", "m"))

        elif current_unit == "m":
            unit_param = "none"
        else:
            unit_param = "mayaPrefs"

        # Split the export settings into a list of options
        parts = options.split(";")

        # Remove any existing 'unit' options
        filtered = [p for p in parts if p and not p.strip().startswith("unit=")]
        # Add the new 'unit' option
        filtered.append(f"unit={unit_param}")
        # Join the options back into a string
        options = ";".join(filtered)
        # Add a trailing semicolon if it's not already there
        if not options.endswith(";"):
            options = options + ";"

        # Return the modified export settings
        return {"options": options}
