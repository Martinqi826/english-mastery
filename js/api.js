/**
 * English Mastery - API 调用层
 * 封装所有后端接口调用，统一错误处理
 */

const API = {
  // API 基础配置 - 自动检测环境
  // Railway 后端 URL（部署后替换）
  // 本地开发: 'http://localhost:8000/api/v1'
  // 生产环境: 'https://your-app.railway.app/api/v1'
  baseURL: window.location.hostname === 'localhost' 
    ? 'http://localhost:8000/api/v1' 
    : (window.API_BASE_URL || '/api/v1'),
  
  // Token 存储键
  ACCESS_TOKEN_KEY: 'em_access_token',
  REFRESH_TOKEN_KEY: 'em_refresh_token',
  
  // ==================== 工具方法 ====================
  
  /**
   * 获取存储的 Access Token
   */
  getAccessToken() {
    return localStorage.getItem(this.ACCESS_TOKEN_KEY);
  },
  
  /**
   * 获取存储的 Refresh Token
   */
  getRefreshToken() {
    return localStorage.getItem(this.REFRESH_TOKEN_KEY);
  },
  
  /**
   * 保存 Token
   */
  saveTokens(accessToken, refreshToken) {
    localStorage.setItem(this.ACCESS_TOKEN_KEY, accessToken);
    if (refreshToken) {
      localStorage.setItem(this.REFRESH_TOKEN_KEY, refreshToken);
    }
  },
  
  /**
   * 清除 Token
   */
  clearTokens() {
    localStorage.removeItem(this.ACCESS_TOKEN_KEY);
    localStorage.removeItem(this.REFRESH_TOKEN_KEY);
  },
  
  /**
   * 检查是否已登录
   */
  isLoggedIn() {
    return !!this.getAccessToken();
  },
  
  /**
   * 构建请求头
   */
  getHeaders(includeAuth = true) {
    const headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth) {
      const token = this.getAccessToken();
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    return headers;
  },
  
  /**
   * 发送请求
   */
  async request(method, endpoint, data = null, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method,
      headers: this.getHeaders(options.auth !== false),
    };
    
    if (data && method !== 'GET') {
      config.body = JSON.stringify(data);
    }
    
    try {
      let response = await fetch(url, config);
      
      // Token 过期，尝试刷新
      if (response.status === 401 && options.retry !== false) {
        const refreshed = await this.refreshTokens();
        if (refreshed) {
          // 重试请求
          config.headers = this.getHeaders(true);
          response = await fetch(url, config);
        } else {
          // 刷新失败，跳转登录
          this.clearTokens();
          this.redirectToLogin();
          throw new Error('登录已过期，请重新登录');
        }
      }
      
      const result = await response.json();
      
      // 统一错误处理
      if (result.code !== 0) {
        throw new APIError(result.code, result.message, result.data);
      }
      
      return result.data;
      
    } catch (error) {
      if (error instanceof APIError) {
        throw error;
      }
      console.error('API request failed:', error);
      throw new APIError(1000, error.message || '网络请求失败');
    }
  },
  
  /**
   * 刷新 Token
   */
  async refreshTokens() {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      return false;
    }
    
    try {
      const response = await fetch(`${this.baseURL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken })
      });
      
      const result = await response.json();
      
      if (result.code === 0 && result.data) {
        this.saveTokens(
          result.data.access_token,
          result.data.refresh_token
        );
        return true;
      }
      
      return false;
    } catch {
      return false;
    }
  },
  
  /**
   * 跳转到登录页
   */
  redirectToLogin() {
    const currentPath = window.location.pathname;
    if (!currentPath.includes('auth.html')) {
      const loginPath = currentPath.includes('/pages/') 
        ? 'auth.html' 
        : 'pages/auth.html';
      window.location.href = loginPath;
    }
  },
  
  // ==================== 认证接口 ====================
  
  auth: {
    /**
     * 用户注册
     */
    async register(data) {
      const result = await API.request('POST', '/auth/register', data, { auth: false });
      if (result.tokens) {
        API.saveTokens(result.tokens.access_token, result.tokens.refresh_token);
      }
      return result;
    },
    
    /**
     * 用户登录
     */
    async login(email, password) {
      const result = await API.request('POST', '/auth/login', { 
        email, 
        password 
      }, { auth: false });
      if (result.tokens) {
        API.saveTokens(result.tokens.access_token, result.tokens.refresh_token);
      }
      return result;
    },
    
    /**
     * 手机号登录
     */
    async loginWithPhone(phone, password) {
      const result = await API.request('POST', '/auth/login', { 
        phone, 
        password 
      }, { auth: false });
      if (result.tokens) {
        API.saveTokens(result.tokens.access_token, result.tokens.refresh_token);
      }
      return result;
    },
    
    /**
     * 退出登录
     */
    async logout() {
      try {
        await API.request('POST', '/auth/logout', {
          refresh_token: API.getRefreshToken()
        });
      } catch (e) {
        console.log('Logout API call failed:', e);
      }
      API.clearTokens();
    },
    
    /**
     * 获取当前用户信息
     */
    async getCurrentUser() {
      return await API.request('GET', '/auth/me');
    }
  },
  
  // ==================== 用户接口 ====================
  
  user: {
    /**
     * 获取用户资料
     */
    async getProfile() {
      return await API.request('GET', '/users/profile');
    },
    
    /**
     * 更新用户资料
     */
    async updateProfile(data) {
      return await API.request('PUT', '/users/profile', data);
    },
    
    /**
     * 修改密码
     */
    async changePassword(oldPassword, newPassword) {
      return await API.request('PUT', '/users/password', {
        old_password: oldPassword,
        new_password: newPassword
      });
    },
    
    /**
     * 获取会员状态
     */
    async getMembership() {
      return await API.request('GET', '/users/membership');
    }
  },
  
  // ==================== 学习接口 ====================
  
  learning: {
    /**
     * 获取学习进度
     */
    async getProgress() {
      return await API.request('GET', '/learning/progress');
    },
    
    /**
     * 更新学习进度
     */
    async updateProgress(data) {
      return await API.request('PUT', '/learning/progress', data);
    },
    
    /**
     * 增加学习时长
     */
    async addStudyTime(minutes) {
      return await API.request('PUT', '/learning/progress', {
        add_study_time: minutes
      });
    },
    
    /**
     * 增加已学词汇数
     */
    async addWordsLearned(count) {
      return await API.request('PUT', '/learning/progress', {
        add_words_learned: count
      });
    },
    
    /**
     * 今日打卡
     */
    async checkin(tasks, studyTime = 0, note = '') {
      return await API.request('POST', '/learning/checkin', {
        tasks,
        study_time: studyTime,
        note
      });
    },
    
    /**
     * 获取打卡历史
     */
    async getCheckinHistory(startDate = null, endDate = null) {
      let endpoint = '/learning/checkin/history';
      const params = [];
      if (startDate) params.push(`start_date=${startDate}`);
      if (endDate) params.push(`end_date=${endDate}`);
      if (params.length) endpoint += '?' + params.join('&');
      return await API.request('GET', endpoint);
    },
    
    /**
     * 获取今日学习状态
     */
    async getTodayStatus() {
      return await API.request('GET', '/learning/today');
    },
    
    /**
     * 获取学习统计
     */
    async getStats() {
      return await API.request('GET', '/learning/stats');
    }
  },
  
  // ==================== 词汇接口 ====================
  
  vocabulary: {
    /**
     * 获取今日词汇
     */
    async getToday(day = 1) {
      return await API.request('GET', `/vocabulary/today?day=${day}`, null, { auth: false });
    },
    
    /**
     * 获取词汇详情
     */
    async getDetail(wordId) {
      return await API.request('GET', `/vocabulary/${wordId}`, null, { auth: false });
    },
    
    /**
     * 搜索词汇
     */
    async search(keyword) {
      return await API.request('GET', `/vocabulary/search?keyword=${encodeURIComponent(keyword)}`, null, { auth: false });
    },
    
    /**
     * 标记词汇已学习
     */
    async markLearned(wordId) {
      return await API.request('POST', `/vocabulary/${wordId}/learned`);
    },
    
    /**
     * 获取词汇学习进度
     */
    async getProgress() {
      return await API.request('GET', '/vocabulary/progress/summary');
    }
  },
  
  // ==================== 支付接口 ====================
  
  payment: {
    /**
     * 获取产品列表
     */
    async getProducts() {
      return await API.request('GET', '/payment/products', null, { auth: false });
    },
    
    /**
     * 创建订单
     */
    async createOrder(productId, payMethod) {
      return await API.request('POST', '/payment/orders', {
        product_id: productId,
        pay_method: payMethod
      });
    },
    
    /**
     * 获取订单列表
     */
    async getOrders(status = null, page = 1, pageSize = 20) {
      let endpoint = `/payment/orders?page=${page}&page_size=${pageSize}`;
      if (status) endpoint += `&status=${status}`;
      return await API.request('GET', endpoint);
    },
    
    /**
     * 获取订单详情
     */
    async getOrderDetail(orderNo) {
      return await API.request('GET', `/payment/orders/${orderNo}`);
    },
    
    /**
     * 取消订单
     */
    async cancelOrder(orderNo) {
      return await API.request('POST', `/payment/orders/${orderNo}/cancel`);
    }
  }
};


/**
 * API 错误类
 */
class APIError extends Error {
  constructor(code, message, data = null) {
    super(message);
    this.name = 'APIError';
    this.code = code;
    this.data = data;
  }
}


// 错误码定义
const ErrorCode = {
  // 通用错误
  UNKNOWN_ERROR: 1000,
  INVALID_PARAMS: 1001,
  NOT_FOUND: 1002,
  PERMISSION_DENIED: 1003,
  RATE_LIMIT_EXCEEDED: 1004,
  
  // 认证错误
  UNAUTHORIZED: 2000,
  INVALID_TOKEN: 2001,
  TOKEN_EXPIRED: 2002,
  INVALID_CREDENTIALS: 2003,
  USER_NOT_FOUND: 2004,
  USER_DISABLED: 2005,
  EMAIL_EXISTS: 2006,
  PHONE_EXISTS: 2007,
  
  // 会员错误
  MEMBERSHIP_EXPIRED: 3000,
  MEMBERSHIP_REQUIRED: 3001,
  PREMIUM_REQUIRED: 3002,
  
  // 支付错误
  ORDER_NOT_FOUND: 4000,
  ORDER_EXPIRED: 4001,
  ORDER_ALREADY_PAID: 4002,
  PAYMENT_FAILED: 4003,
  
  // 内容错误
  CONTENT_NOT_FOUND: 5000,
  CONTENT_UNAVAILABLE: 5001
};


// 导出
window.API = API;
window.APIError = APIError;
window.ErrorCode = ErrorCode;
