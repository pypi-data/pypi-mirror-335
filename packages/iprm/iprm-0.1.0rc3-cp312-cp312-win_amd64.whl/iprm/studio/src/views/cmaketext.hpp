/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QCodeEditor>
#include <QList>
#include <QRegularExpression>
#include <QStyleSyntaxHighlighter>

namespace iprm::views {

struct HighlightRule {
  QRegularExpression pattern;
  QString formatName;
};

struct HighlightBlockRule {
  QRegularExpression startPattern;
  QRegularExpression endPattern;
  QString formatName;
};

class CMakeHighlighter : public QStyleSyntaxHighlighter {
  Q_OBJECT

 public:
  explicit CMakeHighlighter(QTextDocument* document = nullptr);

 protected:
  void highlightBlock(const QString& text) override;

 private:
  QList<HighlightRule> highlight_rules_;
  QList<HighlightBlockRule> highlight_block_rules_;

  QRegularExpression function_pattern_;
  QRegularExpression variable_pattern_;
  QRegularExpression property_pattern_;
};

class CMakeText : public QCodeEditor {
  Q_OBJECT

 public:
  explicit CMakeText(QWidget* parent = nullptr);
};

}  // namespace iprm::views
