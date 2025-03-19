/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#pragma once

#include <graphviz/cgraph.h>
#include <graphviz/gvc.h>
#include "../../../../core/src/typeflags.hpp"

#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace iprm::gv {

struct NodeItem {
  int id{-1};
  std::string name;
  std::string target_type;
  TypeFlags type{TypeFlags::NONE};
  std::string shape_type;
  std::string hex_colour;
  std::string obj_project_rel_dir_path;
  double x{0.0};
  double y{0.0};
  double width{0.0};
  double height{0.0};
};

struct Point {
  double x{0.0};
  double y{0.0};
};

struct EdgeItem {
  int source_id{-1};
  int target_id{-1};
  std::vector<Point> splines;
};

struct LayoutResult {
  std::vector<NodeItem> nodes;
  std::vector<EdgeItem> edges;
};

struct GVC_t_deleter {
  void operator()(GVC_t* gvc_) const;
};
using ctx_ptr_t = std::unique_ptr<GVC_t, GVC_t_deleter>;
ctx_ptr_t make_ctx();

struct Agraph_t_deleter {
  void operator()(Agraph_t* g) const;
};
using graph_ptr_t = std::unique_ptr<Agraph_t, Agraph_t_deleter>;
graph_ptr_t create_graph(const std::string& name);

// TODO: Use the API at https://www.graphviz.org/pdf/cgraph.3.pdf (or tutorial
//  at https://graphviz.org/pdf/cgraph.pdf) for nodes to provide extra metadata
//  to the user (e.g. number of dependencies) as well as general graph wide
//  stats (e.g. number of nodes, number of total dependencies, longest
//  dependency chain, etc)

Agnode_t* add_node(graph_ptr_t& g,
                   int node_id,
                   const std::string& name,
                   const std::string& target_type,
                   const std::string& shape_type,
                   const std::string& hex_colour,
                   const std::string& obj_project_rel_dir_path);
Agedge_t* add_edge(graph_ptr_t& g, Agnode_t* src, Agnode_t* tgt);

std::optional<LayoutResult> apply_layout(ctx_ptr_t& ctx,
                                         graph_ptr_t& g,
                                         const std::string& layout_engine);

}  // namespace iprm::gv
