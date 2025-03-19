add_library(lib_curi)
target_sources(lib_curi
    PUBLIC
        "${CMAKE_CURRENT_SOURCE_DIR}/include/iprm/curi/open.hpp"
        "${CMAKE_CURRENT_SOURCE_DIR}/include/iprm/curi/register.hpp"
)

if (APPLE)
    target_sources(lib_curi
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/src/open_mac.mm"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/register_mac.mm"
    )
    find_library(FOUNDATION Foundation)
    find_library(CORESERVICES CoreServices)
    find_library(APPKIT AppKit)
    target_link_libraries(lib_curi
        PRIVATE
            ${FOUNDATION}
            ${CORESERVICES}
            ${APPKIT}
    )
elseif(WIN32)
    target_sources(lib_curi
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/src/open_win.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/register_win.cpp"
    )
elseif(UNIX AND NOT APPLE)
    find_program(XDG_MIME xdg-mime)
    find_program(XDG_OPEN xdg-open)
    if(NOT XDG_MIME OR NOT XDG_OPEN)
        message(FATAL_ERROR "Please install xdg-utils package.")
    endif()
    find_package(Qt6 REQUIRED COMPONENTS Core)

    target_sources(lib_curi
        PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/src/open_linux.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/register_linux.cpp"
    )
    target_link_libraries(lib_curi
        PRIVATE
            Qt6::Core
    )
endif()

target_include_directories(lib_curi
    PUBLIC
        ${CMAKE_CURRENT_SOURCE_DIR}/include
)
