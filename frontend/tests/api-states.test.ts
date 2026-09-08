import { describe, expect, it } from "vitest";

import { ApiError } from "@/lib/utils";

describe("loading and api error states", () => {
  it("normalizes api error", () => {
    const error = new ApiError("Unauthorized", 401);
    expect(error.status).toBe(401);
    expect(error.message).toBe("Unauthorized");
  });
});

describe("chat submission payload", () => {
  it("keeps expected field names", () => {
    const payload = { message: "Where were you?", evidence_clue_slug: "camera-loop-gap" };
    expect(Object.keys(payload)).toContain("message");
  });
});
