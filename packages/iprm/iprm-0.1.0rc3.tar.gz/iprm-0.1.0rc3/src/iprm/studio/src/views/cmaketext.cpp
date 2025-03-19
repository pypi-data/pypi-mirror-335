/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "cmaketext.hpp"
#include "textstyle.hpp"

#include <QCodeEditor>
#include <QGuiApplication>
#include <QStyleHints>

namespace iprm::views {

CMakeHighlighter::CMakeHighlighter(QTextDocument* document)
    : QStyleSyntaxHighlighter(document),
      function_pattern_(QRegularExpression(R"(\b([A-Za-z0-9_]+)(?=\s*\())")),
      variable_pattern_(QRegularExpression(R"(\$\{[^}]+\})")),
      property_pattern_(QRegularExpression(R"(\b[A-Z_]+\b(?!\s*\())")) {
  static const QStringList keywords = {"if",
                                       "else",
                                       "elseif",
                                       "endif",
                                       "foreach",
                                       "endforeach",
                                       "while",
                                       "endwhile",
                                       "function",
                                       "endfunction",
                                       "macro",
                                       "endmacro",
                                       "set",
                                       "unset",
                                       "return",
                                       "break",
                                       "continue",
                                       "option",
                                       "project",
                                       "add_subdirectory",
                                       "include",
                                       "find_package",
                                       "target_link_libraries",
                                       "target_include_directories",
                                       "add_library",
                                       "add_executable"};

  for (const QString& keyword : keywords) {
    highlight_rules_.append(
        {QRegularExpression(QString(R"(\b%1\b)").arg(keyword)), "Keyword"});
  }

  // Numbers
  highlight_rules_.append({QRegularExpression(R"(\b\d+\b)"), "Number"});

  // Strings - quoted
  highlight_rules_.append(
      {QRegularExpression(R"("[^"\\]*(\\.[^"\\]*)*")"), "String"});

  // Comments - single line
  highlight_rules_.append({QRegularExpression(R"(#[^\n]*)"), "Comment"});

  // Generator expressions
  highlight_rules_.append({QRegularExpression(R"(\$<[^>]+>)"), "Preprocessor"});

  // Multiline strings (bracket arguments)
  highlight_block_rules_.append(
      {QRegularExpression(R"(\[\[)"), QRegularExpression(R"(\]\])"), "String"});

  // Cache variables
  highlight_rules_.append(
      {QRegularExpression(R"(\b[A-Z_]+\s+CACHE\b)"), "Type"});
}

void CMakeHighlighter::highlightBlock(const QString& text) {
  // Function calls
  {
    auto matchIterator = function_pattern_.globalMatch(text);
    while (matchIterator.hasNext()) {
      auto match = matchIterator.next();
      setFormat(match.capturedStart(), match.capturedLength(),
                syntaxStyle()->getFormat("Function"));
    }
  }

  // Variables
  {
    auto matchIterator = variable_pattern_.globalMatch(text);
    while (matchIterator.hasNext()) {
      auto match = matchIterator.next();
      setFormat(match.capturedStart(), match.capturedLength(),
                syntaxStyle()->getFormat("Variable"));
    }
  }

  // Properties
  {
    auto matchIterator = property_pattern_.globalMatch(text);
    while (matchIterator.hasNext()) {
      auto match = matchIterator.next();
      setFormat(match.capturedStart(), match.capturedLength(),
                syntaxStyle()->getFormat("Keyword"));
    }
  }

  // Apply standard rules
  for (const auto& rule : highlight_rules_) {
    auto matchIterator = rule.pattern.globalMatch(text);
    while (matchIterator.hasNext()) {
      auto match = matchIterator.next();
      setFormat(match.capturedStart(), match.capturedLength(),
                syntaxStyle()->getFormat(rule.formatName));
    }
  }

  // Handle multiline strings (bracket arguments)
  setCurrentBlockState(0);

  // First apply standard rules if we're not in a multiline state
  if (previousBlockState() <= 0) {
    for (const auto& rule : highlight_rules_) {
      auto matchIterator = rule.pattern.globalMatch(text);
      while (matchIterator.hasNext()) {
        auto match = matchIterator.next();
        setFormat(match.capturedStart(), match.capturedLength(),
                  syntaxStyle()->getFormat(rule.formatName));
      }
    }
  }

  // Then handle multiline strings
  int startIndex = 0;

  if (previousBlockState() > 0) {
    // We're continuing a multiline string
    startIndex = 0;
    auto& rule = highlight_block_rules_[previousBlockState() - 1];
    auto endMatch = rule.endPattern.match(text);

    if (endMatch.hasMatch()) {
      // End found in this block
      int endIndex = endMatch.capturedStart();
      setFormat(0, endIndex + endMatch.capturedLength(),
                syntaxStyle()->getFormat(rule.formatName));
      startIndex = endIndex + endMatch.capturedLength();
      setCurrentBlockState(0);
    } else {
      // End not found, continue to next block
      setFormat(0, text.length(), syntaxStyle()->getFormat(rule.formatName));
      setCurrentBlockState(previousBlockState());
      return;
    }
  }

  // Look for new multiline strings in the remaining text
  while (startIndex >= 0) {
    int ruleIndex = -1;
    int earliestStart = -1;

    // Find the earliest start pattern
    for (int i = 0; i < highlight_block_rules_.size(); ++i) {
      int start =
          text.indexOf(highlight_block_rules_[i].startPattern, startIndex);
      if (start >= 0 && (earliestStart < 0 || start < earliestStart)) {
        earliestStart = start;
        ruleIndex = i;
      }
    }

    if (ruleIndex < 0)
      break;

    const auto& rule = highlight_block_rules_[ruleIndex];
    auto endMatch = rule.endPattern.match(text, earliestStart + 2);

    if (endMatch.hasMatch()) {
      // Multiline string ends in this block
      int endIndex = endMatch.capturedStart();
      setFormat(earliestStart,
                endIndex + endMatch.capturedLength() - earliestStart,
                syntaxStyle()->getFormat(rule.formatName));
      startIndex = endIndex + endMatch.capturedLength();
    } else {
      // Multiline string continues to next block
      setFormat(earliestStart, text.length() - earliestStart,
                syntaxStyle()->getFormat(rule.formatName));
      setCurrentBlockState(ruleIndex + 1);
      break;
    }
  }
}

CMakeText::CMakeText(QWidget* parent) : QCodeEditor(parent) {
  // TODO: Hook up Editor syntax style to the options page, when switching this
  //  widget should update it's styles. Should keep the full map of available
  //  styles, or have a way to ask for them
  setReadOnly(true);
  setSyntaxStyle(TextStyle::active());
  // No completions as this is a read-only view
  setHighlighter(new CMakeHighlighter);
  setWordWrapMode(QTextOption::NoWrap);
  QStyleHints* styleHints = QGuiApplication::styleHints();
  connect(styleHints, &QStyleHints::colorSchemeChanged, this,
          [this](Qt::ColorScheme colour_scheme) {
            setSyntaxStyle(TextStyle::active());
          });
}

}  // namespace iprm::views
