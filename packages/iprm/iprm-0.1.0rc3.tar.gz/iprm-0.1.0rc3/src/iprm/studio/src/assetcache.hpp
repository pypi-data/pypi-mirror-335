/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "../../core/src/typeflags.hpp"

#include <QHash>
#include <QIcon>
#include <QString>

namespace iprm {

class AssetCache {
 public:
  enum class IconFormat {
    Svg,
    Png,
  };

  static QSize icon_size();

  static const QIcon& windows_icon();
  static const QIcon& macos_icon();
  static const QIcon& linux_icon();

  static const QIcon& msvc_icon();
  static const QIcon& clang_icon();
  static const QIcon& gcc_icon();
  static const QIcon& rustc_icon();

  // TODO: Add the third party content source icons

  static const QIcon& boost_icon();
  static const QIcon& qt_icon();
  static const QIcon& pybind11_icon();
  static const QIcon& icu_icon();

  static const QIcon& colour_icon(const QString& hex_colour);

 private:
  static const QIcon& svg_type_icon(TypeFlags type, const QString& image_path);
  static const QIcon& png_type_icon(TypeFlags type, const QString& image_path);

  static const QIcon& type_icon(TypeFlags type,
                                const QString& image_path,
                                IconFormat format);

  static QIcon make_png_icon(const QString& image_path);
  static QIcon make_svg_icon(const QString& image_path);
  static QIcon make_icon(const QString& image_path, IconFormat format);

  inline static QHash<TypeFlags, QIcon> type_icons_;
  inline static QHash<QString, QIcon> colour_icons_;
};

}  // namespace iprm
