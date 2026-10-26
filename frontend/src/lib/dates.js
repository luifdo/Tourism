// La unidad de reserva es el día y todas las horas se calculan en America/Bogota (booking.yaml)
const TZ = 'America/Bogota'
const ymd = new Intl.DateTimeFormat('en-CA', { timeZone: TZ })

export const today = () => ymd.format(new Date())
export const addDays = (iso, n) => {
  const d = new Date(`${iso}T12:00:00Z`)
  d.setUTCDate(d.getUTCDate() + n)
  return d.toISOString().slice(0, 10)
}
export const tomorrow = () => addDays(today(), 1)
/** 1 = lunes … 7 = domingo */
export const weekday = (iso) => ((new Date(`${iso}T12:00:00Z`).getUTCDay() + 6) % 7) + 1
export const monthKey = (iso) => iso.slice(0, 7)
export const daysInMonth = (key) => new Date(Date.UTC(+key.slice(0, 4), +key.slice(5, 7), 0)).getUTCDate()
export const fmtDate = (iso, locale, opts = { weekday: 'long', day: 'numeric', month: 'long' }) =>
  new Intl.DateTimeFormat(locale, { ...opts, timeZone: 'UTC' }).format(new Date(`${iso}T12:00:00Z`))
