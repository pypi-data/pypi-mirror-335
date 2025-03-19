/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include "dependencygraph.hpp"
#include <QApplication>
#include <QFrame>
#include <QGraphicsProxyWidget>
#include <QGraphicsSceneHoverEvent>
#include <QGuiApplication>
#include <QHBoxLayout>
#include <QPainter>
#include <QScrollBar>
#include <QStackedWidget>
#include <QStyleHints>
#include <QSvgRenderer>
#include <QTabWidget>
#include <QTimer>
#include <QVBoxLayout>

#include "../assetcache.hpp"
#include "loadingwidget.hpp"

#include <numeric>

namespace iprm::views {

static QPainterPath create_ellipse(qreal width, qreal height);

static QColor hex_to_colour(const QString& hex);

static QColor system_colour();

DependencyView::DependencyView(QWidget* parent) : QScrollArea(parent) {
  setWidgetResizable(true);
  setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);

  stack_ = new QStackedWidget(this);
  setWidget(stack_);

  loading_page_ = new LoadingWidget(this);
  loading_page_->set_text(tr("Generating graph..."));

  platform_tabs_ = new QTabWidget(this);
  platform_tabs_->setMovable(true);

  // TODO: don't hardcode to windows, DependencyView should have a function that
  //  passes object of ALL platforms, then setup each tab
  graph_view_ = new DependencyGraphicsView(this);
  scene_ = new DependencyGraphicsScene(this);
  graph_view_->setScene(scene_);

  // TODO: Follow Objects model of being able to dynamically object the
  //  platform-specific views
  platform_tabs_->addTab(graph_view_, AssetCache::windows_icon(),
                         tr("Windows"));
  connect(scene_, &DependencyGraphicsScene::layout_failed, this, [this]() {
    // TODO: Set the graphics view to a "Load Failed" widget (like we have for
    //  the central widget on project load failed)
    Q_EMIT layout_failed(tr("Windows"));
  });

  stack_->addWidget(loading_page_);
  stack_->addWidget(platform_tabs_);
  stack_->setCurrentWidget(loading_page_);
}

void DependencyView::build_graph(
    const lemon::ListDigraph& graph,
    const lemon::ListDigraph::NodeMap<ObjectNode>& node_data) {
  stack_->setCurrentWidget(loading_page_);

  scene_->build_graph(graph, node_data);
  stack_->setCurrentWidget(platform_tabs_);
}

DependencyGraphicsView::DependencyGraphicsView(QWidget* parent)
    : QGraphicsView(parent),
      node_summary_(new DependencyGraphNodeSummary(*this)) {
  setRenderHint(QPainter::Antialiasing);
  setViewportUpdateMode(FullViewportUpdate);
  setHorizontalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  setVerticalScrollBarPolicy(Qt::ScrollBarAsNeeded);
  setDragMode(RubberBandDrag);

  setAttribute(Qt::WA_AcceptTouchEvents);
  grabGesture(Qt::PinchGesture);
  viewport()->setAttribute(Qt::WA_AcceptTouchEvents);
}

bool DependencyGraphicsView::event(QEvent* event) {
  if (event->type() == QEvent::Gesture) {
    return gestureEvent(dynamic_cast<QGestureEvent*>(event));
  }
  return QGraphicsView::event(event);
}

void DependencyGraphicsView::showEvent(QShowEvent* event) {
  QGraphicsView::showEvent(event);
  QTimer::singleShot(0, this, [this]() {
    auto dep_scene = qobject_cast<DependencyGraphicsScene*>(scene());
    if (dep_scene == nullptr) {
      return;
    }

    QRectF itemsRect = dep_scene->itemsBoundingRect();
    if (itemsRect.isEmpty()) {
      return;
    }

    static constexpr qreal margin = 0.2;
    QRectF expandedRect = itemsRect.adjusted(
        -itemsRect.width() * margin, -itemsRect.height() * margin,
        itemsRect.width() * margin, itemsRect.height() * margin);

    dep_scene->setSceneRect(expandedRect);
    fitInView(expandedRect, Qt::KeepAspectRatio);
    viewport()->update();

    dep_scene->addItem(node_summary_);
    connect(dep_scene->item_factory(),
            &DependencyGraphItemFactory::node_hover_state_changed,
            node_summary_, &DependencyGraphNodeSummary::on_hover_state_changed);
    node_summary_->update_position();
  });
}

void DependencyGraphicsView::hideEvent(QHideEvent* event) {
  QGraphicsView::hideEvent(event);
  qApp->restoreOverrideCursor();
}

void DependencyGraphicsView::resizeEvent(QResizeEvent* event) {
  QGraphicsView::resizeEvent(event);
  Q_EMIT viewport_changed();
}

void DependencyGraphicsView::wheelEvent(QWheelEvent* event) {
  bool from_trackpad = (event->source() == Qt::MouseEventSynthesizedBySystem);
  if (!from_trackpad) {
    QPointF scene_pos = mapToScene(event->position().toPoint());
    qreal factor =
        event->angleDelta().y() > 0 ? zoom_factor_ : 1.0 / zoom_factor_;
    scale(factor, factor);
    QPointF delta = mapToScene(event->position().toPoint()) - scene_pos;
    translate(delta.x(), delta.y());
  } else {
    QPoint pixels = event->pixelDelta();
    QPoint degrees = event->angleDelta() / 8;

    // Use pixel delta for smoother scrolling if available
    if (!pixels.isNull()) {
      horizontalScrollBar()->setValue(horizontalScrollBar()->value() -
                                      pixels.x());
      verticalScrollBar()->setValue(verticalScrollBar()->value() - pixels.y());
    } else if (!degrees.isNull()) {
      QPoint steps = degrees / 15;
      horizontalScrollBar()->setValue(horizontalScrollBar()->value() -
                                      steps.x() * 20);
      verticalScrollBar()->setValue(verticalScrollBar()->value() -
                                    steps.y() * 20);
    }
  }
  Q_EMIT viewport_changed();
  event->accept();
}

bool DependencyGraphicsView::gestureEvent(QGestureEvent* event) {
  if (QGesture* pinch = event->gesture(Qt::PinchGesture)) {
    pinchTriggered(dynamic_cast<QPinchGesture*>(pinch));
    return true;
  }
  return false;
}

void DependencyGraphicsView::pinchTriggered(QPinchGesture* gesture) {
  QPinchGesture::ChangeFlags changeFlags = gesture->changeFlags();

  if (changeFlags & QPinchGesture::ScaleFactorChanged) {
    QPointF center = gesture->centerPoint();

    QPointF scene_pos = mapToScene(center.toPoint());

    qreal scale_factor = gesture->scaleFactor();

    // Avoid excessive scaling from single gestures
    if (scale_factor > 2.0)
      scale_factor = 2.0;
    if (scale_factor < 0.5)
      scale_factor = 0.5;

    scale(scale_factor, scale_factor);
    current_scale_ *= scale_factor;

    QPointF delta = mapToScene(center.toPoint()) - scene_pos;
    translate(delta.x(), delta.y());
    Q_EMIT viewport_changed();
  }
}

void DependencyGraphicsView::mousePressEvent(QMouseEvent* event) {
  if (event->button() == Qt::LeftButton) {
    panning_ = true;
    last_mouse_pos_ = event->pos();
    qApp->setOverrideCursor(Qt::ClosedHandCursor);
    event->accept();
  } else {
    QGraphicsView::mousePressEvent(event);
  }
}

void DependencyGraphicsView::mouseReleaseEvent(QMouseEvent* event) {
  if (event->button() == Qt::LeftButton) {
    panning_ = false;
    qApp->restoreOverrideCursor();
    event->accept();
  } else {
    QGraphicsView::mouseReleaseEvent(event);
  }
}

void DependencyGraphicsView::mouseMoveEvent(QMouseEvent* event) {
  if (panning_) {
    QPoint delta = event->pos() - last_mouse_pos_;
    last_mouse_pos_ = event->pos();
    horizontalScrollBar()->setValue(horizontalScrollBar()->value() - delta.x());
    verticalScrollBar()->setValue(verticalScrollBar()->value() - delta.y());
    Q_EMIT viewport_changed();
    event->accept();
  } else {
    QGraphicsView::mouseMoveEvent(event);
  }
}

DependencyGraphNodeSummary::DependencyGraphNodeSummary(
    DependencyGraphicsView& graphics_view)
    : QGraphicsProxyWidget(nullptr), graphics_view_(graphics_view) {
  summary_view_ = new QStackedWidget();
  summary_view_->hide();
  setWidget(summary_view_);
  setZValue(std::numeric_limits<qreal>::max());
  setFlag(ItemIgnoresTransformations, true);

  connect(&graphics_view_, &DependencyGraphicsView::viewport_changed, this,
          &DependencyGraphNodeSummary::update_position);
  connect(this, &DependencyGraphNodeSummary::geometryChanged, this,
          &DependencyGraphNodeSummary::update_position);
}

void DependencyGraphNodeSummary::on_hover_state_changed(
    DependencyGraphNode* node,
    bool hovering) {
  if (!hovering) {
    widget()->hide();
    return;
  }

  auto summary_itr = summaries_.find(node->id());
  if (summary_itr != summaries_.end()) {
    summary_view_->setCurrentWidget(summary_itr->second);
  } else {
    auto summary = new QFrame();
    summary->setFrameShape(QFrame::Box);
    summary->setFrameShadow(QFrame::Plain);
    summary->setLineWidth(2);
    auto main_layout = new QVBoxLayout(summary);
    main_layout->setAlignment(Qt::AlignCenter);

    auto name_label = new QLabel(node->name());
    QFont name_font = name_label->font();
    name_font.setBold(true);
    name_font.setPointSize(12);
    name_label->setFont(name_font);
    main_layout->addWidget(name_label, 0, Qt::AlignHCenter);

    auto name_divider = new QFrame();
    name_divider->setFrameShape(QFrame::HLine);
    name_divider->setFrameShadow(QFrame::Plain);
    name_divider->setLineWidth(1);
    main_layout->addWidget(name_divider);

    auto type_icon_layout = new QHBoxLayout();
    const auto type_flags = node->type_flags();
    const auto icon_size = AssetCache::icon_size();
    auto make_icon_label = [&summary, &type_flags, &icon_size](
                               TypeFlags type, const QIcon& icon) {
      QLabel* label = nullptr;
      if (static_cast<bool>(type_flags & type)) {
        label = new QLabel(summary);
        label->setPixmap(icon.pixmap(icon_size));
      }
      return label;
    };

    type_icon_layout->addStretch(1);

    // Language Compiler
    if (auto msvc_label =
            make_icon_label(TypeFlags::MSVC, AssetCache::msvc_icon())) {
      type_icon_layout->addWidget(msvc_label);
    } else if (auto clang_label = make_icon_label(TypeFlags::CLANG,
                                                  AssetCache::clang_icon())) {
      type_icon_layout->addWidget(clang_label);
    } else if (auto gcc_label =
                   make_icon_label(TypeFlags::GCC, AssetCache::gcc_icon())) {
      type_icon_layout->addWidget(gcc_label);
    } else if (auto rustc_label = make_icon_label(TypeFlags::RUSTC,
                                                  AssetCache::rustc_icon())) {
      type_icon_layout->addWidget(rustc_label);
    }

    // Known Third Party
    if (auto boost_label =
            make_icon_label(TypeFlags::BOOST, AssetCache::boost_icon())) {
      type_icon_layout->addWidget(boost_label);
    } else if (auto qt_label =
                   make_icon_label(TypeFlags::QT, AssetCache::qt_icon())) {
      type_icon_layout->addWidget(qt_label);
    } else if (auto pybind11_label = make_icon_label(
                   TypeFlags::PYBIND11, AssetCache::pybind11_icon())) {
      type_icon_layout->addWidget(pybind11_label);
    } else if (auto icu_label =
                   make_icon_label(TypeFlags::ICU, AssetCache::icu_icon())) {
      type_icon_layout->addWidget(icu_label);
    }

    // Third Party Content Source
    // TODO: set icons for third party targets and where their content came from
    //  (e.g. source archive, precompiled archive, vcpkg, etc)

    type_icon_layout->addStretch(1);

    main_layout->addLayout(type_icon_layout);
    main_layout->addWidget(new QLabel(node->target_type()), 0,
                           Qt::AlignHCenter);

    auto type_divider = new QFrame();
    type_divider->setFrameShape(QFrame::HLine);
    type_divider->setFrameShadow(QFrame::Plain);
    type_divider->setLineWidth(1);
    main_layout->addWidget(type_divider);

    main_layout->addWidget(new QLabel(node->obj_project_rel_dir_path()), 0,
                           Qt::AlignHCenter);

    summary_view_->addWidget(summary);
    summary_view_->setCurrentWidget(summary);
    summaries_[node->id()] = summary;
  }
  widget()->setVisible(hovering);
}

void DependencyGraphNodeSummary::update_position() {
  setPos(graphics_view_.mapToScene(QPoint(
      10, graphics_view_.viewport()->height() - 10 - widget()->height())));
}

DependencyGraphicsScene::DependencyGraphicsScene(QObject* parent)
    : QGraphicsScene(parent),
      gvc_(gvContext()),
      item_factory_(new DependencyGraphItemFactory(this)) {
  setItemIndexMethod(NoIndex);
  assert(gvc_ != nullptr);
}

void DependencyGraphicsScene::build_graph(
    const lemon::ListDigraph& graph,
    const lemon::ListDigraph::NodeMap<ObjectNode>& node_data) {
  item_factory_->clear();
  clear();

  auto g = gv::create_graph("dependency_graph");

  std::unordered_map<int, Agnode_t*> gv_nodes;
  std::unordered_map<std::string, TypeFlags> gv_node_types;

  for (lemon::ListDigraph::NodeIt n(graph); n != lemon::INVALID; ++n) {
    const auto& data = node_data[n];
    const int node_id = graph.id(n);

    const auto name = data.name.toStdString();
    gv_node_types[name] = data.type;
    const auto target_type = data.type_name.toStdString();
    const auto shape_type = data.shape_type.toStdString();
    const auto hex_colour = data.hex_colour.toStdString();
    const auto obj_project_rel_dir_path =
        data.project_rel_dir_path.toStdString();
    gv_nodes[node_id] = add_node(g, node_id, name, target_type, shape_type,
                                 hex_colour, obj_project_rel_dir_path);
  }

  for (lemon::ListDigraph::ArcIt a(graph); a != lemon::INVALID; ++a) {
    auto source_id = graph.id(graph.source(a));
    auto target_id = graph.id(graph.target(a));

    add_edge(g, gv_nodes[source_id], gv_nodes[target_id]);
  }

  if (auto layout_res = gv::apply_layout(gvc_, g, "dot")) {
    for (auto& node : layout_res.value().nodes) {
      node.type = gv_node_types[node.name];
    }
    item_factory_->create(layout_res.value());
  } else {
    Q_EMIT layout_failed();
  }
}

DependencyGraphItemFactory::DependencyGraphItemFactory(QGraphicsScene* scene,
                                                       QObject* parent)
    : QObject(parent), scene_(scene) {}

void DependencyGraphItemFactory::create(const gv::LayoutResult& result) {
  clear();

  for (const auto& layout_node : result.nodes) {
    auto node = new DependencyGraphNode(layout_node);
    connect(&node->state_change_notifier(),
            &NodeStateChangeNotifier::hover_state_changed, this,
            [this](int node_id, bool hovering) {
              Q_EMIT node_hover_state_changed(nodes_[node_id], hovering);
            });
    nodes_[node->id()] = node;
    scene_->addItem(node);
  }

  for (const auto& layout_edge : result.edges) {
    auto edge =
        new DependencyGraphEdge(layout_edge, nodes_[layout_edge.source_id],
                                nodes_[layout_edge.target_id]);
    edges_.push_back(edge);
    scene_->addItem(edge);

    edge->setZValue(-1);
  }
}

void DependencyGraphItemFactory::clear() {
  for (auto& [_, node] : nodes_) {
    scene_->removeItem(node);
    delete node;
    node = nullptr;
  }
  nodes_.clear();

  for (auto& edge : edges_) {
    scene_->removeItem(edge);
    delete edge;
    edge = nullptr;
  }
  edges_.clear();
}

void NodeStateChangeNotifier::notify_state_changed(int node_id, bool hovering) {
  Q_EMIT hover_state_changed(node_id, hovering);
}

DependencyGraphNode::DependencyGraphNode(const gv::NodeItem& node,
                                         QGraphicsItem* parent)
    : QGraphicsItem(parent),
      m_id(node.id),
      name_(QString::fromStdString(node.name)),
      target_type_(QString::fromStdString(node.target_type)),
      type_flags_(node.type),
      shape_type_(QString::fromStdString(node.shape_type)),
      hex_colour_(QString::fromStdString(node.hex_colour)),
      obj_project_rel_dir_path_(
          QString::fromStdString(node.obj_project_rel_dir_path)),
      x_(node.x),
      y_(node.y),
      width_(node.width),
      height_(node.height) {
  setPos(x_, y_);

  setAcceptHoverEvents(true);
}

QPainterPath DependencyGraphNode::node_path() const {
  QPainterPath path;

  if (shape_type_ == "circle") {
    qreal radius = qMin(width_, height_) / 2.0;
    path.addEllipse(-radius, -radius, radius * 2, radius * 2);
  } else if (shape_type_ == "ellipse") {
    path = create_ellipse(width_, height_);
  } else if (shape_type_ == "diamond") {
    path.moveTo(-width_ / 2.0, 0);
    path.lineTo(0, -height_ / 2.0);
    path.lineTo(width_ / 2.0, 0);
    path.lineTo(0, height_ / 2.0);
    path.closeSubpath();
  } else if (shape_type_ == "rectangle") {
    path.addRect(-width_ / 2.0, -height_ / 2.0, width_, height_);
  } else {
    // Default to circle for unknown shapes
    qreal radius = qMin(width_, height_) / 2.0;
    path.addEllipse(-radius, -radius, radius * 2, radius * 2);
  }

  return path;
}

QRectF DependencyGraphNode::boundingRect() const {
  return QRectF(-width_ / 2 - 2, -height_ / 2 - 2, width_ + 4, height_ + 4);
}

void DependencyGraphNode::hoverEnterEvent(QGraphicsSceneHoverEvent* event) {
  const QPointF pos = event->pos();
  if (node_path().contains(pos)) {
    hovering_ = true;
    setCursor(Qt::PointingHandCursor);
    state_change_nofifier_.notify_state_changed(id(), hovering_);
    update();
  }
  QGraphicsItem::hoverEnterEvent(event);
}

void DependencyGraphNode::hoverMoveEvent(QGraphicsSceneHoverEvent* event) {
  const QPointF pos = event->pos();
  const bool was_hovering = hovering_;
  hovering_ = node_path().contains(pos);
  if (was_hovering != hovering_) {
    if (hovering_) {
      setCursor(Qt::PointingHandCursor);
    } else {
      unsetCursor();
    }
    state_change_nofifier_.notify_state_changed(id(), hovering_);
    update();
  }
  QGraphicsItem::hoverMoveEvent(event);
}

void DependencyGraphNode::hoverLeaveEvent(QGraphicsSceneHoverEvent* event) {
  hovering_ = false;
  unsetCursor();
  state_change_nofifier_.notify_state_changed(id(), hovering_);
  update();
  QGraphicsItem::hoverLeaveEvent(event);
}

void DependencyGraphNode::paint(QPainter* painter,
                                const QStyleOptionGraphicsItem* option,
                                QWidget* widget) {
  Q_UNUSED(option);
  Q_UNUSED(widget);

  QPainterPath path = node_path();

  const QColor nodeColor = hex_to_colour(hex_colour_);
  painter->fillPath(path, nodeColor);

  if (hovering_) {
    QPen highlightPen(QColor("#FF3B30"));
    highlightPen.setWidth(1);
    painter->setPen(highlightPen);
    painter->drawPath(path);
  }

  painter->setPen(system_colour());
  painter->setFont(QFont("Arial", 10));

  QRectF textRect = boundingRect();
  painter->drawText(textRect, Qt::AlignCenter, name_);
}

DependencyGraphEdge::DependencyGraphEdge(const gv::EdgeItem& edge,
                                         DependencyGraphNode* source_node,
                                         DependencyGraphNode* target_node,
                                         QGraphicsItem* parent)
    : QGraphicsItem(parent),
      source_id_(edge.source_id),
      source_node_(source_node),
      target_id_(edge.target_id),
      target_node_(target_node) {
  if (!source_node_ || !target_node_) {
    qWarning() << "Edge created with invalid source or target node IDs";
    return;
  }

  for (const auto& spline : edge.splines) {
    spline_points_.push_back(QPointF(spline.x, spline.y));
  }

  // Set item position to (0,0) since we're working in scene coordinates
  setPos(0, 0);
}

QRectF DependencyGraphEdge::boundingRect() const {
  if (spline_points_.empty()) {
    return QRectF();
  }

  qreal minX = spline_points_[0].x();
  qreal minY = spline_points_[0].y();
  qreal maxX = spline_points_[0].x();
  qreal maxY = spline_points_[0].y();

  for (const QPointF& p : spline_points_) {
    minX = qMin(minX, p.x());
    minY = qMin(minY, p.y());
    maxX = qMax(maxX, p.x());
    maxY = qMax(maxY, p.y());
  }

  // Add margin for arrow head and stroke width
  return QRectF(minX - 15, minY - 15, maxX - minX + 30, maxY - minY + 30);
}
void DependencyGraphEdge::paint(QPainter* painter,
                                const QStyleOptionGraphicsItem* option,
                                QWidget* widget) {
  Q_UNUSED(option);
  Q_UNUSED(widget);

  if (spline_points_.size() < 2 || !source_node_ || !target_node_) {
    return;
  }

  QPen edgePen(system_colour(), 1.5, Qt::SolidLine, Qt::RoundCap);
  painter->setPen(edgePen);

  QPainterPath path;
  path.moveTo(spline_points_[0]);

  // If we have a Bézier curve (GraphViz typically provides 4 points per
  // segment)
  if (spline_points_.size() == 4) {
    path.cubicTo(spline_points_[1], spline_points_[2], spline_points_[3]);
  }
  // Handle case where we have multiple segments in a spline
  else if (spline_points_.size() > 4) {
    for (int i = 1; i < spline_points_.size(); i += 3) {
      if (i + 2 < spline_points_.size()) {
        path.cubicTo(spline_points_[i], spline_points_[i + 1],
                     spline_points_[i + 2]);
      } else {
        // Not enough points for a full cubic, just line to the end
        path.lineTo(spline_points_[spline_points_.size() - 1]);
      }
    }
  } else {
    for (int i = 1; i < spline_points_.size(); ++i) {
      path.lineTo(spline_points_[i]);
    }
  }

  painter->drawPath(path);

  QPointF last_point = spline_points_.back();
  QPointF second_last_point;

  if (spline_points_.size() >= 2) {
    second_last_point = spline_points_[spline_points_.size() - 2];
  } else {
    second_last_point = last_point - QPointF(10, 0);  // Fallback
  }

  QPointF dir = last_point - second_last_point;
  qreal length = qSqrt(dir.x() * dir.x() + dir.y() * dir.y());

  if (length > 0.001) {
    dir = QPointF(dir.x() / length, dir.y() / length);
  } else {
    dir = QPointF(1.0, 0.0);
  }

  QPointF head_base = last_point;
  // The tip should be a short distance further in the same direction. Not 100%
  // spot on, but close/good enough without having to do any complex/expensive
  // intersection calculations
  QPointF head_tip = head_base + (dir * 10.0);
  draw_arrow_head(painter, head_tip, head_base);
}

void DependencyGraphEdge::draw_arrow_head(QPainter* painter,
                                          const QPointF& tip,
                                          const QPointF& control) {
  qreal dx = tip.x() - control.x();
  qreal dy = tip.y() - control.y();

  qreal length = qSqrt(dx * dx + dy * dy);
  qreal nx, ny;

  if (length > 0.001) {
    nx = dx / length;
    ny = dy / length;
  } else {
    // Default direction if vectors are too close
    nx = 0.0;
    ny = -1.0;
  }

  qreal arrowLength = 10.0;
  qreal arrowWidth = 6.0;

  qreal baseX = tip.x() - nx * arrowLength;
  qreal baseY = tip.y() - ny * arrowLength;

  qreal perpX = -ny;
  qreal perpY = nx;

  qreal leftX = baseX + perpX * arrowWidth / 2.0;
  qreal leftY = baseY + perpY * arrowWidth / 2.0;

  qreal rightX = baseX - perpX * arrowWidth / 2.0;
  qreal rightY = baseY - perpY * arrowWidth / 2.0;

  QPolygonF arrowHead;
  arrowHead << tip << QPointF(leftX, leftY) << QPointF(rightX, rightY);

  painter->setBrush(system_colour());
  painter->setPen(Qt::NoPen);
  painter->drawPolygon(arrowHead);
}

QPainterPath create_ellipse(qreal width, qreal height) {
  QPainterPath path;

  qreal rx = width / 2.0;
  qreal ry = height / 2.0;

  // Magic constant for a close approximation of an ellipse using Bezier
  // curves
  qreal c = 0.551915024494;

  // Top point
  path.moveTo(0, -ry);

  // Right curve
  path.cubicTo(c * rx, -ry, rx, -c * ry, rx, 0);

  // Bottom curve
  path.cubicTo(rx, c * ry, c * rx, ry, 0, ry);

  // Left curve
  path.cubicTo(-c * rx, ry, -rx, c * ry, -rx, 0);

  // Top curve
  path.cubicTo(-rx, -c * ry, -c * rx, -ry, 0, -ry);

  return path;
}

inline QColor hex_to_colour(const QString& hex) {
  QString cleanHex = hex;
  if (cleanHex.startsWith('#')) {
    cleanHex = cleanHex.mid(1);
  }

  if (cleanHex.length() != 6) {
    return QColor(Qt::gray);  // Default color on error
  }

  bool ok;
  int r = cleanHex.mid(0, 2).toInt(&ok, 16);
  if (!ok)
    return QColor(Qt::gray);

  int g = cleanHex.mid(2, 2).toInt(&ok, 16);
  if (!ok)
    return QColor(Qt::gray);

  int b = cleanHex.mid(4, 2).toInt(&ok, 16);
  if (!ok)
    return QColor(Qt::gray);

  return QColor(r, g, b);
}

QColor system_colour() {
  QStyleHints* styleHints = QGuiApplication::styleHints();
  switch (styleHints->colorScheme()) {
    case Qt::ColorScheme::Dark:
      return Qt::white;
    case Qt::ColorScheme::Light:
    case Qt::ColorScheme::Unknown:
    default:
      return Qt::black;
  }
}

}  // namespace iprm::views
