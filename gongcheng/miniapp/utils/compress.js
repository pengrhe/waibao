/**
 * 图片压缩工具 —— 拍照 / 相册选图后先压缩再上传，大幅减少传输耗时。
 *
 * 策略：长边 > MAX_SIDE 时用 canvas 缩放 + JPEG 重编码；
 *       长边 ≤ MAX_SIDE 仅做 JPEG quality 压缩。
 */

const MAX_SIDE = 1920;
const JPEG_QUALITY = 0.82;

/**
 * @param {string} srcPath  原始临时文件路径
 * @returns {Promise<string>} 压缩后的临时文件路径
 */
function compressPhoto(srcPath) {
  return new Promise((resolve, reject) => {
    wx.getImageInfo({
      src: srcPath,
      success(info) {
        const w = info.width;
        const h = info.height;

        if (w <= MAX_SIDE && h <= MAX_SIDE) {
          _qualityCompress(srcPath, resolve, reject);
          return;
        }

        const ratio = MAX_SIDE / Math.max(w, h);
        const dw = Math.round(w * ratio);
        const dh = Math.round(h * ratio);

        let canvas;
        try {
          canvas = wx.createOffscreenCanvas({ type: '2d', width: dw, height: dh });
        } catch (e) {
          _qualityCompress(srcPath, resolve, reject);
          return;
        }

        const ctx = canvas.getContext('2d');
        const img = canvas.createImage();
        img.onload = () => {
          ctx.drawImage(img, 0, 0, dw, dh);
          wx.canvasToTempFilePath({
            canvas,
            x: 0, y: 0, width: dw, height: dh,
            destWidth: dw, destHeight: dh,
            fileType: 'jpg',
            quality: JPEG_QUALITY,
            success(res) { resolve(res.tempFilePath); },
            fail() { resolve(srcPath); },
          });
        };
        img.onerror = () => { resolve(srcPath); };
        img.src = info.path || srcPath;
      },
      fail() { resolve(srcPath); },
    });
  });
}

function _qualityCompress(src, resolve, reject) {
  wx.compressImage({
    src,
    quality: 80,
    success(res) { resolve(res.tempFilePath); },
    fail() { resolve(src); },
  });
}

module.exports = { compressPhoto };
