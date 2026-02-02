/**
 * 快速修复脚本 - 在浏览器控制台中运行
 * 
 * 说明：
 * 1. 按 F12 打开浏览器开发者工具
 * 2. 转到 Console 标签
 * 3. 复制下面的代码到控制台
 * 4. 按 Enter 运行
 */

console.log('🔧 开始执行快速修复...\n');

// 1. 清除所有缓存存储
console.log('1️⃣  清除缓存存储...');
localStorage.clear();
sessionStorage.clear();
console.log('✅ localStorage 和 sessionStorage 已清除\n');

// 2. 清除 Service Worker 缓存（如果有）
if ('caches' in window) {
  console.log('2️⃣  清除 Service Worker 缓存...');
  caches.keys().then(cacheNames => {
    cacheNames.forEach(cacheName => {
      caches.delete(cacheName);
    });
    console.log('✅ Service Worker 缓存已清除\n');
  });
}

// 3. 重新加载页面
console.log('3️⃣  3 秒后重新加载页面...');
setTimeout(() => {
  window.location.reload();
}, 3000);

console.log('💡 请等待 3 秒...\n');
console.log('🎉 修复完成！页面将自动刷新。');
