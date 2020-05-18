from conans import AutoToolsBuildEnvironment, ConanFile, MSBuild, tools
from conans.errors import ConanInvalidConfiguration
import os


class GoogleGuetzliConan(ConanFile):
    name = "google-guetzli"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://opensource.google/projects/guetzli"
    description = "Perceptual JPEG encoder"
    topics = "jpeg","compression"
    exports_sources = "patches/**"
    settings = "os", "compiler", "build_type", "arch"
    generators = "pkg_config"
    requires = ["libpng/1.6.37"]

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _is_msvc(self):
        return self.settings.compiler == "Visual Studio"

    def configure(self):
        if self.settings.os not in ["Linux", "Windows"]:
            raise ConanInvalidConfiguration("conan recipe for google-guetzli v{0} is not \
                available in {1}.".format(self.version, self.settings.os))

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = "guetzli-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _patch_sources(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)

    def build(self):
        self._patch_sources()
        if self._is_msvc:
            msbuild = MSBuild(self)
            with tools.chdir(self._source_subfolder):
                msbuild.build("guetzli.sln")
        else:
            autotools = AutoToolsBuildEnvironment(self)
            with tools.chdir(self._source_subfolder):
                env_vars = {"PKG_CONFIG_PATH": self.build_folder}
                env_vars.update(autotools.vars)
                with tools.environment_append(env_vars):
                    make_args = [
                        "config={}".format("debug" if self.settings.build_type == "Debug" else "release"),
                        "verbose=1',"
                    ]
                    autotools.make(args=make_args)
            
    def package(self):
        subdir = "Debug" if self.settings.build_type == "Debug" else "Release"
        if self._is_msvc:
            self.copy(os.path.join(self._source_subfolder, "bin, self.settings.arch, subdir, "guetzli.exe"), dst="bin", keep_path=False, )
        else:
            self.copy("{}/bin/{}/guetzli".format(self._source_subfolder, subdir), dst="bin", keep_path=False)
        self.copy("LICENSE", src=self._source_subfolder, dst="licenses")

    def package_info(self):
        bindir = os.path.join(self.package_folder, "bin")
        self.output.info("Appending PATH environment variable: {}".format(bindir))
        self.env_info.PATH.append(bindir)
