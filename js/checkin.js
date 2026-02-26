/**
 * English Mastery - 打卡系统模块
 */

const Checkin = {
  // 打卡所需最少完成任务数
  MIN_TASKS_REQUIRED: 3,
  
  // 所有任务列表
  ALL_TASKS: ['vocabulary', 'listening', 'reading', 'writing', 'test'],

  // 任务名称映射
  TASK_NAMES: {
    vocabulary: '词汇学习',
    listening: '听力练习',
    reading: '阅读练习',
    writing: '写作练习',
    test: '每日测验'
  },

  /**
   * 检查是否可以打卡
   * @returns {Object} { canCheckin: boolean, completedTasks: number, required: number }
   */
  checkCanCheckin() {
    const completedTasks = Storage.getTodayTasks();
    return {
      canCheckin: completedTasks.length >= this.MIN_TASKS_REQUIRED,
      completedTasks: completedTasks.length,
      required: this.MIN_TASKS_REQUIRED,
      tasks: completedTasks
    };
  },

  /**
   * 执行打卡
   * @returns {Object} 打卡结果
   */
  doCheckin() {
    const check = this.checkCanCheckin();
    
    if (!check.canCheckin) {
      return {
        success: false,
        message: `还需完成 ${this.MIN_TASKS_REQUIRED - check.completedTasks} 项任务才能打卡`
      };
    }

    if (Storage.isTodayCheckedIn()) {
      return {
        success: false,
        message: '今天已经打卡过了！'
      };
    }

    // 获取今日学习时长
    const todayRecord = Storage.getCheckinByDate(Storage.getTodayString());
    const studyTime = todayRecord?.studyTime || 0;

    // 执行打卡
    Storage.checkinToday(check.tasks, studyTime);

    // 更新进度（根据完成的任务）
    this.updateProgressByTasks(check.tasks);

    const streak = Storage.calculateStreak();
    
    return {
      success: true,
      message: `打卡成功！已连续学习 ${streak} 天！`,
      streak: streak,
      tasks: check.tasks
    };
  },

  /**
   * 根据完成的任务更新进度
   * @param {Array} tasks - 完成的任务列表
   */
  updateProgressByTasks(tasks) {
    const progress = Storage.getProgress();
    
    tasks.forEach(task => {
      // 根据任务类型更新对应技能进度
      const skillMap = {
        vocabulary: 'vocabulary',
        listening: 'listening',
        reading: 'reading',
        writing: 'writing',
        test: null  // 测试会更新所有技能
      };

      if (task === 'test') {
        // 测试通过，所有技能 +0.5
        ['vocabulary', 'listening', 'reading', 'writing', 'speaking'].forEach(skill => {
          progress[skill] = Math.min(100, (progress[skill] || 0) + 0.5);
        });
      } else if (skillMap[task]) {
        // 对应技能 +1
        progress[skillMap[task]] = Math.min(100, (progress[skillMap[task]] || 0) + 1);
      }
    });

    // 重新计算总体进度
    progress.overall = Storage.calculateOverallProgress(progress);
    Storage.setProgress(progress);
  },

  /**
   * 切换任务完成状态
   * @param {string} task - 任务名称
   * @returns {Object} 切换结果
   */
  toggleTask(task) {
    const currentTasks = Storage.getTodayTasks();
    const isCompleted = currentTasks.includes(task);
    
    const newTasks = Storage.updateTodayTask(task, !isCompleted);
    
    return {
      task,
      completed: !isCompleted,
      totalCompleted: newTasks.length,
      canCheckin: newTasks.length >= this.MIN_TASKS_REQUIRED
    };
  },

  /**
   * 生成日历数据
   * @param {number} year - 年份
   * @param {number} month - 月份（1-12）
   * @returns {Array} 日历天数数组
   */
  generateCalendarDays(year, month) {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const daysInMonth = lastDay.getDate();
    const startWeekday = firstDay.getDay();
    
    const checkinData = Storage.getCheckinData();
    const today = new Date();
    const todayStr = Storage.getTodayString();
    
    const days = [];
    
    // 上月填充
    const prevMonthLastDay = new Date(year, month - 1, 0).getDate();
    for (let i = startWeekday - 1; i >= 0; i--) {
      days.push({
        day: prevMonthLastDay - i,
        type: 'other-month',
        date: null
      });
    }
    
    // 当月天数
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const dateObj = new Date(year, month - 1, d);
      
      let type = 'normal';
      
      if (dateStr === todayStr) {
        type = 'today';
      } else if (dateObj > today) {
        type = 'future';
      } else if (checkinData[dateStr]?.completed) {
        type = 'checked';
      } else if (dateObj < today) {
        // 检查是否是学习开始后的日期
        const study = Storage.getStudyData();
        const startDate = new Date(study.startDate);
        if (dateObj >= startDate) {
          type = 'missed';
        }
      }
      
      days.push({
        day: d,
        type,
        date: dateStr,
        record: checkinData[dateStr] || null
      });
    }
    
    // 下月填充
    const remainingDays = 42 - days.length; // 6行 x 7列
    for (let i = 1; i <= remainingDays; i++) {
      days.push({
        day: i,
        type: 'other-month',
        date: null
      });
    }
    
    return days;
  },

  /**
   * 获取月度统计
   * @param {number} year - 年份
   * @param {number} month - 月份
   * @returns {Object} 统计数据
   */
  getMonthlyStats(year, month) {
    const checkinData = Storage.getCheckinData();
    const today = new Date();
    
    let checkedDays = 0;
    let missedDays = 0;
    let totalStudyTime = 0;
    
    const daysInMonth = new Date(year, month, 0).getDate();
    
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = `${year}-${String(month).padStart(2, '0')}-${String(d).padStart(2, '0')}`;
      const dateObj = new Date(year, month - 1, d);
      
      if (dateObj <= today) {
        if (checkinData[dateStr]?.completed) {
          checkedDays++;
          totalStudyTime += checkinData[dateStr].studyTime || 0;
        } else {
          // 检查是否是学习开始后
          const study = Storage.getStudyData();
          const startDate = new Date(study.startDate);
          if (dateObj >= startDate) {
            missedDays++;
          }
        }
      }
    }
    
    return {
      checkedDays,
      missedDays,
      totalStudyTime,
      completionRate: checkedDays + missedDays > 0 
        ? Math.round((checkedDays / (checkedDays + missedDays)) * 100) 
        : 0
    };
  },

  /**
   * 获取今日学习时长
   * @returns {number} 分钟数
   */
  getTodayStudyTime() {
    const todayRecord = Storage.getCheckinByDate(Storage.getTodayString());
    return todayRecord?.studyTime || 0;
  },

  /**
   * 格式化时长显示
   * @param {number} minutes - 分钟数
   * @returns {string}
   */
  formatStudyTime(minutes) {
    if (minutes < 60) {
      return `${minutes}分钟`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`;
  }
};
