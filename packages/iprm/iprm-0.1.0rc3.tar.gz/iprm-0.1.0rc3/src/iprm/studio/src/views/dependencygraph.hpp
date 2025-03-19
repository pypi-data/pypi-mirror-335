/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include "../apibridge.hpp"
#include <iprm/gv/graphviz.hpp>

#include <lemon/list_graph.h>
#include <QGestureEvent>
#include <QGraphicsView>
#include <QPinchGesture>
#include <QPointF>
#include <QScrollArea>
#include <QStackedWidget>
#include <QString>
#include <QGraphicsItem>
#include <QGraphicsProxyWidget>
#include <optional>
#include <set>
#include <functional>
#include <unordered_map>

class QTabWidget;

namespace iprm::views {

class LoadingWidget;
class DependencyGraphicsView;
class DependencyGraphNodeSummary;
class DependencyGraphicsScene;
class DependencyGraphItemFactory;
class DependencyGraphNode;
class DependencyGraphEdge;

class DependencyView final : public QScrollArea {
  Q_OBJECT
 public:
  explicit DependencyView(QWidget* parent = nullptr);

  void build_graph(const lemon::ListDigraph& graph,
                   const lemon::ListDigraph::NodeMap<ObjectNode>& node_data);

 Q_SIGNALS:
  void layout_failed(const QString& platform);

 private:
  QStackedWidget* stack_{nullptr};
  LoadingWidget* loading_page_{nullptr};
  DependencyGraphicsView* graph_view_{nullptr};
  DependencyGraphicsScene* scene_{nullptr};

  // TODO: Display the ALL dependency graphs for each platform in the tab widget
  QTabWidget* platform_tabs_{nullptr};
};

class DependencyGraphicsView final : public QGraphicsView {
  Q_OBJECT
 public:
  explicit DependencyGraphicsView(QWidget* parent = nullptr);

 Q_SIGNALS:
  void viewport_changed();

 protected:
  bool event(QEvent* event) override;
  void showEvent(QShowEvent* event) override;
  void hideEvent(QHideEvent* event) override;
  void resizeEvent(QResizeEvent* event) override;
  void wheelEvent(QWheelEvent* event) override;
  void mousePressEvent(QMouseEvent* event) override;
  void mouseReleaseEvent(QMouseEvent* event) override;
  void mouseMoveEvent(QMouseEvent* event) override;
  bool gestureEvent(QGestureEvent* event);
  void pinchTriggered(QPinchGesture* gesture);

 private:
  bool panning_{false};
  qreal current_scale_ = 1.0;
  QPoint last_mouse_pos_;
  const qreal zoom_factor_{1.15};
  DependencyGraphNodeSummary* node_summary_{nullptr};
};

class DependencyGraphNodeSummary : public QGraphicsProxyWidget {
  Q_OBJECT
 public:
  DependencyGraphNodeSummary(DependencyGraphicsView& graphics_view);

 public Q_SLOTS:
  void update_position();

  void on_hover_state_changed(DependencyGraphNode* node, bool hovering);

 private:
  DependencyGraphicsView& graphics_view_;
  QStackedWidget* summary_view_{nullptr};
  std::unordered_map<int, QWidget*> summaries_;
};

class DependencyGraphicsScene : public QGraphicsScene {
  Q_OBJECT
 public:
  explicit DependencyGraphicsScene(QObject* parent = nullptr);

  void build_graph(const lemon::ListDigraph& graph,
                   const lemon::ListDigraph::NodeMap<ObjectNode>& node_data);

  DependencyGraphItemFactory* item_factory() const { return item_factory_; }

 Q_SIGNALS:
  void layout_failed();

 private:
  gv::ctx_ptr_t gvc_{nullptr};
  DependencyGraphItemFactory* item_factory_;
};

class DependencyGraphItemFactory : public QObject {
  Q_OBJECT
 public:
  DependencyGraphItemFactory(QGraphicsScene* scene, QObject* parent = nullptr);

  void create(const gv::LayoutResult& result);

  void clear();

Q_SIGNALS:
  void node_hover_state_changed(DependencyGraphNode* node, bool hovering);

 private:
  QGraphicsScene* scene_;
  std::unordered_map<int, DependencyGraphNode*> nodes_;
  std::vector<DependencyGraphEdge*> edges_;
};

class NodeStateChangeNotifier : public QObject {
  Q_OBJECT
 public:
  void notify_state_changed(int node_id, bool hovering);

  Q_SIGNALS:
   void hover_state_changed(int node_id, bool hovering);
};

class DependencyGraphNode : public QGraphicsItem {
 public:
  DependencyGraphNode(const gv::NodeItem& node,
                      QGraphicsItem* parent = nullptr);

  QPainterPath node_path() const;

  QPointF calculate_shape_intersection(qreal nx, qreal ny) const;

  QRectF boundingRect() const override;

  void paint(QPainter* painter,
             const QStyleOptionGraphicsItem* option,
             QWidget* widget) override;

  qreal x() const { return x_; }
  qreal y() const { return y_; }
  qreal width() const { return width_; }
  qreal height() const { return height_; }
  int id() const { return m_id; }
  const QString& name() const { return name_; }
  const QString& target_type() const { return target_type_; }
  TypeFlags type_flags() const { return type_flags_; }
  const QString& shape_type() const { return shape_type_; }
  const QString& obj_project_rel_dir_path() const {
    return obj_project_rel_dir_path_;
  }

  NodeStateChangeNotifier& state_change_notifier() {
    return state_change_nofifier_;
  }

 protected:
  void hoverEnterEvent(QGraphicsSceneHoverEvent* event) override;
  void hoverLeaveEvent(QGraphicsSceneHoverEvent* event) override;
  void hoverMoveEvent(QGraphicsSceneHoverEvent* event) override;

 private:
  int m_id;
  QString name_;
  QString target_type_;
  TypeFlags type_flags_;
  QString shape_type_;
  QString hex_colour_;
  QString obj_project_rel_dir_path_;
  qreal x_;
  qreal y_;
  qreal width_;
  qreal height_;
  bool hovering_{false};
  NodeStateChangeNotifier state_change_nofifier_;
};

class DependencyGraphEdge : public QGraphicsItem {
 public:
  DependencyGraphEdge(const gv::EdgeItem& edge,
                      DependencyGraphNode* source_node,
                      DependencyGraphNode* target_node,
                      QGraphicsItem* parent = nullptr);

  QRectF boundingRect() const override;

  void paint(QPainter* painter,
             const QStyleOptionGraphicsItem* option,
             QWidget* widget) override;

 private:
  void draw_arrow_head(QPainter* painter,
                       const QPointF& tip,
                       const QPointF& control);
  int source_id_;
  DependencyGraphNode* source_node_;
  int target_id_;
  DependencyGraphNode* target_node_;
  std::vector<QPointF> spline_points_;
};

}  // namespace iprm::views
