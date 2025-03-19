/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "../apibridge.hpp"
#include "../models/filesystem.hpp"
#include "../models/objects.hpp"

#include <QFileInfo>
#include <QHash>
#include <QItemSelection>
#include <QTabWidget>

class QTabWidget;

namespace iprm::views {

class File;

class Project : public QTabWidget {
  Q_OBJECT

 public:
  Project(QWidget* parent = nullptr);

  void update(
      const QDir& root_dir,
      const std::unordered_map<std::string, std::vector<ObjectNode>>& objects);

  void add_file(const models::FileNode& file_node);

 Q_SIGNALS:
  void file_closed(const int num_files_opened);

 private Q_SLOTS:
  void on_file_tab_closed(const int tab_index);

 private:
  QDir project_dir_;

  File* add_native(const std::filesystem::path& file_path);
  void add_cmake(const models::CMakeFile& file_node);
  void add_meson(const models::MesonFile& file_node);

  QHash<std::filesystem::path, File*> open_files_;
  std::unordered_map<std::string, std::vector<ObjectNode>> project_objects_;
};

}  // namespace iprm::views
