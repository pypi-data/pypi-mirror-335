/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <pybind11/pybind11.h>
#include "typeflags.hpp"

#include <memory>
#include <string>
#include <vector>

namespace iprm {
class Object : public std::enable_shared_from_this<Object> {
 public:
  Object(std::string name) : name_(std::move(name)) {}

  virtual ~Object() = default;

  const std::string& name() const { return name_; }
  void set_name(const std::string& name) { name_ = name; }

  TypeFlags type_flags() const { return type_flags_; }
  void set_type_flags(TypeFlags type_flags) { type_flags_ = type_flags; }

  const std::vector<std::string>& dependencies() const { return dependencies_; }

  void set_dependencies(const std::vector<std::string>& dependencies) {
    dependencies_ = dependencies;
  }

  const std::string& hex_colour() const { return hex_colour_; }

  void set_hex_colour(const std::string& hex_colour) {
    hex_colour_ = hex_colour;
  }

  const std::string& shape_type() const { return shape_type_; }

  void set_shape_type(const std::string& shape_type) {
    shape_type_ = shape_type;
  }

  // Registers the rename with the Session, so we don't lose track of the
  // objects state, given other objects may we to look up any object in the
  // session to help with its generation
  void rename(const std::string& new_name);

  bool is_type(TypeFlags type_flags) const;

  bool is_project() const;

  bool is_subdirectories() const;

  bool is_target() const;

  bool is_test() const;

  bool is_executable() const;

  bool is_library() const;

  bool is_header() const;

  bool is_static_library() const;

  bool is_shared_library() const;

  bool is_third_party() const;

  bool is_pkgconfig() const;

  bool is_precompiled_archive() const;

  bool is_source_archive() const;

  bool is_git() const;

  bool is_vcpkg() const;

  bool is_conan() const;

  bool is_apt() const;

  bool is_dnf() const;

  bool is_container() const;

  bool is_static_crt() const;

  bool is_dynamic_crt() const;

  bool is_cxx() const;

  bool is_rust() const;

  bool is_boost() const;

  bool is_qt() const;

  bool is_pybind11() const;

  bool is_icu() const;

 private:
  std::string name_;
  TypeFlags type_flags_{TypeFlags::NONE};
  std::vector<std::string> dependencies_;
  std::string hex_colour_{"#212121"};
  std::string shape_type_{"rectangle"};
};
}  // namespace iprm
