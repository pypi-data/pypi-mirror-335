/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QSyntaxStyle>

namespace iprm::views {

class TextStyle {
 public:
  static QSyntaxStyle* active();

  static QSyntaxStyle* default_();
  static QSyntaxStyle* catppmpuccin_macciato();
  static QSyntaxStyle* deep_ocean();
  static QSyntaxStyle* drakula();
  static QSyntaxStyle* forest_night();
  static QSyntaxStyle* github_light();
  static QSyntaxStyle* gruv_box();
  static QSyntaxStyle* material_palenight();
  static QSyntaxStyle* mightnight_blue();
  static QSyntaxStyle* monokai();
  static QSyntaxStyle* nord();
  static QSyntaxStyle* one_dark();
  static QSyntaxStyle* paper();
  static QSyntaxStyle* seashell();
  static QSyntaxStyle* solarized_light();
  static QSyntaxStyle* tokyo_night();
  static QSyntaxStyle* twilight();

 private:
  static void load_style(QSyntaxStyle& style, const QString& fileName);
};

}  // namespace iprm::views
