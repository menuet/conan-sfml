#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools, RunEnvironment
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


class TestPackageConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    @output_enter_leave
    def build(self):
        cmake = CMake(self)
        cmake.definitions["CMAKE_VERBOSE_MAKEFILE"] = "TRUE"
        cmake.configure()
        cmake.build()

    @output_enter_leave
    def test(self):
        with tools.environment_append(RunEnvironment(self).vars):
            bin_path = os.path.join("bin", "test_package")
            if self.settings.os == "Windows":
                self.run(bin_path)
            elif self.settings.os == "Macos":
                self.run("DYLD_LIBRARY_PATH=%s %s" % (os.environ.get('DYLD_LIBRARY_PATH', ''), bin_path))
            else:
                self.run("LD_LIBRARY_PATH=%s %s" % (os.environ.get('LD_LIBRARY_PATH', ''), bin_path))
