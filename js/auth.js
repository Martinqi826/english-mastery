/**
 * English Mastery - 用户认证模块
 */

// ==================== 常量定义 ====================
const AUTH_STORAGE_KEY = 'em_users';
const CURRENT_USER_KEY = 'em_current_user';
const REMEMBER_KEY = 'em_remember';

// ==================== 用户数据管理 ====================

/**
 * 获取所有注册用户
 * @returns {Array} 用户列表
 */
function getUsers() {
  const users = localStorage.getItem(AUTH_STORAGE_KEY);
  return users ? JSON.parse(users) : [];
}

/**
 * 保存用户列表
 * @param {Array} users - 用户列表
 */
function saveUsers(users) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(users));
}

/**
 * 根据邮箱查找用户
 * @param {string} email - 邮箱地址
 * @returns {Object|null} 用户对象或null
 */
function findUserByEmail(email) {
  const users = getUsers();
  return users.find(user => user.email.toLowerCase() === email.toLowerCase());
}

/**
 * 获取当前登录用户
 * @returns {Object|null} 当前用户或null
 */
function getCurrentUser() {
  const user = localStorage.getItem(CURRENT_USER_KEY);
  return user ? JSON.parse(user) : null;
}

/**
 * 设置当前登录用户
 * @param {Object} user - 用户对象
 */
function setCurrentUser(user) {
  // 不保存密码到当前用户状态
  const safeUser = {
    id: user.id,
    name: user.name,
    email: user.email,
    createdAt: user.createdAt,
    lastLogin: new Date().toISOString()
  };
  localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(safeUser));
}

/**
 * 清除当前登录用户
 */
function clearCurrentUser() {
  localStorage.removeItem(CURRENT_USER_KEY);
  localStorage.removeItem(REMEMBER_KEY);
}

/**
 * 检查用户是否已登录
 * @returns {boolean}
 */
function isLoggedIn() {
  return getCurrentUser() !== null;
}

// ==================== 密码处理 ====================

/**
 * 简单的密码哈希（实际生产环境应使用bcrypt等）
 * @param {string} password - 原始密码
 * @returns {string} 哈希后的密码
 */
function hashPassword(password) {
  // 简单的哈希实现，实际生产环境应该使用更安全的方法
  let hash = 0;
  for (let i = 0; i < password.length; i++) {
    const char = password.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash;
  }
  return 'hash_' + Math.abs(hash).toString(36) + '_' + password.length;
}

/**
 * 验证密码
 * @param {string} password - 输入的密码
 * @param {string} hashedPassword - 存储的哈希密码
 * @returns {boolean}
 */
function verifyPassword(password, hashedPassword) {
  return hashPassword(password) === hashedPassword;
}

// ==================== 表单验证 ====================

/**
 * 验证邮箱格式
 * @param {string} email - 邮箱地址
 * @returns {boolean}
 */
function isValidEmail(email) {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证密码强度
 * @param {string} password - 密码
 * @returns {Object} {valid: boolean, strength: string, message: string}
 */
function validatePassword(password) {
  if (password.length < 6) {
    return { valid: false, strength: 'weak', message: '密码至少需要6位' };
  }
  
  let strength = 0;
  
  // 长度检查
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  
  // 包含数字
  if (/\d/.test(password)) strength++;
  
  // 包含小写字母
  if (/[a-z]/.test(password)) strength++;
  
  // 包含大写字母
  if (/[A-Z]/.test(password)) strength++;
  
  // 包含特殊字符
  if (/[!@#$%^&*(),.?":{}|<>]/.test(password)) strength++;
  
  if (strength <= 2) {
    return { valid: true, strength: 'weak', message: '密码强度：弱' };
  } else if (strength <= 4) {
    return { valid: true, strength: 'medium', message: '密码强度：中等' };
  } else {
    return { valid: true, strength: 'strong', message: '密码强度：强' };
  }
}

// ==================== UI 交互函数 ====================

/**
 * 切换登录/注册表单
 * @param {string} tab - 'login' 或 'register'
 */
function switchTab(tab) {
  // 更新标签状态
  document.querySelectorAll('.auth-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  
  // 切换表单显示
  const loginForm = document.getElementById('loginForm');
  const registerForm = document.getElementById('registerForm');
  
  if (tab === 'login') {
    loginForm.classList.remove('hidden');
    registerForm.classList.add('hidden');
  } else {
    loginForm.classList.add('hidden');
    registerForm.classList.remove('hidden');
  }
}

/**
 * 切换密码显示/隐藏
 * @param {string} inputId - 输入框ID
 * @param {HTMLElement} button - 切换按钮
 */
function togglePassword(inputId, button) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    button.textContent = '🙈';
  } else {
    input.type = 'password';
    button.textContent = '👁️';
  }
}

/**
 * 检查密码强度并更新UI
 * @param {string} password - 密码
 */
function checkPasswordStrength(password) {
  const result = validatePassword(password);
  const strengthFill = document.getElementById('strengthFill');
  const strengthText = document.getElementById('strengthText');
  
  if (strengthFill && strengthText) {
    // 移除所有强度类
    strengthFill.classList.remove('weak', 'medium', 'strong');
    strengthText.classList.remove('weak', 'medium', 'strong');
    
    if (password.length > 0) {
      strengthFill.classList.add(result.strength);
      strengthText.classList.add(result.strength);
      strengthText.textContent = result.message;
    } else {
      strengthText.textContent = '密码强度';
    }
  }
}

/**
 * 显示 Toast 提示
 * @param {string} message - 消息内容
 * @param {string} type - 类型 (success/error/info)
 */
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  if (!toast) return;
  
  toast.textContent = message;
  toast.className = `toast ${type} show`;
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// ==================== 认证操作 ====================

/**
 * 处理注册
 * @param {Event} event - 表单提交事件
 */
function handleRegister(event) {
  event.preventDefault();
  
  const name = document.getElementById('registerName').value.trim();
  const email = document.getElementById('registerEmail').value.trim();
  const password = document.getElementById('registerPassword').value;
  const confirmPassword = document.getElementById('confirmPassword').value;
  const agreeTerms = document.getElementById('agreeTerms').checked;
  
  // 验证
  if (!name || name.length < 2) {
    showToast('请输入至少2个字符的昵称', 'error');
    return;
  }
  
  if (!isValidEmail(email)) {
    showToast('请输入有效的邮箱地址', 'error');
    return;
  }
  
  if (password.length < 6) {
    showToast('密码至少需要6位', 'error');
    return;
  }
  
  if (password !== confirmPassword) {
    showToast('两次输入的密码不一致', 'error');
    return;
  }
  
  if (!agreeTerms) {
    showToast('请同意服务条款和隐私政策', 'error');
    return;
  }
  
  // 检查邮箱是否已注册
  if (findUserByEmail(email)) {
    showToast('该邮箱已被注册', 'error');
    return;
  }
  
  // 创建新用户
  const newUser = {
    id: 'user_' + Date.now().toString(36),
    name: name,
    email: email,
    password: hashPassword(password),
    createdAt: new Date().toISOString()
  };
  
  // 保存用户
  const users = getUsers();
  users.push(newUser);
  saveUsers(users);
  
  // 自动登录
  setCurrentUser(newUser);
  
  showToast('🎉 注册成功！正在跳转...', 'success');
  
  // 跳转到首页
  setTimeout(() => {
    window.location.href = '../index.html';
  }, 1500);
}

/**
 * 处理登录
 * @param {Event} event - 表单提交事件
 */
function handleLogin(event) {
  event.preventDefault();
  
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const rememberMe = document.getElementById('rememberMe').checked;
  
  // 验证
  if (!isValidEmail(email)) {
    showToast('请输入有效的邮箱地址', 'error');
    return;
  }
  
  if (!password) {
    showToast('请输入密码', 'error');
    return;
  }
  
  // 查找用户
  const user = findUserByEmail(email);
  
  if (!user) {
    showToast('该邮箱未注册', 'error');
    return;
  }
  
  // 验证密码
  if (!verifyPassword(password, user.password)) {
    showToast('密码错误', 'error');
    return;
  }
  
  // 登录成功
  setCurrentUser(user);
  
  if (rememberMe) {
    localStorage.setItem(REMEMBER_KEY, 'true');
  }
  
  showToast('✅ 登录成功！正在跳转...', 'success');
  
  // 跳转到首页
  setTimeout(() => {
    window.location.href = '../index.html';
  }, 1500);
}

/**
 * 退出登录
 */
function logout() {
  clearCurrentUser();
  window.location.href = 'pages/auth.html';
}

// ==================== 页面保护 ====================

/**
 * 检查登录状态，未登录则跳转到登录页
 * 在需要保护的页面调用此函数
 */
function requireAuth() {
  if (!isLoggedIn()) {
    window.location.href = window.location.pathname.includes('/pages/') 
      ? 'auth.html' 
      : 'pages/auth.html';
  }
}

/**
 * 如果已登录，则跳转到首页
 * 在登录页调用此函数
 */
function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.href = window.location.pathname.includes('/pages/') 
      ? '../index.html' 
      : 'index.html';
  }
}

// ==================== 初始化 ====================

// 页面加载时检查是否需要重定向
document.addEventListener('DOMContentLoaded', function() {
  // 如果在登录页且已登录，跳转到首页
  if (window.location.pathname.includes('auth.html')) {
    redirectIfLoggedIn();
  }
});

// ==================== 导出接口 ====================
window.Auth = {
  isLoggedIn,
  getCurrentUser,
  logout,
  requireAuth
};
