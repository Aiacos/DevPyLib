__author__ = 'Lorenzo Argentieri'

class Convention():
    """Class to manage naming conventions of Maya assets

    Attributes:
        separator (str): separator used in names
        left (str): side tag for left side
        right (str): side tag for right side
        grp (str): tag for group
        loc (str): tag for locator
        geo (str): tag for geometry
        proxyGeo (str): tag for proxy geometry
        cv (str): tag for curve
        joint (str): tag for joint
        ikHandle (str): tag for IK handle
        control (str): tag for control
        conventionDict (dict): dictionary containing all the tags
    """

    def __init__(self, uppercase=True,
                 separator='_',
                 left='l',
                 right='r',
                 grp='GRP',
                 loc='LOC',
                 geo='GEO',
                 proxyGeo='PRX',
                 cv='CRV',
                 joint='JNT',
                 ikHandle='IKH',
                 control='CTRL'):
        """Init Convention

        Args:
            uppercase (bool): if True, all tags will be upper case
            separator (str): separator used in names
            left (str): side tag for left side
            right (str): side tag for right side
            grp (str): tag for group
            loc (str): tag for locator
            geo (str): tag for geometry
            proxyGeo (str): tag for proxy geometry
            cv (str): tag for curve
            joint (str): tag for joint
            ikHandle (str): tag for IK handle
            control (str): tag for control
        """
        # general
        self.separator = separator

        # side
        self.left = left
        self.right = right

        # group
        self.grp = grp

        # locator
        self.loc = loc

        # mesh
        self.geo = geo
        self.proxyGeo = proxyGeo

        # curve
        self.cv = cv

        # jont
        self.joint = joint

        # IK handle
        self.ikHandle = ikHandle

        # control
        self.control = control

        self.conventionDict = {'separator': separator,
                               'left': left,
                               'right': right,
                               'group': grp,
                               'locator': loc,
                               'geometry': geo,
                               'proxyGeo': proxyGeo,
                               'curve': cv,
                               'joint': joint,
                               'ikHandle': ikHandle,
                               'control': control}

    def toLower(self, s):
        """Convert a string to lower case

        Args:
            s (str): string to convert

        Returns:
            str: lower case string
        """
        return s.lower()

    def toUpper(self, s):
        """Convert a string to upper case

        Args:
            s (str): string to convert

        Returns:
            str: upper case string
        """
        return s.upper()

    def convertAllToDefault(self):
        """Convert all tags to default convention"""
        pass

    def convertAllToScene(self):
        """Convert all tags to scene convention"""
        pass


if __name__ == "__main__":
    c = Convention()