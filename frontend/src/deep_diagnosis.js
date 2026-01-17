/**
 * 深度诊断脚本 - 找出用户信息为什么没有保存到 Pinia
 */

console.clear();
console.log("🔍 深度诊断 - 检查 Pinia store 结构\n");

// 1. 检查 Pinia 对象本身
console.log("【步骤1】检查 Pinia 对象:");
console.log("window.__PINIA__ 存在?", !!window.__PINIA__);

if (window.__PINIA__) {
  console.log("__PINIA__.state 存在?", !!window.__PINIA__.state);
  
  if (window.__PINIA__.state) {
    console.log("__PINIA__.state.value 存在?", !!window.__PINIA__.state.value);
    
    if (window.__PINIA__.state.value) {
      console.log("store 名称列表:", Object.keys(window.__PINIA__.state.value));
      
      // 尝试访问不同的 store
      const stateValue = window.__PINIA__.state.value;
      
      console.log("\n【步骤2】尝试不同的访问方式:");
      
      // 方式1: auth store
      if (stateValue.auth) {
        console.log("✅ stateValue.auth 存在");
        console.log("   auth 的键:", Object.keys(stateValue.auth));
        console.log("   auth.user:", stateValue.auth.user);
      } else {
        console.log("❌ stateValue.auth 不存在");
      }
      
      // 方式2: counter store (可能是 auth store 的名称)
      if (stateValue.counter) {
        console.log("✅ stateValue.counter 存在");
        console.log("   counter 的键:", Object.keys(stateValue.counter));
        console.log("   counter.user:", stateValue.counter.user);
      } else {
        console.log("❌ stateValue.counter 不存在");
      }
      
      // 方式3: 遍历所有 store
      console.log("\n【步骤3】所有 store 内容:");
      for (const [storeName, storeData] of Object.entries(stateValue)) {
        console.log(`\n${storeName}:`, storeData);
      }
    }
  }
} else {
  console.log("❌ __PINIA__ 不存在！");
}

// 4. 检查 localStorage
console.log("\n【步骤4】检查 localStorage:");
const token = localStorage.getItem('access_token');
console.log("access_token:", token ? `✅ 存在 (${token.length} chars)` : "❌ 不存在");

// 5. 尝试通过 API 直接获取用户
console.log("\n【步骤5】通过 API 直接获取用户信息:");
if (token) {
  fetch('/api/auth/profile/', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  .then(r => r.json())
  .then(data => {
    console.log("✅ API 返回的用户信息:");
    console.log("   username:", data.username);
    console.log("   is_finance_department:", data.is_finance_department);
    console.log("   完整对象:", JSON.stringify(data, null, 2));
  })
  .catch(e => console.log("❌ API 错误:", e.message));
}
