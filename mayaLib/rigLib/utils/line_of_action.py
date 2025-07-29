import math

import maya.OpenMaya as OpenMaya
import maya.cmds as cmds
import pymel.core as pm


def vector_diff(v1, v2):
    """Return the difference between two vectors.

    Args:
        v1 (list): The first vector as a list of coordinates.
        v2 (list): The second vector as a list of coordinates.

    Returns:
        float: The difference vector between the two vectors.
    """
    return [a - b for a, b in zip(v1, v2)]


def vector_length(v):
    """Return the Euclidean norm of vector v.

    Args:
        v (list): A vector as a list of coordinates.

    Returns:
        float: The Euclidean norm of the vector.
    """
    return math.sqrt(sum(x * x for x in v))


def vector_normalized(v):
    """Return the vector v normalized to unit length.

    Args:
        v (list): A vector as a list of coordinates.

    Returns:
        list: The normalized vector as a list of coordinates.
    """
    norm = vector_length(v)
    if norm == 0:
        return v
    return [x / norm for x in v]


def matrix_mult_vector(matrix, vector):
    """Multiply a square matrix by a vector.

    Args:
        matrix (list): A square matrix as a list of lists.
        vector (list): A vector as a list of coordinates.

    Returns:
        list: The resulting vector as a list of coordinates.
    """
    dimension = len(matrix)
    result = [0.0] * dimension
    for i in range(dimension):
        for j in range(len(vector)):
            result[i] += matrix[i][j] * vector[j]
    return result


def compute_principal_eigenvector(input_matrix, max_iterations=1000, tolerance=1e-9):
    """Computes the principal eigenvector of a square matrix using the
    power iteration method. The principal eigen vector is the direction
    of maximum variance in the data represented by the matrix. It corresponds
    to the largest eigenvalue of the covariance matrix and it is the principal
    component of PCA.


    Args:
        input_matrix (list): A square matrix represented as a list of lists.
        max_iterations (int, optional): Maximum number of power-iteration steps to run.
            Defaults to 1000.
        tolerance (float, optional): Threshold for convergence. Defaults to 1e-9.

    Returns:
        list: A unit-length vector approximating the principal eigenvector.
    """
    dimension = len(input_matrix)

    # 1) Initialize with a guess (all ones) and normalize
    eigenvector_estimate = [1.0] * dimension
    eigenvector_estimate = vector_normalized(eigenvector_estimate)

    for _ in range(max_iterations):
        # 2) Apply the matrix
        transformed_vector = matrix_mult_vector(input_matrix, eigenvector_estimate)

        # 3) Normalize the result
        next_estimate = vector_normalized(transformed_vector)

        # 4) Check for convergence
        difference_vector = vector_diff(next_estimate, eigenvector_estimate)
        difference_norm = vector_length(difference_vector)
        if difference_norm < tolerance:
            break

        # 5) Update for next iteration
        eigenvector_estimate = next_estimate

    return eigenvector_estimate


def compute_covariance_matrix(centered_points):
    """Compute the covariance matrix from the centered points.
    Uses the sample covariance (dividing by n-1). The covariance
    matrix is a square matrix where the element at (i, j) represents
    the covariance between the i-th and j-th dimensions. It describes
    the shape and orientation of the points distribution to allow to
    obtain the oriented bounding box.

    Args:
        centered_points (list): A list of centered points, where each
            point is a list of coordinates.

    Returns:
        list: The covariance matrix as a list of lists.
    """
    num_points = len(centered_points)
    if num_points < 2:
        return None
    dimension = len(centered_points[0])
    # Initialize a d x d matrix filled with 0's
    cov_matrix = [[0.0] * dimension for _ in range(dimension)]
    for p in centered_points:
        for i in range(dimension):
            for j in range(dimension):
                cov_matrix[i][j] += p[i] * p[j]
    factor = 1.0 / (num_points - 1)
    for i in range(dimension):
        for j in range(dimension):
            cov_matrix[i][j] *= factor
    return cov_matrix


def compute_main_axis(points):
    """Given a list of points as a list or tuple of coordinates,
    compute the main axis of the set of points using PCA.
    PCA (Principal Component Analysis) is a linear dimensionality
    reduction technique that allows to find the main axis of a set
    of points. The main axis is the direction of maximum variance
    in the data.

    Args:
        points (list): A list of points, where each point is a list
            or tuple of coordinates.

    Returns:
        centroid: The centroid of the points.
        main_axis: A unit vector representing the main axis.
    """
    if not points:
        return None, None
    dimension = len(points[0])
    # Ensure all points have the same dimension
    for p in points:
        if len(p) != dimension:
            return None, None

    centroid = compute_centroid(points)
    centered_points = center_points(points, centroid)
    cov_matrix = compute_covariance_matrix(centered_points)
    main_axis = compute_principal_eigenvector(cov_matrix)
    return centroid, main_axis


def get_points_py_list(geo_name):
    """Get the vertices of a mesh using maya.OpenMaya API.

    Args:
        geo_name (str): The name of the mesh.

    Returns:
        list: A list of vertices, where each vertex is a list of coordinates.
    """
    vertices = []

    maya_sel = OpenMaya.MSelectionList()
    maya_sel.add(geo_name)
    geo_dag = OpenMaya.MDagPath()
    maya_sel.getDagPath(0, geo_dag)
    geo_fn = OpenMaya.MFnMesh(geo_dag)
    geo_points = OpenMaya.MPointArray()
    geo_fn.getPoints(geo_points)
    geo_triangles_count = OpenMaya.MIntArray()
    geo_triangles_vertices = OpenMaya.MIntArray()
    geo_fn.getTriangles(geo_triangles_count, geo_triangles_vertices)

    points_count = geo_points.length()
    for point_index in range(points_count):
        vertices.append(
            [
                geo_points[point_index].x,
                geo_points[point_index].y,
                geo_points[point_index].z,
            ]
        )

    return vertices


def get_closest_point_and_uv(mesh, query_point):
    """Uses maya.OpenMaya to find the closest point on the mesh to
    target_point and retrieves the corresponding UV coordinates.

    Args:
        mesh (str): The name of the mesh.
        query_point (tuple): A 3-tuple (x, y, z) position for which
            to find the closest point.

    Returns:
        tuple: (closestPoint (MPoint), (u, v) coordinates)
    """
    # Obtain the MObject for the mesh.
    selList = OpenMaya.MSelectionList()
    selList.add(mesh)
    mesh_dag = OpenMaya.MDagPath()
    selList.getDagPath(0, mesh_dag)

    # Create an MFnMesh for API operations.
    mesh_fn = OpenMaya.MFnMesh(mesh_dag)
    mesh_points = OpenMaya.MPointArray()
    mesh_fn.getPoints(mesh_points)

    # Create an MPoint from the query point coordinates.
    query = OpenMaya.MPoint(query_point[0], query_point[1], query_point[2])
    closest_point = OpenMaya.MPoint()

    closest_polygon_util = OpenMaya.MScriptUtil()
    closest_polygon_util.createFromInt(-1)
    closest_polygon_ptr = closest_polygon_util.asIntPtr()

    # Compute the closest point on the mesh (in world space).
    mesh_fn.getClosestPoint(
        query, closest_point, OpenMaya.MSpace.kWorld, closest_polygon_ptr
    )
    closest_polygon = OpenMaya.MScriptUtil.getInt(closest_polygon_ptr)

    # Prepare MScriptUtil objects for retrieving U and V values.
    uv_util = OpenMaya.MScriptUtil()
    uv_util.createFromList([0.0, 0.0], 2)
    uv_point = uv_util.asFloat2Ptr()

    # Get the UV coordinates at the closest point
    polygon_vertices = OpenMaya.MIntArray()
    mesh_fn.getPolygonVertices(closest_polygon, polygon_vertices)
    polygon_vertices_count = polygon_vertices.length()
    polygon_average_point = OpenMaya.MPoint(0.0, 0.0, 0.0)
    for i in range(polygon_vertices_count):
        vertex_index = polygon_vertices[i]
        polygon_average_point += OpenMaya.MVector(mesh_points[vertex_index])
    if polygon_vertices_count > 0:
        polygon_average_point /= polygon_vertices_count
    mesh_fn.getClosestPoint(
        polygon_average_point, closest_point, OpenMaya.MSpace.kWorld
    )
    mesh_fn.getUVAtPoint(closest_point, uv_point, OpenMaya.MSpace.kWorld)

    u = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 0)
    v = OpenMaya.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 1)

    return closest_point, (u, v)


def get_sensor_locator_driver_node(node, matrix_plug, position_plug):
    """Get the driver node from a locator or sensor depending on the connection
    that had been made using the matrix or the position plug.
        - If the matrix plug has a connection return the node directly associated (joint, locator, etc).
        - If the position plug has a connection return the node associated to the
          'decomposeMatrix' that was attached to the plug (joint, locator, etc).

    Args:
        node (str): The locator or sensor node from which to extract the
            driver node from.
        matrix_plug (str): Matrix plug of the locator or sensor. Eg. 'endMatrix'.
        position_plug (str): Position plug of the locator or sensor. Eg. 'endPosition'.

    Returns:
        str: Returns the name of the driver node (joint, locator, etc).
            None if not found.
    """
    conn = cmds.listConnections("{0}.{1}".format(node, matrix_plug))
    if conn:
        return conn[0]

    matrix = cmds.listConnections(
        "{0}.{1}".format(node, position_plug), type="decomposeMatrix"
    )
    if not matrix:
        return None
    conn = cmds.listConnections("{0}.inputMatrix".format(matrix[0]))
    if not conn:
        return None

    return conn[0]


def compute_centroid(points):
    """Compute the centroid of a list of points.

    Args:
        points (list): A list of points, where each point is a list of coordinates.

    Returns:
        list: The centroid of the points as a list of coordinates.
    """
    num_points = len(points)
    if num_points == 0:
        return []
    dimension = len(points[0])
    centroid = [0.0] * dimension
    for p in points:
        for i in range(dimension):
            centroid[i] += p[i]
    centroid = [x / num_points for x in centroid]
    return centroid


def center_points(points, centroid):
    """Subtract the centroid from each point to center the data.

    Args:
        points (list): A list of points, where each point is a list of coordinates.
        centroid (list): The centroid to subtract from each point.

    Returns:
        list: A new list of centered points.
    """
    return [[p[i] - centroid[i] for i in range(len(centroid))] for p in points]


def squared_distance(p1, p2):
    """Compute the squared distance between two points.

    Args:
        p1 (list): The first point as a list of coordinates.
        p2 (list): The second point as a list of coordinates.

    Returns:
        float: The squared distance between the two points.
    """
    return (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2


def find_extremal_vertices(vertices, centroid, direction):
    """Find the two vertices of a mesh that are extremal in the direction
    of the main axis. The two vertices are the closest to the end points
    of the line defined by the centroid and the direction vector.

    This is done by intersecting a parametric line (along the main axis) with
    the mesh's axis-aligned bounding box (AABB), determining the entry and exit
    points of that line through the box, and then selecting the mesh vertices
    closest to those two intersection points.

    The line is expressed in parametric form:
        P(t) = C + t * d
    where:
        C is the mesh centroid,
        d is the direction vector of the main axis,
        t is the scalar parameter.

    As t varies:
      - P(0) = C, the line passes through the centroid.
      - P(t) for t < 0 moves opposite to the direction vector.
      - P(t) for t > 0 moves along the direction vector.

    Args:
        vertices (list): A list of vertices, where each vertex is a list of coordinates.
        centroid (list): The centroid of the mesh as a list of coordinates.
        direction (list): The direction vector as a list of coordinates.

    Returns:
        dict: A dictionary containing the start and end vertices and their indices.
              The keys are "start_vertex", "end_vertex", "start_index", and "end_index".
              If no valid extremal vertices are found, returns None.
    """
    # Unpack centroid and direction for convenience
    centroid_x, centroid_y, centroid_z = centroid
    dir_x, dir_y, dir_z = direction

    # 1. Compute the bounding box of the mesh.
    min_x = min(v[0] for v in vertices)
    max_x = max(v[0] for v in vertices)
    min_y = min(v[1] for v in vertices)
    max_y = max(v[1] for v in vertices)
    min_z = min(v[2] for v in vertices)
    max_z = max(v[2] for v in vertices)

    # 2. Compute intersection points of the line with the bounding box.

    # The line is defined by the parametric equation of a line: P(t) = C + t * d.
    # Where C is the centroid, d is the direction vector and t is the parameter.

    # For each axis, solve for t at the min and max boundaries.
    intersections = []  # will store tuples of (t, (x, y, z))
    eps = 1e-8  # small tolerance to avoid numerical issues
    # For each axis: 0 -> x, 1 -> y, 2 -> z.
    for axis in range(3):
        if axis == 0:
            boundaries = [min_x, max_x]
            centroid_axis = centroid_x
            dir_axis = dir_x
        elif axis == 1:
            boundaries = [min_y, max_y]
            centroid_axis = centroid_y
            dir_axis = dir_y
        else:  # axis == 2
            boundaries = [min_z, max_z]
            centroid_axis = centroid_z
            dir_axis = dir_z

        # Avoid division by zero
        if abs(dir_axis) < eps:
            continue

        for boundary in boundaries:
            # By solving centroid_axis + t * dir_axis = boundary for each face of the
            # bounding box, we find the t values at which the line intersects those faces
            t = (boundary - centroid_axis) / dir_axis
            # The corresponding P(t) gives the intersection point
            p_x = centroid_x + t * dir_x
            p_y = centroid_y + t * dir_y
            p_z = centroid_z + t * dir_z

            # Check if the intersection point lies within the bounding limits for the other axes.
            if axis == 0:
                if (min_y - eps <= p_y <= max_y + eps) and (
                    min_z - eps <= p_z <= max_z + eps
                ):
                    intersections.append((t, (p_x, p_y, p_z)))
            elif axis == 1:
                if (min_x - eps <= p_x <= max_x + eps) and (
                    min_z - eps <= p_z <= max_z + eps
                ):
                    intersections.append((t, (p_x, p_y, p_z)))
            else:  # axis == 2
                if (min_x - eps <= p_x <= max_x + eps) and (
                    min_y - eps <= p_y <= max_y + eps
                ):
                    intersections.append((t, (p_x, p_y, p_z)))

    # Ensure we found at least two intersections.
    if len(intersections) < 2:
        return None

    # Sort intersections by the parameter t.
    intersections.sort(key=lambda item: item[0])
    # The two endpoints are at the smallest and largest t.
    end_point_1 = intersections[0][1]
    end_point_2 = intersections[-1][1]

    # 3. Find the vertex closest to each end point.
    closest_vertex_1 = None
    closest_vertex_2 = None
    closest_index_1 = None
    closest_index_2 = None
    min_dist_1 = float("inf")
    min_dist_2 = float("inf")

    for i, v in enumerate(vertices):
        d1 = squared_distance(v, end_point_1)
        if d1 < min_dist_1:
            min_dist_1 = d1
            closest_vertex_1 = v
            closest_index_1 = i
        d2 = squared_distance(v, end_point_2)
        if d2 < min_dist_2:
            min_dist_2 = d2
            closest_vertex_2 = v
            closest_index_2 = i

    extremal_vertices_data = {
        "start_point": closest_vertex_1,
        "end_point": closest_vertex_2,
        "start_index": closest_index_1,
        "end_index": closest_index_2,
    }

    return extremal_vertices_data


def get_name_from_geo(geo_name, object_name):
    """Generates a name for the object based on the geometry name and the object type.
    If the geometry name ends with "GEO" or "geo", it is removed before concatenation.

    Args:
        geo_name (str): The name of the geometry.
        object_name (str): The name of the object type.

    Returns:
        str: The generated name for the object.
    """
    if not object_name:
        return ""
    if not geo_name:
        return object_name

    if geo_name.upper().endswith("GEO"):
        geo_name = geo_name[:-3]

    return "{0}{1}".format(geo_name, object_name)


def create_rivet_at_point(mesh, target_point, rivet_base_name, space_scale=1.0):
    """Creates a rivet-based rivet on the given mesh at the point closest
    to target_point. The rivet is positioned based on UV coordinates computed
    via maya.OpenMaya, so the resulting locator will follow the mesh as it deforms.

    Args:
        mesh (str): The name of the mesh (e.g., "mummy_geo").
        target_point (tuple): A 3-tuple (x, y, z) representing the target point.
        rivet_base_name (str): Base name for the created nodes.
        space_scale (float, optional): The scale factor for the space scale parameter of
            the nodes. Defaults to 1.0.

    Returns:
        str: The name of the uvPin node created.
        str: The name of the uvOutput node created.
    """
    # Use the API to compute the closest point and its UV in world space.
    closest_point, (u, v) = get_closest_point_and_uv(mesh, target_point)

    # Get the shape node for the mesh.
    if cmds.nodeType(mesh) != "mesh":
        shapes = cmds.listRelatives(mesh, shapes=True)
        if not shapes:
            return None, None

    if rivet_base_name is None:
        rivet_base_name = ""

    # Create a rivet node.
    cmds.select("{0}.f[0]".format(mesh))
    rivet_name = "{0}_rivet".format(rivet_base_name)
    rivet_locator_name = "{0}_rivet_loc".format(rivet_base_name)
    cmds.Rivet()
    uv_pin, pin_output = cmds.ls(selection=True)
    rivet_name = cmds.rename(uv_pin, rivet_name)
    rivet_locator_name = cmds.rename(pin_output, rivet_locator_name)

    # Set the rivet's UV parameters based on the computed UV.
    cmds.setAttr("{0}.coordinate[0].coordinateU".format(rivet_name), u)
    cmds.setAttr("{0}.coordinate[0].coordinateV".format(rivet_name), v)

    # Set local scale based on the space scale for better visualization
    if space_scale > 1e-6:
        local_scale = 1.0 / space_scale
        cmds.setAttr("{0}.localScaleX".format(rivet_locator_name), local_scale)
        cmds.setAttr("{0}.localScaleY".format(rivet_locator_name), local_scale)
        cmds.setAttr("{0}.localScaleZ".format(rivet_locator_name), local_scale)

    return rivet_name, rivet_locator_name


def create_line_of_action(geo, skeleton_geo, name_suffix="_loa_crv", space_scale=1.0):
    """Create a line of action curve between two extremal points on a geometry.

    This function computes the main axis of a given geometry and identifies two
    extremal vertices along that axis. It then creates a rivet and locator at
    each of these vertices and generates a curve between the locators in the world
    space.

    Args:
        geo (str): The name of the geometry to process.
        skeleton_geo (str): The name of the skeleton geometry where the rivets
            will be attached.
        name_suffix (str, optional): Suffix to append to the curve name. Defaults to "_loa_crv".
        space_scale (float, optional): Scale factor for the space. Defaults to 1.0.

    Returns:
        str: The name of the created curve.
    """
    # Retrieve vertices positions from the geometry.
    vertices = get_points_py_list(geo)

    # Compute the main axis of the geometry.
    main_axis_info = compute_main_axis(vertices)
    fibers_centroid = main_axis_info[0]
    fibers_dir = main_axis_info[1]

    # Find the extremal vertices along the main axis.
    extremal_vertices_data = find_extremal_vertices(
        vertices, fibers_centroid, fibers_dir
    )

    # Extract start and end points and indices.
    start_index = extremal_vertices_data["start_index"]
    end_index = extremal_vertices_data["end_index"]
    start_point = extremal_vertices_data["start_point"]
    end_point = extremal_vertices_data["end_point"]

    # Generate names for rivets based on the geometry's short name.
    geo_short_name = str(geo).split("|")[-1]
    rivet_start_name = get_name_from_geo(geo_short_name, "SensorStart")
    rivet_end_name = get_name_from_geo(geo_short_name, "SensorEnd")

    # Create rivets and locators at the extremal points.
    rivet_start, locator_start = create_rivet_at_point(
        skeleton_geo, start_point, rivet_start_name, space_scale
    )
    rivet_end, locator_end = create_rivet_at_point(
        skeleton_geo, end_point, rivet_end_name, space_scale
    )

    # Create a curve between the locators in world space.
    cv_name = str(geo).replace("_geo", "") + name_suffix
    p1 = cmds.getAttr("{0}.worldSpace[0]".format(locator_start))
    p2 = cmds.getAttr("{0}.worldSpace[0]".format(locator_end))
    curve = cmds.curve(p=[p1, p2], degree=1, name=cv_name)

    return curve
