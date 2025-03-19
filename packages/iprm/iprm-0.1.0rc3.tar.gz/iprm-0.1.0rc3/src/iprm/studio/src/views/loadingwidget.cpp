/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "loadingwidget.hpp"
#include <QVBoxLayout>

namespace iprm::views {

LoadingWidget::LoadingWidget(QWidget* parent) : QWidget(parent) {
  auto layout = new QVBoxLayout(this);
  layout->setAlignment(Qt::AlignCenter);

  // Create and set up progress bar
  progress_bar_ = new QProgressBar(this);
  progress_bar_->setMinimum(0);
  progress_bar_->setMaximum(0);  // Busy mode
  progress_bar_->setTextVisible(false);
  progress_bar_->setFixedSize(150, 4);

  // Create label
  label_ = new QLabel(this);

  // Add widgets to layout with proper spacing and alignment
  layout->addStretch(1);
  layout->addWidget(label_, 0, Qt::AlignCenter);
  layout->addWidget(progress_bar_, 0, Qt::AlignCenter);
  layout->addStretch(1);
}

void LoadingWidget::set_text(const QString& text) {
  label_->setText(text);
}

}  // namespace iprm::views
