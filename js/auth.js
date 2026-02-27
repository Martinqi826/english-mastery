/**
 * English Mastery - 用户认证模块
 * 改造版本：使用后端 API 进行认证
 */

// ==================== 常量定义 ====================
const CURRENT_USER_KEY = 'em_current_user';
const REMEMBER_KEY = 'em_remember';

// ==================== 用户数据管理 ====================

/**
 * 获取当前登录用户（从本地缓存）
 * @returns {Object|null} 当前用户或null
 */
function getCurrentUser() {
  const user = localStorage.getItem(CURRENT_USER_KEY);
  return user ? JSON.parse(user) : null;
}

/**
 * 设置当前登录用户（缓存到本地）
 * @param {Object} user - 用户对象
 */
function setCurrentUser(user) {
  const safeUser = {
    id: user.id,
    name: user.name,
    email: user.email,
    phone: user.phone,
    avatar: user.avatar,
    membership_level: user.membership_level || 'free',
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
  // 同时清除 API Token
  if (window.API) {
    API.clearTokens();
  }
}

/**
 * 检查用户是否已登录
 * @returns {boolean}
 */
function isLoggedIn() {
  // 优先检查 API Token
  if (window.API && API.isLoggedIn()) {
    return true;
  }
  // 兼容旧版本：检查本地用户数据
  return getCurrentUser() !== null;
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
 * 验证手机号格式
 * @param {string} phone - 手机号
 * @returns {boolean}
 */
function isValidPhone(phone) {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
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
  
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/\d/.test(password)) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
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
  document.querySelectorAll('.auth-tab').forEach(t => {
    t.classList.toggle('active', t.dataset.tab === tab);
  });
  
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

/**
 * 显示/隐藏加载状态
 * @param {boolean} show - 是否显示
 */
function showLoading(show) {
  const buttons = document.querySelectorAll('button[type="submit"]');
  buttons.forEach(btn => {
    btn.disabled = show;
    if (show) {
      btn.dataset.originalText = btn.textContent;
      btn.textContent = '处理中...';
    } else if (btn.dataset.originalText) {
      btn.textContent = btn.dataset.originalText;
    }
  });
}

// ==================== 认证操作 ====================

/**
 * 处理注册
 * @param {Event} event - 表单提交事件
 */
async function handleRegister(event) {
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
  
  showLoading(true);
  
  try {
    // 调用后端 API 注册
    if (window.API) {
      const result = await API.auth.register({
        name,
        email,
        password
      });
      
      // 保存用户信息到本地缓存
      setCurrentUser(result.user);
      
      showToast('🎉 注册成功！正在跳转...', 'success');
      
      setTimeout(() => {
        window.location.href = '../index.html';
      }, 1500);
    } else {
      // 降级到本地存储（兼容模式）
      handleRegisterLocal(name, email, password);
    }
  } catch (error) {
    console.error('Register failed:', error);
    showToast(error.message || '注册失败，请稍后重试', 'error');
  } finally {
    showLoading(false);
  }
}

/**
 * 本地注册（兼容模式，当后端不可用时）
 */
function handleRegisterLocal(name, email, password) {
  const AUTH_STORAGE_KEY = 'em_users';
  const users = JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY) || '[]');
  
  if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) {
    showToast('该邮箱已被注册', 'error');
    return;
  }
  
  const newUser = {
    id: 'user_' + Date.now().toString(36),
    name,
    email,
    password: 'local_' + btoa(password),
    createdAt: new Date().toISOString()
  };
  
  users.push(newUser);
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(users));
  
  setCurrentUser(newUser);
  showToast('🎉 注册成功！正在跳转...', 'success');
  
  setTimeout(() => {
    window.location.href = '../index.html';
  }, 1500);
}

/**
 * 处理登录
 * @param {Event} event - 表单提交事件
 */
async function handleLogin(event) {
  event.preventDefault();
  
  const email = document.getElementById('loginEmail').value.trim();
  const password = document.getElementById('loginPassword').value;
  const rememberMe = document.getElementById('rememberMe')?.checked;
  
  // 验证
  if (!isValidEmail(email)) {
    showToast('请输入有效的邮箱地址', 'error');
    return;
  }
  
  if (!password) {
    showToast('请输入密码', 'error');
    return;
  }
  
  showLoading(true);
  
  try {
    // 调用后端 API 登录
    if (window.API) {
      const result = await API.auth.login(email, password);
      
      // 保存用户信息到本地缓存
      setCurrentUser(result.user);
      
      if (rememberMe) {
        localStorage.setItem(REMEMBER_KEY, 'true');
      }
      
      showToast('✅ 登录成功！正在跳转...', 'success');
      
      setTimeout(() => {
        window.location.href = '../index.html';
      }, 1500);
    } else {
      // 降级到本地存储（兼容模式）
      handleLoginLocal(email, password, rememberMe);
    }
  } catch (error) {
    console.error('Login failed:', error);
    showToast(error.message || '登录失败，请检查邮箱和密码', 'error');
  } finally {
    showLoading(false);
  }
}

/**
 * 本地登录（兼容模式）
 */
function handleLoginLocal(email, password, rememberMe) {
  const AUTH_STORAGE_KEY = 'em_users';
  const users = JSON.parse(localStorage.getItem(AUTH_STORAGE_KEY) || '[]');
  const user = users.find(u => u.email.toLowerCase() === email.toLowerCase());
  
  if (!user) {
    showToast('该邮箱未注册', 'error');
    return;
  }
  
  const expectedPassword = 'local_' + btoa(password);
  if (user.password !== expectedPassword) {
    showToast('密码错误', 'error');
    return;
  }
  
  setCurrentUser(user);
  
  if (rememberMe) {
    localStorage.setItem(REMEMBER_KEY, 'true');
  }
  
  showToast('✅ 登录成功！正在跳转...', 'success');
  
  setTimeout(() => {
    window.location.href = '../index.html';
  }, 1500);
}

/**
 * 退出登录
 */
async function logout() {
  try {
    if (window.API && API.isLoggedIn()) {
      await API.auth.logout();
    }
  } catch (error) {
    console.log('Logout API failed:', error);
  }
  
  clearCurrentUser();
  
  const loginPath = window.location.pathname.includes('/pages/') 
    ? 'auth.html' 
    : 'pages/auth.html';
  window.location.href = loginPath;
}

// ==================== 页面保护 ====================

/**
 * 检查登录状态，未登录则跳转到登录页
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
 */
function redirectIfLoggedIn() {
  if (isLoggedIn()) {
    window.location.href = window.location.pathname.includes('/pages/') 
      ? '../index.html' 
      : 'index.html';
  }
}

/**
 * 刷新用户信息（从后端获取最新数据）
 */
async function refreshUserInfo() {
  if (window.API && API.isLoggedIn()) {
    try {
      const userData = await API.auth.getCurrentUser();
      setCurrentUser(userData);
      return userData;
    } catch (error) {
      console.error('Failed to refresh user info:', error);
      // Token 可能已失效，清除登录状态
      if (error.code === 2001 || error.code === 2002) {
        clearCurrentUser();
      }
    }
  }
  return getCurrentUser();
}

// ==================== 初始化 ====================

document.addEventListener('DOMContentLoaded', function() {
  if (window.location.pathname.includes('auth.html')) {
    redirectIfLoggedIn();
  }
});

// ==================== 导出接口 ====================
window.Auth = {
  isLoggedIn,
  getCurrentUser,
  setCurrentUser,
  clearCurrentUser,
  logout,
  requireAuth,
  refreshUserInfo
};
