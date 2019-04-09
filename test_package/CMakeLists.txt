cmake_minimum_required (VERSION 3.5)
project (RtAudioTest)

include (${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()

add_executable (rtaudiotest rtaudiotest.cpp)
conan_target_link_libraries (rtaudiotest)
