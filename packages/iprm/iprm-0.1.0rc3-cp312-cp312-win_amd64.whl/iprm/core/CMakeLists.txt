set(PYBIND11_PYTHON_VERSION 3.12)
pybind11_add_module(core
    src/bindings.cpp
    src/typeflags.hpp
    src/object.hpp
    src/object.cpp
    src/session.hpp
    src/session.cpp
)

set_target_properties(core
   PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}"
        LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}"
        ARCHIVE_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}"
)
