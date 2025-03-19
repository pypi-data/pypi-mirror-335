/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "project.hpp"
#include <QFile>
#include <QFileInfo>
#include <QLabel>
#include <QPainter>
#include <QSvgRenderer>
#include <QVBoxLayout>
#include <complex>
#include <filesystem>
#include "cmaketext.hpp"
#include "file.hpp"
#include "mesontext.hpp"
#include "objects.hpp"

namespace iprm::views {

Project::Project(QWidget* parent) : QTabWidget(parent) {
  setTabPosition(QTabWidget::TabPosition::North);
  setMovable(true);
  setTabsClosable(true);
  connect(this, &Project::tabCloseRequested, this,
          &Project::on_file_tab_closed);
}

void Project::update(
    const QDir& root_dir,
    const std::unordered_map<std::string, std::vector<ObjectNode>>& objects) {
  project_dir_ = root_dir;
  while (count() > 0) {
    auto file_node = qobject_cast<File*>(widget(0));
    removeTab(0);
    file_node->deleteLater();
  }
  open_files_.clear();
  project_objects_ = objects;
}

void Project::add_file(const models::FileNode& file_node) {
  std::visit(overloaded{[](const models::Folder&) {
                          // Ignore Folders
                        },
                        [this](const models::NativeFile& n) {
                          (void)add_native(n.path);
                        },
                        [this](const models::CMakeFile& n) { add_cmake(n); },
                        [this](const models::MesonFile& n) { add_meson(n); }},
             file_node);
}

File* Project::add_native(const std::filesystem::path& file_path) {
  auto file_node_itr = open_files_.find(file_path);
  if (file_node_itr != open_files_.end()) {
    File* file_node = file_node_itr.value();
    setCurrentWidget(file_node);
    return file_node;
  }
  auto path = file_path.generic_string();
  auto file_path_str = QString::fromStdString(path);
  QFile native_file(file_path_str);
  if (!native_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return nullptr;
  }

  const auto file_objects_itr = project_objects_.find(file_path.string());
  const auto file_objects = (file_objects_itr != project_objects_.end())
                                ? file_objects_itr->second
                                : std::vector<ObjectNode>{};
  QFileInfo native_info(native_file.fileName());
  const QString native_file_name = native_info.fileName();
  const QString proj_relative_dir_path =
      project_dir_.relativeFilePath(native_info.absoluteDir().path());
  const QString native_file_contents = native_file.readAll();
  auto native_node = new File(native_file_name, proj_relative_dir_path,
                              native_file_contents, file_objects, this);

  const QString tab_display =
      QString("%0 (%1)").arg(native_file_name, proj_relative_dir_path);
  const int tab_index =
      addTab(native_node,
             QString("%0 (%1)").arg(native_file_name, proj_relative_dir_path));
  tabBar()->setTabData(tab_index, native_info.filePath());
  setCurrentIndex(tab_index);
  setTabToolTip(tab_index, tab_display);
  open_files_[file_path] = native_node;
  return native_node;
}

void Project::add_cmake(const models::CMakeFile& file_node) {
  auto path = file_node.path.generic_string();
  auto file_path_str = QString::fromStdString(path);
  QFile cmake_file(file_path_str);
  if (!cmake_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return;
  }
  auto native_node_itr = open_files_.find(file_node.native_path);
  if (native_node_itr != open_files_.end()) {
    File* native_node = native_node_itr.value();
    native_node->show_cmake(cmake_file.readAll());
    setCurrentWidget(native_node);
  } else {
    if (File* native_node = add_native(file_node.native_path)) {
      native_node->show_cmake(cmake_file.readAll());
      setCurrentWidget(native_node);
    }
  }
}

void Project::add_meson(const models::MesonFile& file_node) {
  auto path = file_node.path.generic_string();
  auto file_path_str = QString::fromStdString(path);
  QFile meson_file(file_path_str);
  if (!meson_file.open(QIODevice::ReadOnly | QIODevice::Text)) {
    return;
  }
  auto native_node_itr = open_files_.find(file_node.native_path);
  if (native_node_itr != open_files_.end()) {
    File* native_node = native_node_itr.value();
    native_node->show_meson(meson_file.readAll());
    setCurrentWidget(native_node);
  } else {
    if (File* native_node = add_native(file_node.native_path)) {
      native_node->show_meson(meson_file.readAll());
      setCurrentWidget(native_node);
    }
  }
}

void Project::on_file_tab_closed(const int tab_index) {
  const auto native_file_path = std::filesystem::path(
      tabBar()->tabData(tab_index).toString().toStdString());
  auto file_node = qobject_cast<File*>(widget(tab_index));
  removeTab(tab_index);
  file_node->deleteLater();
  open_files_.remove(native_file_path);
  Q_EMIT file_closed(static_cast<int>(open_files_.size()));
}

}  // namespace iprm::views
