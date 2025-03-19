/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <lemon/list_graph.h>
#include <QAbstractItemModel>
#include <filesystem>
#include <unordered_map>
#include <variant>
#include <vector>

template <class... Ts>
struct overloaded : Ts... {
  using Ts::operator()...;
};

namespace iprm::models {

struct NativeFile {
  std::filesystem::path path;
  std::filesystem::path parent_path;
};

struct CMakeFile {
  std::filesystem::path native_path;
  std::filesystem::path path;
  std::filesystem::path parent_path;
};

struct MesonFile {
  std::filesystem::path native_path;
  std::filesystem::path path;
  std::filesystem::path parent_path;
};

struct Folder {
  std::filesystem::path path;
  std::filesystem::path parent_path;
};

// TODO: Generalize the code for the generator file types to reduce duplication
using FileNode = std::variant<NativeFile, CMakeFile, MesonFile, Folder>;

class FileSystem : public QAbstractItemModel {
  Q_OBJECT

 public:
  explicit FileSystem(QObject* parent = nullptr);
  ~FileSystem() override;

  void load_tree(const std::vector<std::filesystem::path>& files,
                 const std::filesystem::path& root_dir);

  QModelIndex index(int row,
                    int column,
                    const QModelIndex& parent = QModelIndex()) const override;
  QModelIndex parent(const QModelIndex& index) const override;
  int rowCount(const QModelIndex& parent = QModelIndex()) const override;
  int columnCount(const QModelIndex& parent = QModelIndex()) const override;
  QVariant data(const QModelIndex& index,
                int role = Qt::DisplayRole) const override;
  QVariant headerData(int section,
                      Qt::Orientation orientation,
                      int role = Qt::DisplayRole) const override;

  FileNode get_file_node(const QModelIndex& index) const;

 private:
  void build_tree_structure(const std::vector<std::filesystem::path>& files);
  QModelIndex create_index_from_node(int row,
                                     int column,
                                     lemon::ListDigraph::Node node) const;
  lemon::ListDigraph::Node get_node_from_index(const QModelIndex& index) const;
  std::vector<lemon::ListDigraph::Node> get_children(
      lemon::ListDigraph::Node node) const;

  lemon::ListDigraph fs_graph_;
  lemon::ListDigraph::NodeMap<FileNode> fs_node_data_;
  std::filesystem::path root_dir_;
  lemon::ListDigraph::Node root_node_;

  std::unordered_map<int, std::vector<lemon::ListDigraph::Node>>
      sorted_children_;
  std::unordered_map<int, lemon::ListDigraph::Node> parent_map_;
};

}  // namespace iprm::models
