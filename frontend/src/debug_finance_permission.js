/**
 * 财务部权限调试脚本
 * 在浏览器控制台中运行此脚本，检查权限是否正确配置
 * 
 * 使用方法:
 * 1. F12 打开开发者工具
 * 2. 进入 Console 标签
 * 3. 复制粘贴以下内容运行
 */

console.log("=== 财务部权限调试工具 ===\n");

// 1. 检查 localStorage 中的 token
console.log("1. Token 检查:");
const accessToken = localStorage.getItem('access_token');
const refreshToken = localStorage.getItem('refresh_token');

if (accessToken) {
  console.log("✅ access_token 存在");
  console.log("   长度:", accessToken.length);
} else {
  console.log("❌ access_token 不存在 - 需要重新登录");
}

if (refreshToken) {
  console.log("✅ refresh_token 存在");
} else {
  console.log("❌ refresh_token 不存在");
}

// 2. 检查 Pinia store 中的用户信息
console.log("\n2. 用户信息检查 (来自 authStore):");
if (window.__PINIA__) {
  // Pinia 已初始化
  const stores = window.__PINIA__.state.value;
  if (stores && stores.auth) {
    const authState = stores.auth;
    const user = authState.user;
    
    if (user) {
      console.log("✅ 找到用户信息:");
      console.log("   用户名:", user.username);
      console.log("   部门:", user.department_name);
      console.log("   角色:", user.user_type);
      console.log("   is_finance_department:", user.is_finance_department);
      
      if (user.is_finance_department === true) {
        console.log("✅ 用户是财务部员工 - 应该能看到财务管理功能");
      } else if (user.is_finance_department === false) {
        console.log("⚠️ 用户不是财务部员工 - 不应该看到创建/审批/发放功能");
      } else {
        console.log("❌ is_finance_department 未定义 - 序列化器可能未包含此字段");
      }
    } else {
      console.log("❌ 未找到用户信息 - 请先登录");
    }
  } else {
    console.log("❌ Pinia auth store 不存在");
  }
} else {
  console.log("⚠️ Pinia 尚未初始化 - 请等待页面完全加载");
}

// 3. 检查权限计算属性
console.log("\n3. 权限计算检查:");
if (window.__PINIA__) {
  const stores = window.__PINIA__.state.value;
  if (stores && stores.auth) {
    const authState = stores.auth;
    const user = authState.user;
    
    if (user) {
      const isFinanceDept = user.is_finance_department === true;
      const isAdmin = user.user_type === 'admin';
      const isManager = user.user_type === 'manager';
      
      console.log("   canCreate (财务部 OR 管理员):", isFinanceDept || isAdmin);
      console.log("   canApprove (财务部 OR 管理员):", isFinanceDept || isAdmin);
      console.log("   canPay (财务部 OR 管理员):", isFinanceDept || isAdmin);
      console.log("   canReview (经理 OR 管理员):", isManager || isAdmin);
    }
  }
}

// 4. 网络请求检查建议
console.log("\n4. 网络请求检查:");
console.log("   请查看 Network 标签中的请求:");
console.log("   - /api/auth/login/ 的响应应包含 'is_finance_department' 字段");
console.log("   - /api/auth/profile/ 的响应应包含 'is_finance_department' 字段");

// 5. 刷新建议
console.log("\n5. 如果按钮仍未显示:");
console.log("   1. 执行以下命令硬刷新:");
console.log('      location.reload(true)');
console.log("   2. 或按 Ctrl+Shift+R (Windows) 或 Cmd+Shift+R (Mac)");

console.log("\n=== 调试完成 ===");
