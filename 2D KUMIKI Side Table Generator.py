"""SOTSUSEI"""
"""Make KUMIKI side table"""

import rhinoscriptsyntax as rs
import sys

"""
# PARAMETERs
    # TABLE
    width           int     width of table (mm)
    height          int     height of table (mm)
    t_m             int     thickness of material : 1 layer (mm)

    # material1
    x_m1            int     x length of material1
    y_m1            int     y length of material1
    z_m             int     z length of material
    m1_points       list    list of m1 points
    m1_info         list    list of material1 information
                            [x_m1, y_m1, z_m, m1_points]

    # material2
    x_m2            int     x length of material2
    y_m2            int     y length of material2
    z_m             int     z length of material
    m2_points       list    list of m2 points
    m2_info         list    list of material2 information
                            [x_m2, y_m2, z_m, m2_points]

    # material3
    x_m3            int     x length of material3
    y_m3            int     y length of material3
    z_m             int     z length of material
    m3_points       list    list of m3 points
    m3_info         list    list of material3 information
                            [x_m3, y_m3, z_m, m3_points]


    # NOTE:
    1   Get information of table
    2   From table information, make m1_info, m2_info, m3_info
    3   Ask KUMIKI (2 type ; TSUGITE & SHIGUCHI) to make.
        (***In this SOTSUSEI, just 1 pattern ; ARI and IRIWA ***)
    4   From these information, make shape of parts.
        m2
        m3
        m1
"""

# FUNCTIONs---------------------------------------------------------------------
def delete_all():
    """Delete all objects if user wants."""
    answer = ['YES', 'NO']
    str = rs.GetString("Delete all objects?", 'YES', answer)

    if str == 'YES':
        obs = rs.ObjectsByType(0)
        rs.DeleteObjects(obs)
    elif str == 'NO':
        pass
    else:
        sys.exit()

# ------------------------------------------------------------------------------
def RUN():
    """Runner of this code.
    Receives:
        ---
    Returns:
        ---
    """
    TABLE_info = get_TABLE_info()
    m1_info, m2_info, m3_info, m4_info = get_material_info(TABLE_info)

    TSUGITE_name, SHIGUCHI_name, offset = ask_KUMIKI()

    # TSUGITE_list = [m2_left_list, m2_right_list, m3_left_list, m3_right_list]
    TSUGITE_list, m2_SEN_info, m3_SEN_info = make_TSUGITE_list(TSUGITE_name, m2_info, m3_info, m4_info, offset)

    # SHIGUCHI_list = [m2_KUMIKI_points1, m2_KUMIKI_points2, m3_KUMIKI_points1, m3_KUMIKI_points2]
    SHIGUCHI_list = make_SHIGUCHI_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset)

    # m1
    m1_male_points_list, m1_male_SEN_info = make_male_m1_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset)
    m1_female_points_list, m1_female_SEN_info = make_female_m1_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset)

    m1_male_crvs = make_m1_male_crv(m1_male_points_list)
    m1_female_crvs = make_m1_female_crv(m1_female_points_list)

    # m2, m3 crvs
    m2_male_left_crvs, m2_male_right_crvs = make_m2_crv(TSUGITE_list, SHIGUCHI_list)
    m3_male_left_crvs, m3_male_right_crvs = make_m3_crv(TSUGITE_list, SHIGUCHI_list)

    m2_female_left_crvs = rs.CopyObjects(m2_male_left_crvs)
    m2_female_right_crvs = rs.CopyObjects(m2_male_right_crvs)
    m3_female_left_crvs = rs.CopyObjects(m3_male_left_crvs)
    m3_female_right_crvs = rs.CopyObjects(m3_male_right_crvs)

    # m4
    m4_male_points_list, m4_male_SEN_info = make_male_m4_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset)
    m4_female_points_list, m4_female_SEN_info = make_female_m4_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset)

    m4_male_crvs = make_m4_male_crv(m4_male_points_list)
    m4_female_crvs = make_m4_female_crv(m4_female_points_list)

    make_SEN_crvs(m1_male_SEN_info, m1_female_SEN_info, m2_SEN_info, m3_SEN_info, m4_male_SEN_info, m4_female_SEN_info, offset)

    # Make 3D
    male_models = make_male_3D_model\
    (TABLE_info, m1_male_crvs, m2_male_left_crvs, m2_male_right_crvs,\
    m3_male_left_crvs, m3_male_right_crvs, m4_male_crvs)

    female_models = make_female_3D_model\
    (TABLE_info, m1_female_crvs, m2_female_left_crvs, m2_female_right_crvs,\
    m3_female_left_crvs, m3_female_right_crvs, m4_female_crvs)

    # Deploy crvs (processing data)
    deploy_male_crvs\
    (TABLE_info, m1_male_crvs, m2_male_left_crvs, m2_male_right_crvs,\
    m3_male_left_crvs, m3_male_right_crvs, m4_male_crvs)

    deploy_female_crvs\
    (TABLE_info, m1_female_crvs, m2_female_left_crvs, m2_female_right_crvs,\
    m3_female_left_crvs, m3_female_right_crvs, m4_female_crvs)

    make_board(TABLE_info)

    rs.ZoomExtents()
    pass

# Element FUNCTIONs-------------------------------------------------------------
# Get info----------------------------------------------------------------------
def get_TABLE_info():
    """Get TABLE info from user.
    Receives:
        ---
    Returns:
        TABLE_info      list    [width, height, t_m]
        width           int     width of table mm
        height          int     height of table mm
        t_m             int     thickness of material (1 layer) mm
    """
    defalt_width = 300
    defalt_height = 500
    defalt_thickness = 10

    message = 'Put width of table. (mm : int) (width >= 210)'
    width = rs.GetInteger(message, defalt_width, None, None)

    message = 'Put height of table. (mm : int) (height >= 250)'
    height = rs.GetInteger(message, defalt_height, None, None)

    message = 'Put thickness of material (1layer). (mm : int)'
    t_m = rs.GetReal(message, defalt_thickness, None, None)

    TABLE_info = [width, height, t_m]

    info = ["width : %s" % width, "height : %s" % height, "thickness of material : %s" % t_m]
    print (info)

    return TABLE_info

def get_material_info(TABLE_info):
    """Get material info from TABLE_info
    Receives:
        TABLE_info      list    [width, height, t_m]
        width           int     width of table mm
        height          int     height of table mm
        t_m             int     thickness of material (1 layer) mm
    Returns:
        # material1
        x_m1            int     x length of material1
        y_m1            int     y length of material1
        z_m             int     z length of material
        m1_points       list    list of m1 points
        m1_info         list    list of material1 information
                                [x_m1, y_m1, z_m, m1_points, t_sen]
        # material2
        x_m2            int     x length of material2
        y_m2            int     y length of material2
        z_m             int     z length of material
        m2_points       list    list of m2 points
        m2_info         list    list of material2 information
                                [x_m2, y_m2, z_m, m2_points, t_sen]
        # material3
        x_m3            int     x length of material3
        y_m3            int     y length of material3
        z_m             int     z length of material
        m3_points       list    list of m3 points
        m3_info         list    list of material3 information
                                [x_m3, y_m3, z_m, m3_points, t_sen]

        # material4
        x_m4            int     x length of material4
        y_m4            int     y length of material4
        z_m             int     z length of material
        m4_points       list    list of m4 points
        m4_info         list    list of material4 information
                                [x_m4, y_m4, z_m, m4_points, t_sen]
    """
    """
    1   Get info from TABLE_info.
    """
    width = TABLE_info[0]
    height = TABLE_info[1]
    t_m = TABLE_info[2]

    """
    2   Get material info.
    """
    z_m = 3 * t_m

    m_width = rs.GetInteger("Put the width of material", z_m, None, None)

    t_sen = rs.GetReal("Put Int(mm): Thickness of material to cut SEN.", t_m / 2, None, None)

    x_m1 = m_width
    x_m2 = height - x_m1
    x_m3 = x_m2
    x_m4 = x_m1

    y_m2 = m_width
    y_m3 = y_m2
    y_m1 = width - (y_m2 + y_m3)
    y_m4 = y_m1


    # material1
    m1_p0 = (x_m3, y_m3)
    m1_p1 = (x_m3, y_m3 + y_m1)
    m1_p2 = (x_m3 + x_m1, y_m3 + y_m1)
    m1_p3 = (x_m3 + x_m1, y_m3)
    m1_points = [m1_p0, m1_p1, m1_p2, m1_p3]

    m1_info = [x_m1, y_m1, z_m, m1_points, t_sen]

    # material2
    m2_p0 = (0, width - y_m2)
    m2_p1 = (0, width)
    m2_p2 = (height - x_m1, width)
    m2_p3 = (height - x_m1, width - y_m2)
    m2_points = [m2_p0, m2_p1, m2_p2, m2_p3]

    m2_info = [x_m2, y_m2, z_m, m2_points, t_sen]

    # material3
    m3_p0 = (0, 0)
    m3_p1 = (0, y_m3)
    m3_p2 = (x_m3, y_m3)
    m3_p3 = (x_m3, 0)
    m3_points = [m3_p0, m3_p1, m3_p2, m3_p3]

    m3_info = [x_m3, y_m3, z_m, m3_points, t_sen]

    # material4
    m4_p0 = (0, y_m3)
    m4_p1 = (0, y_m3 + y_m4)
    m4_p2 = (-x_m4, y_m3 + y_m4)
    m4_p3 = (-x_m4, y_m3)
    m4_points = [m4_p0, m4_p1, m4_p2, m4_p3]

    m4_info = [x_m4, y_m4, z_m, m4_points, t_sen]

    return m1_info, m2_info, m3_info, m4_info

def ask_KUMIKI():
    """Ask KUMIKI to make.
    Receives:
        ---
    Returns:
        TSUGITE_name    str     name of TSUGITE to make on legs
        SHIGUCHI_name   str     name of SHIGUCHI to make at corner
        offset          num     offset num to fit KUMIKI tight : real number
    """
    # TSUGITE
    TSUGITE_strings = ['ARI', 'KAMA', 'RYAKUKAMA', 'MECHIGAI', 'AIKAKI','KOSHIKAKE', 'HAKO']
    message = 'Which TSUGITE to make on legs?'

    TSUGITE_name = rs.GetString(message, 'ARI', TSUGITE_strings)

    # SIGUCHI
    SHIGUCHI_strings = ['TOME', 'IRIWA', 'SANMAIKUMI', 'AIKAKI', 'HAKO']
    message = 'Which SHIGUCHI to make at corner?'

    SHIGUCHI_name = rs.GetString(message, 'IRIWA', SHIGUCHI_strings)

    print ('TSUGITE : %s' % TSUGITE_name)
    print ('SHIGUCHI : %s' % SHIGUCHI_name)

    """
        Get ofset num.
    """
    minimum = 0
    maximum = 0.3

    offset = rs.GetReal("Put the offset num to fit KUMIKI tight. (0.0 < offset < 0.3)",\
                        0.15, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    return TSUGITE_name, SHIGUCHI_name, offset

# Make lists--------------------------------------------------------------------
def make_TSUGITE_list(TSUGITE_name, m2_info, m3_info, m4_info, offset):
    """Make TSUGITE on legs. (m2, m3)
    Receives:
        TSUGITE_name    str     TSUGITE name
        m_info          list    list of material information
        offset          num     offset num to fit KUMIKI tight : real number

    Returns:
        TSUGITE_list    list    list of list
    """
    """
    1   Get information from m_info.
    """
    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m2 = m2_info[2]

    m2_points = m2_info[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m3 = m3_info[2]

    m3_points = m3_info[3]

    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    """
    2   Get base point to make TSUGITE.
    """
    # base_point = (dx, dy)
    dx_U = x_m2 / 2
    dy_U = m2_p0[1]

    dx_L = x_m3 / 2
    dy_L = m3_p0[1]

    """
    3   Call appropriate function.
    """
    if TSUGITE_name == 'ARI':
        dx = dx_U
        dy = dy_U
        m_info = m2_info

        m2_left_list, m2_right_list, m2_SEN_info = make_ARI_list(dx, dy, m_info, offset)

        dx = dx_L
        dy = dy_L
        m_info = m3_info

        m3_left_list, m3_right_list, m3_SEN_info = make_ARI_list(dx, dy, m_info, offset)

    elif TSUGITE_name == 'KAMA':
        pass
    elif TSUGITE_name == 'RYAKUKAMA':
        pass
    elif TSUGITE_name == 'MECHIGAI':
        pass
    elif TSUGITE_name == 'AIKAKI':
        pass
    elif TSUGITE_name == 'KOSHIKAKE':
        pass
    elif TSUGITE_name == 'HAKO':
        pass
    else:
        sys.exit()

    TSUGITE_list = [m2_left_list, m2_right_list, m3_left_list, m3_right_list]

    return TSUGITE_list, m2_SEN_info, m3_SEN_info

def make_SHIGUCHI_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset):
    """Make SHIGUCHI on upper materials.
    Receives:
        SHIGUCHI_name   str     SHIGUCHI name
        m1_info         list    list of material information
        m2_info         list    list of material information
        m3_info         list    list of material information
        m4_info         list    list of material information
        offset          num     offset num to fit KUMIKI tight

    Returns:
        SHIGUCHI_list   list    list of list
    """
    """
    1   Get information from m1_info, m2_info, m3_info
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m2 = m2_info[2]

    m2_points = m2_info[3]

    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m = m3_info[2]

    m3_points = m3_info[3]

    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]

    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    """
    2   Get base point to make SHIGUCHI
        m1 & m2 -> base point = m2_p3 = (dx_U_right, dy_U_right)
        m1 & m3 -> base point = m3_p2 = (dx_L_right, dy_L_right)

        m4 & m2 -> base point = m2_p0 = (dx_U_left, dy_U_left)
        m4 & m3 -> base point = m3_p1 = (dx_L_left, dy_L_left)
    """
    dx_U_right = m2_p3[0]
    dy_U_right = m2_p3[1]

    dx_L_right = m3_p2[0]
    dy_L_right = m3_p2[1]

    dx_U_left = m2_p0[0]
    dy_U_left = m2_p0[1]

    dx_L_left = m3_p1[0]
    dy_L_left = m3_p1[1]

    """
    3   Call appropriate function.
    """
    if SHIGUCHI_name == 'TOME':
        pass
    elif SHIGUCHI_name == 'IRIWA':
        # Right side
        dx = dx_U_right
        dy = dy_U_right
        m_info = m2_info
        choice = 'UpperRight'
        m2_right_KUMIKI_points1, m2_right_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_right_KUMIKI_points1)
        # rs.AddPolyline(m2_right_KUMIKI_points2)

        dx = dx_L_right
        dy = dy_L_right
        m_info = m3_info
        choice = 'LowerRight'
        m3_right_KUMIKI_points1, m3_right_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_right_KUMIKI_points1)
        # rs.AddPolyline(m3_right_KUMIKI_points2)

        # Left side
        dx = dx_U_left
        dy = dy_U_left
        m_info = m2_info
        choice = 'UpperLeft'
        m2_left_KUMIKI_points1, m2_left_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_left_KUMIKI_points1)
        # rs.AddPolyline(m2_left_KUMIKI_points2)

        dx = dx_L_left
        dy = dy_L_left
        m_info = m3_info
        choice = 'LowerLeft'
        m3_left_KUMIKI_points1, m3_left_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_left_KUMIKI_points1)
        # rs.AddPolyline(m3_left_KUMIKI_points2)

    elif SHIGUCHI_name == 'SANMAIKUMI':
        pass
    elif SHIGUCHI_name == 'AIKAKI':
        pass
    elif SHIGUCHI_name == 'HAKO':
        pass
    else:
        sys.exit()

    SHIGUCHI_list =\
    [m2_right_KUMIKI_points1, m2_right_KUMIKI_points2,\
    m3_right_KUMIKI_points1, m3_right_KUMIKI_points2,\
    m2_left_KUMIKI_points1, m2_left_KUMIKI_points2,\
    m3_left_KUMIKI_points1, m3_left_KUMIKI_points2]

    return SHIGUCHI_list

def make_male_m1_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset):
    """Make male m1 shape. (male of female)
    Receives:
        SHIGUCHI_name       str     SHGUCHI name
        m1_info             list    list of m1 information
        m2_info             list    list of m2 information
        m3_info             list    list of m3 information
        m4_info             list    list of m4 information
        offset              num     offset num to fit KUMIKI tight

    Returns:
        m1_male_points_list list    list of m1 male points
                                    [male_upper_m1, male_middle_m1, male_lower_m1]
        SEN_info            list    list of SEN information on m1
    """
    """
    1   Get information from list.
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m = m2_info[2]

    m2_points = m2_info[3]
    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m = m3_info[2]

    m3_points = m3_info[3]
    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]
    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    """
    2   Get base point to make SHIGUCHI points. (dx, dy)
        Get base point to make AIKAKI shape. (ix, iy)
    """
    # SHIGUCHI
    dx_U = m2_p3[0]
    dy_U = m2_p3[1]

    dx_L = m3_p2[0]
    dy_L = m3_p2[1]

    # AIKAKI
    tx = m1_p0[0]
    ty = (m1_p0[1] + m1_p1[1]) / 2

    """
    3   AIKAKI points
    """
    y_k = z_m

    AIAKAKI_offset = 0.2

    # male AIKAKI
    p = (tx, ty)
    p0 = (tx, ty - z_m / 2 + AIAKAKI_offset / 2)
    p1 = (tx + x_m1 / 2, ty - z_m / 2 + AIAKAKI_offset / 2)
    p2 = (tx + x_m1 / 2, ty + z_m / 2 - AIAKAKI_offset / 2)
    p3 = (tx, ty + z_m / 2 - AIAKAKI_offset / 2)
    male_AIKAKI_points = (p0, p1, p2, p3)

    # female AIKAKI
    p = (tx, ty)
    p0 = (tx + x_m1, ty + z_m / 2 - AIAKAKI_offset / 2)
    p1 = (tx + x_m1 / 2, ty + z_m / 2 - AIAKAKI_offset / 2)
    p2 = (tx + x_m1 / 2, ty - z_m / 2 + AIAKAKI_offset / 2)
    p3 = (tx + x_m1, ty - z_m / 2 + AIAKAKI_offset / 2)
    female_AIKAKI_points = (p0, p1, p2, p3)

    """
    4   Call approriate function.
    """
    if SHIGUCHI_name == 'TOME':
        pass

    elif SHIGUCHI_name == 'IRIWA':
        dx = dx_U
        dy = dy_U

        m_info = m2_info
        choice = 'UpperRight'
        m2_KUMIKI_points1, m2_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_KUMIKI_points1)
        # rs.AddPolyline(m2_KUMIKI_points2)

        m2_KUMIKI_points2.reverse()

        dx = dx_L
        dy = dy_L

        m_info = m3_info
        choice = 'LowerRight'
        m3_KUMIKI_points1, m3_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_KUMIKI_points1)
        # rs.AddPolyline(m3_KUMIKI_points2)

    elif SHIGUCHI_name == 'SANMAIKUMI':
        pass

    elif SHIGUCHI_name == 'AIKAKI':
        pass

    elif SHIGUCHI_name == 'HAKO':
        pass

    else:
        sys.exit()

    """
    5   Get SEN information.
    """
    SEN_info = get_m1_m4_SEN_info(tx, ty, m1_info, y_k)

    # upper shape
    upper_shape_upper, upper_shape_lower =\
    m1_make_upper_shape_points_list(tx, ty, m1_info, SEN_info)

    upper_shape_upper_left_row = upper_shape_upper[0]
    upper_shape_upper_right_row = upper_shape_upper[1]

    upper_shape_lower_left_row = upper_shape_lower[0]
    upper_shape_lower_right_row = upper_shape_lower[1]

    # lower shape
    lower_shape_upper, lower_shape_lower =\
    m1_make_lower_shape_points_list(tx, ty, m1_info, SEN_info)

    lower_shape_upper_left_row = lower_shape_upper[0]
    lower_shape_upper_right_row = lower_shape_upper[1]

    lower_shape_lower_left_row = lower_shape_lower[0]
    lower_shape_lower_right_row = lower_shape_lower[1]

    # middle shape
    middle_shape_upper, middle_shape_lower =\
    m1_make_middle_shape_points_list(tx, ty, m1_info, SEN_info)

    middle_shape_upper_left_row = middle_shape_upper[0]
    middle_shape_upper_right_row = middle_shape_upper[1]

    middle_shape_lower_left_row = middle_shape_lower[0]
    middle_shape_lower_right_row = middle_shape_lower[1]

    """
    6   Extend list
    """
    # Upper
    male_upper_m1 = []
    male_upper_m1.append(m1_p0)
    male_upper_m1.extend(upper_shape_lower_left_row)
    male_upper_m1.extend(male_AIKAKI_points)
    male_upper_m1.extend(upper_shape_upper_left_row)
    male_upper_m1.append(m1_p1)

    male_upper_m1.extend(m2_KUMIKI_points2)

    male_upper_m1.append(m1_p2)
    male_upper_m1.extend(upper_shape_upper_right_row)
    male_upper_m1.extend(upper_shape_lower_right_row)
    male_upper_m1.append(m1_p3)

    male_upper_m1.extend(m3_KUMIKI_points2)

    male_upper_m1.append(m1_p0)

    # rs.AddPolyline(male_upper_m1)

    # Middle
    male_middle_m1 = []
    male_middle_m1.append(m1_p0)
    male_middle_m1.extend(middle_shape_lower_left_row)
    male_middle_m1.extend(male_AIKAKI_points)
    male_middle_m1.extend(middle_shape_upper_left_row)
    male_middle_m1.append(m1_p1)

    male_middle_m1.extend(m2_KUMIKI_points2)

    male_middle_m1.append(m1_p2)
    male_middle_m1.extend(middle_shape_upper_right_row)
    male_middle_m1.extend(middle_shape_lower_right_row)
    male_middle_m1.append(m1_p3)

    male_middle_m1.extend(m3_KUMIKI_points2)

    male_middle_m1.append(m1_p0)

    # rs.AddPolyline(male_middle_m1)

    # Lower
    male_lower_m1 = []
    male_lower_m1.append(m1_p0)
    male_lower_m1.extend(lower_shape_lower_left_row)
    male_lower_m1.extend(male_AIKAKI_points)
    male_lower_m1.extend(lower_shape_upper_left_row)
    male_lower_m1.append(m1_p1)

    male_lower_m1.extend(m2_KUMIKI_points2)

    male_lower_m1.append(m1_p2)
    male_lower_m1.extend(lower_shape_upper_right_row)
    male_lower_m1.extend(lower_shape_lower_right_row)
    male_lower_m1.append(m1_p3)

    male_lower_m1.extend(m3_KUMIKI_points2)

    male_lower_m1.append(m1_p0)

    # rs.AddPolyline(male_lower_m1)

    m1_male_points_list = [male_upper_m1, male_middle_m1, male_lower_m1]

    return m1_male_points_list, SEN_info

def make_female_m1_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset):
    """Make female m1 shape. (male of female)
    Receives:
        SHIGUCHI_name       str     SHGUCHI name
        m1_info             list    list of m1 information
        m2_info             list    list of m2 information
        m3_info             list    list of m3 information
        m4_info             list    list of m4 information
        offset              num     offset num to fit KUMIKI tight

    Returns:
        m1_female__points_list      list    list of m1 male points
                                            [female_upper_m1, female_middle_m1, female_lower_m1]
        SEN_info                    list    list of SEN information on m1
    """
    """
    1   Get information from list.
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m = m2_info[2]

    m2_points = m2_info[3]
    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m = m3_info[2]

    m3_points = m3_info[3]
    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]
    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    """
    2   Get base point to make SHIGUCHI points. (dx, dy)
        Get base point to make AIKAKI shape. (ix, iy)
    """
    # SHIGUCHI
    dx_U = m2_p3[0]
    dy_U = m2_p3[1]

    dx_L = m3_p2[0]
    dy_L = m3_p2[1]

    # AIKAKI
    tx = m1_p0[0]
    ty = (m1_p0[1] + m1_p1[1]) / 2

    """
    3   AIKAKI points
    """
    y_k = z_m

    AIAKAKI_offset = 0.2

    # male AIKAKI
    p = (tx, ty)
    p0 = (tx, ty - z_m / 2 + AIAKAKI_offset / 2)
    p1 = (tx + x_m1 / 2, ty - z_m / 2 + AIAKAKI_offset / 2)
    p2 = (tx + x_m1 / 2, ty + z_m / 2 - AIAKAKI_offset / 2)
    p3 = (tx, ty + z_m / 2 - AIAKAKI_offset / 2)
    male_AIKAKI_points = (p0, p1, p2, p3)

    # female AIKAKI
    p = (tx, ty)
    p0 = (tx + x_m1, ty + z_m / 2 - AIAKAKI_offset / 2)
    p1 = (tx + x_m1 / 2, ty + z_m / 2 - AIAKAKI_offset / 2)
    p2 = (tx + x_m1 / 2, ty - z_m / 2 + AIAKAKI_offset / 2)
    p3 = (tx + x_m1, ty - z_m / 2 + AIAKAKI_offset / 2)
    female_AIKAKI_points = (p0, p1, p2, p3)

    """
    4   Call approriate function.
    """
    if SHIGUCHI_name == 'TOME':
        pass

    elif SHIGUCHI_name == 'IRIWA':
        dx = dx_U
        dy = dy_U

        m_info = m2_info
        choice = 'UpperRight'
        m2_KUMIKI_points1, m2_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_KUMIKI_points1)
        # rs.AddPolyline(m2_KUMIKI_points2)

        m2_KUMIKI_points2.reverse()

        dx = dx_L
        dy = dy_L

        m_info = m3_info
        choice = 'LowerRight'
        m3_KUMIKI_points1, m3_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_KUMIKI_points1)
        # rs.AddPolyline(m3_KUMIKI_points2)

    elif SHIGUCHI_name == 'SANMAIKUMI':
        pass

    elif SHIGUCHI_name == 'AIKAKI':
        pass

    elif SHIGUCHI_name == 'HAKO':
        pass

    else:
        sys.exit()

    """
    5   Get SEN information.
    """
    SEN_info = get_m1_m4_SEN_info(tx, ty, m1_info, y_k)

    # upper shape
    upper_shape_upper, upper_shape_lower =\
    m1_make_upper_shape_points_list(tx, ty, m1_info, SEN_info)

    upper_shape_upper_left_row = upper_shape_upper[0]
    upper_shape_upper_right_row = upper_shape_upper[1]

    upper_shape_lower_left_row = upper_shape_lower[0]
    upper_shape_lower_right_row = upper_shape_lower[1]

    # lower shape
    lower_shape_upper, lower_shape_lower =\
    m1_make_lower_shape_points_list(tx, ty, m1_info, SEN_info)

    lower_shape_upper_left_row = lower_shape_upper[0]
    lower_shape_upper_right_row = lower_shape_upper[1]

    lower_shape_lower_left_row = lower_shape_lower[0]
    lower_shape_lower_right_row = lower_shape_lower[1]

    # middle shape
    middle_shape_upper, middle_shape_lower =\
    m1_make_middle_shape_points_list(tx, ty, m1_info, SEN_info)

    middle_shape_upper_left_row = middle_shape_upper[0]
    middle_shape_upper_right_row = middle_shape_upper[1]

    middle_shape_lower_left_row = middle_shape_lower[0]
    middle_shape_lower_right_row = middle_shape_lower[1]

    """
    6   Extend list
    """

    # Upper
    female_upper_m1 = []
    female_upper_m1.append(m1_p0)
    female_upper_m1.extend(upper_shape_lower_left_row)
    female_upper_m1.extend(upper_shape_upper_left_row)
    female_upper_m1.append(m1_p1)

    female_upper_m1.extend(m2_KUMIKI_points2)

    female_upper_m1.append(m1_p2)
    female_upper_m1.extend(upper_shape_upper_right_row)
    female_upper_m1.extend(female_AIKAKI_points)
    female_upper_m1.extend(upper_shape_lower_right_row)
    female_upper_m1.append(m1_p3)

    female_upper_m1.extend(m3_KUMIKI_points2)

    female_upper_m1.append(m1_p0)

    # rs.AddPolyline(female_upper_m1)

    # Middle
    female_middle_m1 = []
    female_middle_m1.append(m1_p0)
    female_middle_m1.extend(middle_shape_lower_left_row)
    female_middle_m1.extend(middle_shape_upper_left_row)
    female_middle_m1.append(m1_p1)

    female_middle_m1.extend(m2_KUMIKI_points2)

    female_middle_m1.append(m1_p2)
    female_middle_m1.extend(middle_shape_upper_right_row)
    female_middle_m1.extend(female_AIKAKI_points)
    female_middle_m1.extend(middle_shape_lower_right_row)
    female_middle_m1.append(m1_p3)

    female_middle_m1.extend(m3_KUMIKI_points2)

    female_middle_m1.append(m1_p0)

    # rs.AddPolyline(female_middle_m1)

    # Lower
    female_lower_m1 = []
    female_lower_m1.append(m1_p0)
    female_lower_m1.extend(lower_shape_lower_left_row)
    female_lower_m1.extend(lower_shape_upper_left_row)
    female_lower_m1.append(m1_p1)

    female_lower_m1.extend(m2_KUMIKI_points2)

    female_lower_m1.append(m1_p2)
    female_lower_m1.extend(lower_shape_upper_right_row)
    female_lower_m1.extend(female_AIKAKI_points)
    female_lower_m1.extend(lower_shape_lower_right_row)
    female_lower_m1.append(m1_p3)

    female_lower_m1.extend(m3_KUMIKI_points2)

    female_lower_m1.append(m1_p0)

    # rs.AddPolyline(female_lower_m1)

    m1_female_points_list = [female_upper_m1, female_middle_m1, female_lower_m1]

    return m1_female_points_list, SEN_info

def make_male_m4_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset):
    """Make male m4 shape. (male or female)
    Receives:
        SHIGUCHI_name       str     SHIGUCHI name
        m1_info             list    list of m1 information
        m2_info             list    list of m2 information
        m3_info             list    list of m3 information
        m4_info             list    list of m4 information
        offset              num     offset num to fit KUMIKI tight

    Returns:
        m4_male_points_list list    list of m4 male points
                                    [male_upper_m4, male_middle_m4, male_lower_m4]
        SEN_info            list    list of SEN information on m4
    """
    """
    1   Get information from list.
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m = m2_info[2]

    m2_points = m2_info[3]
    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m = m3_info[2]

    m3_points = m3_info[3]
    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]
    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    """
    2   Get base point to make SHIGUCHI points. (dx, dy)
        Get base point to make AIKAKI shape. (ix, iy)
    """
    # SHIGUCHI
    dx_U = m2_p0[0]
    dy_U = m2_p0[1]

    dx_L = m3_p1[0]
    dy_L = m3_p1[1]

    # AIKAKI
    tx = m4_p0[0]
    ty = (m4_p0[1] + m4_p1[1]) / 2

    """
    3   AIKAKI points
    """
    y_k = z_m

    AIKAKI_offset = 0.2

    # male AIKAKI
    p = (tx, ty)
    p0 = (tx, ty - z_m / 2 + AIKAKI_offset / 2)
    p1 = (tx - x_m4 / 2, ty - z_m / 2 + AIKAKI_offset / 2)
    p2 = (tx - x_m4 / 2, ty + z_m / 2 - AIKAKI_offset / 2)
    p3 = (tx, ty + z_m / 2 - AIKAKI_offset / 2)
    male_AIKAKI_points = (p0, p1, p2, p3)

    # female AIKAKI
    p = (tx, ty)
    p0 = (tx - x_m4, ty + z_m / 2 - AIKAKI_offset / 2)
    p1 = (tx - x_m4 / 2, ty + z_m / 2 - AIKAKI_offset / 2)
    p2 = (tx - x_m4 / 2, ty - z_m / 2 + AIKAKI_offset / 2)
    p3 = (tx - x_m4, ty - z_m / 2 + AIKAKI_offset / 2)
    female_AIKAKI_points = (p0, p1, p2, p3)

    """
    4   Call approriate function.
    """
    if SHIGUCHI_name == 'TOME':
        pass

    elif SHIGUCHI_name == 'IRIWA':
        dx = dx_U
        dy = dy_U

        m_info = m2_info
        choice = 'UpperLeft'
        m2_KUMIKI_points1, m2_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_KUMIKI_points1)
        # rs.AddPolyline(m2_KUMIKI_points2)

        m2_KUMIKI_points2.reverse()

        dx = dx_L
        dy = dy_L

        m_info = m3_info
        choice = 'LowerLeft'
        m3_KUMIKI_points1, m3_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_KUMIKI_points1)
        # rs.AddPolyline(m3_KUMIKI_points2)

    elif SHIGUCHI_name == 'SANMAIKUMI':
        pass

    elif SHIGUCHI_name == 'AIKAKI':
        pass

    elif SHIGUCHI_name == 'HAKO':
        pass

    else:
        sys.exit()

    """
    5   Get SEN information.
    """
    SEN_info = get_m1_m4_SEN_info(tx, ty, m4_info, y_k)

    # upper shape
    upper_shape_upper, upper_shape_lower =\
    m4_make_upper_shape_points_list(tx, ty, m4_info, SEN_info)

    upper_shape_upper_left_row = upper_shape_upper[0]
    upper_shape_upper_right_row = upper_shape_upper[1]

    upper_shape_lower_left_row = upper_shape_lower[0]
    upper_shape_lower_right_row = upper_shape_lower[1]

    # lower shape
    lower_shape_upper, lower_shape_lower =\
    m4_make_lower_shape_points_list(tx, ty, m4_info, SEN_info)

    lower_shape_upper_left_row = lower_shape_upper[0]
    lower_shape_upper_right_row = lower_shape_upper[1]

    lower_shape_lower_left_row = lower_shape_lower[0]
    lower_shape_lower_right_row = lower_shape_lower[1]

    # middle shape
    middle_shape_upper, middle_shape_lower =\
    m4_make_middle_shape_points_list(tx, ty, m4_info, SEN_info)

    middle_shape_upper_left_row = middle_shape_upper[0]
    middle_shape_upper_right_row = middle_shape_upper[1]

    middle_shape_lower_left_row = middle_shape_lower[0]
    middle_shape_lower_right_row = middle_shape_lower[1]

    """
    6   Extend list
    """
    # Upper
    male_upper_m4 = []
    male_upper_m4.append(m4_p0)
    male_upper_m4.extend(upper_shape_lower_right_row)
    male_upper_m4.extend(male_AIKAKI_points)
    male_upper_m4.extend(upper_shape_upper_right_row)
    male_upper_m4.append(m4_p1)

    male_upper_m4.extend(m2_KUMIKI_points2)

    male_upper_m4.append(m4_p2)
    male_upper_m4.extend(upper_shape_upper_left_row)
    male_upper_m4.extend(upper_shape_lower_left_row)
    male_upper_m4.append(m4_p3)

    male_upper_m4.extend(m3_KUMIKI_points2)

    male_upper_m4.append(m4_p0)

    # rs.AddPolyline(male_upper_m4)

    # Middle
    male_middle_m4 = []
    male_middle_m4.append(m4_p0)
    male_middle_m4.extend(middle_shape_lower_right_row)
    male_middle_m4.extend(male_AIKAKI_points)
    male_middle_m4.extend(middle_shape_upper_right_row)
    male_middle_m4.append(m4_p1)

    male_middle_m4.extend(m2_KUMIKI_points2)

    male_middle_m4.append(m4_p2)
    male_middle_m4.extend(middle_shape_upper_left_row)
    male_middle_m4.extend(middle_shape_lower_left_row)
    male_middle_m4.append(m4_p3)

    male_middle_m4.extend(m3_KUMIKI_points2)

    male_middle_m4.append(m4_p0)

    # rs.AddPolyline(male_middle_m4)

    # Lower
    male_lower_m4 = []
    male_lower_m4.append(m4_p0)
    male_lower_m4.extend(lower_shape_lower_right_row)
    male_lower_m4.extend(male_AIKAKI_points)
    male_lower_m4.extend(lower_shape_upper_right_row)
    male_lower_m4.append(m4_p1)

    male_lower_m4.extend(m2_KUMIKI_points2)

    male_lower_m4.append(m4_p2)
    male_lower_m4.extend(lower_shape_upper_left_row)
    male_lower_m4.extend(lower_shape_lower_left_row)
    male_lower_m4.append(m4_p3)

    male_lower_m4.extend(m3_KUMIKI_points2)

    male_lower_m4.append(m4_p0)

    # rs.AddPolyline(male_lower_m4)


    m4_male_points_list = [male_upper_m4, male_middle_m4, male_lower_m4]

    return m4_male_points_list, SEN_info

def make_female_m4_list(SHIGUCHI_name, m1_info, m2_info, m3_info, m4_info, offset):
    """Make female m4 shape. (male or female)
    Receives:
        SHIGUCHI_name       str     SHIGUCHI name
        m1_info             list    list of m1 information
        m2_info             list    list of m2 information
        m3_info             list    list of m3 information
        m4_info             list    list of m4 information
        offset              num     offset num to fit KUMIKI tight

    Returns:
        m4_female_points_list   list    list of m4 female points
                                        [female_upper_m4, female_middle_m4, female_lower_m4]
        SEN_info                list    list of SEN information on m4
    """
    """
    1   Get information from list.
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]
    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    x_m2 = m2_info[0]
    y_m2 = m2_info[1]
    z_m = m2_info[2]

    m2_points = m2_info[3]
    m2_p0 = m2_points[0]
    m2_p1 = m2_points[1]
    m2_p2 = m2_points[2]
    m2_p3 = m2_points[3]

    x_m3 = m3_info[0]
    y_m3 = m3_info[1]
    z_m = m3_info[2]

    m3_points = m3_info[3]
    m3_p0 = m3_points[0]
    m3_p1 = m3_points[1]
    m3_p2 = m3_points[2]
    m3_p3 = m3_points[3]

    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]
    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    """
    2   Get base point to make SHIGUCHI points. (dx, dy)
        Get base point to make AIKAKI shape. (ix, iy)
    """
    # SHIGUCHI
    dx_U = m2_p0[0]
    dy_U = m2_p0[1]

    dx_L = m3_p1[0]
    dy_L = m3_p1[1]

    # AIKAKI
    tx = m4_p0[0]
    ty = (m4_p0[1] + m4_p1[1]) / 2

    """
    3   AIKAKI points
    """
    y_k = z_m

    AIKAKI_offset = 0.2

    # male AIKAKI
    p = (tx, ty)
    p0 = (tx, ty - z_m / 2 + AIKAKI_offset / 2)
    p1 = (tx - x_m4 / 2, ty - z_m / 2 + AIKAKI_offset / 2)
    p2 = (tx - x_m4 / 2, ty + z_m / 2 - AIKAKI_offset / 2)
    p3 = (tx, ty + z_m / 2 - AIKAKI_offset / 2)
    male_AIKAKI_points = (p0, p1, p2, p3)

    # female AIKAKI
    p = (tx, ty)
    p0 = (tx - x_m4, ty + z_m / 2 - AIKAKI_offset / 2)
    p1 = (tx - x_m4 / 2, ty + z_m / 2 - AIKAKI_offset / 2)
    p2 = (tx - x_m4 / 2, ty - z_m / 2 + AIKAKI_offset / 2)
    p3 = (tx - x_m4, ty - z_m / 2 + AIKAKI_offset / 2)
    female_AIKAKI_points = (p0, p1, p2, p3)

    """
    4   Call approriate function.
    """
    if SHIGUCHI_name == 'TOME':
        pass

    elif SHIGUCHI_name == 'IRIWA':
        dx = dx_U
        dy = dy_U

        m_info = m2_info
        choice = 'UpperLeft'
        m2_KUMIKI_points1, m2_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m2_KUMIKI_points1)
        # rs.AddPolyline(m2_KUMIKI_points2)

        m2_KUMIKI_points2.reverse()

        dx = dx_L
        dy = dy_L

        m_info = m3_info
        choice = 'LowerLeft'
        m3_KUMIKI_points1, m3_KUMIKI_points2 = make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset)
        # rs.AddPolyline(m3_KUMIKI_points1)
        # rs.AddPolyline(m3_KUMIKI_points2)

    elif SHIGUCHI_name == 'SANMAIKUMI':
        pass

    elif SHIGUCHI_name == 'AIKAKI':
        pass

    elif SHIGUCHI_name == 'HAKO':
        pass

    else:
        sys.exit()

    """
    5   Get SEN information.
    """
    SEN_info = get_m1_m4_SEN_info(tx, ty, m4_info, y_k)

    # upper shape
    upper_shape_upper, upper_shape_lower =\
    m4_make_upper_shape_points_list(tx, ty, m4_info, SEN_info)

    upper_shape_upper_left_row = upper_shape_upper[0]
    upper_shape_upper_right_row = upper_shape_upper[1]

    upper_shape_lower_left_row = upper_shape_lower[0]
    upper_shape_lower_right_row = upper_shape_lower[1]

    # lower shape
    lower_shape_upper, lower_shape_lower =\
    m4_make_lower_shape_points_list(tx, ty, m4_info, SEN_info)

    lower_shape_upper_left_row = lower_shape_upper[0]
    lower_shape_upper_right_row = lower_shape_upper[1]

    lower_shape_lower_left_row = lower_shape_lower[0]
    lower_shape_lower_right_row = lower_shape_lower[1]

    # middle shape
    middle_shape_upper, middle_shape_lower =\
    m4_make_middle_shape_points_list(tx, ty, m4_info, SEN_info)

    middle_shape_upper_left_row = middle_shape_upper[0]
    middle_shape_upper_right_row = middle_shape_upper[1]

    middle_shape_lower_left_row = middle_shape_lower[0]
    middle_shape_lower_right_row = middle_shape_lower[1]

    """
    6   Extend list
    """
    # Upper
    female_upper_m4 = []
    female_upper_m4.append(m4_p0)
    female_upper_m4.extend(upper_shape_lower_right_row)
    female_upper_m4.extend(upper_shape_upper_right_row)
    female_upper_m4.append(m4_p1)

    female_upper_m4.extend(m2_KUMIKI_points2)

    female_upper_m4.append(m4_p2)
    female_upper_m4.extend(upper_shape_upper_left_row)
    female_upper_m4.extend(female_AIKAKI_points)
    female_upper_m4.extend(upper_shape_lower_left_row)
    female_upper_m4.append(m4_p3)

    female_upper_m4.extend(m3_KUMIKI_points2)

    female_upper_m4.append(m4_p0)

    # rs.AddPolyline(female_upper_m4)

    # Middle
    female_middle_m4 = []
    female_middle_m4.append(m4_p0)
    female_middle_m4.extend(middle_shape_lower_right_row)
    female_middle_m4.extend(middle_shape_upper_right_row)
    female_middle_m4.append(m4_p1)

    female_middle_m4.extend(m2_KUMIKI_points2)

    female_middle_m4.append(m4_p2)
    female_middle_m4.extend(middle_shape_upper_left_row)
    female_middle_m4.extend(female_AIKAKI_points)
    female_middle_m4.extend(middle_shape_lower_left_row)
    female_middle_m4.append(m4_p3)

    female_middle_m4.extend(m3_KUMIKI_points2)

    female_middle_m4.append(m4_p0)

    # rs.AddPolyline(female_middle_m4)

    # Lower
    female_lower_m4 = []
    female_lower_m4.append(m4_p0)
    female_lower_m4.extend(lower_shape_lower_right_row)
    female_lower_m4.extend(lower_shape_upper_right_row)
    female_lower_m4.append(m4_p1)

    female_lower_m4.extend(m2_KUMIKI_points2)

    female_lower_m4.append(m4_p2)
    female_lower_m4.extend(lower_shape_upper_left_row)
    female_lower_m4.extend(female_AIKAKI_points)
    female_lower_m4.extend(lower_shape_lower_left_row)
    female_lower_m4.append(m4_p3)

    female_lower_m4.extend(m3_KUMIKI_points2)

    female_lower_m4.append(m4_p0)

    # rs.AddPolyline(female_lower_m4)


    m4_female_points_list = [female_upper_m4, female_middle_m4, female_lower_m4]

    return m4_female_points_list, SEN_info

# Make crv----------------------------------------------------------------------
def make_m1_male_crv(m1_male_points_list):
    """Make m1 male crvs.
    Receives:
        m1_male_points_list        list     list of male m1 points list.
                                            [male_upper_m1, male_middle_m1, male_lower_m1]
    Returns:
        m1_male_crvs        list    list of m1_male crvs
        m1_male_upper_crv   guid    m1_male_upper crv
        m1_male_middle_crv  guid    m1_male_middle_crv
        m1_male_lower_crv   guid    m1_male_lower_crv
    """
    """
    1   Get information from list.
    """
    male_upper_m1 = m1_male_points_list[0]
    male_middle_m1 = m1_male_points_list[1]
    male_lower_m1 = m1_male_points_list[2]

    """
    2   Add Polyline.
    """
    m1_male_upper_crv = rs.AddPolyline(male_upper_m1)
    m1_male_middle_crv = rs.AddPolyline(male_middle_m1)
    m1_male_lower_crv = rs.AddPolyline(male_lower_m1)

    m1_male_crvs = [m1_male_upper_crv, m1_male_middle_crv, m1_male_lower_crv]

    return m1_male_crvs

def make_m1_female_crv(m1_female_points_list):
    """Make m1 female crvs.
    Receives:
        m1_female_points_list       list    list of female m1 points list.
                                            [female_upper_m1, female_middle_m1, female_lower_m1]
    Returns:
        m1_female_crvs              list    list of m1_female crvs
        m1_female_upper_crv         guid    m1_female_upper crv
        m1_female_middle_crv        guid    m1_female_middle_crv
        m1_female_lower_crv         guid    m1_female_lower_crv
    """
    """
    1   Get information from list.
    """
    female_upper_m1 = m1_female_points_list[0]
    female_middle_m1 = m1_female_points_list[1]
    female_lower_m1 = m1_female_points_list[2]

    """
    2   Add Polyline.
    """
    m1_female_upper_crv = rs.AddPolyline(female_upper_m1)
    m1_female_middle_crv = rs.AddPolyline(female_middle_m1)
    m1_female_lower_crv = rs.AddPolyline(female_lower_m1)

    m1_female_crvs = [m1_female_upper_crv, m1_female_middle_crv, m1_female_lower_crv]

    return m1_female_crvs

def make_m2_crv(TSUGITE_list, SHIGUCHI_list):
    """Make m2 crv by extending TSUGITE and SHIGUCHI list.
    Receives:
        TSUGITE_list    list    list of TSUGITE_list
                                [m2_left_list, m2_right_list, m3_left_list, m3_right_list]
        SHIGUCHI_list   list    list of SHIGUCHI_list
                                [m2_KUMIKI_points1, m2_KUMIKI_points2, m3_KUMIKI_points1, m3_KUMIKI_points2]

        left_crvs               [left_upper_crv, left_middle_crv, left_lower_crv]
        right_crvs              [right_upper_crv, right_middle_crv, right_lower_crv]

    Returns:
        m2_left_crvs    list    list of material2 left crv
        m2_right_crvs   list    list of material2 right crv
    """
    """
    1   Get information from TSUGITE_list and SHIGUCHI_list.
    """
    # TSUGITE
    # Left----------------------------------------------------------------------
    # material2
    m2_left_list = TSUGITE_list[0]
    m2_left_upper = m2_left_list[0]
    m2_left_middle = m2_left_list[1]
    m2_left_lower = m2_left_list[2]

    # SHIGUCHI
    m2_KUMIKI_points1 = SHIGUCHI_list[4]
    m2_KUMIKI_points2 = SHIGUCHI_list[5]

    m2_KUMIKI_points1.reverse()

    m2_left_upper.extend(m2_KUMIKI_points1)
    m2_left_upper.append(m2_left_upper[0])
    m2_left_upper_crv = rs.AddPolyline(m2_left_upper)

    m2_left_middle.extend(m2_KUMIKI_points1)
    m2_left_middle.append(m2_left_middle[0])
    m2_left_middle_crv = rs.AddPolyline(m2_left_middle)

    m2_left_lower.extend(m2_KUMIKI_points1)
    m2_left_lower.append(m2_left_lower[0])
    m2_left_lower_crv = rs.AddPolyline(m2_left_lower)

    m2_left_crvs = [m2_left_upper_crv, m2_left_middle_crv, m2_left_lower_crv]

    # Right---------------------------------------------------------------------
    m2_right_list = TSUGITE_list[1]
    m2_right_upper = m2_right_list[0]
    m2_right_middle = m2_right_list[1]
    m2_right_lower = m2_right_list[2]

    # SHIGUCHI
    m2_KUMIKI_points1 = SHIGUCHI_list[0]
    m2_KUMIKI_points2 = SHIGUCHI_list[1]

    # Extend
    # material2
    m2_right_upper.reverse()
    m2_right_middle.reverse()
    m2_right_lower.reverse()

    # m2_KUMIKI_points1.reverse()

    m2_right_upper.extend(m2_KUMIKI_points1)
    m2_right_upper.append(m2_right_upper[0])
    m2_right_upper_crv = rs.AddPolyline(m2_right_upper)

    m2_right_middle.extend(m2_KUMIKI_points1)
    m2_right_middle.append(m2_right_middle[0])
    m2_right_middle_crv = rs.AddPolyline(m2_right_middle)

    m2_right_lower.extend(m2_KUMIKI_points1)
    m2_right_lower.append(m2_right_lower[0])
    m2_right_lower_crv = rs.AddPolyline(m2_right_lower)

    m2_right_crvs = [m2_right_upper_crv, m2_right_middle_crv, m2_right_lower_crv]

    return m2_left_crvs, m2_right_crvs

def make_m3_crv(TSUGITE_list, SHIGUCHI_list):
    """Make m3 crv by extending TSUGITE and SHIGUCHI list.
    Receives:
        TSUGITE_list    list    list of TSUGITE_list
                                [m2_left_list, m2_right_list, m3_left_list, m3_right_list]
        SHIGUCHI_list   list    list of SHIGUCHI_list
                                [m2_KUMIKI_points1, m2_KUMIKI_points2, m3_KUMIKI_points1, m3_KUMIKI_points2]

        left_crvs               [left_upper_crv, left_middle_crv, left_lower_crv]
        right_crvs              [right_upper_crv, right_middle_crv, right_lower_crv]

    Returns:
        m3_left_crvs    list    list of material3 left crv
        m3_right_crvs   list    list of material3 right crv
    """
    """
    1   Get information from TSUGITE_list and SHIGUCHI_list.
    """
    # TSUGITE
    # Left----------------------------------------------------------------------
    # material2
    m3_left_list = TSUGITE_list[2]
    m3_left_upper = m3_left_list[0]
    m3_left_middle = m3_left_list[1]
    m3_left_lower = m3_left_list[2]

    # SHIGUCHI
    m3_KUMIKI_points1 = SHIGUCHI_list[6]
    m3_KUMIKI_points2 = SHIGUCHI_list[7]

    # m3_KUMIKI_points1.reverse()

    m3_left_upper.extend(m3_KUMIKI_points1)
    m3_left_upper.append(m3_left_upper[0])
    m3_left_upper_crv = rs.AddPolyline(m3_left_upper)

    m3_left_middle.extend(m3_KUMIKI_points1)
    m3_left_middle.append(m3_left_middle[0])
    m3_left_middle_crv = rs.AddPolyline(m3_left_middle)

    m3_left_lower.extend(m3_KUMIKI_points1)
    m3_left_lower.append(m3_left_lower[0])
    m3_left_lower_crv = rs.AddPolyline(m3_left_lower)

    m3_left_crvs = [m3_left_upper_crv, m3_left_middle_crv, m3_left_lower_crv]

    # Right---------------------------------------------------------------------
    # material3
    m3_right_list = TSUGITE_list[3]
    m3_right_upper = m3_right_list[0]
    m3_right_middle = m3_right_list[1]
    m3_right_lower = m3_right_list[2]

    # SHIGUCHI
    m3_KUMIKI_points1 = SHIGUCHI_list[2]
    m3_KUMIKI_points2 = SHIGUCHI_list[3]

    # Extend
    # material3
    m3_right_upper.extend(m3_KUMIKI_points1)
    m3_right_upper.append(m3_right_upper[0])
    m3_right_upper_crv = rs.AddPolyline(m3_right_upper)

    m3_right_middle.extend(m3_KUMIKI_points1)
    m3_right_middle.append(m3_right_middle[0])
    m3_right_middle_crv = rs.AddPolyline(m3_right_middle)

    m3_right_lower.extend(m3_KUMIKI_points1)
    m3_right_lower.append(m3_right_lower[0])
    m3_right_lower_crv = rs.AddPolyline(m3_right_lower)

    m3_right_crvs = [m3_right_upper_crv, m3_right_middle_crv, m3_right_lower_crv]

    return m3_left_crvs, m3_right_crvs

def make_m4_male_crv(m4_male_points_list):
    """Make m4 male crvs.
    Receives:
        m4_male_points_list        list     list of male m4 points list.
                                            [male_upper_m4, male_middle_m4, male_lower_m4]
    Returns:
        m4_male_crvs        list    list of m4_male crvs
        m4_male_upper_crv   guid    m4_male_upper crv
        m4_male_middle_crv  guid    m4_male_middle_crv
        m4_male_lower_crv   guid    m4_male_lower_crv
    """
    """
    1   Get information from list.
    """
    male_upper_m4 = m4_male_points_list[0]
    male_middle_m4 = m4_male_points_list[1]
    male_lower_m4 = m4_male_points_list[2]

    """
    2   Add Polyline.
    """
    m4_male_upper_crv = rs.AddPolyline(male_upper_m4)
    m4_male_middle_crv = rs.AddPolyline(male_middle_m4)
    m4_male_lower_crv = rs.AddPolyline(male_lower_m4)

    m4_male_crvs = [m4_male_upper_crv, m4_male_middle_crv, m4_male_lower_crv]

    return m4_male_crvs

def make_m4_female_crv(m4_female_points_list):
    """Make m4 female crvs.
    Receives:
        m4_female_points_list       list    list of female m4 points list.
                                            [female_upper_m4, female_middle_m4, female_lower_m4]
    Returns:
        m4_female_crvs              list    list of m4_female crvs
        m4_female_upper_crv         guid    m4_female_upper crv
        m4_female_middle_crv        guid    m4_female_middle_crv
        m4_female_lower_crv         guid    m4_female_lower_crv
    """
    """
    1   Get information from list.
    """
    female_upper_m4 = m4_female_points_list[0]
    female_middle_m4 = m4_female_points_list[1]
    female_lower_m4 = m4_female_points_list[2]

    """
    2   Add Polyline.
    """
    m4_female_upper_crv = rs.AddPolyline(female_upper_m4)
    m4_female_middle_crv = rs.AddPolyline(female_middle_m4)
    m4_female_lower_crv = rs.AddPolyline(female_lower_m4)

    m4_female_crvs = [m4_female_upper_crv, m4_female_middle_crv, m4_female_lower_crv]

    return m4_female_crvs

# KUMIKI FUNCTIONs--------------------------------------------------------------
# TSUGITE-----------------------------------------------------------------------
def make_ARI_list(dx, dy, m_info, offset):
    """Make ARI points list.
    Receives:
        dx, dy      pt      base point to make TSUGITE
        m_info      list    list of material information
        offset      num     offset num to fit KUMIKI tight

    Returns:
        left_list   list
        right_list  list
        SEN_info    list    list of SEN information of material
    """
    """
    1   Get information from m_info.
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    m_points = m_info[3]

    m_p0 = m_points[0]
    m_p1 = m_points[1]
    m_p2 = m_points[2]
    m_p3 = m_points[3]

    """
    2   Get points of ARI.
    """
    x_k = y_m * 2 / 3               # NOTE: fixed number

    # KUMIKI_points_left    reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 3 - offset)
    p3 = (dx + x_k, dy + y_m / 4 - offset)
    p2 = (dx + x_k, dy + 3 * y_m / 4 + offset)
    p1 = (dx, dy + 2 * y_m / 3 + offset)
    p0 = (dx, dy + y_m)

    KUMIKI_points_left = [p0, p1, p2, p3, p4, p5]

    # KUMIKI_points_right   not reflect offset
    p5 = (dx, dy)
    p4 = (dx, dy + y_m / 3)
    p3 = (dx + x_k, dy + y_m / 4)
    p2 = (dx + x_k, dy + 3 * y_m / 4)
    p1 = (dx, dy + 2 * y_m / 3)
    p0 = (dx, dy + y_m)

    KUMIKI_points_right = [p0, p1, p2, p3, p4, p5]

    """
    3   Get SEN information.
    """
    SEN_info = get_m2_m3_SEN_info(dx, dy, m_info, x_k)

    # upper shape
    upper_shape_left, upper_shape_right =\
    m2_m3_make_upper_shape_points_list(dx, dy, m_info, SEN_info)

    upper_shape_left_upper_row = upper_shape_left[0]
    upper_shape_left_lower_row = upper_shape_left[1]

    upper_shape_right_upper_row = upper_shape_right[0]
    upper_shape_right_lower_row = upper_shape_right[1]

    # lower shape
    lower_shape_left, lower_shape_right =\
    m2_m3_make_lower_shape_points_list(dx, dy, m_info, SEN_info)

    lower_shape_left_upper_row = lower_shape_left[0]
    lower_shape_left_lower_row = lower_shape_left[1]

    lower_shape_right_upper_row = lower_shape_right[0]
    lower_shape_right_lower_row = lower_shape_right[1]

    # middle shape
    middle_shape_left, middle_shape_right =\
    m2_m3_make_middle_shape_points_list(dx, dy, m_info, SEN_info)

    middle_shape_left_upper_row = middle_shape_left[0]
    middle_shape_left_lower_row = middle_shape_left[1]

    middle_shape_right_upper_row = middle_shape_right[0]
    middle_shape_right_lower_row = middle_shape_right[1]

    """
    4   Make ARI lists
    """
    # Leftside
    # Upper
    left_upper = []
    left_upper.append(m_p1)
    left_upper.extend(upper_shape_left_upper_row)

    left_upper.extend(KUMIKI_points_left)
    left_upper.extend(upper_shape_left_lower_row)
    left_upper.append(m_p0)

    # left_upper_crv = rs.AddPolyline(left_upper)

    # Middle
    left_middle = []
    left_middle.append(m_p1)
    left_middle.extend(middle_shape_left_upper_row)

    left_middle.extend(KUMIKI_points_left)
    left_middle.extend(middle_shape_left_lower_row)
    left_middle.append(m_p0)

    # left_middle_crv = rs.AddPolyline(left_middle)

    # Lower
    left_lower = []
    left_lower.append(m_p1)
    left_lower.extend(lower_shape_left_upper_row)

    left_lower.extend(KUMIKI_points_left)
    left_lower.extend(lower_shape_left_lower_row)
    left_lower.append(m_p0)

    # left_lower_crv = rs.AddPolyline(left_lower)

    # left_crvs = [left_upper_crv, left_middle_crv, left_lower_crv]

    left_list = [left_upper, left_middle, left_lower]

    # Rightside
    # Upper
    right_upper = []
    right_upper.append(m_p2)
    right_upper.extend(upper_shape_right_upper_row)

    right_upper.extend(KUMIKI_points_right)
    right_upper.extend(upper_shape_right_lower_row)
    right_upper.append(m_p3)

    # right_upper_crv = rs.AddPolyline(right_upper)

    # Middle
    right_middle = []
    right_middle.append(m_p2)
    right_middle.extend(middle_shape_right_upper_row)

    right_middle.extend(KUMIKI_points_right)
    right_middle.extend(middle_shape_right_lower_row)
    right_middle.append(m_p3)

    # right_middle_crv = rs.AddPolyline(right_middle)

    # Lower
    right_lower = []
    right_lower.append(m_p2)
    right_lower.extend(lower_shape_right_upper_row)

    right_lower.extend(KUMIKI_points_right)
    right_lower.extend(lower_shape_right_lower_row)
    right_lower.append(m_p3)

    # right_lower_crv = rs.AddPolyline(right_lower)

    # right_crvs = [right_upper_crv, right_middle_crv, right_lower_crv]

    right_list = [right_upper, right_middle, right_lower]

    return left_list, right_list, SEN_info

# SHIGUCHI----------------------------------------------------------------------
def make_IRIWA_KUMIKI_points(dx, dy, m_info, choice, offset):
    """Make IRIWA KUMIKI points to extend TSUGITE right list.
    Receives:
        dx, dy      pt      base point to make KUMIKI.
        m_info      list    list of material information.
        choice      str     direction to make KUMIKI points.
                            'UpperRight', 'LowerRight', 'UpperLeft', 'LowerLeft'
    Returns:
        IRIWA_KUMIKI_points1    list    list of IRIWA KUMIKI points
        IRIWA_KUMIKI_points2    list    list of IRIWA KUMIKI points
    """
    """
    1   Get information from list.
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    """
    2   KUMIKI_points
    """
    x_k = y_m
    y_k = x_k

    if choice == 'UpperRight':
        pass
    elif choice == 'LowerRight':
        y_k = -y_k
    elif choice == 'UpperLeft':
        x_k = -x_k
    elif choice == 'LowerLeft':
        x_k = -x_k
        y_k = -y_k
    else:
        sys.exit()

    p5 = (dx, dy)
    p4 = (dx, dy + 2 * y_k / 5)
    p3 = (dx + 2 * x_k / 5, dy + 2 * y_k / 5)
    p2 = (dx + 2 * x_k / 5, dy)
    p1 = (dx + x_k, dy)
    p0 = (dx + x_k, dy + y_k )

    IRIWA_KUMIKI_points1 = [p0, p1, p2, p3, p4, p5]

    if choice == 'UpperRight':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + 2 * y_k / 5)
        p3 = (dx + 2 * x_k / 5 + 2 * offset, dy + 2 * y_k / 5)
        p2 = (dx + 2 * x_k / 5 + 2 * offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        IRIWA_KUMIKI_points2 = [p2, p3, p4, p5]

    elif choice == 'LowerRight':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + 2 * y_k / 5)
        p3 = (dx + 2 * x_k / 5 + 2 * offset, dy + 2 * y_k / 5)
        p2 = (dx + 2 * x_k / 5 + 2 * offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        IRIWA_KUMIKI_points2 = [p2, p3, p4, p5]

    elif choice == 'UpperLeft':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + 2 * y_k / 5)
        p3 = (dx + 2 * x_k / 5 - 2 * offset, dy + 2 * y_k / 5)
        p2 = (dx + 2 * x_k / 5 - 2 * offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        IRIWA_KUMIKI_points2 = [p2, p3, p4, p5]

    elif choice == 'LowerLeft':
        # KUMIKI_points2
        p5 = (dx, dy)
        p4 = (dx, dy + 2 * y_k / 5)
        p3 = (dx + 2 * x_k / 5 - 2 * offset, dy + 2 * y_k / 5)
        p2 = (dx + 2 * x_k / 5 - 2 * offset, dy)
        p1 = (dx + x_k, dy)
        p0 = (dx + x_k, dy + y_k )

        IRIWA_KUMIKI_points2 = [p2, p3, p4, p5]

    else:
        sys.exit()


    return IRIWA_KUMIKI_points1, IRIWA_KUMIKI_points2

# ------------------------------------------------------------------------------
# SEN FUNCTIONs-----------------------------------------------------------------
def get_m1_m4_SEN_info(tx, ty, m1_info, y_k):
    """Get SEN information of m1.
    Receives:
        tx, ty          pt      base point to make AIKAKI
        m1_info         list    list of m1 information
        y_k

    Returns:
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 u_n, l_n, set, u_offset, l_offset]

        w_sen           int     width of sen
        n_w_sen         int     narrow part width of sen
        h_sen           int     height of sen
        t_sen           int     thickness of sen

        u_n             int     the number of sen on y side of upper material
        l_n             int     the number of sen on y side of lower material
        set             int     the number of setback from edge line of material to line up SEN
        u_offset        int     the number of offst between each SENs
        l_offset        int     the number of offst between each SENs
    """
    """
    1   Get information from m1_info
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]
    t_m = z_m / 3

    t_sen = m1_info[4]

    m1_points = m1_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    b_p = (tx, ty)

    u_distance = rs.Distance(m1_p3, b_p) - y_k / 2
    l_distance = rs.Distance(m1_p0, b_p) - y_k / 2

    """
    2   Get SEN information
    """
    # Automatically fixed---------------------------------------------------
    # t_sen = rs.GetReal("Put Int(mm): Thickness of material to cut SEN.", t_m / 2, None, None)
    w_sen = t_sen
    n_w_sen = w_sen / 2
    h_sen = z_m

    u_max_n = u_distance / (2 * w_sen - n_w_sen)       # NOTE: divide max_n by 2 to controll "n"
    u_max_n = int(u_max_n)

    u_n = u_max_n / 4
    u_n = int(u_n)

    l_max_n = l_distance / (2 * w_sen - n_w_sen)      # NOTE: divide max_n by 2 to controll "n"
    l_max_n = int(l_max_n)

    l_n = l_max_n / 4
    l_n = int(l_n)


    set = 20
    u_offset = (u_distance - 2 * set) / (u_n - 1)
    l_offset = (l_distance - 2 * set) / (l_n - 1)

    SEN_info = [w_sen, n_w_sen, h_sen, t_sen, u_n, l_n, set, u_offset, l_offset]

    return SEN_info

def get_m2_m3_SEN_info(dx, dy, m_info, x_k):
    """Get SEN information of m2 or m3.
    Receices:
        dx, dy          pt      base point to make TSUGITE
        m_info          list    list of material information (m2_info or m3_info)
        x_k             int     x length of KUMIKI

    Returns:
        SEN_info        list    list of SEN information
                                [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]

        w_sen           int     width of sen
        n_w_sen         int     narrow part width of sen
        h_sen           int     height of sen
        t_sen           int     thickness of sen

        l_n             int     the number of sen on x side of material
        r_n             int     the number of sen on x side of material
        set             int     the number of setback from edge line of material to line up SEN
        l_offset        int     the number of offst between each SENs
        r_offset        int     the number of offst between each SENs
    """
    """
    1   Get information from m_info
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]
    t_m = z_m / 3

    t_sen = m_info[4]

    m_points = m_info[3]

    m_p0 = m_points[0]
    m_p1 = m_points[1]
    m_p2 = m_points[2]
    m_p3 = m_points[3]

    b_p = (dx, dy)

    l_distance = rs.Distance(m_p0, b_p)
    r_distance = rs.Distance(m_p3, b_p) - x_k

    """
    2   Get SEN information
    """
    # Automatically fixed---------------------------------------------------
    w_sen = t_sen
    n_w_sen = w_sen / 2
    h_sen = z_m

    l_max_n = l_distance / (2 * w_sen - n_w_sen)       # NOTE: divide max_n by 2 to controll "n"
    l_max_n = int(l_max_n)

    l_n = l_max_n / 6
    l_n = int(l_n)

    r_max_n = r_distance / (2 * w_sen - n_w_sen)       # NOTE: divide max_n by 2 to controll "n"
    r_max_n = int(r_max_n)

    r_n = r_max_n / 6
    r_n = int(r_n)

    set = 20
    l_offset = (l_distance - 2 * set) / (l_n - 1)
    r_offset = (r_distance - 2 * set) / (r_n - 1)

    SEN_info = [w_sen, n_w_sen, h_sen, t_sen, l_n, r_n, set, l_offset, r_offset]

    return SEN_info

# SEN shape---------------------------------------------------------------------
# upper shape-------------------------------------------------------------------
def X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of X direction upper shapes points.
    Receives:
        (ix, iy)        point   Base point of shape.
            w_sen       int     x length of sen
            n_w_sen     int     narrow part x length of sen
            t_sen       int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2, iy - t_sen)
    p2 = (ix - w_sen + n_w_sen / 2, iy)
    p3 = (ix - n_w_sen / 2, iy)
    p4 = (ix - n_w_sen / 2, iy + t_sen)
    p5 = (ix + w_sen - n_w_sen / 2, iy + t_sen)
    p6 = (ix + w_sen - n_w_sen / 2, iy)
    p7 = (ix + n_w_sen / 2, iy)
    p8 = (ix + n_w_sen / 2, iy - t_sen)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction upper shapes points.
    Receives:
        (ix, iy)        point   Base point of shape.
            w_sen       int     x length of sen
            n_w_sen     int     narrow part x length of sen
            t_sen       int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - t_sen, iy - w_sen + n_w_sen / 2)
    p2 = (ix, iy - w_sen + n_w_sen / 2)
    p3 = (ix, iy - n_w_sen / 2)
    p4 = (ix + t_sen, iy - n_w_sen / 2)
    p5 = (ix + t_sen, iy + w_sen - n_w_sen / 2)
    p6 = (ix, iy + w_sen - n_w_sen / 2)
    p7 = (ix, iy + n_w_sen / 2)
    p8 = (ix - t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def m1_make_upper_shape_points_list(tx, ty, m1_info, SEN_info):
    """Make m1 upper shape points list.
    Receives:
        tx, ty      pt      base point to make AIKAKI
        m1_info     list    list of material1 information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 u_n, l_n, set, u_offset, l_offset]
    Returns:
        upper_shape_upper   list    upper side upper_shape
                                    [upper_shape_upper_left_row, upper_shape_upper_right_row]
        upper_shape_lower   list    lower side upper_shape
                                    [upper_shape_lower_left_row, upper_shape_lower_right_row]
    """
    """
    1   Get information from m1_info & SEN_info
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        upper_shape_upper_left_row      list
        upper_shape_upper_right_row     list

        upper_shape_lower_left_row      list
        upper_shape_lower_right_row     list
    """
    # upper side
    upper_shape_upper_left_row = []
    upper_shape_upper_right_row = []

    for i in range(u_n):
        # left row
        ix = tx + t_sen
        iy = ty + (i * u_offset + set) + 10 # have to "+" something now its magic number

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        upper_shape_upper_left_row.extend((left_points))

    for i in range(u_n - 1, -1, -1):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        upper_shape_upper_right_row.extend(right_points)

    # lower side
    upper_shape_lower_left_row = []
    upper_shape_lower_right_row = []

    for i in range(l_n -1, -1, -1):
        # left row
        ix = tx + t_sen
        iy = ty - (i * l_offset + set) - 10 # have to "-" something now its magic number

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        upper_shape_lower_left_row.extend((left_points))

    for i in range(l_n):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty -  (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        upper_shape_lower_right_row.extend(right_points)

    upper_shape_upper = [upper_shape_upper_left_row, upper_shape_upper_right_row]
    upper_shape_lower = [upper_shape_lower_left_row, upper_shape_lower_right_row]

    return upper_shape_upper, upper_shape_lower

def m2_m3_make_upper_shape_points_list(dx, dy, m_info, SEN_info):
    """Make m2 or m3 upper shape points list.
    Receives:
        dx, dy      pt      base point to make TSUGITE
        m_info      list    list of material information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]
    Returns:
        upper_shape_left    list        leftside upper_shape
                                        [upper_shape_left_upper_row, upper_shape_left_lower_row]
        upper_shape_right   list        rightside upper_shape
                                        [upper_shape_right_upper_row, upper_shape_right_lower_row]
    """
    """
    1   Get information from m_info & SEN_info.
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    m_points = m_info[3]

    m_p0 = m_points[0]
    m_p1 = m_points[1]
    m_p2 = m_points[2]
    m_p3 = m_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        upper_shape_left_upper_row      list
        upper_shape_left_lower_row      list

        upper_shape_right_upper_row     list
        upper_shape_right_lower_row     list
    """
    # Leftside
    upper_shape_left_upper_row = []
    upper_shape_left_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        upper_shape_left_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        upper_shape_left_lower_row.extend(lower_points)

    # Rightside
    upper_shape_right_upper_row = []
    upper_shape_right_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        upper_shape_right_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        upper_shape_right_lower_row.extend(lower_points)

    upper_shape_left = [upper_shape_left_upper_row, upper_shape_left_lower_row]
    upper_shape_right = [upper_shape_right_upper_row, upper_shape_right_lower_row]

    return upper_shape_left, upper_shape_right

def m4_make_upper_shape_points_list(tx, ty, m4_info, SEN_info):
    """Make m4 upper shape points list.
    Receives:
        tx, ty              pt      base point to make AIKAKI
        m4_info             list    list of material4 information
        SEN_info            list    list of SEN information
                                    [w_sen, n_w_sen, h_sen, t_sen,
                                         u_n, l_n, set, u_offset, l_offset]
    Returns:
        upper_shape_upper   list    upper side upper_shape
        upper_shape_lower   list    lower side upper_shape
    """
    """
    1   Get information from m4_info & SEN_info
    """
    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]

    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        upper_shape_upper_left_row  list
        upper_shape_upper_right_row  list

        upper_shape_lower_left_row  list
        upper_shape_lower_right_row  list
    """
    # upper side
    upper_shape_upper_left_row = []
    upper_shape_upper_right_row = []

    for i in range(u_n - 1, -1, -1):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        upper_shape_upper_left_row.extend((left_points))

    for i in range(u_n):
        # right row
        ix = tx - t_sen
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        upper_shape_upper_right_row.extend(right_points)

    # lower side
    upper_shape_lower_left_row = []
    upper_shape_lower_right_row = []

    for i in range(l_n):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        upper_shape_lower_left_row.extend((left_points))

    for i in range(l_n - 1, -1, -1):
        # right row
        ix = tx - t_sen
        iy = ty -  (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_upper_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        upper_shape_lower_right_row.extend(right_points)

    upper_shape_upper = [upper_shape_upper_left_row, upper_shape_upper_right_row]
    upper_shape_lower = [upper_shape_lower_left_row, upper_shape_lower_right_row]

    return upper_shape_upper, upper_shape_lower

# lower shape-------------------------------------------------------------------
def X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of X direction lower shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2, iy + t_sen)
    p2 = (ix - w_sen + n_w_sen / 2, iy)
    p3 = (ix - n_w_sen / 2, iy)
    p4 = (ix - n_w_sen / 2, iy - t_sen)
    p5 = (ix + w_sen - n_w_sen / 2, iy - t_sen)
    p6 = (ix + w_sen - n_w_sen / 2, iy)
    p7 = (ix + n_w_sen / 2, iy)
    p8 = (ix + n_w_sen / 2, iy + t_sen)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction lower shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix + t_sen, iy - w_sen + n_w_sen / 2)
    p2 = (ix, iy - w_sen + n_w_sen / 2)
    p3 = (ix, iy - n_w_sen / 2)
    p4 = (ix - t_sen, iy - n_w_sen / 2)
    p5 = (ix - t_sen, iy + w_sen - n_w_sen / 2)
    p6 = (ix, iy + w_sen - n_w_sen / 2)
    p7 = (ix, iy + n_w_sen / 2)
    p8 = (ix + t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def m1_make_lower_shape_points_list(tx, ty, m1_info, SEN_info):
    """Make m1 lower shape points list.
    Receives:
        ix, iy      pt      base point to make AIKAKI
        m1_info     list    list of material1 information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 u_n, l_n, set, u_offset, l_offset]
    Returns:
        lower_shape_upper   list    upper side lower_shape
                                    [lower_shape_upper_left_row, lower_shape_upper_right_row]
        lower_shape_lower   list    lower side lower_shape
                                    [lower_shape_lower_left_row, lower_shape_lower_right_row]
    """
    """
    1   Get information from m1_info & SEN_info
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        lower_shape_upper_left_row      list
        lower_shape_upper_right_row     list

        lower_shape_lower_left_row      list
        lower_shape_lower_right_row     list
    """
    # upper side
    lower_shape_upper_left_row = []
    lower_shape_upper_right_row = []

    for i in range(u_n):
        # left row
        ix = tx + t_sen
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        lower_shape_upper_left_row.extend((left_points))

    for i in range(u_n - 1, -1, -1):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        lower_shape_upper_right_row.extend(right_points)

    # lower side
    lower_shape_lower_left_row = []
    lower_shape_lower_right_row = []

    for i in range(l_n - 1, -1, -1):
        # left row
        ix = tx + t_sen
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        lower_shape_lower_left_row.extend((left_points))

    for i in range(l_n):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        lower_shape_lower_right_row.extend(right_points)

    lower_shape_upper = [lower_shape_upper_left_row, lower_shape_upper_right_row]
    lower_shape_lower = [lower_shape_lower_left_row, lower_shape_lower_right_row]

    return lower_shape_upper, lower_shape_lower

def m2_m3_make_lower_shape_points_list(dx, dy, m_info, SEN_info):
    """Make lower shape points list.
    Receives:
        dx, dy      pt      base point to make TSUGITE
        m_info      list    list of material information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]
    Returns:
        lower_shape_left    list        leftside lower_shape
                                        [lower_shape_left_upper_row, lower_shape_left_lower_row]
        lower_shape_right   list        rightside lower_shape
                                        [lower_shape_right_upper_row, lower_shape_right_lower_row]
    """
    """
    1   Get information from m_info & SEN_info.
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    m_points = m_info[3]

    m_p0 = m_points[0]
    m_p1 = m_points[1]
    m_p2 = m_points[2]
    m_p3 = m_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        lower_shape_left_upper_row      list
        lower_shape_left_lower_row      list

        lower_shape_right_upper_row     list
        lower_shape_right_lower_row     list
    """
    # Leftside
    lower_shape_left_upper_row = []
    lower_shape_left_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        lower_shape_left_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        lower_shape_left_lower_row.extend(lower_points)

    # Rightside
    lower_shape_right_upper_row = []
    lower_shape_right_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p8, p7, p6, p5, p4, p3, p2, p1]
        lower_shape_right_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen + dy
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = X_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p4, p3, p2, p1, p8, p7, p6, p5]
        lower_shape_right_lower_row.extend(lower_points)

    lower_shape_left = [lower_shape_left_upper_row, lower_shape_left_lower_row]
    lower_shape_right = [lower_shape_right_upper_row, lower_shape_right_lower_row]

    return lower_shape_left, lower_shape_right

def m4_make_lower_shape_points_list(tx, ty, m4_info, SEN_info):
    """Make m4 lower shape points list.
    Receives:
        tx, ty              pt      base point to make AIKAKI
        m4_info             list    list of material4 information
        SEN_info            list    list of SEN information
                                    [w_sen, n_w_sen, h_sen, t_sen,
                                         u_n, l_n, set, u_offset, l_offset]
    Returns:
        lower_shape_upper   list    upper side lower_shape
        lower_shape_lower   list    lower side lower_shape
    """
    """
    1   Get information from m4_info & SEN_info
    """
    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]

    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        lower_shape_upper_left_row   list
        lower_shape_upper_right_row  list

        lower_shape_lower_left_row   list
        lower_shape_lower_right_row  list
    """
    # upper side
    lower_shape_upper_left_row = []
    lower_shape_upper_right_row = []

    for i in range(u_n - 1, -1, -1):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        lower_shape_upper_left_row.extend((left_points))

    for i in range(u_n):
        # right row
        ix = tx - t_sen
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        lower_shape_upper_right_row.extend(right_points)

    # lower side
    lower_shape_lower_left_row = []
    lower_shape_lower_right_row = []

    for i in range(l_n):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p5, p6, p7, p8, p1, p2, p3, p4]
        lower_shape_lower_left_row.extend((left_points))

    for i in range(l_n - 1, -1, -1):
        # right row
        ix = tx - t_sen
        iy = ty -  (i * l_offset + set) - 10

        p0, p1, p2, p3, p4, p5, p6, p7, p8 = Y_lower_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p1, p2, p3, p4, p5, p6, p7, p8]
        lower_shape_lower_right_row.extend(right_points)

    lower_shape_upper = [lower_shape_upper_left_row, lower_shape_upper_right_row]
    lower_shape_lower = [lower_shape_lower_left_row, lower_shape_lower_right_row]

    return lower_shape_upper, lower_shape_lower

# middle shape------------------------------------------------------------------
def X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of middle shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix - n_w_sen / 2, iy + t_sen)
    p2 = (ix - n_w_sen / 2, iy - t_sen)
    p3 = (ix + n_w_sen / 2, iy - t_sen)
    p4 = (ix + n_w_sen / 2, iy + t_sen)

    return p0, p1, p2, p3, p4

def Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen):
    """Make list of Y direction middle shapes points.
    Receives:
        (ix, iy)       point   Base point of shape.
            w_sen      int     x length of sen
            n_w_sen    int     narrow part x length of sen
            t_sen      int     z length of sen (thickness of sen)
    Returns:
            points
    """
    p0 = (ix, iy)
    p1 = (ix + t_sen, iy - n_w_sen / 2)
    p2 = (ix - t_sen, iy - n_w_sen / 2)
    p3 = (ix - t_sen, iy + n_w_sen / 2)
    p4 = (ix + t_sen, iy + n_w_sen / 2)

    return p0, p1, p2, p3, p4

def m1_make_middle_shape_points_list(tx, ty, m1_info, SEN_info):
    """Make m1 middle shape points list.
    Receives:
        ix, iy      pt      base point to make AIKAKI
        m1_info     list    list of material1 information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 u_n, l_n, set, u_offset, l_offset]
    Returns:
        middle_shape_upper  list    upper side middle_shape
                                    [middle_shape_upper_left_row, middle_shape_upper_right_row]
        middle_shape_lower  list    lower side middle_shape
                                    [middle_shape_lower_left_row, upper_shape_lower_right_row]
    """
    """
    1   Get information from m1_info & SEN_info
    """
    x_m1 = m1_info[0]
    y_m1 = m1_info[1]
    z_m = m1_info[2]

    m1_points = m1_info[3]

    m1_p0 = m1_points[0]
    m1_p1 = m1_points[1]
    m1_p2 = m1_points[2]
    m1_p3 = m1_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        middle_shape_upper_left_row      list
        middle_shape_upper_right_row     list

        middle_shape_lower_left_row      list
        middle_shape_lower_right_row     list
    """
    # upper side
    middle_shape_upper_left_row = []
    middle_shape_upper_right_row = []

    for i in range(u_n):
        # left row
        ix = tx + t_sen
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p2, p1, p4, p3]
        middle_shape_upper_left_row.extend((left_points))

    for i in range(u_n - 1, -1, -1):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p4, p3, p2, p1]
        middle_shape_upper_right_row.extend(right_points)

    # lower side
    middle_shape_lower_left_row = []
    middle_shape_lower_right_row = []

    for i in range(l_n - 1, -1, -1):
        # left row
        ix = tx + t_sen
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p2, p1, p4, p3]
        middle_shape_lower_left_row.extend((left_points))

    for i in range(l_n):
        # right row
        ix = tx + (x_m1 - t_sen)
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p4, p3, p2, p1]
        middle_shape_lower_right_row.extend(right_points)

    middle_shape_upper = [middle_shape_upper_left_row, middle_shape_upper_right_row]
    middle_shape_lower = [middle_shape_lower_left_row, middle_shape_lower_right_row]

    return middle_shape_upper, middle_shape_lower

def m2_m3_make_middle_shape_points_list(dx, dy, m_info, SEN_info):
    """Make middle shape points list.
    Receives:
        dx, dy      pt      base point to make TSUGITE
        m_info      list    list of material information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 l_n, r_n, set, l_offset, r_offset]
    Returns:
        middle_shape_m1     list    material1 middle_shape
                                    [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
        middle_shape_m2     list    material2 middle_shape
                                    [middle_shape_m2_upper_row, middle_shape_m2_lower_row]
    """
    """
    1   Get information from m_info & SEN_info.
    """
    x_m = m_info[0]
    y_m = m_info[1]
    z_m = m_info[2]

    m_points = m_info[3]

    m_p0 = m_points[0]
    m_p1 = m_points[1]
    m_p2 = m_points[2]
    m_p3 = m_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    l_n = SEN_info[4]
    r_n = SEN_info[5]
    set = SEN_info[6]
    l_offset = SEN_info[7]
    r_offset = SEN_info[8]

    """
    2   Make lists.
        middle_shape_m1_upper_row      list
        middle_shape_m1_lower_row      list

        middle_shape_m2_upper_row     list
        middle_shape_m2_lower_row     list
    """
    # material1
    middle_shape_m1_upper_row = []
    middle_shape_m1_lower_row = []

    for i in range(l_n):
        # upper row
        ix = i * l_offset + set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p1, p2, p3, p4]
        middle_shape_m1_upper_row.extend((upper_points))

    for i in range(l_n - 1, -1, -1):
        # lower row
        ix = i * l_offset + set
        iy = t_sen + dy
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p3, p4, p1, p2]
        middle_shape_m1_lower_row.extend(lower_points)

    # material2
    middle_shape_m2_upper_row = []
    middle_shape_m2_lower_row = []

    for i in range(r_n):
        # upper row
        ix = x_m - i * r_offset - set
        iy = y_m - t_sen + dy
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        upper_points = [p4, p3, p2, p1]
        middle_shape_m2_upper_row.extend((upper_points))

    for i in range(r_n - 1, -1, -1):
        # lower row
        ix = x_m - i * r_offset - set
        iy = t_sen + dy
        p0, p1, p2, p3, p4 = X_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        lower_points = [p2, p1, p4, p3]
        middle_shape_m2_lower_row.extend(lower_points)

    middle_shape_m1 = [middle_shape_m1_upper_row, middle_shape_m1_lower_row]
    middle_shape_m2 = [middle_shape_m2_upper_row, middle_shape_m2_lower_row]

    return middle_shape_m1, middle_shape_m2

def m4_make_middle_shape_points_list(tx, ty, m4_info, SEN_info):
    """Make m4 middle shape points list.
    Receives:
        ix, iy      pt      base point to make AIKAKI
        m4_info     list    list of material1 information
        SEN_info    list    list of SEN information
                            [w_sen, n_w_sen, h_sen, t_sen,
                                 u_n, l_n, set, u_offset, l_offset]
    Returns:
        middle_shape_upper  list    upper side middle_shape
                                    [middle_shape_upper_left_row, middle_shape_upper_right_row]
        middle_shape_lower  list    lower side middle_shape
                                    [middle_shape_lower_left_row, upper_shape_lower_right_row]
    """
    """
    1   Get information from m1_info & SEN_info
    """
    x_m4 = m4_info[0]
    y_m4 = m4_info[1]
    z_m = m4_info[2]

    m4_points = m4_info[3]

    m4_p0 = m4_points[0]
    m4_p1 = m4_points[1]
    m4_p2 = m4_points[2]
    m4_p3 = m4_points[3]

    w_sen = SEN_info[0]
    n_w_sen = SEN_info[1]
    h_sen = SEN_info[2]
    t_sen = SEN_info[3]
    u_n = SEN_info[4]
    l_n = SEN_info[5]
    set = SEN_info[6]
    u_offset = SEN_info[7]
    l_offset = SEN_info[8]

    """
    2   Make lists.
        middle_shape_upper_left_row      list
        middle_shape_upper_right_row     list

        middle_shape_lower_left_row      list
        middle_shape_lower_right_row     list
    """
    # upper side
    middle_shape_upper_left_row = []
    middle_shape_upper_right_row = []

    for i in range(u_n - 1, -1, -1):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p3, p4, p1, p2]
        middle_shape_upper_left_row.extend((left_points))

    for i in range(u_n):
        # right row
        ix = tx - t_sen
        iy = ty + (i * u_offset + set) + 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p1, p2, p3, p4]
        middle_shape_upper_right_row.extend(right_points)

    # lower side
    middle_shape_lower_left_row = []
    middle_shape_lower_right_row = []

    for i in range(l_n):
        # left row
        ix = tx - (x_m4 - t_sen)
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        left_points = [p3, p4, p1, p2]
        middle_shape_lower_left_row.extend((left_points))

    for i in range(l_n - 1, -1, -1):
        # right row
        ix = tx - t_sen
        iy = ty - (i * l_offset + set) - 10

        p0, p1, p2, p3, p4 = Y_middle_shape_points(ix, iy, w_sen, t_sen, n_w_sen)
        right_points = [p1, p2, p3, p4]
        middle_shape_lower_right_row.extend(right_points)

    middle_shape_upper = [middle_shape_upper_left_row, middle_shape_upper_right_row]
    middle_shape_lower = [middle_shape_lower_left_row, middle_shape_lower_right_row]

    return middle_shape_upper, middle_shape_lower

# For User----------------------------------------------------------------------
# SEN shape---------------------------------------------------------------------
def SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset):
    """Make list of SEN points.
    Receives:
        (ix, iy)        num     Base point of SEN
        w_sen           int     x length of sen
        n_w_sen         int     narrow part x length of sen
        t_m             int     z length of material (thickness of material)
    Returns:
        points          list    list of SEN points.
    """
    p0 = (ix, iy)
    p1 = (ix - w_sen + n_w_sen / 2 - 3 * SEN_offset / 4, iy)
    p2 = (ix - w_sen + n_w_sen / 2 - 3 * SEN_offset / 4, iy + t_m)
    p3 = (ix - n_w_sen / 2 - SEN_offset / 4, iy + t_m)
    p4 = (ix - n_w_sen / 2 - SEN_offset / 4, iy + 3 * t_m)
    p5 = (ix + w_sen - n_w_sen / 2 + 3 * SEN_offset / 4, iy + 3 * t_m)
    p6 = (ix + w_sen - n_w_sen / 2 + 3 * SEN_offset / 4, iy + 2 * t_m)
    p7 = (ix + n_w_sen / 2 + SEN_offset / 4, iy + 2 * t_m)
    p8 = (ix + n_w_sen / 2 + SEN_offset / 4, iy)

    return p0, p1, p2, p3, p4, p5, p6, p7, p8

def make_SEN_crvs\
    (m1_male_SEN_info, m1_female_SEN_info, m2_SEN_info, m3_SEN_info,\
        m4_male_SEN_info, m4_female_SEN_info, offset):
    """Make SEN crvs.
    Receives:
        m1_male_SEN_info    list    list of SEN information
        m1_female_SEN_info  list    ditto
        m2_SEN_info         list    ditto
        m3_SEN_info         list    ditto
        m4_male_SEN_info    list    ditto
        m4_female_SEN_info  list    ditto

        [w_sen, n_w_sen, h_sen, t_sen, u_n, l_n, set, u_offset, l_offset]

    Returns:
        SEN_crvs    list    list of SEN crvs
    """
    """
    1   Get information from each SEN_info
    """
    w_sen = m2_SEN_info[0]
    n_w_sen = m2_SEN_info[1]
    h_sen = m2_SEN_info[2]
    t_m = h_sen / 3

    # m1 number of SEN (male and female are same number)
    u_n = m1_male_SEN_info[4]
    l_n = m1_male_SEN_info[5]
    m1_n = u_n + l_n
    print (m1_n)

    # m2 number of SEN
    l_n = m2_SEN_info[4]
    r_n = m2_SEN_info[5]
    m2_n = l_n + r_n
    print (m2_n)

    # m3 number of SEN
    l_n = m3_SEN_info[4]
    r_n = m3_SEN_info[5]
    m3_n = l_n + r_n

    # m4 number of SEN (male and female are same number)
    u_n = m4_male_SEN_info[4]
    l_n = m4_male_SEN_info[5]
    m4_n = u_n + l_n


    SEN_n = (m1_n + m2_n + m3_n + m4_n) * 2 + 5

    minimum = 0
    maximum = 0.5

    SEN_offset = rs.GetReal("Put the offset num to fit SEN tight. (0.0 < offset < 0.5)",\
                        0.4, minimum, maximum)

    # NOTE: offset num is not parametric number. It's always fixed.

    """
    2   Make SEN shapes.
    """
    SEN_shapes = []
    j = 0

    for i in range(SEN_n):
        ix = i * 1.25 * (2 * w_sen - n_w_sen)
        iy = -100 * (j + 1)
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
        SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
        SEN_shape = rs.AddPolyline(SEN_shape_list)
        SEN_shapes.append(SEN_shape)

    for i in range(SEN_n):
        ix = i * 1.25 * (2 * w_sen - n_w_sen)
        iy = -100 * (j + 1) - 50
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
        SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
        SEN_shape = rs.AddPolyline(SEN_shape_list)
        SEN_shapes.append(SEN_shape)

    SEN_shape = []
    j = 1
    for i in range(SEN_n):
        ix = i * 1.25 * (2 * w_sen - n_w_sen)
        iy = -100 * (j + 1)
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
        SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
        SEN_shape = rs.AddPolyline(SEN_shape_list)
        SEN_shapes.append(SEN_shape)

    for i in range(SEN_n):
        ix = i * 1.25 * (2 * w_sen - n_w_sen)
        iy = -100 * (j + 1) - 50
        p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
        SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
        SEN_shape = rs.AddPolyline(SEN_shape_list)
        SEN_shapes.append(SEN_shape)


    """
    for j in range(3):
        for i in range(SEN_n):
            ix = i * 1.25 * (2 * w_sen - n_w_sen)
            iy = -100 * (j + 1)
            p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
            SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
            SEN_shape = rs.AddPolyline(SEN_shape_list)
            SEN_shapes.append(SEN_shape)

        for i in range(SEN_n):
            ix = i * 1.25 * (2 * w_sen - n_w_sen)
            iy = -100 * (j + 1) - 50
            p0, p1, p2, p3, p4, p5, p6, p7, p8 = SEN_points(ix, iy, w_sen, n_w_sen, t_m, SEN_offset)
            SEN_shape_list = [p1, p2, p3, p4, p5, p6, p7, p8, p1]
            SEN_shape = rs.AddPolyline(SEN_shape_list)
            SEN_shapes.append(SEN_shape)
    """

    return SEN_shapes

# Deploy crvs (processing data)-------------------------------------------------
def deploy_male_crvs\
    (TABLE_info, m1_male_crvs, m2_male_left_crvs, m2_male_right_crvs,\
        m3_male_left_crvs, m3_male_right_crvs, m4_male_crvs):
    """Deploy male crvs.
    Receives:
        TABLE_info          list    list of TABLE information
        m1_male_crvs        list    list of guid [upper, middle, lower]
        m2_male_left_crvs   list    ditto
        m2_male_right_crvs  list    ditto
        m3_male_left_crvs   list    ditto
        m3_male_right_crvs  list    ditto
        m4_male_crvs        list    ditto
    Returns:
        ---
    """
    """
    1   Get information from crv list
    """
    # TABLE_info
    width = TABLE_info[0]
    height = TABLE_info[1]
    t_m = TABLE_info[2]

    # m1
    m1_male_upper_crv = m1_male_crvs[0]
    m1_male_middle_crv = m1_male_crvs[1]
    m1_male_lower_crv = m1_male_crvs[2]

    # m2
    m2_male_left_upper_crv = m2_male_left_crvs[0]
    m2_male_left_middle_crv = m2_male_left_crvs[1]
    m2_male_left_lower_crv = m2_male_left_crvs[2]

    m2_male_right_upper_crv = m2_male_right_crvs[0]
    m2_male_right_middle_crv = m2_male_right_crvs[1]
    m2_male_right_lower_crv = m2_male_right_crvs[2]

    # m3
    m3_male_left_upper_crv = m3_male_left_crvs[0]
    m3_male_left_middle_crv = m3_male_left_crvs[1]
    m3_male_left_lower_crv = m3_male_left_crvs[2]

    m3_male_right_upper_crv = m3_male_right_crvs[0]
    m3_male_right_middle_crv = m3_male_right_crvs[1]
    m3_male_right_lower_crv = m3_male_right_crvs[2]

    # m4
    m4_male_upper_crv = m4_male_crvs[0]
    m4_male_middle_crv = m4_male_crvs[1]
    m4_male_lower_crv = m4_male_crvs[2]

    """
    2   Deploy crvs to user can pick up crv data.
    """
    # upper
    # m1
    trans = (0, 3 * width, 0)
    rs.MoveObject(m1_male_upper_crv, trans)

    # m2
    trans = (-5 * t_m, 3 * width + 3 * t_m, 0)
    rs.MoveObject(m2_male_left_upper_crv, trans)

    trans = (0, 3 * width + 3 * t_m, 0)
    rs.MoveObject(m2_male_right_upper_crv, trans)

    # m3
    trans = (-5 * t_m, 3 * width - 3 * t_m, 0)
    rs.MoveObject(m3_male_left_upper_crv, trans)

    trans = (0, 3 * width - 3 * t_m, 0)
    rs.MoveObject(m3_male_right_upper_crv, trans)

    # m4
    trans = (-5 * t_m, 3 * width, 0)
    rs.MoveObject(m4_male_upper_crv, trans)

    # middle
    # m1
    trans = (0, 1.5 * width, 0)
    rs.MoveObject(m1_male_middle_crv, trans)

    # m2
    trans = (-5 * t_m, 1.5 * width + 3 * t_m, 0)
    rs.MoveObject(m2_male_left_middle_crv, trans)

    trans = (0, 1.5 * width + 3 * t_m, 0)
    rs.MoveObject(m2_male_right_middle_crv, trans)

    # m3
    trans = (-5 * t_m, 1.5 * width - 3 * t_m, 0)
    rs.MoveObject(m3_male_left_middle_crv, trans)

    trans = (0, 1.5 * width - 3 * t_m, 0)
    rs.MoveObject(m3_male_right_middle_crv, trans)

    # m4
    trans = (-5 * t_m, 1.5 * width, 0)
    rs.MoveObject(m4_male_middle_crv, trans)

    # lower
    # m1
    trans = (0, 0, 0)
    rs.MoveObject(m1_male_lower_crv, trans)

    # m2
    trans = (-5 * t_m, 3 * t_m, 0)
    rs.MoveObject(m2_male_left_lower_crv, trans)

    trans = (0, 3 * t_m, 0)
    rs.MoveObject(m2_male_right_lower_crv, trans)

    # m3
    trans = (-5 * t_m, -3 * t_m, 0)
    rs.MoveObject(m3_male_left_lower_crv, trans)

    trans = (0, -3 * t_m, 0)
    rs.MoveObject(m3_male_right_lower_crv, trans)

    # m4
    trans = (-5 * t_m, 0, 0)
    rs.MoveObject(m4_male_lower_crv, trans)

def deploy_female_crvs\
    (TABLE_info, m1_female_crvs, m2_female_left_crvs, m2_female_right_crvs,\
        m3_female_left_crvs, m3_female_right_crvs, m4_female_crvs):
    """Deploy male crvs.
    Receives:
        TABLE_info            list    list of TABLE information
        m1_female_crvs        list    list of guid [upper, middle, lower]
        m2_female_left_crvs   list    ditto
        m2_female_right_crvs  list    ditto
        m3_female_left_crvs   list    ditto
        m3_female_right_crvs  list    ditto
        m4_female_left_crvs   list    ditto
        m4_female_right_crvs  list    ditto
    Returns:
        ---
    """
    """
    1   Get information from crv list
    """
    # TABLE_info
    width = TABLE_info[0]
    height = TABLE_info[1]
    t_m = TABLE_info[2]

    # m1
    m1_female_upper_crv = m1_female_crvs[0]
    m1_female_middle_crv = m1_female_crvs[1]
    m1_female_lower_crv = m1_female_crvs[2]

    # m2
    m2_female_left_upper_crv = m2_female_left_crvs[0]
    m2_female_left_middle_crv = m2_female_left_crvs[1]
    m2_female_left_lower_crv = m2_female_left_crvs[2]

    m2_female_right_upper_crv = m2_female_right_crvs[0]
    m2_female_right_middle_crv = m2_female_right_crvs[1]
    m2_female_right_lower_crv = m2_female_right_crvs[2]

    # m3
    m3_female_left_upper_crv = m3_female_left_crvs[0]
    m3_female_left_middle_crv = m3_female_left_crvs[1]
    m3_female_left_lower_crv = m3_female_left_crvs[2]

    m3_female_right_upper_crv = m3_female_right_crvs[0]
    m3_female_right_middle_crv = m3_female_right_crvs[1]
    m3_female_right_lower_crv = m3_female_right_crvs[2]

    # m4
    m4_female_upper_crv = m4_female_crvs[0]
    m4_female_middle_crv = m4_female_crvs[1]
    m4_female_lower_crv = m4_female_crvs[2]

    """
    2   Deploy crvs to user can pick up crv data.
    """
    # upper
    # m1
    trans = (1.5 * height, 3 * width, 0)
    rs.MoveObject(m1_female_upper_crv, trans)

    # m2
    trans = (1.5 * height - 5 * t_m, 3 * width + 3 * t_m, 0)
    rs.MoveObject(m2_female_left_upper_crv, trans)

    trans = (1.5 * height, 3 * width + 3 * t_m, 0)
    rs.MoveObject(m2_female_right_upper_crv, trans)

    # m3
    trans = (1.5 * height - 5 * t_m, 3 * width - 3 * t_m, 0)
    rs.MoveObject(m3_female_left_upper_crv, trans)

    trans = (1.5 * height, 3 * width - 3 * t_m, 0)
    rs.MoveObject(m3_female_right_upper_crv, trans)

    # m4
    trans = (1.5 * height - 5 * t_m, 3 * width, 0)
    rs.MoveObject(m4_female_upper_crv, trans)

    # middle
    # m1
    trans = (1.5 * height, 1.5 * width, 0)
    rs.MoveObject(m1_female_middle_crv, trans)

    # m2
    trans = (1.5 * height - 5 * t_m, 1.5 * width + 3 * t_m, 0)
    rs.MoveObject(m2_female_left_middle_crv, trans)

    trans = (1.5 * height, 1.5 * width + 3 * t_m, 0)
    rs.MoveObject(m2_female_right_middle_crv, trans)

    # m3
    trans = (1.5 * height - 5 * t_m, 1.5 * width - 3 * t_m, 0)
    rs.MoveObject(m3_female_left_middle_crv, trans)

    trans = (1.5 * height, 1.5 * width - 3 * t_m, 0)
    rs.MoveObject(m3_female_right_middle_crv, trans)

    # m4
    trans = (1.5 * height - 5 * t_m, 1.5 * width, 0)
    rs.MoveObject(m4_female_middle_crv, trans)

    # lower
    # m1
    trans = (1.5 * height, 0, 0)
    rs.MoveObject(m1_female_lower_crv, trans)

    # m2
    trans = (1.5 * height - 5 * t_m, 3 * t_m, 0)
    rs.MoveObject(m2_female_left_lower_crv, trans)

    trans = (1.5 * height, 3 * t_m, 0)
    rs.MoveObject(m2_female_right_lower_crv, trans)

    # m3
    trans = (1.5 * height - 5 * t_m, -3 * t_m, 0)
    rs.MoveObject(m3_female_left_lower_crv, trans)

    trans = (1.5 * height, -3 * t_m, 0)
    rs.MoveObject(m3_female_right_lower_crv, trans)

    # m4
    trans = (1.5 * height - 5 * t_m, 0, 0)
    rs.MoveObject(m4_female_lower_crv, trans)

# Make table model--------------------------------------------------------------
def make_male_3D_model\
    (TABLE_info, m1_male_crvs, m2_male_left_crvs, m2_male_right_crvs,\
    m3_male_left_crvs, m3_male_right_crvs, m4_male_crvs):
    """Make 3D model of male parts.
    Receives:
        TABLE_info          list    list of TABLE information
                                    [width, height, t_m]
        m1_male_crvs        list    list of crvs
        m2_male_left_crvs   list    ditto
        m2_male_right_crvs  list    ditto
        m3_male_left_crvs   list    ditto
        m3_male_right_crvs  list    ditto
        m4_male_crvs        list    ditto
    Returns:
        male_models         list    list of models (rotated)
    """
    """
    1   Get t_m from TABLE_info
    """
    width = TABLE_info[0]
    t_m = TABLE_info[2]

    """
    2   Get crvs from list.
    """
    # m1
    m1_male_upper_crv = m1_male_crvs[0]
    m1_male_middle_crv = m1_male_crvs[1]
    m1_male_lower_crv = m1_male_crvs[2]

    # m2
    m2_male_left_upper_crv = m2_male_left_crvs[0]
    m2_male_left_middle_crv = m2_male_left_crvs[1]
    m2_male_left_lower_crv = m2_male_left_crvs[2]

    m2_male_right_upper_crv = m2_male_right_crvs[0]
    m2_male_right_middle_crv = m2_male_right_crvs[1]
    m2_male_right_lower_crv = m2_male_right_crvs[2]

    # m3
    m3_male_left_upper_crv = m3_male_left_crvs[0]
    m3_male_left_middle_crv = m3_male_left_crvs[1]
    m3_male_left_lower_crv = m3_male_left_crvs[2]

    m3_male_right_upper_crv = m3_male_right_crvs[0]
    m3_male_right_middle_crv = m3_male_right_crvs[1]
    m3_male_right_lower_crv = m3_male_right_crvs[2]

    # m4
    m4_male_upper_crv = m4_male_crvs[0]
    m4_male_middle_crv = m4_male_crvs[1]
    m4_male_lower_crv = m4_male_crvs[2]

    """
    3   Make 3D.
    """
    # path
    start = (0, 0, 0)
    end = (0, 0, t_m)
    path = rs.AddLine(start, end)

    # m1
    m1_male_upper_model = rs.ExtrudeCurve(m1_male_upper_crv, path)
    m1_male_middle_model = rs.ExtrudeCurve(m1_male_middle_crv, path)
    m1_male_lower_model = rs.ExtrudeCurve(m1_male_lower_crv, path)

    rs.CapPlanarHoles(m1_male_upper_model)
    rs.CapPlanarHoles(m1_male_middle_model)
    rs.CapPlanarHoles(m1_male_lower_model)

    # m2 left
    m2_male_left_upper_model = rs.ExtrudeCurve(m2_male_left_upper_crv, path)
    m2_male_left_middle_model = rs.ExtrudeCurve(m2_male_left_middle_crv, path)
    m2_male_left_lower_model = rs.ExtrudeCurve(m2_male_left_lower_crv, path)

    rs.CapPlanarHoles(m2_male_left_upper_model)
    rs.CapPlanarHoles(m2_male_left_middle_model)
    rs.CapPlanarHoles(m2_male_left_lower_model)

    # m2 right
    m2_male_right_upper_model = rs.ExtrudeCurve(m2_male_right_upper_crv, path)
    m2_male_right_middle_model = rs.ExtrudeCurve(m2_male_right_middle_crv, path)
    m2_male_right_lower_model = rs.ExtrudeCurve(m2_male_right_lower_crv, path)

    rs.CapPlanarHoles(m2_male_right_upper_model)
    rs.CapPlanarHoles(m2_male_right_middle_model)
    rs.CapPlanarHoles(m2_male_right_lower_model)

    # m3 left
    m3_male_left_upper_model = rs.ExtrudeCurve(m3_male_left_upper_crv, path)
    m3_male_left_middle_model = rs.ExtrudeCurve(m3_male_left_middle_crv, path)
    m3_male_left_lower_model = rs.ExtrudeCurve(m3_male_left_lower_crv, path)

    rs.CapPlanarHoles(m3_male_left_upper_model)
    rs.CapPlanarHoles(m3_male_left_middle_model)
    rs.CapPlanarHoles(m3_male_left_lower_model)

    # m3 right
    m3_male_right_upper_model = rs.ExtrudeCurve(m3_male_right_upper_crv, path)
    m3_male_right_middle_model = rs.ExtrudeCurve(m3_male_right_middle_crv, path)
    m3_male_right_lower_model = rs.ExtrudeCurve(m3_male_right_lower_crv, path)

    rs.CapPlanarHoles(m3_male_right_upper_model)
    rs.CapPlanarHoles(m3_male_right_middle_model)
    rs.CapPlanarHoles(m3_male_right_lower_model)

    # m4
    m4_male_upper_model = rs.ExtrudeCurve(m4_male_upper_crv, path)
    m4_male_middle_model = rs.ExtrudeCurve(m4_male_middle_crv, path)
    m4_male_lower_model = rs.ExtrudeCurve(m4_male_lower_crv, path)

    rs.CapPlanarHoles(m4_male_upper_model)
    rs.CapPlanarHoles(m4_male_middle_model)
    rs.CapPlanarHoles(m4_male_lower_model)

    male_upper_models =\
    [m1_male_upper_model, m2_male_left_upper_model, m2_male_right_upper_model,\
    m3_male_left_upper_model, m3_male_right_upper_model, m4_male_upper_model]

    male_middle_models =\
    [m1_male_middle_model, m2_male_left_middle_model, m2_male_right_middle_model,\
    m3_male_left_middle_model, m3_male_right_middle_model, m4_male_middle_model]

    male_lower_models =\
    [m1_male_lower_model, m2_male_left_lower_model, m2_male_right_lower_model,\
    m3_male_left_lower_model, m3_male_right_lower_model, m4_male_lower_model]

    # move objects
    trans_upper = (0, 0, 2 * t_m)
    trans_middle = (0, 0, t_m)
    rs.MoveObjects(male_upper_models, trans_upper)
    rs.MoveObjects(male_middle_models, trans_middle)


    # deploy models
    O = (0, 0, 0)
    angle = 90
    rs.RotateObjects(male_upper_models, O, angle, None, False)
    rs.RotateObjects(male_middle_models, O, angle, None, False)
    rs.RotateObjects(male_lower_models, O, angle, None, False)

    axis = (1, 0, 0)
    rs.RotateObjects(male_upper_models, O, angle, axis, False)
    rs.RotateObjects(male_middle_models, O, angle, axis, False)
    rs.RotateObjects(male_lower_models, O, angle, axis, False)

    trans = (-1.5 * width, 0, 0)
    rs.MoveObjects(male_upper_models, trans)
    rs.MoveObjects(male_middle_models, trans)
    rs.MoveObjects(male_lower_models, trans)

    rs.DeleteObject(path)

    male_models = [male_upper_models, male_middle_models, male_lower_models]

def make_female_3D_model\
    (TABLE_info, m1_female_crvs, m2_female_left_crvs, m2_female_right_crvs,\
    m3_female_left_crvs, m3_female_right_crvs, m4_female_crvs):
    """Make 3D model of female parts.
    Receives:
        TABLE_info              list    list of TABLE information
                                    [width, height, t_m]
        m1_female_crvs          list    list of crvs
        m2_female_left_crvs     list    ditto
        m2_female_right_crvs    list    ditto
        m3_female_left_crvs     list    ditto
        m3_female_right_crvs    list    ditto
        m4_female_crvs          list    ditto
    Returns:
        female_models           list    list of models (rotated)
    """
    """
    1   Get t_m from TABLE_info
    """
    width = TABLE_info[0]
    height = TABLE_info[1]
    t_m = TABLE_info[2]

    """
    2   Get crvs from list.
    """
    # m1
    m1_female_upper_crv = m1_female_crvs[0]
    m1_female_middle_crv = m1_female_crvs[1]
    m1_female_lower_crv = m1_female_crvs[2]

    # m2
    m2_female_left_upper_crv = m2_female_left_crvs[0]
    m2_female_left_middle_crv = m2_female_left_crvs[1]
    m2_female_left_lower_crv = m2_female_left_crvs[2]

    m2_female_right_upper_crv = m2_female_right_crvs[0]
    m2_female_right_middle_crv = m2_female_right_crvs[1]
    m2_female_right_lower_crv = m2_female_right_crvs[2]

    # m3
    m3_female_left_upper_crv = m3_female_left_crvs[0]
    m3_female_left_middle_crv = m3_female_left_crvs[1]
    m3_female_left_lower_crv = m3_female_left_crvs[2]

    m3_female_right_upper_crv = m3_female_right_crvs[0]
    m3_female_right_middle_crv = m3_female_right_crvs[1]
    m3_female_right_lower_crv = m3_female_right_crvs[2]

    # m4
    m4_female_upper_crv = m4_female_crvs[0]
    m4_female_middle_crv = m4_female_crvs[1]
    m4_female_lower_crv = m4_female_crvs[2]

    """
    3   Make 3D.
    """
    # path
    start = (0, 0, 0)
    end = (0, 0, t_m)
    path = rs.AddLine(start, end)

    # m1
    m1_female_upper_model = rs.ExtrudeCurve(m1_female_upper_crv, path)
    m1_female_middle_model = rs.ExtrudeCurve(m1_female_middle_crv, path)
    m1_female_lower_model = rs.ExtrudeCurve(m1_female_lower_crv, path)

    rs.CapPlanarHoles(m1_female_upper_model)
    rs.CapPlanarHoles(m1_female_middle_model)
    rs.CapPlanarHoles(m1_female_lower_model)

    # m2 left
    m2_female_left_upper_model = rs.ExtrudeCurve(m2_female_left_upper_crv, path)
    m2_female_left_middle_model = rs.ExtrudeCurve(m2_female_left_middle_crv, path)
    m2_female_left_lower_model = rs.ExtrudeCurve(m2_female_left_lower_crv, path)

    rs.CapPlanarHoles(m2_female_left_upper_model)
    rs.CapPlanarHoles(m2_female_left_middle_model)
    rs.CapPlanarHoles(m2_female_left_lower_model)

    # m2 right
    m2_female_right_upper_model = rs.ExtrudeCurve(m2_female_right_upper_crv, path)
    m2_female_right_middle_model = rs.ExtrudeCurve(m2_female_right_middle_crv, path)
    m2_female_right_lower_model = rs.ExtrudeCurve(m2_female_right_lower_crv, path)

    rs.CapPlanarHoles(m2_female_right_upper_model)
    rs.CapPlanarHoles(m2_female_right_middle_model)
    rs.CapPlanarHoles(m2_female_right_lower_model)

    # m3 left
    m3_female_left_upper_model = rs.ExtrudeCurve(m3_female_left_upper_crv, path)
    m3_female_left_middle_model = rs.ExtrudeCurve(m3_female_left_middle_crv, path)
    m3_female_left_lower_model = rs.ExtrudeCurve(m3_female_left_lower_crv, path)

    rs.CapPlanarHoles(m3_female_left_upper_model)
    rs.CapPlanarHoles(m3_female_left_middle_model)
    rs.CapPlanarHoles(m3_female_left_lower_model)

    # m3 right
    m3_female_right_upper_model = rs.ExtrudeCurve(m3_female_right_upper_crv, path)
    m3_female_right_middle_model = rs.ExtrudeCurve(m3_female_right_middle_crv, path)
    m3_female_right_lower_model = rs.ExtrudeCurve(m3_female_right_lower_crv, path)

    rs.CapPlanarHoles(m3_female_right_upper_model)
    rs.CapPlanarHoles(m3_female_right_middle_model)
    rs.CapPlanarHoles(m3_female_right_lower_model)

    # m4
    m4_female_upper_model = rs.ExtrudeCurve(m4_female_upper_crv, path)
    m4_female_middle_model = rs.ExtrudeCurve(m4_female_middle_crv, path)
    m4_female_lower_model = rs.ExtrudeCurve(m4_female_lower_crv, path)

    rs.CapPlanarHoles(m4_female_upper_model)
    rs.CapPlanarHoles(m4_female_middle_model)
    rs.CapPlanarHoles(m4_female_lower_model)

    female_upper_models =\
    [m1_female_upper_model, m2_female_left_upper_model, m2_female_right_upper_model,\
    m3_female_left_upper_model, m3_female_right_upper_model, m4_female_upper_model]

    female_middle_models =\
    [m1_female_middle_model, m2_female_left_middle_model, m2_female_right_middle_model,\
    m3_female_left_middle_model, m3_female_right_middle_model, m4_female_middle_model]

    female_lower_models =\
    [m1_female_lower_model, m2_female_left_lower_model, m2_female_right_lower_model,\
    m3_female_left_lower_model, m3_female_right_lower_model, m4_female_lower_model]

    # move objects
    trans_upper = (0, 0, 2 * t_m)
    trans_middle = (0, 0, t_m)
    rs.MoveObjects(female_upper_models, trans_upper)
    rs.MoveObjects(female_middle_models, trans_middle)


    # deploy models
    O = (0, 0, 0)
    angle = 90
    rs.RotateObjects(female_upper_models, O, angle, None, False)
    rs.RotateObjects(female_middle_models, O, angle, None, False)
    rs.RotateObjects(female_lower_models, O, angle, None, False)

    axis = (1, 0, 0)
    rs.RotateObjects(female_upper_models, O, angle, axis, False)
    rs.RotateObjects(female_middle_models, O, angle, axis, False)
    rs.RotateObjects(female_lower_models, O, angle, axis, False)

    rs.RotateObjects(female_upper_models, O, angle, None, False)
    rs.RotateObjects(female_middle_models, O, angle, None, False)
    rs.RotateObjects(female_lower_models, O, angle, None, False)

    trans = (-2 * width - 3 * t_m / 2, width / 2 - 3 * t_m / 2, 0)
    rs.MoveObjects(female_upper_models, trans)
    rs.MoveObjects(female_middle_models, trans)
    rs.MoveObjects(female_lower_models, trans)

    rs.DeleteObject(path)

    female_models = [female_upper_models, female_middle_models, female_lower_models]

def make_board(TABLE_info):
    """Make temporary board 3D.
    Receives:
        TABLE_info  list        list of TABLE informaiton.
                                [width, height, t_m]
    Returns:
        board       guid        rhino guid.
    """
    """
    1   Get information from list.
    """
    width = TABLE_info[0]
    height = TABLE_info[1]
    t_m = TABLE_info[2]

    """
    2   Make board 3D.
    """
    plane = rs.WorldXYPlane()

    # radius = 1 * width
    # circle = rs.AddCircle(plane, radius)

    w = 1.5 * width
    h = w
    rect = rs.AddRectangle(plane, w, h)

    start = (0, 0, 0)
    end = (0, 0, t_m)
    path = rs.AddLine(start, end)

    # board = rs.ExtrudeCurve(circle, path)
    board = rs.ExtrudeCurve(rect, path)

    rs.CapPlanarHoles(board)
    rs.DeleteObject(path)

    # """
    # 3'  Move circle board.
    # """
    # trans = (0, 0, height)
    # rs.MoveObject(board, trans)
    #
    # trans = (-4 * width / 2, -3 * t_m / 2, 0)
    # rs.MoveObject(board, trans)
    # rs.MoveObject(circle, trans)
    #
    # trans = (0, 3 * width, 0)
    # rs.MoveObject(circle, trans)

    """
    3'' Move rect board.
    """
    trans = (0, 0, height)
    rs.MoveObject(board, trans)

    trans = (-2.75 * width, - 0.75 * width - 3 * t_m / 2, 0)
    rs.MoveObject(board, trans)
    rs.MoveObject(rect, trans)

    trans = (0, 3 * width, 0)
    rs.MoveObject(rect, trans)

# ------------------------------------------------------------------------------
# CODE--------------------------------------------------------------------------
delete_all()
RUN()
