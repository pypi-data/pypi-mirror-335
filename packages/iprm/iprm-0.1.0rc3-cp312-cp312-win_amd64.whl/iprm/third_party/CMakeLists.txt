add_subdirectory(lemon)
add_subdirectory(pybind11)

if(IPRM_BUILD_STUDIO)
    add_subdirectory(graphviz)
    add_subdirectory(K-Editor)

    # TODO: Don't hard code the macOS Qt install, just like windows, create a PLATFORM-macos
    #  section with a precompiled portion, only contained the Qt modules we need (Core, GUi, Widgets,
    #  and Svg) to keep the git LFS light
    #-DCMAKE_PREFIX_PATH="~/qt/6.8.2/macos/lib/cmake/Qt6"
    # Linux can just use system libs via pkgconfig
    add_subdirectory(qt)
endif()
