/*
 * SITRA-CGE UNL — Modelo C4 (niveles 1 a 3) en Structurizr DSL.
 * Fuente editable. Renderizar con Structurizr Lite / CLI:
 *   docker run -it --rm -p 8080:8080 -v "$PWD":/usr/local/structurizr structurizr/lite
 * Estado verificado contra el código de la rama feature/sdd-spec-kit-structure (2026-11-10).
 */
workspace "SITRA-CGE UNL" "Seguimiento de recomendaciones de la Contraloría General del Estado para la Universidad Nacional de Loja" {

    !identifiers hierarchical

    model {
        uai = person "UAI" "Unidad de Auditoría Interna: registra informes y recomendaciones, revisa evidencias y dictamina."
        ejecutor = person "Ejecutor de unidad" "Responsable de una unidad orgánica: registra hitos y carga evidencias PDF."
        rectorado = person "Rectorado" "Máxima autoridad: consulta el tablero ejecutivo y la matriz."
        auditorCge = person "Auditor CGE" "Consulta de solo lectura: auditoría, integridad y matriz."
        dti = person "Administrador DTI" "Gestiona usuarios, roles, unidades y notificaciones."

        sso = softwareSystem "SSO institucional UNL" "Proveedor de identidad; el sistema usa introspección OAuth2." "Externo"
        smtp = softwareSystem "Servidor SMTP institucional" "Entrega de alertas por correo." "Externo"
        cge = softwareSystem "Contraloría General del Estado" "Recibe la matriz de cumplimiento (sin integración técnica)." "Externo"

        sitra = softwareSystem "SITRA-CGE UNL" "Registro, ejecución, validación y auditoría de recomendaciones CGE." {
            spa = container "SPA web" "Interfaz por rol." "React 19, TypeScript, Vite 6" "Navegador"
            api = container "API REST" "Casos de uso, autorización, auditoría y contrato OpenAPI." "Python, Django 5.2, DRF 3.18" {
                auth = component "core/auth" "Autenticación JWT Bearer y permisos por rol." "DRF BaseAuthentication / BasePermission"
                apiCore = component "core/api" "Vista base, envoltura universal, catálogo de errores, request_id, /health/." "Django / DRF"
                audit = component "core/audit" "Bitácora append-only AuditLog y record_audit." "Django ORM"
                usuarios = component "usuarios" "Login SSO, emisión JWT, usuarios y unidades." "Módulo Django"
                informes = component "informes_cge" "Registro y consulta de informes CGE." "Módulo Django"
                recomendaciones = component "recomendaciones" "Máquina de estados, plan de acción, dictamen, reapertura, vencimiento." "Módulo Django"
                evidencias = component "evidencias" "Carga en flujo, anulación, descarga autorizada e integridad SHA-256." "Módulo Django"
                notificaciones = component "notificaciones" "Alertas, vencimientos, preferencias, configuración y comando evaluar_plazos." "Módulo Django"
                reportes = component "reportes" "KPIs, tablero ejecutivo, matriz CSV y consulta de auditoría." "Módulo Django"
            }
            scheduler = container "Programador de plazos" "Ejecuta manage.py evaluar_plazos periódicamente." "Imagen del backend / cron"
            db = container "Base de datos" "Datos transaccionales y bitácora." "SQLite (dev) / PostgreSQL 16" "BaseDatos"
            files = container "Almacenamiento de PDF" "Evidencias e informes; no se publica como estático." "Sistema de archivos (MEDIA_ROOT)" "BaseDatos"
            docs = container "Servidor de documentación" "Renderiza docs/*.md." "Quart 0.23"
        }

        uai -> sitra.spa "Registra, revisa y dictamina"
        ejecutor -> sitra.spa "Registra hitos y carga evidencias"
        rectorado -> sitra.spa "Consulta tablero y matriz"
        auditorCge -> sitra.spa "Consulta auditoría e integridad"
        dti -> sitra.spa "Administra identidad y notificaciones"
        uai -> cge "Entrega la matriz CSV" "Fuera del sistema"

        sitra.spa -> sitra.api "Invoca" "HTTPS/JSON, Bearer JWT"
        sitra.api -> sitra.db "Lee y escribe" "ORM"
        sitra.api -> sitra.files "Guarda y lee PDF" "Flujo de bytes"
        sitra.api -> sso "Introspección de token" "HTTPS"
        sitra.api -> smtp "Envía alertas" "SMTP/STARTTLS"
        sitra.scheduler -> sitra.db "Evalúa plazos" "ORM"
        sitra.scheduler -> smtp "Envía alertas" "SMTP"

        sitra.spa -> sitra.api.usuarios "POST /sesiones"
        sitra.spa -> sitra.api.recomendaciones "recomendaciones, hitos, dictamenes"
        sitra.spa -> sitra.api.evidencias "evidencias, archivo, integridad"
        sitra.spa -> sitra.api.informes "informes"
        sitra.spa -> sitra.api.notificaciones "notificaciones, configuracion"
        sitra.spa -> sitra.api.reportes "dashboard, tablero, matriz, auditoria"
        sitra.api.usuarios -> sso "Introspección"
        sitra.api.auth -> sitra.api.usuarios "Resuelve Usuario activo"
        sitra.api.informes -> sitra.api.recomendaciones "Usa modelos InformeCGE"
        sitra.api.evidencias -> sitra.api.recomendaciones "Usa modelos y caso de uso de carga"
        sitra.api.notificaciones -> sitra.api.recomendaciones "Lee plazos y estados"
        sitra.api.reportes -> sitra.api.recomendaciones "Agrega indicadores"
        sitra.api.reportes -> sitra.api.audit "Consulta bitácora"
        sitra.api.recomendaciones -> sitra.api.audit "Registra eventos"
        sitra.api.evidencias -> sitra.files "Lee/escribe PDF"
        sitra.api.notificaciones -> smtp "Envía correo"
        sitra.api.audit -> sitra.db "INSERT audit_logs"
    }

    views {
        systemContext sitra "contexto" {
            include *
            autoLayout lr
        }
        container sitra "contenedores" {
            include *
            autoLayout lr
        }
        component sitra.api "componentesApi" {
            include *
            autoLayout tb
        }
        styles {
            element "Person" {
                shape Person
                background #1f4e79
                color #ffffff
            }
            element "Software System" {
                background #2e75b6
                color #ffffff
            }
            element "Externo" {
                background #9e9e9e
            }
            element "Container" {
                background #5b9bd5
                color #ffffff
            }
            element "BaseDatos" {
                shape Cylinder
            }
            element "Navegador" {
                shape WebBrowser
            }
            element "Component" {
                background #deebf7
                color #000000
            }
        }
    }
}
