// API base，按平台区分。开发：H5 走 vite proxy 用相对路径，小程序走真域名。
// process.env.UNI_PLATFORM 在编译期注入。
export const API_BASE = (() => {
  // h5 dev 走 vite proxy
  // #ifdef H5
  return '/api/v1'
  // #endif
  // #ifndef H5
  return 'http://127.0.0.1:8200/api/v1'
  // #endif
})()

export const PLATFORM = (() => {
  // #ifdef MP-WEIXIN
  return 'mp-weixin'
  // #endif
  // #ifdef MP-TOUTIAO
  return 'mp-toutiao'
  // #endif
  // #ifdef H5
  return 'h5'
  // #endif
  return 'unknown'
})()
