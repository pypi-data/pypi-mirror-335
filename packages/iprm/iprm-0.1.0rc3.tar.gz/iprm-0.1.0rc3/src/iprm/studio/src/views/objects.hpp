/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "../apibridge.hpp"
#include "../models/objects.hpp"

#include <QHash>
#include <QTabWidget>
#include <QTreeView>

namespace iprm::views {

// TODO: for gui view, we'll need to handle merging all the targets and their
//  properties together.
//  It's probably easier to update objects view to have the paltforms a target
//  is on within the properties view, then each remaining property also be have
//  a paltform specifier (any combination of the 3 we support). It will make the
//  merging logic/python script generation much simpler

class PlatformObjects : public QTreeView {
  Q_OBJECT

 public:
  PlatformObjects(QWidget* parent = nullptr);

  void load_objects(const std::vector<ObjectNode>& objects);

 Q_SIGNALS:
  void object_selection_changed(const QModelIndex& index);

 protected:
  void showEvent(QShowEvent* event) override;

 private:
  models::Objects* objects_model_{nullptr};
};

class Objects : public QTabWidget {
  Q_OBJECT
 public:
  Objects(QWidget* parent = nullptr);

  void load_windows_objects(const std::vector<ObjectNode>& objects);

 Q_SIGNALS:
  void object_selection_changed(const QModelIndex& index);

 private:
  // TODO: support Linux and macOS
  QHash<QString, PlatformObjects*> platform_objects_;
};

}  // namespace iprm::views
