/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "apibridge.hpp"
#include "models/filesystem.hpp"

#include <QDir>
#include <QDockWidget>
#include <QLabel>
#include <QMainWindow>
#include <QProcess>
#include <QProgressBar>
#include <QStackedWidget>
#include <QStatusBar>
#include <QString>
#include <QTimer>
#include <QToolBar>

namespace iprm {

namespace models {
class FileSystem;
}  // namespace models

namespace views {
class FileSystem;
class DependencyView;
class Log;
class Project;
class LoadingWidget;
}  // namespace views

class Object;

class MainWindow : public QMainWindow {
  Q_OBJECT

 public:
  MainWindow(APIBridgeThread& api_bridge);

  void set_project(const QDir& project_dir) { project_dir_ = project_dir; }
  void load_project(const QDir& project_dir);

 public Q_SLOTS:
  void on_project_load_failed(const APIError& error) const;
  void on_project_loaded();

 private Q_SLOTS:
  void on_dep_graph_layout_failed(const QString& platform) const;

  // TODO: genreaize thing so arbitrary amount of built in generators and
  //  plugin generators can easily be built up and use the state reporting
  //  infra with out duplication
  void on_cmake_generated() const;
  void on_meson_generated() const;

  void on_print_stdout(const QString& message) const;

  void on_file_activated(const models::FileNode& file_node) const;
  void on_file_modified(bool modified) const;
  void save_current_file();
  void save_file_as();

  void new_project();
  void open_project();

  void run_cmake_generate();
  void run_cmake_configure() const;
  void run_cmake_build() const;
  void run_cmake_test() const;
  void run_meson_generate();
  void run_meson_configure() const;
  void run_meson_build() const;
  void run_meson_test() const;
  void handle_process_started(const QString& command) const;
  void handle_process_finished(int exit_code, QProcess::ExitStatus exit_status);
  void handle_process_error(QProcess::ProcessError error);

  void on_scons_import();

  void on_msbuild_import();

 protected:
  void closeEvent(QCloseEvent* event) override;

 private:
  void create_actions();
  void create_menu_bar() const;
  void create_tool_bar();
  void disable_actions() const;
  void enable_actions() const;
  void setup_ui();
  void setup_api_bridge();

  APIBridgeThread& api_bridge_;

  QDir project_dir_;
  bool project_loaded_{false};
  QString file_filter_;

  views::Log* log_view_{nullptr};
  QDockWidget* log_dock_{nullptr};

  views::Project* proj_view_{nullptr};

  models::FileSystem* fs_model_{nullptr};
  views::FileSystem* fs_view_{nullptr};
  QDockWidget* fs_dock_{nullptr};

  views::DependencyView* dep_view_{nullptr};
  QDockWidget* dep_dock_{nullptr};

  QStatusBar* status_bar_{nullptr};
  QLabel* status_label_{nullptr};
  QProgressBar* progress_bar_{nullptr};

  QStackedWidget* stack_{nullptr};
  QStackedWidget* proj_file_view_{nullptr};
  QWidget* no_file_view_{nullptr};

  QWidget* no_proj_view_{nullptr};
  views::LoadingWidget* loading_proj_view_{nullptr};
  QWidget* loading_proj_failed_view_{nullptr};

  QAction* save_action_{nullptr};
  QAction* save_as_action_{nullptr};

  QAction* new_action_{nullptr};
  QAction* open_action_{nullptr};

// TODO: For all these actions, just make them regular tools buttons with a
//  popup dialog, where said dialog is a QStackedWidget for each action we
//  support. For example, the generate dialog will have a check box to say
//  "re-generate", and configure and build, and test will allow for all the
//  options exposed that the CLI supports, as we'll be directly invoking the
//  IPRM CLI here now instead of building up the commands ourselves

// TODO: Have a single global clean toolbutton that launches a dialog and
//  allows you to selection from all the available generators to clean the files

  // TODO: add clean command that removes all generated files and the binary dir
  QAction* cmake_generate_action_{nullptr};
  QAction* cmake_configure_action_{nullptr};
  QAction* cmake_build_action_{nullptr};
  QAction* cmake_test_action_{nullptr};

  // TODO: add clean command that removes all generated files and the binary dir
  QAction* meson_generate_action_{nullptr};
  QAction* meson_configure_action_{nullptr};
  QAction* meson_build_action_{nullptr};
  QAction* meson_test_action_{nullptr};

  // TODO: Make these generators as well
  QAction* scons_generate_action_{nullptr};
  QAction* msbuild_generate_action_{nullptr};
};

}  // namespace iprm
