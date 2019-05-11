from conans import ConanFile, CMake, tools
import re, os, platform

class RtAudioConan(ConanFile):
    name = "RtAudio"
    version = "5.1.0"
    license = "MIT"
    author = "Gary P. Scavone"
    homepage = "https://github.com/thestk/rtaudio"
    url = "https://github.com/qno/conan-rtaudio"
    description = "A set of C++ classes that provide a common API for realtime audio input/output across Linux (native ALSA, JACK, PulseAudio and OSS), Macintosh OS X (CoreAudio and JACK), and Windows (DirectSound, ASIO, and WASAPI) operating systems."

    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    options = {
        "shared": [True, False],
        "fPIC": [True, False]
        }
    default_options = {
        "shared": False,
         "fPIC": True
         }

    _pkg_name = "rtaudio-5.1.0"
    _libname = "rtaudio"

    def system_requirements(self):
        if tools.os_info.is_linux:
            if tools.os_info.with_apt:
                installer = tools.SystemPackageTool()
                if self.settings.arch == "x86" and tools.detected_architecture() == "x86_64":
                    arch_suffix = ':i386'
                    installer.install("g++-multilib")
                else:
                    arch_suffix = ''
                installer.install("{}{}".format("libasound2-dev", arch_suffix))
                installer.install("{}{}".format("libjack-dev", arch_suffix))
                installer.install("{}{}".format("libpulse-dev", arch_suffix))
            elif tools.os_info.with_yum:
                installer = tools.SystemPackageTool()
                if self.settings.arch == "x86" and tools.detected_architecture() == "x86_64":
                    arch_suffix = '.i686'
                else:
                    arch_suffix = ''
                installer.install("{}{}".format("alsa-lib-devel", arch_suffix))
                installer.install("{}{}".format("jack-audio-connection-kit-devel", arch_suffix))
                installer.install("{}{}".format("pulseaudio-libs-devel", arch_suffix))
            elif tools.os_info.with_pacman:
                if self.settings.arch == "x86" and tools.detected_architecture() == "x86_64":
                    # Note: The packages with the "lib32-" prefix will only be
                    # available if the user has activate Arch's multilib
                    # repository, See
                    # https://wiki.archlinux.org/index.php/official_repositories#multilib
                    arch_suffix = 'lib32-'
                else:
                    arch_suffix = ''
                installer = tools.SystemPackageTool()
                installer.install("{}{}".format(arch_suffix, "alsa-lib"))
                installer.install("{}{}".format(arch_suffix, "jack2"))
                installer.install("{}{}".format(arch_suffix, "libpulse"))
            else:
                self.output.warn("Could not determine package manager, skipping Linux system requirements installation.")

    def source(self):
        url = "http://www.music.mcgill.ca/~gary/rtaudio/release/{}.tar.gz".format(self._pkg_name)
        self.output.info("Downloading {}".format(url))
        tools.get(url)
        # the conan_basic_setup() must be called, otherwise the compiler runtime settings won't be setup correct,
        # which then leads then to linker errors if recipe e.g. is build with /MT runtime for MS compiler
        # see https://github.com/conan-io/conan/issues/3312
        self._patchCMakeListsFile(self._pkg_name)

    def configure(self):
        if self._isVisualStudioBuild():
            del self.options.fPIC

    def build(self):
        cmake = CMake(self)

        if self._isVisualStudioBuild() or self._isMinGWBuild():
            if self.settings.build_type == "Debug":
                cmake.definitions["CMAKE_DEBUG_POSTFIX"] = "d"

        if self._isVisualStudioBuild():
            cmake.definitions["RTAUDIO_BUILD_TESTING"] = "False"
            cmake.definitions["RTAUDIO_API_DS"] = "On"
            cmake.definitions["RTAUDIO_API_ASIO"] = "On"
            cmake.definitions["RTAUDIO_API_WASAPI"] = "On"

        if self.options.shared:
            cmake.definitions["RTAUDIO_BUILD_STATIC_LIBS"] = "False"
        else:
            cmake.definitions["RTAUDIO_BUILD_SHARED_LIBS"] = "False"

        cmake.definitions["RTAUDIO_BUILD_TESTING"] = "False"

        cmake.configure(source_dir=self._pkg_name)
        cmake.build()

    def package(self):
        self.copy("RtAudio.h", dst="include", src=self._pkg_name)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def package_info(self):
        release_libs = [self._libname]
        debug_libs = [self._libname]
        libs = []

        # Note: this must be correctly refined with options added for selecting
        # --with-jack --with-alsa --with-pulse --with-oss --with-core --with-asio --with-ds --with-wasapi
        if self.settings.os == "Linux":
            libs = ["pthread", "asound", "pulse-simple", "pulse", "jack"]

        if self.settings.os == "Macos":
            libs = ["pthread"]

            self.cpp_info.exelinkflags.append(" -framework CoreAudio -framework CoreFoundation")

        if self._isVisualStudioBuild() or self._isMinGWBuild():
            debug_libs = ["{}d".format(self._libname)]
            libs = ["dsound"]

        if self._isMinGWBuild():
            libs.extend(["ole32", "winmm", "ksuser", "mfplat", "mfuuid", "wmcodecdspuuid"])

        release_libs.extend(libs)
        debug_libs.extend(libs)

        self.cpp_info.release.libs = release_libs
        self.cpp_info.debug.libs = debug_libs

    def _isVisualStudioBuild(self):
        return self.settings.os == "Windows" and self.settings.compiler == "Visual Studio"

    def _isMinGWBuild(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def _patchCMakeListsFile(self, src_dir):
        cmake_project_line = ""
        cmake_file = "{}{}CMakeLists.txt".format(src_dir, os.sep)
        self.output.warn("patch '{}' to inject conanbuildinfo".format(cmake_file))
        for line in open(cmake_file, "r", encoding="utf8"):
            if re.match("^PROJECT.*\\(.*\\).*", line.strip().upper()):
                cmake_project_line = line.strip()
                self.output.warn("found cmake project declaration '{}'".format(cmake_project_line))
                break

        tools.replace_in_file(cmake_file, "{}".format(cmake_project_line),
                              '''{}
include(${{CMAKE_BINARY_DIR}}/conanbuildinfo.cmake)
conan_basic_setup()'''.format(cmake_project_line))

        self.output.warn("remove -Werror flag for Debug builds with gcc, otherwise CI builds will fail")
        tools.replace_in_file(cmake_file, "set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS} -Werror\")",
            "set(CMAKE_CXX_FLAGS \"${CMAKE_CXX_FLAGS}\")")

        if platform.platform().startswith("Windows-2012"):
            self.output.warn("set minimum required CMake version back to 3.7 on {} build server".format(platform.platform()))
            tools.replace_in_file(cmake_file, "cmake_minimum_required(VERSION 3.10 FATAL_ERROR)",
                "cmake_minimum_required(VERSION 3.7 FATAL_ERROR)")
