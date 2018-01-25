#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


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

    def source(self):
        source_url = "https://github.com/SFML/SFML"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name.upper() + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

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

    def system_requirements(self):
        if self.settings.os == "Linux":
            # - On Linux, as stated in https://www.sfml-dev.org/tutorials/2.4/compile-with-cmake.php,
            #   we are advised to install the following system packages:
            #     freetype, jpeg, x11, xrandr, xcb, x11-xcb, xcb-randr, xcb-image,
            #     opengl, flac, ogg, vorbis, vorbisenc, vorbisfile, openal, pthread
            # Should we do this ?
            # installer = SystemPackageTool()
            # installer.install("libx11-dev")
            # installer.install("libxrandr-dev")
            # installer.install("freeglut3-dev")
            # installer.install("libudev-dev")
            # installer.install("libjpeg8-dev")
            # installer.install("libopenal-dev")
            # installer.install("libsndfile1-dev")
            # installer.install("libfreetype6-dev")
            pass

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join("..", self.install_subfolder)
        cmake.definitions["CMAKE_INSTALL_FRAMEWORK_PREFIX"] = os.path.join("..", self.install_subfolder, "frameworks")
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["SFML_USE_STATIC_STD_LIBS"] = "TRUE" if str(self.settings.compiler.runtime).startswith("MT") else "FALSE"
        cmake.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

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
