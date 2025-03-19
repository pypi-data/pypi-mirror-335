if (NOT WIN32)
    set(CMAKE_AUTOMOC ON)
    set(CMAKE_AUTORCC ON)
endif()

if (APPLE)
    add_executable(iprm_studio MACOSX_BUNDLE)
    set_target_properties(iprm_studio PROPERTIES
            MACOSX_BUNDLE_INFO_PLIST "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist"
    )

    find_package(Python3 COMPONENTS Interpreter REQUIRED)
    set(IPRM_ICON_OUTPUT_FILE "${CMAKE_CURRENT_SOURCE_DIR}/res/logos/icon.icns")
    set(IPRM_ICON_INPUT_FILE "${CMAKE_CURRENT_SOURCE_DIR}/res/logos/iprm_icon.svg")
    add_custom_command(
            OUTPUT ${IPRM_ICON_OUTPUT_FILE}
            COMMAND
                ${Python3_EXECUTABLE} "${CMAKE_CURRENT_SOURCE_DIR}/res/logos/make_macos_icon.py"
            WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}/res/logos"
            DEPENDS ${IPRM_ICON_INPUT_FILE}
            COMMENT "Generating IPRM icon.icns file"
    )
    add_custom_target(iprm_macosx_icon_generation DEPENDS ${IPRM_ICON_OUTPUT_FILE})

    add_dependencies(iprm_studio iprm_macosx_icon_generation)

    set(IPRM_MACOSX_ICON "${CMAKE_CURRENT_SOURCE_DIR}/res/logos/icon.icns")
    set_source_files_properties(
        ${IPRM_MACOSX_ICON}
            PROPERTIES
                MACOSX_PACKAGE_LOCATION "Resources"
    )
    target_sources(iprm_studio PRIVATE ${IPRM_MACOSX_ICON})


    set(IPRM_APP_BUNDLE_DIR "${CMAKE_CURRENT_SOURCE_DIR}/bin/iprm_studio.app")

    add_custom_command(TARGET iprm_studio POST_BUILD
            # NOTE: CMake should be doing this automatically, and I've had it do it automatically for me before,
            # but maybe the custom output location here has exposed a CMake bug. If I can isolate further I'll report it
            COMMAND ${CMAKE_COMMAND} -E copy
                "${CMAKE_CURRENT_SOURCE_DIR}/Info.plist"
                ${IPRM_APP_BUNDLE_DIR}/Contents/Info.plist
            COMMENT "Copying Info.plist to app bundle"

            # NOTE: Required for the custom URI to actually be registered/acknowledged by browsers on macOS
            # NOTE: Execute `open "/System/Library/CoreServices/Applications/Keychain Access.app"`
            # (Apple has apparently hidden the app away in latest macOS versions)
            # TODO: Before IPRM official public releases need to be signed with a certificate from a CA. Can fallback to
            #   self-signed here for local dev. Maybe we can use LetsEncrypt? Hopefully their isn't a large cost
            COMMAND
                codesign -s "$ENV{IPRM_SIGNING_IDENTITY}" -f --deep ${IPRM_APP_BUNDLE_DIR}
            COMMENT "Self-signing the IPRM Studio application bundle"
    )
else()
    add_executable(iprm_studio)
endif()


# TODO: Instead of splitting things into models/views folder, create folders for each major view.
#   E.g. src/dependencygraph/*.<h|c>pp. That way files can be smaller and more concise.

target_sources(iprm_studio
      PRIVATE
      "${CMAKE_CURRENT_SOURCE_DIR}/src/apibridge.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/apierror.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/assetcache.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/mainwindow.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/splashscreen.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/models/filesystem.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/models/objects.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/dependencygraph.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/project.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/file.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/filesystem.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/loadingwidget.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/log.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/nativetext.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/cmaketext.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/mesontext.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/textstyle.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/objects.hpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/apibridge.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/assetcache.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/mainwindow.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/splashscreen.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/models/filesystem.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/models/objects.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/dependencygraph.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/project.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/file.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/filesystem.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/loadingwidget.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/log.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/nativetext.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/cmaketext.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/mesontext.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/textstyle.cpp"
      "${CMAKE_CURRENT_SOURCE_DIR}/src/views/objects.cpp"
)
target_sources(iprm_studio
      PRIVATE
      "${CMAKE_CURRENT_SOURCE_DIR}/res/res.qrc"
)

set_target_properties(iprm_studio
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        LIBRARY_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}/bin"
        ARCHIVE_OUTPUT_DIRECTORY
        "${CMAKE_CURRENT_SOURCE_DIR}/bin"
)

find_package(Python 3.12 COMPONENTS Interpreter Development REQUIRED)
target_link_libraries(iprm_studio
    PUBLIC
        tp_lemon
        tp_qt
        tp_pybind11
        tp_K-Editor_md
        Python::Python
        lib_curi
        lib_gv
)
add_dependencies(iprm_studio core)
target_compile_definitions(iprm_studio
    PRIVATE
        QT_NO_KEYWORDS
)

if (WIN32)
    set_target_properties(iprm_studio
        PROPERTIES
            WIN32_EXECUTABLE TRUE
    )
    target_link_options(iprm_studio PRIVATE
        "/SUBSYSTEM:WINDOWS"
        "/ENTRY:mainCRTStartup"
    )

    add_custom_command(TARGET iprm_studio
          POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_directory
          ${CMAKE_BINARY_DIR}/third_party/qt/Archive/plugins
          $<TARGET_FILE_DIR:iprm_studio>/plugins
    )

    # TODO: Get this method of including Qt working in regular API tests before using in IPRM, so all the kinks have been
    #	worked out, as our manual solution is fine enough for now
    #[===[
    add_executable(iprm_studio)
    target_sources(iprm_studio
            PRIVATE
            "${CMAKE_CURRENT_SOURCE_DIR}/src/apibridge.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/apierror.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/mainwindow.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/splashscreen.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/models/filesystem.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/models/objects.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/dependencygraph.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/files.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/filesystem.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/loadingwidget.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/log.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/nativetext.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/cmaketext.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/textstyle.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/objects.hpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/apibridge.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/main.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/mainwindow.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/splashscreen.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/models/filesystem.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/models/objects.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/dependencygraph.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/files.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/filesystem.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/loadingwidget.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/log.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/nativetext.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/cmaketext.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/textstyle.cpp"
            "${CMAKE_CURRENT_SOURCE_DIR}/src/views/objects.cpp"
    )

    set_target_properties(iprm_studio PROPERTIES
            MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL"
    )

    target_link_libraries(iprm_studio
            PUBLIC
            tp_lemon
            tp_graphviz
            tp_qt
            tp_pybind11
            tp_K-Editor_md
    )

    target_compile_definitions(iprm_studio
            PRIVATE
            QT_NO_KEYWORDS
    )

    add_custom_command(TARGET iprm_studio
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            $<TARGET_RUNTIME_DLLS:iprm_studio>
            $<TARGET_FILE_DIR:iprm_studio>
            COMMAND_EXPAND_LISTS
    )

    find_program(WINDEPLOYQT_EXECUTABLE
            NAMES windeployqt6 windeployqt
            HINTS ${QT_BIN_DIR}
            REQUIRED
    )

    target_compile_definitions(iprm_studio
            PUBLIC
            QT_NO_KEYWORDS
    )

    set_target_properties(iprm_studio
            PROPERTIES
            OUTPUT_NAME
            iprm_studio
            RUNTIME_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_SOURCE_DIR}/."
            LIBRARY_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_SOURCE_DIR}/."
            ARCHIVE_OUTPUT_DIRECTORY
            "${CMAKE_CURRENT_SOURCE_DIR}/."
    )

    add_custom_command(TARGET iprm_studio
            POST_BUILD
            COMMAND ${WINDEPLOYQT_EXECUTABLE}
            --verbose 0
            --no-translations
            --no-compiler-runtime
            --plugindir=$<TARGET_FILE_DIR:iprm_studio>/plugins
            --dir $<TARGET_FILE_DIR:iprm_studio>
            $<TARGET_FILE:iprm_studio>
            COMMENT "Running windeployqt for iprm_studio"
            COMMAND_EXPAND_LISTS
    )
    ]===]

    get_target_property(target_sources iprm_studio SOURCES)
    foreach (source ${target_sources})
        if (source MATCHES "\.(h|hpp)$")
            get_filename_component(directory ${source} DIRECTORY)
            get_filename_component(filename ${source} NAME_WE)
            get_filename_component(ext ${source} EXT)
            file(RELATIVE_PATH rel_directory ${CMAKE_CURRENT_SOURCE_DIR} ${directory})
            set(moc_output "${CMAKE_CURRENT_BINARY_DIR}/${rel_directory}/moc_${filename}.cpp")
            set(moc_includes "$<LIST:TRANSFORM,$<TARGET_PROPERTY:iprm_studio,INTERFACE_INCLUDE_DIRECTORIES>,PREPEND,-I>")
            add_custom_command(
                    OUTPUT ${moc_output}
                    COMMAND ${CMAKE_BINARY_DIR}/third_party/qt/Archive/bin/moc.exe
                    ${moc_includes}
                    "${directory}/${filename}${ext}"
                    -o ${moc_output}
                    DEPENDS
                    ${source} tp_qt_unpack_qt_archive
                    COMMAND_EXPAND_LISTS
            )
            target_sources(iprm_studio PRIVATE ${moc_output})
        endif ()
    endforeach ()

    get_target_property(target_sources iprm_studio SOURCES)
    foreach (source ${target_sources})
        if (source MATCHES "\.qrc$")
            get_filename_component(directory ${source} DIRECTORY)
            get_filename_component(filename ${source} NAME_WE)
            get_filename_component(ext ${source} EXT)
            file(RELATIVE_PATH rel_directory ${CMAKE_CURRENT_SOURCE_DIR} ${directory})
            set(rcc_output "${CMAKE_CURRENT_BINARY_DIR}/${rel_directory}/qrc_${filename}.cpp")
            add_custom_command(
                    OUTPUT ${rcc_output}
                    COMMAND ${CMAKE_BINARY_DIR}/third_party/qt/Archive/bin/rcc.exe
                    --name ${filename}
                    "${directory}/${filename}${ext}"
                    -o ${rcc_output}
                    DEPENDS
                    ${source} tp_qt_unpack_qt_archive
            )
            target_sources(iprm_studio PRIVATE ${rcc_output})
        endif ()
    endforeach ()


    add_custom_command(TARGET iprm_studio
    POST_BUILD
          COMMAND ${CMAKE_COMMAND} -E copy_directory
        ${CMAKE_BINARY_DIR}/third_party/qt/Archive/plugins
        $<TARGET_FILE_DIR:iprm_studio>/plugins
          COMMAND ${CMAKE_COMMAND} -E copy_if_different
          $<TARGET_RUNTIME_DLLS:iprm_studio>
          $<TARGET_FILE_DIR:iprm_studio>

          COMMAND_EXPAND_LISTS
    )

    set_target_properties(iprm_studio PROPERTIES
            MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL"
    )
    set(graphviz_config6_file "${CMAKE_BINARY_DIR}/third_party/graphviz/Archive/bin/config6")
    add_custom_command(TARGET iprm_studio
            POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy
            ${graphviz_config6_file}
            $<TARGET_FILE_DIR:iprm_studio>
    )
endif()