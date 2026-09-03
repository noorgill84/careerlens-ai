import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ScoreRing } from "@/components/charts/ScoreRing";

describe("ScoreRing", () => {
  it("renders a rounded score", () => {
    render(<ScoreRing score={87.6} />);
    expect(screen.getByText("88")).toBeInTheDocument();
  });

  it("clamps scores above 100 down to 100", () => {
    render(<ScoreRing score={150} />);
    expect(screen.getByText("100")).toBeInTheDocument();
  });

  it("clamps negative scores up to 0", () => {
    render(<ScoreRing score={-20} />);
    expect(screen.getByText("0")).toBeInTheDocument();
  });

  it("renders an optional label", () => {
    render(<ScoreRing score={70} label="ATS" />);
    expect(screen.getByText("ATS")).toBeInTheDocument();
  });
});
