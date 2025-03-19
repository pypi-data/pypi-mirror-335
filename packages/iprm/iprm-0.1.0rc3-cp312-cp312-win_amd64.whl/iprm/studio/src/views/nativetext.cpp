/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "nativetext.hpp"
#include "textstyle.hpp"

#include <QCodeEditor>
#include <QFile>
#include <QGuiApplication>
#include <QJsonArray>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPythonCompleter>
#include <QPythonHighlighter>
#include <QStringListModel>
#include <QStyleHints>
#include <QTextBlock>
#include <QTextCursor>

namespace iprm::views {

NativeCompleter::NativeCompleter(QObject* parent)
    : ICodeEditorCompleter(parent), method_call_pattern_(R"((\w+)\.(\w+)\s*\(?)" /*, QRegularExpression::CaseInsensitiveOption*/), variable_pattern_(R"((\w+)\s*=\s*(\w+)\()" /*, QRegularExpression::CaseInsensitiveOption*/) {
  setModel(new QStringListModel(this));
  setCompletionMode(QCompleter::PopupCompletion);
  setCaseSensitivity(Qt::CaseInsensitive /*Qt::CaseSensitive*/);
  setModelSorting(QCompleter::CaseInsensitivelySortedModel);
  setWrapAround(true);
}

bool NativeCompleter::load_api_data(const QString& filename) {
  QFile file(filename);
  if (!file.open(QIODevice::ReadOnly)) {
    return false;
  }

  QJsonDocument doc = QJsonDocument::fromJson(file.readAll());
  if (doc.isNull()) {
    return false;
  }

  // TODO: Associate a colour or Q Icon (in the case of Qt, CRT, etc)
  //  for class completion. Should be added into inspect API script
  QJsonObject root = doc.object();
  QJsonArray classes = root["classes"].toArray();

  // Process each class
  for (const QJsonValue& classVal : classes) {
    process_class_info(classVal.toObject());
  }

  // Build inheritance method lists
  for (const auto& className : class_info_.keys()) {
    inherited_methods_[className] = get_all_methods_for_class(className);
  }

  // Set initial completion list to class names
  static_cast<QStringListModel*>(model())->setStringList(class_info_.keys());

  return true;
}

bool NativeCompleter::can_trigger_completion(QCodeEditor* editor,
                                             QKeyEvent* event) {
  if (event->key() == Qt::Key_Period) {
    return true;
  }

  // Trigger on alphanumeric keys for class name completion
  if (event->text().length() == 1 &&
      (event->text()[0].isLetterOrNumber() || event->text()[0] == '_')) {
    auto cursor = editor->textCursor();
    QString currentLine = cursor.block().text().left(cursor.positionInBlock());

    // Check if we're in a context where class name completion makes sense
    return !currentLine.contains('.') && !currentLine.contains('(');
  }

  return false;
}

void NativeCompleter::handle_editor_event(QCodeEditor* editor,
                                          QKeyEvent* event) {
  if (event->key() == Qt::Key_Period) {
    QTextCursor cursor = editor->textCursor();
    QString currentLine = cursor.block().text().left(cursor.positionInBlock());

    // Get the word before the cursor (the variable or class name)
    QString lastWord =
        currentLine.split(QRegularExpression("\\s+|[(){}\\[\\]]"))
            .last()
            .trimmed();
    QString varType = get_variable_type(lastWord);

    qDebug() << "Last word before dot:" << lastWord;
    qDebug() << "Variable type:" << varType;

    // Don't insert period yet
    if (!varType.isEmpty() && inherited_methods_.contains(varType)) {
      // We have a valid variable with methods - update model with method list
      QStringList methods = inherited_methods_[varType];
      if (class_info_.contains(varType)) {
        methods.append(class_info_[varType].properties);
      }
      static_cast<QStringListModel*>(model())->setStringList(methods);

      // Now insert the period and show completions
      editor->insertPlainText(".");
      QRect cr = editor->cursorRect();
      cr.setWidth(200);
      complete(cr);
    } else {
      // Not a valid context for method completion
      editor->insertPlainText(".");
    }
  } else {
    // For other keys, update completions as normal
    update_completions(editor);
  }
}

void NativeCompleter::process_class_info(const QJsonObject& classObj) {
  ClassInfo info;
  info.name = classObj["name"].toString();

  // Load bases
  QJsonArray bases = classObj["bases"].toArray();
  for (const QJsonValue& base : bases) {
    info.bases.append(base.toString());
  }

  // Load methods
  QJsonArray methods = classObj["methods"].toArray();
  for (const QJsonValue& methodVal : methods) {
    QJsonObject methodObj = methodVal.toObject();
    MethodInfo method;
    method.name = methodObj["name"].toString();
    method.signature = methodObj["signature"].toString();
    method.documentation = methodObj["doc"].toString();

    // Parse parameters from signature
    QString sig = method.signature;
    int start = sig.indexOf('(') + 1;
    int end = sig.indexOf(')');
    QString params = sig.mid(start, end - start);
    if (!params.isEmpty()) {
      method.parameters = params.split(',');
    }

    info.methods.append(method);
  }

  // Load properties
  QJsonArray properties = classObj["properties"].toArray();
  for (const QJsonValue& prop : properties) {
    info.properties.append(prop.toString());
  }

  info.documentation = classObj["doc"].toString();
  class_info_[info.name] = info;
}

QStringList NativeCompleter::get_all_methods_for_class(
    const QString& className) const {
  QStringList methods;

  if (class_info_.contains(className)) {
    const ClassInfo& info = class_info_[className];
    for (const MethodInfo& method : info.methods) {
      methods.append(method.name);
    }

    // Get methods from base classes
    for (const QString& base : info.bases) {
      methods.append(get_all_methods_for_class(base));
    }
  }

  return methods;
}

QString NativeCompleter::get_completion_prefix(const QString& text) const {
  auto matchMethod = method_call_pattern_.match(text);
  if (matchMethod.hasMatch()) {
    return matchMethod.captured(2);  // Return the partial method name
  }

  // For class name completion, return the last word
  int lastSpace = text.lastIndexOf(' ');
  if (lastSpace == -1) {
    return text;
  }
  return text.mid(lastSpace + 1);
}

void NativeCompleter::insert_completion(QCodeEditor* editor,
                                        const QString& completion) {
  if (!editor)
    return;

  QTextCursor tc = editor->textCursor();
  int extra = completion.length() - completionPrefix().length();
  tc.movePosition(QTextCursor::Left);
  tc.movePosition(QTextCursor::EndOfWord);
  tc.insertText(completion.right(extra));
  editor->setTextCursor(tc);
}

void NativeCompleter::update_completions(QCodeEditor* editor) {
  if (!editor)
    return;

  QTextCursor cursor = editor->textCursor();
  QString currentLine = cursor.block().text().left(cursor.positionInBlock());

  qDebug() << "Current line:" << currentLine;

  // Track variable assignments
  track_variable_assignment(currentLine);

  QStringList completions;
  QString prefix;

  // Check for method completion (after a dot)
  auto methodMatch = method_call_pattern_.match(currentLine);
  if (methodMatch.hasMatch()) {
    QString varName = methodMatch.captured(1);
    QString partialMethod = methodMatch.captured(2);

    qDebug() << "Method completion - Variable:" << varName
             << "Partial method:" << partialMethod;

    QString varType = get_variable_type(varName);
    if (!varType.isEmpty() && inherited_methods_.contains(varType)) {
      completions = inherited_methods_[varType];
      if (class_info_.contains(varType)) {
        completions.append(class_info_[varType].properties);
      }
      prefix = partialMethod;
    }
  } else {
    // Class name completion
    completions = class_info_.keys();
    prefix = get_completion_prefix(currentLine);
  }

  qDebug() << "Completion prefix:" << prefix;
  qDebug() << "Available completions:" << completions;

  setCompletionPrefix(prefix);
  static_cast<QStringListModel*>(model())->setStringList(completions);

  // Show completion popup if we have matches
  if (!completions.isEmpty()) {
    QString completionPrefix = get_completion_prefix(currentLine);
    QRect cr = editor->cursorRect();
    cr.setWidth(200);  // Set a reasonable width for the popup
    complete(cr);
  }
}

void NativeCompleter::track_variable_assignment(const QString& text) {
  // Check for variable assignments
  auto assignMatch = variable_pattern_.match(text);
  if (assignMatch.hasMatch()) {
    // Track the variable type
    QString varName = assignMatch.captured(1);
    QString varType = assignMatch.captured(2);
    if (class_info_.contains(varType)) {
      variable_types_[varName] = varType;
    }
  }
}

QString NativeCompleter::get_variable_type(const QString& variableName) const {
  // First check our tracked variables
  if (variable_types_.contains(variableName)) {
    return variable_types_[variableName];
  }

  // If it's not a tracked variable, check if it's a class name
  if (class_info_.contains(variableName)) {
    return variableName;  // The "variable" is actually a class name
  }

  return QString();
}

NativeText::NativeText(QWidget* parent) : QCodeEditor(parent) {
  // TODO: Hook up Editor syntax style to the options page, when switching this
  //  widget should update it's styles. Should keep the full map of available
  //  styles, or have a way to ask for them
  setSyntaxStyle(TextStyle::active());
  // TODO: Use NativeCompleter once it's implementation is working soundly
  setCompleter(new QPythonCompleter);
  setHighlighter(new QPythonHighlighter);
  setWordWrapMode(QTextOption::NoWrap);
  setTabReplace(true);
  setTabReplaceSize(2);
  QStyleHints* styleHints = QGuiApplication::styleHints();
  connect(styleHints, &QStyleHints::colorSchemeChanged, this,
          [this](Qt::ColorScheme colour_scheme) {
            setSyntaxStyle(TextStyle::active());
          });
}

}  // namespace iprm::views
