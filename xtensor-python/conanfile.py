from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class XtensorConan(ConanFile):
    name = "xtensor-python"
    license = "BSD-3-Clause"
    url = "https://github.com/xtensor-stack/xtensor-python"
    homepage = "https://github.com/xtensor-stack/xtensor-python"
    description = "Python bindings for the xtensor C++ multi-dimensional array library."
    topics = ("conan", "c++", "multidimensional-arrays", "python bindings")
    settings = "os", "arch", "compiler", "build_type"
    version = "0.25.3"

    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("pybind11/2.7.1")
        self.requires("xtensor/0.23.10")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.hpp", dst="include", src=os.path.join(self._source_subfolder, "include")
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"xtensor-python": "xtensor-python::xtensor-python"}
        )

    @staticmethod
    def _create_cmake_module_alias_targets(module_file, targets):
        content = ""
        for alias, aliased in targets.items():
            content += textwrap.dedent("""\
                if(TARGET {aliased} AND NOT TARGET {alias})
                    add_library({alias} INTERFACE IMPORTED)
                    set_property(TARGET {alias} PROPERTY INTERFACE_LINK_LIBRARIES {aliased})
                endif()
            """.format(alias=alias, aliased=aliased))
        tools.save(module_file, content)

    @property
    def _module_subfolder(self):
        return os.path.join("lib", "cmake")

    @property
    def _module_file_rel_path(self):
        return os.path.join(self._module_subfolder,
                            "conan-official-{}-targets.cmake".format(self.name))

    def package_info(self):
        self.cpp_info.names["cmake_find_package"] = "xtensor-python"
        self.cpp_info.names["cmake_find_package_multi"] = "xtensor-python"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "xtensor-python"