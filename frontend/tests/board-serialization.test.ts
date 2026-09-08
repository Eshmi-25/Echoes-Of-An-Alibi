import { describe, expect, it } from "vitest";

import { serializeBoard } from "@/lib/board-serializer";

describe("evidence board serialization", () => {
  it("serializes nodes and edges", () => {
    const payload = serializeBoard(
      [{ id: "n1", position: { x: 10.3, y: 20.2 }, data: { label: "Clue" }, type: "default" }],
      [{ id: "e1", source: "n1", target: "n2", label: "linked" }]
    );
    expect(payload.nodes[0].x).toBe(10);
    expect(payload.edges[0].id).toBe("e1");
  });
});
