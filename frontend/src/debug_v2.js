/**
 * 完整的财务部权限调试脚本 v2
 * 在浏览器console中运行，检查从后端接收的数据
 */

console.log("=== 财务部权限完整诊断工具 v2 ===\n");

// ====== 第1部分: 检查已登录的用户数据 ======
console.log("【第1部分】已登录用户数据检查:\n");

// 方法1: 从 localStorage 中的 token 读取用户信息
const accessToken = localStorage.getItem('access_token');
console.log("1. Access Token 状态:");
if (accessToken) {
  console.log("   ✅ Token 存在，长度:", accessToken.length);
  // 尝试解析 JWT token (第二部分，不解密)
  try {
    const parts = accessToken.split('.');
    if (parts.length === 3) {
      const payload = JSON.parse(atob(parts[1]));
      console.log("   Token 内容 - user_id:", payload.user_id);
    }
  } catch(e) {
    console.log("   ⚠️ Token 解析失败");
  }
} else {
  console.log("   ❌ 未找到 Token - 需要重新登录");
}

// ====== 第2部分: 检查 Pinia Store 中的用户信息 ======
console.log("\n【第2部分】Pinia Store 用户信息检查:\n");

// 获取 Pinia 中的认证 store
let authStore = null;
let userInfo = null;

// 方式1: 通过 window.__PINIA__ 访问 (通常适用于 Vue 3)
if (window.__PINIA__ && window.__PINIA__.state && window.__PINIA__.state.value) {
  const state = window.__PINIA__.state.value;
  if (state.auth && state.auth.user) {
    authStore = state.auth;
    userInfo = state.auth.user;
    console.log("✅ 通过 window.__PINIA__ 找到用户信息");
  }
}

if (!userInfo) {
  // 方式2: 检查全局对象中的其他可能的 store 位置
  console.log("❌ 通过 window.__PINIA__ 未找到用户信息");
  console.log("尝试其他方式...");
}

if (userInfo) {
  console.log("\n2. 用户详细信息:");
  console.log("   用户名:", userInfo.username);
  console.log("   ID:", userInfo.id);
  console.log("   部门ID:", userInfo.department);
  console.log("   部门名称:", userInfo.department_name);
  console.log("   用户类型:", userInfo.user_type);
  console.log("   is_finance_department:", userInfo.is_finance_department);
  
  if (userInfo.is_finance_department === true) {
    console.log("\n   ✅ is_finance_department = true (财务部员工)");
  } else if (userInfo.is_finance_department === false) {
    console.log("\n   ❌ is_finance_department = false (非财务部员工)");
  } else {
    console.log("\n   ❌ is_finance_department = undefined (字段不存在!)");
    console.log("   问题: 后端没有返回这个字段!");
  }
  
  // 显示所有用户字段，以便排查问题
  console.log("\n3. 用户对象的所有字段:");
  const keys = Object.keys(userInfo);
  keys.forEach(key => {
    const value = userInfo[key];
    if (typeof value === 'object') {
      console.log(`   ${key}: [Object]`);
    } else {
      console.log(`   ${key}: ${value}`);
    }
  });
} else {
  console.log("\n❌ 未找到 Pinia store 中的用户信息");
  console.log("   可能原因:");
  console.log("   1. 页面未完全加载");
  console.log("   2. 未登录");
  console.log("   3. Store 结构不同");
}

// ====== 第3部分: 进行网络请求以验证后端响应 ======
console.log("\n【第3部分】后端 API 响应检查:\n");

if (accessToken) {
  console.log("4. 调用 /api/auth/profile/ 验证后端响应...");
  
  fetch('/api/auth/profile/', {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${accessToken}`,
      'Content-Type': 'application/json'
    }
  })
  .then(response => {
    console.log(`   响应状态: ${response.status}`);
    if (response.status === 401) {
      console.log("   ❌ Token 过期或无效，需要重新登录");
    }
    return response.json();
  })
  .then(data => {
    console.log("   ✅ 响应数据:");
    console.log("   {");
    const keys = Object.keys(data);
    keys.forEach(key => {
      const value = data[key];
      if (typeof value === 'string' && value.length > 50) {
        console.log(`     "${key}": "${value.substring(0, 50)}..."`);
      } else if (typeof value === 'object') {
        console.log(`     "${key}": [Object]`);
      } else {
        console.log(`     "${key}": ${JSON.stringify(value)}`);
      }
    });
    console.log("   }");
    
    // 特别检查 is_finance_department 字段
    if ('is_finance_department' in data) {
      console.log(`\n   ✅ 后端返回了 is_finance_department: ${data.is_finance_department}`);
    } else {
      console.log("\n   ❌ 后端未返回 is_finance_department 字段!");
      console.log("   问题: UserSerializer 或 ProfileSerializer 可能未正确修改");
    }
  })
  .catch(error => {
    console.log("   ❌ 网络请求错误:", error.message);
  });
} else {
  console.log("❌ 无有效的 Token，无法进行 API 请求");
}

// ====== 第4部分: 权限计算检查 ======
console.log("\n【第4部分】权限计算检查:\n");

if (userInfo) {
  const isFinanceDept = userInfo.is_finance_department === true;
  const isAdmin = userInfo.user_type === 'admin';
  const isManager = userInfo.user_type === 'manager';
  
  console.log("5. 权限判断结果:");
  console.log(`   是财务部员工: ${isFinanceDept ? '✅ 是' : '❌ 否'}`);
  console.log(`   是管理员: ${isAdmin ? '✅ 是' : '❌ 否'}`);
  console.log(`   是部门经理: ${isManager ? '✅ 是' : '❌ 否'}`);
  
  console.log("\n   权限计算结果:");
  console.log(`   canCreate (财务部 OR 管理员): ${isFinanceDept || isAdmin ? '✅ 可以' : '❌ 不可以'}`);
  console.log(`   canApprove (财务部 OR 管理员): ${isFinanceDept || isAdmin ? '✅ 可以' : '❌ 不可以'}`);
  console.log(`   canPay (财务部 OR 管理员): ${isFinanceDept || isAdmin ? '✅ 可以' : '❌ 不可以'}`);
  console.log(`   canReview (经理 OR 管理员): ${isManager || isAdmin ? '✅ 可以' : '❌ 不可以'}`);
}

// ====== 第5部分: 故障排查建议 ======
console.log("\n【第5部分】故障排查建议:\n");

if (!userInfo || userInfo.is_finance_department === undefined) {
  console.log("⚠️ 检测到问题! 请按顺序尝试以下方案:\n");
  
  console.log("方案 A: 清除浏览器缓存");
  console.log("  1. F12 → Application 标签");
  console.log("  2. 点击 'Clear site data'");
  console.log("  3. Ctrl+Shift+R 硬刷新");
  
  console.log("\n方案 B: 重启后端服务");
  console.log("  1. 停止 Django 服务 (Ctrl+C)");
  console.log("  2. 运行: python manage.py runserver");
  
  console.log("\n方案 C: 验证序列化器修改");
  console.log("  1. 检查 users/serializers.py");
  console.log("  2. UserSerializer 应包含:");
  console.log("     - is_finance_department = serializers.SerializerMethodField()");
  console.log("     - 'is_finance_department' 在 fields 列表中");
  console.log("     - get_is_finance_department() 方法");
  
  console.log("\n方案 D: 重新登录");
  console.log("  1. 登出当前账号");
  console.log("  2. 清除 localStorage: localStorage.clear()");
  console.log("  3. 重新登录 '财务1' 账号");
}

console.log("\n=== 诊断完成 ===");
console.log("\n💡 TIP: 刷新页面后，重新在 console 中运行此脚本以获取最新数据");
