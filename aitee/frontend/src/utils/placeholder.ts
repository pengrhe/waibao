/**
 * 占位 SVG 生成器：返回 data URL，可直接用作 <img :src>。
 * 全部自制 SVG，不依赖外部图床，离线演示也能跑。
 */

function svgToDataUrl(svg: string): string {
  const cleaned = svg.replace(/\n+/g, '').replace(/\s{2,}/g, ' ')
  return `data:image/svg+xml;utf8,${encodeURIComponent(cleaned)}`
}

/** 短袖 T 恤底图 */
export function tshirtMockup(color = '#ffffff', side: 'front' | 'back' = 'front'): string {
  const stroke = isLight(color) ? '#9ca3af' : '#374151'
  const shadow = darken(color, 0.08)
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 420">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fafafa"/>
      <stop offset="1" stop-color="#eeeeee"/>
    </linearGradient>
  </defs>
  <rect width="360" height="420" fill="url(#bg)"/>
  <!-- 阴影 -->
  <ellipse cx="180" cy="395" rx="120" ry="10" fill="rgba(0,0,0,0.08)"/>
  <!-- T 恤主体 -->
  <path d="M90 90 L140 60 L150 75 Q180 95 210 75 L220 60 L270 90 L300 130 L260 150 L260 380 L100 380 L100 150 L60 130 Z"
    fill="${color}" stroke="${stroke}" stroke-width="1.5" stroke-linejoin="round"/>
  <!-- 领口 -->
  <path d="M150 75 Q180 100 210 75" fill="none" stroke="${stroke}" stroke-width="1.5"/>
  <!-- 衣袖阴影 -->
  <path d="M90 90 L60 130 L100 150 L100 175 L130 165 L130 130 L120 100 Z" fill="${shadow}" opacity="0.4"/>
  <path d="M270 90 L300 130 L260 150 L260 175 L230 165 L230 130 L240 100 Z" fill="${shadow}" opacity="0.4"/>
  <!-- 标签：side -->
  <text x="180" y="230" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="14" font-weight="600"
    fill="${isLight(color) ? '#d4d4d8' : 'rgba(255,255,255,0.4)'}" text-anchor="middle">${side === 'front' ? '正面' : '背面'}</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 帆布包底图 */
export function toteMockup(color = '#ffffff'): string {
  const stroke = isLight(color) ? '#9ca3af' : '#374151'
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 420">
  <rect width="360" height="420" fill="#f5f5f5"/>
  <ellipse cx="180" cy="400" rx="110" ry="8" fill="rgba(0,0,0,0.08)"/>
  <path d="M120 130 Q120 70 150 70 Q180 70 180 100 Q180 130 150 130" fill="none" stroke="${stroke}" stroke-width="3"/>
  <path d="M240 130 Q240 70 210 70 Q180 70 180 100 Q180 130 210 130" fill="none" stroke="${stroke}" stroke-width="3"/>
  <rect x="90" y="130" width="180" height="240" rx="8" fill="${color}" stroke="${stroke}" stroke-width="1.5"/>
  <text x="180" y="260" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="14" font-weight="600"
    fill="${isLight(color) ? '#d4d4d8' : 'rgba(255,255,255,0.5)'}" text-anchor="middle">帆布包</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 印花占位（带文字与几何图形） */
export function patternImage(opts: {
  text?: string
  bg?: string
  fg?: string
  shape?: 'square' | 'circle' | 'tag'
  width?: number
  height?: number
}): string {
  const {
    text = 'TEE',
    bg = '#FFE4E6',
    fg = '#FF4D4F',
    shape = 'square',
    width = 240,
    height = 240,
  } = opts
  const cornerR = shape === 'circle' ? Math.min(width, height) / 2 : 16
  const accent = darken(fg, 0.18)
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${width} ${height}">
  <rect width="${width}" height="${height}" rx="${cornerR}" fill="${bg}"/>
  <circle cx="${width * 0.25}" cy="${height * 0.3}" r="${Math.min(width, height) * 0.15}" fill="${fg}" opacity="0.85"/>
  <rect x="${width * 0.5}" y="${height * 0.5}" width="${width * 0.32}" height="${height * 0.25}" rx="6" fill="${accent}" opacity="0.7"/>
  <path d="M${width * 0.15} ${height * 0.75} L${width * 0.45} ${height * 0.6} L${width * 0.35} ${height * 0.85} Z" fill="${fg}" opacity="0.55"/>
  <text x="${width / 2}" y="${height * 0.55}" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="${Math.floor(Math.min(width, height) * 0.18)}" font-weight="800"
    fill="${darken(fg, 0.25)}" text-anchor="middle">${escapeXml(text)}</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 主视觉 banner 占位 */
export function bannerImage(opts: {
  title: string
  subtitle?: string
  bg?: [string, string]
  cta?: string
}): string {
  const { title, subtitle = '', bg = ['#FFE4E6', '#FFD7BA'], cta = '' } = opts
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 690 300">
  <defs>
    <linearGradient id="grad" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="${bg[0]}"/>
      <stop offset="1" stop-color="${bg[1]}"/>
    </linearGradient>
  </defs>
  <rect width="690" height="300" rx="16" fill="url(#grad)"/>
  <circle cx="540" cy="200" r="120" fill="#fff" opacity="0.45"/>
  <circle cx="600" cy="80" r="36" fill="#fff" opacity="0.5"/>
  <text x="40" y="120" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="46" font-weight="900" fill="#1F2937">${escapeXml(title)}</text>
  <text x="40" y="170" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="22" font-weight="600" fill="#FF4D4F">${escapeXml(subtitle)}</text>
  ${
    cta
      ? `<rect x="40" y="200" width="160" height="44" rx="22" fill="#FF4D4F"/>
         <text x="120" y="228" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="16" font-weight="700" fill="#fff" text-anchor="middle">${escapeXml(cta)}</text>`
      : ''
  }
</svg>
`
  return svgToDataUrl(svg)
}

/** 圆形头像占位 */
export function avatarImage(initial = 'A', bg = '#FF4D4F'): string {
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 80">
  <circle cx="40" cy="40" r="40" fill="${bg}"/>
  <text x="40" y="50" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="32" font-weight="800" fill="#fff" text-anchor="middle">${escapeXml(initial)}</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 五入口卡片 / 入口图标占位 */
export function entryIcon(opts: { emoji?: string; bg?: string; fg?: string }): string {
  const { emoji = 'T', bg = '#FFF1F2', fg = '#FF4D4F' } = opts
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 120">
  <rect width="120" height="120" rx="24" fill="${bg}"/>
  <text x="60" y="78" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="48" font-weight="800" fill="${fg}" text-anchor="middle">${escapeXml(emoji)}</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 推荐卡片：T 恤剪影 + 标题徽标 */
export function recommendCard(opts: { title: string; bg?: string; tee?: string }): string {
  const { title, bg = '#fafafa', tee = '#1F2937' } = opts
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 220">
  <rect width="220" height="220" rx="14" fill="${bg}"/>
  <path d="M55 55 L80 40 L88 50 Q110 60 132 50 L140 40 L165 55 L182 80 L160 90 L160 175 L60 175 L60 90 L38 80 Z"
    fill="${tee}" opacity="0.85"/>
  <rect x="20" y="170" width="${Math.max(48, title.length * 18 + 16)}" height="32" rx="16" fill="#FF4D4F"/>
  <text x="${28}" y="${191}" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="14" font-weight="800" fill="#fff">${escapeXml(title)}</text>
</svg>
`
  return svgToDataUrl(svg)
}

/** 专区横滑卡片占位 */
export function topicCard(opts: { title: string; bg?: string; fg?: string }): string {
  const { title, bg = '#FEF3C7', fg = '#92400E' } = opts
  const svg = `
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 280 200">
  <rect width="280" height="200" rx="14" fill="${bg}"/>
  <circle cx="60" cy="60" r="30" fill="#fff" opacity="0.6"/>
  <rect x="120" y="40" width="120" height="60" rx="8" fill="#fff" opacity="0.55"/>
  <rect x="60" y="120" width="180" height="40" rx="6" fill="#fff" opacity="0.55"/>
  <text x="20" y="40" font-family="-apple-system,Helvetica,Arial,sans-serif" font-size="22" font-weight="800" fill="${fg}">${escapeXml(title)}</text>
</svg>
`
  return svgToDataUrl(svg)
}

// ===== helpers =====

export function isLight(hex: string): boolean {
  const { r, g, b } = hexToRgb(hex)
  return (r * 299 + g * 587 + b * 114) / 1000 > 200
}

function darken(hex: string, amount: number): string {
  const { r, g, b } = hexToRgb(hex)
  const f = (v: number) => Math.max(0, Math.min(255, Math.round(v * (1 - amount))))
  return `rgb(${f(r)},${f(g)},${f(b)})`
}

function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const v = hex.replace('#', '')
  const full = v.length === 3 ? v.split('').map((c) => c + c).join('') : v
  const num = parseInt(full, 16)
  return { r: (num >> 16) & 0xff, g: (num >> 8) & 0xff, b: num & 0xff }
}

function escapeXml(text: string): string {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')
}
