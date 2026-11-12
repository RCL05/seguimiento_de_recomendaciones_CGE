"""Rendimiento de reportes (RNF): tablero ≤ 3 s y matriz CGE ≤ 5 s con un volumen realista.

Se mide el tiempo real de las peticiones HTTP sobre 500 recomendaciones y se verifica
que la cantidad de consultas SQL no crezca con el número de filas (sin N+1).
"""

import time
from datetime import timedelta

import pytest
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from backend.modules.recomendaciones.models import InformeCGE, Recomendacion
from backend.modules.usuarios.models import Usuario
from tests import factories
from tests.auth_helpers import authenticated_headers

pytestmark = pytest.mark.django_db

ESTADOS = [
    Recomendacion.Estado.PENDIENTE,
    Recomendacion.Estado.EN_PROCESO,
    Recomendacion.Estado.EN_VALIDACION,
    Recomendacion.Estado.CUMPLIDA,
]


def _sembrar(cantidad: int, prefijo: str) -> None:
    uai = factories.usuario(Usuario.Rol.UAI, "uai-perf", "UAI")
    unidades = [factories.unidad(f"DEP-{i}") for i in range(10)]
    informe = InformeCGE.objects.create(
        numero_informe=f"INF-PERF-{prefijo}",
        periodo_auditado="2026",
        fecha_notificacion=timezone.localdate(),
        pdf_informe_url="https://example.test/inf.pdf",
        creado_por=uai,
    )
    hoy = timezone.localdate()
    Recomendacion.objects.bulk_create(
        Recomendacion(
            informe=informe,
            numero_recomendacion=f"{prefijo}-{i}",
            descripcion="Recomendación de carga",
            prioridad="MEDIA",
            unidad_responsable=unidades[i % len(unidades)],
            plazo_legal_dias=30,
            fecha_vencimiento_legal=hoy + timedelta(days=(i % 60) - 20),
            estado=ESTADOS[i % len(ESTADOS)],
        )
        for i in range(cantidad)
    )


def _medir(ruta, headers):
    with CaptureQueriesContext(connection) as consultas:
        inicio = time.perf_counter()
        response = Client().get(ruta, **headers)
        duracion = time.perf_counter() - inicio
    assert response.status_code == 200, response.content
    return response, duracion, len(consultas)


@pytest.fixture
def uai():
    return authenticated_headers("UAI", "uai-perf", "UAI")


def test_tablero_responde_en_menos_de_3_segundos(uai):
    _sembrar(500, "T")

    response, duracion, _ = _medir("/api/v1/reportes/tablero", uai)

    assert duracion <= 3.0
    assert response.json()["success"] is True


def test_matriz_cge_se_exporta_en_menos_de_5_segundos_con_todas_las_filas(uai):
    _sembrar(500, "M")

    response, duracion, _ = _medir("/api/v1/reportes/matriz-cge", uai)

    assert duracion <= 5.0
    filas = response.content.decode("utf-8-sig").strip().splitlines()
    assert len(filas) == 501  # encabezado + 500 recomendaciones


@pytest.mark.parametrize("ruta", ["/api/v1/reportes/tablero", "/api/v1/reportes/matriz-cge"])
def test_las_consultas_sql_no_crecen_con_el_volumen(uai, ruta):
    _sembrar(20, "A")
    _, _, pocas = _medir(ruta, uai)

    _sembrar(200, "B")
    _, _, muchas = _medir(ruta, uai)

    assert muchas <= pocas + 2
