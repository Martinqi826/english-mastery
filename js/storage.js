/**
 * English Mastery - 数据存储模块
 * 改造版本：支持云端同步 + 本地缓存
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
    SETTINGS: 'em_settings',
    SYNC_TIMESTAMP: 'em_sync_timestamp'
  },

  // 同步状态
  _syncInProgress: false,
  _syncQueue: [],

  // ==================== 基础存储操作 ====================

  /**
   * 获取本地数据
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
   * 设置本地数据
   */
  set(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch (e) {
      console.error('Storage.set error:', e);
    }
  },

  /**
   * 删除本地数据
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

  // ==================== 云端同步 ====================

  /**
   * 检查是否可以使用云端同步
   */
  canUseCloudSync() {
    return window.API && API.isLoggedIn();
  },

  /**
   * 从云端获取学习进度
   */
  async fetchProgressFromCloud() {
    if (!this.canUseCloudSync()) return null;

    try {
      const cloudProgress = await API.learning.getProgress();
      
      // 缓存到本地
      this.set(this.KEYS.PROGRESS, {
        vocabulary: cloudProgress.vocabulary,
        listening: cloudProgress.listening,
        reading: cloudProgress.reading,
        writing: cloudProgress.writing,
        speaking: cloudProgress.speaking,
        overall: cloudProgress.overall
      });

      this.set(this.KEYS.STUDY, {
        currentDay: cloudProgress.current_day,
        startDate: cloudProgress.start_date,
        streak: cloudProgress.streak_days,
        totalTime: cloudProgress.total_study_time,
        wordsLearned: cloudProgress.words_learned,
        todayTasks: []
      });

      this.set(this.KEYS.SYNC_TIMESTAMP, Date.now());

      return cloudProgress;
    } catch (error) {
      console.error('Failed to fetch progress from cloud:', error);
      return null;
    }
  },

  /**
   * 同步进度到云端
   */
  async syncProgressToCloud(progressData) {
    if (!this.canUseCloudSync()) return false;

    try {
      await API.learning.updateProgress(progressData);
      this.set(this.KEYS.SYNC_TIMESTAMP, Date.now());
      return true;
    } catch (error) {
      console.error('Failed to sync progress to cloud:', error);
      // 加入同步队列，稍后重试
      this._syncQueue.push({ type: 'progress', data: progressData });
      return false;
    }
  },

  /**
   * 处理同步队列
   */
  async processSyncQueue() {
    if (this._syncInProgress || this._syncQueue.length === 0) return;

    this._syncInProgress = true;

    while (this._syncQueue.length > 0) {
      const item = this._syncQueue.shift();
      try {
        if (item.type === 'progress') {
          await API.learning.updateProgress(item.data);
        } else if (item.type === 'checkin') {
          await API.learning.checkin(item.data.tasks, item.data.studyTime);
        }
      } catch (error) {
        console.error('Sync queue item failed:', error);
        // 重新加入队列
        this._syncQueue.unshift(item);
        break;
      }
    }

    this._syncInProgress = false;
  },

  // ==================== 进度数据 ====================

  /**
   * 获取进度数据（优先从缓存，可选从云端刷新）
   */
  getProgress(forceRefresh = false) {
    const localProgress = this.get(this.KEYS.PROGRESS, {
      vocabulary: 0,
      listening: 0,
      reading: 0,
      writing: 0,
      speaking: 0,
      overall: 0
    });

    // 异步刷新云端数据
    if (forceRefresh && this.canUseCloudSync()) {
      this.fetchProgressFromCloud();
    }

    return localProgress;
  },

  /**
   * 更新进度数据
   */
  async setProgress(progress) {
    // 先更新本地
    this.set(this.KEYS.PROGRESS, progress);

    // 同步到云端
    if (this.canUseCloudSync()) {
      await this.syncProgressToCloud(progress);
    }
  },

  /**
   * 更新单项进度
   */
  async updateSkillProgress(skill, value) {
    const progress = this.getProgress();
    progress[skill] = Math.min(100, Math.max(0, value));
    progress.overall = this.calculateOverallProgress(progress);
    
    // 保存到本地
    this.set(this.KEYS.PROGRESS, progress);

    // 同步到云端
    if (this.canUseCloudSync()) {
      const updateData = {};
      updateData[skill] = value;
      await this.syncProgressToCloud(updateData);
    }

    return progress;
  },

  /**
   * 计算总体进度
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
   * 获取打卡记录（本地缓存）
   */
  getCheckinData() {
    return this.get(this.KEYS.CHECKIN, {});
  },

  /**
   * 获取某天的打卡记录
   */
  getCheckinByDate(date) {
    const data = this.getCheckinData();
    return data[date] || null;
  },

  /**
   * 设置某天的打卡记录
   */
  setCheckinByDate(date, record) {
    const data = this.getCheckinData();
    data[date] = record;
    this.set(this.KEYS.CHECKIN, data);
  },

  /**
   * 今日打卡
   */
  async checkinToday(tasks, studyTime = 0) {
    const today = this.getTodayString();

    // 本地记录
    this.setCheckinByDate(today, {
      completed: true,
      tasks: tasks,
      studyTime: studyTime,
      timestamp: Date.now()
    });

    // 更新本地学习数据
    const study = this.getStudyData();
    study.streak = this.calculateStreak();
    this.setStudyData(study);

    // 同步到云端
    if (this.canUseCloudSync()) {
      try {
        const result = await API.learning.checkin(tasks, studyTime);
        // 更新云端返回的连续打卡天数
        if (result && result.streak_days !== undefined) {
          study.streak = result.streak_days;
          this.setStudyData(study);
        }
        return result;
      } catch (error) {
        console.error('Cloud checkin failed:', error);
        // 加入同步队列
        this._syncQueue.push({ type: 'checkin', data: { tasks, studyTime } });
      }
    }

    return { streak_days: study.streak };
  },

  /**
   * 检查今日是否已打卡
   */
  isTodayCheckedIn() {
    const today = this.getTodayString();
    const record = this.getCheckinByDate(today);
    return record && record.completed;
  },

  /**
   * 从云端获取打卡历史
   */
  async fetchCheckinHistory(startDate = null, endDate = null) {
    if (!this.canUseCloudSync()) return this.getCheckinData();

    try {
      const history = await API.learning.getCheckinHistory(startDate, endDate);

      // 更新本地缓存
      const localData = this.getCheckinData();
      if (history.records) {
        history.records.forEach(record => {
          localData[record.checkin_date] = {
            completed: true,
            tasks: record.tasks,
            studyTime: record.study_time,
            timestamp: new Date(record.checkin_date).getTime()
          };
        });
        this.set(this.KEYS.CHECKIN, localData);
      }

      return history;
    } catch (error) {
      console.error('Failed to fetch checkin history:', error);
      return { records: [], current_streak: this.calculateStreak() };
    }
  },

  // ==================== 学习数据 ====================

  /**
   * 获取学习数据
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
   */
  setStudyData(data) {
    this.set(this.KEYS.STUDY, data);
  },

  /**
   * 获取当前学习天数
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
   */
  calculateStreak() {
    const checkinData = this.getCheckinData();
    let streak = 0;
    let currentDate = new Date();

    const todayStr = this.getTodayString();
    if (!checkinData[todayStr]?.completed) {
      currentDate.setDate(currentDate.getDate() - 1);
    }

    while (true) {
      const dateStr = this.formatDate(currentDate);
      if (checkinData[dateStr]?.completed) {
        streak++;
        currentDate.setDate(currentDate.getDate() - 1);
      } else {
        break;
      }
    }

    if (checkinData[todayStr]?.completed) {
      streak++;
    }

    return streak;
  },

  /**
   * 更新今日任务完成状态
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
   */
  getTodayTasks() {
    const study = this.getStudyData();
    return study.todayTasks || [];
  },

  /**
   * 增加学习时长
   */
  async addStudyTime(minutes) {
    const study = this.getStudyData();
    study.totalTime = (study.totalTime || 0) + minutes;
    this.setStudyData(study);

    const today = this.getTodayString();
    const checkin = this.getCheckinByDate(today) || { tasks: [], studyTime: 0 };
    checkin.studyTime = (checkin.studyTime || 0) + minutes;
    this.setCheckinByDate(today, checkin);

    // 同步到云端
    if (this.canUseCloudSync()) {
      try {
        await API.learning.addStudyTime(minutes);
      } catch (error) {
        console.error('Failed to sync study time:', error);
      }
    }
  },

  /**
   * 增加已学词汇数
   */
  async addWordsLearned(count) {
    const study = this.getStudyData();
    study.wordsLearned = (study.wordsLearned || 0) + count;
    this.setStudyData(study);

    // 同步到云端
    if (this.canUseCloudSync()) {
      try {
        await API.learning.addWordsLearned(count);
      } catch (error) {
        console.error('Failed to sync words learned:', error);
      }
    }
  },

  // ==================== 评估数据 ====================

  /**
   * 获取评估数据
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
   */
  getTodayString() {
    return this.formatDate(new Date());
  },

  /**
   * 格式化日期
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
  async initializeStudy() {
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

    // 如果已登录，从云端同步数据
    if (this.canUseCloudSync()) {
      await this.fetchProgressFromCloud();
    }

    return study;
  },

  /**
   * 全量同步（登录后调用）
   */
  async fullSync() {
    if (!this.canUseCloudSync()) return;

    try {
      // 获取云端进度
      await this.fetchProgressFromCloud();

      // 获取最近30天打卡记录
      const thirtyDaysAgo = new Date();
      thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);
      await this.fetchCheckinHistory(this.formatDate(thirtyDaysAgo));

      // 处理同步队列
      await this.processSyncQueue();

      console.log('Full sync completed');
    } catch (error) {
      console.error('Full sync failed:', error);
    }
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

// 监听登录状态变化，自动同步
window.addEventListener('focus', () => {
  if (Storage.canUseCloudSync()) {
    Storage.processSyncQueue();
  }
});
