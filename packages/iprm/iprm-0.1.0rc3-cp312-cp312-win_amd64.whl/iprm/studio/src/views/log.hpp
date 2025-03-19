/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QDir>
#include <QPlainTextEdit>
#include <QProcess>
#include <QTextCursor>
#include "../apibridge.hpp"

namespace iprm::views {

class Log : public QPlainTextEdit {
  Q_OBJECT

 public:
  explicit Log(const QDir& root_dir, QWidget* parent = nullptr);
  ~Log();

  enum class Type {
    Normal,
    Section,
    Success,
    Error,
  };

  void log(const QString& text, const Type type = Type::Normal);
  void log_api_error(const APIError& error);
  void start_logging_section(const QString& title);
  void clear_log();
  void run_command(const QString& program,
                   const QStringList& arguments = QStringList(),
                   const QString& working_dir = QString());

 Q_SIGNALS:
  void process_started(const QString& command);
  void process_finished(int exit_code, QProcess::ExitStatus exit_status);
  void process_error(const QProcess::ProcessError error);

 private Q_SLOTS:
  void handle_stdout();
  void handle_stderr();
  void handle_process_finished(int exit_code, QProcess::ExitStatus exit_status);

 private:
  void append_to_log(const QString& text, const Type type);
  void run_cmake_windows(const QStringList& cmake_args);
  void setup_process();

 private:
  QDir root_dir_;
  QDir default_working_dir_;
  QString current_command_;
  QProcess* process_{nullptr};
};

}  // namespace iprm::views