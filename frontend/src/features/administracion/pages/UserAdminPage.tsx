import { FormEvent, useEffect, useState } from "react";

import { AdminUser, api, ApiError, Role, Unit } from "../../../api/client";
import { ROLES, ROLE_LABELS } from "../../../components/roles";
import { Toast } from "../../../components/Toast";
import { PageHeader } from "../../../components/ui";
import { useToast } from "../../../hooks/useToast";

type UserEdit = {
  rol: Role;
  unidad_codigo: string;
};

function editKey(user: AdminUser): UserEdit {
  return { rol: user.rol, unidad_codigo: user.unidad_codigo ?? "" };
}

export function UserAdminPage() {
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [units, setUnits] = useState<Unit[]>([]);
  const [edits, setEdits] = useState<Record<string, UserEdit>>({});
  const [loading, setLoading] = useState(true);
  const [savingId, setSavingId] = useState("");
  const [creatingUnit, setCreatingUnit] = useState(false);
  const { toast, showToast, dismissToast } = useToast();

  useEffect(() => {
    let active = true;
    Promise.all([api.listUsers(), api.listUnits()])
      .then(([loadedUsers, loadedUnits]) => {
        if (!active) return;
        setUsers(loadedUsers);
        setUnits(loadedUnits);
        setEdits(Object.fromEntries(loadedUsers.map((user) => [user.id, editKey(user)])));
      })
      .catch((caught) =>
        showToast(
          caught instanceof ApiError ? caught.message : "No se pudo cargar la administración.",
          "error",
        ),
      )
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [showToast]);

  function updateEdit(userId: string, patch: Partial<UserEdit>) {
    setEdits((current) => ({
      ...current,
      [userId]: { ...(current[userId] ?? { rol: "EJECUTOR", unidad_codigo: "" }), ...patch },
    }));
  }

  async function saveUser(user: AdminUser) {
    const edit = edits[user.id] ?? editKey(user);
    const payload: { rol?: Role; unidad_codigo?: string } = {};
    if (edit.rol !== user.rol) payload.rol = edit.rol;
    if (edit.unidad_codigo && edit.unidad_codigo !== (user.unidad_codigo ?? "")) {
      payload.unidad_codigo = edit.unidad_codigo;
    }
    if (Object.keys(payload).length === 0) {
      showToast("El usuario no tiene cambios por guardar.");
      return;
    }
    setSavingId(user.id);
    try {
      const updated = await api.updateUser(user.id, payload);
      setUsers((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setEdits((current) => ({ ...current, [updated.id]: editKey(updated) }));
      showToast("Usuario actualizado y auditado.");
    } catch (caught) {
      showToast(
        caught instanceof ApiError ? caught.message : "No se pudo actualizar el usuario.",
        "error",
      );
    } finally {
      setSavingId("");
    }
  }

  async function createUnit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const codigo = String(data.get("codigo") ?? "").trim();
    const nombre = String(data.get("nombre") ?? "").trim();
    setCreatingUnit(true);
    try {
      const unit = await api.createUnit({ codigo, nombre });
      setUnits((current) =>
        [...current.filter((item) => item.codigo !== unit.codigo), unit].sort((left, right) =>
          left.codigo.localeCompare(right.codigo),
        ),
      );
      form.reset();
      showToast("Unidad registrada y auditada.");
    } catch (caught) {
      showToast(caught instanceof ApiError ? caught.message : "No se pudo registrar la unidad.", "error");
    } finally {
      setCreatingUnit(false);
    }
  }

  return (
    <>
      <PageHeader
        eyebrow="Administración DTI"
        title="Usuarios y unidades"
        description="Asigne roles, cambie la unidad orgánica de una cuenta o registre nuevas unidades. Cada cambio queda auditado."
      />

      <section className="card" aria-labelledby="users-title">
        <div className="card-header">
          <div>
            <h2 id="users-title">Cuentas institucionales</h2>
            <p>Los roles definen qué secciones y operaciones puede ejecutar cada cuenta.</p>
          </div>
        </div>

        {loading ? (
          <p role="status" className="muted">
            Cargando usuarios...
          </p>
        ) : users.length === 0 ? (
          <p className="muted">No hay cuentas registradas.</p>
        ) : (
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Correo</th>
                  <th>Nombre</th>
                  <th>Rol</th>
                  <th>Unidad orgánica</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((user) => {
                  const edit = edits[user.id] ?? editKey(user);
                  return (
                    <tr key={user.id}>
                      <td>{user.correo_institucional}</td>
                      <td>{user.nombres}</td>
                      <td>
                        <select
                          aria-label={`Rol de ${user.correo_institucional}`}
                          value={edit.rol}
                          onChange={(event) => updateEdit(user.id, { rol: event.target.value as Role })}
                        >
                          {ROLES.map((role) => (
                            <option key={role} value={role}>
                              {ROLE_LABELS[role]}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <select
                          aria-label={`Unidad de ${user.correo_institucional}`}
                          value={edit.unidad_codigo}
                          onChange={(event) => updateEdit(user.id, { unidad_codigo: event.target.value })}
                        >
                          <option value="">Sin unidad</option>
                          {units.map((unit) => (
                            <option key={unit.id} value={unit.codigo}>
                              {unit.codigo} · {unit.nombre}
                            </option>
                          ))}
                        </select>
                      </td>
                      <td>
                        <span className={`badge ${user.activo ? "state-cumplida" : "danger"}`}>
                          {user.activo ? "Activo" : "Inactivo"}
                        </span>
                      </td>
                      <td>
                        <button
                          type="button"
                          className="secondary"
                          disabled={savingId === user.id}
                          onClick={() => void saveUser(user)}
                        >
                          {savingId === user.id ? "Guardando..." : "Guardar"}
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="card" aria-labelledby="units-title">
        <div className="card-header">
          <div>
            <h2 id="units-title">Unidades orgánicas</h2>
            <p>Catálogo usado para asignar recomendaciones y responsables.</p>
          </div>
        </div>

        <div className="split">
          <div>
            {units.length === 0 ? (
              <p className="muted">Sin unidades registradas.</p>
            ) : (
              <ul className="evidence-list">
                {units.map((unit) => (
                  <li key={unit.id}>
                    <div>
                      <strong>{unit.codigo}</strong>
                      <small className="muted">{unit.nombre}</small>
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          <form className="form-grid" onSubmit={createUnit}>
            <h3>Registrar o renombrar unidad</h3>
            <label>
              Código
              <input name="codigo" maxLength={50} required placeholder="DEP-B" />
            </label>
            <label>
              Nombre
              <input name="nombre" maxLength={200} required placeholder="Departamento B" />
            </label>
            <div className="form-footer">
              <button type="submit" disabled={creatingUnit}>
                {creatingUnit ? "Guardando..." : "Guardar unidad"}
              </button>
            </div>
          </form>
        </div>
      </section>

      <Toast toast={toast} onClose={dismissToast} />
    </>
  );
}
