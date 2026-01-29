const chatHistory = document.getElementById('chat-history');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const taskList = document.getElementById('task-list');
const memoryList = document.getElementById('memory-list');

// Session
let sessionId = localStorage.getItem('echo_session_id');
if (!sessionId) {
    sessionId = crypto.randomUUID();
    localStorage.setItem('echo_session_id', sessionId);
}
console.log("Session:", sessionId);

// --- Chat Logic ---
function appendMessage(text, sender) {
    const div = document.createElement('div');
    div.classList.add('message', sender === 'user' ? 'user-message' : 'assistant-message');
    div.textContent = text;
    chatHistory.appendChild(div);
    chatHistory.scrollTop = chatHistory.scrollHeight;
}

async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;

    appendMessage(text, 'user');
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Loading placeholder
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'assistant-message');
    loadingDiv.textContent = '...';
    chatHistory.appendChild(loadingDiv);
    chatHistory.scrollTop = chatHistory.scrollHeight;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text, session_id: sessionId })
        });
        const data = await response.json();

        chatHistory.removeChild(loadingDiv);

        if (response.ok) {
            appendMessage(data.response, 'assistant');
            // Immediate Refresh on action
            refreshData();
        } else {
            appendMessage(`Error: ${data.detail || 'Failed'}`, 'assistant');
        }
    } catch (e) {
        if (loadingDiv.parentNode) chatHistory.removeChild(loadingDiv);
        appendMessage(`Net Error: ${e.message}`, 'assistant');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
}

sendBtn.addEventListener('click', sendMessage);
userInput.addEventListener('keypress', (e) => e.key === 'Enter' && sendMessage());

// --- Projects Logic ---
const projectList = document.getElementById('project-list');

async function fetchProjects() {
    try {
        const res = await fetch('/api/projects');
        if (res.ok) {
            const projects = await res.json();
            renderProjects(projects);
        }
    } catch (e) { console.error("Project fetch fail", e); }
}

// --- Batch Selection Logic ---
let selectedItems = new Set(); // Stores IDs like "proj-123" or "task-456"
const deleteSelectedBtn = document.getElementById('delete-selected-btn');

function toggleSelection(id, type) {
    const key = `${type}:${id}`;
    if (selectedItems.has(key)) {
        selectedItems.delete(key);
    } else {
        selectedItems.add(key);
    }
    updateBatchUI();
}

function updateBatchUI() {
    if (selectedItems.size > 0) {
        deleteSelectedBtn.style.display = 'block';
        deleteSelectedBtn.textContent = `Delete Selected (${selectedItems.size})`;
    } else {
        deleteSelectedBtn.style.display = 'none';
    }
}

async function deleteSelectedItems() {
    if (!confirm(`Delete ${selectedItems.size} items?`)) return;

    const projIds = [];
    const taskIds = [];
    const memIds = [];

    selectedItems.forEach(key => {
        const [type, id] = key.split(':');
        if (type === 'project') projIds.push(id);
        if (type === 'task') taskIds.push(id);
        if (type === 'memory') memIds.push(id);
    });

    try {
        if (projIds.length > 0) {
            await fetch('/api/projects/batch-delete', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: projIds })
            });
        }
        if (taskIds.length > 0) {
            await fetch('/api/tasks/batch-delete', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: taskIds })
            });
        }
        if (memIds.length > 0) {
            await fetch('/api/memories/batch-delete', {
                method: 'POST', headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ids: memIds })
            });
        }

        selectedItems.clear();
        updateBatchUI();
        refreshData();

    } catch (e) {
        console.error("Batch Delete Fail", e);
        alert("Failed to delete some items.");
    }
}

// Update Renderers to include Checkboxes
function createCheckbox(id, type) {
    const box = document.createElement('input');
    box.type = 'checkbox';
    box.className = 'select-checkbox';
    box.onclick = (e) => {
        e.stopPropagation();
        toggleSelection(id, type);
    };
    // Persist checking state on re-render? For simplicity, clear on refreshData? 
    // Ideally persist if ID match.
    if (selectedItems.has(`${type}:${id}`)) {
        box.checked = true;
    }
    return box;
}

// ... Overwrite renderProjects and renderTasks to use createCheckbox ...

function renderProjects(projects) {
    projectList.innerHTML = '';
    if (!projects || projects.length === 0) {
        projectList.innerHTML = '<div class="empty-state">No projects</div>';
        return;
    }

    projects.forEach(proj => {
        const card = document.createElement('div');
        card.classList.add('card', 'project-card');
        if (proj.status === 'active') {
            card.style.borderLeft = '3px solid #238636';
            card.style.backgroundColor = 'rgba(35, 134, 54, 0.1)';
        } else {
            card.style.opacity = '0.7';
        }

        const header = document.createElement('div');
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';
        header.style.alignItems = 'center';

        // Checkbox Container to left
        const titleArea = document.createElement('div');
        titleArea.style.display = 'flex';
        titleArea.style.alignItems = 'center';

        titleArea.appendChild(createCheckbox(proj.id, 'project'));

        const title = document.createElement('div');
        title.style.fontWeight = '600';
        title.textContent = proj.name;
        titleArea.appendChild(title);

        const status = document.createElement('div');
        status.style.fontSize = '10px';
        status.style.textTransform = 'uppercase';
        status.textContent = proj.status;

        header.appendChild(titleArea);
        header.appendChild(status);

        // Actions... (Existing switch logic)
        const actions = document.createElement('div');
        actions.className = 'task-actions';
        actions.style.marginTop = '8px';

        if (proj.status !== 'active') {
            const switchBtn = document.createElement('button');
            switchBtn.textContent = 'Switch To';
            switchBtn.onclick = () => switchProject(proj.id);
            actions.appendChild(switchBtn);
        } else {
            const label = document.createElement('span');
            label.textContent = 'Active';
            label.style.fontSize = '11px';
            label.style.color = '#238636';
            actions.appendChild(label);
        }

        card.appendChild(header);
        card.appendChild(actions);
        projectList.appendChild(card);
    });
}

async function switchProject(id) {
    if (!confirm("Switch project? This pauses current tasks.")) return;
    try {
        await fetch(`/api/projects/${id}/switch`, { method: 'POST' });
        refreshData();
    } catch (e) { console.error("Switch fail", e); }
}

async function deleteAllProjects() {
    if (!confirm("⚠️ DANGER: Delete ALL projects? This cannot be undone.")) return;
    try {
        await fetch('/api/projects', { method: 'DELETE' });
        refreshData();
    } catch (e) { console.error("Delete All Proj fail", e); }
}

// --- Tasks Logic ---
async function fetchTasks() {
    try {
        const res = await fetch('/api/tasks');
        if (res.ok) {
            const tasks = await res.json();
            renderTasks(tasks);
        }
    } catch (e) { console.error("Task fetch fail", e); }
}

async function deleteAllTasks() {
    if (!confirm("Delete ALL tasks?")) return;
    try {
        await fetch('/api/tasks', { method: 'DELETE' });
        refreshData();
    } catch (e) { console.error("Delete All Tasks fail", e); }
}

function renderTasks(tasks) {
    taskList.innerHTML = '';
    if (!tasks || tasks.length === 0) {
        taskList.innerHTML = '<div class="empty-state">No active tasks</div>';
        return;
    }

    // Sort: Active first, then Paused
    tasks.sort((a, b) => (a.status === 'active' ? -1 : 1));

    tasks.forEach(task => {
        if (task.status === 'completed') return; // Don't show completed

        const card = document.createElement('div');
        card.classList.add('card', 'task-card');
        if (task.status === 'paused') card.classList.add('paused');

        const header = document.createElement('div');
        header.classList.add('task-header');

        // Checkbox wrapper
        const leftSide = document.createElement('div');
        leftSide.style.display = 'flex';
        leftSide.style.alignItems = 'center';
        leftSide.style.gap = '8px';

        leftSide.appendChild(createCheckbox(task.id, 'task'));

        const intent = document.createElement('div');
        intent.className = 'task-intent';
        intent.textContent = task.intent;
        leftSide.appendChild(intent);

        // Reassemble header
        header.style.display = 'flex';
        header.style.justifyContent = 'space-between';

        header.appendChild(leftSide);

        const status = document.createElement('div');
        status.className = 'task-status';
        status.textContent = task.status;
        header.appendChild(status);

        const actions = document.createElement('div');
        actions.classList.add('task-actions');

        if (task.status === 'active') {
            const pauseBtn = document.createElement('button');
            pauseBtn.className = 'small-btn';
            pauseBtn.textContent = 'Pause';
            pauseBtn.onclick = () => controlTask(task.id, 'pause');
            actions.appendChild(pauseBtn);
        } else if (task.status === 'paused') {
            const resBtn = document.createElement('button');
            resBtn.className = 'small-btn';
            resBtn.textContent = 'Resume';
            resBtn.onclick = () => controlTask(task.id, 'resume');
            actions.appendChild(resBtn);
        }

        // Dismiss calls 'paused' currently? Or need dismiss endpoint?
        // API has 'dismiss' which clears COMPLETED.
        // For active/paused, maybe cancel? 'controlTask' only handles pause/resume so far.
        // Let's stick to Pause/Resume for now to match backend.

        card.appendChild(header);
        card.appendChild(actions);
        taskList.appendChild(card);
    });
}

async function controlTask(id, action) {
    try {
        await fetch(`/api/tasks/${id}/control?action=${action}`, { method: 'POST' });
        fetchTasks(); // Instant update
    } catch (e) { console.error("Control fail", e); }
}

// --- Memory Logic ---
async function fetchMemories() {
    try {
        const res = await fetch('/api/memories');
        if (res.ok) {
            const memories = await res.json();
            renderMemories(memories);
        }
    } catch (e) { console.error("Memory fetch fail", e); }
}

function renderMemories(memories) {
    memoryList.innerHTML = '';
    if (!memories || memories.length === 0) {
        memoryList.innerHTML = '<div class="empty-state">No memories yet</div>';
        return;
    }

    memories.forEach(mem => {
        const item = document.createElement('div');
        item.className = "card memory-card";

        // Header
        const header = document.createElement('div');
        header.style.display = "flex";
        header.style.justifyContent = "space-between";
        header.style.alignItems = "center"; // Align Checkbox
        header.style.marginBottom = "4px";

        // Title Area (Checkbox + Title)
        const titleArea = document.createElement('div');
        titleArea.style.display = "flex";
        titleArea.style.alignItems = "center";

        // Memory ID Key: "memory"
        titleArea.appendChild(createCheckbox(mem.memory_id || mem.id, 'memory'));

        const title = document.createElement('div');
        title.style.fontWeight = "600";
        title.style.color = "var(--accent-color)";
        title.style.marginLeft = "8px"; // Gap for checkbox
        title.textContent = mem.title || "Memory";

        titleArea.appendChild(title);

        const rightSide = document.createElement('div');
        rightSide.style.display = "flex";
        rightSide.style.alignItems = "center";

        const typeChip = document.createElement('div');
        typeChip.className = "status-badge";
        typeChip.style.fontSize = "9px";
        typeChip.textContent = mem.type || "fact";

        // Delete Action
        const delBtn = document.createElement('span');
        delBtn.innerHTML = '&times;';
        delBtn.style.color = "#f85149";
        delBtn.style.cursor = "pointer";
        delBtn.style.marginLeft = "8px";
        delBtn.title = "Delete Memory";
        delBtn.onclick = (e) => { e.stopPropagation(); deleteMemory(mem.memory_id || mem.id); };

        rightSide.appendChild(typeChip);
        rightSide.appendChild(delBtn);

        header.appendChild(titleArea);
        header.appendChild(rightSide);

        // Content
        const content = document.createElement('div');
        content.style.fontSize = "12px";
        content.style.lineHeight = "1.4";
        content.style.color = "var(--text-primary)";
        content.textContent = mem.content || mem.memory; // Fallback

        // Tags
        const footer = document.createElement('div');
        footer.style.marginTop = "8px";
        footer.style.display = "flex";
        footer.style.gap = "4px";
        footer.style.flexWrap = "wrap";

        if (mem.tags && Array.isArray(mem.tags)) {
            mem.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.style.backgroundColor = "rgba(255,255,255,0.05)";
                tagSpan.style.padding = "2px 6px";
                tagSpan.style.borderRadius = "4px";
                tagSpan.style.fontSize = "10px";
                tagSpan.style.color = "var(--text-secondary)";
                tagSpan.textContent = `#${tag}`;
                footer.appendChild(tagSpan);
            });
        }

        item.appendChild(header);
        item.appendChild(content);
        if (mem.tags && mem.tags.length > 0) item.appendChild(footer);

        memoryList.appendChild(item);
    });
}

async function deleteMemory(id) {
    if (!confirm("Forget this memory?")) return;
    try {
        await fetch(`/api/memories/${id}`, { method: 'DELETE' });
        fetchMemories();
    } catch (e) { console.error("Delete fail", e); }
}

// --- Utils ---
function refreshData() {
    fetchProjects();
    fetchTasks();
    fetchMemories();
}

// Init
refreshData();
setInterval(fetchTasks, 2000); // Poll tasks often
setInterval(fetchMemories, 5000); // Poll memories less often
setInterval(fetchProjects, 5000); // Poll projects
