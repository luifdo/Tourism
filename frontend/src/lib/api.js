import { mock, MockError } from './mockBookings'

/*
 * Cliente del booking-service según contracts/openapi/booking.yaml (servidor /api/bookings).
 * Con VITE_API_MOCK=true usa el servicio simulado; con false llama al Gateway (Traefik).
 */
const USE_MOCK = import.meta.env.VITE_API_MOCK !== 'false'
const BASE = '/api/bookings'

export class ApiError extends Error {
  constructor(status, code, message, correlationId) {
    super(message)
    this.status = status; this.code = code; this.correlationId = correlationId
  }
}

const token = () => { try { return localStorage.getItem('token') } catch { return null } }
export const isMock = USE_MOCK
/** En modo simulado siempre hay un turista de demostración; en real hace falta el JWT (UC2). */
export const hasSession = () => USE_MOCK || !!token()

async function http(method, path, { body, headers = {}, query } = {}) {
  const qs = query ? '?' + new URLSearchParams(Object.entries(query).filter(([, v]) => v != null && v !== '')) : ''
  const h = { Accept: 'application/json', ...headers }
  if (body) h['Content-Type'] = 'application/json'
  if (token()) h.Authorization = `Bearer ${token()}`
  let res
  try { res = await fetch(`${BASE}${path}${qs}`, { method, headers: h, body: body ? JSON.stringify(body) : undefined }) }
  catch { throw new ApiError(0, 'SIN_CONEXION', 'No hay conexión con el servidor.') }
  const data = await res.json().catch(() => null)
  if (!res.ok) throw new ApiError(res.status, data?.error ?? (res.status === 401 ? 'NO_AUTENTICADO' : 'ERROR'), data?.message ?? res.statusText, data?.correlation_id)
  return { data, etag: res.headers.get('ETag') }
}

// Normaliza los errores del simulador al mismo tipo que los del Gateway
const guard = (p) => p.catch((e) => { throw e instanceof MockError ? new ApiError(e.status, e.code, e.message, e.correlationId) : e })

export const bookings = {
  /** UC10 · pública */
  consultarDisponibilidad: (servicioId, desde, hasta) => USE_MOCK
    ? guard(mock.consultarDisponibilidad(servicioId, desde, hasta)).then((r) => r.data)
    : http('GET', '/disponibilidad', { query: { servicio_id: servicioId, desde, hasta } }).then((r) => r.data),

  /** UC11 · requiere conexión; la clave evita duplicados ante un reintento */
  solicitarReserva: (body, idempotencyKey) => USE_MOCK
    ? guard(mock.solicitarReserva(body, idempotencyKey))
    : http('POST', '/', { body, headers: { 'Idempotency-Key': idempotencyKey } }),

  /** UC13 */
  misReservas: (params = {}) => USE_MOCK
    ? guard(mock.misReservas(params)).then((r) => r.data)
    : http('GET', '/mis-reservas', { query: params }).then((r) => r.data),

  /** UC12 · If-Match con la versión que el usuario vio */
  modificarReserva: (id, version, cambios) => USE_MOCK
    ? guard(mock.modificarReserva(id, `"${version}"`, cambios))
    : http('PATCH', `/${id}`, { body: cambios, headers: { 'If-Match': `"${version}"` } }),

  /** UC12 */
  cancelarReserva: (id, motivo) => USE_MOCK
    ? guard(mock.cancelarReserva(id, motivo))
    : http('POST', `/${id}/cancelar`, { body: motivo ? { motivo } : {} }),
}
