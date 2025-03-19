add_library(lib_gv STATIC
    "${CMAKE_CURRENT_SOURCE_DIR}/include/iprm/gv/graphviz.hpp"
    "${CMAKE_CURRENT_SOURCE_DIR}/src/graphviz.cpp"
)
target_link_libraries(lib_gv
    PUBLIC
        tp_graphviz
)
target_include_directories(lib_gv
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
