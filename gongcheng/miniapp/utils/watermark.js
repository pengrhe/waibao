/**
 * 微信小程序水印绘制 —— 三段式布局
 * 顶部：蓝底 logo + 白字机构名
 * 中部：白底黑字 拍摄时间 / 地点
 * 底部：蓝底白字 所属项目
 */

const BLUE_BG = 'rgba(30,64,175,0.92)';
const WHITE_BG = 'rgba(255,255,255,0.92)';
const WHITE = '#ffffff';
const DARK = '#1e293b';
const LOGO_PATH = '/images/logo_longhua.png';
const LOGO_RATIO = 531 / 210;

function roundRectTop(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + w - r, y);
  ctx.arcTo(x + w, y, x + w, y + r, r);
  ctx.lineTo(x + w, y + h);
  ctx.lineTo(x, y + h);
  ctx.lineTo(x, y + r);
  ctx.arcTo(x, y, x + r, y, r);
  ctx.closePath();
}

function roundRectBottom(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x, y);
  ctx.lineTo(x + w, y);
  ctx.lineTo(x + w, y + h - r);
  ctx.arcTo(x + w, y + h, x + w - r, y + h, r);
  ctx.lineTo(x + r, y + h);
  ctx.arcTo(x, y + h, x, y + h - r, r);
  ctx.closePath();
}

/**
 * @param {CanvasRenderingContext2D} ctx
 * @param {number} cW  canvas width
 * @param {number} cH  canvas height
 * @param {object} opts
 * @param {Image|null} logoImage
 */
/**
 * Word output: 13.2cm × 8.34cm; target watermark: 6.3cm wide × 2.2cm tall
 * Heights at scale=1 sum to 151px, so scale = targetH_px / 151
 */
const WM_DISPLAY_W = 13.2;
const WM_DISPLAY_H = 8.34;
const WM_TARGET_W = 6.0;
const WM_TARGET_H = 2.2;
const H_COEFF = 151;

const LOC_MAX_CHARS = 20;

function wrapByChars(text, maxChars) {
  const lines = [];
  for (let i = 0; i < text.length; i += maxChars) {
    lines.push(text.slice(i, i + maxChars));
  }
  return lines.length ? lines : [''];
}

function drawWatermark(canvas, ctx, cW, cH, opts, logoImage) {
  const orgName = opts.orgName || '';
  const time = opts.time || '';
  const location = opts.location || '';
  const project = opts.project || '';

  const shortSide = Math.min(cW, cH);
  const scale = Math.max((WM_TARGET_H * shortSide / WM_DISPLAY_H) / H_COEFF, 0.5);

  const pad = Math.round(16 * scale);
  const innerPadX = Math.round(18 * scale);
  const innerPadY = Math.round(10 * scale);
  const radius = Math.round(12 * scale);
  const orgFont = Math.round(20 * scale);
  const lineFont = Math.round(17 * scale);
  const lineGap = Math.round(6 * scale);
  const logoH = Math.round(34 * scale);
  const logoW = Math.round(logoH * LOGO_RATIO);
  const logoGap = Math.round(12 * scale);

  ctx.save();
  ctx.textBaseline = 'middle';

  ctx.font = `bold ${orgFont}px sans-serif`;
  const orgW = ctx.measureText(orgName).width;

  ctx.font = `${lineFont}px sans-serif`;
  const line2 = `拍 摄 时 间：${time}`;
  const locLabel = '地　　　点：';
  const line4 = `所 属 项 目：${project}`;

  const locLabelW = ctx.measureText(locLabel).width;
  const locLines = wrapByChars(location, LOC_MAX_CHARS);

  const row1ContentW = logoW + logoGap + orgW;
  const line2W = ctx.measureText(line2).width;
  const locMaxLineW = locLabelW + Math.max(...locLines.map(l => ctx.measureText(l).width));
  const botTextW = ctx.measureText(line4).width;
  const contentW = Math.max(row1ContentW, line2W, locMaxLineW, botTextW);
  const boxW = Math.round(contentW + innerPadX * 2);

  const midLineCount = 1 + locLines.length;
  const topH = Math.max(logoH, orgFont) + innerPadY * 2;
  const midH = (lineFont * midLineCount) + lineGap * (midLineCount - 1) + innerPadY * 2;
  const botH = lineFont + innerPadY * 2;
  const totalH = topH + midH + botH;

  const boxX = pad;
  const boxY = cH - totalH - pad;

  // --- Top section ---
  ctx.fillStyle = BLUE_BG;
  roundRectTop(ctx, boxX, boxY, boxW, topH, radius);
  ctx.fill();

  const logoDrawX = boxX + innerPadX;
  const logoDrawY = boxY + Math.round((topH - logoH) / 2);
  if (logoImage) {
    ctx.drawImage(logoImage, logoDrawX, logoDrawY, logoW, logoH);
  }

  ctx.fillStyle = WHITE;
  ctx.font = `bold ${orgFont}px sans-serif`;
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(orgName, logoDrawX + logoW + logoGap, boxY + topH / 2);

  // --- Middle section ---
  const midY = boxY + topH;
  ctx.fillStyle = WHITE_BG;
  ctx.fillRect(boxX, midY, boxW, midH);

  ctx.fillStyle = DARK;
  ctx.font = `${lineFont}px sans-serif`;
  ctx.textBaseline = 'top';
  let ty = midY + innerPadY;
  ctx.fillText(line2, boxX + innerPadX, ty);
  ty += lineFont + lineGap;

  ctx.fillText(locLabel + locLines[0], boxX + innerPadX, ty);
  for (let i = 1; i < locLines.length; i++) {
    ty += lineFont + lineGap;
    ctx.fillText(locLines[i], boxX + innerPadX + locLabelW, ty);
  }

  // --- Bottom section ---
  const botY = midY + midH;
  ctx.fillStyle = BLUE_BG;
  roundRectBottom(ctx, boxX, botY, boxW, botH, radius);
  ctx.fill();

  ctx.fillStyle = WHITE;
  ctx.font = `${lineFont}px sans-serif`;
  ctx.textBaseline = 'middle';
  ctx.fillText(line4, boxX + innerPadX, botY + botH / 2);

  ctx.restore();
}

/**
 * 加载图片 → 绘制到离屏 canvas → 叠加水印 → 导出临时文件
 */
function applyWatermark(tempFilePath, options) {
  return new Promise((resolve, reject) => {
    if (typeof wx.createOffscreenCanvas !== 'function') {
      reject(new Error('当前基础库不支持 createOffscreenCanvas'));
      return;
    }

    wx.getImageInfo({
      src: tempFilePath,
      success(info) {
        let w = info.width;
        let h = info.height;
        const maxSide = 1920;
        if (w > maxSide || h > maxSide) {
          const ratio = maxSide / Math.max(w, h);
          w = Math.round(w * ratio);
          h = Math.round(h * ratio);
        }
        let canvas;
        try {
          canvas = wx.createOffscreenCanvas({ type: '2d', width: w, height: h });
        } catch (e) {
          reject(e);
          return;
        }

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('无法获取 canvas 2d 上下文'));
          return;
        }

        const photoImg = canvas.createImage();
        const logoImg = canvas.createImage();
        let photoReady = false;
        let logoReady = false;
        let logoFailed = false;

        function tryCompose() {
          if (!photoReady || (!logoReady && !logoFailed)) return;
          try {
            ctx.drawImage(photoImg, 0, 0, w, h);
            drawWatermark(canvas, ctx, w, h, options, logoReady ? logoImg : null);
            wx.canvasToTempFilePath({
              canvas,
              x: 0, y: 0, width: w, height: h,
              destWidth: w, destHeight: h,
              fileType: 'jpg', quality: 0.92,
              success(res) { resolve(res.tempFilePath); },
              fail: reject,
            });
          } catch (err) {
            reject(err);
          }
        }

        photoImg.onload = () => { photoReady = true; tryCompose(); };
        photoImg.onerror = (err) => { reject(err || new Error('照片加载失败')); };
        logoImg.onload = () => { logoReady = true; tryCompose(); };
        logoImg.onerror = () => { logoFailed = true; tryCompose(); };

        photoImg.src = info.path || tempFilePath;
        logoImg.src = LOGO_PATH;
      },
      fail: reject,
    });
  });
}

module.exports = { drawWatermark, applyWatermark };
