# Plan de Desarrollo de Software y Gestión del Proyecto

**Proyecto:** Plataforma Digital para la Gestión Integrada y Sostenible del Turismo en Santa Marta  
**Curso:** Arquitectura de Software — Experiencia Final de Diseño  
**Programa:** Ingeniería de Sistemas — Universidad del Magdalena  
**Versión:** 1.0  
**Fecha:** Agosto 2026  

---

## Tabla de Contenido

* [1. Condiciones Generales del Proyecto](#1-condiciones-generales-del-proyecto)
* [2. Cronograma de Ejecución y Plan de Fases](#2-cronograma-de-ejecución-y-plan-de-fases)
  * [2.1 Diagrama de Gantt (14 Semanas)](#21-diagrama-de-gantt-14-semanas)
  * [2.2 Desglose de Fases y Entregables Principales](#22-desglose-de-fases-y-entregables-principales)
* [3. Metodología de Desarrollo y Control de Calidad](#3-metodología-de-desarrollo-y-control-de-calidad)
  * [3.1 Selección y Justificación del Proceso de Desarrollo](#31-selección-y-justificación-del-proceso-de-desarrollo)
* [4. Modelo de Negocio y Sostenibilidad Institucional](#4-modelo-de-negocio-y-sostenibilidad-institucional)
* [5. Modelos Presupuestales y Asignación de Recursos](#5-modelos-presupuestales-y-asignación-de-recursos)
  * [5.1 Escenario A: Prototipo Académico y Validación Semestral (Austeridad FOSS / Free-Tier)](#51-escenario-a-prototipo-académico-y-validación-semestral-austeridad-foss--free-tier)
  * [5.2 Escenario B: Despliegue Piloto a Escala Real / Producción Institucional (Uso Total: USD 20.000)](#52-escenario-b-despliegue-piloto-a-escala-real--producción-institucional-uso-total-usd-20000)

---

## 1. Condiciones Generales del Proyecto

* **Equipo de Trabajo:** 5 ingenieros en formación, cada uno con un rol técnico y un rol de gestión (detalle de responsabilidades en el [Apéndice D del SRS](./Requirements_docIEEE.md#apéndice-d-equipo-de-trabajo-y-asignación-de-roles)):

| Integrante | Rol Técnico (Módulos) | Rol de Gestión |
|---|---|---|
| **Juan Francisco Gonzalez Pacheco** | Arquitecto Líder · Módulo 1 (IAM & Seguridad) + API Gateway | Product Owner |
| **Valentina Sarait Nieves Hernandez** | Desarrolladora Backend · Módulo 2 (Catálogo & GIS) | Scrum Master |
| **Andres Felipe Gamero Sanchez** | Desarrollador Backend · Módulo 3 (Reservas & Broker) | Líder de Calidad (QA) |
| **Alvaro David Ospino Sanchez** | Desarrollador Fullstack · Módulo 4 (Reseñas & Frontend Web) | Líder de UX y Documentación |
| **Luis Fernando Barraza Sanchez** | Especialista en IA · Módulos 5 & 6 (IA, Analítica & Gobernanza) | DevOps y Observabilidad |

* **Horizonte Temporal:** 14 semanas lectivas efectivas.
* **Paradigma & Estilo Arquitectónico:** Orientación a Objetos, Servicios RESTful, Arquitectura Hexagonal / Limpia en servicios individuales y Desacople Asíncrono Orientado a Eventos.
* **Tope Presupuestal Asignado:** **USD 20.000**.

---

## 2. Cronograma de Ejecución y Plan de Fases

### 2.1 Diagrama de Gantt (14 Semanas)

![Cronograma General de Ejecución](./Diagrama_Cronograma_Gantt.svg)

<details>
<summary><b>Ver especificación de código Mermaid del cronograma</b></summary>

```mermaid
gantt
    dateFormat  YYYY-MM-DD
    title Cronograma General de Ejecución — Plataforma de Turismo Santa Marta
    excludes    weekends

    section 1. Requerimientos
    Congelación de Especificación v2.0   :done,    req1, 2026-08-24, 2026-09-06
    section 2. Arquitectura
    Comparación y Selección de Patrones  :active,  arch1, 2026-09-07, 2026-09-20
    section 3. Diseño Detallado
    Diseño Arquitectónico y Mockups Figma:         des1, 2026-09-21, 2026-10-04
    section 4. Implementación
    Construcción Microservicios (Must)   :         dev1, 2026-10-05, 2026-11-15
    section 5. Validación
    Pruebas de Carga y Sustentación Final:         val1, 2026-11-16, 2026-11-29
```
</details>

### 2.2 Desglose de Fases y Entregables Principales

| Fase | Entregables Principales | Semanas | Fechas |
|---|---|---|---|
| **Fase 1: Requerimientos y Dominio** | Documento de Requerimientos consolidado (v2.0 / SRS ISO 29148). | Semanas 1–2 | 24 ago – 6 sep |
| **Fase 2: Comparación Arquitectónica** | [Informe de Selección de Patrones y Estilos Arquitectónicos](./Comparacion_Alternativas_Arquitectonicas.md). | Semanas 3–4 | 7 sep – 20 sep |
| **Fase 3: Diseño Arquitectónico** | Especificación técnica de interfaces, modelo de datos y wireframes UI en Figma. | Semanas 5–6 | 21 sep – 4 oct |
| **Fase 4: Construcción del Prototipo** | Microservicios, API Gateway, Broker y Base de Datos desplegados en contenedores (**Meta: $\ge 60\%$ de casos de uso *Must have***). | Semanas 7–12 | 5 oct – 15 nov |
| **Fase 5: Validación y Cierre** | Pruebas de carga, verificación de calidad, informe final y sustentación técnica. | Semanas 13–14 | 16 nov – 29 nov |

---

## 3. Metodología de Desarrollo y Control de Calidad

* **Marco de Trabajo:** Scrum adaptado para entornos académicos e interdisciplinarios, con ceremonias estructuradas en **sprints de 2 semanas** y seguimiento semanal de compromisos y dependencias técnicas.
* **Plataforma de Gestión:** GitHub Projects (tablero Kanban integrado directamente al control de versiones, ramas y *pull requests* de los repositorios de cada microservicio).
* **Control de Calidad:** Revisiones de código por pares (*Code Reviews*), linters estáticos automatizados y pruebas unitarias antes de la integración continua en ramas principales.

### 3.1 Selección y Justificación del Proceso de Desarrollo

Se evaluaron cuatro procesos de desarrollo frente a las condiciones reales del proyecto: 14 semanas lectivas, 5 integrantes con disponibilidad heterogénea (riesgo R-05), hitos académicos de entrega fijos, una arquitectura de 6 microservicios con propiedad 1:1 por integrante y un stack tecnológico aún en evaluación.

| Proceso | Ventaja para el proyecto | Limitación para el proyecto | Decisión |
|---|---|---|---|
| **Cascada** | Documentación completa por fase; coincide con la entrega formal del SRS. | Integración y pruebas solo al final; un error de diseño detectado en la semana 13 no tiene margen de corrección. | Descartado |
| **RUP** | Iterativo y guiado por casos de uso, coherente con la matriz UC1–UC38. | Sobrecarga de roles y artefactos desproporcionada para 5 personas y 14 semanas. | Descartado |
| **Kanban** | Flujo continuo, bajo costo de adopción. | Sin iteraciones con fecha fija, dificulta alinear el trabajo con los hitos académicos de cada fase. | Se adopta solo su tablero visual |
| **Scrum adaptado** | Sprints de duración fija alineables con las fases del cronograma, revisión incremental y roles explícitos. | Exige disciplina en ceremonias; se adapta reduciendo su duración. | **Seleccionado** |

**Justificación de la selección:**

* **Alineación con el cronograma:** Las 14 semanas se dividen en 7 sprints de 2 semanas; cada fase del Gantt (Sección 2) corresponde a uno o más sprints completos, de modo que cada hito académico coincide con una revisión de sprint.
* **Riesgo técnico controlado:** La curva de aprendizaje en microservicios (riesgo R-01) se aborda con incrementos funcionales tempranos, en lugar de descubrir problemas de integración al final del proyecto.
* **Trabajo en paralelo:** La propiedad 1:1 de cada microservicio permite que cada integrante gestione su propio backlog dentro del sprint, reduciendo dependencias (mitigación de R-05).
* **Requerimientos priorizados:** El backlog se ordena con la priorización MoSCoW del SRS; los requerimientos *Must* se implementan primero para asegurar la meta de $\ge 60\%$ de casos de uso *Must* en la Fase 4.
* **Roles definidos:** *Product Owner* y *Scrum Master* asignados a integrantes distintos (ver [Apéndice D del SRS](./Requirements_docIEEE.md#apéndice-d-equipo-de-trabajo-y-asignación-de-roles)).

**Adaptaciones al contexto académico:**

| Ceremonia | Frecuencia | Adaptación |
|---|---|---|
| Sprint Planning | Inicio de cada sprint | Máximo 1 hora; selección de historias del backlog por módulo. |
| Daily Scrum | 2–3 veces por semana | Asíncrona por canal de mensajería, por la disponibilidad heterogénea del equipo. |
| Sprint Review | Fin de cada sprint | Demostración del incremento, coincidiendo con los hitos de entrega del curso. |
| Sprint Retrospective | Fin de cada sprint | Breve (30 minutos), enfocada en bloqueos técnicos y de coordinación. |

---

## 4. Modelo de Negocio y Sostenibilidad Institucional

* **Financiación Pública y Enfoque Social:** La plataforma se concibe como un bien público digital financiado por la Entidad de Gestión del Destino (Alcaldía Distrital de Santa Marta / Secretaría de Turismo / INDETUR), orientada al fortalecimiento del sector y la protección del patrimonio natural y cultural.
* **Gratuidad Integral:** Acceso libre y gratuito tanto para turistas como para prestadores turísticos (hoteles, guías y restaurantes locales), eliminando comisiones e intermediaciones abusivas.
* **Exclusión de Pasarela de Pagos Interna:** Al operar bajo un modelo de "solicitud y confirmación de disponibilidad", no se procesan transferencias monetarias ni números de tarjetas bancarias dentro de la infraestructura, eliminando los costos de certificación PCI-DSS y minimizando vectores de ataque financiero. La decisión se documenta en [ADR-001](./ADR-001_Exclusion_Pasarela_Pagos.md).

---

## 5. Modelos Presupuestales y Asignación de Recursos

Para responder a la formulación económica del proyecto, se presentan **dos alternativas presupuestales exhaustivas**: el **Escenario A (Austeridad Académica / Prototipo Semestral)** y el **Escenario B (Despliegue Piloto Operativo a Escala Institucional — Uso Total de USD 20.000)**.

![Distribución Presupuestal Escenario B](./Diagrama_Distribucion_Presupuesto.svg)

---

### 5.1 Escenario A: Prototipo Académico y Validación Semestral (Austeridad FOSS / Free-Tier)

* **Objetivo:** Demostración de viabilidad técnica y cumplimiento de requerimientos del curso con máxima eficiencia de costos.
* **Presupuesto Estimado:** **USD ≈ 6.900** (dejando una holgura intencional de USD 13.100).

| Rubro | Estimado (USD) | Justificación Técnica |
|---|---|---|
| **Infraestructura Cloud Básica** | **4.500** | Cómputo en contenedores (ECS/Fargate o VPS Linux dedicado), base de datos gestionada y almacenamiento de archivos temporales durante 6 meses, apoyado en créditos académicos (AWS Educate / GitHub Student Pack). |
| **Servicios de Terceros & Notificaciones** | **1.200** | Uso de OpenStreetMap (100% gratuito sin licencia comercial) y servicios de correo transaccional en capa gratuita/baja escala (AWS SES / Mailtrap). |
| **Herramientas de Desarrollo y Colaboración** | **300** | Planes educativos en GitHub, Figma y Postman; margen para plugins o librerías específicas. |
| **Fondo de Contingencia Técnica (15%)** | **900** | Reserva ante eventuales picos de consumo o ajuste de instancias en fase de pruebas. |
| **TOTAL ESCENARIO A** | **≈ 6.900** | Modelo austero de desarrollo académico. |

---

### 5.2 Escenario B: Despliegue Piloto a Escala Real / Producción Institucional (Uso Total: USD 20.000)

* **Objetivo:** Ejecutar la totalidad de los **USD 20.000** en un plan integral de **despliegue piloto operativo a 12 meses** administrado por la Entidad de Gestión del Destino (Secretaría de Turismo de Santa Marta), asegurando alta disponibilidad, ciberseguridad rigurosa, digitalización de prestadores locales y adopción comunitaria.

| Componente de Inversión | Asignación (USD) | Desglose y Justificación Detallada |
|---|---|---|
| **1. Infraestructura Cloud de Alta Disponibilidad & Redundancia (12 Meses)** | **7.200** | • **Clúster de Cómputo Kubernetes / Docker:** Nodos redundantes en 2 zonas de disponibilidad para microservicios (USD 3.600 / año).<br>• **Clúster de Bases de Datos PostgreSQL Multi-AZ & MongoDB:** Réplicas de lectura y alta disponibilidad con backups automáticos diarios (USD 2.200 / año).<br>• **Almacenamiento Distribuido (S3/Object Storage):** Repositorio cifrado para documentos de prestadores (RNT, RUT) y multimedia (USD 600 / año).<br>• **Red de Entrega de Contenidos (CDN) y WAF:** Mitigación DDoS y aceleración de assets estáticos y tiles de mapas OSM (USD 800 / año). |
| **2. Ciberseguridad, Pentesting y Cumplimiento Normativo (Ley 1581)** | **3.200** | • **Auditoría Externa de Seguridad y Pentesting:** Evaluación ética de penetración bajo metodología OWASP Top 10 antes del lanzamiento público (USD 1.800).<br>• **Consultoría Jurídica en Habeas Data & Registro SIC:** Validación de términos y condiciones, avisos de privacidad y registro formal de bases de datos ante la Superintendencia de Industria y Comercio (USD 1.400). |
| **3. Levantamiento de Datos, Fotografía y Cartografía SIG Local** | **3.600** | • **Trabajo de Campo y Georreferenciación:** Levantamiento de coordenadas exactas y rutas para 100+ atractivos y prestadores en Santa Marta, Taganga, Rodadero, Minca y zonas de amortiguación del Tayrona (USD 2.000).<br>• **Producción de Activos Digitales Abiertos:** Fotografía profesional de alta resolución libre de derechos de autor para el catálogo público (USD 1.600). |
| **4. Programa de Alfabetización Digital e Inclusión de MiPyMEs Turísticas** | **3.200** | • **Talleres Presenciales de Capacitación:** 4 jornadas comunitarias dirigidas a pequeños hoteleros, guías de turismo y asociaciones de lancheros para el uso del panel de prestador (USD 2.000).<br>• **Materiales Didácticos y Kits de Adopción:** Guías visuales impresas y audiovisuales de soporte para prestadores de bajos recursos tecnológicos (USD 1.200). |
| **5. Observabilidad, Dominios Institucionales y Reserva de Contingencia** | **2.800** | • **Infraestructura de Monitoreo 24/7:** Servidores dedicados para Prometheus/Grafana y gestión de alertas operacionales (USD 800).<br>• **Dominios y Certificados SSL Extended Validation (EV):** Adquisición de dominio institucional `.gov.co` o `.org` y certificados SSL seguros (USD 400).<br>• **Fondo de Reserva y Contingencia Operativa (8%):** Reserva técnica para contingencias en servidores o ajustes normativos imprevistos (USD 1.600). |
| **TOTAL ESCENARIO B** | **20.000** | **Ejecución completa del 100% del presupuesto asignado.** |
