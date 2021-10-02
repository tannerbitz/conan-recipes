from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

class XtensorZarrConan(ConanFile):
    name = "xtensor-zarr"
    version = "0.0.7"
    license = "BSD-3-Clause"
    url = "http://xtensor-zarr.readthedocs.io/"
    description = "xtensor-zarr offers an API to create and access a Zarr (v2 or v3) hierarchy in a store (locally or in the cloud), read and write arrays (in various formats) and groups in the hierarchy, and explore the hierarchy."
    topics = ("xtensor-zarr", "zarr")
    settings = "os", "compiler", "build_type", "arch"
    options = {
        "disable_arch_native": [True, False],
        "shared": [True, False],
    }

    default_options = {
        "disable_arch_native": False, 
        "shared": False,
    }

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def configure(self):
        # https://xtensor-zarr.readthedocs.io/en/latest/
        # - On Windows platforms, Visual C++ 2015 Update 2, or more recent
        # - On Unix platforms, gcc 4.9 or a recent version of Clang
        version = tools.Version(self.settings.compiler.version)
        compiler = self.settings.compiler
        if compiler == "Visual Studio" and version < "16":
            raise ConanInvalidConfiguration(
                "xtensor requires at least Visual Studio version 15.9, please use 16"
            )
        if (compiler == "gcc" and version < "5.0") or (
            compiler == "clang" and version < "4"
        ):
            raise ConanInvalidConfiguration("xtensor requires at least C++14")

    def requirements(self):
        self.requires("xtensor/0.23.10")
        self.requires("xtensor-io/0.12.9")
        self.requires("zarray/0.1.0")
        self.requires("nlohmann_json/3.9.1")
        self.requires("c-blosc/1.21.0")
        self.requires("zlib/1.2.11")
        self.requires("gdal/3.3.1")
        self.requires("ghc-filesystem/1.5.8")
        self.requires("zstd/1.5.0")


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
            {"xtensor-zarr": "xtensor-zarr::xtensor-zarr"}
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
        self.cpp_info.names["cmake_find_package"] = "xtensor-zarr"
        self.cpp_info.names["cmake_find_package_multi"] = "xtensor-zarr"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "xtensor-zarr"
        if self.options.disable_arch_native:
            self.cpp_info.defines.append("XTENSOR_ZARR_DISABLE_ARCH_NATIVE")
        if self.options.shared:
            self.cpp_info.defines.append("XTENSOR_ZARR_BUILD_SHARED_LIBS")
        else:
            self.cpp_info.defines.append("XTENSOR_ZARR_BUILD_STATIC_LIBS")
