__author__ = 'Lorenzo Argentieri'

import inspect
import pkgutil
#import mayaLib as mLib


def getDocs(element, advanced=True):
    if advanced:
        docs = inspect.getdoc(element)
        return docs
        print 'advanced'
    else:
        print element.__doc__
        print help(element)
        print 'base'

class readDocstring():
    """
    Read Documentation in docstring
    """

    root_package = ''

    def __init__(self):
        self.package_list = self.listAllPackage()
        print 'Package list: ', self.package_list

        self.module_list = self.listAllModule()
        print 'Module list: ', self.module_list

        # Testing
        print self.module_list

    def listAllPackage(self):
        package_list = []
        for p in pkgutil.iter_modules(self.root_package.__path__):
            package_list.append(p[1])

        return  package_list

    def listSubPackages(self, package):
        subpackage_list = []

        for subpackage in subpackage_list:
            print subpackage

        return subpackage_list

    def listModules(self, package):
        module_list = []
        package_name = self.root_package.__name__ + '.' + package
        module_list.append(self.explore_package(package_name))

        return module_list

    # ToDo: rewrite
    def listAllModule(self):
        module_list = []
        for package in self.package_list:
            package_name = self.root_package.__name__ + '.' + package
            module_list.append(self.explore_package(package_name))

        return module_list

    def getAllClass(self, module):
        class_list = [o for o in inspect.getmembers(module) if inspect.isclass(o[1])]
        return class_list

    def getAllMethod(self, module):
        method_list = [o for o in inspect.getmembers(module) if inspect.ismethod(o[1])]
        return method_list

    def getAllFunction(self, module):
        functions_list = [o for o in inspect.getmembers(module) if inspect.isfunction(o[1])]
        return functions_list

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
