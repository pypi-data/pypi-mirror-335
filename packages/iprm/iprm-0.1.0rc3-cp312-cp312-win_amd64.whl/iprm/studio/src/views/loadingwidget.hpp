/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QLabel>
#include <QProgressBar>
#include <QWidget>

namespace iprm::views {

class LoadingWidget : public QWidget {
  Q_OBJECT

 public:
  explicit LoadingWidget(QWidget* parent = nullptr);
  ~LoadingWidget() = default;

  void set_text(const QString& text);

 private:
  QProgressBar* progress_bar_{nullptr};
  QLabel* label_{nullptr};
};

}  // namespace iprm::views
