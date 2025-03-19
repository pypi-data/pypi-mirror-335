/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "textstyle.hpp"
#include <QFile>
#include <QGuiApplication>
#include <QStyleHints>

namespace iprm::views {
void TextStyle::load_style(QSyntaxStyle& style, const QString& fileName) {
  if (!style.isLoaded()) {
#ifdef _WIN64
    Q_INIT_RESOURCE(res);
#endif
    QFile fl(QString(":/styles/%0").arg(fileName));

    if (!fl.open(QIODevice::ReadOnly)) {
      return;
    }

    if (!style.load(fl.readAll())) {
      qDebug() << QString("Can't load style '%0'.").arg(fileName);
    }
  }
}

QSyntaxStyle* TextStyle::active() {
  QStyleHints* styleHints = QGuiApplication::styleHints();
  switch (styleHints->colorScheme()) {
    case Qt::ColorScheme::Dark: {
      return TextStyle::one_dark();
    }
    case Qt::ColorScheme::Light:
    case Qt::ColorScheme::Unknown:
    default: {
      return TextStyle::paper();
    }
  }
}

QSyntaxStyle* TextStyle::default_() {
  return QSyntaxStyle::defaultStyle();
}

QSyntaxStyle* TextStyle::catppmpuccin_macciato() {
  static QSyntaxStyle style;
  load_style(style, "catppuccinmacchiato.xml");
  return &style;
}

QSyntaxStyle* TextStyle::deep_ocean() {
  static QSyntaxStyle style;
  load_style(style, "deepocean.xml");
  return &style;
}

QSyntaxStyle* TextStyle::drakula() {
  static QSyntaxStyle style;
  load_style(style, "drakula.xml");
  return &style;
}

QSyntaxStyle* TextStyle::forest_night() {
  static QSyntaxStyle style;
  load_style(style, "forestnight.xml");
  return &style;
}

QSyntaxStyle* TextStyle::github_light() {
  static QSyntaxStyle style;
  load_style(style, "githublight.xml");
  return &style;
}

QSyntaxStyle* TextStyle::gruv_box() {
  static QSyntaxStyle style;
  load_style(style, "gruvbox.xml");
  return &style;
}

QSyntaxStyle* TextStyle::material_palenight() {
  static QSyntaxStyle style;
  load_style(style, "materialpalenight.xml");
  return &style;
}

QSyntaxStyle* TextStyle::mightnight_blue() {
  static QSyntaxStyle style;
  load_style(style, "midnightblue.xml");
  return &style;
}

QSyntaxStyle* TextStyle::monokai() {
  static QSyntaxStyle style;
  load_style(style, "monokai.xml");
  return &style;
}

QSyntaxStyle* TextStyle::nord() {
  static QSyntaxStyle style;
  load_style(style, "nord.xml");
  return &style;
}

QSyntaxStyle* TextStyle::one_dark() {
  static QSyntaxStyle style;
  load_style(style, "onedark.xml");
  return &style;
}

QSyntaxStyle* TextStyle::paper() {
  static QSyntaxStyle style;
  load_style(style, "paper.xml");
  return &style;
}

QSyntaxStyle* TextStyle::seashell() {
  static QSyntaxStyle style;
  load_style(style, "seashell.xml");
  return &style;
}

QSyntaxStyle* TextStyle::solarized_light() {
  static QSyntaxStyle style;
  load_style(style, "solarizedlight.xml");
  return &style;
}

QSyntaxStyle* TextStyle::tokyo_night() {
  static QSyntaxStyle style;
  load_style(style, "tokyonight.xml");
  return &style;
}

QSyntaxStyle* TextStyle::twilight() {
  static QSyntaxStyle style;
  load_style(style, "twilight.xml");
  return &style;
}

}  // namespace iprm::views
