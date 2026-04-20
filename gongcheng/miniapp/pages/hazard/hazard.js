const {
  getProjectDetail,
  getHazardPhotoUrl,
  getRectifyPhotoUrl,
  uploadRectifyPhoto,
  uploadHazardPhoto,
  updateHazardRemark,
  updateRectifyStatus,
  updateHazard,
  downloadImage,
} = require('../../utils/api.js');

function riskClassFromText(risk) {
  if (!risk) return '';
  const s = String(risk);
  if (/重大|较大/.test(s)) return 'risk-high';
  if (/一般/.test(s)) return 'risk-mid';
  return 'risk-low';
}

function isRectifyDone(h) {
  if (!h) return false;
  return Boolean(h.has_rectify_photo) || h.rectify_status === 'done';
}

Page({
  data: {
    loading: true,
    error: '',
    projectId: '',
    hazardId: '',
    projectName: '',
    projectAddress: '',
    hazard: null,
    hazardPhotoUrl: '',
    rectifyPhotoUrl: '',
    statusTagClass: 'status-pending',
    statusText: '未整改',
    riskClass: '',
    remarkText: '',
    remarkDraft: '',
    editingRemark: false,
    savingRemark: false,
    isWenti: false,
    editingHazard: false,
    hazardEditForm: {},
    savingHazard: false,
  },

  onLoad(options) {
    const projectId = options.projectId != null ? String(options.projectId) : '';
    const hazardId = options.hazardId != null ? String(options.hazardId) : '';
    this._newCreated = options.newCreated === '1';
    this.setData({ projectId, hazardId });
    if (!projectId || !hazardId) {
      this.setData({ loading: false, error: '缺少 projectId 或 hazardId 参数' });
    }
  },

  onShow() {
    const { projectId, hazardId } = this.data;
    if (projectId && hazardId) {
      this.loadData();
    }
  },

  async loadData() {
    const { projectId, hazardId } = this.data;
    if (!projectId || !hazardId) return;

    this.setData({ loading: true, error: '' });

    try {
      const detail = await getProjectDetail(projectId);
      const hazards = detail.hazards || [];
      const hazard = hazards.find((h) => String(h.id) === String(hazardId));

      if (!hazard) {
        this.setData({
          loading: false,
          error: '未找到该隐患',
          hazard: null,
          hazardPhotoUrl: '',
          rectifyPhotoUrl: '',
        });
        return;
      }

      const ts = Date.now();
      const hazardRemoteUrl = hazard.has_hazard_photo
        ? `${getHazardPhotoUrl(projectId, hazardId)}?t=${ts}`
        : '';
      const rectifyRemoteUrl = hazard.has_rectify_photo
        ? `${getRectifyPhotoUrl(projectId, hazardId)}?t=${ts}`
        : '';

      const done = isRectifyDone(hazard);
      const isWenti = detail.project_type === 'wenti';
      const autoEdit = this._newCreated && !hazard.description;
      this._newCreated = false;
      this.setData({
        loading: false,
        error: '',
        projectName: detail.name || '',
        projectAddress: detail.address || '',
        hazard,
        hazardPhotoUrl: '',
        rectifyPhotoUrl: '',
        statusTagClass: done ? 'status-done' : 'status-pending',
        statusText: done ? '已整改' : '待整改',
        riskClass: riskClassFromText(hazard.risk),
        remarkText: hazard.remark || '',
        editingRemark: false,
        isWenti,
        editingHazard: false,
      });

      if (autoEdit) {
        this.onEditHazard();
      }

      if (hazardRemoteUrl) {
        downloadImage(hazardRemoteUrl).then((tmp) => {
          this.setData({ hazardPhotoUrl: tmp });
        }).catch(() => {});
      }
      if (rectifyRemoteUrl) {
        downloadImage(rectifyRemoteUrl).then((tmp) => {
          this.setData({ rectifyPhotoUrl: tmp });
        }).catch(() => {});
      }
    } catch (e) {
      this.setData({
        loading: false,
        error: '加载失败，请稍后重试',
        hazard: null,
      });
    }
  },

  onPreviewHazardPhoto() {
    const u = this.data.hazardPhotoUrl;
    if (!u) return;
    const all = [u, this.data.rectifyPhotoUrl].filter(Boolean);
    wx.previewImage({ current: u, urls: all });
  },

  onPreviewRectifyPhoto() {
    const u = this.data.rectifyPhotoUrl;
    if (!u) return;
    const all = [this.data.hazardPhotoUrl, u].filter(Boolean);
    wx.previewImage({ current: u, urls: all });
  },

  onEditRemark() {
    this.setData({
      editingRemark: true,
      remarkDraft: this.data.remarkText || '',
    });
  },

  onRemarkInput(e) {
    this.setData({ remarkDraft: e.detail.value });
  },

  onCancelRemark() {
    this.setData({ editingRemark: false, remarkDraft: '' });
  },

  async onSaveRemark() {
    const { hazardId, remarkDraft } = this.data;
    if (this.data.savingRemark) return;

    this.setData({ savingRemark: true });
    try {
      await updateHazardRemark(Number(hazardId), remarkDraft);
      this.setData({
        remarkText: remarkDraft,
        editingRemark: false,
        savingRemark: false,
      });
      const hazard = this.data.hazard;
      if (hazard) {
        hazard.remark = remarkDraft;
        this.setData({ hazard });
      }
      wx.showToast({ title: '保存成功', icon: 'success' });
    } catch (e) {
      this.setData({ savingRemark: false });
    }
  },

  async onToggleRectifyStatus() {
    const { hazard, hazardId } = this.data;
    if (!hazard) return;
    const currentDone = hazard.rectify_status === 'done';
    const newStatus = currentDone ? 'pending' : 'done';
    try {
      await updateRectifyStatus(Number(hazardId), newStatus);
      hazard.rectify_status = newStatus;
      const done = newStatus === 'done';
      this.setData({
        hazard,
        statusTagClass: done ? 'status-done' : 'status-pending',
        statusText: done ? '已整改' : '待整改',
      });
      wx.showToast({ title: done ? '已标记为已整改' : '已标记为待整改', icon: 'success' });
    } catch (e) {
      wx.showToast({ title: '状态更新失败', icon: 'none' });
    }
  },

  goRectifyCamera() {
    const { projectId, hazardId, projectName, projectAddress } = this.data;
    const q = [
      `projectId=${encodeURIComponent(projectId)}`,
      `hazardId=${encodeURIComponent(hazardId)}`,
      'type=rectify',
    ].join('&');
    wx.navigateTo({
      url: `/pages/camera/camera?${q}`,
      events: {
        rectifyCaptured: (data) => {
          this.onRectifyPhotoFromCamera(data);
        },
      },
      success: (res) => {
        if (res.eventChannel && res.eventChannel.emit) {
          res.eventChannel.emit('hazardContext', {
            projectId,
            hazardId,
            projectName,
            projectAddress,
          });
        }
      },
    });
  },

  async onRectifyPhotoFromCamera(payload) {
    const tempFilePath = payload && payload.tempFilePath;
    if (!tempFilePath) return;

    const { hazardId } = this.data;
    wx.showLoading({ title: '上传中…', mask: true });

    try {
      await uploadRectifyPhoto(Number(hazardId), tempFilePath);
      wx.showToast({ title: '上传成功', icon: 'success' });
      await this.loadData();
    } catch (err) {
      /* uploadRectifyPhoto 内已 toast */
    } finally {
      wx.hideLoading();
    }
  },

  onEditHazard() {
    const h = this.data.hazard;
    if (!h) return;
    const form = {
      hazard_type: h.hazard_type || '',
      description: h.description || '',
      suggestion: h.suggestion || '',
      reference: h.reference || '',
    };
    if (!this.data.isWenti) {
      form.risk = h.risk || '';
    }
    this.setData({
      editingHazard: true,
      hazardEditForm: form,
    });
  },

  onCancelEditHazard() {
    this.setData({ editingHazard: false, hazardEditForm: {} });
  },

  onHazardEditInput(e) {
    const field = e.currentTarget.dataset.field;
    if (!field) return;
    this.setData({ [`hazardEditForm.${field}`]: e.detail.value });
  },

  async onSaveEditHazard() {
    const { hazardId, hazardEditForm } = this.data;
    if (this.data.savingHazard) return;
    this.setData({ savingHazard: true });
    try {
      await updateHazard(Number(hazardId), hazardEditForm);
      wx.showToast({ title: '保存成功', icon: 'success' });
      this.setData({ editingHazard: false, savingHazard: false });
      this.loadData();
    } catch (e) {
      this.setData({ savingHazard: false });
    }
  },

  onChooseHazardPhoto() {
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera', 'album'],
      success: (res) => {
        const tempFilePath = res.tempFiles[0].tempFilePath;
        this.doUploadHazardPhoto(tempFilePath);
      },
    });
  },

  async doUploadHazardPhoto(tempFilePath) {
    if (!tempFilePath) return;
    const { hazardId } = this.data;
    wx.showLoading({ title: '上传中…', mask: true });
    try {
      await uploadHazardPhoto(Number(hazardId), tempFilePath);
      wx.showToast({ title: '上传成功', icon: 'success' });
      await this.loadData();
    } catch (err) {
      /* api 内已 toast */
    } finally {
      wx.hideLoading();
    }
  },
});
