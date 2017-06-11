__author__ = 'Lorenzo Argentieri'

import inspect
import pkgutil
import mayaLib as mLib


def getDocs(element):
    advanced = True

    if advanced:
        print inspect.getdoc(element)
    else:
        print element.__doc__
        print help(element)

class readDocstring():
    """
    Read Documentation in docstring
    """

    root_module = mLib

    def __init__(self):
        self.module_list = self.listAllModule()
        print 'Module list: ', self.module_list

        self.package_list = self.listAllPackage()
        print 'Package list: ', self.package_list

        # Testing
        for module in self.package_list:
            for package in module:
                print help(package)

    def listAllModule(self):
        module_list = []
        for p in pkgutil.iter_modules(self.root_module.__path__):
            module_list.append(p[1])

        return  module_list


    def listAllPackage(self):
        package_list = []
        for module in self.module_list:
            module_name = self.root_module.__name__ + '.' + module
            package_list.append(self.explore_package(module_name))

        return package_list

    def explore_package(self, module_name):
        package_list = []
        loader = pkgutil.get_loader(module_name)
        for sub_module in pkgutil.walk_packages([loader.filename]):
            _, sub_module_name, _ = sub_module
            qname = module_name + "." + sub_module_name
            package_list.append(qname)
            self.explore_package(qname)

        return package_list

if __name__ == "__main__":
    readDocstring()
