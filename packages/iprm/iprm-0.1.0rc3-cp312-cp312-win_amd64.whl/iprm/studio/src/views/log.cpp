/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "log.hpp"
#include <QOperatingSystemVersion>
#include <QTemporaryFile>
#include <QTextStream>

namespace iprm::views {

Log::Log(const QDir& root_dir, QWidget* parent)
    : QPlainTextEdit(parent),
      root_dir_(root_dir),
      default_working_dir_(root_dir) {
  setReadOnly(true);

  // Set monospace font
  QFont font("Consolas, Monaco, monospace");
  font.setStyleHint(QFont::Monospace);
  setFont(font);

  setup_process();
}

Log::~Log() {
  if (process_) {
    process_->kill();
    delete process_;
  }
}

void Log::setup_process() {
  process_ = new QProcess(this);
  process_->setWorkingDirectory(default_working_dir_.absolutePath());

  connect(process_, &QProcess::readyReadStandardOutput, this,
          &Log::handle_stdout);
  connect(process_, &QProcess::readyReadStandardError, this,
          &Log::handle_stderr);
  connect(process_, &QProcess::started, this,
          [this]() { Q_EMIT process_started(current_command_); });
  connect(process_, &QProcess::finished, this, &Log::handle_process_finished);
  connect(
      process_, &QProcess::errorOccurred, this,
      [this](QProcess::ProcessError error) { Q_EMIT process_error(error); });
}

void Log::log(const QString& text, const Type type) {
  append_to_log(text, type);
}

void Log::log_api_error(const APIError& error) {
  log(error.message, Type::Error);
}

void Log::start_logging_section(const QString& title) {
  append_to_log(
      QString("\n%1\n%2\n%1\n").arg(QString("=").repeated(50)).arg(title),
      Type::Section);
}

void Log::handle_stdout() {
  QByteArray data = process_->readAllStandardOutput();
  append_to_log(QString::fromUtf8(data), Type::Normal);
}

void Log::handle_stderr() {
  QByteArray data = process_->readAllStandardError();
  append_to_log(QString::fromUtf8(data), Type::Error);
}

void Log::handle_process_finished(int exit_code,
                                  QProcess::ExitStatus exit_status) {
  process_->setWorkingDirectory(default_working_dir_.absolutePath());
  Q_EMIT process_finished(exit_code, exit_status);
}

void Log::append_to_log(const QString& text, const Type type) {
  QTextCursor cursor = textCursor();
  cursor.movePosition(QTextCursor::End);

  QString processed_text = text;
  processed_text.replace("\\n", "\n");
  if (!processed_text.endsWith('\n')) {
    processed_text += '\n';
  }
  QTextCharFormat format;
  switch (type) {
    case Type::Error: {
      format.setForeground(QColor("#FF3B30"));
      break;
    }
    case Type::Section: {
      format.setForeground(QColor("#4A9EFF"));
      break;
    }
    case Type::Success: {
      format.setForeground(QColor("#34C759"));
      break;
    }
    case Type::Normal:
    default: {
      break;
    }
  }

  cursor.insertText(processed_text, format);
  setTextCursor(cursor);
}

void Log::clear_log() {
  clear();
}

void Log::run_command(const QString& program,
                      const QStringList& arguments,
                      const QString& working_dir) {
  current_command_ = QString("%1 %2").arg(program, arguments.join(' '));

  if (!working_dir.isEmpty()) {
    append_to_log(
        QString("Changing working directory to: %1\n").arg(working_dir),
        Type::Normal);
    process_->setWorkingDirectory(working_dir);
  }

  if (QOperatingSystemVersion::currentType() ==
          QOperatingSystemVersion::Windows &&
      program.toLower() == "cmake") {
    run_cmake_windows(arguments);
  } else {
    process_->start(program, arguments);
  }
}

void Log::run_cmake_windows(const QStringList& cmake_args) {
  // Try to locate vcvarsall.bat
  QStringList possible_vs_paths;
  QString program_files_64 = QString::fromLocal8Bit(qgetenv("ProgramFiles"));
  QString program_files_32 =
      QString::fromLocal8Bit(qgetenv("ProgramFiles(x86)"));

  if (program_files_64.isEmpty())
    program_files_64 = "C:\\Program Files";
  if (program_files_32.isEmpty())
    program_files_32 = "C:\\Program Files (x86)";

  // Check VS2022
  QStringList editions = {"Enterprise", "Professional", "Community"};
  for (const auto& edition : editions) {
    possible_vs_paths << QString(
                             "%1/Microsoft Visual "
                             "Studio/2022/%2/VC/Auxiliary/Build/vcvarsall.bat")
                             .arg(program_files_64, edition);
  }

  // Check VS2019 and VS2017
  QStringList versions = {"2019", "2017"};
  for (const auto& ver : versions) {
    for (const auto& edition : editions) {
      possible_vs_paths << QString(
                               "%1/Microsoft Visual "
                               "Studio/%2/%3/VC/Auxiliary/Build/vcvarsall.bat")
                               .arg(program_files_32, ver, edition);
    }
  }

  QString vcvarsall_path;
  for (const auto& path : possible_vs_paths) {
    if (QFile::exists(path)) {
      vcvarsall_path = path;
      break;
    }
  }

  if (vcvarsall_path.isEmpty()) {
    append_to_log("Could not find Visual Studio vcvarsall.bat\n", Type::Error);
    return;
  }

  // Create temporary batch file
  QTemporaryFile batch_file(QString("%0/%1").arg(
      QDir::tempPath(), "iprm_cmake_configure_XXXXXX.bat"));
  batch_file.setAutoRemove(false);
  if (!batch_file.open()) {
    append_to_log("Failed to create temporary batch file\n", Type::Error);
    return;
  }

  QTextStream stream(&batch_file);
  stream << "@echo off\n"
         << "call \"" << vcvarsall_path << "\" x64\n"
         << "echo Setting up Visual Studio environment...\n"
         << "cmake " << cmake_args.join(' ') << "\n";

  batch_file.close();

  append_to_log(
      QString("Using Visual Studio environment from: %1\n").arg(vcvarsall_path),
      Type::Normal);
  process_->start("cmd.exe", {"/C", batch_file.fileName()});

  // Schedule cleanup
  connect(process_, &QProcess::finished, this,
          [fileName = batch_file.fileName()]() { QFile::remove(fileName); });
}

}  // namespace iprm::views
