/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <iprm/curi/open.hpp>

#include <Windows.h>

namespace iprm::curi {

bool open_uri(const std::string& uri) {
  auto result = reinterpret_cast<INT_PTR>(ShellExecuteA(
      nullptr, nullptr, uri.c_str(), nullptr, nullptr, SW_SHOWNORMAL));
  return result > 32;
}

}  // namespace iprm::curi
