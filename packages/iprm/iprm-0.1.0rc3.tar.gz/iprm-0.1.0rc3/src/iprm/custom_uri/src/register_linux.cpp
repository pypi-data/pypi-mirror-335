/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <iprm/curi/register.hpp>

#include <QProcess>
#include <QString>
#include <QStringList>

#include <filesystem>
#include <fstream>

namespace fs = std::filesystem;

namespace iprm::curi {

bool register_uri_scheme(const std::string& scheme,
                         const std::filesystem::path& executable) {
  if (scheme.empty() || executable.empty()) {
    return false;
  }

  std::string desktop_file_contents;
  desktop_file_contents.append("[Desktop Entry]\n");
  desktop_file_contents.append("Name=CURI Echo\n");
  const std::string exec_line = "Exec=" + executable.string() + " %u\n";
  desktop_file_contents.append(exec_line);
  desktop_file_contents.append("Icon=\n");
  desktop_file_contents.append("Type=Application\n");
  desktop_file_contents.append("Terminal=false\n");
  desktop_file_contents.append("Categories=Utility;\n");
  const std::string mimetype = "x-scheme-handler/" + scheme;
  const std::string mimetype_line = "MimeType=" + mimetype + "\n";
  desktop_file_contents.append(mimetype_line);

  const std::string desktop_file_name = scheme + ".desktop";
  fs::path desktop_file_path = desktop_file_name;
  std::ofstream out_file(desktop_file_path);
  if (!out_file) {
    return false;
  }
  out_file << desktop_file_contents;
  out_file.close();

  fs::path symlink_path = fs::path(std::getenv("HOME")) /
                          ".local/share/applications/" /
                          desktop_file_path.string();

  fs::create_directories(symlink_path.parent_path());

  if (fs::exists(symlink_path)) {
    fs::remove(symlink_path);
  }
  fs::create_symlink(fs::absolute(desktop_file_path),
                     fs::absolute(symlink_path));

  // Use QProcess instead of boost::process to run xdg-mime
  QProcess process;

  // Create argument list
  QStringList arguments;
  arguments << "default"
            << QString::fromStdString(desktop_file_name)
            << QString::fromStdString(mimetype);

  // Start the process and wait for it to finish
  process.start("xdg-mime", arguments);

  // Wait for the process to finish
  if (!process.waitForFinished()) {
    return false;
  }

  // Check exit code
  return process.exitCode() == 0;
}

}  // namespace iprm::curi
