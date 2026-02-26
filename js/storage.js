/**
 * English Mastery - 数据存储模块
 * 使用 LocalStorage 进行数据持久化
 */

const Storage = {
  // 存储键名前缀
  PREFIX: 'em_',

  // 键名定义
  KEYS: {
    PROGRESS: 'em_progress',
    CHECKIN: 'em_checkin',
    STUDY: 'em_study',
    ASSESSMENT: 'em_assessment',
    SETTINGS: 'em_settings'
  },

  /**
   * 获取数据
   * @param {string} key - 存储键名
   * @param {any} defaultValue - 默认值
   * @returns {any}
   */
  get(key, defaultValue = null) {
    try {
      const data = localStorage.getItem(key);
      return data ? JSON.parse(data) : defaultValue;
    } catch (e) {
      console.error('Storage.get error:', e);
      return defaultValue;
    }
  },

  /**
   * 设置数据
   * @param {string} key - 存储键名
   * @param {any} value - 数据值
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.error('Storage.set error:', e);
    }
  },

  /**
   * 删除数据
   * @param {string} key - 存储键名
   */
  remove(key) {
    try {
      localStorage.removeItem(key);
    } catch (e) {
      console.error('Storage.remove error:', e);
    }
  },

  /**
   * 清除所有 English Mastery 数据
   */
  clearAll() {
    Object.values(this.KEYS).forEach(key => {
      this.remove(key);
    });
  },

  // ==================== 进度数据 ====================

  /**
   * 获取进度数据
   * @returns {Object}
   */
  getProgress() {
    return this.get(this.KEYS.PROGRESS, {
      vocabulary: 40,
      listening: 35,
      reading: 38,
      writing: 32,
      speaking: 30,
      overall: 35
    });
  },

  /**
   * 更新进度数据
   * @param {Object} progress - 进度数据
   */
  setProgress(progress) {
    this.set(this.KEYS.PROGRESS, progress);
  },

  /**
   * 更新单项进度
   * @param {string} skill - 技能名称
   * @param {number} value - 进度值
   */
  updateSkillProgress(skill, value) {
    const progress = this.getProgress();
    progress[skill] = Math.min(100, Math.max(0, value));
    progress.overall = this.calculateOverallProgress(progress);
    this.setProgress(progress);
    return progress;
  },

  /**
   * 计算总体进度
   * @param {Object} progress - 进度数据
   * @returns {number}
   */
  calculateOverallProgress(progress) {
    const weights = {
      vocabulary: 0.2,
      listening: 0.2,
      reading: 0.2,
      writing: 0.2,
      speaking: 0.2
    };
    let total = 0;
    Object.keys(weights).forEach(skill => {
      total += (progress[skill] || 0) * weights[skill];
    });
    return Math.round(total);
  },

  // ==================== 打卡数据 ====================

  /**
   * 获取打卡记录
   * @returns {Object}
   */
  getCheckinData() {
    return this.get(this.KEYS.CHECKIN, {});
  },

  /**
   * 获取某天的打卡记录
   * @param {string} date - 日期字符串 YYYY-MM-DD
   * @returns {Object|null}
   */
  getCheckinByDate(date) {
    const data = this.getCheckinData();
    return data[date] || null;
  },

  /**
   * 设置某天的打卡记录
   * @param {string} date - 日期字符串 YYYY-MM-DD
   * @param {Object} record - 打卡记录
   */
  setCheckinByDate(date, record) {
    const data = this.getCheckinData();
    data[date] = record;
    this.set(this.KEYS.CHECKIN, data);
  },

  /**
   * 今日打卡
   * @param {Array} tasks - 完成的任务列表
   * @param {number} studyTime - 学习时长（分钟）
   */
  checkinToday(tasks, studyTime = 0) {
    const today = this.getTodayString();
    this.setCheckinByDate(today, {
      completed: true,
      tasks: tasks,
      studyTime: studyTime,
      timestamp: Date.now()
    });
    
    // 更新学习数据
    const study = this.getStudyData();
    study.streak = this.calculateStreak();
    this.setStudyData(study);
  },

  /**
   * 检查今日是否已打卡
   * @returns {boolean}
   */
  isTodayCheckedIn() {
    const today = this.getTodayString();
    const record = this.getCheckinByDate(today);
    return record && record.completed;
  },

  // ==================== 学习数据 ====================

  /**
   * 获取学习数据
   * @returns {Object}
   */
  getStudyData() {
    const defaultData = {
      currentDay: 1,
      startDate: this.getTodayString(),
      streak: 0,
      totalTime: 0,
      wordsLearned: 0,
      todayTasks: []
    };
    return this.get(this.KEYS.STUDY, defaultData);
  },

  /**
   * 设置学习数据
   * @param {Object} data - 学习数据
   */
  setStudyData(data) {
    this.set(this.KEYS.STUDY, data);
  },

  /**
   * 获取当前学习天数
   * @returns {number}
   */
  getCurrentDay() {
    const study = this.getStudyData();
    const startDate = new Date(study.startDate);
    const today = new Date(this.getTodayString());
    const diffDays = Math.floor((today - startDate) / (1000 * 60 * 60 * 24));
    return Math.min(30, Math.max(1, diffDays + 1));
  },

  /**
   * 计算连续打卡天数
   * @returns {number}
   */
  calculateStreak() {
    const checkinData = this.getCheckinData();
    let streak = 0;
    let currentDate = new Date();
    
    // 检查今天是否打卡
    const todayStr = this.getTodayString();
    if (!checkinData[todayStr]?.completed) {
      // 如果今天没打卡，从昨天开始检查
      currentDate.setDate(currentDate.getDate() - 1);
    }
    
    // 向前检查连续打卡天数
    while (true) {
      const dateStr = this.formatDate(currentDate);
      if (checkinData[dateStr]?.completed) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }
    
    // 如果今天已打卡，streak 需要 +1
    if (checkinData[todayStr]?.completed) {
      streak++;
    }
    
    return streak;
  },

  /**
   * 更新今日任务完成状态
   * @param {string} task - 任务名称
   * @param {boolean} completed - 是否完成
   */
  updateTodayTask(task, completed) {
    const study = this.getStudyData();
    if (!study.todayTasks) {
      study.todayTasks = [];
    }
    
    if (completed) {
      if (!study.todayTasks.includes(task)) {
        study.todayTasks.push(task);
      }
    } else {
      study.todayTasks = study.todayTasks.filter(t => t !== task);
    }
    
    this.setStudyData(study);
    return study.todayTasks;
  },

  /**
   * 获取今日已完成任务
   * @returns {Array}
   */
  getTodayTasks() {
    const study = this.getStudyData();
    return study.todayTasks || [];
  },

  /**
   * 增加学习时长
   * @param {number} minutes - 分钟数
   */
  addStudyTime(minutes) {
    const study = this.getStudyData();
    study.totalTime = (study.totalTime || 0) + minutes;
    this.setStudyData(study);
    
    // 同时更新今日打卡记录的学习时长
    const today = this.getTodayString();
    const checkin = this.getCheckinByDate(today) || { tasks: [], studyTime: 0 };
    checkin.studyTime = (checkin.studyTime || 0) + minutes;
    this.setCheckinByDate(today, checkin);
  },

  /**
   * 增加已学词汇数
   * @param {number} count - 词汇数
   */
  addWordsLearned(count) {
    const study = this.getStudyData();
    study.wordsLearned = (study.wordsLearned || 0) + count;
    this.setStudyData(study);
  },

  // ==================== 评估数据 ====================

  /**
   * 获取评估数据
   * @returns {Object}
   */
  getAssessmentData() {
    return this.get(this.KEYS.ASSESSMENT, {
      initial: null,
      week1: null,
      week2: null,
      week3: null,
      final: null
    });
  },

  /**
   * 保存评估结果
   * @param {string} type - 评估类型 (initial/week1/week2/week3/final)
   * @param {Object} result - 评估结果
   */
  saveAssessment(type, result) {
    const data = this.getAssessmentData();
    data[type] = {
      ...result,
      date: this.getTodayString(),
      timestamp: Date.now()
    };
    this.set(this.KEYS.ASSESSMENT, data);
  },

  // ==================== 工具方法 ====================

  /**
   * 获取今天的日期字符串
   * @returns {string} YYYY-MM-DD
   */
  getTodayString() {
    return this.formatDate(new Date());
  },

  /**
   * 格式化日期
   * @param {Date} date - 日期对象
   * @returns {string} YYYY-MM-DD
   */
  formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  },

  /**
   * 初始化学习（首次使用）
   */
  initializeStudy() {
    const study = this.getStudyData();
    if (!study.startDate) {
      study.startDate = this.getTodayString();
      study.currentDay = 1;
      study.streak = 0;
      study.totalTime = 0;
      study.wordsLearned = 0;
      study.todayTasks = [];
      this.setStudyData(study);
    }
    return study;
  },

  /**
   * 重置所有数据（用于测试）
   */
  resetAll() {
    if (confirm('确定要重置所有学习数据吗？此操作不可恢复！')) {
      this.clearAll();
      location.reload();
    }
  }
};

// 初始化
Storage.initializeStudy();
