import type { Edge, Node } from "reactflow";

import type { BoardPayload } from "@/types/api";

export function serializeBoard(nodes: Node[], edges: Edge[]): BoardPayload {
  return {
    nodes: nodes.map((n) => ({
      id: n.id,
      type: String(n.type ?? "default"),
      label: String((n.data as { label?: string } | undefined)?.label ?? n.id),
      x: Math.round(n.position.x),
      y: Math.round(n.position.y),
      extra: {}
    })),
    edges: edges.map((e) => ({
      id: e.id,
      source: e.source,
      target: e.target,
      label: String(e.label ?? "")
    }))
  };
}
