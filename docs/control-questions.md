# Preguntas de Control

## 1. ¿Por qué el equipo seleccionó esta estrategia de ramas y cómo apoyará el trabajo colaborativo?

Se seleccionó una estrategia basada en main, develop y ramas por características (feature/*). main refleja el estado estable de producción, develop integra los avances del equipo y las ramas feature/* permiten que los 4 integrantes trabajen simultáneamente sin generar conflictos de código o sobreescribir la documentación del otro.

## 2. ¿Qué debe contener el README para que otro integrante pueda reproducir el entorno?

Debe incluir: requisitos previos (versiones de Node/Python/Git), instrucciones de clonación del repositorio, comandos para instalación de dependencias, variables de entorno de ejemplo (env.example), comando de ejecución del servidor local y pasos de verificación rápida.

## 3. ¿Qué diferencia existe entre constitution, specify, clarify, plan y tasks dentro del flujo SDD?

- constitution: Define las reglas de gobierno, principios arquitectónicos y estándares del equipo.
- specify: Describe qué problema se resuelve, alcance, requisitos y criterios de éxito sin detallar aún implementación.
- clarify: Registra las dudas, ambigüedades resueltas y preguntas sobre la lógica de negocio o normativa.
- plan: Define la estrategia de diseño, arquitectura, modelos de datos y flujo de trabajo.
- tasks: Desglosa el plan en unidades de trabajo ejecutables y asignables.

## 4. ¿Cuál es el problema delimitado y qué elementos quedaron fuera del alcance inicial?

El problema es la falta de trazabilidad y automatización en el cumplimiento de recomendaciones emitidas por la CGE a la UNL. Queda fuera del alcance inicial la sincronización automática vía API con los servidores centrales de la CGE y la gestión de responsabilidades penales/judiciales asociadas.

## 5. ¿Qué riesgo considera el equipo más relevante en esta fase y por qué?

El riesgo más crítico es el Modelado Incorrecto del Flujo de Estados de Cumplimiento (riesgo de lógica de negocio), ya que si no se alinean las validaciones internas (UAI) con la normativa de la CGE (Acuerdo 010-CG-2022), el sistema podría dar por "cumplida" una recomendación que normativamente aún está rechazada o pendiente.