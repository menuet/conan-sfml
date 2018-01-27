#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


def output_enter_leave(fn):
    def _impl(*args, **kwargs):
        conan_obj = args[0]
        functionTitle = "{module}.{cls}.{fn}".format(module=fn.__module__, cls=conan_obj.__class__.__name__, fn=fn.__name__) if args else "{module}.{fn}.".format(module=fn.__module__, fn=fn.__name__)
        conan_obj.output.info("ENTER {}()".format(functionTitle))
        try:
            return fn(*args, **kwargs)
        finally:
            conan_obj.output.info("LEAVE {}".format(functionTitle))
    return _impl


class SfmlConan(ConanFile):
    name = "sfml"
    version = "2.4.2"
    url = "https://github.com/bincrafters/conan-sfml"
    description = "Simple and Fast Multimedia Library"
    license = "https://www.sfml-dev.org/license.php"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    install_subfolder = "install_subfolder"

    @output_enter_leave
    def source(self):
        source_url = "https://github.com/SFML/SFML"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name.upper() + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    @output_enter_leave
    def requirements(self):
        # SFML depends on many external third-parties.
        # - On Windows, they are bundled as binaries inside the sources.
        # - On Linux, we are advised to install them as system packages.
        # - On Android, it may be the same as on Linux.
        # - On Macos, they seem to be bundled as frameworks inside the sources (but I don't know enough about how this works).
        # - On iOS, it may be the same as on Macos.

        # Ideally, for all platforms, we would install them as conan packages
        # but this would probably require to work with SFML team to modify their cmakelist ?

        # The following conan packages are available in bincrafters bintray:
        # self.requires("libjpeg/9b@bincrafters/stable") # jpeg
        # self.requires("freetype/2.8.1@bincrafters/stable") # freetype
        # self.requires("glfw/3.2.1@bincrafters/stable") # opengl
        # self.requires("vorbis/1.3.5@bincrafters/stable") # vorbis
        # self.requires("flac/1.3.2@bincrafters/stable") # flac
        # self.requires("ogg/1.3.3@bincrafters/stable") # ogg
        pass

    @output_enter_leave
    def system_requirements(self):
        if self.settings.os == "Linux":
            # - On Linux, as stated in https://www.sfml-dev.org/tutorials/2.4/compile-with-cmake.php,
            #   we are advised to install the following system packages:
            #     freetype, jpeg, x11, xrandr, xcb, x11-xcb, xcb-randr, xcb-image,
            #     opengl, flac, ogg, vorbis, vorbisenc, vorbisfile, openal, pthread
            package_tool = tools.SystemPackageTool()
            package_tool.install("libx11-dev")
            package_tool.install("libxrandr-dev")
            package_tool.install("freeglut3-dev")
            package_tool.install("libudev-dev")
            package_tool.install("libjpeg8-dev")
            package_tool.install("libopenal-dev")
            package_tool.install("libsndfile1-dev")
            package_tool.install("libfreetype6-dev")

    @output_enter_leave
    def build(self):
        self.output.info("Current Dir: {}".format(os.getcwd()))
        if self.settings.os == "Linux": # See: https://stackoverflow.com/questions/38727800/ld-linker-error-cpu-model-hidden-symbol
            self._patch_cmakelist_for_graphics()
        cmake = CMake(self)
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = "TRUE"
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join("..", self.install_subfolder)
        cmake.definitions["CMAKE_INSTALL_FRAMEWORK_PREFIX"] = os.path.join("..", self.install_subfolder, "frameworks")
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["SFML_USE_STATIC_STD_LIBS"] = "TRUE" if str(self.settings.compiler.runtime).startswith("MT") else "FALSE"
        cmake.configure(source_folder=".", build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

    @output_enter_leave
    def package(self):
        include_folder = os.path.join(self.install_subfolder, "include")
        bin_folder = os.path.join(self.install_subfolder, "bin")
        lib_folder = os.path.join(self.install_subfolder, "lib")
        frameworks_folder = os.path.join(self.install_subfolder, "frameworks")

        self.copy(pattern="LICENSE", dst="license")
        self.copy(pattern="*", dst="include", src=include_folder)
        self.copy(pattern="*.*", dst="frameworks", src=frameworks_folder)
        self.copy(pattern="*.dll", dst="bin", src=bin_folder, keep_path=False)
        self.copy(pattern="*.so*", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.dylib", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.lib", dst="lib", src=lib_folder, keep_path=False)
        self.copy(pattern="*.a", dst="lib", src=lib_folder, keep_path=False)

    @output_enter_leave
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        if not self.options.shared:
            self.cpp_info.defines = ["SFML_STATIC"]
            if self.settings.os == "Windows":
                self.cpp_info.libs.extend(["opengl32.lib", "winmm.lib", "gdi32.lib", "ws2_32.lib"])
        if self.settings.os == "Linux":
            # On Linux, do we need to link with sfml's third-parties too ?
            pass
        if self.settings.os == "Macos" or self.settings.os == "iOS":
            # On Mac, do we may need to do something like this ?
            # self.cpp_info.exelinkflags.append("-framework FLAC")
            # self.cpp_info.exelinkflags.append("-framework freetype")
            # self.cpp_info.exelinkflags.append("-framework ogg")
            # self.cpp_info.exelinkflags.append("-framework OpenAL")
            # self.cpp_info.exelinkflags.append("-framework vorbis")
            # self.cpp_info.exelinkflags.append("-framework vorbisenc")
            # self.cpp_info.exelinkflags.append("-framework vorbisfile")
            # self.cpp_info.sharedlinkflags = self.cpp_info.exelinkflags
            pass

    def _patch_cmakelist_for_graphics(self):
        def _read_file(file_path_name):
            f = open(file_path_name, "r")
            contents = f.readlines()
            f.close()
            return contents
        def _write_file(file_path_name, contents):
            f = open(file_path_name, "w")
            contents = "".join(contents)
            f.write(contents)
            f.close()
        self.output.warn("Applying workaround for bug https://bugs.launchpad.net/ubuntu/+source/gcc-5/+bug/1568899")
        search_for = "# define the sfml-graphics target\n"
        replace_with = "\n".join([
            '# BEGIN PATCH for link error: hidden symbol __cpu_model (https://bugs.launchpad.net/ubuntu/+source/gcc-5/+bug/1568899)',
            'if(SFML_COMPILER_GCC AND BUILD_SHARED_LIBS)',
            '    list(APPEND GRAPHICS_EXT_LIBS "-lgcc_s -lgcc")',
            'endif()',
            '# END PATCH',
            '',
            search_for,
        ])
        cmakelist_path_name = os.path.join(self.source_subfolder, "src/SFML/Graphics/CMakeLists.txt")
        contents = _read_file(cmakelist_path_name)
        contents = [replace_with if x==search_for else x for x in contents]
        _write_file(cmakelist_path_name, contents)
