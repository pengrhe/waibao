const ci = require('miniprogram-ci');
const path = require('path');

(async () => {
  const project = new ci.Project({
    appid: 'wx3134faada697e694',
    type: 'miniProgram',
    projectPath: path.resolve(__dirname, 'miniapp'),
    privateKeyPath: path.resolve(__dirname, 'private.wx3134faada697e694.key'),
    ignores: ['node_modules/**/*'],
  });

  try {
    const uploadResult = await ci.upload({
      project,
      version: '2.3.0',
      desc: '新增旅业项目(C包)支持',
      setting: {
        es6: true,
        es7: true,
        minify: true,
        autoPrefixWXSS: true,
        minifyWXML: true,
      },
      robot: 1,
    });
    console.log('上传成功！', uploadResult);
  } catch (err) {
    console.error('上传失败：', err);
    process.exit(1);
  }
})();
