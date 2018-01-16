#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os


class SfmlConan(ConanFile):
    name = "sfml"
    version = "2.4.2"
    url = "https://github.com/bincrafters/conan-sfml"
    description = "Simple and Fast Multimedia Library"

    # Indicates License type of the packaged library
    license = "https://www.sfml-dev.org/license.php"

    # Packages the license for the conanfile.py
    exports = ["LICENSE.md"]

    # Remove following lines if the target lib does not use cmake.
    exports_sources = ["CMakeLists.txt"]
    generators = "cmake"

    # Options may need to change depending on the packaged library.
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False]}
    default_options = "shared=True"

    # Custom attributes for Bincrafters recipe conventions
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    install_subfolder = "install_subfolder"

    # Use version ranges for dependencies unless there's a reason not to
    requires = ()

    def source(self):
        source_url = "https://github.com/SFML/SFML"
        tools.get("{0}/archive/{1}.tar.gz".format(source_url, self.version))
        extracted_dir = self.name.upper() + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_INSTALL_PREFIX"] = os.path.join("..", self.install_subfolder)
        cmake.definitions["CMAKE_INSTALL_FRAMEWORK_PREFIX"] = os.path.join("..", self.install_subfolder, "frameworks")
        if self.settings.compiler == "Visual Studio":
            cmake.definitions["SFML_USE_STATIC_STD_LIBS"] = "TRUE" if str(self.settings.compiler.runtime).startswith("MT") else "FALSE"
        cmake.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder)
        cmake.build()
        cmake.install()

        # Note for Linux:
        # As stated in https://www.sfml-dev.org/tutorials/2.4/compile-with-cmake.php,
        # you need to install these system packages:
        #   freetype, jpeg, x11, xrandr, xcb, x11-xcb, xcb-randr, xcb-image,
        #   opengl, flac, ogg, vorbis, vorbisenc, vorbisfile, openal, pthread
        # (see .travis.yml for the list of related apt-get commands)
        # (in the future, this packages may be provided as conan packages too)

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
