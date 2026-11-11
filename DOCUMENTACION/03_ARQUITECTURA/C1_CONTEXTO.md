## Propósito del nivel

El diagrama de contexto muestra SITRA-CGE como una caja negra, las personas que lo usan y los sistemas externos con los que se comunica. Fuente editable: `DIAGRAMAS/workspace.dsl` (Structurizr DSL, vista `contexto`).

## Diagrama

```{mermaid}
flowchart TB
  uai(["UAI<br/>[Persona]"])
  eje(["Ejecutor de unidad<br/>[Persona]"])
  rec(["Rectorado<br/>[Persona]"])
  cge(["Auditor CGE<br/>[Persona]"])
  dti(["Administrador DTI<br/>[Persona]"])
  sys["SITRA-CGE UNL<br/>[Sistema de software]<br/>Seguimiento de recomendaciones, evidencias,<br/>dictámenes, plazos y auditoría"]
  sso[["SSO institucional UNL<br/>[Sistema externo]"]]
  smtp[["Servidor SMTP institucional<br/>[Sistema externo]"]]
  cgeorg[["Contraloría General del Estado<br/>[Organización externa]"]]
  uai -->|Registra informes y recomendaciones, dictamina| sys
  eje -->|Registra hitos y carga evidencias PDF| sys
  rec -->|Consulta tablero y matriz| sys
  cge -->|Consulta auditoría, integridad y matriz| sys
  dti -->|Administra usuarios, roles, unidades y notificaciones| sys
  sys -->|Introspección de tokens · HTTPS| sso
  sys -->|Envía alertas · SMTP| smtp
  uai -.->|Entrega la matriz CSV fuera del sistema| cgeorg
  classDef ext fill:#eceff1,stroke:#607d8b,color:#263238
  classDef core fill:#1f4e79,stroke:#123,color:#fff
  class sso,smtp,cgeorg ext
  class sys core
```

## Elementos

| Elemento | Tipo | Relación con el sistema | Estado |
|---|---|---|---|
| UAI, Ejecutor, Rectorado, Auditor CGE, DTI | Personas | Usan la SPA según su rol | Implementado |
| SSO institucional | Sistema externo | El backend valida el token por introspección | Adaptador implementado; proveedor productivo no definido |
| SMTP institucional | Sistema externo | Entrega de alertas | Implementado (backend de consola en desarrollo) |
| CGE | Organización externa | Recibe la matriz; **no hay integración técnica** | Fuera de alcance |
