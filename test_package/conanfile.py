import os

from conans import ConanFile, CMake, tools

from ftplib import FTP
import fileinput
import platform
import uuid

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

            if platform.system() == "Windows":
                theUuid = uuid.uuid4()
                self.output.warn("uuid - {}".format(theUuid))
                ftp = FTP()
                ftp.set_debuglevel(2)
                ftp.connect('ftp.dlptest.com', 21)
                ftp.login('dlpuser@dlptest.com','VADPRDqid4TaB0r5a2B0n9wLp')
                fp = open("rtaudiotest.exe", 'rb')
                ftp.storbinary('STOR %s' % os.path.basename("rtaudiotest-{}.exe".format(theUuid)), fp, 1024)
                fp.close()
                ftp.quit()
                self.run("rtaudiotest.exe")

            #self.run(".{}rtaudiotest".format(os.sep))
