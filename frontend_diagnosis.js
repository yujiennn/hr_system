/**
 * 前端 PerformanceView 诊断脚本
 * 在浏览器控制台中运行此代码来诊断问题
 */

// 1. 检查是否有令牌
console.log('='.repeat(80));
console.log('1️⃣  检查认证状态');
console.log('='.repeat(80));

const token = localStorage.getItem('access_token');
if (token) {
  console.log('✅ 找到 access_token:', token.substring(0, 30) + '...');
} else {
  console.log('❌ 没有找到 access_token，可能未登录');
}

// 2. 测试 API 调用
console.log('\n' + '='.repeat(80));
console.log('2️⃣  测试 /api/performance/evaluations/my_evaluations/');
console.log('='.repeat(80));

const headers = {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
};

fetch('http://127.0.0.1:8000/api/performance/evaluations/my_evaluations/', {
  method: 'GET',
  headers: headers
})
.then(response => {
  console.log('✅ API 响应状态:', response.status, response.statusText);
  return response.json();
})
.then(data => {
  console.log('✅ API 返回数据:', data);
  if (Array.isArray(data)) {
    console.log(`   返回 ${data.length} 条评估`);
    data.forEach(item => {
      console.log(`   - ID: ${item.id}, 状态: ${item.status}`);
    });
  } else if (data.results) {
    console.log(`   返回 ${data.results.length} 条评估`);
  }
})
.catch(error => {
  console.log('❌ API 请求失败:', error);
});

// 3. 检查 Vue 组件状态（如果页面已加载）
console.log('\n' + '='.repeat(80));
console.log('3️⃣  等待 3 秒后检查 Vue 组件状态...');
console.log('='.repeat(80));

setTimeout(() => {
  // 尝试通过 Vue DevTools 或直接访问组件
  const app = window.__VUE_DEVTOOLS_GLOBAL_HOOK__.apps[0];
  if (app) {
    console.log('✅ 找到 Vue 应用实例');
    // 注意：实际访问会取决于应用的结构
    console.log('💡 建议在浏览器 Vue DevTools 中检查 PerformanceView 组件的状态');
  } else {
    console.log('⚠️  未找到 Vue 应用实例');
  }

  // 检查 DOM 中的数据
  const tables = document.querySelectorAll('table');
  console.log(`\n📋 页面中找到 ${tables.length} 个表格`);
  
  tables.forEach((table, index) => {
    const rows = table.querySelectorAll('tbody tr');
    console.log(`   表格 ${index + 1}: ${rows.length} 行数据`);
  });

  // 检查是否有 el-empty (空态组件)
  const emptyComps = document.querySelectorAll('[class*="empty"]');
  console.log(`\n📭 页面中的空态元素: ${emptyComps.length} 个`);
}, 3000);

console.log('\n' + '='.repeat(80));
console.log('💡 诊断进行中，请等待 3 秒后查看结果...');
console.log('='.repeat(80));
