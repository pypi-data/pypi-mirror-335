/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <QString>

namespace iprm {

class APIError {
 public:
  explicit APIError(const QString& msg) : message(msg) {}
  QString message;
};

}  // namespace iprm

Q_DECLARE_METATYPE(iprm::APIError)
