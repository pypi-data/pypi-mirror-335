/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "object.hpp"
#include "session.hpp"

#include <pybind11/pybind11.h>

#include <filesystem>

namespace iprm {
void Object::rename(const std::string& new_name) {
  Session::register_rename(new_name, shared_from_this());
}

bool Object::is_type(TypeFlags type_flags) const {
  return static_cast<bool>(this->type_flags() & type_flags);
}

bool Object::is_project() const {
  return is_type(TypeFlags::PROJECT);
}
bool Object::is_subdirectories() const {
  return is_type(TypeFlags::SUBDIRS);
}

bool Object::is_target() const {
  return is_type(TypeFlags::TARGET);
}

bool Object::is_test() const {
  return is_type(TypeFlags::TEST);
}

bool Object::is_executable() const {
  return is_type(TypeFlags::EXECUTABLE);
}

bool Object::is_library() const {
  return is_type(TypeFlags::LIBRARY);
}

bool Object::is_header() const {
  return is_type(TypeFlags::HEADER);
}

bool Object::is_static_library() const {
  return is_type(TypeFlags::STATIC);
}

bool Object::is_shared_library() const {
  return is_type(TypeFlags::SHARED);
}

bool Object::is_third_party() const {
  return is_type(TypeFlags::THIRDPARTY);
}

bool Object::is_pkgconfig() const {
  return is_type(TypeFlags::PKGCONFIG);
}

bool Object::is_precompiled_archive() const {
  return is_type(TypeFlags::PRECOMPILEDARCHIVE);
}

bool Object::is_source_archive() const {
  return is_type(TypeFlags::SOURCEARCHIVE);
}

bool Object::is_git() const {
  return is_type(TypeFlags::GIT);
}

bool Object::is_vcpkg() const {
  return is_type(TypeFlags::VCPKG);
}

bool Object::is_conan() const {
  return is_type(TypeFlags::CONAN);
}

bool Object::is_apt() const {
  return is_type(TypeFlags::APT);
}

bool Object::is_dnf() const {
  return is_type(TypeFlags::DNF);
}

bool Object::is_container() const {
  return is_type(TypeFlags::CONTAINER);
}

bool Object::is_static_crt() const {
  return is_type(TypeFlags::CRTSTATIC);
}

bool Object::is_dynamic_crt() const {
  return is_type(TypeFlags::CRTDYNAMIC);
}

bool Object::is_cxx() const {
  return is_type(TypeFlags::CXX);
}

bool Object::is_rust() const {
  return is_type(TypeFlags::RUST);
}

bool Object::is_boost() const {
  return is_type(TypeFlags::BOOST);
}

bool Object::is_qt() const {
  return is_type(TypeFlags::QT);
}

bool Object::is_pybind11() const {
  return is_type(TypeFlags::PYBIND11);
}

bool Object::is_icu() const {
  return is_type(TypeFlags::ICU);
}

}  // namespace iprm
