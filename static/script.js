/**
 * Text2PPT Frontend JavaScript
 * Clean, modern interface for PPT generation
 */

// DOM Elements
const userInput = document.getElementById('user-input');
const submitBtn = document.getElementById('submit-btn');
const modalOverlay = document.getElementById('modal-overlay');
const resultModal = document.getElementById('result-modal');
const progressFill = document.getElementById('progress-fill');
const progressText = document.getElementById('progress-text');
const resultInfo = document.getElementById('result-info');
const downloadBtn = document.getElementById('download-btn');
const closeResult = document.getElementById('close-result');

// State
let currentTaskId = null;
let selectedStyle = '科技涂鸦';
let currentSlides = 5;
let currentLang = '中文';
let currentRatio = '16:9';

// API Base URL
const API_BASE = '';

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initDropdowns();
    initStyleCards();
    initSuggestions();
    initTextarea();
});

// Auto-resize textarea
function initTextarea() {
    userInput.addEventListener('input', () => {
        userInput.style.height = 'auto';
        userInput.style.height = Math.min(userInput.scrollHeight, 150) + 'px';
    });

    // Ctrl+Enter to submit
    userInput.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'Enter') {
            e.preventDefault();
            handleSubmit();
        }
    });
}

// Initialize dropdowns
function initDropdowns() {
    // Slides dropdown
    document.querySelectorAll('#slides-dropdown .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            currentSlides = parseInt(item.dataset.value);
            document.getElementById('current-slides').textContent = currentSlides;
            document.querySelectorAll('#slides-dropdown .dropdown-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Language dropdown
    document.querySelectorAll('#lang-dropdown .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            currentLang = item.dataset.value;
            document.getElementById('current-lang').textContent = currentLang;
            document.querySelectorAll('#lang-dropdown .dropdown-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });

    // Ratio dropdown
    document.querySelectorAll('#ratio-dropdown .dropdown-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            currentRatio = item.dataset.value;
            document.getElementById('current-ratio').textContent = currentRatio;
            document.querySelectorAll('#ratio-dropdown .dropdown-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
        });
    });
}

// Initialize style cards
function initStyleCards() {
    document.querySelectorAll('.style-card').forEach(card => {
        card.addEventListener('click', () => {
            document.querySelectorAll('.style-card').forEach(c => c.classList.remove('active'));
            card.classList.add('active');
            selectedStyle = card.dataset.style;
        });
    });
}

// Initialize suggestion cards
function initSuggestions() {
    document.querySelectorAll('.suggestion-card').forEach(card => {
        card.addEventListener('click', () => {
            userInput.value = card.dataset.text;
            userInput.focus();
            userInput.style.height = 'auto';
            userInput.style.height = userInput.scrollHeight + 'px';
        });
    });
}

// Handle submit
submitBtn.addEventListener('click', handleSubmit);

async function handleSubmit() {
    const text = userInput.value.trim();
    if (!text) {
        userInput.focus();
        return;
    }

    // Disable button
    submitBtn.disabled = true;

    // Show progress modal
    showModal(modalOverlay);
    progressFill.style.width = '5%';
    progressText.textContent = '正在提交请求...';

    try {
        // Start generation
        const response = await fetch(`${API_BASE}/api/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                text: text,
                num_slides: currentSlides,
                language: currentLang,
                style: selectedStyle
            })
        });

        const data = await response.json();

        if (response.ok) {
            currentTaskId = data.task_id;
            pollStatus();
        } else {
            hideModal(modalOverlay);
            alert('错误：' + (data.error || '请求失败'));
            submitBtn.disabled = false;
        }
    } catch (error) {
        hideModal(modalOverlay);
        alert('网络错误：' + error.message);
        submitBtn.disabled = false;
    }
}

// Poll for status
async function pollStatus() {
    let progress = 10;

    const poll = async () => {
        try {
            const response = await fetch(`${API_BASE}/api/status/${currentTaskId}`);
            const data = await response.json();

            if (data.status === 'processing') {
                progress = Math.min(progress + 12, 85);
                progressFill.style.width = progress + '%';
                progressText.textContent = data.progress || '处理中...';
                setTimeout(poll, 2000);
            } else if (data.status === 'completed') {
                progressFill.style.width = '100%';
                progressText.textContent = '完成！';

                setTimeout(() => {
                    hideModal(modalOverlay);
                    showResult(data.result);
                }, 500);
            } else if (data.status === 'failed') {
                hideModal(modalOverlay);
                alert('生成失败：' + (data.error || '未知错误'));
                submitBtn.disabled = false;
            } else {
                setTimeout(poll, 1500);
            }
        } catch (error) {
            progressText.textContent = '连接中断，重试中...';
            setTimeout(poll, 3000);
        }
    };

    poll();
}

// Show result
function showResult(result) {
    resultInfo.innerHTML = `
        <p>已生成 <strong>${result.slides_count}</strong> 页演示文稿</p>
        <div class="slides-list">
            ${result.slides.map((s, i) => `
                <span class="slide-chip">${i + 1}. ${s.title}</span>
            `).join('')}
        </div>
    `;

    downloadBtn.onclick = () => {
        window.open(`${API_BASE}/api/download/${currentTaskId}`, '_blank');
    };

    showModal(resultModal);
    submitBtn.disabled = false;
}

// Close result modal
closeResult.addEventListener('click', () => {
    hideModal(resultModal);
});

resultModal.addEventListener('click', (e) => {
    if (e.target === resultModal) {
        hideModal(resultModal);
    }
});

// Modal helpers
function showModal(modal) {
    modal.classList.add('active');
}

function hideModal(modal) {
    modal.classList.remove('active');
}
