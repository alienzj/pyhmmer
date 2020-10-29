import configparser
import glob
import os
import sys

import setuptools
from Cython.Build import cythonize
from setuptools.command.build_ext import build_ext as _build_ext
from setuptools.command.sdist import sdist as _sdist


class sdist(_sdist):
    """A `sdist` that generates a `pyproject.toml` on the fly.
    """

    def run(self):
        # build `pyproject.toml` from `setup.cfg`
        c = configparser.ConfigParser()
        c.add_section("build-system")
        c.set("build-system", "requires", str(self.distribution.setup_requires))
        c.set("build-system", 'build-backend', '"setuptools.build_meta"')
        with open("pyproject.toml", "w") as pyproject:
            c.write(pyproject)
        # run the rest of the packaging
        _sdist.run(self)


class build_ext(_build_ext):
    """A `build_ext` that disables optimizations if compiled in debug mode.
    """

    def build_static(self, lib, path, libdir="."):
        try:
            self.announce("entering directory {!r}".format(path))
            _cwd = os.getcwd()
            os.chdir(path)

            # run autoconf to generate the configure script
            autoconf = "autoconf.ac" if os.path.isfile("autoconf.ac") else "configure.ac"
            self.make_file([autoconf], "configure", self.spawn, (["autoconf"],))

            # run the configure script
            configure_cmd = ["./configure"]
            if self.debug:
                configure_cmd.append("--enable-debugging")
            self.make_file(["configure"], "Makefile", self.spawn, (configure_cmd,))

            # use the makefile to build the static library
            self.make_file(["Makefile"], lib, self.spawn, (["make", "-C", libdir, lib],))

        finally:
            os.chdir(_cwd)


    def build_extension(self, ext):
        # use the distutils/setuptools temporary folder to build out of source
        _vendor_dir = os.path.join(os.path.dirname(__file__), "vendor")
        _build_dir = os.path.join(self.build_temp, "hmmer")

        # remove the build dir if rebuild is forced
        if self.force and os.path.exists(os.path.join(_build_dir, "hmmer")):
            self.remove_tree(os.path.join(_build_dir, "hmmer"))

        # copy the HMMER and Easel source to the build directory
        if not os.path.exists(_build_dir):
            self.copy_tree(os.path.join(_vendor_dir, "hmmer"), _build_dir, preserve_symlinks=1)
            self.copy_tree(os.path.join(_vendor_dir, "easel"), os.path.join(_build_dir, "easel"), preserve_symlinks=1)

        # build the static libraries
        self.build_static("libeasel.a", os.path.join(_build_dir, "easel"))
        self.build_static("libhmmer.a", _build_dir, libdir="src")

        # update the extension link flags to use the temporary build folder
        ext.library_dirs.append(os.path.join(_build_dir, "easel"))
        ext.library_dirs.append(os.path.join(_build_dir, "src"))

        # update
        if self.debug:
            if sys.platform == "linux" or sys.platform == "darwin":
                ext.extra_compile_args.append("-O0")
            if sys.implementation.name == "cpython":
                ext.define_macros.append(("CYTHON_TRACE_NOGIL", 1))

        _build_ext.build_extension(self, ext)


extensions = [
    setuptools.Extension(
        "hmmer._hmmer",
        ["hmmer/__init__.pyx"],
        include_dirs=["vendor/hmmer/src", "vendor/easel"],
        libraries=["hmmer", "easel"],
        library_dirs=[],
        extra_compile_args=["-Wall"],
    ),
]


setuptools.setup(
    ext_modules=cythonize(extensions, annotate=True),
    cmdclass=dict(sdist=sdist, build_ext=build_ext),
)
