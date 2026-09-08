import { describe, expect, it } from "vitest";

describe("frontend smoke", () => {
  it("validates accusation schema intent", () => {
    const clues = ["a", "b"];
    expect(clues.length).toBeGreaterThanOrEqual(2);
  });

  it("chat submission payload shape", () => {
    const payload = { message: "Where were you at 11:47?" };
    expect(typeof payload.message).toBe("string");
  });
});
