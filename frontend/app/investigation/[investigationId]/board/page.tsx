"use client";

import { useMemo, useState } from "react";
import { useParams } from "next/navigation";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import ReactFlow, { addEdge, Background, Controls, Connection, Edge, Node } from "reactflow";
import "reactflow/dist/style.css";
import toast from "react-hot-toast";

import { AuthGuard } from "@/components/layout/auth-guard";
import { AppShell } from "@/components/layout/app-shell";
import { Button } from "@/components/ui/button";
import { Panel } from "@/components/ui/panel";
import { serializeBoard } from "@/lib/board-serializer";
import { api } from "@/services/api";

export default function BoardPage() {
  const params = useParams<{ investigationId: string }>();
  const id = Number(params.investigationId);
  const qc = useQueryClient();

  const clues = useQuery({ queryKey: ["clues", id], queryFn: () => api.clues(id) });
  const suspects = useQuery({ queryKey: ["suspects", id], queryFn: () => api.suspects(id) });
  const board = useQuery({ queryKey: ["board", id], queryFn: () => api.board(id) });

  const initialNodes: Node[] = useMemo(() => {
    if (board.data?.nodes?.length) {
      return board.data.nodes.map((n) => ({ id: n.id, type: "default", data: { label: n.label }, position: { x: n.x, y: n.y } }));
    }
    const clueNodes = (clues.data ?? []).map((c, idx) => ({
      id: `clue-${c.clue_slug}`,
      type: "default",
      data: { label: c.title },
      position: { x: 40 + (idx % 3) * 220, y: 70 + Math.floor(idx / 3) * 130 }
    }));
    const suspectNodes = (suspects.data ?? []).map((s, idx) => ({
      id: `suspect-${s.suspect_slug}`,
      type: "default",
      data: { label: s.suspect_slug },
      position: { x: 60 + (idx % 2) * 300, y: 420 + Math.floor(idx / 2) * 140 }
    }));
    return [...clueNodes, ...suspectNodes];
  }, [board.data, clues.data, suspects.data]);

  const initialEdges: Edge[] = useMemo(() => {
    return (board.data?.edges ?? []).map((e) => ({ id: e.id, source: e.source, target: e.target, label: e.label }));
  }, [board.data]);

  const [nodes, setNodes] = useState<Node[]>(initialNodes);
  const [edges, setEdges] = useState<Edge[]>(initialEdges);

  const save = useMutation({
    mutationFn: async () => api.saveBoard(id, serializeBoard(nodes, edges)),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["board", id] });
      toast.success("Board saved.");
    },
    onError: (error) => toast.error(error instanceof Error ? error.message : "Could not save board")
  });

  return (
    <AuthGuard>
      <AppShell investigationId={params.investigationId}>
        <Panel title="Evidence Board">
          <div className="mb-2 flex gap-2">
            <Button onClick={() => save.mutate()} disabled={save.isPending}>Save Board</Button>
            <Button className="bg-white/20 text-white" onClick={() => { setEdges([]); toast("Connections cleared"); }}>Reset Layout</Button>
          </div>
          <div className="h-[70vh] rounded-xl border border-white/15 bg-black/30">
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onConnect={(connection: Connection) => setEdges((eds) => addEdge(connection, eds))}
              onNodesChange={(changes) => {
                setNodes((prev) => {
                  let next = [...prev];
                  changes.forEach((change) => {
                    if (change.type === "position" && change.position) {
                      next = next.map((n) => (n.id === change.id ? { ...n, position: change.position ?? n.position } : n));
                    }
                  });
                  return next;
                });
              }}
              onEdgesChange={(changes) => {
                setEdges((prev) => {
                  const removeIds = new Set(changes.filter((c) => c.type === "remove").map((c) => c.id));
                  return prev.filter((e) => !removeIds.has(e.id));
                });
              }}
            >
              <Background />
              <Controls />
            </ReactFlow>
          </div>
        </Panel>
      </AppShell>
    </AuthGuard>
  );
}
