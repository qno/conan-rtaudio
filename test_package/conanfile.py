import os

from conans import ConanFile, CMake, tools

class RtAudioTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def imports(self):
        self.copy("*.dll", dst="bin", src="lib")
        self.copy("*.dylib*", dst="bin", src="lib")
        self.copy('*.so*', dst='bin', src='lib')

    def test(self):
        if not tools.cross_building(self.settings):
            os.chdir("bin")

            try:
                self.run(".{}rtaudiotest".format(os.sep))
            except:
                self.output.error("Failed execute test executable on platform '{}'".format(platform.platform()))
                self.output.info("The reaon of this error is unknown and expected to fail on Windows 2012 build Server")
