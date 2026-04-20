const {
  getHazardTemplates,
  getTemplateCategories,
  addHazard,
} = require('../../utils/api.js');

Page({
  data: {
    projectId: '',
    categories: [],
    currentCat: '',
    templates: [],
    allTemplates: [],
    filteredTemplates: [],
    keyword: '',
    loading: true,
    batchMode: false,
    selected: [],
    editingIdx: -1,
    editDesc: '',
    editSuggestion: '',
    editType: '',
    saving: false,
    addingSingle: false,
  },

  onLoad(options) {
    this.setData({ projectId: options.projectId || '' });
    this._searchTimer = null;
    this.loadCategories();
  },

  async loadCategories() {
    try {
      const cats = await getTemplateCategories();
      if (cats.length) {
        this.setData({ categories: cats, currentCat: cats[0] });
        this.loadTemplates(cats[0]);
        this._loadAllTemplates(cats);
      } else {
        this.setData({ loading: false });
      }
    } catch (e) {
      this.setData({ loading: false });
    }
  },

  async _loadAllTemplates(cats) {
    const all = [];
    for (const cat of cats) {
      try {
        const items = await getHazardTemplates(cat);
        all.push(...items);
      } catch (e) { /* skip */ }
    }
    this._allTemplates = all;
  },

  async loadTemplates(cat) {
    this.setData({ loading: true, currentCat: cat });
    try {
      const templates = await getHazardTemplates(cat);
      this.setData({ templates, loading: false });
    } catch (e) {
      this.setData({ templates: [], loading: false });
    }
  },

  onCatTap(e) {
    const cat = e.currentTarget.dataset.cat;
    if (cat === this.data.currentCat) return;
    this.loadTemplates(cat);
  },

  onSearchInput(e) {
    const keyword = e.detail.value.trim();
    this.setData({ keyword });
    clearTimeout(this._searchTimer);
    if (!keyword) {
      this.setData({ filteredTemplates: [] });
      return;
    }
    this._searchTimer = setTimeout(() => this._doSearch(keyword), 300);
  },

  _doSearch(keyword) {
    const kw = keyword.toLowerCase();
    const all = this._allTemplates || [];
    const filtered = all.filter(t =>
      (t.description || '').toLowerCase().includes(kw) ||
      (t.suggestion || '').toLowerCase().includes(kw) ||
      (t.category || '').toLowerCase().includes(kw)
    );
    this.setData({ filteredTemplates: filtered });
  },

  onClearSearch() {
    this.setData({ keyword: '', filteredTemplates: [] });
  },

  onToggleBatchMode() {
    const entering = !this.data.batchMode;
    this.setData({
      batchMode: entering,
      selected: entering ? this.data.selected : [],
    });
  },

  onTapTemplate(e) {
    const { keyword } = this.data;
    let t;
    if (keyword) {
      const idx = e.currentTarget.dataset.idx;
      t = this.data.filteredTemplates[idx];
    } else {
      const idx = e.currentTarget.dataset.idx;
      t = this.data.templates[idx];
    }
    if (!t) return;

    if (this.data.batchMode) {
      this._toggleSelect(t);
    } else {
      this._addSingle(t);
    }
  },

  _toggleSelect(t) {
    const selected = [...this.data.selected];
    const existIdx = selected.findIndex(s => s.id === t.id);
    if (existIdx >= 0) {
      selected.splice(existIdx, 1);
    } else {
      selected.push({
        id: t.id,
        hazard_type: t.category,
        description: t.description,
        suggestion: t.suggestion || '',
        reference: [t.reference_standard, t.standard_clause].filter(Boolean).join(' '),
      });
    }
    this.setData({ selected });
  },

  async _addSingle(t) {
    if (this.data.addingSingle) return;
    const { projectId } = this.data;
    if (!projectId) return;

    this.setData({ addingSingle: true });
    wx.showLoading({ title: '添加中', mask: true });

    try {
      const res = await addHazard(projectId, {
        hazard_type: t.category || t.hazard_type || '',
        description: t.description,
        suggestion: t.suggestion || '',
        reference: t.reference || [t.reference_standard, t.standard_clause].filter(Boolean).join(' '),
      });
      wx.hideLoading();
      this.setData({ addingSingle: false });
      const hazardId = res.hazard_id;
      wx.redirectTo({
        url: `/pages/hazard/hazard?projectId=${encodeURIComponent(projectId)}&hazardId=${encodeURIComponent(hazardId)}`,
      });
    } catch (e) {
      wx.hideLoading();
      this.setData({ addingSingle: false });
    }
  },

  onCustomAdd() {
    const { projectId } = this.data;
    if (!projectId) return;

    if (this.data.batchMode) {
      const selected = [...this.data.selected];
      selected.push({
        id: `custom_${Date.now()}`,
        hazard_type: '',
        description: '',
        suggestion: '',
        reference: '',
      });
      const newIdx = selected.length - 1;
      this.setData({
        selected,
        editingIdx: newIdx,
        editType: '',
        editDesc: '',
        editSuggestion: '',
      });
    } else {
      this._addCustomSingle();
    }
  },

  async _addCustomSingle() {
    if (this.data.addingSingle) return;
    const { projectId } = this.data;
    this.setData({ addingSingle: true });
    wx.showLoading({ title: '创建中', mask: true });

    try {
      const res = await addHazard(projectId, {
        hazard_type: '',
        description: '新隐患',
        suggestion: '',
        reference: '',
      });
      wx.hideLoading();
      this.setData({ addingSingle: false });
      wx.redirectTo({
        url: `/pages/hazard/hazard?projectId=${encodeURIComponent(projectId)}&hazardId=${encodeURIComponent(res.hazard_id)}`,
      });
    } catch (e) {
      wx.hideLoading();
      this.setData({ addingSingle: false });
    }
  },

  onEditItem(e) {
    const idx = e.currentTarget.dataset.idx;
    const item = this.data.selected[idx];
    if (!item) return;
    this.setData({
      editingIdx: idx,
      editDesc: item.description,
      editSuggestion: item.suggestion,
      editType: item.hazard_type,
    });
  },

  onEditDescInput(e) { this.setData({ editDesc: e.detail.value }); },
  onEditSuggestionInput(e) { this.setData({ editSuggestion: e.detail.value }); },
  onEditTypeInput(e) { this.setData({ editType: e.detail.value }); },

  onSaveEditItem() {
    const { editingIdx, editDesc, editSuggestion, editType, selected } = this.data;
    if (editingIdx < 0 || editingIdx >= selected.length) return;
    selected[editingIdx].description = editDesc;
    selected[editingIdx].suggestion = editSuggestion;
    selected[editingIdx].hazard_type = editType;
    this.setData({ selected, editingIdx: -1 });
  },

  onCancelEdit() { this.setData({ editingIdx: -1 }); },

  onRemoveSelected(e) {
    const idx = e.currentTarget.dataset.idx;
    const selected = [...this.data.selected];
    selected.splice(idx, 1);
    this.setData({ selected });
  },

  async onConfirm() {
    const { selected, projectId } = this.data;
    if (!selected.length || !projectId) return;

    this.setData({ saving: true });
    let success = 0;
    for (const s of selected) {
      try {
        await addHazard(projectId, {
          hazard_type: s.hazard_type,
          description: s.description,
          suggestion: s.suggestion,
          reference: s.reference,
        });
        success++;
      } catch (e) { /* skip */ }
    }

    this.setData({ saving: false });
    wx.showToast({ title: `已添加 ${success} 条隐患`, icon: 'success' });
    setTimeout(() => wx.navigateBack(), 1200);
  },
});
