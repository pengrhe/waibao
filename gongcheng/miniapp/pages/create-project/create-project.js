const { createProject } = require('../../utils/api.js');

const CATEGORIES = [
  '网吧', '游艺娱乐场所', '歌舞娱乐场所', '游泳场所',
  '健身场所', '体育场馆', '棋牌室', '其他',
];

Page({
  data: {
    projectType: 'wenti',
    form: {
      name: '',
      street: '',
      address: '',
      contact: '',
      phone: '',
      category: '',
      report_code: '',
      area: '',
      floor_info: '',
      inspectors: '',
      check_date: '',
      build_unit: '',
      construct_unit: '',
      supervise_unit: '',
    },
    categories: CATEGORIES,
    categoryIndex: -1,
    submitting: false,
  },

  onLoad(options) {
    const type = options.type || wx.getStorageSync('projectType') || 'wenti';
    this.setData({ projectType: type });
    wx.setNavigationBarTitle({
      title: type === 'wenti' ? '新建文体项目' : '新建龙华项目',
    });
  },

  onInput(e) {
    const field = e.currentTarget.dataset.field;
    if (!field) return;
    this.setData({ [`form.${field}`]: e.detail.value });
  },

  onCategoryChange(e) {
    const idx = Number(e.detail.value);
    this.setData({
      categoryIndex: idx,
      'form.category': CATEGORIES[idx] || '',
    });
  },

  async onSubmit() {
    const { form, projectType } = this.data;
    if (!form.name.trim()) {
      wx.showToast({ title: '请输入项目名称', icon: 'none' });
      return;
    }

    this.setData({ submitting: true });

    try {
      const res = await createProject({
        ...form,
        project_type: projectType,
      });
      wx.showToast({ title: '创建成功', icon: 'success' });
      const projectId = res.project_id;
      setTimeout(() => {
        wx.redirectTo({
          url: `/pages/project/project?id=${projectId}`,
        });
      }, 800);
    } catch (e) {
      this.setData({ submitting: false });
    }
  },
});
