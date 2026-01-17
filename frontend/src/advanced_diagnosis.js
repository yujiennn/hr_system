/**
 * 高级诊断脚本 - 找出 Pinia 的真实结构
 */

console.clear();
console.log("🔍 高级诊断 - 找出 Pinia 真实结构\n");

// 1. 检查所有可能的全局对象
console.log("【步骤1】检查所有可能的全局认证对象:");

const potentialStoreNames = ['__PINIA__', '__PINIA_ROOT__', '__stores__', '__auth__'];
for (const name of potentialStoreNames) {
  if (window[name]) {
    console.log(`✅ 找到 window.${name}`);
  }
}

// 2. 深入检查 __PINIA__ 结构
if (window.__PINIA__) {
  console.log("\n【步骤2】__PINIA__ 结构详解:");
  console.log("- __PINIA__:", window.__PINIA__);
  console.log("- __PINIA__.state:", window.__PINIA__.state);
  
  if (window.__PINIA__.state?.value) {
    console.log("- __PINIA__.state.value 的所有 key:", Object.keys(window.__PINIA__.state.value));
    
    // 3. 列出所有 store
    console.log("\n【步骤3】所有 store 内容:");
    const stateValue = window.__PINIA__.state.value;
    
    for (const [storeName, storeData] of Object.entries(stateValue)) {
      console.log(`\n--- Store: "${storeName}" ---`);
      if (typeof storeData === 'object' && storeData) {
        console.log("  Keys:", Object.keys(storeData).slice(0, 10)); // 显示前10个
        
        // 特别检查是否有 user 或 isAuthenticated
        if ('user' in storeData) {
          console.log(`  ✅ 有 "user" 字段:`, storeData.user);
        }
        if ('isAuthenticated' in storeData) {
          console.log(`  ✅ 有 "isAuthenticated" 字段:`, storeData.isAuthenticated);
        }
      }
    }
  }
} else {
  console.log("\n❌ 无法访问 window.__PINIA__");
}

// 4. 检查 localStorage
console.log("\n【步骤4】localStorage 检查:");
const token = localStorage.getItem('access_token');
console.log("- access_token:", token ? `✅ 存在 (${token.substring(0, 20)}...)` : "❌ 不存在");

// 5. 直接调用 API
console.log("\n【步骤5】直接调用 API:");
if (token) {
  (async () => {
    try {
      const response = await fetch('/api/auth/profile/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      const data = await response.json();
      console.log("✅ API 返回的用户数据:");
      console.log("  - username:", data.username);
      console.log("  - user_type:", data.user_type);
      console.log("  - is_finance_department:", data.is_finance_department);
      console.log("  - 完整数据:", JSON.stringify(data, null, 2));
    } catch (e) {
      console.log("❌ API 错误:", e.message);
    }
  })();
}

console.log("\n=== 诊断完成 ===");
console.log("请把上面的输出全部复制给开发者");
