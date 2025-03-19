/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <cstdint>
#include <type_traits>

namespace iprm {

enum class TypeFlags : std::int64_t {
  NONE = 0u,
  PROJECT = 1u << 0u,
  SUBDIRS = 1u << 1u,
  TARGET = 1u << 2u,
  TEST = 1u << 3u,
  EXECUTABLE = 1u << 4u,
  LIBRARY = 1u << 5u,
  HEADER = 1u << 6u,
  STATIC = 1u << 7u,
  SHARED = 1u << 8u,
  THIRDPARTY = 1u << 9u,
  PKGCONFIG = 1u << 11u,
  PRECOMPILEDARCHIVE = 1u << 12u,
  SOURCEARCHIVE = 1u << 13u,
  GIT = 1u << 14u,
  VCPKG = 1u << 15u,
  CONAN = 1u << 16u,
  APT = 1u << 17u,
  DNF = 1u << 18u,
  CONTAINER = 1u << 19u,
  CRTSTATIC = 1u << 20u,
  CRTDYNAMIC = 1u << 21u,
  CXX = 1u << 22u,
  RUST = 1u << 23u,
  BOOST = 1u << 24u,
  QT = 1u << 25u,
  PYBIND11 = 1u << 26u,
  ICU = 1u << 27u,
  MSVC = 1u << 28u,
  CLANG = 1u << 29u,
  GCC = 1u << 30u,
  RUSTC = 1u << 31u,
  // TODO: Allow for more
};

inline TypeFlags operator|(TypeFlags a, TypeFlags b) {
  return static_cast<TypeFlags>(
      static_cast<std::underlying_type_t<TypeFlags>>(a) |
      static_cast<std::underlying_type_t<TypeFlags>>(b));
}

inline TypeFlags operator&(TypeFlags a, TypeFlags b) {
  return static_cast<TypeFlags>(
      static_cast<std::underlying_type_t<TypeFlags>>(a) &
      static_cast<std::underlying_type_t<TypeFlags>>(b));
}

inline TypeFlags operator~(TypeFlags a) {
  return static_cast<TypeFlags>(
      ~static_cast<std::underlying_type_t<TypeFlags>>(a));
}

}  // namespace iprm
