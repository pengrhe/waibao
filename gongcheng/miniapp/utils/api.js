/**
 * 微信小程序 HTTP / 上传封装
 * 默认与线上一致；app.js onLaunch 会 setBaseUrl(globalData.baseUrl)
 */

const DEFAULT_BASE_URL = 'https://me6lyl8xtw9bg7x.shanxiangjiaoyu.com/gongcheng';

let baseUrl = DEFAULT_BASE_URL.replace(/\/$/, '');

function setBaseUrl(url) {
  baseUrl = (url || DEFAULT_BASE_URL).replace(/\/$/, '');
}

function getBaseUrl() {
  return baseUrl;
}

function buildQuery(params) {
  if (!params || typeof params !== 'object') return '';
  const parts = [];
  Object.keys(params).forEach((key) => {
    const v = params[key];
    if (v === undefined || v === null) return;
    parts.push(`${encodeURIComponent(key)}=${encodeURIComponent(String(v))}`);
  });
  return parts.length ? `?${parts.join('&')}` : '';
}

function toast(title) {
  const t = String(title || '请求失败').slice(0, 32);
  wx.showToast({ title: t, icon: 'none', duration: 2500 });
}

function failHint(errMsg) {
  const s = String(errMsg || '');
  if (/合法域名|domain list|not in domain|url not in domain/i.test(s)) {
    return '域名未在小程序后台配置';
  }
  if (/certificate|ssl|证书|TLS/i.test(s)) {
    return 'HTTPS证书异常';
  }
  if (/timeout|超时/i.test(s)) {
    return '请求超时，请重试';
  }
  return '网络异常';
}

/**
 * 通用请求（GET/POST 等）
 * @param {object} options
 * @param {string} options.url 相对路径，如 /api/projects
 * @param {string} [options.method='GET']
 * @param {object} [options.data]
 * @param {object} [options.header]
 * @param {boolean} [options.showErrorToast=true] 是否自动 toast
 */
function request(options) {
  const {
    url,
    method = 'GET',
    data,
    header = {},
    showErrorToast = true,
  } = options;

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${baseUrl}${url}`,
      method,
      data: data || {},
      header: {
        'Content-Type': 'application/json',
        ...header,
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data);
          return;
        }
        const msg =
          (res.data && (res.data.message || res.data.msg || res.data.error)) ||
          `请求失败(${res.statusCode})`;
        if (showErrorToast) toast(msg);
        reject(res);
      },
      fail(err) {
        if (showErrorToast) toast(failHint(err && err.errMsg));
        reject(err);
      },
    });
  });
}

/**
 * 文件上传（multipart/form-data）
 * @param {object} options
 * @param {string} options.url 相对路径
 * @param {string} options.filePath 本地临时路径
 * @param {string} [options.name='file'] 表单字段名
 * @param {object} [options.formData]
 * @param {object} [options.header]
 */
function uploadFile(options) {
  const {
    url,
    filePath,
    name = 'file',
    formData = {},
    header = {},
    showErrorToast = true,
  } = options;

  return new Promise((resolve, reject) => {
    wx.uploadFile({
      url: `${baseUrl}${url}`,
      filePath,
      name,
      formData,
      header,
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          let body = res.data;
          try {
            body = JSON.parse(res.data);
          } catch (e) {
            /* 非 JSON 原样返回 */
          }
          resolve(body);
          return;
        }
        let msg = '上传失败';
        try {
          const j = JSON.parse(res.data);
          msg = j.message || j.msg || j.error || msg;
        } catch (e) {
          /* ignore */
        }
        if (showErrorToast) toast(msg);
        reject(res);
      },
      fail(err) {
        if (showErrorToast) toast(failHint(err && err.errMsg) || '上传失败');
        reject(err);
      },
    });
  });
}

function getProjects(params) {
  return request({
    url: `/api/projects${buildQuery(params)}`,
    method: 'GET',
  });
}

function getProjectDetail(id) {
  return request({
    url: `/api/projects/${encodeURIComponent(id)}`,
    method: 'GET',
  });
}

function updateHazardRemark(hazardId, remark) {
  return request({
    url: `/api/hazards/${encodeURIComponent(hazardId)}/remark`,
    method: 'PATCH',
    data: { remark },
  });
}

function uploadRectifyPhoto(hazardId, filePath) {
  return uploadFile({
    url: `/api/hazards/${encodeURIComponent(hazardId)}/rectify-photo`,
    filePath,
    name: 'file',
  });
}

function uploadScenePhoto(projectId, photoType, filePath) {
  return uploadFile({
    url: `/api/projects/${encodeURIComponent(projectId)}/scene-photo?photo_type=${encodeURIComponent(photoType)}`,
    filePath,
    name: 'file',
  });
}

/**
 * 隐患照片访问地址（完整 URL，供 image 组件 src 或下载使用）
 * 路径约定：GET /api/projects/{projectId}/hazards/{hazardId}/photo
 */
function getHazardPhotoUrl(projectId, hazardId) {
  return `${baseUrl}/api/projects/${encodeURIComponent(projectId)}/hazard-photo/${encodeURIComponent(hazardId)}`;
}

function getRectifyPhotoUrl(projectId, hazardId) {
  return `${baseUrl}/api/projects/${encodeURIComponent(projectId)}/rectify-photo/${encodeURIComponent(hazardId)}`;
}

/**
 * 下载远程图片到本地临时路径，解决真机 <image> 无法加载 HTTP 图片的问题
 */
function downloadImage(url) {
  return new Promise((resolve, reject) => {
    if (!url) { reject(new Error('空URL')); return; }
    wx.downloadFile({
      url,
      success(res) {
        if (res.statusCode === 200 && res.tempFilePath) {
          resolve(res.tempFilePath);
        } else {
          reject(new Error(`下载失败(${res.statusCode})`));
        }
      },
      fail: reject,
    });
  });
}

function updateRectifyStatus(hazardId, rectifyStatus) {
  return request({
    url: `/api/hazards/${encodeURIComponent(hazardId)}/rectify-status`,
    method: 'PATCH',
    data: { rectify_status: rectifyStatus },
  });
}

function createProject(data) {
  return request({
    url: '/api/projects',
    method: 'POST',
    data,
  });
}

function updateProject(projectId, data) {
  return request({
    url: `/api/projects/${encodeURIComponent(projectId)}`,
    method: 'PATCH',
    data,
  });
}

function getHazardTemplates(category) {
  const q = category ? `?category=${encodeURIComponent(category)}` : '';
  return request({ url: `/api/hazard-templates${q}`, method: 'GET' });
}

function getTemplateCategories() {
  return request({ url: '/api/hazard-template-categories', method: 'GET' });
}

function addHazard(projectId, data) {
  return request({
    url: `/api/projects/${encodeURIComponent(projectId)}/hazards`,
    method: 'POST',
    data,
  });
}

function updateHazard(hazardId, data) {
  return request({
    url: `/api/hazards/${encodeURIComponent(hazardId)}`,
    method: 'PATCH',
    data,
  });
}

function deleteHazard(hazardId) {
  return request({
    url: `/api/hazards/${encodeURIComponent(hazardId)}`,
    method: 'DELETE',
  });
}

function uploadHazardPhoto(hazardId, filePath) {
  return uploadFile({
    url: `/api/hazards/${encodeURIComponent(hazardId)}/photo`,
    filePath,
    name: 'file',
  });
}

function getDetections(projectId, detectionType) {
  const q = detectionType ? `?detection_type=${encodeURIComponent(detectionType)}` : '';
  return request({ url: `/api/projects/${encodeURIComponent(projectId)}/detections${q}` });
}

function addDetection(projectId, data) {
  return request({
    url: `/api/projects/${encodeURIComponent(projectId)}/detections`,
    method: 'POST', data,
  });
}

function updateDetection(recordId, data) {
  return request({
    url: `/api/detections/${encodeURIComponent(recordId)}`,
    method: 'PATCH', data,
  });
}

function deleteDetection(recordId) {
  return request({
    url: `/api/detections/${encodeURIComponent(recordId)}`,
    method: 'DELETE',
  });
}

function uploadDetectionPhoto(recordId, filePath) {
  return uploadFile({
    url: `/api/detections/${encodeURIComponent(recordId)}/photo`,
    filePath, name: 'file',
  });
}

function getDetectionPhotoUrl(recordId) {
  return `${baseUrl}/api/detections/${encodeURIComponent(recordId)}/photo`;
}

function getChecklist(projectId, tableIndex) {
  const q = tableIndex != null ? `?table_index=${encodeURIComponent(tableIndex)}` : '';
  return request({ url: `/api/projects/${encodeURIComponent(projectId)}/checklist${q}` });
}

function updateChecklist(projectId, items) {
  return request({
    url: `/api/projects/${encodeURIComponent(projectId)}/checklist`,
    method: 'PATCH', data: { items },
  });
}

function initChecklist(projectId) {
  return request({
    url: `/api/projects/${encodeURIComponent(projectId)}/init-checklist`,
    method: 'POST',
  });
}

function getInspectors(street) {
  const q = street ? `?street=${encodeURIComponent(street)}` : '';
  return request({ url: `/api/inspectors${q}`, method: 'GET' });
}

function addInspector(name, street) {
  return request({
    url: '/api/inspectors',
    method: 'POST',
    data: { name, street },
  });
}

module.exports = {
  setBaseUrl,
  getBaseUrl,
  request,
  uploadFile,
  getProjects,
  getProjectDetail,
  createProject,
  updateHazardRemark,
  updateRectifyStatus,
  updateProject,
  uploadRectifyPhoto,
  uploadScenePhoto,
  getHazardPhotoUrl,
  getRectifyPhotoUrl,
  downloadImage,
  getHazardTemplates,
  getTemplateCategories,
  addHazard,
  updateHazard,
  deleteHazard,
  uploadHazardPhoto,
  getDetections,
  addDetection,
  updateDetection,
  deleteDetection,
  uploadDetectionPhoto,
  getDetectionPhotoUrl,
  getChecklist,
  updateChecklist,
  initChecklist,
  getInspectors,
  addInspector,
};
