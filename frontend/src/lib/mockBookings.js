import { experiences } from '../data/mock'
import { addDays, today, tomorrow, weekday } from './dates'

/*
 * Servicio SIMULADO de booking-service (solo mientras no exista el Gateway).
 * Reproduce las reglas de contracts/openapi/booking.yaml y de la Guía Técnica del Módulo 3:
 * máquina de estados, cupos sin sobreventa, Idempotency-Key, If-Match/ETag y los códigos de error.
 */
const KEY = 'mock.bookings.v1'
const ME = 'turista-demo'
const CAPACIDAD = { 'bahia-concha': 20, 'quebrada-valencia': 15, 'ruta-cacao': 12 }
const ACTIVOS = ['SOLICITADA', 'CONFIRMADA']

export class MockError extends Error {
  constructor(status, error, message, headers = {}) {
    super(message)
    this.status = status; this.code = error; this.headers = headers
    this.correlationId = `mock-${Math.random().toString(16).slice(2, 10)}`
  }
}

const uid = () => (crypto.randomUUID ? crypto.randomUUID() : `${Date.now()}-${Math.random().toString(16).slice(2)}`)
const nowIso = () => new Date().toISOString()

// Plazo de respuesta: mín(ahora + 48 h, 00:00 del día de la reserva) en America/Bogota (UTC-5)
function expira(fecha) {
  const limite = new Date(`${fecha}T00:00:00-05:00`).getTime()
  return new Date(Math.min(Date.now() + 48 * 3600e3, limite)).toISOString()
}

function seed() {
  const t = today()
  const mk = (servicio_id, dias, n, estado, extra = {}) => ({
    id: uid(), servicio_id, turista_id: ME, prestador_id: `prestador-${servicio_id}`,
    fecha_reserva: addDays(t, dias), numero_personas: n, estado, version: 1,
    creado_en: nowIso(), actualizado_en: nowIso(), expira_en: null, motivo: null, cancelada_por: null, ...extra,
  })
  return {
    reservas: [
      mk('bahia-concha', 6, 2, 'CONFIRMADA', { version: 2 }),
      mk('quebrada-valencia', 9, 3, 'SOLICITADA', { expira_en: expira(addDays(t, 9)) }),
      mk('ruta-cacao', -12, 2, 'FINALIZADA', { version: 3 }),
      mk('bahia-concha', 14, 4, 'CANCELADA', { motivo: 'Cambio de planes', cancelada_por: 'Turista', version: 2 }),
    ],
    idem: {},
  }
}

function load() {
  let db
  try { db = JSON.parse(localStorage.getItem(KEY)) } catch { /* vacío */ }
  if (!db) db = seed()
  // Transiciones del sistema (perezosas): plazo vencido -> RECHAZADA; fecha pasada -> FINALIZADA
  let dirty = false
  for (const r of db.reservas) {
    if (r.estado === 'SOLICITADA' && r.expira_en && new Date(r.expira_en) < new Date()) {
      Object.assign(r, { estado: 'RECHAZADA', expira_en: null, motivo: 'Venció el plazo de respuesta del prestador.', version: r.version + 1 }); dirty = true
    }
    if (r.estado === 'CONFIRMADA' && r.fecha_reserva < today()) { Object.assign(r, { estado: 'FINALIZADA', version: r.version + 1 }); dirty = true }
  }
  if (dirty) save(db)
  return db
}
const save = (db) => { try { localStorage.setItem(KEY, JSON.stringify(db)) } catch { /* sin almacenamiento */ } }
const etag = (r) => `"${r.version}"`
const delay = (v) => new Promise((res) => setTimeout(() => res(v), 220))

const servicio = (id) => {
  const s = experiences.find((e) => e.id === id)
  if (!s) throw new MockError(404, 'NO_ENCONTRADO', 'El servicio no existe.')
  return s
}

// Días operativos del servicio: la quebrada cierra los lunes; los sábados de Bahía Concha cuestan 20 % más
function dia(db, id, fecha) {
  const s = servicio(id)
  if (id === 'quebrada-valencia' && weekday(fecha) === 1) return null
  const total = CAPACIDAD[id] ?? 10
  const reservados = db.reservas.filter((r) => r.servicio_id === id && r.fecha_reserva === fecha && ACTIVOS.includes(r.estado)).reduce((a, r) => a + r.numero_personas, 0)
  return { fecha, cupos_totales: total, cupos_disponibles: Math.max(0, total - reservados), tarifa_dia: id === 'bahia-concha' && weekday(fecha) === 6 ? Math.round(s.fee * 1.2) : null }
}

export const mock = {
  async consultarDisponibilidad(servicioId, desde, hasta) {
    const db = load(); servicio(servicioId)
    if (hasta < desde || hasta > addDays(desde, 62)) throw new MockError(400, 'VALIDACION', 'El rango máximo es de 62 días.')
    const dias = []
    for (let f = desde; f <= hasta; f = addDays(f, 1)) {
      const d = dia(db, servicioId, f)
      if (d) dias.push({ fecha: d.fecha, cupos_disponibles: d.cupos_disponibles, tarifa_dia: d.tarifa_dia })
    }
    return delay({ data: { servicio_id: servicioId, dias } })
  },

  async solicitarReserva(body, idemKey) {
    const db = load()
    if (idemKey && db.idem[idemKey]) { // mismo intento = misma respuesta, sin repetir la operación
      const r = db.reservas.find((x) => x.id === db.idem[idemKey]); return delay({ data: r, etag: etag(r) })
    }
    servicio(body.servicio_id)
    if (!(body.numero_personas >= 1)) throw new MockError(400, 'VALIDACION', 'El número de personas debe ser al menos 1.')
    if (body.fecha_reserva < tomorrow()) throw new MockError(400, 'VALIDACION', 'La fecha debe ser a partir de mañana.')
    const d = dia(db, body.servicio_id, body.fecha_reserva)
    if (!d) throw new MockError(409, 'DIA_NO_DISPONIBLE', `El prestador no opera el ${body.fecha_reserva}.`)
    if (db.reservas.some((r) => r.turista_id === ME && r.servicio_id === body.servicio_id && r.fecha_reserva === body.fecha_reserva && ACTIVOS.includes(r.estado)))
      throw new MockError(409, 'RESERVA_DUPLICADA', 'Ya tienes una reserva activa para ese servicio y fecha.')
    if (d.cupos_disponibles < body.numero_personas) throw new MockError(409, 'CUPOS_INSUFICIENTES', `Solo quedan ${d.cupos_disponibles} cupos para el ${body.fecha_reserva}.`)
    const r = {
      id: uid(), servicio_id: body.servicio_id, turista_id: ME, prestador_id: `prestador-${body.servicio_id}`,
      fecha_reserva: body.fecha_reserva, numero_personas: body.numero_personas, estado: 'SOLICITADA', expira_en: expira(body.fecha_reserva),
      motivo: null, cancelada_por: null, version: 1, creado_en: nowIso(), actualizado_en: nowIso(),
    }
    db.reservas.unshift(r)
    if (idemKey) db.idem[idemKey] = r.id
    save(db)
    return delay({ data: r, etag: etag(r) })
  },

  async misReservas({ estado, pagina = 1, tamano = 20 } = {}) {
    const db = load()
    const todas = db.reservas.filter((r) => r.turista_id === ME && (!estado || r.estado === estado)).sort((a, b) => b.creado_en.localeCompare(a.creado_en))
    return delay({ data: { items: todas.slice((pagina - 1) * tamano, pagina * tamano), pagina, tamano, total: todas.length } })
  },

  async modificarReserva(id, ifMatch, cambios) {
    const db = load()
    const r = db.reservas.find((x) => x.id === id && x.turista_id === ME)
    if (!r) throw new MockError(404, 'NO_ENCONTRADO', 'La reserva no existe.')
    if (!ifMatch) throw new MockError(428, 'FALTA_IF_MATCH', 'Falta el encabezado If-Match.')
    if (ifMatch !== etag(r)) throw new MockError(409, 'VERSION_DISTINTA', 'La reserva cambió en el servidor.', { ETag: etag(r) })
    if (r.estado !== 'SOLICITADA') throw new MockError(409, 'TRANSICION_INVALIDA', `Solo se puede modificar en estado SOLICITADA; está ${r.estado}.`)
    const fecha = cambios.fecha_reserva ?? r.fecha_reserva
    const n = cambios.numero_personas ?? r.numero_personas
    if (fecha < tomorrow() || !(n >= 1)) throw new MockError(400, 'VALIDACION', 'Fecha a partir de mañana y al menos 1 persona.')
    const d = dia(db, r.servicio_id, fecha)
    if (!d) throw new MockError(409, 'DIA_NO_DISPONIBLE', `El prestador no opera el ${fecha}.`)
    const propios = fecha === r.fecha_reserva ? r.numero_personas : 0 // al mismo día se reutilizan sus propios cupos
    if (d.cupos_disponibles + propios < n) throw new MockError(409, 'CUPOS_INSUFICIENTES', `Solo quedan ${d.cupos_disponibles + propios} cupos para el ${fecha}.`)
    Object.assign(r, { fecha_reserva: fecha, numero_personas: n, version: r.version + 1, expira_en: expira(fecha), actualizado_en: nowIso() })
    save(db)
    return delay({ data: r, etag: etag(r) })
  },

  async cancelarReserva(id, motivo) {
    const db = load()
    const r = db.reservas.find((x) => x.id === id && x.turista_id === ME)
    if (!r) throw new MockError(404, 'NO_ENCONTRADO', 'La reserva no existe.')
    if (!ACTIVOS.includes(r.estado)) throw new MockError(409, 'TRANSICION_INVALIDA', `No se puede cancelar una reserva ${r.estado}.`)
    if (r.estado === 'CONFIRMADA' && r.fecha_reserva <= today()) throw new MockError(409, 'FUERA_DE_PLAZO', 'Solo se puede cancelar hasta las 23:59 del día anterior a la reserva.')
    Object.assign(r, { estado: 'CANCELADA', expira_en: null, motivo: motivo || null, cancelada_por: 'Turista', version: r.version + 1, actualizado_en: nowIso() })
    save(db)
    return delay({ data: r, etag: etag(r) })
  },
}
