import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { SkillBadge } from "@/components/ui/SkillBadge";

describe("SkillBadge", () => {
  it("renders the label", () => {
    render(<SkillBadge label="Python" />);
    expect(screen.getByText("Python")).toBeInTheDocument();
  });

  it("applies matched styling", () => {
    render(<SkillBadge label="Python" state="matched" />);
    expect(screen.getByText("Python").closest("span")).toHaveClass("text-signal-good");
  });

  it("applies missing styling", () => {
    render(<SkillBadge label="AWS" state="missing" />);
    expect(screen.getByText("AWS").closest("span")).toHaveClass("text-signal-bad");
  });

  it("defaults to neutral styling when no state given", () => {
    render(<SkillBadge label="Docker" />);
    expect(screen.getByText("Docker").closest("span")).toHaveClass("text-text-muted");
  });
});
