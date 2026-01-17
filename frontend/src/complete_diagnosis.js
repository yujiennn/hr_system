/**
 * 完整的前端诊断脚本
 * 在浏览器 F12 → Console 中运行
 */

console.clear();
console.log("🔍 完整的前端权限诊断\n");

// ===== 第1部分: 检查 localStorage 中的数据 =====
console.log("【步骤1】LocalStorage 检查:");
const token = localStorage.getItem('access_token');
console.log("  access_token:", token ? `✅ 存在 (长度:${token.length})` : "❌ 不存在");

// ===== 第2部分: 调用 API 获取用户信息 =====
console.log("\n【步骤2】调用 API 获取用户信息:");
if (token) {
  (async () => {
    try {
      console.log("  📤 请求中...");
      const response = await fetch('/api/auth/profile/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log(`  📥 响应状态: ${response.status}`);
      const data = await response.json();
      
      if (response.ok) {
        console.log("  ✅ 响应成功");
        console.log("    username:", data.username);
        console.log("    department_name:", data.department_name);
        console.log("    user_type:", data.user_type);
        console.log("    is_finance_department:", data.is_finance_department);
        
        if (data.is_finance_department === true) {
          console.log("    ✅ 后端返回了正确的 is_finance_department");
        } else {
          console.log("    ❌ is_finance_department 不是 true:", data.is_finance_department);
        }
      } else {
        console.log("  ❌ 响应失败:", data);
      }
    } catch (e) {
      console.log("  ❌ 错误:", e.message);
    }
    
    // ===== 第3部分: 检查 Pinia store =====
    console.log("\n【步骤3】Pinia Store 检查:");
    try {
      // 尝试访问 Pinia store
      if (window.__PINIA__?.state?.value?.auth) {
        const authState = window.__PINIA__.state.value.auth;
        const user = authState.user;
        
        if (user) {
          console.log("  ✅ 找到 Pinia auth store");
          console.log("    user.username:", user.username);
          console.log("    user.department:", user.department);
          console.log("    user.department_name:", user.department_name);
          console.log("    user.is_finance_department:", user.is_finance_department);
          
          if (user.is_finance_department === true) {
            console.log("    ✅ Pinia 中的用户有正确的 is_finance_department");
          } else {
            console.log("    ⚠️ Pinia 中的用户的 is_finance_department:", user.is_finance_department);
          }
        } else {
          console.log("  ❌ Pinia auth store 中没有用户信息");
        }
      } else {
        console.log("  ❌ 无法访问 Pinia store");
      }
    } catch (e) {
      console.log("  ❌ 错误:", e.message);
    }
    
    // ===== 第4部分: 测试权限计算 =====
    console.log("\n【步骤4】权限计算测试:");
    try {
      const user = window.__PINIA__?.state?.value?.auth?.user;
      if (user) {
        const isFinance = user.is_finance_department === true;
        const isAdmin = user.user_type === 'admin';
        
        console.log("  user.is_finance_department:", user.is_finance_department);
        console.log("  isFinance (=== true):", isFinance);
        console.log("  isAdmin:", isAdmin);
        console.log("  canCreate (isFinance || isAdmin):", isFinance || isAdmin);
        
        if ((isFinance || isAdmin) === true) {
          console.log("  ✅ 应该显示 [创建薪资] 按钮");
        } else {
          console.log("  ❌ 不应该显示 [创建薪资] 按钮");
        }
      }
    } catch (e) {
      console.log("  ❌ 错误:", e.message);
    }
    
    // ===== 第5部分: 查看完整用户对象 =====
    console.log("\n【步骤5】完整用户对象:");
    try {
      const user = window.__PINIA__?.state?.value?.auth?.user;
      if (user) {
        console.log(JSON.stringify(user, null, 2));
      }
    } catch (e) {
      console.log("  ❌ 错误:", e.message);
    }
    
    console.log("\n🔍 诊断完成");
  })();
} else {
  console.log("  ❌ 没有 token，请先登录");
}
