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
        """Customize the USD export settings in Maya.

        The USD export settings are modified here to set the unit to meters.
        This is done by replacing or adding the "unit=m" parameter to the
        options string.

        Args:
            origin (str): Origin of the command call.
            options (str): Options string for the USD export.
            outputPath (str): Output path of the USD export.

        Returns:
            dict: Dictionary with the modified options string.
        """
        unit_param = ";unit=m"
        if "unit=" in options:
            # Replace the existing unit parameter with the new one
            # This is done using a regular expression to ensure that
            # the existing unit parameter is completely replaced
            import re

            options = re.sub(r"unit=\w+", unit_param, options)
        else:
            # Add the unit parameter to the options string
            options += unit_param + ";"

        print(f" ---------- PyCharm Customized USD export settings: {options}")

        return {"options": options}
