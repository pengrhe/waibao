const { getChecklist, updateChecklist, initChecklist } = require('../../utils/api.js');

const TABLE_NAMES = {
  17: '配电装置及线路(1)',
  18: '配电装置及线路(2)',
  19: '开关、插座',
  20: '剩余电流保护装置',
  21: '室内低压配电线路(1)',
  22: '室内低压配电线路(2)',
  23: '照明装置(1)',
  24: '照明装置(2)',
};

const RESULT_OPTIONS = ['符合规范要求', '不符合规范要求', '-', '/'];

Page({
  data: {
    tableNames: TABLE_NAMES,
    tableKeys: [17, 18, 19, 20, 21, 22, 23, 24],
    activeTable: 17,
    items: [],
    loading: true,
    saving: false,
    dirty: false,
    resultOptions: RESULT_OPTIONS,
  },

  onLoad(options) {
    this._projectId = options.projectId || '';
  },

  onShow() {
    this._init();
  },

  onPullDownRefresh() {
    this.loadItems().finally(() => wx.stopPullDownRefresh());
  },

  async _init() {
    if (!this._projectId) return;
    try {
      await initChecklist(this._projectId);
    } catch (e) { /* may already exist */ }
    this.loadItems();
  },

  onTableChange(e) {
    const ti = parseInt(e.currentTarget.dataset.ti, 10);
    if (this.data.dirty) {
      this._saveBeforeSwitch(ti);
      return;
    }
    this.setData({ activeTable: ti });
    this.loadItems();
  },

  async _saveBeforeSwitch(nextTable) {
    await this._doSave();
    this.setData({ activeTable: nextTable });
    this.loadItems();
  },

  async loadItems() {
    this.setData({ loading: true });
    try {
      const list = await getChecklist(this._projectId, this.data.activeTable);
      this.setData({ items: list, loading: false, dirty: false });
    } catch (e) {
      this.setData({ loading: false });
    }
  },

  onResultChange(e) {
    const idx = e.currentTarget.dataset.idx;
    const pickerIdx = e.detail.value;
    const result = RESULT_OPTIONS[pickerIdx];
    this.setData({
      [`items[${idx}].result`]: result,
      dirty: true,
    });
  },

  async onSave() {
    await this._doSave();
    wx.showToast({ title: '保存成功', icon: 'success' });
  },

  async _doSave() {
    const { items, activeTable } = this.data;
    this.setData({ saving: true });
    try {
      const payload = items.map(it => ({
        table_index: activeTable,
        item_seq: it.item_seq,
        result: it.result,
      }));
      await updateChecklist(this._projectId, payload);
      this.setData({ saving: false, dirty: false });
    } catch (e) {
      this.setData({ saving: false });
    }
  },

  onUnload() {
    if (this.data.dirty) {
      this._doSave();
    }
  },
});
