/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "filesystem.hpp"
#include <QAbstractItemModel>

namespace iprm::views {

FileSystem::FileSystem(QWidget* parent) : QTreeView(parent) {
  setup_ui();
}

FileSystem::~FileSystem() = default;

void FileSystem::setup_ui() {
  setHeaderHidden(true);
  setAnimated(true);
  setAlternatingRowColors(true);
  setSelectionMode(QTreeView::SingleSelection);
  setSelectionBehavior(QTreeView::SelectRows);
  connect(this, &QTreeView::activated, this, &FileSystem::on_activated);
}

void FileSystem::setModel(QAbstractItemModel* model) {
  QTreeView::setModel(model);
  fs_model_ = qobject_cast<models::FileSystem*>(model);
  connect(model, &QAbstractItemModel::modelReset, this, &QTreeView::expandAll);
  expandAll();
}

void FileSystem::on_activated(const QModelIndex& index) {
  assert(fs_model_ != nullptr);
  Q_EMIT file_activated(fs_model_->get_file_node(index));
}

void FileSystem::select_file(const std::filesystem::path& file_path) {
  auto index = find_index(QModelIndex(), file_path);
  if (index.isValid()) {
    setCurrentIndex(index);
  }
}

QModelIndex FileSystem::find_index(const QModelIndex& parent_index,
                                   const std::filesystem::path& target_path) {
  if (!model()) {
    return QModelIndex();
  }

  const int rows = model()->rowCount(parent_index);

  for (int row = 0; row < rows; ++row) {
    QModelIndex index = model()->index(row, 0, parent_index);
    std::filesystem::path path = std::filesystem::path(
        model()->data(index, Qt::UserRole).toString().toStdString());

    if (path == target_path) {
      return index;
    }

    if (std::filesystem::is_directory(path) &&
        target_path.string().find(path.string()) != std::string::npos) {
      QModelIndex child_index = find_index(index, target_path);
      if (child_index.isValid()) {
        expand(index);
        return child_index;
      }
    }
  }

  return QModelIndex();
}

}  // namespace iprm::views
