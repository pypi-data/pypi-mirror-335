/*
 * Copyright (c) 2025 ayeteadoe <ayeteadoe@gmail.com>
 *
 * SPDX-License-Identifier: MIT
 */
#include <graphviz/cgraph.h>
#include <graphviz/gvc.h>
#include <chrono>
#include <functional>
#include <iprm/gv/graphviz.hpp>
#include <string>
#include <unordered_map>

#ifdef _WIN64
#define STRDUP _strdup
#else
#define STRDUP strdup
#endif

namespace iprm::gv {

void GVC_t_deleter::operator()(GVC_t* gvc) const {
  if (gvc != nullptr) {
    gvFreeContext(gvc);
  }
}

ctx_ptr_t get_ctx() {
  return ctx_ptr_t{gvContext()};
}

void Agraph_t_deleter::operator()(Agraph_t* g) const {
  if (g != nullptr) {
    agclose(g);
  }
}

graph_ptr_t create_graph(const std::string& name) {
  Agdesc_t dir = {1, 0, 0, 1};
  Agraph_t* g = agopen(STRDUP(name.c_str()), dir, nullptr);
  agattr(g, AGRAPH, STRDUP("rankdir"), STRDUP("RL"));
  return graph_ptr_t{g};
}

Agnode_t* add_node(graph_ptr_t& g,
                   int node_id,
                   const std::string& name,
                   const std::string& target_type,
                   const std::string& shape_type,
                   const std::string& hex_colour,
                   const std::string& obj_project_rel_dir_path) {
  if (g == nullptr) {
    return nullptr;
  }

  Agnode_t* node = agnode(g.get(), STRDUP(name.c_str()), 1);
  agsafeset(node, STRDUP("target_type"), STRDUP(target_type.c_str()),
            STRDUP(""));
  agsafeset(node, STRDUP("shape"), STRDUP(shape_type.c_str()), STRDUP(""));
  agsafeset(node, STRDUP("fillcolor"), STRDUP(hex_colour.c_str()), STRDUP(""));
  agsafeset(node, STRDUP("style"), STRDUP("filled"), STRDUP(""));

  agsafeset(node, STRDUP("obj_project_rel_dir_path"),
            STRDUP(obj_project_rel_dir_path.c_str()), STRDUP(""));

  char id_str[16];
  snprintf(id_str, sizeof(id_str), "%d", node_id);
  agsafeset(node, STRDUP("id"), id_str, STRDUP(""));
  return node;
}

Agedge_t* add_edge(graph_ptr_t& g, Agnode_t* src, Agnode_t* tgt) {
  return agedge(g.get(), src, tgt, nullptr, 1);
}

int get_node_id(Agnode_t* node) {
  char* id_str = agget(node, STRDUP("id"));
  if (id_str) {
    return std::stoi(id_str);
  }
  return -1;
}

LayoutResult get_layout_result(ctx_ptr_t& ctx, graph_ptr_t& g) {
  int node_count = 0;
  auto g_ptr = g.get();
  for (Agnode_t* n = agfstnode(g_ptr); n; n = agnxtnode(g_ptr, n)) {
    node_count++;
  }

  int edge_count = 0;
  for (Agnode_t* n = agfstnode(g_ptr); n; n = agnxtnode(g_ptr, n)) {
    for (Agedge_t* e = agfstout(g_ptr, n); e; e = agnxtout(g_ptr, e)) {
      edge_count++;
    }
  }

  std::vector<NodeItem> nodes;
  nodes.reserve(node_count);
  std::vector<EdgeItem> edges;
  edges.reserve(edge_count);

  std::unordered_map<Agnode_t*, int> node_indices;

  int node_index = 0;
  for (Agnode_t* n = agfstnode(g_ptr); n; n = agnxtnode(g_ptr, n)) {
    NodeItem item;
    item.id = get_node_id(n);
    item.name = STRDUP(agnameof(n));
    item.target_type = STRDUP(agget(n, STRDUP("target_type")));
    item.shape_type = STRDUP(agget(n, STRDUP("shape")));
    item.hex_colour = STRDUP(agget(n, STRDUP("fillcolor")));
    item.obj_project_rel_dir_path =
        STRDUP(agget(n, STRDUP("obj_project_rel_dir_path")));

    item.x = ND_coord(n).x;
    item.y = ND_coord(n).y;
    // Convert from inches to points
    item.width = ND_width(n) * 72;
    item.height = ND_height(n) * 72;

    node_indices[n] = node_index;

    node_index++;
    nodes.push_back(item);
  }

  int edge_index = 0;
  for (Agnode_t* n = agfstnode(g_ptr); n; n = agnxtnode(g_ptr, n)) {
    for (Agedge_t* e = agfstout(g_ptr, n); e; e = agnxtout(g_ptr, e)) {
      EdgeItem item;
      item.source_id = node_indices[agtail(e)];
      item.target_id = node_indices[aghead(e)];

      if (ED_spl(e) && ED_spl(e)->list) {
        for (int i = 0; i < ED_spl(e)->size; i++) {
          const bezier* bez = &(ED_spl(e)->list[i]);

          // Add all points (start, control points, end)
          for (int j = 0; j < bez->size; j++) {
            pointf pt = bez->list[j];
            item.splines.emplace_back(pt.x, pt.y);
          }
        }
      } else {
        item.splines.reserve(2);
        Agnode_t* src = agtail(e);
        Agnode_t* tgt = aghead(e);
        item.splines.emplace_back(ND_coord(src).x, -ND_coord(src).y);
        item.splines.emplace_back(ND_coord(tgt).x, -ND_coord(tgt).y);
      }

      edge_index++;
      edges.push_back(item);
    }
  }

  return LayoutResult{nodes, edges};
}

std::optional<LayoutResult> apply_layout(ctx_ptr_t& ctx,
                                         graph_ptr_t& g,
                                         const std::string& layout_engine) {
  if (gvLayout(ctx.get(), g.get(), STRDUP(layout_engine.c_str())) == 0) {
    auto layout_result = get_layout_result(ctx, g);
    gvFreeLayout(ctx.get(), g.get());
    return layout_result;
  }
  return std::nullopt;
}

}  // namespace iprm::gv
