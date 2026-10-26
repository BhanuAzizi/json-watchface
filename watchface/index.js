// JSON Watchface - Amazfit Bip 6 (390 x 450)
// Koordinat slot berasal dari tools/layout.json (hasil tools/generate_assets.py)

const DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'].map((n) => 'digits/' + n + '.png')
const WEEK = [0, 1, 2, 3, 4, 5, 6].map((n) => 'week/' + n + '.png') // 0 = Mon ... 6 = Sun
const MONTH = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11].map((n) => 'month/' + n + '.png') // 0 = Jan ... 11 = Dec

const SLOT = {
  hour: { x: 181, y: 117 },
  minute: { x: 221, y: 117 },
  second: { x: 260, y: 117 },
  week: { x: 181, y: 154 },
  month: { x: 247, y: 154 },
  day: { x: 300, y: 154 },
  steps: { x: 221, y: 228, w: 66 },
  heart: { x: 221, y: 265, w: 40 },
  battery: { x: 221, y: 339, w: 40 }
}

const POLL_MS = 3000

WatchFace({
  build() {
    const NORMAL = hmUI.show_level.ONLY_NORMAL

    try {
      // Bagian statis: tab editor, nomor baris, key, kurung, tanda kutip, titik dua jam
      hmUI.createWidget(hmUI.widget.IMG, { x: 0, y: 0, src: 'background.png', show_level: NORMAL })

      // "time":"HH:MM:SS"
      hmUI.createWidget(hmUI.widget.IMG_TIME, {
        hour_zero: 1, hour_startX: SLOT.hour.x, hour_startY: SLOT.hour.y,
        hour_array: DIGITS, hour_space: 0, hour_align: hmUI.align.LEFT,
        minute_zero: 1, minute_startX: SLOT.minute.x, minute_startY: SLOT.minute.y,
        minute_array: DIGITS, minute_space: 0, minute_align: hmUI.align.LEFT, minute_follow: 0,
        second_zero: 1, second_startX: SLOT.second.x, second_startY: SLOT.second.y,
        second_array: DIGITS, second_space: 0, second_align: hmUI.align.LEFT, second_follow: 0,
        show_level: NORMAL
      })

      // "date":"Www, Mmm DD"
      hmUI.createWidget(hmUI.widget.IMG_WEEK, {
        x: SLOT.week.x, y: SLOT.week.y,
        week_en: WEEK, week_tc: WEEK, week_sc: WEEK,
        show_level: NORMAL
      })
      hmUI.createWidget(hmUI.widget.IMG_DATE, {
        month_startX: SLOT.month.x, month_startY: SLOT.month.y,
        month_align: hmUI.align.LEFT, month_space: 0, month_zero: 0, month_follow: 0,
        month_is_character: true,
        month_en_array: MONTH, month_sc_array: MONTH, month_tc_array: MONTH,
        day_startX: SLOT.day.x, day_startY: SLOT.day.y,
        day_align: hmUI.align.LEFT, day_space: 0, day_zero: 1, day_follow: 0, day_is_character: false,
        day_en_array: DIGITS, day_sc_array: DIGITS, day_tc_array: DIGITS,
        show_level: NORMAL
      })

      buildStats(NORMAL)
    } catch (e) {
      console.log('JSONWF ERROR: ' + e)
    }
  },

  onDestroy() {}
})

// Angka statistik (steps, heart, battery), rata tengah di dalam tanda kutip.
// Nilainya diisi manual dari sensor, karena widget data_type bawaan
// tidak selalu me-refresh heart rate saat watch face sedang tampil.
function buildStats(NORMAL) {
  const mk = (slot, type) => hmUI.createWidget(hmUI.widget.TEXT_IMG, {
    x: slot.x, y: slot.y, w: slot.w, h: 30,
    type: type, font_array: DIGITS, h_space: 0,
    align_h: hmUI.align.CENTER_H,
    show_level: NORMAL
  })

  let heart, step, battery
  try {
    heart = hmSensor.createSensor(hmSensor.id.HEART)
    step = hmSensor.createSensor(hmSensor.id.STEP)
    battery = hmSensor.createSensor(hmSensor.id.BATTERY)
  } catch (e) {
    // Fallback: biarkan sistem yang mengisi nilainya
    console.log('JSONWF sensor fallback: ' + e)
    mk(SLOT.steps, hmUI.data_type.STEP)
    mk(SLOT.heart, hmUI.data_type.HEART)
    mk(SLOT.battery, hmUI.data_type.BATTERY)
    return
  }

  const stepW = mk(SLOT.steps)
  const heartW = mk(SLOT.heart)
  const batW = mk(SLOT.battery)
  const setText = (w, v) => w.setProperty(hmUI.prop.TEXT, String(v))

  // 'last' = hasil pengukuran terakhir; 'current' kadang tertahan di nilai lama
  const updHeart = () => setText(heartW, heart.last || heart.current || 0)
  const updStep = () => setText(stepW, step.current || 0)
  const updBat = () => setText(batW, battery.current || 0)
  const updAll = () => { updHeart(); updStep(); updBat() }

  const listen = (label, fn) => {
    try { fn() } catch (e) { console.log('JSONWF listen ' + label + ' gagal: ' + e) }
  }
  listen('heart current', () => heart.addEventListener(heart.event.CURRENT, updHeart))
  listen('heart last', () => heart.addEventListener(heart.event.LAST, updHeart))
  listen('step', () => step.addEventListener(hmSensor.event.CHANGE, updStep))
  listen('battery', () => battery.addEventListener(hmSensor.event.CHANGE, updBat))
  updAll()

  // Cadangan: event heart rate tidak selalu terkirim, jadi cek ulang
  // tiap POLL_MS selama layar menyala, dan berhenti saat layar mati.
  let poll = null
  const startPoll = () => {
    if (poll !== null) return
    try {
      poll = timer.createTimer(POLL_MS, POLL_MS, function () { updAll() }, {})
    } catch (e) { console.log('JSONWF timer gagal: ' + e) }
  }
  const stopPoll = () => {
    if (poll === null) return
    try { timer.stopTimer(poll) } catch (e) {}
    poll = null
  }
  startPoll()

  hmUI.createWidget(hmUI.widget.WIDGET_DELEGATE, {
    resume_call: function () { updAll(); startPoll() },
    pause_call: function () { stopPoll() }
  })
}
