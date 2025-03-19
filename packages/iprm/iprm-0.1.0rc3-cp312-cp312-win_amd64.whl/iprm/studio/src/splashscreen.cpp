/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "splashscreen.hpp"

#include <QGuiApplication>
#include <QPainter>
#include <QScreen>
#include <QSvgRenderer>

namespace iprm {

SplashScreen::SplashScreen() : QSplashScreen() {
  QSvgRenderer renderer(QString(":/logos/iprm_splash.svg"));
  QPixmap pixmap(400, 400);
  pixmap.fill(Qt::transparent);
  QPainter painter(&pixmap);
  renderer.render(&painter);
  setPixmap(pixmap);

  QScreen* screen = QGuiApplication::primaryScreen();
  move(screen->geometry().center() - rect().center());
}

}  // namespace iprm
