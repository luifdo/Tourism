# ADR-001: Exclusión de la Pasarela de Pagos en Línea del Prototipo

**Proyecto:** Plataforma Digital para la Gestión Integrada y Sostenible del Turismo en Santa Marta  
**Estado:** Aceptada  
**Fecha:** Octubre 2026  
**Responsable de la decisión:** Arquitecto Líder / Product Owner (ver [Apéndice D del SRS](./Requirements_docIEEE.md#apéndice-d-equipo-de-trabajo-y-asignación-de-roles))  
**Casos de uso afectados:** UC34 y UC35 (pago en línea de reservas), excluidos del alcance  
**Documentos relacionados:** [SRS §1.2 y §2.4](./Requirements_docIEEE.md), [Plan de Desarrollo §4](./Plan_de_Desarrollo_de_Software.md), [Comparación de Alternativas Arquitectónicas](./Comparacion_Alternativas_Arquitectonicas.md)

---

## 1. Contexto

La plataforma permite a los turistas solicitar reservas de servicios turísticos (UC11) que los prestadores confirman o rechazan (UC20). La decisión es si el sistema debe además **cobrar** esas reservas mediante una pasarela de pagos en línea integrada.

Restricciones que condicionan la decisión:

* **Económica (SRS §2.4.2):** Techo de USD 20.000 y modelo gratuito *sin monetización directa ni comisiones sobre transacciones de reserva*.
* **Técnica (SRS §2.4.1):** Stack 100% software libre; las pasarelas de pago son servicios comerciales de terceros, con comisión por transacción y sin alternativa FOSS equivalente para el procesamiento de tarjetas.
* **Temporal (SRS §2.4.2):** 14 semanas y 5 integrantes, con meta de $\ge 60\%$ de los casos de uso *Must* en el prototipo.
* **Normativa (SRS §2.4.5):** Manejar datos de tarjetas exige cumplir el estándar PCI-DSS; el cobro anticipado de servicios a distancia además implica gestionar el derecho de retracto y los reembolsos del Estatuto del Consumidor (Ley 1480 de 2011).
* **Social (SRS §2.4.3):** Muchos prestadores comunitarios no cuentan con cuentas bancarias empresariales ni con capacidad para conciliar pagos electrónicos.

## 2. Alternativas consideradas

| Alternativa | Descripción | Ventaja principal | Desventaja principal |
|---|---|---|---|
| **A. Pasarela integrada** | Integrar una pasarela comercial de pagos para cobrar la reserva al solicitarla, con reembolsos y conciliación por prestador. | Reserva garantizada y menor tasa de inasistencia (*no-show*). | Comisión por transacción contraria al modelo gratuito, cumplimiento PCI-DSS, gestión de reembolsos y conciliación; alto costo en tiempo para el prototipo. |
| **B. Solicitud y confirmación sin pagos** *(seleccionada)* | El sistema gestiona disponibilidad, solicitud y confirmación; el pago se acuerda directamente entre turista y prestador. | Sin datos financieros en la infraestructura, sin comisiones y sin integración externa adicional. | La reserva no está garantizada económicamente; mayor riesgo de inasistencia para el prestador. |
| **C. Enlace de pago externo del prestador** | El prestador registra en su ficha un enlace o medio de pago propio (p. ej. un enlace de cobro de su banco), sin que la plataforma procese el pago. | Facilita el prepago sin que la plataforma maneje datos financieros. | Experiencia heterogénea entre prestadores; la plataforma no puede verificar el pago ni reflejarlo en el estado de la reserva. |

## 3. Decisión

Se adopta la **Alternativa B: modelo de solicitud y confirmación sin procesamiento de pagos**. UC34 y UC35 quedan fuera del alcance de esta iteración. La Alternativa C queda registrada como evolución posible de bajo costo.

**Criterios determinantes:**

1. **Coherencia con el modelo gratuito:** Una pasarela introduce comisiones por transacción, lo que contradice la restricción económica del SRS y el carácter de bien público de la plataforma (Plan §4).
2. **Seguridad y cumplimiento:** Excluir datos de tarjetas elimina el alcance PCI-DSS y un vector de ataque financiero, concentrando el esfuerzo de seguridad en los datos personales protegidos por la Ley 1581 de 2012.
3. **Tiempo de implementación:** La integración, conciliación y reembolsos consumirían parte significativa de las 14 semanas sin aportar a los casos de uso *Must*.

## 4. Consecuencias y trade-offs

| Se gana | Se sacrifica |
|---|---|
| Ningún dato financiero en la infraestructura: sin alcance PCI-DSS y menor superficie de ataque. | Garantía económica de la reserva; el prestador asume el riesgo de inasistencia. |
| Uso gratuito real para turistas y prestadores, sin comisiones. | Ingresos potenciales por comisión para sostener la plataforma (se financia como bien público, Plan §4). |
| Tiempo del prototipo concentrado en catálogo, reservas, IAM y recomendación. | Experiencia de reserva "de un solo paso" comparable a plataformas comerciales. |
| Inclusión de prestadores sin cuentas bancarias empresariales. | Trazabilidad del pago dentro de la plataforma; la analítica (Módulo 6) mide demanda, no ingresos. |

**Mitigaciones del riesgo de inasistencia:**

* El prestador confirma o rechaza cada solicitud (UC20) y define sus propios cupos (UC19), por lo que no asume compromisos automáticos.
* Políticas de cancelación visibles en la ficha del servicio y notificación por correo de cada cambio de estado (UC36, RF-11).
* El historial de reservas (UC13) y las reseñas (UC15) incentivan el cumplimiento de ambas partes.

## 5. Condiciones para revisar esta decisión

Esta decisión se reevaluará si se cumple alguna de las siguientes condiciones:

* La Entidad de Gestión del Destino solicita cobro anticipado para atractivos con aforo restringido (p. ej. Parque Tayrona), donde la inasistencia afecta la capacidad de carga.
* Se cuenta con financiación para cubrir comisiones y una auditoría de cumplimiento PCI-DSS.
* Los prestadores reportan una tasa de inasistencia que haga inviable el modelo de solicitud.

En ese caso, la primera opción a evaluar sería la Alternativa C (enlace de pago externo), antes que una pasarela integrada, por mantener los datos financieros fuera de la infraestructura.
