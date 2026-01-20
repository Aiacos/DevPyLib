"""Function discovery and introspection utilities.

Provides tools for discovering available functions and classes in modules
for dynamic UI generation via the StructureManager class.
"""

__author__ = "Lorenzo Argentieri"

import pymel.core as pm

if pm.about(version=True) == "2022":
    import collections as collection
else:
    import collections.abc as collection
import inspect
import pkgutil

import mayaLib as mLib


class StructureManager:
    """Manage Lib Structure."""

    # root_package = ''

    def __init__(self, lib):
        """Initialize the class with the root package."""
        self.root_package = lib
        self.struct_lib = {}

        self.final_class_list = []
        self.module_class_list = []

        self.package_list = self.list_all_package()

        self.module_list = self.list_all_module()
        self.module_list = sum(self.module_list, [])

        self.sub_package_list = []
        for mod in self.module_list:
            try:
                # Module Case
                sub_pack = self.list_sub_packages(mod)
            except (AttributeError, ImportError):
                self.module_class_list.append(mod)
            else:
                self.module_class_list.extend(sub_pack)

        for item in self.module_class_list:
            # Class OR Function Case

            # Add Class to path
            self.class_list = self.get_all_class(item)
            for c in self.class_list:
                self.final_class_list.append(item + "." + c[0])
            # Add Function to path
            self.function_list = self.get_all_function(item)
            for f in self.function_list:
                self.final_class_list.append(item + "." + f[0])

        # Testing
        for item in self.final_class_list:
            split = item.split(".")
            tmp_dict = {}
            for key in reversed(split):
                tmp_dict = {key: item} if key == split[-1] else self.incapsulate_dict(tmp_dict, key)

            # print tmp_dict
            self.dict_merge(self.struct_lib, tmp_dict)

        # print(self.struct_lib)
        # for k, v in self.struct_lib['mayaLib']['fluidLib'].iteritems():
        #    print(k, v)
        # func = self.import_and_exec('mayaLib.fluidLib.fire', 'Fire')
        # print('FUNCTION: ', func)
        # func()

    def dict_merge(self, dct, merge_dct):
        """Recursively merges two dictionaries.

        If both dictionaries have a key with dictionary values, the function
        will recursively merge those dictionary values. Otherwise, the value
        from `merge_dct` will overwrite the value in `dct`.

        Parameters:
        dct (dict): The dictionary to be merged into.
        merge_dct (dict): The dictionary to merge from.
        """
        for k, _v in merge_dct.items():
            if (
                k in dct
                and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collection.Mapping)
            ):
                self.dict_merge(dct[k], merge_dct[k])
            else:
                dct[k] = merge_dct[k]

    def incapsulate_dict(self, dictionary, key):
        """Incapsulate the dictionary into a new one with the given key."""
        return {key: dictionary}

    def get_struct_lib(self):
        """Return the structure dictionary."""
        return self.struct_lib

    def import_and_exec(self, module_string, function):
        """Import the module and execute the given function."""
        module = __import__(module_string, fromlist=[""])
        func = getattr(module, function)
        return func

    def list_all_package(self):
        """Return a list of all packages in the root package."""
        package_list = []
        for p in pkgutil.walk_packages(self.root_package.__path__):
            if "utility" not in p[1]:
                package_list.append(p[1])

        return package_list

    def list_all_package_2(self):
        """List all packages using inspect.getmembers approach.

        Alternative method to list packages by inspecting module members,
        filtering out dunder (double underscore) names.

        Returns:
            list: Package member objects from root_package
        """
        package_list = [o[1] for o in inspect.getmembers(self.root_package) if "__" not in o[0]]
        # print(package_list)
        return package_list

    def list_sub_packages(self, package_str):
        """Return a list of all sub packages in the given package."""
        package_list = []
        package = __import__(package_str, fromlist=[""])
        for p in pkgutil.iter_modules(package.__path__):
            package_list.append(package_str + "." + p[1])

        return package_list

    def list_modules(self, package):
        """Return a list of all modules in the given package."""
        module_list = []
        package_name = self.root_package.__name__ + "." + package
        modules_list = self.explore_package(package_name)
        if len(modules_list) != 0:
            module_list.append(modules_list)

        return module_list

    def list_all_module(self):
        """Return a list of all modules in the root package."""
        module_list = []
        for package in self.package_list:
            # print('PACKAGE:: ', str(package))
            if ("utility" not in str(package)) and ("licenseRegister" not in str(package)):
                package_name = self.root_package.__name__ + "." + str(package)
                if not (
                    (package_name == "mayaLib.install") or (package_name == "mayaLib.installCmd")
                ):
                    modules_list = self.list_sub_packages(package_name)
                    if len(modules_list) != 0:
                        module_list.append(modules_list)

        return module_list

    def get_all_class(self, module_str):
        """Return a list of all classes in the given module.

        Args:
            module_str (str): The name of the module to inspect.

        Returns:
            list: A list of tuples where each tuple contains the class name
                  and the class object.

        Note:
            The function will not inspect modules named 'licenseRegister',
            'fix_loa_connection', or 'paintable_maps'. In these cases, it returns
            an empty string.
        """
        if (
            ("licenseRegister" not in module_str)
            and ("fix_loa_connection" not in module_str)
            and ("paintable_maps" not in module_str)
        ):
            module = __import__(module_str, fromlist=[""])
            class_list = [o for o in inspect.getmembers(module) if inspect.isclass(o[1])]
            return class_list
        else:
            return ""

    def get_all_method(self, module_str):
        """Return a list of all methods in the given module."""
        module = __import__(module_str, fromlist=[""])
        method_list = [o for o in inspect.getmembers(module) if inspect.ismethod(o[1])]
        return method_list

    def get_all_function(self, module_str):
        """Return a list of all functions in the given module.

        Args:
            module_str (str): The name of the module to inspect.

        Returns:
            list: A list of tuples where each tuple contains the function name
                  and the function object.

        Note:
            The function will not inspect modules named 'licenseRegister',
            'fix_loa_connection', or 'paintable_maps'. In these cases, it returns
            an empty string.
        """
        if (
            ("licenseRegister" not in module_str)
            and ("fix_loa_connection" not in module_str)
            and ("paintable_maps" not in module_str)
        ):
            module = __import__(module_str, fromlist=[""])
            functions_list = [o for o in inspect.getmembers(module) if inspect.isfunction(o[1])]
            return functions_list
        else:
            return ""

    def explore_package(self, module_name):
        """Explore the given package and return a list of all sub packages."""
        package_list = []
        if ("licenseRegister" not in module_name) and ("fix_loa_connection" not in module_name):
            loader = pkgutil.get_loader(module_name)

            if loader is not None:
                for sub_module in pkgutil.iter_modules([module_name]):
                    print("SubMod: ", sub_module)
                    _, sub_module_name, _ = sub_module
                    qname = module_name + "." + sub_module_name
                    package_list.append(qname)
                    self.explore_package(qname)

        return package_list

    def nested_dict_iter(self, dictionary):
        """Iterate the nested dictionary and print the values."""
        for k, v in dictionary.items():
            if isinstance(v, dict):
                self.nested_dict_iter(v)
            else:
                # print("{0} : {1}".format(k, v))
                module = v
                class_list = self.get_all_class(module)
                function_list = self.get_all_function(module)

                class_dict = {}
                function_dict = {}

                for c in class_list:
                    class_dict = {c[0]: v + "." + c[0]}
                for f in function_list:
                    function_dict = {f[0]: v + "." + f[0]}

                callable_dict = {"class": class_dict, "function": function_dict}
                dictionary[k] = callable_dict


if __name__ == "__main__":
    StructureManager(mLib)
