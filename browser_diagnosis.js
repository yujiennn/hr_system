/**
 * 为了使用此脚本：
 * 1. 打开浏览器开发者工具（F12）
 * 2. 转到控制台（Console）
 * 3. 复制粘贴整个脚本
 * 4. 按 Enter 运行
 */

console.log('🔍 开始诊断 PerformanceView 的数据加载问题');

// 1. 获取 localStorage 中的令牌
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

console.log('📌 认证信息:');
console.log('  access_token:', accessToken ? accessToken.substring(0, 30) + '...' : '❌ 未找到');
console.log('  refresh_token:', refreshToken ? refreshToken.substring(0, 30) + '...' : '❌ 未找到');

// 2. 测试 API 端点
const testApis = [
  '/api/performance/evaluations/my_evaluations/',
  '/api/performance/goals/my_goals/',
  '/api/performance/evaluations/statistics/',
  '/api/performance/periods/',
  '/api/performance/templates/'
];

console.log('\n📌 API 端点测试:');

const apiTests = testApis.map(url => {
  return fetch(`http://127.0.0.1:8000${url}`, {
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(resp => {
    const status = resp.status;
    return resp.json().then(data => ({
      url,
      status,
      dataLength: typeof data === 'object' ? (data.results ? data.results.length : data.length) : 'N/A'
    }));
  })
  .catch(err => ({
    url,
    status: 'ERROR',
    error: err.message
  }));
});

Promise.all(apiTests).then(results => {
  results.forEach(result => {
    const icon = result.status === 200 ? '✅' : '❌';
    console.log(`  ${icon} ${result.url}`);
    console.log(`      状态: ${result.status}, 数据数: ${result.dataLength}`);
  });

  // 3. 检查 DOM
  console.log('\n📌 DOM 结构检查:');
  const perfView = document.querySelector('[class*="performance"]');
  console.log('  PerformanceView 组件:', perfView ? '✅ 找到' : '❌ 未找到');

  const tables = document.querySelectorAll('table');
  console.log(`  表格数量: ${tables.length}`);
  
  tables.forEach((table, i) => {
    const rows = table.querySelectorAll('tbody tr');
    console.log(`    表格 ${i + 1}: ${rows.length} 行数据`);
  });

  // 4. 检查空态提示
  const emptyElements = document.querySelectorAll('[class*="empty"]');
  console.log(`  空态元素: ${emptyElements.length}`);

  // 5. 检查加载状态
  const spinner = document.querySelector('[class*="spinner"], [class*="loading"]');
  console.log('  加载指示器:', spinner ? '✅ 显示中' : '❌ 未显示');

  console.log('\n✅ 诊断完成');
  console.log('💡 如果所有 API 都返回 200 但页面显示为空，问题可能是:');
  console.log('   1. Vue 数据绑定问题');
  console.log('   2. 组件未正确加载');
  console.log('   3. onActivated 钩子未触发');
  console.log('   4. 浏览器缓存问题');
});
