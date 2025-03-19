/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <iprm/curi/register.hpp>
#include "apibridge.hpp"
#include "mainwindow.hpp"
#include "splashscreen.hpp"

#include <QApplication>
#include <QCommandLineOption>
#include <QCommandLineParser>
#include <QDir>
#include <QStyleHints>
#include <QUrl>

#include <optional>

int main(int argc, char** argv) {
  QApplication app(argc, argv);
  QApplication::setApplicationName("IPRM Studio");
  QApplication::setApplicationVersion("0.1.0-rc3");

  QCommandLineParser parser;
  parser.addHelpOption();
  parser.addVersionOption();

  QCommandLineOption projdir_option(
      QStringList() << "p" << "projdir",
      QApplication::tr("Path to project directory"), QApplication::tr("path"));
  parser.addOption(projdir_option);

  parser.process(app);

  QString project_dir;
  QString iprm_uri;

  if (parser.isSet(projdir_option)) {
    project_dir = parser.value(projdir_option);
  } else if (!parser.positionalArguments().isEmpty()) {
    QString uriArg = parser.positionalArguments().first();

    QUrl url(uriArg);
    if (url.isValid() && url.scheme() == "iprm") {
      iprm_uri = uriArg;
    } else {
      parser.showHelp(1);
    }
  }

  if (!project_dir.isEmpty() && !iprm_uri.isEmpty()) {
    parser.showHelp(1);
  }

  if (!iprm_uri.isEmpty()) {
    // TODO: Parse unique ID that contains the local server name of the
    //  requesting IPRM Studio instance that opened a link that IPRM Web
    //  server opened up via serving a page that automatically redirected
    //  us to said link
    return 0;
  }

  iprm::SplashScreen splash;
  splash.show();
  QApplication::processEvents();

  const std::string exe_path =
      std::filesystem::path{std::string{argv[0]}}.string();
  if (!iprm::curi::register_uri_scheme("iprm", exe_path)) {
    qDebug() << "Failed to register `iprm://` uri scheme";
    return 1;
  }

  std::optional<iprm::MainWindow> window;
  iprm::APIBridgeThread api_bridge;
  if (!project_dir.isEmpty()) {
    const auto iprm_project_dir = QDir(QDir::toNativeSeparators(
        QDir::current().absoluteFilePath(QDir(project_dir).absolutePath())));
    api_bridge.set_root_dir(iprm_project_dir);

    QApplication::connect(&api_bridge, &iprm::APIBridgeThread::print_stdout,
                          &app, [](const QString&) {
                            // TODO: Log this somewhere? Main Window doesn't
                            // existing
                            //  yet and we may fail, so best place to put it is
                            //  to disk to help debug if project load fails on
                            //  startup
                          });
    QApplication::connect(
        &api_bridge, &iprm::APIBridgeThread::error, &app,
        [&app, &splash, &window, &api_bridge](const iprm::APIError& error) {
          QApplication::disconnect(&api_bridge, nullptr, &app, nullptr);
          splash.finish(nullptr);
          window.emplace(api_bridge);
          window.value().on_project_load_failed(error);
          window.value().show();
        });
    QApplication::connect(
        &api_bridge, &iprm::APIBridgeThread::project_load_success, &app,
        [project_dir, &app, &window, &splash, &api_bridge]() {
          QApplication::disconnect(&api_bridge, nullptr, &app, nullptr);
          splash.finish(nullptr);
          window.emplace(api_bridge);
          window.value().set_project(project_dir);
          window.value().on_project_loaded();
          window.value().show();
        });

    QMetaObject::invokeMethod(&api_bridge, &iprm::APIBridgeThread::load_project,
                              Qt::QueuedConnection);
  } else {
    splash.finish(nullptr);
    window.emplace(api_bridge);
    window.value().show();
  }

  QStyleHints* styleHints = QGuiApplication::styleHints();
  auto set_stylesheet = [&app](const Qt::ColorScheme colour_scheme) {
    switch (colour_scheme) {
      case Qt::ColorScheme::Dark: {
        QFile ss(":/styles/dark_theme_stylesheet.qss");
        ss.open(QFile::ReadOnly);
        app.setStyleSheet(QString::fromUtf8(ss.readAll()));
        break;
      }
      case Qt::ColorScheme::Light:
      case Qt::ColorScheme::Unknown:
      default: {
        QFile ss(":/styles/light_theme_stylesheet.qss");
        ss.open(QFile::ReadOnly);
        app.setStyleSheet(QString::fromUtf8(ss.readAll()));
        break;
      }
    }
  };
  set_stylesheet(styleHints->colorScheme());
  QObject::connect(styleHints, &QStyleHints::colorSchemeChanged, &app,
                   [&set_stylesheet](Qt::ColorScheme colour_scheme) {
                     set_stylesheet(colour_scheme);
                   });
  return QApplication::exec();
}
