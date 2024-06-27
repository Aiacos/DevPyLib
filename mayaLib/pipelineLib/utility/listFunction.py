__author__ = 'Lorenzo Argentieri'
import pymel.core as pm

if pm.about(version=True) == '2022':
    import collections as collection
else:
    import collections.abc as collection
import inspect
import pkgutil

import mayaLib as mLib


class StructureManager():
    """
    Manage Lib Structure
    """

    # root_package = ''

    def __init__(self, lib):
        self.root_package = lib
        self.structLib = {}

        self.finalClassList = []
        self.moduleClassList = []

        self.package_list = self.listAllPackage()

        self.module_list = self.listAllModule()
        self.module_list = sum(self.module_list, [])

        self.subPackage_list = []
        for mod in self.module_list:
            try:
                # Module Case
                subPack = self.listSubPackages(mod)
                self.moduleClassList.extend(subPack)
            except:
                self.moduleClassList.append(mod)

        for item in self.moduleClassList:
            # Class OR Function Case

            # Add Class to path
            self.class_list = self.getAllClass(item)
            for c in self.class_list:
                self.finalClassList.append(item + '.' + c[0])
            # Add Function to path
            self.function_list = self.getAllFunction(item)
            for f in self.function_list:
                self.finalClassList.append(item + '.' + f[0])

        # Testing
        for item in self.finalClassList:
            split = item.split('.')
            tmpDict = {}
            for key in reversed(split):
                if key == split[-1]:
                    tmpDict = {key: item}
                else:
                    tmpDict = self.incapsulateDict(tmpDict, key)

            # print tmpDict
            self.dict_merge(self.structLib, tmpDict)

        # print(self.structLib)
        # for k, v in self.structLib['mayaLib']['fluidLib'].iteritems():
        #    print(k, v)
        # func = self.importAndExec('mayaLib.fluidLib.fire', 'Fire')
        # print('FUNCTION: ', func)
        # func()

    def dict_merge(self, dct, merge_dct):
        """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
        updating only top-level keys, dict_merge recurses down into dicts nested
        to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
        ``dct``.
        :param dct: dict onto which the merge is executed
        :param merge_dct: dct merged into dct
        :return: None
        """
        for k, v in merge_dct.items():
            if (k in dct and isinstance(dct[k], dict)
                    and isinstance(merge_dct[k], collection.Mapping)):
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    def incapsulateDict(self, dict, key):
        return {key: dict}

    def getStructLib(self):
        return self.structLib

    def importAndExec(self, moduleString, function):
        module = __import__(moduleString, fromlist=[''])
        func = getattr(module, function)
        return func

    def listAllPackage(self):
        package_list = []
        for p in pkgutil.walk_packages(self.root_package.__path__):
            if 'utility' not in p[1]:
                package_list.append(p[1])

        return package_list

    def listAllPackage2(self):
        package_list = [o[1] for o in inspect.getmembers(self.root_package) if '__' not in o[0]]
        # print(package_list)
        return package_list

    def listSubPackages(self, package_str):
        package_list = []
        package = __import__(package_str, fromlist=[''])
        for p in pkgutil.iter_modules(package.__path__):
            package_list.append(package_str + '.' + p[1])

        return package_list

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
            # print('PACKAGE:: ', str(package))
            if ('utility' not in str(package)) and ('licenseRegister' not in str(package)):
                package_name = self.root_package.__name__ + '.' + str(package)
                if not ((package_name == 'mayaLib.install') or (package_name == 'mayaLib.installCmd')):
                    modules_list = self.listSubPackages(package_name)
                    if len(modules_list) != 0:
                        module_list.append(modules_list)

        return module_list

    def getAllClass(self, module_str):
        if ('licenseRegister' not in module_str) and ('fix_loa_connection' not in module_str) and (
                'paintable_maps' not in module_str):
            module = __import__(module_str, fromlist=[''])
            class_list = [o for o in inspect.getmembers(module) if inspect.isclass(o[1])]
            return class_list
        else:
            return ''

    def getAllMethod(self, module_str):
        module = __import__(module_str, fromlist=[''])
        method_list = [o for o in inspect.getmembers(module) if inspect.ismethod(o[1])]
        return method_list

    def getAllFunction(self, module_str):
        if ('licenseRegister' not in module_str) and ('fix_loa_connection' not in module_str) and (
                'paintable_maps' not in module_str):
            module = __import__(module_str, fromlist=[''])
            functions_list = [o for o in inspect.getmembers(module) if inspect.isfunction(o[1])]
            return functions_list
        else:
            return ''

    def explore_package(self, module_name):
        package_list = []
        if ('licenseRegister' not in module_name) and ('fix_loa_connection' not in module_name):
            loader = pkgutil.get_loader(module_name)

            if loader != None:
                for sub_module in pkgutil.iter_modules([module_name]):
                    print('SubMod: ', sub_module)
                    _, sub_module_name, _ = sub_module
                    qname = module_name + "." + sub_module_name
                    package_list.append(qname)
                    self.explore_package(qname)

        return package_list

    def nested_dict_iter(self, dictionary):
        for k, v in dictionary.items():
            if isinstance(v, dict):
                self.nested_dict_iter(v)
            else:
                # print("{0} : {1}".format(k, v))
                module = v
                class_list = self.getAllClass(module)
                function_list = self.getAllFunction(module)

                class_dict = {}
                function_dict = {}

                for c in class_list:
                    class_dict = {c[0]: v + '.' + c[0]}
                for f in function_list:
                    function_dict = {f[0]: v + '.' + f[0]}

                callable_dict = {'class': class_dict, 'function': function_dict}
                dictionary[k] = callable_dict


if __name__ == "__main__":
    StructureManager(mLib)
