/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "../apibridge.hpp"

#include <QWidget>

class QTabWidget;

namespace iprm::views {

class NativeText;
class CMakeText;
class MesonText;
class Objects;

class File : public QWidget {
  Q_OBJECT
 public:
  File(
const QString& file_name,
  const QString& proj_relative_dir_path,
           const QString& file_contents,
           const std::vector<ObjectNode>& objects,
           QWidget* parent = nullptr);

  void show_cmake(QString contents);
  void show_meson(QString contents);

  QString file_path() const;

  private Q_SLOTS:
   void on_object_selection_changed(const QModelIndex& index);

private:
  QString file_name_;
  QString proj_relative_dir_path_;
  Objects* objects_view_{nullptr};
  NativeText* native_text_view_{nullptr};
  QTabWidget* cmake_text_{nullptr};
  QTabWidget* meson_text_{nullptr};
  // TODO: This should be a QHash of platform to GeneratedText file instances
  // that are
  //  in the tab widget, given Windows +WSL means we can have one scenario
  //  where there is more than 1 platform we can generate to on a single host
  CMakeText* cmake_text_view_{nullptr};
  MesonText* meson_text_view_{nullptr};
};

} // namespace iprm::views