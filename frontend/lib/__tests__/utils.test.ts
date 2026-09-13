import { describe, it, expect } from "vitest";
import { cn } from "@/lib/utils";

describe("cn", () => {
  it("merges class names", () => {
    expect(cn("a", "b")).toBe("a b");
  });

  it("drops falsy values", () => {
    expect(cn("a", false, undefined, null, "b")).toBe("a b");
  });

  it("resolves conflicting tailwind classes to the last one", () => {
    // tailwind-merge should keep only the last conflicting utility
    expect(cn("px-2", "px-4")).toBe("px-4");
  });

  it("supports conditional object syntax via clsx", () => {
    expect(cn("base", { active: true, hidden: false })).toBe("base active");
  });
});
