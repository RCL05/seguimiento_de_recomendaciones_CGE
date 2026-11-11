import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { api } from "../../../api/client";
import { UserAdminPage } from "./UserAdminPage";

vi.mock("../../../api/client", () => ({
  api: {
    listUsers: vi.fn(),
    listUnits: vi.fn(),
    updateUser: vi.fn(),
    createUnit: vi.fn(),
  },
  ApiError: class ApiError extends Error {},
}));

const users = [
  {
    id: "u-1",
    correo_institucional: "ejecutor@unl.edu.ec",
    nombres: "Ejecutor Uno",
    rol: "EJECUTOR" as const,
    unidad_codigo: "DEP-A",
    activo: true,
  },
  {
    id: "u-2",
    correo_institucional: "uai@unl.edu.ec",
    nombres: "Auditor UAI",
    rol: "UAI" as const,
    unidad_codigo: null,
    activo: true,
  },
];

const units = [
  { id: "un-1", codigo: "DEP-A", nombre: "Departamento A" },
  { id: "un-2", codigo: "UAI", nombre: "Auditoría Interna" },
];

describe("UserAdminPage", () => {
  beforeEach(() => {
    vi.mocked(api.listUsers).mockReset();
    vi.mocked(api.listUnits).mockReset();
    vi.mocked(api.updateUser).mockReset();
    vi.mocked(api.createUnit).mockReset();
    vi.mocked(api.listUsers).mockResolvedValue(users);
    vi.mocked(api.listUnits).mockResolvedValue(units);
  });

  it("lista las cuentas institucionales y sus unidades", async () => {
    render(<UserAdminPage />);

    expect(await screen.findByText("ejecutor@unl.edu.ec")).toBeInTheDocument();
    expect(screen.getByText("Auditor UAI")).toBeInTheDocument();
    expect(screen.getByLabelText("Rol de ejecutor@unl.edu.ec")).toHaveValue("EJECUTOR");
    expect(screen.getByLabelText("Unidad de uai@unl.edu.ec")).toHaveValue("");
  });

  it("envía solo los cambios de rol y unidad", async () => {
    vi.mocked(api.updateUser).mockResolvedValue({ ...users[0], rol: "UAI", unidad_codigo: "UAI" });
    const user = userEvent.setup();
    render(<UserAdminPage />);

    await user.selectOptions(await screen.findByLabelText("Rol de ejecutor@unl.edu.ec"), "UAI");
    await user.selectOptions(screen.getByLabelText("Unidad de ejecutor@unl.edu.ec"), "UAI");
    await user.click(screen.getAllByRole("button", { name: "Guardar" })[0]);

    expect(api.updateUser).toHaveBeenCalledWith("u-1", { rol: "UAI", unidad_codigo: "UAI" });
  });

  it("registra una nueva unidad orgánica", async () => {
    vi.mocked(api.createUnit).mockResolvedValue({
      id: "un-3",
      codigo: "DEP-B",
      nombre: "Departamento B",
    });
    const user = userEvent.setup();
    render(<UserAdminPage />);

    await screen.findByText("Departamento A");
    await user.type(screen.getByLabelText("Código"), "DEP-B");
    await user.type(screen.getByLabelText("Nombre"), "Departamento B");
    await user.click(screen.getByRole("button", { name: "Guardar unidad" }));

    expect(api.createUnit).toHaveBeenCalledWith({ codigo: "DEP-B", nombre: "Departamento B" });
    expect(await screen.findByText("Departamento B")).toBeInTheDocument();
  });
});
