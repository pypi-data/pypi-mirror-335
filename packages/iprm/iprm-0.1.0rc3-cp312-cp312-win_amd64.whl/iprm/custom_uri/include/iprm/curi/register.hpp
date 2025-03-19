/*
* Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <filesystem>
#include <string>

namespace iprm::curi {

bool register_uri_scheme(const std::string& scheme,
                         const std::filesystem::path& executable);

}  // namespace iprm::curi
