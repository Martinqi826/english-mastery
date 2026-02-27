/**
 * English Mastery - 素材管理模块
 * 用户自定义学习素材的上传和管理
 */

const Materials = {
  // API 基础地址
  API_BASE: 'https://english-mastery-production.up.railway.app/api/v1',
  
  // 轮询间隔（毫秒）
  POLL_INTERVAL: 2000,
  
  // 当前轮询的素材 ID 列表
  pollingIds: new Set(),
  
  // 轮询定时器
  pollTimer: null,

  /**
   * 获取认证头
   */
  getAuthHeaders() {
    const token = localStorage.getItem('em_access_token');
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    };
  },

  /**
   * 发起 API 请求
   */
  async request(endpoint, options = {}) {
    const url = `${this.API_BASE}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        ...this.getAuthHeaders(),
        ...options.headers
      }
    });
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail?.message || error.message || `请求失败: ${response.status}`);
    }
    
    return response.json();
  },

  /**
   * 创建文本素材
   */
  async createFromText(title, content) {
    return this.request('/materials/text', {
      method: 'POST',
      body: JSON.stringify({ title, content })
    });
  },

  /**
   * 创建 URL 素材
   */
  async createFromUrl(title, url) {
    return this.request('/materials/url', {
      method: 'POST',
      body: JSON.stringify({ title: title || null, url })
    });
  },

  /**
   * 获取素材列表
   */
  async getList(page = 1, pageSize = 20) {
    return this.request(`/materials?page=${page}&page_size=${pageSize}`);
  },

  /**
   * 获取素材详情
   */
  async getDetail(id) {
    return this.request(`/materials/${id}`);
  },

  /**
   * 获取素材状态
   */
  async getStatus(id) {
    return this.request(`/materials/${id}/status`);
  },

  /**
   * 删除素材
   */
  async delete(id) {
    return this.request(`/materials/${id}`, { method: 'DELETE' });
  },

  /**
   * 获取素材词汇
   */
  async getVocabularies(id) {
    return this.request(`/materials/${id}/vocabularies`);
  },

  /**
   * 更新词汇状态
   */
  async updateVocabulary(materialId, vocabId, data) {
    return this.request(`/materials/${materialId}/vocabularies/${vocabId}`, {
      method: 'PATCH',
      body: JSON.stringify(data)
    });
  },

  /**
   * 获取阅读题目
   */
  async getQuestions(id) {
    return this.request(`/materials/${id}/questions`);
  },

  /**
   * 提交答案
   */
  async submitAnswer(materialId, questionId, answer) {
    return this.request(`/materials/${materialId}/questions/answer`, {
      method: 'POST',
      body: JSON.stringify({ question_id: questionId, answer })
    });
  },

  /**
   * 开始轮询素材状态
   */
  startPolling(materialId) {
    this.pollingIds.add(materialId);
    
    if (!this.pollTimer) {
      this.pollTimer = setInterval(() => this.pollStatuses(), this.POLL_INTERVAL);
    }
  },

  /**
   * 停止轮询
   */
  stopPolling(materialId) {
    this.pollingIds.delete(materialId);
    
    if (this.pollingIds.size === 0 && this.pollTimer) {
      clearInterval(this.pollTimer);
      this.pollTimer = null;
    }
  },

  /**
   * 轮询所有待处理素材的状态
   */
  async pollStatuses() {
    for (const id of this.pollingIds) {
      try {
        const result = await this.getStatus(id);
        const status = result.data?.status || result.status;
        
        if (status === 'completed' || status === 'failed') {
          this.stopPolling(id);
          // 触发列表刷新
          if (window.loadMaterials) {
            window.loadMaterials();
          }
        }
      } catch (error) {
        console.error(`Failed to poll status for material ${id}:`, error);
      }
    }
  }
};

// ==================== 页面交互函数 ====================

/**
 * 切换上传方式标签
 */
function switchUploadTab(tab) {
  // 更新标签样式
  document.querySelectorAll('.upload-tab').forEach(el => {
    el.classList.remove('active');
  });
  document.querySelector(`.upload-tab[onclick="switchUploadTab('${tab}')"]`).classList.add('active');
  
  // 显示对应表单
  document.querySelectorAll('.upload-form').forEach(el => {
    el.classList.remove('active');
  });
  document.getElementById(`${tab}Form`).classList.add('active');
}

/**
 * 更新字符计数
 */
function updateCharCount(textarea) {
  const count = textarea.value.length;
  const countEl = document.getElementById('textCharCount');
  countEl.textContent = `${count} / 10000 字符`;
  
  if (count > 10000) {
    countEl.classList.add('error');
    countEl.classList.remove('warning');
  } else if (count > 8000) {
    countEl.classList.add('warning');
    countEl.classList.remove('error');
  } else {
    countEl.classList.remove('warning', 'error');
  }
}

/**
 * 处理文本提交
 */
async function handleTextSubmit(event) {
  event.preventDefault();
  
  const title = document.getElementById('textTitle').value.trim();
  const content = document.getElementById('textContent').value.trim();
  
  if (content.length < 50) {
    showToast('内容太短，请至少输入 50 个字符', 'error');
    return;
  }
  
  if (content.length > 10000) {
    showToast('内容过长，请控制在 10000 字符以内', 'error');
    return;
  }
  
  const btn = document.getElementById('textSubmitBtn');
  setButtonLoading(btn, true);
  
  try {
    const result = await Materials.createFromText(title, content);
    showToast('素材上传成功，正在生成学习内容...', 'success');
    
    // 清空表单
    document.getElementById('textForm').reset();
    updateCharCount(document.getElementById('textContent'));
    
    // 刷新列表
    await loadMaterials();
    
    // 开始轮询新创建的素材
    if (result.data?.id) {
      Materials.startPolling(result.data.id);
    }
  } catch (error) {
    showToast(error.message || '上传失败，请重试', 'error');
  } finally {
    setButtonLoading(btn, false);
  }
}

/**
 * 处理 URL 提交
 */
async function handleUrlSubmit(event) {
  event.preventDefault();
  
  const title = document.getElementById('urlTitle').value.trim();
  const url = document.getElementById('urlInput').value.trim();
  
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    showToast('请输入有效的网页链接', 'error');
    return;
  }
  
  const btn = document.getElementById('urlSubmitBtn');
  setButtonLoading(btn, true);
  
  try {
    const result = await Materials.createFromUrl(title, url);
    showToast('网页抓取成功，正在生成学习内容...', 'success');
    
    // 清空表单
    document.getElementById('urlForm').reset();
    
    // 刷新列表
    await loadMaterials();
    
    // 开始轮询
    if (result.data?.id) {
      Materials.startPolling(result.data.id);
    }
  } catch (error) {
    showToast(error.message || '抓取失败，请检查链接或直接粘贴文本', 'error');
  } finally {
    setButtonLoading(btn, false);
  }
}

/**
 * 加载素材列表
 */
async function loadMaterials() {
  const loadingEl = document.getElementById('loadingState');
  const emptyEl = document.getElementById('emptyState');
  const listEl = document.getElementById('materialsList');
  
  loadingEl.style.display = 'block';
  emptyEl.style.display = 'none';
  listEl.style.display = 'none';
  
  try {
    const result = await Materials.getList();
    const items = result.data?.items || [];
    
    loadingEl.style.display = 'none';
    
    if (items.length === 0) {
      emptyEl.style.display = 'block';
    } else {
      listEl.style.display = 'flex';
      renderMaterialsList(items);
      
      // 为处理中的素材启动轮询
      items.forEach(item => {
        if (item.status === 'pending' || item.status === 'processing') {
          Materials.startPolling(item.id);
        }
      });
    }
  } catch (error) {
    loadingEl.style.display = 'none';
    showToast('加载失败: ' + error.message, 'error');
  }
}

/**
 * 渲染素材列表
 */
function renderMaterialsList(items) {
  const listEl = document.getElementById('materialsList');
  
  listEl.innerHTML = items.map(item => {
    const statusMap = {
      pending: { text: '等待处理', class: 'pending' },
      processing: { text: '生成中...', class: 'processing' },
      completed: { text: '已完成', class: 'completed' },
      failed: { text: '处理失败', class: 'failed' }
    };
    
    const status = statusMap[item.status] || statusMap.pending;
    const sourceIcon = item.source_type === 'url' ? '🔗' : '📝';
    const createdAt = new Date(item.created_at).toLocaleDateString('zh-CN');
    
    return `
      <div class="material-card" data-id="${item.id}">
        <div class="material-card-header">
          <div class="material-title">${sourceIcon} ${escapeHtml(item.title)}</div>
          <span class="material-status ${status.class}">${status.text}</span>
        </div>
        <div class="material-meta">
          <span class="material-meta-item">📅 ${createdAt}</span>
          <span class="material-meta-item">📊 ${item.word_count || 0} 字</span>
          ${item.status === 'completed' ? `
            <span class="material-meta-item">🔤 ${item.generated_vocab_count || 0} 词汇</span>
            <span class="material-meta-item">❓ ${item.generated_question_count || 0} 题目</span>
          ` : ''}
        </div>
        <div class="material-actions">
          ${item.status === 'completed' ? `
            <button class="action-btn primary" onclick="startVocabLearning(${item.id})">
              学习词汇
            </button>
            <button class="action-btn secondary" onclick="startReadingPractice(${item.id})">
              阅读练习
            </button>
          ` : item.status === 'processing' ? `
            <button class="action-btn secondary" disabled>
              <span class="loading-spinner" style="width:14px;height:14px;border-width:2px;"></span>
              生成中...
            </button>
          ` : item.status === 'failed' ? `
            <span style="color:var(--notion-red);font-size:0.875rem;">
              ${item.error_message || '处理失败'}
            </span>
          ` : ''}
          <button class="action-btn danger" onclick="deleteMaterial(${item.id})">
            删除
          </button>
        </div>
      </div>
    `;
  }).join('');
}

/**
 * 刷新素材列表
 */
async function refreshMaterials() {
  const btn = document.getElementById('refreshBtn');
  btn.classList.add('refreshing');
  
  try {
    await loadMaterials();
    showToast('刷新成功', 'success');
  } catch (error) {
    showToast('刷新失败', 'error');
  } finally {
    btn.classList.remove('refreshing');
  }
}

/**
 * 删除素材
 */
async function deleteMaterial(id) {
  if (!confirm('确定要删除这个素材吗？删除后无法恢复。')) {
    return;
  }
  
  try {
    await Materials.delete(id);
    showToast('删除成功', 'success');
    Materials.stopPolling(id);
    await loadMaterials();
  } catch (error) {
    showToast('删除失败: ' + error.message, 'error');
  }
}

/**
 * 开始词汇学习
 */
function startVocabLearning(materialId) {
  // 跳转到词汇学习页面，带上素材 ID
  window.location.href = `vocabulary.html?material=${materialId}`;
}

/**
 * 开始阅读练习
 */
function startReadingPractice(materialId) {
  // 跳转到阅读练习页面，带上素材 ID
  window.location.href = `reading.html?material=${materialId}`;
}

// ==================== 工具函数 ====================

/**
 * 设置按钮加载状态
 */
function setButtonLoading(btn, loading) {
  if (loading) {
    btn.disabled = true;
    btn.innerHTML = '<span class="loading-spinner"></span><span>处理中...</span>';
  } else {
    btn.disabled = false;
    btn.innerHTML = '<span>' + (btn.id === 'textSubmitBtn' ? '开始生成学习内容' : '抓取并生成学习内容') + '</span>';
  }
}

/**
 * 显示 Toast 消息
 */
function showToast(message, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = 'toast ' + type;
  toast.classList.add('show');
  
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

/**
 * HTML 转义
 */
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// 导出到全局
window.Materials = Materials;
window.loadMaterials = loadMaterials;
window.switchUploadTab = switchUploadTab;
window.updateCharCount = updateCharCount;
window.handleTextSubmit = handleTextSubmit;
window.handleUrlSubmit = handleUrlSubmit;
window.refreshMaterials = refreshMaterials;
window.deleteMaterial = deleteMaterial;
window.startVocabLearning = startVocabLearning;
window.startReadingPractice = startReadingPractice;
window.showToast = showToast;
