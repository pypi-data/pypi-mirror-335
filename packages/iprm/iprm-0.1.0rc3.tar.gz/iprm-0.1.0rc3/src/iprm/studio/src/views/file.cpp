/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "file.hpp"
#include "nativetext.hpp"
#include "cmaketext.hpp"
#include "mesontext.hpp"
#include "objects.hpp"
#include "../assetcache.hpp"

#include <QSvgRenderer>
#include <QSplitter>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QPainter>
#include <QLabel>
#include <QTabWidget>

namespace iprm::views {

File::File(const QString& file_name,
                   const QString& proj_relative_dir_path,
                   const QString& file_contents,
                   const std::vector<ObjectNode>& objects,
                   QWidget* parent)
    : QWidget(parent),
      file_name_(file_name),
      proj_relative_dir_path_(proj_relative_dir_path) {
  // Graphical and Textual representation of a native project file
  auto view = new QSplitter(Qt::Vertical, this);
  auto gui_view = new QSplitter(Qt::Horizontal, this);
  objects_view_ = new Objects(this);
  connect(objects_view_, &Objects::object_selection_changed, this,
          &File::on_object_selection_changed);
  // TODO: don't hardcode to windows, File should have a function that
  //  passes object of ALL platforms, then setup each tab
  objects_view_->load_windows_objects(objects);
  gui_view->addWidget(objects_view_);

  // TODO: add objects properties view
  // gui_view->setSizes({300, 400});

  auto text_view = new QSplitter(Qt::Horizontal, this);
  auto native_text = new QWidget();
  auto native_text_layout = new QVBoxLayout(native_text);
  native_text_layout->setContentsMargins(0, 0, 0, 0);

  auto native_platforms_layout = new QHBoxLayout();
  native_platforms_layout->setContentsMargins(0, 0, 0, 0);
  native_platforms_layout->setSpacing(0);

  auto windows_layout = new QHBoxLayout();
  windows_layout->setContentsMargins(0, 0, 0, 0);
  auto windows_icon = new QLabel(this);
  windows_icon->setPixmap(AssetCache::windows_icon().pixmap(16, 16));
  windows_layout->addWidget(windows_icon);
  auto windows_text = new QLabel(tr("Windows"), this);
  windows_layout->addWidget(windows_text);
  windows_layout->addStretch();
  native_platforms_layout->addLayout(windows_layout);

  auto macos_layout = new QHBoxLayout();
  macos_layout->setContentsMargins(0, 0, 0, 0);
  auto macos_icon = new QLabel(this);
  macos_icon->setPixmap(AssetCache::macos_icon().pixmap(16, 16));
  macos_layout->addWidget(macos_icon);
  auto macos_text = new QLabel(tr("macOS"), this);
  macos_layout->addWidget(macos_text);
  macos_layout->addStretch();
  native_platforms_layout->addLayout(macos_layout);

  auto linux_layout = new QHBoxLayout();
  linux_layout->setContentsMargins(0, 0, 0, 0);
  auto linux_icon = new QLabel(this);
  linux_icon->setPixmap(AssetCache::linux_icon().pixmap(16, 16));
  linux_layout->addWidget(linux_icon);
  auto linux_text = new QLabel(tr("Linux"), this);
  linux_layout->addWidget(linux_text);
  linux_layout->addStretch();

  native_platforms_layout->addLayout(linux_layout);
  native_platforms_layout->addStretch(1);
  native_text_layout->addLayout(native_platforms_layout);

  native_text_view_ = new NativeText(this);
  native_text_view_->setPlainText(file_contents);
  native_text_layout->addWidget(native_text_view_);
  text_view->addWidget(native_text);

  // TODO: With windows WSL, we should be able to generate the files for windows
  // and Linux,
  //  so making this a TabWidget instead as windows users will be able to view
  //  the CMake for Windows AND their WSL distro

  // TODO: Don't hardcode all the text views to windows
  cmake_text_ = new QTabWidget(this);
  cmake_text_->hide();
  cmake_text_view_ = new CMakeText(this);
  cmake_text_->addTab(cmake_text_view_,
                      AssetCache::windows_icon(),
                      tr("Windows"));
  text_view->addWidget(cmake_text_);

  meson_text_ = new QTabWidget(this);
  meson_text_->hide();
  meson_text_view_ = new MesonText(this);
  meson_text_->addTab(meson_text_view_,
                      AssetCache::windows_icon(),
                      tr("Windows"));
  text_view->addWidget(meson_text_);

  // TODO: Don't set this as there can be an arbitrary amount of files
  //  being generated
  // text_view->setSizes({400, 300, 300});

  view->addWidget(gui_view);
  view->addWidget(text_view);

  view->setSizes({100, 200});

  auto main_layout = new QVBoxLayout(this);
  main_layout->addWidget(view);
}

QString File::file_path() const {
  return QDir(proj_relative_dir_path_).filePath(file_name_);
}

void File::show_cmake(QString contents) {
  auto cmake_contents = std::move(contents);
  // TODO: handle multiple platforms here in the Windows + WSL scenario
  cmake_text_view_->setText(
      cmake_contents.replace(QChar('\t'), QString(" ").repeated(4)));
  cmake_text_->show();
}

void File::show_meson(QString contents) {
  auto meson_contents = std::move(contents);
  // TODO: handle multiple platforms here in the Windows + WSL scenario
  meson_text_view_->setText(
      meson_contents.replace(QChar('\t'), QString(" ").repeated(4)));
  meson_text_->show();
}

void File::on_object_selection_changed(const QModelIndex& index) {
  Q_UNUSED(index);
}


} // namespace iprm::views

