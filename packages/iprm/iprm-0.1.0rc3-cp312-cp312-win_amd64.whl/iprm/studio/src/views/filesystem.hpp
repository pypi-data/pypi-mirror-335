/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QTreeView>
#include <filesystem>

#include "../models/filesystem.hpp"

namespace iprm::views {

class FileSystem : public QTreeView {
  Q_OBJECT

 public:
  explicit FileSystem(QWidget* parent = nullptr);
  ~FileSystem() override;

  void select_file(const std::filesystem::path& file_path);

  void setModel(QAbstractItemModel* model) override;

 Q_SIGNALS:
  void file_activated(const models::FileNode& file_node);

 private Q_SLOTS:
  void on_activated(const QModelIndex& index);

 private:
  void setup_ui();
  QModelIndex find_index(const QModelIndex& parent_index,
                         const std::filesystem::path& target_path);

  models::FileSystem* fs_model_{nullptr};
};

}  // namespace iprm::views
