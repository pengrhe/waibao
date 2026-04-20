const api = require('./utils/api.js');

App({
  globalData: {
    /** 与后台管理页同一套服务；本地调试可改为 http://127.0.0.1:8900 */
    baseUrl: 'https://me6lyl8xtw9bg7x.shanxiangjiaoyu.com/gongcheng',
  },
  onLaunch() {
    api.setBaseUrl(this.globalData.baseUrl);
  },
});
