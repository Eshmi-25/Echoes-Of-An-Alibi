import { describe, expect, it } from "vitest";

import { accusationSchema, loginSchema } from "@/lib/validation";

describe("login form validation", () => {
  it("rejects short password", () => {
    const result = loginSchema.safeParse({ username_or_email: "det", password: "short" });
    expect(result.success).toBe(false);
  });
});

describe("final accusation validation", () => {
  it("requires two supporting clues", () => {
    const result = accusationSchema.safeParse({
      attacker_slug: "a",
      thief_slug: "b",
      motive: "money",
      supporting1: "",
      supporting2: "",
      explanation: "too short"
    });
    expect(result.success).toBe(false);
  });
});
