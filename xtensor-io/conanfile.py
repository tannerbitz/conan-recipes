from conans import ConanFile, tools
from conans.errors import RecipeNotFoundException
import os
import textwrap

required_conan_version = ">=1.33.0"


class XtensorIoConan(ConanFile):
    name = "xtensor-io"
    license = "BSD-3-Clause"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/xtensor-stack/xtensor-io"
    description = "xtensor-io offers an API to read and write various file formats into xtensor data structures"
    topics = ("conan", "xtesnor-io", "binary storage")
    settings = "os", "arch", "compiler", "build_type"
    version = "0.12.7"
    options = {
        "oiio": [True, False],
        "sndfile": [True, False],
        "zlib": [True, False],
        "highfive": [True, False],
        "blosc": [True, False],
        "gdal": [True, False],
        "storage_client": [True, False],
        "awssdk": [True, False],
    }
    default_options = {
        "oiio": False,
        "sndfile": False,
        "zlib": False,
        "highfive": False,
        "blosc": False,
        "gdal": False,
        "storage_client": False,
        "awssdk": False,
    }
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def requirements(self):
        self.requires("xtensor/0.23.10")
        if (self.options.oiio):
            self.requires("openimageio/2.3.7.2")
        if (self.options.sndfile):
            self.requires("libsndfile/1.0.31")
        if (self.options.zlib):
            self.requires("zlib/1.2.11")
        if (self.options.highfive):
            raise RecipeNotFoundException("HighFive Recipe Not Found")
        if (self.options.blosc):
            self.requires("c-blosc/1.21.0")
        if (self.options.gdal):
            self.requires("gdal/3.3.1")
        if (self.options.storage_client):
            self.requires("google-cloud-cpp/1.30.1")
        if (self.options.awssdk):
            self.requires("aws-sdk-cpp/1.8.130")


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
            {"xtensor-io": "xtensor-io::xtensor-io"}
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
        self.cpp_info.names["cmake_find_package"] = "xtensor-io"
        self.cpp_info.names["cmake_find_package_multi"] = "xtensor-io"
        self.cpp_info.builddirs.append(self._module_subfolder)
        self.cpp_info.build_modules["cmake_find_package"] = [self._module_file_rel_path]
        self.cpp_info.build_modules["cmake_find_package_multi"] = [self._module_file_rel_path]
        self.cpp_info.names["pkg_config"] = "xtensor-io"
        if (self.options.oiio):
            self.cpp_info.defines.append("HAVE_OIIO")
        if (self.options.sndfile):
            self.cpp_info.defines.append("HAVE_SndFile")
        if (self.options.zlib):
            self.cpp_info.defines.append("HAVE_ZLIB")
        if (self.options.highfive):
            self.cpp_info.defines.append("HAVE_HighFive")
        if (self.options.blosc):
            self.cpp_info.defines.append("HAVE_Blosc")
        if (self.options.gdal):
            self.cpp_info.defines.append("HAVE_GDAL")
        if (self.options.storage_client):
            self.cpp_info.defines.append("HAVE_storage_client")
        if (self.options.awssdk):
            self.cpp_info.defines.append("HAVE_AWSSDK")
