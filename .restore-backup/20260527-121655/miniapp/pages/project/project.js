const {
  getProjectDetail,
  getHazardPhotoUrl,
  getRectifyPhotoUrl,
  getBaseUrl,
  downloadImage,
  updateProject,
  deleteHazard,
  updateRectifyStatus,
  getInspectors,
  addInspector,
  addHazard,
} = require('../../utils/api.js');

const DESC_MAX = 72;

function truncateDesc(text) {
  const s = String(text || '').trim();
  if (!s) return '—';
  if (s.length <= DESC_MAX) return s;
  return `${s.slice(0, DESC_MAX)}…`;
}

function scenePhotoUrl(projectId, photoType, cacheBust) {
  const base = getBaseUrl();
  const q = `photo_type=${encodeURIComponent(photoType)}${cacheBust ? `&_t=${cacheBust}` : ''}`;
  return `${base}/api/projects/${encodeURIComponent(projectId)}/scene-photo?${q}`;
}

function hasSceneType(scenePhotos, type) {
  if (!Array.isArray(scenePhotos)) return false;
  return scenePhotos.some((p) => p && p.photo_type === type);
}

Page({
  data: {
    loading: true,
    loadError: '',
    project: null,
    hazards: [],
    facadeSrc: '',
    cardSrc: '',
    licenseSrc: '',
    permitSrc: '',
    recordSheetSrc: '',
    facadeUploaded: false,
    cardUploaded: false,
    licenseUploaded: false,
    permitUploaded: false,
    recordSheetUploaded: false,
    allSceneDone: false,
    isWenti: false,
    editing: false,
    editForm: {},
    inspectorList: [],
    inspectorNames: [],
    inspectorRealNames: [],
    inspectorIndex: -1,
  },

  onLoad(options) {
    const id = options.id || options.projectId;
    this._projectId = id ? String(id) : '';
  },

  onShow() {
    if (this._projectId) {
      this.loadDetail();
    } else {
      this.setData({
        loading: false,
        loadError: '缺少项目参数',
      });
    }
  },

  onPullDownRefresh() {
    this.loadDetail().finally(() => {
      wx.stopPullDownRefresh();
    });
  },

  async loadDetail() {
    const id = this._projectId;
    if (!id) return;

    this.setData({ loading: true, loadError: '' });

    try {
      const p = await getProjectDetail(id);
      const bust = Date.now();
      const isWenti = p.project_type === 'wenti' || p.project_type === 'lvye';
      const facadeUploaded = hasSceneType(p.scene_photos, 'facade');
      const cardUploaded = hasSceneType(p.scene_photos, 'card');
      const licenseUploaded = hasSceneType(p.scene_photos, 'license');
      const permitUploaded = hasSceneType(p.scene_photos, 'permit');
      const recordSheetUploaded = hasSceneType(p.scene_photos, 'record_sheet');

      const hazards = (p.hazards || []).map((h) => ({
        ...h,
        descSummary: truncateDesc(h.description),
        photoThumb: '',
        rectifyThumb: '',
        _remoteThumb: h.has_hazard_photo ? getHazardPhotoUrl(id, h.id) : '',
        _remoteRectify: h.has_rectify_photo ? `${getRectifyPhotoUrl(id, h.id)}?t=${bust}` : '',
        statusLabel: h.rectify_status === 'done' ? '已整改' : '待整改',
        statusDone: h.rectify_status === 'done',
      }));

      const allSceneDone = isWenti
        ? facadeUploaded
        : (facadeUploaded && cardUploaded);

      this.setData({
        loading: false,
        project: p,
        hazards,
        isWenti,
        facadeUploaded,
        cardUploaded,
        licenseUploaded,
        permitUploaded,
        recordSheetUploaded,
        facadeSrc: '',
        cardSrc: '',
        licenseSrc: '',
        permitSrc: '',
        recordSheetSrc: '',
        allSceneDone,
      });

      this._loadImages(id, bust, facadeUploaded, cardUploaded, licenseUploaded, permitUploaded, recordSheetUploaded, hazards);
    } catch (e) {
      this.setData({
        loading: false,
        loadError: '加载失败，请下拉重试',
      });
    }
  },

  async _loadImages(id, bust, facadeUploaded, cardUploaded, licenseUploaded, permitUploaded, recordSheetUploaded, hazards) {
    const tasks = [];
    if (facadeUploaded) {
      tasks.push({ url: scenePhotoUrl(id, 'facade', bust), key: 'facadeSrc' });
    }
    if (cardUploaded) {
      tasks.push({ url: scenePhotoUrl(id, 'card', bust), key: 'cardSrc' });
    }
    if (licenseUploaded) {
      tasks.push({ url: scenePhotoUrl(id, 'license', bust), key: 'licenseSrc' });
    }
    if (permitUploaded) {
      tasks.push({ url: scenePhotoUrl(id, 'permit', bust), key: 'permitSrc' });
    }
    if (recordSheetUploaded) {
      tasks.push({ url: scenePhotoUrl(id, 'record_sheet', bust), key: 'recordSheetSrc' });
    }
    hazards.forEach((h, i) => {
      if (h._remoteThumb) {
        tasks.push({ url: h._remoteThumb, key: `hazards[${i}].photoThumb` });
      }
      if (h._remoteRectify) {
        tasks.push({ url: h._remoteRectify, key: `hazards[${i}].rectifyThumb` });
      }
    });

    const BATCH = 3;
    for (let i = 0; i < tasks.length; i += BATCH) {
      const batch = tasks.slice(i, i + BATCH);
      const results = await Promise.allSettled(
        batch.map((t) => downloadImage(t.url).then((tmp) => ({ key: t.key, tmp })))
      );
      const update = {};
      results.forEach((r) => {
        if (r.status === 'fulfilled') {
          update[r.value.key] = r.value.tmp;
        }
      });
      if (Object.keys(update).length) {
        this.setData(update);
      }
    }
  },

  onOpenCamera(e) {
    const type = e.currentTarget.dataset.type;
    if (!this._projectId || !type) return;
    const pt = this.data.project?.project_type || (this.data.isWenti ? 'wenti' : 'longhua');
    wx.navigateTo({
      url: `/pages/camera/camera?projectId=${encodeURIComponent(this._projectId)}&type=${encodeURIComponent(type)}&projectType=${pt}`,
    });
  },

  onOpenHazard(e) {
    const hazardId = e.currentTarget.dataset.id;
    if (!this._projectId || hazardId == null) return;
    wx.navigateTo({
      url: `/pages/hazard/hazard?projectId=${encodeURIComponent(this._projectId)}&hazardId=${encodeURIComponent(hazardId)}`,
    });
  },

  async onStartEdit() {
    const p = this.data.project;
    if (!p) return;
    const form = {
      name: p.name || '',
      street: p.street || '',
      address: p.address || '',
      contact: p.contact || '',
      phone: p.phone || '',
      category: p.category || '',
    };
    if (p.project_type === 'wenti' || p.project_type === 'lvye') {
      form.inspectors = p.inspectors || '';
      form.check_date = p.check_date || '';
      form.area = p.area || '';
      form.floor_info = p.floor_info || '';
    } else {
      form.inspectors = p.inspectors || '';
      form.check_date = p.check_date || '';
    }
    this.setData({ editing: true, editForm: form });

    if (p.project_type !== 'wenti' && p.project_type !== 'lvye') {
      this._loadInspectorList(p.street, form.inspectors);
    }
  },

  async _loadInspectorList(street, currentInspector) {
    const GROUP_LABEL = { A: '1组', B: '2组' };
    const STREET_GROUP = {
      观澜: 'A', 观湖: 'A', 福城: 'A',
      民治: 'B', 龙华: 'B', 大浪: 'B',
    };
    try {
      const list = await getInspectors();
      const groups = {};
      list.forEach((i) => {
        if (!groups[i.street_group]) groups[i.street_group] = [];
        groups[i.street_group].push(i.name);
      });
      const groupKeys = Object.keys(groups).sort();
      const displayNames = groupKeys.map((g) => {
        const label = GROUP_LABEL[g] || g;
        return `${label} ${groups[g].join('\u3001')}`;
      });
      const realNames = groupKeys.map((g) => groups[g].join('\u3001'));
      let idx = -1;
      if (currentInspector) {
        idx = realNames.indexOf(currentInspector);
      }
      if (idx === -1 && street) {
        let matchGroup = '';
        for (const [k, g] of Object.entries(STREET_GROUP)) {
          if (street.includes(k)) { matchGroup = g; break; }
        }
        if (matchGroup) {
          const gi = groupKeys.indexOf(matchGroup);
          if (gi !== -1) {
            idx = gi;
            this.setData({ 'editForm.inspectors': realNames[gi] });
          }
        }
      }
      this.setData({
        inspectorList: list,
        inspectorNames: displayNames,
        inspectorRealNames: realNames,
        inspectorIndex: idx,
      });
    } catch (e) {
      this.setData({ inspectorList: [], inspectorNames: [], inspectorRealNames: [], inspectorIndex: -1 });
    }
  },

  onCancelEdit() {
    this.setData({ editing: false, editForm: {} });
  },

  onInspectorChange(e) {
    const idx = Number(e.detail.value);
    const name = this.data.inspectorRealNames[idx] || '';
    this.setData({
      inspectorIndex: idx,
      'editForm.inspectors': name,
    });
  },

  onAddInspector() {
    const self = this;
    wx.showModal({
      title: '添加新成员',
      placeholderText: '请输入姓名',
      editable: true,
      success: async (res) => {
        if (!res.confirm) return;
        const name = (res.content || '').trim();
        if (!name) {
          wx.showToast({ title: '姓名不能为空', icon: 'none' });
          return;
        }
        const street = self.data.project && self.data.project.street || '';
        try {
          await addInspector(name, street);
          await self._loadInspectorList(street, name);
          const idx = self.data.inspectorRealNames.indexOf(name);
          self.setData({
            inspectorIndex: idx,
            'editForm.inspectors': name,
          });
          wx.showToast({ title: '添加成功', icon: 'success' });
        } catch (e) {
          wx.showToast({ title: '添加失败', icon: 'none' });
        }
      },
    });
  },

  onEditInput(e) {
    const field = e.currentTarget.dataset.field;
    if (!field) return;
    this.setData({ [`editForm.${field}`]: e.detail.value });
  },

  async onSaveEdit() {
    const { editForm } = this.data;
    const id = this._projectId;
    if (!id) return;
    try {
      await updateProject(id, editForm);
      wx.showToast({ title: '保存成功', icon: 'success' });
      this.setData({ editing: false, editForm: {} });
      this.loadDetail();
    } catch (e) {
      wx.showToast({ title: '保存失败', icon: 'none' });
    }
  },

  onAddHazard() {
    if (!this._projectId) return;
    const self = this;
    wx.showActionSheet({
      itemList: ['手动新建', '从模板库选择'],
      success(res) {
        if (res.tapIndex === 0) {
          self._createBlankHazard();
        } else if (res.tapIndex === 1) {
          wx.navigateTo({
            url: `/pages/template-select/template-select?projectId=${encodeURIComponent(self._projectId)}`,
          });
        }
      },
    });
  },

  async _createBlankHazard() {
    const projectId = this._projectId;
    if (!projectId) return;
    wx.showLoading({ title: '创建中', mask: true });
    try {
      const res = await addHazard(projectId, {
        hazard_type: '',
        description: '',
        suggestion: '',
        reference: '',
      });
      wx.hideLoading();
      wx.navigateTo({
        url: `/pages/hazard/hazard?projectId=${encodeURIComponent(projectId)}&hazardId=${encodeURIComponent(res.hazard_id)}&newCreated=1`,
      });
    } catch (e) {
      wx.hideLoading();
    }
  },

  onOpenDetection() {
    if (!this._projectId) return;
    wx.navigateTo({
      url: `/pages/detection/detection?projectId=${encodeURIComponent(this._projectId)}`,
    });
  },

  onOpenChecklist() {
    if (!this._projectId) return;
    wx.navigateTo({
      url: `/pages/checklist/checklist?projectId=${encodeURIComponent(this._projectId)}`,
    });
  },

  async onToggleStatus(e) {
    const hazardId = e.currentTarget.dataset.id;
    const index = e.currentTarget.dataset.index;
    if (hazardId == null || index == null) return;
    const hazard = this.data.hazards[index];
    if (!hazard) return;

    const currentDone = hazard.statusDone;
    const newStatus = currentDone ? 'pending' : 'done';
    try {
      await updateRectifyStatus(Number(hazardId), newStatus);
      const done = newStatus === 'done';
      this.setData({
        [`hazards[${index}].statusDone`]: done,
        [`hazards[${index}].statusLabel`]: done ? '已整改' : '未整改',
      });
      wx.showToast({ title: done ? '已整改' : '未整改', icon: 'success' });
    } catch (err) {
      wx.showToast({ title: '状态更新失败', icon: 'none' });
    }
  },

  async onDeleteHazard(e) {
    const hazardId = e.currentTarget.dataset.id;
    if (!hazardId) return;
    const res = await new Promise(resolve => {
      wx.showModal({
        title: '确认删除',
        content: '确定要删除此隐患记录吗？',
        success: resolve,
      });
    });
    if (!res.confirm) return;
    try {
      await deleteHazard(hazardId);
      wx.showToast({ title: '已删除', icon: 'success' });
      this.loadDetail();
    } catch (e) {
      wx.showToast({ title: '删除失败', icon: 'none' });
    }
  },
});
