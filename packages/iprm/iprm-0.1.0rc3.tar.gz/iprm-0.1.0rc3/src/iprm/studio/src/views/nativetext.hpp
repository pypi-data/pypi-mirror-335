/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QCodeEditor>
#include <QCompleter>
#include <QRegularExpression>

namespace iprm::views {

class ICodeEditorCompleter : public QCompleter {
  Q_OBJECT

 public:
  explicit ICodeEditorCompleter(QObject* parent = nullptr)
      : QCompleter(parent) {}

  // Called when text changes or special keys are pressed
  virtual void handle_editor_event(QCodeEditor* editor, QKeyEvent* event) = 0;

  // Called to determine if this completer should handle the current context
  virtual bool can_trigger_completion(QCodeEditor* editor,
                                      QKeyEvent* event) = 0;

 protected:
  QString get_word_under_cursor(const QTextCursor& cursor) const {
    auto tc = cursor;
    tc.select(QTextCursor::WordUnderCursor);
    return tc.selectedText();
  }
};

struct MethodInfo {
  QString name;
  QString signature;
  QString documentation;
  QStringList parameters;
};

struct ClassInfo {
  QString name;
  QStringList bases;
  QList<MethodInfo> methods;
  QStringList properties;
  QString documentation;
};

// TODO: Finish implementation properly
class NativeCompleter : public ICodeEditorCompleter {
  Q_OBJECT

 public:
  explicit NativeCompleter(QObject* parent = nullptr);

  bool load_api_data(const QString& filename);

  void handle_editor_event(QCodeEditor* editor, QKeyEvent* event) override;

  bool can_trigger_completion(QCodeEditor* editor, QKeyEvent* event) override;

 private:
  void insert_completion(QCodeEditor* editor, const QString& completion);
  void update_completions(QCodeEditor* editor);

  QString get_completion_prefix(const QString& text) const;

  void process_class_info(const QJsonObject& classObj);

  QStringList get_all_methods_for_class(const QString& className) const;

  QString get_variable_type(const QString& variableName) const;

  void track_variable_assignment(const QString& text);

  QRegularExpression method_call_pattern_;
  QRegularExpression variable_pattern_;
  QMap<QString, ClassInfo> class_info_;
  QMap<QString, QStringList> inherited_methods_;
  QMap<QString, QString> variable_types_;
};

class NativeText : public QCodeEditor {
  Q_OBJECT

 public:
  explicit NativeText(QWidget* parent = nullptr);
};

}  // namespace iprm::views
