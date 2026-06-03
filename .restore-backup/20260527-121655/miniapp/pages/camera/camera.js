const {
  uploadRectifyPhoto,
  uploadScenePhoto,
  getProjectDetail,
  updateProject,
} = require('../../utils/api.js');
const { applyWatermark } = require('../../utils/watermark.js');

const TITLE_MAP = {
  facade: '拍摄企业门面',
  card: '拍摄廉政监督卡',
  rectify: '拍摄整改照片',
  license: '拍摄营业执照',
  permit: '拍摄经营许可证',
  record_sheet: '拍摄记录表',
};

const DEFAULT_ORG = '区安委办（应急局）';
const DEFAULT_PROJECT_LINE = '核查验收销号';
const CROP_RATIO = 4 / 3;
const PORTRAIT_RATIO = 3 / 5;
const PORTRAIT_TYPES = ['permit', 'record_sheet'];

function pad2(n) {
  return String(n).padStart(2, '0');
}

function formatTime(d) {
  return `${d.getFullYear()}.${pad2(d.getMonth() + 1)}.${pad2(d.getDate())} ${pad2(
    d.getHours(),
  )}:${pad2(d.getMinutes())}`;
}

function toPickerDate(d) {
  return `${d.getFullYear()}-${pad2(d.getMonth() + 1)}-${pad2(d.getDate())}`;
}

function toPickerTime(d) {
  return `${pad2(d.getHours())}:${pad2(d.getMinutes())}`;
}

function pickerToDisplay(date, time) {
  return date.replace(/-/g, '.') + ' ' + time;
}

function buildLocation(detail) {
  if (!detail) return '深圳市·—';
  const street = detail.street || '';
  const addr = detail.address || '';
  let loc;
  if (street && addr && addr.indexOf(street) === 0) {
    loc = addr;
  } else {
    loc = [street, addr].filter(Boolean).join(' ') || '—';
  }
  return '深圳市·' + loc;
}

Page({
  data: {
    showPreview: false,
    watermarkedPath: '',
    orgName: DEFAULT_ORG,
    timeStr: '',
    locationText: '—',
    projectLabel: DEFAULT_PROJECT_LINE,
    takingPhoto: false,
    uploading: false,
    projectId: '',
    photoType: '',
    hazardId: '',
    maskH: 0,
    maskW: 0,
    devicePosition: 'back',
    showTimePicker: false,
    pickerDate: '',
    pickerTime: '',
  },

  _pendingCroppedPath: '',
  _fromAlbum: false,

  _timeTimer: null,
  _cameraCtx: null,
  _screenW: 0,
  _screenH: 0,

  onLoad(options) {
    const projectId = options.projectId != null ? String(options.projectId) : '';
    const type = options.type || '';
    const hazardId = options.hazardId != null ? String(options.hazardId) : '';
    this._projectType = options.projectType || 'longhua';

    if (!projectId) {
      wx.showToast({ title: '缺少项目参数', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    const validTypes = ['facade', 'card', 'rectify', 'license', 'permit', 'record_sheet'];
    if (!validTypes.includes(type)) {
      wx.showToast({ title: '照片类型无效', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    if (type === 'rectify' && !hazardId) {
      wx.showToast({ title: '缺少隐患ID', icon: 'none' });
      setTimeout(() => wx.navigateBack(), 1500);
      return;
    }

    const isW = this._projectType === 'wenti' || this._projectType === 'lvye';
    let title = TITLE_MAP[type] || '拍照';
    if (isW && type === 'facade') title = '拍摄场所照片';
    wx.setNavigationBarTitle({ title });

    const sysInfo = wx.getSystemInfoSync();
    this._screenW = sysInfo.windowWidth;
    this._screenH = sysInfo.windowHeight;

    this._isPortrait = isW && PORTRAIT_TYPES.includes(type);
    const masks = this._calcMasks(this._screenW, this._screenH);

    this.setData({
      projectId,
      photoType: type,
      hazardId,
      timeStr: formatTime(new Date()),
      maskH: masks.maskH,
      maskW: masks.maskW,
      isWenti: isW,
      isPortrait: this._isPortrait,
    });

    this._cameraCtx = wx.createCameraContext();

    if (this._needWatermark()) {
      this._tickTime();
      this._timeTimer = setInterval(() => this._tickTime(), 1000);
      this._loadProject(projectId);
    }
  },

  onUnload() {
    if (this._timeTimer) {
      clearInterval(this._timeTimer);
      this._timeTimer = null;
    }
  },

  _getCropRatio() {
    return this._isPortrait ? PORTRAIT_RATIO : CROP_RATIO;
  },

  _calcMasks(w, h) {
    const ratio = this._getCropRatio();
    const cropH = w / ratio;
    if (cropH <= h) {
      return { maskH: Math.max(0, Math.floor((h - cropH) / 2)), maskW: 0 };
    }
    const cropW = h * ratio;
    return { maskH: 0, maskW: Math.max(0, Math.floor((w - cropW) / 2)) };
  },

  onResize(res) {
    const { windowWidth, windowHeight } = res.size || {};
    if (!windowWidth || !windowHeight) return;
    this._screenW = windowWidth;
    this._screenH = windowHeight;
    this.setData(this._calcMasks(windowWidth, windowHeight));
  },

  _tickTime() {
    if (this.data.showPreview) return;
    this.setData({ timeStr: formatTime(new Date()) });
  },

  _loadProject(projectId) {
    getProjectDetail(projectId)
      .then((detail) => {
        this.setData({ locationText: buildLocation(detail) });
      })
      .catch(() => {
        this.setData({ locationText: '—' });
      });
  },

  _needWatermark() {
    if (this._projectType === 'wenti' || this._projectType === 'lvye') return false;
    return this.data.photoType === 'facade' || this.data.photoType === 'card';
  },

  _cropImage(srcPath) {
    return new Promise((resolve, reject) => {
      const ratio = this._getCropRatio();
      wx.getImageInfo({
        src: srcPath,
        success: (info) => {
          const imgW = info.width;
          const imgH = info.height;
          const targetH = Math.round(imgW / ratio);

          let sx = 0, sy = 0, sw = imgW, sh = imgH;
          let outW = imgW, outH = imgH;

          if (targetH < imgH) {
            sy = Math.round((imgH - targetH) / 2);
            sh = targetH;
            outH = targetH;
          } else {
            const targetW = Math.round(imgH * ratio);
            if (targetW < imgW) {
              sx = Math.round((imgW - targetW) / 2);
              sw = targetW;
              outW = targetW;
            } else {
              resolve(srcPath);
              return;
            }
          }

          const query = this.createSelectorQuery();
          query.select('#cropCanvas').fields({ node: true, size: true }).exec((res) => {
            if (!res || !res[0] || !res[0].node) {
              resolve(srcPath);
              return;
            }

            const canvas = res[0].node;
            canvas.width = outW;
            canvas.height = outH;
            const ctx = canvas.getContext('2d');

            const image = canvas.createImage();
            image.onload = () => {
              ctx.drawImage(image, sx, sy, sw, sh, 0, 0, outW, outH);
              wx.canvasToTempFilePath({
                canvas,
                x: 0,
                y: 0,
                width: outW,
                height: outH,
                destWidth: outW,
                destHeight: outH,
                fileType: 'jpg',
                quality: 0.92,
                success: (r) => resolve(r.tempFilePath),
                fail: () => resolve(srcPath),
              });
            };
            image.onerror = () => resolve(srcPath);
            image.src = info.path || srcPath;
          });
        },
        fail: () => resolve(srcPath),
      });
    });
  },

  onTakePhoto() {
    if (this.data.takingPhoto || !this._cameraCtx) return;
    this._fromAlbum = false;
    this._cameraCtx.takePhoto({
      quality: 'high',
      success: (res) => {
        this._processPhoto(res.tempImagePath);
      },
      fail: () => {
        wx.showToast({ title: '拍照失败', icon: 'none' });
      },
    });
  },

  onFlipCamera() {
    this.setData({
      devicePosition: this.data.devicePosition === 'back' ? 'front' : 'back',
    });
  },

  onChooseAlbum() {
    if (this.data.takingPhoto) return;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['album'],
      sizeType: ['original'],
      success: (res) => {
        const tempPath = res.tempFiles[0].tempFilePath;
        this._fromAlbum = true;
        this._processPhoto(tempPath);
      },
    });
  },

  _processPhoto(rawPath) {
    this.setData({ takingPhoto: true });
    this._cropImage(rawPath).then((croppedPath) => {
      if (this._needWatermark()) {
        const now = new Date();
        this._pendingCroppedPath = croppedPath;
        this.setData({
          takingPhoto: false,
          showTimePicker: true,
          pickerDate: toPickerDate(now),
          pickerTime: toPickerTime(now),
        });
      } else {
        this.setData({ watermarkedPath: croppedPath, showPreview: true, takingPhoto: false });
      }
    });
  },

  onPickerDateChange(e) {
    this.setData({ pickerDate: e.detail.value });
  },

  onPickerTimeChange(e) {
    this.setData({ pickerTime: e.detail.value });
  },

  onTimePickerConfirm() {
    const { pickerDate, pickerTime } = this.data;
    const croppedPath = this._pendingCroppedPath;
    if (!croppedPath) return;

    const timeDisplay = pickerToDisplay(pickerDate, pickerTime);
    this.setData({ showTimePicker: false, takingPhoto: true });

    const opts = {
      orgName: this.data.orgName,
      time: timeDisplay,
      location: this.data.locationText,
      project: this.data.projectLabel,
    };
    applyWatermark(croppedPath, opts)
      .then((path) => {
        this.setData({ watermarkedPath: path, showPreview: true, takingPhoto: false });
      })
      .catch(() => {
        this.setData({ watermarkedPath: croppedPath, showPreview: true, takingPhoto: false });
      });
  },

  onTimePickerCancel() {
    this._pendingCroppedPath = '';
    this.setData({ showTimePicker: false });
  },

  onRetake() {
    this.setData({
      showPreview: false,
      watermarkedPath: '',
      timeStr: formatTime(new Date()),
    });
  },

  _saveToAlbum(filePath) {
    wx.saveImageToPhotosAlbum({
      filePath,
      fail(err) {
        if (/deny|auth/i.test(String(err && err.errMsg))) {
          wx.showModal({
            title: '提示',
            content: '需要相册权限才能保存照片，请前往设置开启',
            confirmText: '去设置',
            success(res) {
              if (res.confirm) wx.openSetting();
            },
          });
        }
      },
    });
  },

  onConfirmUpload() {
    const { watermarkedPath, projectId, photoType, hazardId, uploading } = this.data;
    if (!watermarkedPath || uploading) return;

    this.setData({ uploading: true });

    const p =
      photoType === 'rectify'
        ? uploadRectifyPhoto(hazardId, watermarkedPath)
        : uploadScenePhoto(projectId, photoType, watermarkedPath);

    p.then(() => {
      if ((photoType === 'facade' || photoType === 'card') && this.data.pickerDate) {
        const parts = this.data.pickerDate.split('-');
        const checkDate = `${parts[0]}年${parseInt(parts[1])}月${parseInt(parts[2])}日`;
        updateProject(projectId, { check_date: checkDate }).catch(() => {});
      }

      this.setData({ uploading: false });
      wx.showToast({ title: '上传成功', icon: 'success' });
      const delta = photoType === 'rectify' ? 2 : 1;
      setTimeout(() => wx.navigateBack({ delta }), 1200);
    }).catch(() => {
      this.setData({ uploading: false });
    });
  },
});
