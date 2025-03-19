add_library(tp_graphviz INTERFACE)

if (WIN32)
	function(add_framework_shared_module target_name implib dll archive_name)
		add_library(${target_name} SHARED IMPORTED GLOBAL)

		file(MAKE_DIRECTORY "${include}")

		set_target_properties(${target_name}
			PROPERTIES
				IMPORTED_IMPLIB "${implib}"
				IMPORTED_LOCATION "${dll}"
				INTERFACE_INCLUDE_DIRECTORIES "${CMAKE_CURRENT_BINARY_DIR}/Archive/include"
		)
		add_dependencies(${target_name}
			${archive_name}
		)
	endfunction(add_framework_shared_module)

	set(archive_output_files
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cdt.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cgraph.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvc.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_core.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_dot_layout.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/xdot.lib"
	)

	target_link_libraries(tp_graphviz
		INTERFACE
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_gvc_release>
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_cgraph_release>
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_cdt_release>
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_xdot_release>
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_gvplugin_core_release>
			$<$<OR:$<CONFIG:Release>,$<CONFIG:RelWithDebInfo>,$<CONFIG:MinSizeRel>>:tp_graphviz_gvplugin_dot_layout_release>
			$<$<CONFIG:Debug>:tp_graphviz_gvc_debug>
			$<$<CONFIG:Debug>:tp_graphviz_cgraph_debug>
			$<$<CONFIG:Debug>:tp_graphviz_cdt_debug>
			$<$<CONFIG:Debug>:tp_graphviz_xdot_debug>
			$<$<CONFIG:Debug>:tp_graphviz_gvplugin_core_debug>
			$<$<CONFIG:Debug>:tp_graphviz_gvplugin_dot_layout_debug>
	)
	target_include_directories(tp_graphviz
		INTERFACE
			"${CMAKE_CURRENT_BINARY_DIR}/Archive/include"
	)

	add_framework_shared_module(tp_graphviz_gvc_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvc.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvc.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_gvc_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvc.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvc.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_cgraph_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cgraph.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/cgraph.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_cgraph_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cgraph.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/cgraph.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_cdt_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cdt.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/cdt.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_cdt_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/cdt.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/cdt.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_xdot_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/xdot.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/xdot.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_xdot_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/xdot.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/xdot.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_gvplugin_core_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_core.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvplugin_core.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_gvplugin_core_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_core.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvplugin_core.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_gvplugin_dot_layout_release
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_dot_layout.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvplugin_dot_layout.dll"
		tp_graphviz_unpack_archive
	)

	add_framework_shared_module(tp_graphviz_gvplugin_dot_layout_debug
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/lib/gvplugin_dot_layout.lib"
		"${CMAKE_CURRENT_BINARY_DIR}/Archive/bin/gvplugin_dot_layout.dll"
		tp_graphviz_unpack_archive
	)

	set(extract_dir "${CMAKE_CURRENT_BINARY_DIR}/Archive")
	set(archive_file "${CMAKE_CURRENT_SOURCE_DIR}/PLATFORM-win64/graphviz_12.2.1.zip")
	set(sentinel_file ${extract_dir}/tp_graphviz_unpack_archive_unpack_archive.sentinel)

	add_custom_command(
		OUTPUT
			${sentinel_file}
			${archive_output_files}
		DEPENDS ${archive_file}
		COMMAND ${CMAKE_COMMAND} -E make_directory ${extract_dir}
		COMMAND ${CMAKE_COMMAND} -E tar xz ${archive_file}
		COMMENT "Unpacking ${archive_file} to ${extract_dir}"
		COMMAND ${CMAKE_COMMAND} -E touch ${sentinel_file}
		WORKING_DIRECTORY ${extract_dir}
		VERBATIM
		COMMAND_EXPAND_LISTS
	)

	add_custom_target(tp_graphviz_unpack_archive DEPENDS ${sentinel_file})

	add_library(tp_graphviz_gvc INTERFACE)
	target_link_libraries(tp_graphviz_gvc
		INTERFACE
			tp_graphviz_gvc_release
			tp_graphviz_gvc_debug
	)

	add_library(tp_graphviz_cgraph INTERFACE)
	target_link_libraries(tp_graphviz_cgraph
		INTERFACE
			tp_graphviz_cgraph_release
			tp_graphviz_cgraph_debug
	)

	add_library(tp_graphviz_cdt INTERFACE)
	target_link_libraries(tp_graphviz_cdt
		INTERFACE
			tp_graphviz_cdt_release
			tp_graphviz_cdt_debug
	)

	add_library(tp_graphviz_xdot INTERFACE)
	target_link_libraries(tp_graphviz_xdot
		INTERFACE
			tp_graphviz_xdot_release
			tp_graphviz_xdot_debug
	)

	add_library(tp_graphviz_gvplugin_core INTERFACE)
	target_link_libraries(tp_graphviz_gvplugin_core
		INTERFACE
			tp_graphviz_gvplugin_core_release
			tp_graphviz_gvplugin_core_debug
	)

	add_library(tp_graphviz_gvplugin_dot_layout INTERFACE)
	target_link_libraries(tp_graphviz_gvplugin_dot_layout
		INTERFACE
			tp_graphviz_gvplugin_dot_layout_release
			tp_graphviz_gvplugin_dot_layout_debug
	)


else()
	find_package(PkgConfig REQUIRED)
	pkg_check_modules(GRAPHVIZ REQUIRED libgvc libcgraph)

	target_link_libraries(tp_graphviz INTERFACE ${GRAPHVIZ_LIBRARIES})
	target_include_directories(tp_graphviz INTERFACE ${GRAPHVIZ_INCLUDE_DIRS})
	target_link_directories(tp_graphviz INTERFACE ${GRAPHVIZ_LIBRARY_DIRS})
endif()
