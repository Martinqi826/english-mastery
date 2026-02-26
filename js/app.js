/**
 * English Mastery - 主应用逻辑
 */

// ==================== 全局状态 ====================
let radarChart = null;

// ==================== 初始化 ====================
document.addEventListener('DOMContentLoaded', function() {
  initApp();
});

function initApp() {
  // 初始化存储
  Storage.initializeStudy();
  
  // 更新UI
  updateDayBadge();
  updateProgress();
  updateStats();
  updateTaskList();
  updateCheckinButton();
  updateCalendar();
  initRadarChart();
  
  // 初始化社区统计
  initCommunityStats();
  
  console.log('English Mastery 初始化完成');
}

// ==================== UI 更新函数 ====================

/**
 * 更新天数徽章
 */
function updateDayBadge() {
  const currentDay = Storage.getCurrentDay();
  const dayBadge = document.getElementById('dayBadge');
  if (dayBadge) {
    dayBadge.textContent = `Day ${currentDay} / 30`;
  }
}

/**
 * 更新进度显示
 */
function updateProgress() {
  const progress = Storage.getProgress();
  const overall = progress.overall || 40;
  
  // 更新进度条
  const progressFill = document.getElementById('progressFill');
  const overallProgress = document.getElementById('overallProgress');
  
  if (progressFill) {
    progressFill.style.width = `${overall}%`;
  }
  if (overallProgress) {
    overallProgress.textContent = `${overall}%`;
  }
  
  // 更新等级徽章
  const level = Progress.getLevel(overall);
  const levelBadge = document.getElementById('levelBadge');
  if (levelBadge) {
    levelBadge.textContent = level.name;
    levelBadge.className = `level-badge ${level.badge}`;
  }
}

/**
 * 更新统计数据
 */
function updateStats() {
  const study = Storage.getStudyData();
  const streak = Storage.calculateStreak();
  const todayTasks = Storage.getTodayTasks();
  
  // 连续打卡天数
  const streakDays = document.getElementById('streakDays');
  const streakDisplay = document.getElementById('streakDisplay');
  if (streakDays) streakDays.textContent = streak;
  if (streakDisplay) streakDisplay.textContent = streak;
  
  // 今日完成任务
  const todayTasksEl = document.getElementById('todayTasks');
  if (todayTasksEl) {
    todayTasksEl.textContent = `${todayTasks.length}/5`;
  }
  
  // 已学词汇
  const wordsLearned = document.getElementById('wordsLearned');
  if (wordsLearned) {
    wordsLearned.textContent = study.wordsLearned || 0;
  }
  
  // 累计学习时长
  const totalTime = document.getElementById('totalTime');
  if (totalTime) {
    const hours = Math.round((study.totalTime || 0) / 60);
    totalTime.textContent = `${hours}h`;
  }
  
  // 今日学习时长
  const todayTime = document.getElementById('todayTime');
  if (todayTime) {
    todayTime.textContent = Checkin.getTodayStudyTime();
  }
}

// 任务按钮文字配置
const TASK_BUTTON_TEXT = {
  vocabulary: { default: '开始学习', completed: '强化复习' },
  listening: { default: '开始学习', completed: '再听一遍' },
  reading: { default: '开始学习', completed: '重读巩固' },
  writing: { default: '开始学习', completed: '继续练习' },
  test: { default: '开始测验', completed: '重新测验' }
};

/**
 * 更新任务列表
 */
function updateTaskList() {
  const completedTasks = Storage.getTodayTasks();
  const taskItems = document.querySelectorAll('.task-item');
  
  taskItems.forEach(item => {
    const taskId = item.dataset.task;
    const checkbox = item.querySelector('.task-checkbox');
    const taskBtn = document.getElementById(`taskBtn-${taskId}`);
    const isCompleted = completedTasks.includes(taskId);
    
    if (isCompleted) {
      item.classList.add('completed');
      checkbox.classList.add('checked');
      // 更新按钮文字
      if (taskBtn && TASK_BUTTON_TEXT[taskId]) {
        taskBtn.textContent = TASK_BUTTON_TEXT[taskId].completed;
      }
    } else {
      item.classList.remove('completed');
      checkbox.classList.remove('checked');
      // 恢复默认按钮文字
      if (taskBtn && TASK_BUTTON_TEXT[taskId]) {
        taskBtn.textContent = TASK_BUTTON_TEXT[taskId].default;
      }
    }
  });
  
  // 更新任务进度显示
  const taskProgress = document.getElementById('taskProgress');
  if (taskProgress) {
    taskProgress.textContent = `${completedTasks.length}/5 完成`;
  }
}

/**
 * 更新打卡按钮状态
 */
function updateCheckinButton() {
  const btn = document.getElementById('checkinBtn');
  const hint = document.getElementById('checkinHint');
  
  if (!btn) return;
  
  const isCheckedIn = Storage.isTodayCheckedIn();
  const check = Checkin.checkCanCheckin();
  
  if (isCheckedIn) {
    btn.textContent = '✅ 今日已打卡';
    btn.classList.add('checked');
    btn.disabled = true;
    if (hint) hint.textContent = '明天继续加油！';
  } else if (check.canCheckin) {
    btn.textContent = '✅ 完成今日打卡';
    btn.classList.remove('checked');
    btn.disabled = false;
    if (hint) hint.textContent = '已满足打卡条件，点击打卡！';
  } else {
    btn.textContent = '✅ 完成今日打卡';
    btn.classList.remove('checked');
    btn.disabled = true;
    if (hint) hint.textContent = `还需完成 ${Checkin.MIN_TASKS_REQUIRED - check.completedTasks} 项任务`;
  }
}

/**
 * 更新日历
 */
function updateCalendar() {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1;
  
  // 更新月份显示
  const currentMonth = document.getElementById('currentMonth');
  if (currentMonth) {
    currentMonth.textContent = `${year}年${month}月`;
  }
  
  // 生成日历天数
  const calendarDays = document.getElementById('calendarDays');
  if (!calendarDays) return;
  
  const days = Checkin.generateCalendarDays(year, month);
  
  calendarDays.innerHTML = days.map(day => `
    <div class="calendar-day ${day.type}" data-date="${day.date || ''}">
      ${day.day}
    </div>
  `).join('');
}

/**
 * 初始化雷达图
 */
function initRadarChart() {
  const canvas = document.getElementById('radarChart');
  if (!canvas) return;
  
  const progress = Storage.getProgress();
  
  const data = {
    labels: ['词汇', '听力', '阅读', '写作', '口语'],
    datasets: [{
      label: '当前水平',
      data: [
        progress.vocabulary || 40,
        progress.listening || 35,
        progress.reading || 38,
        progress.writing || 32,
        progress.speaking || 30
      ],
      fill: true,
      backgroundColor: 'rgba(79, 70, 229, 0.2)',
      borderColor: 'rgb(79, 70, 229)',
      pointBackgroundColor: 'rgb(79, 70, 229)',
      pointBorderColor: '#fff',
      pointHoverBackgroundColor: '#fff',
      pointHoverBorderColor: 'rgb(79, 70, 229)'
    }, {
      label: '目标水平',
      data: [85, 85, 85, 85, 85],
      fill: false,
      borderColor: 'rgba(16, 185, 129, 0.5)',
      borderDash: [5, 5],
      pointRadius: 0
    }]
  };

  const config = {
    type: 'radar',
    data: data,
    options: {
      responsive: true,
      maintainAspectRatio: true,
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 0,
          suggestedMax: 100,
          ticks: {
            stepSize: 20,
            font: {
              size: 10
            }
          },
          pointLabels: {
            font: {
              size: 12
            }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    }
  };

  if (radarChart) {
    radarChart.destroy();
  }
  
  radarChart = new Chart(canvas, config);
}

/**
 * 更新雷达图数据
 */
function updateRadarChart() {
  if (!radarChart) return;
  
  const progress = Storage.getProgress();
  radarChart.data.datasets[0].data = [
    progress.vocabulary || 40,
    progress.listening || 35,
    progress.reading || 38,
    progress.writing || 32,
    progress.speaking || 30
  ];
  radarChart.update();
}

// ==================== 交互函数 ====================

/**
 * 切换任务完成状态
 * @param {string} taskId - 任务ID
 */
function toggleTask(taskId) {
  const result = Checkin.toggleTask(taskId);
  
  // 更新UI
  updateTaskList();
  updateStats();
  updateCheckinButton();
  
  // 显示提示
  if (result.completed) {
    showToast(`✅ ${Checkin.TASK_NAMES[taskId]} 已完成！`, 'success');
    
    // 记录用户完成任务（用于社区统计）
    recordTaskCompletion();
    
    // 更新社区统计显示
    updateCommunityStats();
    
    // 模拟增加学习时长
    Storage.addStudyTime(15);
    
    // 如果是词汇任务，增加词汇数
    if (taskId === 'vocabulary') {
      Storage.addWordsLearned(30);
    }
  }
  
  // 检查是否可以打卡
  if (result.canCheckin && !Storage.isTodayCheckedIn()) {
    showToast('🎉 已满足打卡条件，可以打卡了！');
  }
}

/**
 * 执行打卡
 */
function doCheckin() {
  const result = Checkin.doCheckin();
  
  if (result.success) {
    showToast(result.message, 'success');
    
    // 更新所有UI
    updateProgress();
    updateStats();
    updateTaskList();
    updateCheckinButton();
    updateCalendar();
    updateRadarChart();
    
    // 播放庆祝动画
    celebrateCheckin();
  } else {
    showToast(result.message, 'error');
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
 * 打卡成功庆祝动画
 */
function celebrateCheckin() {
  const btn = document.getElementById('checkinBtn');
  if (btn) {
    btn.classList.add('animate-pulse');
    setTimeout(() => {
      btn.classList.remove('animate-pulse');
    }, 2000);
  }
}

// ==================== 工具函数 ====================

/**
 * 重置所有数据（调试用）
 */
function resetAllData() {
  Storage.resetAll();
}

/**
 * 模拟完成所有任务（调试用）
 */
function simulateCompleteTasks() {
  Checkin.ALL_TASKS.forEach(task => {
    if (!Storage.getTodayTasks().includes(task)) {
      Checkin.toggleTask(task);
    }
  });
  updateTaskList();
  updateStats();
  updateCheckinButton();
}

// ==================== 导出调试接口 ====================
window.EM = {
  Storage,
  Progress,
  Checkin,
  resetAllData,
  simulateCompleteTasks,
  showToast
};

// ==================== 社区统计功能 ====================

/**
 * 初始化社区统计
 */
function initCommunityStats() {
  // 记录本次访问（UV统计）
  recordVisit();
  
  // 更新显示
  updateCommunityStats();
  
  // 每30秒更新一次数据
  setInterval(updateCommunityStats, 30000);
}

/**
 * 获取今日日期字符串
 */
function getTodayDateString() {
  const now = new Date();
  return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`;
}

/**
 * 获取或创建用户唯一ID
 */
function getUserId() {
  let visitorId = localStorage.getItem('em_visitor_id');
  if (!visitorId) {
    // 生成一个简单的唯一ID
    visitorId = 'v_' + Date.now().toString(36) + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('em_visitor_id', visitorId);
  }
  return visitorId;
}

/**
 * 记录用户访问（UV统计）
 */
function recordVisit() {
  const today = getTodayDateString();
  const visitorId = getUserId();
  
  // 获取今日访问记录
  let visitData = JSON.parse(localStorage.getItem('em_visit_data') || '{}');
  
  // 如果不是今天的数据，重置
  if (visitData.date !== today) {
    visitData = {
      date: today,
      visitors: [],
      completedUsers: []
    };
  }
  
  // 记录当前访客
  if (!visitData.visitors.includes(visitorId)) {
    visitData.visitors.push(visitorId);
  }
  
  localStorage.setItem('em_visit_data', JSON.stringify(visitData));
}

/**
 * 记录用户完成任务（完成学习统计）
 * 当用户完成任意一项任务时调用此函数
 */
function recordTaskCompletion() {
  const today = getTodayDateString();
  const visitorId = getUserId();
  
  // 获取今日访问记录
  let visitData = JSON.parse(localStorage.getItem('em_visit_data') || '{}');
  
  // 如果不是今天的数据，重置
  if (visitData.date !== today) {
    visitData = {
      date: today,
      visitors: [visitorId],
      completedUsers: []
    };
  }
  
  // 记录完成学习的用户
  if (!visitData.completedUsers.includes(visitorId)) {
    visitData.completedUsers.push(visitorId);
  }
  
  localStorage.setItem('em_visit_data', JSON.stringify(visitData));
}

/**
 * 更新社区统计数据
 * 基于真实的本地用户行为数据
 */
function updateCommunityStats() {
  const today = getTodayDateString();
  const now = new Date();
  
  // 获取今日访问数据
  let visitData = JSON.parse(localStorage.getItem('em_visit_data') || '{}');
  
  // 如果不是今天的数据，显示初始值
  if (visitData.date !== today) {
    visitData = {
      date: today,
      visitors: [],
      completedUsers: []
    };
  }
  
  // 参与学习人数 = 今日UV
  const learningCount = visitData.visitors.length;
  
  // 完成学习人数 = 完成任意任务的用户数
  const completedCount = visitData.completedUsers.length;
  
  // 计算完成率
  const completionRate = learningCount > 0 ? Math.round((completedCount / learningCount) * 100) : 0;
  
  // 更新UI
  animateNumber('completedCount', completedCount);
  animateNumber('learningCount', learningCount);
  
  // 更新进度条
  const progressFill = document.getElementById('communityProgressFill');
  const rateDisplay = document.getElementById('completionRate');
  if (progressFill) {
    progressFill.style.width = `${completionRate}%`;
  }
  if (rateDisplay) {
    rateDisplay.textContent = `${completionRate}%`;
  }
  
  // 更新时间
  const updateTime = document.getElementById('updateTime');
  if (updateTime) {
    updateTime.textContent = `${now.getHours().toString().padStart(2, '0')}:${now.getMinutes().toString().padStart(2, '0')} 更新`;
  }
}

/**
 * 数字动画效果
 * @param {string} elementId - 元素ID
 * @param {number} targetValue - 目标值
 */
function animateNumber(elementId, targetValue) {
  const element = document.getElementById(elementId);
  if (!element) return;
  
  const currentValue = parseInt(element.textContent) || 0;
  const diff = targetValue - currentValue;
  const duration = 1000; // 动画时长1秒
  const steps = 30;
  const stepValue = diff / steps;
  let currentStep = 0;
  
  const timer = setInterval(() => {
    currentStep++;
    const newValue = Math.round(currentValue + stepValue * currentStep);
    element.textContent = newValue.toLocaleString();
    
    if (currentStep >= steps) {
      clearInterval(timer);
      element.textContent = targetValue.toLocaleString();
    }
  }, duration / steps);
}
