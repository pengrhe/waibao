const {
  getDetections, addDetection, updateDetection, deleteDetection,
  uploadDetectionPhoto, getDetectionPhotoUrl, downloadImage,
} = require('../../utils/api.js');

const TABS = [
  { key: 'infrared', label: '红外检测', multi: true },
  { key: 'ground_resistance', label: '接地电阻', multi: true },
  { key: 'residual_current', label: '剩余电流', multi: false },
  { key: 'insulation', label: '绝缘电阻', multi: false },
  { key: 'terminal', label: '接线端子', multi: false },
  { key: 'indoor_wiring', label: '配电线路', multi: false },
  { key: 'distribution_box', label: '照明配电箱', multi: false },
  { key: 'ceiling_wiring', label: '吊顶线路', multi: false },
  { key: 'grounding', label: '接地联结', multi: false },
];

Page({
  data: {
    tabs: TABS,
    activeTab: 0,
    records: [],
    loading: true,
    showForm: false,
    form: {},
    saving: false,
    editingId: null,
  },

  onLoad(options) {
    this._projectId = options.projectId || '';
  },

  onShow() {
    this.loadRecords();
  },

  onPullDownRefresh() {
    this.loadRecords().finally(() => wx.stopPullDownRefresh());
  },

  onTabChange(e) {
    const idx = parseInt(e.currentTarget.dataset.idx, 10);
    this.setData({ activeTab: idx, showForm: false, editingId: null });
    this.loadRecords();
  },

  currentTab() {
    return TABS[this.data.activeTab] || TABS[0];
  },

  async loadRecords() {
    if (!this._projectId) return;
    this.setData({ loading: true });
    try {
      const tab = this.currentTab();
      const list = await getDetections(this._projectId, tab.key);
      const records = list.map(r => ({
        ...r,
        photoThumb: '',
        _remotePhoto: r.has_photo ? getDetectionPhotoUrl(r.id) : '',
      }));
      this.setData({ records, loading: false });
      this._loadThumbs(records);
    } catch (e) {
      this.setData({ loading: false });
    }
  },

  async _loadThumbs(records) {
    for (let i = 0; i < records.length; i++) {
      const url = records[i]._remotePhoto;
      if (!url) continue;
      try {
        const tmp = await downloadImage(url);
        this.setData({ [`records[${i}].photoThumb`]: tmp });
      } catch (e) { /* ignore */ }
    }
  },

  onShowAddForm() {
    const tab = this.currentTab();
    const form = { location: '总配电箱', code: '', temperature: '', resistance_value: '', result: '', remark: '' };
    if (!tab.multi) {
      form.result = '符合规范要求';
      form.remark = '/';
    }
    this.setData({ showForm: true, editingId: null, form });
  },

  onEditRecord(e) {
    const id = e.currentTarget.dataset.id;
    const rec = this.data.records.find(r => r.id === id);
    if (!rec) return;
    this.setData({
      showForm: true,
      editingId: id,
      form: {
        location: rec.location || '',
        code: rec.code || '',
        temperature: rec.temperature || '',
        resistance_value: rec.resistance_value || '',
        result: rec.result || '',
        remark: rec.remark || '',
      },
    });
  },

  onFormInput(e) {
    const field = e.currentTarget.dataset.field;
    this.setData({ [`form.${field}`]: e.detail.value });
  },

  onCancelForm() {
    this.setData({ showForm: false, editingId: null });
  },

  async onSaveForm() {
    const tab = this.currentTab();
    const { form, editingId } = this.data;
    this.setData({ saving: true });
    try {
      if (editingId) {
        await updateDetection(editingId, form);
      } else {
        await addDetection(this._projectId, { ...form, detection_type: tab.key });
      }
      wx.showToast({ title: '保存成功', icon: 'success' });
      this.setData({ showForm: false, editingId: null, saving: false });
      this.loadRecords();
    } catch (e) {
      this.setData({ saving: false });
    }
  },

  async onDeleteRecord(e) {
    const id = e.currentTarget.dataset.id;
    const res = await new Promise(resolve => {
      wx.showModal({ title: '确认删除', content: '删除此检测记录？', success: resolve });
    });
    if (!res.confirm) return;
    try {
      await deleteDetection(id);
      wx.showToast({ title: '已删除', icon: 'success' });
      this.loadRecords();
    } catch (e) { /* toast shown by api */ }
  },

  onTakePhoto(e) {
    const id = e.currentTarget.dataset.id;
    wx.chooseMedia({
      count: 1,
      mediaType: ['image'],
      sourceType: ['camera', 'album'],
      success: (res) => {
        const filePath = res.tempFiles[0].tempFilePath;
        this._doUploadPhoto(id, filePath);
      },
    });
  },

  async _doUploadPhoto(recordId, filePath) {
    wx.showLoading({ title: '上传中' });
    try {
      await uploadDetectionPhoto(recordId, filePath);
      wx.hideLoading();
      wx.showToast({ title: '上传成功', icon: 'success' });
      this.loadRecords();
    } catch (e) {
      wx.hideLoading();
    }
  },

  onResultPick(e) {
    const val = e.currentTarget.dataset.val;
    this.setData({ 'form.result': val });
  },
});
