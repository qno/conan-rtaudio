from conans import ConanFile, CMake, AutoToolsBuildEnvironment, tools
from conans.errors import ConanInvalidConfiguration
import platform

class RtAudioConan(ConanFile):
    name = "RtAudio"
    version = "master"
    license = "MIT"
    author = "Gary P. Scavone"
    url = "https://github.com/qno/conan-rtaudio"
    description = "A set of C++ classes that provide a common API for realtime audio input/output across Linux (native ALSA, JACK, PulseAudio and OSS), Macintosh OS X (CoreAudio and JACK), and Windows (DirectSound, ASIO, and WASAPI) operating systems."

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    options = {"shared": [True, False]}
    default_options = "shared=False"

    _rtaudio_pkg_name = "rtaudio"
    _rtaudio_libname = "rtaudio"

    scm = {
         "type": "git",
         "subfolder": _rtaudio_libname,
         "url": "https://github.com/thestk/rtaudio",
         "revision": "master"
      }

    def build(self):
        if self._isVisualStudioBuild():
            cmake = CMake(self)
            cmake.definitions["BUILD_TESTING"] = "False"
            cmake.configure(source_dir=self._rtaudio_pkg_name)
            cmake.build()
        else:
            self.run("cd {} && sh autogen.sh --no-configure && cd ..".format(self._rtaudio_pkg_name))
            autotools = AutoToolsBuildEnvironment(self)
            autotools.configure(configure_dir=self._rtaudio_pkg_name)
            autotools.make()
            autotools.install()

    def package(self):
        self.copy("RtAudio.h", dst="include", src=self._rtaudio_pkg_name)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="lib", keep_path=False)
        self.copy("*.so", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        libs = [self._rtaudio_libname]
        if self._isVisualStudioBuild():
            libs.append("{}_static".format(self._rtaudio_libname))

        self.cpp_info.libs = libs

    def _isVisualStudioBuild(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"
