"""python-for-android recipe for the pygame-ce version used by the game."""

from os.path import join
import glob
import os
import subprocess
import sys

from pythonforandroid.recipe import CompiledComponentsPythonRecipe
from pythonforandroid.toolchain import current_directory


class PygameCeRecipe(CompiledComponentsPythonRecipe):
    version = "2.5.8"
    url = "https://github.com/pygame-community/pygame-ce/archive/refs/tags/{version}.tar.gz"

    site_packages_name = "pygame-ce"
    name = "pygame-ce"

    depends = [
        "sdl2",
        "sdl2_image",
        "sdl2_mixer",
        "sdl2_ttf",
        "setuptools",
        "jpeg",
        "png",
    ]
    call_hostpython_via_targetpython = False
    install_in_hostpython = False

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        with current_directory(self.get_build_dir(arch.arch)):
            import Cython

            if int(Cython.__version__.split(".", maxsplit=1)[0]) < 3:
                raise RuntimeError(
                    "pygame-ce 2.5.8 requires Cython 3 or newer for Python 3.14; "
                    "install Cython 3 in the Python environment running Buildozer."
                )

            pyx_files = (
                glob.glob(os.path.join("src_c", "cython", "pygame", "*.pyx"))
                + glob.glob(
                    os.path.join("src_c", "cython", "pygame", "**", "*.pyx"),
                    recursive=True,
                )
            )
            for pyx_file in pyx_files:
                c_file = pyx_file.split(os.path.sep)
                del c_file[1:3]
                c_file = os.path.splitext(os.path.sep.join(c_file))[0] + ".c"
                if os.path.isfile(c_file):
                    os.remove(c_file)
            subprocess.run(
                [sys.executable, "setup.py", "cython_only"],
                check=True,
            )

            setup_template = open(
                join("buildconfig", "Setup.Android.SDL2.in"),
                encoding="utf-8",
            ).read()
            env = self.get_recipe_env(arch)
            env["ANDROID_ROOT"] = join(self.ctx.ndk.sysroot, "usr")

            png = self.get_recipe("png", self.ctx)
            png_lib_dir = join(png.get_build_dir(arch.arch), ".libs")
            png_inc_dir = png.get_build_dir(arch)

            jpeg = self.get_recipe("jpeg", self.ctx)
            jpeg_inc_dir = jpeg_lib_dir = jpeg.get_build_dir(arch.arch)

            sdl_mixer_includes = ""
            sdl2_mixer_recipe = self.get_recipe("sdl2_mixer", self.ctx)
            for include_dir in sdl2_mixer_recipe.get_include_dirs(arch):
                sdl_mixer_includes += f"-I{include_dir} "

            sdl_image_includes = ""
            sdl2_image_recipe = self.get_recipe("sdl2_image", self.ctx)
            for include_dir in sdl2_image_recipe.get_include_dirs(arch):
                sdl_image_includes += f"-I{include_dir} "

            setup_file = setup_template.format(
                sdl_includes=(
                    " -I"
                    + join(self.ctx.bootstrap.build_dir, "jni", "SDL", "include")
                    + " -L"
                    + join(self.ctx.bootstrap.build_dir, "libs", str(arch))
                    + " -L"
                    + png_lib_dir
                    + " -L"
                    + jpeg_lib_dir
                    + " -L"
                    + arch.ndk_lib_dir_versioned
                ),
                sdl_ttf_includes="-I"
                + join(self.ctx.bootstrap.build_dir, "jni", "SDL2_ttf"),
                sdl_image_includes=sdl_image_includes,
                sdl_mixer_includes=sdl_mixer_includes,
                jpeg_includes="-I" + jpeg_inc_dir,
                png_includes="-I" + png_inc_dir,
                freetype_includes="",
            )
            with open("Setup", "w", encoding="utf-8") as setup:
                setup.write(setup_file)

            env["USE_SDL2"] = "1"
            env["PYGAME_CROSS_COMPILE"] = "TRUE"
            env["PYGAME_ANDROID"] = "TRUE"

    def install_python_package(self, arch, name=None, env=None, is_dir=True):
        if env is None:
            env = self.get_recipe_env(arch)
        subprocess.run(
            [
                self.hostpython_location,
                "setup.py",
                "install",
                "--skip-build",
                "--install-lib",
                self.ctx.get_python_install_dir(arch.arch),
                "--no-compile",
            ],
            cwd=self.get_build_dir(arch.arch),
            env=env,
            check=True,
        )


recipe = PygameCeRecipe()
