/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "assetcache.hpp"
#include <QPainter>
#include <QSvgRenderer>

namespace iprm {

const QIcon& AssetCache::windows_icon() {
  static QIcon s_windows_icon(make_svg_icon(":/logos/windows.svg"));
  return s_windows_icon;
}

const QIcon& AssetCache::macos_icon() {
  static QIcon s_macos_icon(make_svg_icon(":/logos/macos2.svg"));
  return s_macos_icon;
}
const QIcon& AssetCache::linux_icon() {
  static QIcon s_linux_icon(make_svg_icon(":/logos/linux.svg"));
  return s_linux_icon;
}

const QIcon& AssetCache::msvc_icon() {
  return svg_type_icon(TypeFlags::MSVC, ":/logos/visualstudio.svg");
}

const QIcon& AssetCache::clang_icon() {
  return png_type_icon(TypeFlags::CLANG, ":/logos/llvm.png");
}

const QIcon& AssetCache::gcc_icon() {
  return svg_type_icon(TypeFlags::GCC, ":/logos/gnu.svg");
}

const QIcon& AssetCache::rustc_icon() {
  return png_type_icon(TypeFlags::RUSTC, ":/logos/rust.png");
}

const QIcon& AssetCache::boost_icon() {
  return png_type_icon(TypeFlags::BOOST, ":/logos/boost.png");
}
const QIcon& AssetCache::qt_icon() {
  return svg_type_icon(TypeFlags::QT, ":/logos/qt.svg");
}
const QIcon& AssetCache::pybind11_icon() {
  return png_type_icon(TypeFlags::RUSTC, ":/logos/pybind11.png");
}

const QIcon& AssetCache::icu_icon() {
  return svg_type_icon(TypeFlags::ICU, ":/logos/unicode.svg");
}

const QIcon& AssetCache::svg_type_icon(TypeFlags type,
                                       const QString& image_path) {
  return type_icon(type, image_path, IconFormat::Svg);
}

const QIcon& AssetCache::png_type_icon(TypeFlags type,
                                       const QString& image_path) {
  return type_icon(type, image_path, IconFormat::Png);
}

const QIcon& AssetCache::type_icon(TypeFlags type,
                                   const QString& image_path,
                                   IconFormat format) {
  auto icon_itr = type_icons_.find(type);
  if (icon_itr != type_icons_.end()) {
    return *icon_itr;
  }
  type_icons_[type] = make_icon(image_path, format);
  return type_icons_[type];
}

QIcon AssetCache::make_png_icon(const QString& image_path) {
  QPixmap pixmap(image_path);
  return QIcon(pixmap.scaled(icon_size()));
}

QIcon AssetCache::make_svg_icon(const QString& image_path) {
  QSvgRenderer renderer(image_path);
  QPixmap pixmap(icon_size());
  pixmap.fill(Qt::transparent);
  QPainter painter(&pixmap);
  painter.setRenderHint(QPainter::Antialiasing);
  renderer.render(&painter);
  painter.end();
  QIcon icon;
  icon.addPixmap(pixmap);
  return icon;
}

QIcon AssetCache::make_icon(const QString& image_path, IconFormat format) {
  switch (format) {
    case IconFormat::Svg:
      return make_svg_icon(image_path);
    case IconFormat::Png:
    default:
      return make_png_icon(image_path);
  }
}

const QIcon& AssetCache::colour_icon(const QString& hex_colour) {
  auto icon_itr = colour_icons_.find(hex_colour);
  if (icon_itr != colour_icons_.end()) {
    return *icon_itr;
  }

  const auto size = icon_size();
  QPixmap pixmap(size);
  pixmap.fill(Qt::transparent);
  QPainter painter(&pixmap);
  painter.setRenderHint(QPainter::Antialiasing);
  painter.setPen(Qt::NoPen);
  painter.setBrush(QColor::fromString(hex_colour));
  painter.drawRect(1, 1, size.width() - 2, size.height() - 2);
  painter.end();

  colour_icons_[hex_colour] = QIcon(pixmap);
  return colour_icons_[hex_colour];
}

QSize AssetCache::icon_size() {
  return QSize(16, 16);
}

}  // namespace iprm