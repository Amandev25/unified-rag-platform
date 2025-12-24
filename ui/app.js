// API Configuration
// Change this if your API is running on a different URL
const API_BASE_URL = 'http://localhost:8000';

// Page Management
function showPage(pageId) {
    document.querySelectorAll('.page').forEach(page => {
        page.classList.remove('active');
    });
    document.getElementById(pageId).classList.add('active');
}

function showLandingPage() {
    showPage('landing-page');
    loadStats();
}

function showUploadPage() {
    showPage('upload-page');
    setupFileUpload();
}

function showQueryPage() {
    showPage('query-page');
    document.getElementById('query-input').focus();
}

// Stats Loading
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/ingestion/collection/count`);
        const data = await response.json();
        document.getElementById('doc-count').textContent = data.count || 0;
    } catch (error) {
        console.error('Error loading stats:', error);
        document.getElementById('doc-count').textContent = '-';
    }
}

// File Upload
function setupFileUpload() {
    const uploadArea = document.getElementById('upload-area');
    const fileInput = document.getElementById('file-input');
    const fileList = document.getElementById('file-list');
    const chooseFilesBtn = document.getElementById('choose-files-btn');

    // Button click handler
    if (chooseFilesBtn) {
        chooseFilesBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }

    // Click to upload
    uploadArea.addEventListener('click', () => {
        fileInput.click();
    });

    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('dragover');
    });

    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('dragover');
    });

    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('dragover');
        const files = Array.from(e.dataTransfer.files);
        handleFiles(files);
    });

    fileInput.addEventListener('change', (e) => {
        const files = Array.from(e.target.files);
        handleFiles(files);
    });
}

async function handleFiles(files) {
    const fileList = document.getElementById('file-list');
    fileList.innerHTML = '';

    for (const file of files) {
        await uploadFile(file);
    }
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);

    const progressContainer = document.getElementById('upload-progress');
    const progressFill = document.getElementById('progress-fill');
    const progressText = document.getElementById('progress-text');
    const uploadResults = document.getElementById('upload-results');
    const fileList = document.getElementById('file-list');

    // Show file in list
    const fileItem = document.createElement('div');
    fileItem.className = 'file-item';
    fileItem.innerHTML = `
        <div class="file-icon">${getFileIcon(file.name)}</div>
        <div class="file-info">
            <div class="file-name">${file.name}</div>
            <div class="file-size">${formatFileSize(file.size)}</div>
        </div>
        <div class="file-status">Uploading...</div>
    `;
    fileList.appendChild(fileItem);

    // Show progress
    progressContainer.style.display = 'block';
    progressFill.style.width = '0%';
    progressText.textContent = `Uploading ${file.name}...`;

    try {
        const response = await fetch(`${API_BASE_URL}/api/ingestion/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upload failed');
        }

        const result = await response.json();
        
        // Update progress
        progressFill.style.width = '100%';
        progressText.textContent = 'Upload complete!';

        // Show success result
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item success';
        resultItem.innerHTML = `
            <div>
                <strong>${file.name}</strong> uploaded successfully
                <div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.25rem;">
                    ${result.chunks_processed} chunks processed
                </div>
            </div>
        `;
        uploadResults.appendChild(resultItem);

        // Update file item
        fileItem.querySelector('.file-status').textContent = '✓ Uploaded';
        fileItem.querySelector('.file-status').style.color = 'var(--success-color)';

        // Reload stats
        loadStats();

        // Hide progress after delay
        setTimeout(() => {
            progressContainer.style.display = 'none';
        }, 2000);

    } catch (error) {
        console.error('Upload error:', error);
        
        progressFill.style.width = '0%';
        progressText.textContent = 'Upload failed';

        // Show error result
        const resultItem = document.createElement('div');
        resultItem.className = 'result-item error';
        resultItem.innerHTML = `
            <div>
                <strong>${file.name}</strong> - ${error.message}
            </div>
        `;
        uploadResults.appendChild(resultItem);

        // Update file item
        fileItem.querySelector('.file-status').textContent = '✗ Failed';
        fileItem.querySelector('.file-status').style.color = 'var(--error-color)';
    }
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const icons = {
        'pdf': '📄',
        'docx': '📝',
        'doc': '📝',
        'jpg': '🖼️',
        'jpeg': '🖼️',
        'png': '🖼️',
        'gif': '🖼️',
        'bmp': '🖼️',
        'webp': '🖼️',
        'mp3': '🎵',
        'wav': '🎵',
        'm4a': '🎵',
        'flac': '🎵'
    };
    return icons[ext] || '📎';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

// Query/Chat Functionality
function handleQueryKeyPress(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendQuery();
    }
}

async function sendQuery() {
    const input = document.getElementById('query-input');
    const query = input.value.trim();
    const sendBtn = document.getElementById('send-btn');

    if (!query) return;

    // Disable input
    input.disabled = true;
    sendBtn.disabled = true;

    // Add user message
    addMessage(query, 'user');

    // Clear input
    input.value = '';

    // Show loading
    showLoading();

    try {
        const response = await fetch(`${API_BASE_URL}/api/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                query: query,
                top_k: 10
            })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Query failed');
        }

        const data = await response.json();
        
        // Add bot response
        addMessage(data.answer, 'bot', data.sources);

    } catch (error) {
        console.error('Query error:', error);
        addMessage(`Sorry, I encountered an error: ${error.message}`, 'bot');
    } finally {
        hideLoading();
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    }
}

function addMessage(text, type, sources = null) {
    const messagesContainer = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}-message`;

    let sourcesHtml = '';
    if (sources && sources.length > 0) {
        sourcesHtml = `
            <div class="sources-section">
                <div class="sources-title">Sources (${sources.length}):</div>
                ${sources.slice(0, 5).map((source, idx) => `
                    <div class="source-item">${idx + 1}. ${source.source} (${source.type})</div>
                `).join('')}
                ${sources.length > 5 ? `<div class="source-item">... and ${sources.length - 5} more</div>` : ''}
            </div>
        `;
    }

    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${formatMessageText(text)}</p>
            ${sourcesHtml}
        </div>
    `;

    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function formatMessageText(text) {
    // Convert markdown-style citations to HTML
    text = text.replace(/\[Citation (\d+)\]/g, '<strong>[Citation $1]</strong>');
    
    // Convert line breaks
    text = text.replace(/\n/g, '<br>');
    
    return text;
}

function showLoading() {
    document.getElementById('loading-overlay').style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    
    // Set up query input
    const queryInput = document.getElementById('query-input');
    queryInput.addEventListener('keypress', handleQueryKeyPress);
});

