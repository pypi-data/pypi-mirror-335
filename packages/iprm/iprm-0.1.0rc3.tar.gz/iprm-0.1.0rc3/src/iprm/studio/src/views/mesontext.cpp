/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "mesontext.hpp"
#include "textstyle.hpp"

#include <QPythonHighlighter>
#include <QCodeEditor>
#include <QGuiApplication>
#include <QStyleHints>

namespace iprm::views {

MesonText::MesonText(QWidget* parent) : QCodeEditor(parent) {
  // TODO: Hook up Editor syntax style to the options page, when switching this
  //  widget should update it's styles. Should keep the full map of available
  //  styles, or have a way to ask for them
  setReadOnly(true);
  setSyntaxStyle(TextStyle::active());
  // No completions as this is a read-only view
  setHighlighter(new QPythonHighlighter);
  setWordWrapMode(QTextOption::NoWrap);
  QStyleHints* styleHints = QGuiApplication::styleHints();
  connect(styleHints, &QStyleHints::colorSchemeChanged, this,
          [this](Qt::ColorScheme colour_scheme) {
            setSyntaxStyle(TextStyle::active());
          });
}

}  // namespace iprm::views
