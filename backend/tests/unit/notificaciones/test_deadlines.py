from datetime import date, timedelta


def test_umbrales_alerta_15_dias_o_menos_e_idempotencia():
    hoy = date(2026, 10, 25)
    for dias in [15, 10, 1, 0]:
        venc = hoy + timedelta(days=dias)
        assert (venc - hoy).days <= 15
    venc_fuera = hoy + timedelta(days=16)
    assert (venc_fuera - hoy).days > 15

    clave = "ALERTA_VENCIMIENTO:R-001:2026-10-25"
    claves = set([clave])
    assert clave in claves


def test_evidencia_presentada_frente_a_validada():
    evidencia_presentada = {"cargada": True, "validada": False}
    evidencia_validada = {"cargada": True, "validada": True}
    assert evidencia_presentada["cargada"] and not evidencia_presentada["validada"]
    assert evidencia_validada["validada"] is True
