/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QCodeEditor>

namespace iprm::views {


class MesonText : public QCodeEditor {
  Q_OBJECT

 public:
  explicit MesonText(QWidget* parent = nullptr);
};

}  // namespace iprm::views
