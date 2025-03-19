/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <QProcess>
#include <iprm/curi/open.hpp>

namespace iprm::curi {

bool open_uri(const std::string& uri) {
  QProcess process;

  // Set process to not be bound to the parent's stdio
  process.setInputChannelMode(QProcess::InputChannelMode::ManagedInputChannel);
  process.closeReadChannel(QProcess::StandardOutput);
  process.closeReadChannel(QProcess::StandardError);

  // Start the process detached - this is equivalent to child.detach() in
  // boost::process
  bool success = QProcess::startDetached(
      "xdg-open", QStringList() << QString::fromStdString(uri));

  return success;
}

}  // namespace iprm::curi
