import { render } from "@testing-library/react";
import { axe, toHaveNoViolations } from "jest-axe";
import MainNavbar from "../MainNavbar";

expect.extend(toHaveNoViolations);

describe("MainNavbar accesibilidad", () => {
  it("no tiene violaciones WCAG AA", async () => {
    const { container } = render(<MainNavbar />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
