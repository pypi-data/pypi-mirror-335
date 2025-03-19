set(archive_output_files
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QCodeEditor.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QFramedTextAttribute.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QHighlightBlockRule.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QHighlightRule.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QLanguage.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QLineNumberArea.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QStyleSyntaxHighlighter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QSyntaxStyle.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/completers/QPythonCompleter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/highlighters/QPythonHighlighter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/resources/qcodeeditor_resources.qrc
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QCodeEditor.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QFramedTextAttribute.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QLanguage.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QLineNumberArea.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QStyleSyntaxHighlighter.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QSyntaxStyle.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/completers/QPythonCompleter.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/highlighters/QPythonHighlighter.cpp
)

set(tp_K-Editor_md_generated_sources
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QCodeEditor.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QFramedTextAttribute.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QHighlightBlockRule.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QHighlightRule.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QLanguage.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QLineNumberArea.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QStyleSyntaxHighlighter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/QSyntaxStyle.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/completers/QPythonCompleter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public/highlighters/QPythonHighlighter.hpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/resources/qcodeeditor_resources.qrc
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QCodeEditor.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QFramedTextAttribute.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QLanguage.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QLineNumberArea.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QStyleSyntaxHighlighter.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/QSyntaxStyle.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/completers/QPythonCompleter.cpp
    ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/src/highlighters/QPythonHighlighter.cpp
)

set(extract_dir "${CMAKE_CURRENT_BINARY_DIR}/Archive")
set(archive_file "${CMAKE_CURRENT_SOURCE_DIR}/src/K-Editor.tar.gz")

# Single custom command to extract and patch the archive
add_custom_command(
    OUTPUT ${archive_output_files}
    DEPENDS ${archive_file}
    COMMAND ${CMAKE_COMMAND} -E make_directory ${extract_dir}
    COMMAND ${CMAKE_COMMAND} -E tar xzf ${archive_file}
    COMMENT "Unpacking ${archive_file} to ${extract_dir}"
    COMMAND git apply "${CMAKE_CURRENT_SOURCE_DIR}/initial_iprm_modifications.patch"
    COMMENT "Patching 'initial_iprm_modifications.patch' to ${extract_dir}"
    WORKING_DIRECTORY ${extract_dir}
    VERBATIM
    COMMAND_EXPAND_LISTS
)

# Create the unpack target that depends directly on the output files
add_custom_target(tp_K-Editor_md_unpack_archive DEPENDS ${archive_output_files})

# Configure Qt build settings
if(NOT WIN32)
    set(CMAKE_AUTOMOC ON)
else()
    set(CMAKE_AUTOMOC OFF) # Handled manually for Windows
endif()

# Disable AUTORCC - we'll handle RCC manually for consistency
set(CMAKE_AUTORCC OFF)

# Create the object library
add_library(tp_K-Editor_md_objects OBJECT)
target_sources(tp_K-Editor_md_objects
    PRIVATE
        ${tp_K-Editor_md_generated_sources}
)
set_source_files_properties(${tp_K-Editor_md_generated_sources}
    PROPERTIES GENERATED TRUE
)

# Establish dependencies
add_dependencies(tp_K-Editor_md_objects tp_K-Editor_md_unpack_archive)

# Configure include directories
target_include_directories(tp_K-Editor_md_objects
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public
        ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/.
)

# Link dependencies
target_link_libraries(tp_K-Editor_md_objects
    PUBLIC
        tp_qt
)

# Create the final static library
add_library(tp_K-Editor_md STATIC)

# Handle Qt's MOC and RCC
if(WIN32)
    # Handle MOC for Windows
    get_target_property(target_sources tp_K-Editor_md_objects SOURCES)
    foreach(source ${target_sources})
        if(source MATCHES "\.(h|hpp)$")
            get_filename_component(directory ${source} DIRECTORY)
            get_filename_component(filename ${source} NAME_WE)
            get_filename_component(ext ${source} EXT)
            file(RELATIVE_PATH rel_directory ${CMAKE_CURRENT_SOURCE_DIR} ${directory})
            set(moc_output "${CMAKE_CURRENT_BINARY_DIR}/${rel_directory}/moc_${filename}.cpp")
            set(moc_includes "$<LIST:TRANSFORM,$<TARGET_PROPERTY:tp_K-Editor_md_objects,INTERFACE_INCLUDE_DIRECTORIES>,PREPEND,-I>")
            add_custom_command(
                OUTPUT ${moc_output}
                COMMAND ${CMAKE_BINARY_DIR}/third_party/qt/Archive/bin/moc.exe
                    ${moc_includes}
                    "${directory}/${filename}${ext}"
                    -o ${moc_output}
                DEPENDS
                    ${source} tp_qt_unpack_qt_archive tp_K-Editor_md_unpack_archive
                COMMAND_EXPAND_LISTS
            )
            target_sources(tp_K-Editor_md_objects PRIVATE ${moc_output})
        endif()
    endforeach()
endif()
# Handle RCC for all platforms
get_target_property(target_sources tp_K-Editor_md_objects SOURCES)
foreach(source ${target_sources})
    if(source MATCHES "\.qrc$")
        get_filename_component(directory ${source} DIRECTORY)
        get_filename_component(filename ${source} NAME_WE)
        get_filename_component(ext ${source} EXT)
        file(RELATIVE_PATH rel_directory ${CMAKE_CURRENT_SOURCE_DIR} ${directory})
        
        if(WIN32)
            set(rcc_output "${CMAKE_CURRENT_BINARY_DIR}/${rel_directory}/qrc_${filename}.cpp")
            add_custom_command(
                OUTPUT ${rcc_output}
                COMMAND ${CMAKE_BINARY_DIR}/third_party/qt/Archive/bin/rcc.exe
                    --name ${filename}
                    "${directory}/${filename}${ext}"
                    -o ${rcc_output}
                DEPENDS
                    ${source} tp_qt_unpack_qt_archive tp_K-Editor_md_unpack_archive
            )
        else()
            # For non-Windows platforms
            set(rcc_output "${CMAKE_CURRENT_BINARY_DIR}/${rel_directory}/qrc_${filename}.cpp")
            
            # Find Qt6 properly
            if(NOT TARGET Qt6::rcc)
                find_package(Qt6 COMPONENTS Core REQUIRED)
            endif()
            
            add_custom_command(
                OUTPUT ${rcc_output}
                COMMAND Qt6::rcc
                    --name ${filename}
                    "${directory}/${filename}${ext}"
                    -o ${rcc_output}
                DEPENDS
                    ${source} tp_K-Editor_md_unpack_archive
            )
        endif()
        
        target_sources(tp_K-Editor_md_objects PRIVATE ${rcc_output})
    endif()
endforeach()

# Windows-specific settings
if(WIN32)
    set_target_properties(tp_K-Editor_md PROPERTIES
        MSVC_RUNTIME_LIBRARY "MultiThreaded$<$<CONFIG:Debug>:Debug>DLL"
    )
endif()

# Configure the static library
target_sources(tp_K-Editor_md
    PRIVATE
        $<TARGET_OBJECTS:tp_K-Editor_md_objects>
)

target_link_libraries(tp_K-Editor_md
    PUBLIC
        tp_qt
)

add_dependencies(tp_K-Editor_md tp_K-Editor_md_objects)

target_include_directories(tp_K-Editor_md
    PUBLIC
        ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/public
        ${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/.
)
