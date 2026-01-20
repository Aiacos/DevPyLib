"""Maya skin weights save/load utility.

High-performance tool for exporting and importing skinCluster weights, supporting
both full object weights and per-vertex soft selection weights.

Author: Thomas Bittner (thomasbittner@hotmail.de)
Copyright: 2013-2016
"""

import time

from maya import OpenMaya, OpenMayaAnim, cmds, mel

# pylint: disable=too-many-lines,too-many-locals,too-many-branches
# pylint: disable=too-many-statements,too-many-nested-blocks
# pylint: disable=missing-function-docstring,invalid-name,line-too-long
# pylint: disable=consider-using-enumerate,redefined-builtin,consider-using-f-string

# def showUI():
#     global mainWin
#     mainWin = bSkinSaverUI()
#     mainWin.show()
#
#
# def getMayaWindow():
#     ptr = omui.MQtUtil.mainWindow()
#     return wrapInstance(int(ptr), QtWidgets.QWidget)
#
#
# class bSkinSaverUI(QtWidgets.QDialog):
#     def __init__(self, parent=getMayaWindow()):
#         super(bSkinSaverUI, self).__init__(parent, QtCore.Qt.WindowStaysOnTopHint)
#
#         tab_widget = QtWidgets.QTabWidget()
#         objectsTab = QtWidgets.QWidget()
#         verticesTab = QtWidgets.QWidget()
#
#         tab_widget.addTab(objectsTab, "Objects")
#         tab_widget.addTab(verticesTab, "Vertices")
#         self.desc_label = QtWidgets.QLabel("(C) 2015 by Thomas Bittner", parent=self)
#         self.setWindowTitle('bSkinSaver 1.1')
#
#         self.objects_file_line = QtWidgets.QLineEdit('/Users/thomas/default.weights', parent=self)
#         self.select_objects_file_button = QtWidgets.QPushButton("Set File", parent=self)
#         self.save_objects_button = QtWidgets.QPushButton("Save Weights from selected Objects", parent=self)
#         self.load_objects_button = QtWidgets.QPushButton("Load", parent=self)
#         self.load_objects_selection_button = QtWidgets.QPushButton("Load to Selected Object", parent=self)
#
#         objectsLayout = QtWidgets.QVBoxLayout(objectsTab)
#         objectsLayout.setAlignment(QtCore.Qt.AlignTop)
#         objectsLayout.setSpacing(3)
#         objectsFileLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
#         objectsFileLayout.addWidget(self.objects_file_line)
#         objectsFileLayout.addWidget(self.select_objects_file_button)
#         objectsLayout.addLayout(objectsFileLayout)
#
#         objectsButtonLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
#         objectsButtonLayout.setSpacing(0)
#         objectsButtonLayout.addWidget(self.save_objects_button)
#         objectsButtonLayout.addWidget(self.load_objects_button)
#         objectsButtonLayout.addWidget(self.load_objects_selection_button)
#
#         objectsLayout.addLayout(objectsButtonLayout)
#
#         self.vertices_file_line = QtWidgets.QLineEdit('/Users/thomas/defaultVertex.weights', parent=self)
#         self.select_vertices_file_button = QtWidgets.QPushButton("Set File", parent=self)
#         self.save_vertices_button = QtWidgets.QPushButton("Save Weights from selected Vertices", parent=self)
#         self.load_vertices_button = QtWidgets.QPushButton("Load onto selected Object", parent=self)
#         self.ignore_soft_selection_when_saving = QtWidgets.QCheckBox("ignore Soft Selection when Saving", parent=self)
#         self.ignore_joint_locks_when_loading = QtWidgets.QCheckBox("ignore Joint Locks when Loading", parent=self)
#
#         verticesLayout = QtWidgets.QVBoxLayout(verticesTab)
#         verticesLayout.setAlignment(QtCore.Qt.AlignTop)
#         verticesLayout.setSpacing(3)
#         verticesFileLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.LeftToRight)
#         verticesFileLayout.addWidget(self.vertices_file_line)
#         verticesFileLayout.addWidget(self.select_vertices_file_button)
#         verticesLayout.addLayout(verticesFileLayout)
#
#         verticesButtonLayout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom)
#         verticesButtonLayout.setSpacing(0)
#         verticesButtonLayout.addWidget(self.save_vertices_button)
#         verticesButtonLayout.addWidget(self.load_vertices_button)
#         verticesButtonLayout.addWidget(self.ignore_soft_selection_when_saving)
#         verticesButtonLayout.addWidget(self.ignore_joint_locks_when_loading)
#         verticesLayout.addLayout(verticesButtonLayout)
#
#         self.layout = QtWidgets.QBoxLayout(QtWidgets.QBoxLayout.TopToBottom, self)
#         self.layout.addWidget(tab_widget)
#         self.layout.addWidget(self.desc_label)
#         self.resize(400, 10)
#
#         # select files
#         self.connect(self.select_objects_file_button, QtCore.SIGNAL("clicked()"), self.selectObjectsFile)
#         self.connect(self.select_vertices_file_button, QtCore.SIGNAL("clicked()"), self.selectVerticesFile)
#
#         self.connect(self.save_objects_button, QtCore.SIGNAL("clicked()"), self.saveObjects)
#         self.connect(self.load_objects_button, QtCore.SIGNAL("clicked()"), self.loadObjects)
#         self.connect(self.load_objects_selection_button, QtCore.SIGNAL("clicked()"), self.loadObjectsSelection)
#
#         self.connect(self.save_vertices_button, QtCore.SIGNAL("clicked()"), self.saveVertices)
#         self.connect(self.load_vertices_button, QtCore.SIGNAL("clicked()"), self.loadVertices)
#
#     def selectObjectsFile(self):
#         fileResult = cmds.fileDialog2()
#         if fileResult != None:
#             self.objects_file_line.setText(fileResult[0])
#
#     def selectVerticesFile(self):
#         fileResult = cmds.fileDialog2()
#         if fileResult != None:
#             self.vertices_file_line.setText(fileResult[0])
#
#     def loadObjects(self):
#         b_load_skin_values(False, str(self.objects_file_line.text()))
#
#     def loadObjectsSelection(self):
#         b_load_skin_values(True, str(self.objects_file_line.text()))
#
#     def saveObjects(self):
#         b_save_skin_values(str(self.objects_file_line.text()))
#
#     def loadVertices(self):
#         b_load_vertex_skin_values(str(self.vertices_file_line.text()), self.ignore_joint_locks_when_loading.isChecked())
#
#     def saveVertices(self):
#         b_save_vertex_skin_values(str(self.vertices_file_line.text()), self.ignore_soft_selection_when_saving.isChecked())


def b_find_skin_cluster(object_name, b_skin_path=None):
    """Find skin cluster connected to a deformed object.

    Args:
        object_name (str): Name of the object to find skin cluster for.
        b_skin_path (MDagPath | None): Optional path parameter (unused).

    Returns:
        MObject or bool: Skin cluster node if found, False otherwise.
    """
    if b_skin_path is None:
        b_skin_path = OpenMaya.MDagPath()
    it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kSkinClusterFilter)
    while not it.isDone():
        fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(it.item())
        fn_skin_cluster.getPathAtIndex(0, b_skin_path)

        if (
            OpenMaya.MFnDagNode(b_skin_path.node()).partialPathName() == object_name
            or OpenMaya.MFnDagNode(
                OpenMaya.MFnDagNode(b_skin_path.node()).parent(0)
            ).partialPathName()
            == object_name
        ):
            return it.item()
        next(it)
    return False


def b_load_vertex_skin_values(input_file, ignore_joint_locks):
    """Load vertex-level skin weights from a file to selected object.

    Reads skin weight data from a formatted file and applies it to vertices
    of the selected mesh, handling joint locks and soft selection.

    Args:
        input_file (str): Path to the weight file.
        ignore_joint_locks (bool): If True, ignore joint lock attributes.
    """
    time_before = time.time()

    line = ""
    file_joints = []
    splitted_strings = []
    splitted_weights = []
    selection_list = OpenMaya.MSelectionList()
    vertex_count = 0

    OpenMaya.MGlobal.getActiveSelectionList(selection_list)
    node = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    selection_list.getDagPath(0, node, component)

    if not node.hasFn(OpenMaya.MFn.kTransform):
        print("select a skinned object")

    new_transform = OpenMaya.MFnTransform(node)
    if not new_transform.childCount() or not new_transform.child(0).hasFn(OpenMaya.MFn.kMesh):
        print("select a skinned object..")

    mesh = new_transform.child(0)
    object_name = OpenMaya.MFnDagNode(mesh).name()
    skin_cluster = b_find_skin_cluster(object_name)
    if not skin_cluster.hasFn(OpenMaya.MFn.kSkinClusterFilter):
        print("select a skinned object")

    fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_cluster)

    file_position = 0

    # getting the weightLines
    #
    file_weight_floats = []
    fn_vtx_comp = OpenMaya.MFnSingleIndexedComponent()
    vtx_components = OpenMaya.MObject()
    vtx_components = fn_vtx_comp.create(OpenMaya.MFn.kMeshVertComponent)

    bind_vert_count = 0
    did_check_soft_selection = False
    do_soft_selection = False
    soft_weights = []
    weights_index = 1

    with open(input_file, encoding="utf-8") as input_stream:
        while True:
            raw_line = input_stream.readline()
            if not raw_line:
                break
            line = raw_line.strip()
            if not line:
                break

            if file_position == 0:
                vertex_count = int(line)
                if OpenMaya.MItGeometry(node).count() != vertex_count:
                    print("vertex counts don't match!")
                    return
                file_position = 1

            elif file_position == 1:
                if not line.startswith("========"):
                    file_joints.append(line)
                else:
                    file_position = 2

            elif file_position == 2:
                splitted_strings = line.split(":")

                # do we have softselection?
                if not did_check_soft_selection:
                    if len(splitted_strings) == 3:
                        weights_index = 2
                        do_soft_selection = True
                        soft_weights = [1.0] * bind_vert_count
                    else:
                        weights_index = 1
                        do_soft_selection = False
                    did_check_soft_selection = True

                # vertId
                vert_id = int(splitted_strings[0])
                fn_vtx_comp.addElement(vert_id)

                # softselection
                if do_soft_selection:
                    soft_weights.append(float(splitted_strings[1]))

                # weights
                splitted_weights = splitted_strings[weights_index].split(" ")
                file_weight_floats.append(list(map(float, splitted_weights)))

                bind_vert_count += 1

    b_skin_path = OpenMaya.MDagPath()
    fn_skin_cluster.getPathAtIndex(0, b_skin_path)

    # print('file_weight_floats: ', file_weight_floats)

    # getting mayaJoints
    #
    influence_array = OpenMaya.MDagPathArray()
    maya_joints = []

    inf_count = fn_skin_cluster.influenceObjects(influence_array)
    for i in range(inf_count):
        maya_joints.append(OpenMaya.MFnDagNode(influence_array[i]).name().split("|")[-1])

        # getting old weights
    #
    old_weight_doubles = OpenMaya.MDoubleArray()
    script_util = OpenMaya.MScriptUtil()
    inf_count_ptr = script_util.asUintPtr()
    fn_skin_cluster.getWeights(b_skin_path, vtx_components, old_weight_doubles, inf_count_ptr)

    # making allJoints
    #
    all_joints = list(file_joints)
    for maya_joint in maya_joints:
        if maya_joint not in file_joints:
            all_joints.append(maya_joint)

    # mapping joints and making sure we have all joints in the skinCluster
    #
    all_influences_in_scene = True
    missing_influences_list = []
    for i in range(len(file_joints)):
        influence_in_scene = False
        for k in range(len(maya_joints)):
            if maya_joints[k] == file_joints[i]:
                influence_in_scene = True

        if not influence_in_scene:
            all_influences_in_scene = False
            missing_influences_list.append(file_joints[i])

    if not all_influences_in_scene:
        print(("There are influences missing:", missing_influences_list))
        return

    # getting allExistInMaya
    #
    all_exist_in_maya = [-1] * len(all_joints)
    for i in range(len(all_joints)):
        for k in range(len(maya_joints)):
            if all_joints[i] == maya_joints[k]:
                all_exist_in_maya[i] = k
                break

    # print('all_exist_in_maya: ', all_exist_in_maya)

    # getting joint locks
    #
    all_locks = [False] * len(all_joints)
    if not ignore_joint_locks:
        for i in range(len(all_joints)):
            all_locks[i] = cmds.getAttr(f"{all_joints[i]}.liw")

    weight_doubles = OpenMaya.MDoubleArray(0)

    # copy weights from file_weight_floats and old_weight_doubles into weight_doubles (include joint locks) and soft_weights lists
    #
    print(("bind_vert_count: ", bind_vert_count))
    for i in range(bind_vert_count):
        for k in range(len(all_joints)):
            # file_joints:
            #
            if k < len(file_joints):
                if not all_locks[k]:
                    weight_doubles.append(
                        file_weight_floats[i][k]
                    )  # weight_doubles[k + len(all_joints) * i] = file_weight_floats[i][k]
                else:
                    if all_exist_in_maya[k]:
                        weight_doubles.append(
                            old_weight_doubles[all_exist_in_maya[k] + len(maya_joints) * i]
                        )
                    else:
                        weight_doubles.append(0)

            # maya_joints
            #
            else:
                if not all_locks[k]:
                    weight_doubles.append(0)
                else:
                    if all_exist_in_maya[k]:
                        weight_doubles.append(
                            old_weight_doubles[all_exist_in_maya[k] + len(maya_joints) * i]
                        )
                    else:
                        weight_doubles.append(0)

    # normalize
    #
    for i in range(bind_vert_count):
        sum_a = 0
        sum_b = 0
        for inf in range(len(all_joints)):
            if not all_locks[inf]:
                sum_a += weight_doubles[inf + i * len(all_joints)]
            else:
                sum_b += weight_doubles[inf + i * len(all_joints)]

        if sum_a > 0.0001:
            sum_a_denom = 1 / sum_a
            for inf in range(len(all_joints)):
                if not all_locks[inf]:
                    weight_doubles[inf + i * len(all_joints)] *= sum_a_denom * (1 - sum_b)

    # soft selection
    #
    if do_soft_selection:
        for i in range(bind_vert_count):
            for inf in range(len(all_exist_in_maya)):
                index = inf + i * len(all_exist_in_maya)
                old_weights = old_weight_doubles[all_exist_in_maya[inf] + len(maya_joints) * i]

                weight_doubles[index] = weight_doubles[index] * soft_weights[i] + old_weights * (
                    1.0 - soft_weights[i]
                )

    # SET WEIGHTS
    #
    all_joints_indices = OpenMaya.MIntArray(len(all_exist_in_maya))
    for i in range(len(all_exist_in_maya)):
        all_joints_indices[i] = all_exist_in_maya[i]

    # print 'maya_joints: ', maya_joints
    # print 'all_joints_indices: ', all_joints_indices
    # print 'all_joints: ', all_joints
    # print 'weight_doubles before: ', weight_doubles

    print("setting weights...")
    fn_skin_cluster.setWeights(b_skin_path, vtx_components, all_joints_indices, weight_doubles, 0)

    # select the vertices
    #
    point_selection_list = OpenMaya.MSelectionList()
    point_selection_list.add(OpenMaya.MDagPath(node), vtx_components)
    OpenMaya.MGlobal.setActiveSelectionList(point_selection_list)

    print(("done, it took", (time.time() - time_before), " seconds"))


def vertex_to_id(vertex):
    """Extract vertex index from vertex component string.

    Args:
        vertex (str): Vertex component string (e.g., 'mesh.vtx[10]').

    Returns:
        int: Vertex index.
    """
    return int(vertex.split("[")[1].split("]")[0])


def vertex_to_id_list(verts):
    """Convert list of vertex component strings to list of indices.

    Args:
        verts (list): List of vertex component strings.

    Returns:
        list: List of vertex indices.
    """
    vert_ids = [0] * len(verts)
    for i, vert in enumerate(verts):
        vert_ids[i] = vertex_to_id(vert)
    return vert_ids


def b_save_vertex_skin_values(input_file, ignore_soft_selection):
    """Save vertex-level skin weights from selected vertices to file.

    Exports skin weight data for selected vertices to a formatted text file,
    optionally including soft selection weights.

    Args:
        input_file (str): Path to save weight file to.
        ignore_soft_selection (bool): If False, save soft selection weights.
    """
    time_before = time.time()

    print("saving Vertex skinWeights.. ")

    if not ignore_soft_selection:
        verts, soft_weights = get_soft_selection()
    else:
        verts = cmds.ls(selection=True, flatten=True)

    vert_ids = vertex_to_id_list(verts)
    selection = OpenMaya.MSelectionList()
    OpenMaya.MGlobal.getActiveSelectionList(selection)

    iterate = OpenMaya.MItSelectionList(selection)
    dag_path = OpenMaya.MDagPath()
    component = OpenMaya.MObject()
    iterate.getDagPath(dag_path, component)

    skin_cluster = b_find_skin_cluster(OpenMaya.MFnDagNode(dag_path).partialPathName())
    fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_cluster)

    if not skin_cluster.hasFn(OpenMaya.MFn.kSkinClusterFilter):
        print("no skinCluster found on selected vertices")
        return

    with open(input_file, "w", encoding="utf-8") as output:
        output.write(str(OpenMaya.MItGeometry(dag_path).count()) + "\n")

        fn_vtx_comp = OpenMaya.MFnSingleIndexedComponent()
        vtx_components = OpenMaya.MObject()
        vtx_components = fn_vtx_comp.create(OpenMaya.MFn.kMeshVertComponent)

        weight_array = OpenMaya.MFloatArray()
        mesh_iter = OpenMaya.MItMeshVertex(dag_path, component)
        # while not mesh_iter.isDone():
        for vert_id in vert_ids:
            fn_vtx_comp.addElement(vert_id)
            # mesh_iter.next()

        vertex_count = mesh_iter.count()
        script_util = OpenMaya.MScriptUtil()
        inf_count_ptr = script_util.asUintPtr()
        fn_skin_cluster.getWeights(dag_path, vtx_components, weight_array, inf_count_ptr)
        inf_count = OpenMaya.MScriptUtil.getUint(inf_count_ptr)

        weight_check_array = []
        for i in range(inf_count):
            weight_check_array.append(False)

        for i in range(vertex_count):
            for k in range(inf_count):
                if not weight_check_array[k] and weight_array[((i * inf_count) + k)]:
                    weight_check_array[k] = True

        # joints..
        influents_array = OpenMaya.MDagPathArray()
        fn_skin_cluster.influenceObjects(influents_array)
        for i in range(inf_count):
            if weight_check_array[i]:
                output.write(OpenMaya.MFnDagNode(influents_array[i]).name() + "\n")

        output.write("============\n")

        counter = 0
        weight_array_string = []
        for i in range(len(vert_ids)):
            vert_id = vert_ids[i]
            soft_weight = ""
            if not ignore_soft_selection:
                soft_weight = f"{soft_weights[i]:f}:"

            weights_string = " ".join(
                [
                    "0" if x == 0 else str(x)
                    for n, x in enumerate(weight_array[i * inf_count : (i + 1) * inf_count])
                    if weight_check_array[n]
                ]
            )
            weight_array_string = f"{vert_id}:{soft_weight}{weights_string}"

            output.write(weight_array_string + "\n")
            counter += 1
            next(mesh_iter)

    print(("done, it took", (time.time() - time_before), " seconds"))


def b_save_skin_values(input_file):
    """Save all skin weights from selected objects to file.

    Exports skin weight data for all vertices of selected mesh objects
    to a formatted text file.

    Args:
        input_file (str): Path to save weight file to.
    """
    time_before = time.time()

    with open(input_file, "w", encoding="utf-8") as output:
        selection = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(selection)

        iterate = OpenMaya.MItSelectionList(selection)

        while not iterate.isDone():
            node = OpenMaya.MDagPath()
            component = OpenMaya.MObject()
            iterate.getDagPath(node, component)
            if not node.hasFn(OpenMaya.MFn.kTransform):
                print(
                    OpenMaya.MFnDagNode(node).name()
                    + " is not a Transform node (need to select transform node of polyMesh)"
                )
            else:
                object_name = OpenMaya.MFnDagNode(node).name()
                new_transform = OpenMaya.MFnTransform(node)
                for child_index in range(new_transform.childCount()):
                    child_object = new_transform.child(child_index)
                    if (
                        child_object.hasFn(OpenMaya.MFn.kMesh)
                        or child_object.hasFn(OpenMaya.MFn.kNurbsSurface)
                        or child_object.hasFn(OpenMaya.MFn.kCurve)
                    ):
                        skin_cluster = b_find_skin_cluster(
                            OpenMaya.MFnDagNode(child_object).partialPathName()
                        )
                        if skin_cluster is not False:
                            b_skin_path = OpenMaya.MDagPath()
                            fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_cluster)
                            fn_skin_cluster.getPathAtIndex(0, b_skin_path)
                            influence_array = OpenMaya.MDagPathArray()
                            fn_skin_cluster.influenceObjects(influence_array)
                            influents_count = influence_array.length()
                            output.write(object_name + "\n")

                            for k in range(influents_count):
                                joint_tokens = str(influence_array[k].fullPathName()).split("|")
                                joint_tokens = joint_tokens[len(joint_tokens) - 1].split(":")
                                output.write(joint_tokens[len(joint_tokens) - 1] + "\n")

                            output.write("============\n")

                            fn_vtx_comp = OpenMaya.MFnSingleIndexedComponent()
                            vtx_components = OpenMaya.MObject()
                            vtx_components = fn_vtx_comp.create(OpenMaya.MFn.kMeshVertComponent)

                            vertex_count = OpenMaya.MFnMesh(b_skin_path).numVertices()
                            for i in range(vertex_count):
                                fn_vtx_comp.addElement(i)

                            weight_array = OpenMaya.MFloatArray()
                            script_util = OpenMaya.MScriptUtil()
                            inf_count_ptr = script_util.asUintPtr()
                            fn_skin_cluster.getWeights(
                                b_skin_path, vtx_components, weight_array, inf_count_ptr
                            )
                            inf_count = OpenMaya.MScriptUtil.getUint(inf_count_ptr)

                            for i in range(vertex_count):
                                # save_string = ' '.join(map(str,weight_array[i*inf_count : (i+1)*inf_count]))
                                save_string = " ".join(
                                    [
                                        "0" if x == 0 else str(x)
                                        for n, x in enumerate(
                                            weight_array[i * inf_count : (i + 1) * inf_count]
                                        )
                                    ]
                                )

                                output.write(save_string + "\n")

                            output.write("\n")

            next(iterate)

    print(("done saving weights, it took ", (time.time() - time_before), " seconds."))


def b_skin_object(object_name, file_joints, weights):
    """Apply skin weights to object from file data.

    Creates or updates a skin cluster on the specified object and applies
    weight data from a saved file.

    Args:
        object_name (str): Name of the mesh object to apply weights to.
        file_joints (list): List of joint names from the weight file.
        weights (list): List of weight strings for each vertex.
    """
    if not cmds.objExists(object_name):
        print((object_name, " doesn't exist - skipping. "))
        return

    it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kJoint)

    # quick check if all the joints are in scene
    #
    all_influences_in_scene = True
    scene_joint_tokens = []

    for joint_index in range(len(file_joints)):
        joint_here = False
        it = OpenMaya.MItDependencyNodes(OpenMaya.MFn.kJoint)
        while not it.isDone():
            scene_joint_tokens = str(OpenMaya.MFnDagNode(it.item()).fullPathName()).split("|")
            if str(file_joints[joint_index]) == str(
                scene_joint_tokens[len(scene_joint_tokens) - 1]
            ):
                joint_here = True

            next(it)

        if not joint_here:
            all_influences_in_scene = False
            print(("missing influence: ", file_joints[joint_index]))

    if not all_influences_in_scene:
        print((object_name, " can't be skinned because of missing influences."))
        return

    # create some arrays
    #
    all_joints_here = False
    file_joints_map_array = list(range(len(file_joints)))
    object_empty_joints = []

    # let's check if there's already a skinCluster, let's try to use that - if it contains all the needed joints
    #
    skin_cluster = b_find_skin_cluster(object_name)
    if not isinstance(skin_cluster, bool):
        fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_cluster)
        influents_array = OpenMaya.MDagPathArray()
        inf_count = fn_skin_cluster.influenceObjects(influents_array)

        influence_string_array = []
        for i in range(inf_count):
            influence_string_array.append(OpenMaya.MFnDagNode(influents_array[i]).name())

        all_joints_here = True
        for joint in file_joints:
            if joint not in influence_string_array:
                print(("missing a joint (", joint, ", ..)"))
                all_joints_here = False
                break

        if not all_joints_here:
            mel.eval("DetachSkin " + object_name)
        else:
            object_found_joints_in_file = [False] * len(influence_string_array)

            for i in range(len(file_joints)):
                for k in range(len(influence_string_array)):
                    if file_joints[i] == influence_string_array[k]:
                        file_joints_map_array[i] = k
                        object_found_joints_in_file[k] = True

            for i in range(len(influence_string_array)):
                if not object_found_joints_in_file[i]:
                    object_empty_joints.append(i)

            # print 'joint_map_array: ', file_joints_map_array

    if not all_joints_here:
        cmd = "select "
        for i in range(len(file_joints)):
            cmd += " " + file_joints[i]

        cmd += " " + object_name
        mel.eval(cmd)

        mel.eval("skinCluster -tsb -mi 10")
        mel.eval("select `listRelatives -p " + object_name + "`")
        mel.eval("refresh")
        # mel.eval("undoInfo -st 1")

        skin_cluster = b_find_skin_cluster(object_name)

    fn_skin_cluster = OpenMayaAnim.MFnSkinCluster(skin_cluster)
    influents_array = OpenMaya.MDagPathArray()
    fn_skin_cluster.influenceObjects(influents_array)

    b_skin_path = OpenMaya.MDagPath()
    fn_skin_cluster.getPathAtIndex(fn_skin_cluster.indexForOutputConnection(0), b_skin_path)

    weight_strings = []
    vertex_iter = OpenMaya.MItGeometry(b_skin_path)

    weight_doubles = OpenMaya.MDoubleArray()

    single_indexed = True
    vtx_components = OpenMaya.MObject()
    fn_vtx_comp = OpenMaya.MFnSingleIndexedComponent()
    fn_vtx_comp_double = OpenMaya.MFnDoubleIndexedComponent()

    if b_skin_path.node().apiType() == OpenMaya.MFn.kMesh:
        vtx_components = fn_vtx_comp.create(OpenMaya.MFn.kMeshVertComponent)
    elif b_skin_path.node().apiType() == OpenMaya.MFn.kNurbsSurface:
        single_indexed = False
        vtx_components = fn_vtx_comp_double.create(OpenMaya.MFn.kSurfaceCVComponent)
    elif b_skin_path.node().apiType() == OpenMaya.MFn.kNurbsCurve:
        vtx_components = fn_vtx_comp.create(OpenMaya.MFn.kCurveCVComponent)

    # nurbs curves..
    #
    counter_value = 0
    current_u = 0
    current_v = 0
    if not single_indexed:
        cvs_u = OpenMaya.MFnNurbsSurface(b_skin_path.node()).numCVsInU()
        cvs_v = OpenMaya.MFnNurbsSurface(b_skin_path.node()).numCVsInV()
        form_u = OpenMaya.MFnNurbsSurface(b_skin_path.node()).formInU()
        form_v = OpenMaya.MFnNurbsSurface(b_skin_path.node()).formInV()

        if form_u == 3:
            cvs_u -= 3
        if form_v == 3:
            cvs_v -= 3

    # go through all vertices and append to the weight_doubles array
    #
    vertex_iter = OpenMaya.MItGeometry(b_skin_path)
    while not vertex_iter.isDone():
        weight_strings = []
        if single_indexed:
            fn_vtx_comp.addElement(counter_value)
        else:
            fn_vtx_comp_double.addElement(current_u, current_v)
            current_v += 1
            if current_v >= cvs_v:
                current_v = 0
                current_u += 1

        weight_strings = weights[counter_value].split(" ")
        for i in range(len(weight_strings)):
            weight_doubles.append(float(weight_strings[i]))
        for i in range(len(object_empty_joints)):
            weight_doubles.append(0)

        counter_value += 1
        next(vertex_iter)

    # createing the influence Array
    #
    maya_file_joints_map_array = OpenMaya.MIntArray()
    for i in range(len(file_joints_map_array)):
        maya_file_joints_map_array.append(file_joints_map_array[i])
    for i in range(len(object_empty_joints)):
        maya_file_joints_map_array.append(object_empty_joints[i])

    # set the weights
    #
    fn_skin_cluster.setWeights(
        b_skin_path, vtx_components, maya_file_joints_map_array, weight_doubles, 0
    )
    # Maya.mel.eval("skinPercent -normalize true " + fn_skin_cluster.name() + " " + object_name)


def b_load_skin_values(load_on_selection, input_file):
    """Load skin weights from file and apply to objects.

    Reads a skin weight file and applies weights to mesh objects.
    Can load to selected object or all objects in the file.

    Args:
        load_on_selection (bool): If True, apply weights only to selected object.
        input_file (str): Path to the weight file to load.
    """
    time_before = time.time()

    joints = []
    weights = []
    polygon_object = ""

    if load_on_selection:
        selection_list = OpenMaya.MSelectionList()
        OpenMaya.MGlobal.getActiveSelectionList(selection_list)
        node = OpenMaya.MDagPath()
        component = OpenMaya.MObject()
        if selection_list.length():
            selection_list.getDagPath(0, node, component)
            if node.hasFn(OpenMaya.MFn.kTransform):
                new_transform = OpenMaya.MFnTransform(node)
                if new_transform.childCount():
                    if new_transform.child(0).hasFn(OpenMaya.MFn.kMesh):
                        polygon_object = str(
                            OpenMaya.MFnDagNode(new_transform.child(0)).partialPathName()
                        )

    if load_on_selection and len(polygon_object) == 0:
        print("You need to select a polygon object")
        return

    with open(input_file, encoding="utf-8") as input_stream:
        file_position = 0
        while True:
            line = input_stream.readline()
            if not line:
                break

            line = line.strip()

            if file_position != 0:
                if not line.startswith("============"):
                    if file_position == 1:
                        joints.append(line)
                    elif file_position == 2:
                        if len(line) > 0:
                            weights.append(line)
                        else:
                            b_skin_object(polygon_object, joints, weights)
                            polygon_object = ""
                            joints = []
                            weights = []
                            file_position = 0
                            if load_on_selection:
                                break

                else:  # it's ========
                    file_position = 2

            else:  # file_position == 0
                if not load_on_selection:
                    polygon_object = line
                file_position = 1

            if cmds.objExists(polygon_object):
                mel.eval("select " + polygon_object)
                mel.eval("refresh")

    print(("done loading weights, it took ", (time.time() - time_before), " seconds."))


def get_soft_selection():
    """Get vertex components from soft selection with weights.

    Returns:
        tuple: (vertex_list, weight_list) where weights are influence values
               from the soft selection.
    """
    # Grab the soft selection

    selection = OpenMaya.MSelectionList()
    soft_selection = OpenMaya.MRichSelection()
    OpenMaya.MGlobal.getRichSelection(soft_selection)
    soft_selection.getSelection(selection)

    dag_path = OpenMaya.MDagPath()
    component = OpenMaya.MObject()

    selection_iter = OpenMaya.MItSelectionList(selection, OpenMaya.MFn.kMeshVertComponent)
    elements, weights = [], []
    while not selection_iter.isDone():
        selection_iter.getDagPath(dag_path, component)
        dag_path.pop()  # Grab the parent of the shape node
        node = dag_path.fullPathName()
        fn_comp = OpenMaya.MFnSingleIndexedComponent(component)

        def get_weight(index, comp=fn_comp):
            if comp.hasWeights():
                return comp.weight(index).influence()
            return 1.0

        for i in range(fn_comp.elementCount()):
            elements.append(f"{node}.vtx[{fn_comp.element(i)}]")
            weights.append(get_weight(i))
        next(selection_iter)

    return elements, weights
