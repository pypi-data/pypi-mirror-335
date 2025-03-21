# pylint: skip-file
# Setuptools
from setuptools import Extension, find_packages, setup
from setuptools.command.build_ext import build_ext
from setuptools.errors import OptionError, SetupError

# Other
import subprocess
import pybind11
import os

# Conan
from conan.api.conan_api import ConanAPI
from conan.api.model import Remote
from conan.cli.printers import print_profiles
from conan.cli.printers.graph import print_graph_packages, print_graph_basic
from conan.cli import make_abs_path
from conans.util.files import save
from conan.api.output import ConanOutput


# -------------------------------------------------------------
# Extension class
# -------------------------------------------------------------


class ConanCMakeExtension(Extension):
    def __init__(self, name, build_type="Release"):
        super().__init__(name, sources=[])
        if build_type not in ["Debug", "Release"]:
            raise OptionError(f"Extension build_type should be Debug or Release (Got {build_type}")
        self.build_type = build_type


class ConanCMakeBuildExtension(build_ext):
    def run(self):
        for ext in self.extensions:
            if not isinstance(ext, ConanCMakeExtension):
                raise SetupError("Extension is not ConanCMakeExtension")
            self._build(ext)

    # Some code here come from https://stackoverflow.com/questions/42585210/extending-setuptools-extension-to-use-cmake-in-setup-py
    def _build(self, ext: ConanCMakeExtension):
        ## Create a new home directory for conan
        ## And a new profile
        cache_folder = None
        # cache_folder = "/tmp/conan_home"

        api = ConanAPI(cache_folder)
        remotes = api.remotes.list()
        if "lrde-public" not in (x.name for x in remotes):
            remotes.insert(
                0,
                Remote(
                    "lrde-public",
                    "https://artifactory.lrde.epita.fr/artifactory/api/conan/lrde-public",
                ),
            )

        cwd = os.getcwd()

        conanfile_path = api.local.get_conanfile_path(".", cwd, py=True)
        default_profile = api.profiles.detect()
        default_profile.settings["compiler.cppstd"] = 20
        default_profile.settings["compiler.libcxx"] = "libstdc++11"
        default_profile.settings["build_type"] = f"{ext.build_type}"
        # https://blog.conan.io/2023/10/03/backup-sources-feature.html (thanks https://github.com/conan-io/conan-center-index/issues/25712)
        api.config.global_conf.update(
            "core.sources:download_urls",
            ["origin", "https://c3i.jfrog.io/artifactory/conan-center-backup-sources/"],
        )

        profile_pathname = api.profiles.get_path("default", cwd, exists=False)

        contents = default_profile.dumps()
        ConanOutput().warning("This profile is a guess of your environment, please check it.")
        if default_profile.settings.get("os") == "Macos":
            ConanOutput().warning("Defaulted to cppstd='gnu17' for apple-clang.")
        ConanOutput().warning(
            "The output of this command is not guaranteed to be stable and can " "change in future Conan versions."
        )
        ConanOutput().warning("Use your own profile files for stability.")
        ConanOutput().success(f"Saving detected profile to {profile_pathname}")
        save(profile_pathname, contents)

        args = {
            "profile_build": None,
            "profile_host": None,
            "settings_build": None,
            "settings_host": None,
            "options_build": None,
            "options_host": None,
            "conf_build": None,
            "conf_host": None,
        }
        args = type("Arg", (object,), args)
        host_profile, build_profile = api.profiles.get_profiles_from_args(args)
        print_profiles(host_profile, build_profile)

        deps_graph = api.graph.load_graph_consumer(
            conanfile_path,
            None,
            None,
            None,
            None,
            profile_host=host_profile,
            profile_build=build_profile,
            lockfile=None,
            remotes=remotes,
            update=None,
        )

        print_graph_basic(deps_graph)

        deps_graph.report_graph_error()
        force = int(
            os.environ.get("PYLENA_FORCE_BUILD_FROM_SOURCES", 0)
        )  # Hack to force rebuild from sources (setup.py build --force)
        build_mode = "*" if (force or self.force) else "missing"
        api.graph.analyze_binaries(deps_graph, [build_mode], remotes=remotes, update=None, lockfile=None)
        print_graph_packages(deps_graph)

        ## Install binaries
        out = ConanOutput()
        api.install.install_binaries(deps_graph=deps_graph, remotes=remotes)

        out.title("Finalizing install (deploy, generators)")
        libname = self.get_ext_fullpath(ext.name)
        installdir = os.path.dirname(make_abs_path(libname))
        source_folder = os.path.dirname(conanfile_path)
        output_folder = cwd
        api.install.install_consumer(
            deps_graph=deps_graph,
            generators=None,
            output_folder=output_folder,
            source_folder=source_folder,
        )

        ## Invoke CMake
        cmake_variables = {
            "CMAKE_POLICY_DEFAULT_CMP0148": "OLD",
            "pybind11_DIR": pybind11.get_cmake_dir(),
            "CMAKE_INSTALL_RPATH_USE_LINK_PATH": "ON",  # Install with full path, these paths will be fixed by auditwheel
        }
        if "PYTHON_EXECUTABLE" in os.environ:
            cmake_variables["PYTHON_EXECUTABLE"] = os.environ["PYTHON_EXECUTABLE"]

        options = ["-D{k}={v}".format(k=k, v=v) for (k, v) in cmake_variables.items()]

        subprocess.run(
            [
                "cmake",
                "-S",
                ".",
                "-B",
                "build",
                "--preset",
                f"conan-{ext.build_type.lower()}",
            ]
            + options,
            cwd=cwd,
            check=True,
        )
        subprocess.run(["cmake", "--build", "build"], cwd=cwd, check=True)
        subprocess.run(["cmake", "--install", "build", "--prefix", installdir], cwd=cwd, check=True)


# -------------------------------------------------------------
# Setup
# -------------------------------------------------------------

setup(
    cmdclass={"build_ext": ConanCMakeBuildExtension},
    ext_modules=[ConanCMakeExtension("pylena/pylena_cxx")],
    platforms=["linux"],
    packages=find_packages(exclude=["tests", "doc"]),
)
