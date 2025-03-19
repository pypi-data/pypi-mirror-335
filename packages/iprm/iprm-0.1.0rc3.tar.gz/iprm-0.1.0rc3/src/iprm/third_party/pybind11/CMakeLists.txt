include(FetchContent)
FetchContent_Declare(
        pybind11
        GIT_REPOSITORY https://github.com/pybind/pybind11.git
        GIT_TAG v2.13.6
)
FetchContent_MakeAvailable(pybind11)

add_library(tp_pybind11 INTERFACE)
target_link_libraries(tp_pybind11 INTERFACE pybind11::pybind11)
target_compile_definitions(tp_pybind11 INTERFACE 
    PYBIND11_VERSION_MAJOR=${pybind11_VERSION_MAJOR}
    PYBIND11_VERSION_MINOR=${pybind11_VERSION_MINOR}
)
