from conans import ConanFile, tools
from conans.errors import ConanInvalidConfiguration
import os
import textwrap

required_conan_version = ">=1.33.0"


class Z5Conan(ConanFile):
    name = "Z5"
    license = "BSD-3-Clause"
    url = "https://github.com/constantinpape/z5"
    homepage = "https://github.com/constantinpape/z5"
    description = "C++ and Python wrapper for zarr and n5 file formats"
    topics = ("conan", "z5", "zarr", "n5")
    settings = "os", "arch", "compiler", "build_type"
    version = "2.0.10"
    options = {
        "blosc": [True, False],
        "zlib": [True, False],
        "bzip2": [True, False],
        "xz": [True, False],
        "lz4": [True, False],
    }
    default_options = {
        "blosc": False,
        "zlib": False,
        "bzip2": False,
        "xz": False,
        "lz4": False,
    }
    
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("boost/1.77.0")
        self.requires("xtensor/0.23.10")
        self.requires("nlohmann_json/3.10.2")
        if self.options.blosc:
            self.requires("c-blosc/1.21.0")
        if self.options.zlib:
            self.requires("zlib/1.2.11")
        if self.options.bzip2:
            self.requires("bzip2/1.0.8")
        if self.options.xz:
            self.requires("xz_utils/5.2.5")
        if self.options.lz4:
            self.requires("lz4/1.9.3")

    def package_id(self):
        self.info.header_only()

    def source(self):
        tools.get(**self.conan_data["sources"][self.version],
                  destination=self._source_subfolder, strip_root=True)

    def package(self):
        self.copy("LICENSE", dst="licenses", src=self._source_subfolder)
        self.copy(
            "*.h*", dst="include", src=os.path.join(self._source_subfolder, "include")
        )
        self._create_cmake_module_alias_targets(
            os.path.join(self.package_folder, self._module_file_rel_path),
            {"z5": "z5::z5"}
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
        self.cpp_info.names["cmake_find_package"] = "z5"
        self.cpp_info.names["cmake_find_package_multi"] = "z5"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "z5"
        if self.options.blosc:
            self.cpp_info.defines.append("WITH_BLOSC")
        if self.options.zlib:
            self.cpp_info.defines.append("WITH_ZLIB")
        if self.options.bzip2:
            self.cpp_info.defines.append("WITH_BZIP2")
        if self.options.xz:
            self.cpp_info.defines.append("WITH_XZ")
        if self.options.lz4:
            self.cpp_info.defines.append("WITH_LZ4")

