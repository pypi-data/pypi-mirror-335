/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "apibridge.hpp"
#include <pybind11/embed.h>
#include <QList>
#include <QString>

#include <ranges>

namespace iprm {

APIError make_error(const QString& err_msg,
                    const pybind11::error_already_set& e) {
  const char* py_err_details = e.what();
  const QString err_details =
      QByteArray::fromRawData(py_err_details, std::strlen(py_err_details));
  return APIError(QString("%0: %1").arg(err_msg, err_details));
}

APIBridge::APIBridge(QObject* parent)
    : QObject(parent), dep_node_data_(dep_graph_) {
  qRegisterMetaType<APIError>();
}

void APIBridge::set_root_dir(const QDir& root_dir) {
  root_dir_ = root_dir;
}

void APIBridge::capture_io() {
  auto sys = py::module::import("sys");
  if (!sys) {
    Q_EMIT error(APIError("Failed to import sys module"));
    return;
  }

  py::module io = py::module::import("io");
  if (!io) {
    Q_EMIT error(APIError("Failed to import io module"));
    return;
  }

  py::module builtins = py::module::import("builtins");
  if (!builtins) {
    Q_EMIT error(APIError("Failed to import builtins module"));
    return;
  }

  py::cpp_function print([this, sys](py::args args, py::kwargs kwargs) {
    // TODO: Handle stderr so we log it as an error
    if (args.size() == 1) {
      Q_EMIT print_stdout(QString::fromStdString(args[0].cast<std::string>()));
    }
  });
  builtins.attr("print") = print;
}

void APIBridge::init_sess() {
  destroy_sess();

  try {
    auto sys = py::module::import("sys");
    if (!sys) {
      Q_EMIT error(APIError("Failed to import sys module"));
      return;
    }

    auto platform_module = py::module::import("platform");
    if (!platform_module) {
      Q_EMIT error(APIError("Failed to import platform module"));
      return;
    }

    try {
      auto plat = platform_module.attr("system")().cast<std::string>();
      host_platform_ = QString::fromStdString(plat);
    } catch (const py::error_already_set& e) {
      Q_EMIT error(make_error("Failed to get current platform", e));
      return;
    }

    std::filesystem::path iprm_root(__FILE__);
    for (int i = 0; i < 4 && !iprm_root.parent_path().empty(); i++) {
      iprm_root = iprm_root.parent_path();
    }
    auto path_list = sys.attr("path").cast<py::list>();
    path_list.append(iprm_root.string());

    auto iprm_utl_env = py::module::import("iprm.util.env");
    if (!iprm_utl_env) {
      Q_EMIT error(APIError("Failed to import iprm.util.env module"));
      return;
    }

    // TODO: Use this for multi-platform calls (project file view and dep graph)
    /*
    py::list supported_platforms = iprm_utl_env.attr("PLATFORMS");
    for (const auto& platform : supported_platforms) {
      const auto plat = platform.cast<std::string>();
      supported_platforms_.append(QString::fromStdString(plat));
    }
    if (std::ranges::find(supported_platforms_, host_platform_) ==
        supported_platforms_.end()) {
      Q_EMIT error(APIError(
          QString("'%0' is not a supported platform").arg(host_platform_)));
      return;
    }
    */

    auto iprm_core_session = py::module::import("iprm.core.session");
    if (!iprm_core_session) {
      Q_EMIT error(APIError("Failed to import iprm.core.session module"));
      return;
    }

    std::string dir = root_dir_.absolutePath().toLatin1().data();
    // Create kwargs dict with default values matching CLI
    // py::dict kwargs;
    // kwargs["use_cache"] = true;  // Match CLI default behavior

    try {
      auto session_class = iprm_core_session.attr("Session");
      session_class.attr("create")(dir);
      sess_ = session_class;
    } catch (const py::error_already_set& e) {
      Q_EMIT error(make_error("Failed to create Session", e));
      return;
    }
  } catch (const py::error_already_set& e) {
    Q_EMIT error(make_error("Error during initialization", e));
  }
}

void APIBridge::destroy_sess() {
  if (!sess_.has_value()) {
    return;
  }
  if (native_loader_.has_value()) {
    native_loader_.value().release();
  }
  sess_.value().attr("destroy")();
  sess_.value().release();
  sess_.reset();
}

void APIBridge::load_project() {
  init_sess();
  if (!sess_.has_value()) {
    Q_EMIT error(APIError("APIBridge not initialized"));
    return;
  }

  auto iprm_load_native = py::module::import("iprm.load.native");
  if (!iprm_load_native) {
    Q_EMIT error(APIError("Failed to import iprm.load.native module"));
    return;
  }

  // TODO: create loaders for all supported platforms
  std::string dir = root_dir_.absolutePath().toLatin1().data();
  native_loader_ = iprm_load_native.attr("NativeLoader")(
      dir, host_platform_.toLatin1().data());
  if (!native_loader_) {
    Q_EMIT error(APIError("Failed to create NativeLoader instance"));
    return;
  }

  try {
    objs_.clear();
    [[maybe_unused]] py::dict py_objects =
        native_loader_.value().attr("load_project")();

    process_objects(py_objects);
    Q_EMIT project_load_success();
  } catch (const py::error_already_set& e) {
    Q_EMIT error(make_error("Error during project loading", e));
  }
}

void APIBridge::process_objects(const py::dict& py_objects) {
  dep_graph_.clear();
  target_map_.clear();
  // TODO: Need to reset this to load graphs in different contexts
  // dep_node_data_ = lemon::ListDigraph::NodeMap<ObjectNode>(
  //    dep_graph_);  // Reset the node map for the new graph

  // TODO: setup data for gui/main thread more efficiently here
  for (const auto& [key, value] : py_objects) {
    const auto file_path = key.cast<std::string>();
    py::list obj_list = value.cast<py::list>();
    std::vector<ObjectNode> objects;
    for (const auto& obj : obj_list) {
      const auto cpp_obj_name = obj.attr("name").cast<std::string>();
      const auto cpp_obj_type_name =
          obj.get_type().attr("__name__").cast<std::string>();
      const auto cpp_obj_type_flags =
          static_cast<TypeFlags>(obj.attr("type_flags").cast<std::uint64_t>());
      const py::list obj_dependencies = obj.attr("dependencies");
      std::vector<std::string> cpp_obj_dependencies;
      cpp_obj_dependencies.reserve(obj_dependencies.size());
      for (const auto& obj_dep : obj_dependencies) {
        cpp_obj_dependencies.push_back(py::cast<std::string>(obj_dep));
      }
      const auto obj_hex_colour = obj.attr("hex_colour").cast<std::string>();
      const auto cpp_obj_shape_type =
          obj.attr("shape_type").cast<std::string>();

      const auto obj_file_path =
          QDir::toNativeSeparators(QString::fromStdString(file_path));
      const auto obj_file_dir_path = QFileInfo(obj_file_path).absolutePath();
      const QString proj_relative_dir_path =
          root_dir_.relativeFilePath(obj_file_dir_path);

      objects.emplace_back(cpp_obj_name, cpp_obj_type_name, cpp_obj_type_flags,
                           cpp_obj_dependencies, obj_hex_colour,
                           cpp_obj_shape_type, proj_relative_dir_path);
      if (static_cast<bool>(cpp_obj_type_flags & TypeFlags::PROJECT)) {
        cxx_compiler_version_ = QString::fromStdString(
            obj.attr("cxx_compiler_version")().cast<std::string>());
        rust_compiler_version_ = QString::fromStdString(
            obj.attr("rust_compiler_version")().cast<std::string>());
      }
    }
    for (auto& obj : objects) {
      if (static_cast<bool>(obj.type & TypeFlags::CXX)) {
        obj.set_property("compiler_version", cxx_compiler_version_);
      } else if (static_cast<bool>(obj.type & TypeFlags::RUST)) {
        obj.set_property("compiler_version", rust_compiler_version_);
      }
    }
    objs_[file_path] = std::move(objects);
  }

  // Now build the graph exactly like Session does
  for (const auto& [file_path, objects] : objs_) {
    for (const auto& obj : objects) {
      if (static_cast<bool>(obj.type & TypeFlags::TARGET)) {
        auto node = dep_graph_.addNode();
        dep_node_data_[node] = obj;
        target_map_[obj.name] = node;
      }
    }
  }

  // Second pass: add dependencies
  for (const auto& [file_path, objects] : objs_) {
    for (const auto& obj : objects) {
      const auto is_target = static_cast<bool>(obj.type & TypeFlags::TARGET);
      if (auto deps = obj.dependencies; is_target) {
        for (const auto& dep : deps) {
          auto from_it = target_map_.find(obj.name);
          auto to_it = target_map_.find(dep);
          if (from_it != target_map_.end() && to_it != target_map_.end()) {
            dep_graph_.addArc(from_it->second, to_it->second);
          }
        }
      }
    }
  }
}

void APIBridge::generate(const std::string& generator_module,
                         const std::string& generator_class,
                         std::function<void()> notify_success) {
  // TODO: Fix up error handling to not assume all returned errors are project
  //  load failures
  if (!sess_.has_value() || !native_loader_.has_value()) {
    Q_EMIT error(APIError("APIBridge not initialized"));
    return;
  }

  auto iprm_gen_cmake = py::module::import(generator_module.c_str());
  if (!iprm_gen_cmake) {
    Q_EMIT error(APIError("Failed to import iprm.backend.cmake module"));
    return;
  }

  std::string dir = root_dir_.absolutePath().toLatin1().data();
  auto generator =
      iprm_gen_cmake.attr(generator_class.c_str())(native_loader_.value());
  if (!generator) {
    Q_EMIT error(APIError(QString("Failed to create '%0' instance")
                              .arg(QString::fromStdString(generator_class))));
    return;
  }

  try {
    (void)generator.attr("generate_project")();
    notify_success();
  } catch (const py::error_already_set& e) {
    Q_EMIT error(
        make_error(QString("Error during generating project files with '%0'")
                       .arg(QString::fromStdString(generator_class)),
                   e));
  }
}

void APIBridge::cmake_generate() {
  generate("iprm.backend.cmake", "CMake",
           [this]() { Q_EMIT cmake_generate_success(); });
}

void APIBridge::meson_generate() {
  generate("iprm.backend.meson", "Meson",
           [this]() { Q_EMIT meson_generate_success(); });
}

APIBridgeThread::APIBridgeThread() : QThread(nullptr), bridge_(), interp_() {
  bridge_.moveToThread(this);
  connect(&bridge_, &APIBridge::error, this, &APIBridgeThread::error);
  connect(&bridge_, &APIBridge::print_stdout, this,
          &APIBridgeThread::print_stdout);
  connect(&bridge_, &APIBridge::project_load_success, this,
          &APIBridgeThread::project_load_success);
  connect(&bridge_, &APIBridge::cmake_generate_success, this,
          &APIBridgeThread::cmake_generate_success);
  connect(&bridge_, &APIBridge::meson_generate_success, this,
          &APIBridgeThread::meson_generate_success);
}

void APIBridgeThread::set_root_dir(const QDir& root_dir) {
  bridge_.set_root_dir(root_dir);
}

void APIBridgeThread::capture_io() {
  py::gil_scoped_acquire acq;
  bridge_.capture_io();
}

void APIBridgeThread::destroy_sess() {
  py::gil_scoped_acquire acq;
  bridge_.destroy_sess();
}

void APIBridgeThread::load_project() {
  py::gil_scoped_acquire acq;
  bridge_.load_project();
}

void APIBridgeThread::cmake_generate() {
  py::gil_scoped_acquire acq;
  bridge_.cmake_generate();
}

void APIBridgeThread::meson_generate() {
  py::gil_scoped_acquire acq;
  bridge_.meson_generate();
}
}  // namespace iprm