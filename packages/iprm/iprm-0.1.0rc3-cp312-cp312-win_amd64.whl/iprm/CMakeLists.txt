cmake_minimum_required(VERSION 3.23)

# TODO: Become self-hosted and use IPRM itself to build
#  IPRM, instead of being hardcoded to use CMake
project(iprm
    VERSION
        0.0.1
    LANGUAGES
        C CXX
)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED True)

if(MSVC)
    add_compile_options(/Zc:__cplusplus /permissive-)
endif()

# TODO: Once Studio becomes stable enough on all platforms, it can be built by default
option(IPRM_BUILD_STUDIO "Build IPRM Studio" OFF)
option(IPRM_BUILD_REMOTE "Build IPRM Remote Web Worker" OFF)

add_subdirectory(third_party)
add_subdirectory(core)
# TODO: Use in the remote web worker infra (NOTE: Might not be needed if we just use Google OAuth 2.0, as we can use
#   local HTTP web server in that case
add_subdirectory(custom_uri)

if(IPRM_BUILD_STUDIO)
    add_subdirectory(graphviz)
    add_subdirectory(studio)
endif()

# TODO: Infrastructure for the remote worker that allows for builds on other platforms,
#   will house the web server (done via QtHttpServer) as well as the custom gRPC-based
#   protobuf API that sends data back and forth between the actual worker. Long term goal
#   is one could bind from any machine and package up the resulting binaries even if their
#   host is not the correct one
if(IPRM_BUILD_REMOTE)
    add_subdirectory(web)
    add_subdirectory(worker)
endif()
