const api = require('../../utils/api.js');

function formatCheckDate(checkDate) {
  if (!checkDate) return '--';
  const s = String(checkDate);
  const m = s.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (m) return `${m[1]}-${m[2]}-${m[3]}`;
  return s.length > 10 ? s.slice(0, 10) : s;
}

function statusClass(status) {
  if (status === 'done') return 'tag-done';
  if (status === 'progress') return 'tag-progress';
  return 'tag-pending';
}

function statusText(status) {
  if (status === 'done') return '已完成';
  if (status === 'progress') return '进行中';
  return '待处理';
}

function enrichProject(p) {
  const totalNeeded = p.total_photos || (p.hazard_count || 0) + 2;
  const totalUploaded = p.total_uploaded || 0;
  const percent = totalNeeded > 0 ? Math.round((totalUploaded / totalNeeded) * 100) : 0;
  let progressColor = '#ef4444';
  if (percent === 100) progressColor = '#10b981';
  else if (percent > 0) progressColor = '#6366f1';
  return {
    ...p,
    totalNeeded,
    totalUploaded,
    progressPercent: Math.min(percent, 100),
    progressColor,
    statusClass: statusClass(p.status),
    statusText: statusText(p.status),
    dateStr: formatCheckDate(p.check_date),
  };
}

function filterProjects(list, keyword) {
  const k = (keyword || '').trim().toLowerCase();
  if (!k) return list;
  return list.filter((p) => {
    const name = (p.name || '').toLowerCase();
    const addr = (p.address || '').toLowerCase();
    const contact = (p.contact || '').toLowerCase();
    return name.includes(k) || addr.includes(k) || contact.includes(k);
  });
}

function extractStreets(list) {
  const set = {};
  list.forEach((p) => {
    const s = p.street || '未分类街道';
    set[s] = (set[s] || 0) + 1;
  });
  return Object.keys(set).map((s) => ({ name: s, count: set[s] }));
}

function groupByStreet(list) {
  const map = {};
  const order = [];
  list.forEach((p) => {
    const street = p.street || '未分类街道';
    if (!map[street]) {
      map[street] = [];
      order.push(street);
    }
    map[street].push(enrichProject(p));
  });
  return order.map((street) => ({
    street,
    count: map[street].length,
    projects: map[street],
  }));
}

function extractSourceFiles(list) {
  const map = {};
  list.forEach((p) => {
    const sf = p.source_file || '未分类';
    if (!map[sf]) map[sf] = 0;
    map[sf]++;
  });
  return Object.keys(map).map((name) => ({ name, count: map[name] }));
}

Page({
  data: {
    keyword: '',
    projectType: '',
    projectTypeLabel: '',
    showTypeModal: false,
    sections: [],
    loading: true,
    error: '',
    _rawList: [],
    sourceFiles: [],
    activeSource: '',
    streetList: [],
    activeStreet: '',
  },

  onLoad() {
    const saved = wx.getStorageSync('projectType');
    const TYPE_LABELS = { longhua: '龙华项目', wenti: '文体项目', lvye: '旅业项目' };
    if (saved === 'longhua' || saved === 'wenti' || saved === 'lvye') {
      this.setData({
        projectType: saved,
        projectTypeLabel: TYPE_LABELS[saved] || saved,
      });
      this.loadProjects();
    } else {
      this.setData({ showTypeModal: true, loading: false });
    }
  },

  onPullDownRefresh() {
    this.loadProjects();
  },

  onSearchInput(e) {
    const keyword = e.detail.value || '';
    this.setData({ keyword });
    this.applyFilter();
  },

  applyFilter() {
    const { _rawList, keyword, activeSource, activeStreet } = this.data;
    let list = _rawList;
    if (activeSource) {
      list = list.filter((p) => (p.source_file || '未分类') === activeSource);
    }
    if (activeStreet) {
      list = list.filter((p) => (p.street || '未分类街道') === activeStreet);
    }
    list = filterProjects(list, keyword);
    this.setData({ sections: groupByStreet(list) });
  },

  onSelectType(e) {
    const type = e.currentTarget.dataset.type;
    if (!type) return;
    const TYPE_LABELS = { longhua: '龙华项目', wenti: '文体项目', lvye: '旅业项目' };
    wx.setStorageSync('projectType', type);
    this.setData({
      projectType: type,
      projectTypeLabel: TYPE_LABELS[type] || type,
      showTypeModal: false,
      activeSource: '',
    });
    this.loadProjects();
  },

  onSwitchType() {
    const TYPE_ITEMS = ['龙华项目', '文体项目', '旅业项目'];
    const TYPE_KEYS = ['longhua', 'wenti', 'lvye'];
    wx.showActionSheet({
      itemList: TYPE_ITEMS,
      success: (res) => {
        const type = TYPE_KEYS[res.tapIndex];
        if (type === this.data.projectType) return;
        wx.setStorageSync('projectType', type);
        this.setData({
          projectType: type,
          projectTypeLabel: TYPE_ITEMS[res.tapIndex],
          activeSource: '',
        });
        this.loadProjects();
      },
    });
  },

  onSourceTap(e) {
    const name = e.currentTarget.dataset.name || '';
    const current = this.data.activeSource;
    this.setData({ activeSource: current === name ? '' : name });
    this.applyFilter();
  },

  onStreetTap(e) {
    const name = e.currentTarget.dataset.street || '';
    const current = this.data.activeStreet;
    this.setData({ activeStreet: current === name ? '' : name });
    this.applyFilter();
  },

  loadProjects() {
    this.setData({ loading: true, error: '' });
    const params = {};
    if (this.data.projectType) params.project_type = this.data.projectType;
    api
      .getProjects(params)
      .then((list) => {
        const arr = Array.isArray(list) ? list : [];
        this.setData({
          _rawList: arr,
          sourceFiles: extractSourceFiles(arr),
          streetList: extractStreets(arr),
          loading: false,
          error: '',
        });
        this.applyFilter();
      })
      .catch((err) => {
        const msg =
          (err && err.message) || (typeof err === 'string' ? err : '网络错误');
        this.setData({
          loading: false,
          error: msg,
          sections: [],
          _rawList: [],
          sourceFiles: [],
        });
      })
      .finally(() => {
        wx.stopPullDownRefresh();
      });
  },

  onCardTap(e) {
    const id = e.currentTarget.dataset.id;
    if (id == null) return;
    wx.navigateTo({
      url: `/pages/project/project?id=${id}`,
    });
  },

  onCreateProject() {
    const type = this.data.projectType || 'wenti';
    wx.navigateTo({
      url: `/pages/create-project/create-project?type=${type}`,
    });
  },
});
