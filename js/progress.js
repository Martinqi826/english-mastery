/**
 * English Mastery - 进度计算模块
 */

const Progress = {
  // 等级定义
  LEVELS: {
    A1: { min: 0, max: 20, name: 'A1 入门', badge: 'level-a1' },
    A2: { min: 20, max: 40, name: 'A2 基础', badge: 'level-a2' },
    B1: { min: 40, max: 55, name: 'B1 中级', badge: 'level-b1' },
    B2: { min: 55, max: 70, name: 'B2 中高级', badge: 'level-b2' },
    C1: { min: 70, max: 85, name: 'C1 高级', badge: 'level-c1' },
    C2: { min: 85, max: 100, name: 'C2 精通', badge: 'level-c2' }
  },

  // 技能权重
  WEIGHTS: {
    vocabulary: 0.2,
    listening: 0.2,
    reading: 0.2,
    writing: 0.2,
    speaking: 0.2
  },

  // 技能名称映射
  SKILL_NAMES: {
    vocabulary: '词汇',
    listening: '听力',
    reading: '阅读',
    writing: '写作',
    speaking: '口语'
  },

  /**
   * 计算总体进度
   * @param {Object} skills - 各技能进度 { vocabulary: 40, listening: 35, ... }
   * @returns {number} 总体进度 0-100
   */
  calculateOverall(skills) {
    let total = 0;
    Object.keys(this.WEIGHTS).forEach(skill => {
      total += (skills[skill] || 0) * this.WEIGHTS[skill];
    });
    return Math.round(total);
  },

  /**
   * 获取当前等级
   * @param {number} progress - 进度值 0-100
   * @returns {Object} 等级信息
   */
  getLevel(progress) {
    for (const [key, level] of Object.entries(this.LEVELS)) {
      if (progress >= level.min && progress < level.max) {
        return { code: key, ...level };
      }
    }
    return { code: 'C2', ...this.LEVELS.C2 };
  },

  /**
   * 计算到达目标还需要多少进度
   * @param {number} current - 当前进度
   * @param {number} target - 目标进度
   * @returns {number}
   */
  getRemainingProgress(current, target = 85) {
    return Math.max(0, target - current);
  },

  /**
   * 计算预计完成天数
   * @param {number} currentProgress - 当前进度
   * @param {number} targetProgress - 目标进度
   * @param {number} dailyGain - 每日预计增长
   * @returns {number}
   */
  estimateDaysToComplete(currentProgress, targetProgress = 85, dailyGain = 2) {
    const remaining = this.getRemainingProgress(currentProgress, targetProgress);
    return Math.ceil(remaining / dailyGain);
  },

  /**
   * 根据学习活动增加进度
   * @param {string} skill - 技能名称
   * @param {string} activity - 活动类型
   * @returns {number} 增加的进度值
   */
  getActivityPoints(skill, activity) {
    const pointsMap = {
      vocabulary: {
        learn: 0.5,      // 学习新词
        review: 0.2,     // 复习
        test: 1          // 测试通过
      },
      listening: {
        listen: 0.5,     // 听一段材料
        complete: 1,     // 完成练习
        test: 1.5        // 测试通过
      },
      reading: {
        read: 0.5,       // 阅读文章
        complete: 1,     // 完成理解题
        test: 1.5        // 测试通过
      },
      writing: {
        practice: 1,     // 完成写作练习
        submit: 1.5,     // 提交作文
        test: 2          // 测试通过
      },
      speaking: {
        practice: 0.5,   // 口语练习
        record: 1,       // 录音练习
        test: 1.5        // 测试通过
      }
    };

    return pointsMap[skill]?.[activity] || 0.5;
  },

  /**
   * 计算 30 天学习计划的预期进度
   * @param {number} startProgress - 起始进度
   * @returns {Array} 每天的预期进度数组
   */
  generateExpectedProgress(startProgress = 40) {
    const schedule = [];
    let progress = startProgress;
    
    for (let day = 1; day <= 30; day++) {
      // 第一周：快速提升（每天 +2%）
      if (day <= 7) {
        progress += 2;
      }
      // 第二周：稳定提升（每天 +1.5%）
      else if (day <= 14) {
        progress += 1.5;
      }
      // 第三周：精细提升（每天 +1.2%）
      else if (day <= 21) {
        progress += 1.2;
      }
      // 第四周：冲刺阶段（每天 +1%）
      else {
        progress += 1;
      }
      
      schedule.push({
        day,
        expectedProgress: Math.min(95, Math.round(progress))
      });
    }
    
    return schedule;
  },

  /**
   * 获取进度条颜色
   * @param {number} progress - 进度值
   * @returns {string} 颜色类名
   */
  getProgressColor(progress) {
    if (progress < 40) return 'progress-low';
    if (progress < 60) return 'progress-medium';
    if (progress < 80) return 'progress-high';
    return 'progress-complete';
  },

  /**
   * 格式化进度显示
   * @param {number} progress - 进度值
   * @param {boolean} showLevel - 是否显示等级
   * @returns {string}
   */
  formatProgress(progress, showLevel = false) {
    if (showLevel) {
      const level = this.getLevel(progress);
      return `${progress}% (${level.name})`;
    }
    return `${progress}%`;
  },

  /**
   * 获取技能提升建议
   * @param {Object} skills - 各技能进度
   * @returns {Array} 建议列表
   */
  getSuggestions(skills) {
    const suggestions = [];
    const sortedSkills = Object.entries(skills)
      .filter(([key]) => key !== 'overall')
      .sort((a, b) => a[1] - b[1]);

    // 找出最弱的技能
    const weakest = sortedSkills.slice(0, 2);
    weakest.forEach(([skill, value]) => {
      suggestions.push({
        skill,
        name: this.SKILL_NAMES[skill],
        value,
        message: `${this.SKILL_NAMES[skill]}是当前最薄弱的环节，建议重点加强`
      });
    });

    return suggestions;
  },

  /**
   * 计算完成率
   * @param {number} completed - 已完成数量
   * @param {number} total - 总数量
   * @returns {number} 百分比
   */
  calculateCompletionRate(completed, total) {
    if (total === 0) return 0;
    return Math.round((completed / total) * 100);
  },

  /**
   * 获取激励消息
   * @param {number} progress - 当前进度
   * @param {number} streak - 连续打卡天数
   * @returns {string}
   */
  getMotivationMessage(progress, streak) {
    const messages = {
      low: [
        '千里之行，始于足下！继续加油！💪',
        '每天进步一点点，终将达到目标！🎯',
        '坚持就是胜利，你已经开始了！🚀'
      ],
      medium: [
        '太棒了！你已经完成了一半的旅程！🎉',
        '进步明显，继续保持这个势头！⭐',
        '你正在变得越来越强！💪'
      ],
      high: [
        '即将到达终点，最后的冲刺！🏃‍♂️',
        '胜利在望，不要放弃！🏆',
        '你已经是英语高手了！👏'
      ],
      complete: [
        '恭喜！你已经达到了母语水平！🎊',
        '完美！你是真正的英语大师！👑',
        '目标达成！你太棒了！🥇'
      ]
    };

    // 根据连续打卡加成消息
    let streakBonus = '';
    if (streak >= 7) {
      streakBonus = ` 连续学习${streak}天，太厉害了！🔥`;
    } else if (streak >= 3) {
      streakBonus = ` 已连续${streak}天，继续保持！`;
    }

    let category;
    if (progress < 40) category = 'low';
    else if (progress < 70) category = 'medium';
    else if (progress < 90) category = 'high';
    else category = 'complete';

    const randomIndex = Math.floor(Math.random() * messages[category].length);
    return messages[category][randomIndex] + streakBonus;
  }
};
