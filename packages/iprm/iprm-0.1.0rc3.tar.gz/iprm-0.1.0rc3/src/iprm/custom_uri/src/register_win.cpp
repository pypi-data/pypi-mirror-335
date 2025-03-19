/*
* Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <iprm/curi/register.hpp>

#include <Windows.h>

namespace iprm::curi {

bool register_uri_scheme(const std::string& scheme,
                         const std::filesystem::path& executable) {
  if (scheme.empty() || executable.empty()) {
    return false;
  }

  // Only 7-bit ASCII schemes are supported
  std::wstring scheme_wide;
  for (char c : scheme) {
    scheme_wide.push_back(static_cast<wchar_t>(c));
  }

  // Construct registry paths
  std::wstring keyPath = L"Software\\Classes\\" + scheme_wide;
  std::wstring urlDecl = L"URL:" + scheme_wide;
  std::wstring cmdPath = keyPath + L"\\shell\\open\\command";

  // Open or create the main key
  HKEY hKey;
  LSTATUS status =
      RegCreateKeyExW(HKEY_CURRENT_USER, keyPath.c_str(), 0, nullptr, 0,
                      KEY_ALL_ACCESS, nullptr, &hKey, nullptr);
  if (status != ERROR_SUCCESS) {
    return false;
  }

  // Set URL Protocol values
  status = RegSetValueExW(hKey, L"URL Protocol", 0, REG_SZ,
                          reinterpret_cast<const BYTE*>(L""), sizeof(wchar_t));
  if (status != ERROR_SUCCESS) {
    RegCloseKey(hKey);
    return false;
  }

  status = RegSetValueExW(hKey, nullptr, 0, REG_SZ,
                          reinterpret_cast<const BYTE*>(urlDecl.c_str()),
                          (urlDecl.length() + 1) * sizeof(wchar_t));
  if (status != ERROR_SUCCESS) {
    RegCloseKey(hKey);
    return false;
  }

  // Close the main key
  RegCloseKey(hKey);

  // Open or create the command key
  status = RegCreateKeyExW(HKEY_CURRENT_USER, cmdPath.c_str(), 0, nullptr, 0,
                           KEY_ALL_ACCESS, nullptr, &hKey, nullptr);
  if (status != ERROR_SUCCESS) {
    return false;
  }

  // Construct the command string manually
  std::wstring command = L"\"";
  command += executable.wstring();
  command += L"\"";
  command += L"\"%1\"";

  // Set the command to execute
  status = RegSetValueExW(hKey, nullptr, 0, REG_SZ,
                          reinterpret_cast<const BYTE*>(command.c_str()),
                          (command.length() + 1) * sizeof(wchar_t));
  if (status != ERROR_SUCCESS) {
    RegCloseKey(hKey);
    return false;
  }

  // Close the command key
  RegCloseKey(hKey);
  return true;
}

}  // namespace iprm::curi
