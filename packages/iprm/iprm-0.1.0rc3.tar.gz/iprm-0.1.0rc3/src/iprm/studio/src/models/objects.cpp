/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "objects.hpp"
#include "../assetcache.hpp"

#include <QGuiApplication>
#include <QPainter>
#include <QSvgRenderer>

namespace iprm::models {

// TODO: moved this into a shared location to prevent duplication,
//  as Objects and Dependency Graph use this too
QIcon create_svg_icon(const QString& svg_file) {
  QSvgRenderer renderer(svg_file);
  QPixmap pixmap(QSize(16, 16));
  pixmap.fill(Qt::transparent);
  QPainter painter(&pixmap);
  painter.setRenderHint(QPainter::Antialiasing);
  renderer.render(&painter);
  painter.end();
  QIcon icon;
  icon.addPixmap(pixmap);
  return icon;
}

Objects::Objects(QObject* parent) : QAbstractItemModel(parent) {
  // TODO: Boost, Qt, and PyBind11 icons will go into the target properties
  //  view instead of being inline on the type column
}

void Objects::load_objects(const std::vector<ObjectNode>& objects) {
  // TODO: Implicit objects shouldn't be shown here, but they SHOULD be
  //  shown in a specific objects properties view
  beginResetModel();
  objects_ = objects;
  endResetModel();
}

QVariant Objects::data(const QModelIndex& index, int role) const {
  if (!index.isValid()) {
    return QModelIndex();
  }

  const int row = index.row();
  const int column = index.column();

  const ObjectNode& obj = objects_[row];

  switch (role) {
    case Qt::DisplayRole: {
      if (column == 0) {
        if (static_cast<bool>(obj.type & TypeFlags::SUBDIRS)) {
          return QString("<iprm_subdirectories>");
        }
        return obj.name;
      } else if (column == 1) {
        return obj.type_name;
      }
    }
    case Qt::DecorationRole: {
      if (column == 0) {
        return AssetCache::colour_icon(obj.hex_colour);
      } else if (column == 1) {
        // TODO: Key off of the targets compiler AND whether or not they are qt,
        //  which will mean we will to have this decoration role support at
        //  least 3 maximum (in the case of Clang-CL Qt project). Object will
        //  need a compiler field

        if (static_cast<bool>(obj.type & TypeFlags::MSVC)) {
          return AssetCache::msvc_icon();
        } else if (static_cast<bool>(obj.type & TypeFlags::CLANG)) {
          return AssetCache::clang_icon();
        } else if (static_cast<bool>(obj.type & TypeFlags::GCC)) {
          return AssetCache::gcc_icon();
        } else if (static_cast<bool>(obj.type & TypeFlags::RUSTC)) {
          return AssetCache::rustc_icon();
        }
        // TODO: Display icon for source archives, and for pre-compiled
      }
    }
    case Qt::ToolTipRole: {
      if (static_cast<bool>(obj.type & TypeFlags::CXX) ||
          static_cast<bool>(obj.type & TypeFlags::RUST)) {
        return obj.properties["compiler_version"].toString();
      }
    }
    default:
      break;
  }

  return QVariant{};
}

QVariant Objects::headerData(int section,
                             Qt::Orientation orientation,
                             int role) const {
  if (orientation == Qt::Horizontal && role == Qt::DisplayRole) {
    static const QStringList headers{tr("Name"), tr("Type")};
    return headers[section];
  }
  return QVariant{};
}

int Objects::columnCount(const QModelIndex&) const {
  // Name and Type
  return 2;
}

QModelIndex Objects::index(int row,
                           int column,
                           const QModelIndex& parent) const {
  if (row < 0 || column < 0 || row >= rowCount(parent) ||
      column >= columnCount(parent)) {
    return QModelIndex{};
  }
  return createIndex(row, column, &objects_.at(row));
}

QModelIndex Objects::parent(const QModelIndex&) const {
  // We tabular
  return QModelIndex{};
}

int Objects::rowCount(const QModelIndex&) const {
  return static_cast<int>(objects_.size());
}

}  // namespace iprm::models
