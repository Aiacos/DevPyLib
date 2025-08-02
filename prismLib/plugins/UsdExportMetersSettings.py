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
        """Modify the export settings for the USD exporter.

        The USD exporter's settings are passed as a string to this plugin.
        The string is a semicolon-separated list of options where each option
        is a key-value pair. This plugin will add the 'unit' option to the
        list of options. The value of the 'unit' option is determined by the
        current Maya unit setting. If the current unit is set to 'meter', the
        'unit' option is set to 'cm', otherwise it is set to 'mayaPrefs'.

        Args:
            origin (str): The origin of the export.
            options (str): The export settings.
            outputPath (str): The path to the output file.

        Returns:
            dict: A dictionary with the modified export settings.
        """

        unit_param = "mayaPrefs"

        # Get the current Maya unit setting
        import maya.cmds as cmds

        current_unit = cmds.currentUnit(query=True, linear=True)

        # Set the 'unit' option based on the current Maya unit setting
        if current_unit == "cm":
            unit_param = "cm"
        elif current_unit == "m":
            unit_param = "mayaPrefs"
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
