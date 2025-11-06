"""BVH motion capture file importer for Maya.

Importer for .bvh files (BioVision Hierarchy files).
BVH is a common ASCII motion capture data format containing skeletal
and motion data. Provides utilities for importing BVH motion capture
data onto Maya skeletons with UI dialog and retargeting support.

License:
    GNU General Public License v3.0 or later.
    Copyright (C) 2012 Jeroen Hoolmans.
"""

__author__ = "Jeroen Hoolmans"

__copyright__ = "Copyright 2012, Jeroen Hoolmans"
__credits__ = ["Jeroen Hoolmans"]
__license__ = "GPL"
__version__ = "1.0.1"
__maintainer__ = "Jeroen Hoolmans"
__email__ = "jhoolmans@gmail.com"
__status__ = "Production"

import os

import maya.cmds as mc
import pymel.core as pm

# This maps the BVH naming convention to Maya
TRANSLATION_DICT = {
    "Xposition": "translateX",
    "Yposition": "translateY",
    "Zposition": "translateZ",
    "Xrotation": "rotateX",
    "Yrotation": "rotateY",
    "Zrotation": "rotateZ"
}


class TinyDAG(object):
    """# Small helper class to keep track of parents
    """

    def __init__(self, obj, p_obj=None):
        """Initialize BVH node wrapper.

        Args:
            obj: Node name or object
            p_obj: Parent BVHNode object. Defaults to None.
        """
        self.obj = obj
        self.p_obj = p_obj

    def __str__(self):
        # returns object name
        return str(self.obj)

    def _full_path(self):
        # returns full object path
        if self.p_obj is not None:
            return "%s|%s" % (self.p_obj._full_path(), self.__str__())
        return str(self.obj)


class BVHImporterDialog(object):
    """# Dialog class..
    """

    def __init__(self, debug=False):
        """Initialize BVH Importer dialog window.

        Creates a Maya UI dialog for importing BVH motion capture files,
        with options for scale, frame range, and rotation order.

        Args:
            debug: Enable debug output during import. Defaults to False.
                  WARNING: Don't use debug when importing more than 10 frames.

        Attributes:
            _filename: Path to BVH file
            _channels: Parsed motion channels from BVH
            _rootNode: Target root joint for retargeting
        """
        # Don't use debug when importing more than 10 frames.. Otherwise it gets messy
        self._name = "bvhImportDialog"
        self._title = "BVH Importer %s" % __version__

        # UI related
        self._textfield = ""
        self._scale_field = ""
        self._frame_field = ""
        self._rotation_order = ""
        self._reload = ""

        # Other
        self._root_node = None  # Used for targeting
        self._debug = debug

        # BVH specific stuff
        self._filename = ""
        self._channels = []

        self.setup_ui()

    def setup_ui(self):
        """Create and display the BVH Importer UI window.

        Builds the Maya UI with text fields for file path, scale factor,
        frame range, rotation order dropdown, and import/reload buttons.
        """
        # Creates the great dialog
        win = self._name
        if mc.window(win, ex=True):
            mc.deleteUI(win)

        # Non sizeable dialog
        win = mc.window(self._name, title=self._title, w=200, rtf=True, sizeable=False)

        mc.columnLayout(adj=1, rs=5)
        mc.separator()
        mc.text("Options")
        mc.separator()

        mc.rowColumnLayout(numberOfColumns=2,
                           columnWidth=[(1, 80), (2, 150)],
                           cal=[(1, "right"), (2, "center")],
                           cs=[(1, 5), (2, 5)],
                           rs=[(1, 5), (2, 5)])

        mc.text("Rig scale")
        self._scale_field = mc.floatField(minValue=0.01, maxValue=2, value=1)
        mc.text("Frame offset")
        self._frame_field = mc.intField(minValue=0)
        mc.text("Rotation Order")
        self._rotation_order = mc.optionMenu()
        mc.menuItem(label='XYZ')
        mc.menuItem(label='YZX')
        mc.menuItem(label='ZXY')
        mc.menuItem(label='XZY')
        mc.menuItem(label='YXZ')
        mc.menuItem(label='ZYX')

        mc.setParent("..")
        mc.separator()

        # Targeting UI
        mc.text("Skeleton Targeting")
        mc.text("(Select the hips)")
        mc.separator()

        mc.rowColumnLayout(numberOfColumns=2,
                           columnWidth=[(1, 150), (2, 80)],
                           cs=[(1, 5), (2, 5)],
                           rs=[(1, 5), (2, 5)])

        self._textfield = mc.textField(editable=False)
        mc.button("Select/Clear", c=self._on_select_root)

        mc.setParent("..")
        mc.separator()
        mc.button("Import..", c=self._on_select_file)
        self._reload = mc.button("Reload", enable=False, c=self._read_bvh)

        # Sorry :)
        mc.text("Created by Jeroen Hoolmans")

        mc.window(win, e=True, rtf=True, sizeable=False)
        mc.showWindow(win)

    def _on_select_file(self, e):
        # Without All Files it didn't work for some reason..
        file_filter = "All Files (*.*);;Motion Capture (*.bvh)"
        dialog = mc.fileDialog2(fileFilter=file_filter, dialogStyle=1, fm=1)

        if dialog is None:
            return
        if not len(dialog):
            return

        self._filename = dialog[0]

        mc.button(self._reload, e=True, enable=True)

        # Action!
        self._read_bvh()

    def _read_bvh(self, e=False):
        # Safe close is needed for End Site part to keep from setting new parent.
        safe_close = False
        # Once motion is active, animate.
        motion = False
        # Clear channels before appending
        self._channels = []

        # Scale the entire rig and animation
        rig_scale = mc.floatField(self._scale_field, q=True, value=True)
        frame = mc.intField(self._frame_field, q=True, value=True)
        rot_order = mc.optionMenu(self._rotation_order, q=True, select=True) - 1

        with open(self._filename, encoding='utf-8') as f:
            # Check to see if the file is valid (sort of)
            if not f.next().startswith("HIERARCHY"):
                mc.error("No valid .bvh file selected.")
                return False

            if self._root_node is None:
                # Create a group for the rig, easier to scale. (Freeze transform when ungrouping please..)
                mocap_name = os.path.basename(self._filename)
                grp = pm.group(em=True, name="_mocap_%s_grp" % mocap_name)
                grp.scale.set(rig_scale, rig_scale, rig_scale)

                # The group is now the 'root'
                my_parent = TinyDAG(str(grp), None)
            else:
                my_parent = TinyDAG(str(self._root_node), None)
                self._clear_animation()

            for line in f:
                line = line.replace("	", " ")  # force spaces
                if not motion:
                    # root joint
                    if line.startswith("ROOT"):
                        # Set the Hip joint as root
                        if self._root_node:
                            my_parent = TinyDAG(str(self._root_node), None)
                        else:
                            my_parent = TinyDAG(line[5:].rstrip(), my_parent)

                    if "JOINT" in line:
                        jnt = line.split(" ")
                        # Create the joint
                        my_parent = TinyDAG(jnt[-1].rstrip(), my_parent)

                    if "End Site" in line:
                        # Finish up a hierarchy and ignore a closing bracket
                        safe_close = True

                    if "}" in line:
                        # Ignore when safe_close is on
                        if safe_close:
                            safe_close = False
                            continue

                        # Go up one level
                        if my_parent is not None:
                            my_parent = my_parent.p_obj
                            if my_parent is not None:
                                mc.select(my_parent._full_path())

                    if "CHANNELS" in line:
                        chan = line.strip().split(" ")
                        if self._debug:
                            print(chan)

                        # Append the channels that are animated
                        for i in range(int(chan[1])):
                            self._channels.append("%s.%s" % (my_parent._full_path(), TRANSLATION_DICT[chan[2 + i]]))

                    if "OFFSET" in line:
                        offset = line.strip().split(" ")
                        if self._debug:
                            print(offset)
                        jnt_name = str(my_parent)

                        # When End Site is reached, name it "_tip"
                        if safe_close:
                            jnt_name += "_tip"

                        # skip if exists
                        if mc.objExists(my_parent._full_path()):
                            jnt = pm.PyNode(my_parent._full_path())
                            jnt.rotateOrder.set(rot_order)
                            jnt.translate.set([float(offset[1]), float(offset[2]), float(offset[3])])
                            continue

                        # Build the joint and set its properties
                        jnt = pm.joint(name=jnt_name, p=(0, 0, 0))
                        jnt.translate.set([float(offset[1]), float(offset[2]), float(offset[3])])
                        jnt.rotateOrder.set(rot_order)

                    if "MOTION" in line:
                        # Animate!
                        motion = True

                    if self._debug:
                        if my_parent is not None:
                            print(("parent: %s" % my_parent._full_path()))

                else:
                    # We don't really need to use Framecount and time(since Python handles file reads nicely)
                    if "Frame" not in line:
                        data = line.split(" ")
                        if len(data) > 0:
                            if data[0] == "":
                                data.pop(0)

                        if self._debug:
                            print("Animating..")
                            print("Data size: %d" % len(data))
                            print("Channels size: %d" % len(self._channels))
                        # Set the values to channels
                        for x in range(0, len(data) - 1):
                            if self._debug:
                                print("Set Attribute: %s %f" % (self._channels[x], float(data[x])))
                            mc.setKeyframe(self._channels[x], time=frame, value=float(data[x]))

                        frame = frame + 1

    def _clear_animation(self):
        # select root joint
        pm.select(str(self._root_node), hi=True)
        nodes = pm.ls(sl=True)

        trans_attrs = ["translateX", "translateY", "translateZ"]
        rot_attrs = ["rotateX", "rotateY", "rotateZ"]
        for node in nodes:
            for attr in trans_attrs:
                connections = node.attr(attr).inputs()
                pm.delete(connections)
            for attr in rot_attrs:
                connections = node.attr(attr).inputs()
                pm.delete(connections)
                node.attr(attr).set(0)

    def _on_select_root(self, e):
        # When targeting, set the root joint (Hips)
        selection = pm.ls(sl=True, type="joint")
        if len(selection) == 0:
            self._root_node = None
            mc.textField(self._textfield, e=True, text="")
        else:
            self._root_node = selection[0]
            mc.textField(self._textfield, e=True, text=str(self._root_node))


if __name__ == "__main__":
    dialog = BVHImporterDialog()
