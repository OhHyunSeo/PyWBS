/**
 * 노션 스타일 간트 차트 렌더링 기능
 */

class NotionGanttChart {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
    }
    
    /**
     * 태스크 데이터를 기반으로 간트 차트 렌더링
     * @param {Array} tasks - 태스크 배열
     */
    render(tasks) {
        if (!this.container) {
            console.error('간트 차트 컨테이너를 찾을 수 없습니다.');
            return;
        }
        
        if (!tasks || tasks.length === 0) {
            this.container.innerHTML = '<div class="text-center py-4"><p class="text-muted">프로젝트에 태스크가 없습니다. 태스크를 추가하여 간트 차트를 확인해보세요.</p></div>';
            return;
        }
        
        // 태스크 데이터 유효성 검사
        let validTasks = tasks.filter(task => {
            return task && task.title && (task.startDate || task.endDate);
        });
        
        if (validTasks.length === 0) {
            this.container.innerHTML = '<div class="text-center py-4"><p class="text-muted">유효한 태스크 데이터가 없습니다. 시작일과 종료일이 설정된 태스크를 추가해주세요.</p></div>';
            return;
        }
        
        // 날짜 변환 함수
        const parseDate = (dateStr) => {
            if (!dateStr) return new Date();
            try {
                return new Date(dateStr);
            } catch (e) {
                console.error('날짜 변환 오류:', dateStr, e);
                return new Date();
            }
        };
        
        // 날짜 범위 계산
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        let minDate = today;
        let maxDate = today;
        
        validTasks.forEach(task => {
            const startDate = task.startDate ? parseDate(task.startDate) : today;
            const endDate = task.endDate ? parseDate(task.endDate) : today;
            
            if (startDate < minDate) minDate = startDate;
            if (endDate > maxDate) maxDate = endDate;
        });
        
        // 여유 기간 추가 (3일)
        minDate = new Date(minDate);
        minDate.setDate(minDate.getDate() - 3);
        maxDate = new Date(maxDate);
        maxDate.setDate(maxDate.getDate() + 3);
        
        // 날짜 범위가 너무 좁으면 확장
        if (minDate.getTime() === maxDate.getTime()) {
            minDate.setDate(minDate.getDate() - 7);
            maxDate.setDate(maxDate.getDate() + 7);
        }
        
        // 날짜 배열 생성
        const dateRange = [];
        const tempDate = new Date(minDate);
        
        while (tempDate <= maxDate) {
            dateRange.push(new Date(tempDate));
            tempDate.setDate(tempDate.getDate() + 1);
        }
        
        // 간트 차트 스타일 추가
        this.addGanttStyles();
        
        // 간트 차트 HTML 구조 생성
        let ganttHTML = `
            <div class="notion-gantt-wrapper">
                <div class="notion-gantt-timeline">
                    <div class="notion-gantt-header">
                        <div class="notion-gantt-task-info notion-gantt-header-label">
                            Task
                        </div>
        `;
        
        // 날짜 헤더 생성 - 형식 개선
        dateRange.forEach(date => {
            const isWeekend = date.getDay() === 0 || date.getDay() === 6;
            const isToday = date.toDateString() === today.toDateString();
            
            // 날짜, 월 표시의 포맷 통일
            const day = date.getDate();
            // 한국어 월 표시 
            const month = date.getMonth() + 1 + '월';
            
            ganttHTML += `
                <div class="notion-gantt-day ${isWeekend ? 'weekend' : ''} ${isToday ? 'today' : ''}">
                    <span class="notion-gantt-day-label">${day}</span>
                    <span class="notion-gantt-month-label">${month}</span>
                </div>
            `;
        });
        
        ganttHTML += `
                    </div>
                    <div class="notion-gantt-body">
        `;
        
        // 태스크를 계층 구조로 정렬
        const rootTasks = validTasks.filter(task => !task.parentId);
        
        // 모든 태스크 행 생성
        ganttHTML += this.generateTaskRows(rootTasks, validTasks, dateRange, today);
        ganttHTML += `
                    </div>
                </div>
            </div>
        `;
        
        // 간트 차트 HTML 삽입
        this.container.innerHTML = ganttHTML;
        
        // 간트 차트 이벤트 리스너 추가
        this.addEventListeners();
    }
    
    /**
     * 태스크 행 HTML 생성
     * @param {Array} tasksList - 부모 태스크 목록
     * @param {Array} allTasks - 전체 태스크 목록
     * @param {Array} dateRange - 날짜 범위
     * @param {Date} today - 오늘 날짜
     * @param {Number} level - 현재 깊이 레벨
     * @returns {String} HTML 문자열
     */
    generateTaskRows(tasksList, allTasks, dateRange, today, level = 0) {
        let rowsHTML = '';
        
        tasksList.forEach(task => {
            // 태스크 정보 표시
            rowsHTML += `
                <div class="notion-gantt-task-row" data-task-id="${task.id}">
                    <div class="notion-gantt-task-info ${level > 0 ? 'notion-gantt-subtask level-' + level : ''}">
                        <div class="notion-gantt-task-title">${task.title}</div>
                    </div>
                    <div class="notion-gantt-timeline-section">
            `;
            
            // 요일 구분선 표시
            dateRange.forEach((date, index) => {
                const isWeekend = date.getDay() === 0 || date.getDay() === 6;
                const isToday = date.toDateString() === today.toDateString();
                
                if (isWeekend) {
                    const left = index * 30;
                    rowsHTML += `
                        <div class="notion-gantt-day-column weekend" style="left: ${left}px;"></div>
                    `;
                }
                
                if (isToday) {
                    const left = index * 30 + 15;
                    rowsHTML += `
                        <div class="notion-gantt-today-line" style="left: ${left}px;"></div>
                    `;
                }
            });
            
            // 태스크 바 생성
            if (task.startDate && task.endDate) {
                try {
                    const startDate = new Date(task.startDate);
                    const endDate = new Date(task.endDate);
                    
                    const startIndex = dateRange.findIndex(date => 
                        date.toDateString() === startDate.toDateString()
                    );
                    
                    const endIndex = dateRange.findIndex(date => 
                        date.toDateString() === endDate.toDateString()
                    );
                    
                    if (startIndex >= 0 && endIndex >= 0) {
                        const left = startIndex * 30;
                        const width = (endIndex - startIndex + 1) * 30;
                        
                        rowsHTML += `
                            <div class="notion-gantt-bar ${task.status || 'not_started'}" style="left: ${left}px; width: ${width}px;">
                                <div class="notion-gantt-progress-bar" style="width: ${task.progress || 0}%;"></div>
                                <div class="notion-gantt-bar-label">${task.title}</div>
                            </div>
                        `;
                    }
                } catch (e) {
                    console.error('태스크 바 생성 오류:', task, e);
                }
            }
            
            rowsHTML += `
                    </div>
                </div>
            `;
            
            // 하위 태스크 처리
            const childTasks = allTasks.filter(t => t.parentId === task.id);
            if (childTasks.length > 0) {
                rowsHTML += this.generateTaskRows(childTasks, allTasks, dateRange, today, level + 1);
            }
        });
        
        return rowsHTML;
    }
    
    /**
     * 간트 차트 스타일을 동적으로 추가
     */
    addGanttStyles() {
        if (document.getElementById('notion-gantt-styles')) return;
        
        const styleElement = document.createElement('style');
        styleElement.id = 'notion-gantt-styles';
        styleElement.textContent = `
            .notion-gantt-wrapper {
                width: 100%;
                overflow-x: auto;
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                margin-bottom: 2rem;
            }
            .notion-gantt-timeline {
                display: flex;
                flex-direction: column;
                min-width: 100%;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                overflow: hidden;
            }
            .notion-gantt-header {
                display: flex;
                border-bottom: 1px solid #e0e0e0;
                background-color: #f9f9f9;
                position: sticky;
                top: 0;
                z-index: 10;
            }
            .notion-gantt-header-label {
                font-weight: 600;
                color: #333;
                background-color: #f9f9f9;
            }
            .notion-gantt-day {
                min-width: 30px;
                width: 30px;
                height: 48px;
                text-align: center;
                border-right: 1px solid #f0f0f0;
                padding: 2px 0;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
            }
            .notion-gantt-day-label {
                font-size: 14px;
                font-weight: 500;
                color: #333;
                line-height: 1.2;
                display: block;
                margin-bottom: 2px;
            }
            .notion-gantt-month-label {
                font-size: 11px;
                color: #888;
                line-height: 1.2;
                display: block;
            }
            .notion-gantt-day.weekend {
                background-color: #f5f5f5;
            }
            .notion-gantt-day.today .notion-gantt-day-label {
                color: #0366d6;
                font-weight: 700;
            }
            .notion-gantt-day.today {
                background-color: rgba(3, 102, 214, 0.05);
            }
            .notion-gantt-body {
                max-height: 500px;
                overflow-y: auto;
            }
            .notion-gantt-task-row {
                display: flex;
                position: relative;
                border-bottom: 1px solid #f0f0f0;
                min-height: 40px;
            }
            .notion-gantt-task-row:hover {
                background-color: #f9f9f9;
            }
            .notion-gantt-task-info {
                width: 250px;
                min-width: 250px;
                padding: 8px 15px;
                position: sticky;
                left: 0;
                background: white;
                z-index: 5;
                border-right: 1px solid #e0e0e0;
                display: flex;
                align-items: center;
            }
            .notion-gantt-task-title {
                font-size: 14px;
                font-weight: 500;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }
            .notion-gantt-subtask {
                padding-left: 30px;
                background-color: #fafafa;
            }
            .notion-gantt-subtask.level-2 {
                padding-left: 50px;
                background-color: #f7f7f7;
            }
            .notion-gantt-timeline-section {
                position: relative;
                display: flex;
                flex: 1;
                min-width: 0;
                height: 100%;
            }
            .notion-gantt-day-column {
                position: absolute;
                width: 30px;
                height: 100%;
                z-index: 1;
            }
            .notion-gantt-day-column.weekend {
                background-color: #f5f5f5;
            }
            .notion-gantt-today-line {
                position: absolute;
                width: 2px;
                height: 100%;
                background-color: #0366d6;
                z-index: 2;
            }
            .notion-gantt-bar {
                position: absolute;
                height: 24px;
                top: 8px;
                border-radius: 4px;
                z-index: 3;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }
            .notion-gantt-bar.not_started {
                background-color: #f0f0f0;
                border: 1px solid #ddd;
            }
            .notion-gantt-bar.in_progress {
                background-color: #fff8e6;
                border: 1px solid #ffd166;
            }
            .notion-gantt-bar.completed {
                background-color: #e3fcef;
                border: 1px solid #0ca678;
            }
            .notion-gantt-bar.blocked {
                background-color: #ffebee;
                border: 1px solid #f44336;
            }
            .notion-gantt-progress-bar {
                position: absolute;
                height: 100%;
                top: 0;
                left: 0;
                background-color: rgba(0, 0, 0, 0.1);
                z-index: 1;
            }
            .notion-gantt-bar.completed .notion-gantt-progress-bar {
                background-color: rgba(10, 128, 67, 0.2);
            }
            .notion-gantt-bar.in_progress .notion-gantt-progress-bar {
                background-color: rgba(255, 209, 102, 0.3);
            }
            .notion-gantt-bar.blocked .notion-gantt-progress-bar {
                background-color: rgba(244, 67, 54, 0.2);
            }
            .notion-gantt-bar-label {
                position: relative;
                padding: 4px 8px;
                font-size: 12px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                z-index: 2;
            }
        `;
        
        document.head.appendChild(styleElement);
    }
    
    /**
     * 간트 차트에 이벤트 리스너 추가
     */
    addEventListeners() {
        // 미래 기능을 위한 자리 표시자
    }
}

// 간트 차트 초기화 및 탭 변경 감지
document.addEventListener('DOMContentLoaded', function() {
    const ganttTab = document.querySelector('a[href="#gantt"]');
    const ganttContainer = document.getElementById('notion-gantt');
    
    // 간트 차트가 페이지에 존재하는 경우에만 처리
    if (ganttContainer) {
        const ganttChart = new NotionGanttChart('notion-gantt');
        
        // 디버그 요소 확인
        const debugElement = document.getElementById('gantt-debug');
        
        // JSON 데이터 가져오기 (여러 소스에서 시도)
        let tasksJson;
        
        // 디버그 요소에서 먼저 시도
        if (debugElement && debugElement.textContent) {
            console.log('디버그 요소에서 태스크 데이터 가져오기 시도');
            tasksJson = debugElement.textContent.trim();
        } 
        // 그 다음 data-tasks 속성에서 시도
        else if (ganttContainer.hasAttribute('data-tasks')) {
            console.log('data-tasks 속성에서 태스크 데이터 가져오기 시도');
            tasksJson = ganttContainer.getAttribute('data-tasks');
        }
        
        if (tasksJson) {
            try {
                console.log('간트 차트 데이터 처리 시작');
                
                // 데이터 파싱 시도
                let tasks;
                
                try {
                    // 기본 JSON 파싱 먼저 시도
                    tasks = JSON.parse(tasksJson);
                    console.log('기본 JSON 파싱 성공');
                } catch (error) {
                    console.warn('기본 JSON 파싱 실패, 대체 방법 시도...', error);
                    
                    // HTML 이스케이프 문자 제거
                    const textArea = document.createElement('textarea');
                    textArea.innerHTML = tasksJson;
                    const decodedJson = textArea.value;
                    
                    try {
                        tasks = JSON.parse(decodedJson);
                        console.log('HTML 디코딩 후 JSON 파싱 성공');
                    } catch (error2) {
                        console.error('모든 JSON 파싱 시도 실패', error2);
                        throw new Error('JSON 데이터를 파싱할 수 없습니다: ' + error2.message);
                    }
                }
                
                if (!tasks || !Array.isArray(tasks)) {
                    console.error('파싱된 데이터가 배열이 아님:', tasks);
                    throw new Error('유효한 태스크 배열이 아닙니다');
                }
                
                if (tasks.length === 0) {
                    console.warn('태스크 배열이 비어 있습니다');
                    ganttContainer.innerHTML = `
                        <div class="alert alert-info">
                            <strong>표시할 태스크가 없습니다.</strong>
                            <p class="mb-0">태스크를 추가하고 시작일과 종료일을 설정해주세요.</p>
                        </div>
                    `;
                    return;
                }
                
                console.log('태스크 데이터 파싱 성공:', tasks.length + '개 항목');
                
                // 탭 변경 시 간트 차트 렌더링
                if (ganttTab) {
                    ganttTab.addEventListener('shown.bs.tab', function() {
                        ganttChart.render(tasks);
                    });
                }
                
                // 초기 탭이 간트 차트인 경우 바로 렌더링
                if (document.querySelector('.tab-pane.active#gantt')) {
                    ganttChart.render(tasks);
                } else if (ganttTab) {
                    // 부트스트랩 탭 초기화 지연 문제를 위한 타임아웃
                    setTimeout(() => {
                        if (document.querySelector('.tab-pane.active#gantt')) {
                            ganttChart.render(tasks);
                        }
                    }, 500);
                }
            } catch (error) {
                console.error('간트 차트 데이터 파싱 오류:', error);
                console.error('원본 데이터:', tasksJson);
                ganttContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <strong>간트 차트 데이터를 불러오는 중 오류가 발생했습니다.</strong>
                        <p class="mb-0 mt-2">오류 내용: ${error.message}</p>
                        <p class="small mt-2">브라우저 콘솔(F12)에서 자세한 오류 정보를 확인하세요.</p>
                        <div class="mt-3">
                            <button class="btn btn-sm btn-outline-secondary" onclick="document.getElementById('gantt-error-details').style.display='block'">디버그 정보 보기</button>
                            <div id="gantt-error-details" style="display:none; margin-top:10px; padding:10px; background:#f8f9fa; border-radius:4px; font-family:monospace; font-size:12px; overflow:auto; max-height:200px; white-space:pre-wrap;">
                            태스크 데이터: ${JSON.stringify(tasksJson).substring(0, 500)}...
                            </div>
                        </div>
                    </div>
                `;
            }
        } else {
            ganttContainer.innerHTML = `
                <div class="alert alert-warning">
                    <strong>간트 차트 데이터가 없습니다.</strong>
                    <p class="mb-0">태스크를 추가하고 시작일/종료일을 설정해주세요.</p>
                </div>
            `;
        }
    }
}); 