#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from conans import ConanFile, tools, AutoToolsBuildEnvironment
from conans.errors import ConanException


class CmakeinstallerConan(ConanFile):
    name        = 'cmake_installer'
    version     = '3.11.3'
    license     = 'MIT'
    url         = 'https://github.com/kheaactua/conan-cmake-installer'
    description = 'Install CMake from source'
    settings    = 'os', 'compiler', 'build_type', 'arch'
    requires    = 'helpers/0.3@ntc/stable'

    def minor_version(self):
        return ".".join(str(self.cmake_version).split(".")[:2])

    def system_requirements(self):
        pack_names = None
        if tools.os_info.linux_distro == 'ubuntu':
            pack_names = ['libncurses5-dev', 'libssl-dev']

            if self.settings.arch == 'x86':
                full_pack_names = []
                for pack_name in pack_names:
                    full_pack_names += [pack_name + ':i386']
                pack_names = full_pack_names

        if pack_names:
            installer = tools.SystemPackageTool()
            try:
                installer.update() # Update the package database
                installer.install(' '.join(pack_names)) # Install the package
            except ConanException:
                self.output.warn('Could not run system requirements installer.  Required packages might be missing.')

    def source(self):
        self.run('git clone https://github.com/Kitware/CMake')
        self.run('cd CMake && git checkout v%s'%self.version)

    def build(self):
        from platform_helpers import which

        ccache = False
        if which('ccache') is not None:
            ccache = True

        with tools.chdir('CMake'):
            autotools = AutoToolsBuildEnvironment(self, win_bash=('Windows' == self.settings.os))
            self.run('./bootstrap --parallel=%d --prefix=%s %s'%(tools.cpu_count(), self.package_folder, '--enable-ccache' if ccache else ''))
            autotools.make()
            autotools.make(target='install')

    def package_info(self):
        if self.package_folder is not None:
            minor = self.minor_version()
            self.env_info.path.append(os.path.join(self.package_folder, "bin"))
            self.env_info.CMAKE_ROOT = self.package_folder
            mod_path = os.path.join(self.package_folder, "share", "cmake-%s" % minor, "Modules")
            self.env_info.CMAKE_MODULE_PATH = mod_path
            if not os.path.exists(mod_path):
                raise Exception("Module path not found: %s" % mod_path)

# vim: ts=4 sw=4 expandtab ffs=unix ft=python foldmethod=marker :
