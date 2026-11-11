## Propósito

Esta matriz lista los artefactos documentales que corresponden a SITRA-CGE UNL, la evidencia encontrada al iniciar la auditoría (Fase 0) y la acción decidida. El estado final de cada artefacto está en la matriz de cierre (`DOCUMENTACION/12_CIERRE/INFORME_FINAL.md`).

Estados: **Existe** · **Parcial** · **Desactualizado** · **No existe** · **No aplica**.

| ID | Elemento | Evidencia encontrada | Ubicación | Estado | Acción |
|---|---|---|---|---|---|
| MC-01 | Introducción y contexto | Contexto en spec y README | `spec.md`, `README.md` | Parcial | Redactar `01_GENERAL/INTRODUCCION.md` |
| MC-02 | Problema y justificación | Delimitación y riesgo crítico | `docs/problem-definition.md` | Existe | Consolidar en `PROBLEMA_Y_JUSTIFICACION.md` |
| MC-03 | Objetivos y alcance | Objetivo del incremento, alcance, fuera de alcance | `spec.md` | Parcial | Redactar `OBJETIVOS_Y_ALCANCE.md` |
| MC-04 | Actores | Tabla de actores | `spec.md`, `docs/architecture/sitra-cge.md` | Existe | Verificar contra RBAC y consolidar en `ACTORES.md` |
| MC-05 | Requisitos RF/RNF, HU, criterios | RF-001…024, RNF-001…013, HU1–6, BDD | `spec.md` | Existe | Resumir con estado de implementación en `REQUISITOS.md` |
| MC-06 | Matriz de trazabilidad | Método y 6 ejemplos | `docs/trazabilidad.md` | Parcial | Construir matriz RF→componente→prueba en `MATRIZ_TRAZABILIDAD.md` |
| MC-07 | Análisis de procesos | Máquina de estados textual | `README.md` | Parcial | Redactar `02_PROCESOS/ANALISIS_PROCESOS.md` |
| MC-08 | Diagramas BPMN 2.0.2 | — | — | No existe | Crear fuentes `.bpmn` y vista renderizada |
| MC-09 | Arquitectura general | Capas y límites modulares | `docs/architecture/sitra-cge.md` | Desactualizado | Corregir en `ARQUITECTURA_GENERAL.md` |
| MC-10 | C4 C1–C3 | Mermaid y texto | `docs/ARQUITECTURA.md` | Existe | Structurizr DSL + vistas Mermaid |
| MC-11 | C4 nivel código (UML) | Lista de carpetas | `docs/ARQUITECTURA.md` | Parcial | PlantUML (clases, secuencia) + vistas Mermaid |
| MC-12 | ADR | 11 ADR | `docs/adr/` | Existe | Consolidar y añadir recomendaciones de auditoría en `ADR.md` |
| MC-13 | Tecnologías y versiones | Requirements, package.json | manifiestos | Parcial | Verificar versiones instaladas en `TECNOLOGIAS.md` |
| MC-14 | Estructura del código | Árbol en README | `README.md` | Parcial | `ESTRUCTURA.md` |
| MC-15 | Componentes | Descripción breve por módulo | `docs/architecture/sitra-cge.md` | Parcial | `COMPONENTES.md` |
| MC-16 | Modelo de datos y ER | DDL lógico | `data-model.md` | Desactualizado | Derivar de modelos/migraciones en `MODELO_DATOS.md` |
| MC-17 | API general y endpoints | OpenAPI 3.0.3, Swagger | `backend/contracts/openapi.yaml` | Existe | Documentar en `05_API/` verificando roles en código |
| MC-18 | Contratos y envoltura | Envoltura universal y errores | `spec.md`, ADR-0007 | Existe | `CONTRATOS.md` |
| MC-19 | Integraciones externas | SSO, SMTP | `configuration.md` | Parcial | `INTEGRACIONES.md` con lo realmente implementado |
| MC-20 | Autenticación | JWT, SSO | ADR-0002, `configuration.md` | Desactualizado | `06_SEGURIDAD/AUTENTICACION.md` |
| MC-21 | Autorización | RBAC, BOLA | spec, ADR-0002 | Parcial | `AUTORIZACION.md` con matriz rol × operación |
| MC-22 | Riesgos y controles | Riesgo crítico normativo | `problem-definition.md` | Parcial | `RIESGOS_Y_CONTROLES.md` (OWASP) |
| MC-23 | Protección de datos | Redacción de logs, archivos privados | código | No existe | `PROTECCION_DATOS.md` |
| MC-24 | Estrategia de pruebas | Lista de validaciones | `manual-tecnico.md` | Parcial | `07_CALIDAD/ESTRATEGIA_PRUEBAS.md` |
| MC-25 | Inventario de pruebas | Archivos de prueba | `backend/tests`, `frontend/src/**/*.test.tsx` | Existe (código) | `PRUEBAS.md` |
| MC-26 | Resultados de pruebas | — | — | No existe | Ejecutar y registrar en `RESULTADOS.md` |
| MC-27 | Matriz de verificación | — | — | No existe | `MATRIZ_VERIFICACION.md` |
| MC-28 | Requisitos de instalación | Requisitos previos | `README.md` | Existe | `08_DESPLIEGUE/REQUISITOS.md` |
| MC-29 | Instalación y ejecución | Pasos detallados | `README.md` | Existe | `INSTALACION.md`, `EJECUCION.md` |
| MC-30 | Configuración | Variables | `.env.example`, `configuration.md` | Parcial | `CONFIGURACION.md` marcando variables sin efecto |
| MC-31 | Docker y despliegue | Dockerfile, Compose | raíz y `backend/` | Parcial | `DESPLIEGUE.md` (sin producción real) |
| MC-32 | CI/CD | Workflow CI | `.github/workflows/ci.yml` | Existe | Documentar en `DESPLIEGUE.md` |
| MC-33 | Problemas frecuentes | 4 problemas | `README.md` | Existe | `PROBLEMAS_FRECUENTES.md` ampliado |
| MC-34 | Operación y mantenimiento | Lista breve | `docs/ARQUITECTURA.md` | Parcial | `09_OPERACION/OPERACION_Y_MANTENIMIENTO.md` |
| MC-35 | Referencias y bibliografía | — | — | No existe | `REFERENCIAS.md` + `references.bib` |
| MC-36 | Declaración de uso de IA | Agentes Spec Kit/Copilot en el repo | `.github/agents/`, `.specify/` | Parcial | Declarar en referencias |
| MC-37 | Portal Quarto | — | — | No existe | `docs/_quarto.yml` + páginas `.qmd` |
| MC-38 | Workflow GitHub Pages | Solo CI | `.github/workflows/` | No existe | `publish-quarto.yml` |
| MC-39 | Guía de publicación | — | — | No existe | `11_PUBLICACION_GITHUB_PAGES.md` |
| MC-40 | Informe final | — | — | No existe | `12_CIERRE/INFORME_FINAL.md` |
| MC-41 | Manual de usuario | Guía por rol | `docs/manual-usuario.md` | Parcial | Fuera del alcance de este encargo (técnico); se enlaza sin reescribir |
| MC-42 | Diseño de interfaz / capturas | — | — | No existe | No se generan capturas: requieren ejecutar la aplicación con datos; se declara limitación |
