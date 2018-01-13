__author__ = 'Lorenzo Argentieri'

import inspect
import pkgutil
import mayaLib as mLib


class StructureManager():
    """
    Read Documentation in docstring
    """

    #root_package = ''

    def __init__(self, lib):
        self.root_package = lib
        self.structLib = {}

        # Main Packages
        self.package_list = self.listAllPackage()
        #print 'Package list: ', self.package_list
        for pack in self.package_list[1:]:
            self.structLib[pack] = {}

        # Packages
        for key in self.structLib.iterkeys():
            pack_list = self.listModules(key)
            if len(pack_list) != 0:
                for pack in pack_list[0]:
                    mod = pack.split('.')
                    self.structLib[mod[-2]][mod[-1]] = pack

                    # Sub Packages
                    if mod[-1] == 'base' or mod[-1] == 'utility' or mod[-1] == 'utils':
                        subMod_list = self.explore_package(pack)
                        for subMod in subMod_list:
                            subModNameSplit = subMod.split('.')
                            self.structLib[subModNameSplit[-3]][subModNameSplit[-2]] = {subModNameSplit[-1]: subMod}


        ##################
        # self.package_list = self.listAllPackage()
        # print 'Package list: ', self.package_list

        # self.module_list = self.listAllModule()
        # print 'Module list: ', self.module_list
        #
        # self.subPackage_list = self.listSubPackages(self.module_list[0][0])
        # print 'subPackage list: ', self.subPackage_list
        #
        # self.class_list = self.getAllClass(self.subPackage_list[0])
        # print 'class list: ', self.class_list[0]

        # Testing
        module = self.structLib['fluidLib']['fireSmoke']
        print module
        test = self.getAllClass(module)
        print test
        testFuncStr = test[1][0]

        func = self.importAndExec(module, testFuncStr)
        print func
        func()

    def getStructLib(self):
        return self.structLib

    def importAndExec(self, moduleString, function):
        module = __import__(moduleString, fromlist=[''])
        func = getattr(module, function)
        return func

    def listAllPackage(self):
        package_list = []
        for p in pkgutil.walk_packages(self.root_package.__path__):
            package_list.append(p[1])

        return  package_list

    def listSubPackages(self, package_str):
        package_list = []
        package = __import__(package_str, fromlist=[''])
        for p in pkgutil.iter_modules(package.__path__):
            package_list.append(package_str + '.' + p[1])

        return  package_list

    def listModules(self, package):
        module_list = []
        package_name = self.root_package.__name__ + '.' + package
        modules_list = self.explore_package(package_name)
        if len(modules_list) != 0:
            module_list.append(modules_list)

        return module_list

    # ToDo: rewrite
    def listAllModule(self):
        module_list = []
        for package in self.package_list:
            package_name = self.root_package.__name__ + '.' + package
            modules_list = self.explore_package(package_name)
            if len(modules_list) != 0:
                module_list.append(modules_list)

        return module_list

    def getAllClass(self, module_str):
        module = __import__(module_str, fromlist=[''])
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
    StructureManager(mLib)
