// Unified Interface JavaScript
// Combines project management, radar visualization, and Excel editing

// ===== Global State =====
let currentProject = null;
let radarData = null;
let gridApi = null;
let isDirty = false;
let currentMode = 'view'; // 'view' or 'edit'

// ===== API Helpers =====
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`/api${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        // Get response text first
        const text = await response.text();
        
        if (!response.ok) {
            // Try to parse error as JSON
            try {
                const error = JSON.parse(text);
                throw new Error(error.error || 'API request failed');
            } catch (e) {
                // If not JSON, use text as error
                throw new Error(text || `HTTP ${response.status}`);
            }
        }
        
        // Parse successful response
        try {
            return JSON.parse(text);
        } catch (parseError) {
            console.error('JSON Parse Error:', parseError);
            console.error('Response text:', text.substring(0, 500));
            throw new Error(`Invalid JSON response: ${parseError.message}`);
        }
    } catch (error) {
        console.error('API Error:', error);
        alert(`Error: ${error.message}`);
        throw error;
    }
}

// ===== Project Management =====
async function loadProjects() {
    const projectList = document.getElementById('project-list');
    projectList.innerHTML = '<div class="loading">Loading projects...</div>';
    
    try {
        const data = await apiCall('/projects');
        
        if (data.projects.length === 0) {
            projectList.innerHTML = '<div class="loading">No projects found. Create one!</div>';
            return;
        }
        
        projectList.innerHTML = '';
        data.projects.forEach(project => {
            const item = document.createElement('div');
            item.className = 'project-item';
            item.dataset.projectId = project.id;
            
            const date = new Date(project.modified).toLocaleDateString();
            item.innerHTML = `
                <div class="project-item-name">${project.name}</div>
                <div class="project-item-meta">${date}</div>
            `;
            
            item.addEventListener('click', () => selectProject(project.id));
            projectList.appendChild(item);
        });
        
        // Auto-select first project
        if (data.projects.length > 0 && !currentProject) {
            selectProject(data.projects[0].id);
        }
    } catch (error) {
        projectList.innerHTML = '<div class="loading">Error loading projects</div>';
    }
}

async function selectProject(projectId) {
    // Update UI
    document.querySelectorAll('.project-item').forEach(item => {
        item.classList.toggle('active', item.dataset.projectId === projectId);
    });
    
    currentProject = projectId;
    document.getElementById('active-project-name').textContent = 
        projectId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    // Load radar data
    await loadRadar(projectId);
}

async function loadRadar(projectId) {
    try {
        radarData = await apiCall(`/projects/${projectId}`);
        renderRadar(radarData);
    } catch (error) {
        console.error('Failed to load radar:', error);
    }
}

// ===== New Project =====
function showNewProjectModal() {
    document.getElementById('new-project-modal').style.display = 'flex';
    document.getElementById('new-project-name').value = '';
    document.getElementById('new-project-name').focus();
}

function hideNewProjectModal() {
    document.getElementById('new-project-modal').style.display = 'none';
}

async function createProject() {
    const name = document.getElementById('new-project-name').value.trim();
    if (!name) {
        alert('Please enter a project name');
        return;
    }
    
    try {
        await apiCall('/projects', {
            method: 'POST',
            body: JSON.stringify({ name, template: 'default' })
        });
        
        hideNewProjectModal();
        await loadProjects();
    } catch (error) {
        console.error('Failed to create project:', error);
    }
}

// ===== Mode Switching =====
function switchToViewMode() {
    currentMode = 'view';
    document.getElementById('view-mode-btn').classList.add('active');
    document.getElementById('edit-mode-btn').classList.remove('active');
    document.getElementById('save-btn').style.display = 'none';
    
    // Show radar, hide editor
    document.querySelector('.app-container').classList.remove('edit-mode');
    document.getElementById('radar-view').style.display = 'flex';
    document.getElementById('edit-view-main').style.display = 'none';
}

async function switchToEditMode() {
    if (!currentProject) {
        alert('Please select a project first');
        return;
    }
    
    currentMode = 'edit';
    document.getElementById('view-mode-btn').classList.remove('active');
    document.getElementById('edit-mode-btn').classList.add('active');
    document.getElementById('save-btn').style.display = 'block';
    
    // Hide radar, show editor in full width
    document.querySelector('.app-container').classList.add('edit-mode');
    document.getElementById('radar-view').style.display = 'none';
    document.getElementById('edit-view-main').style.display = 'flex';
    
    await loadExcelData();
}

// ===== Excel Editing =====
async function loadExcelData() {
    try {
        console.log('Loading Excel data for project:', currentProject);
        const data = await apiCall(`/projects/${currentProject}/excel`);
        console.log('Received data:', data);
        
        if (!data || !data.columns || !data.rows) {
            throw new Error('Invalid data structure received from API');
        }
        
        // Initialize AG Grid
        const columnDefs = data.columns.map(col => ({
            field: String(col), // Ensure field is a string
            headerName: String(col),
            editable: true,
            sortable: true,
            filter: true,
            resizable: true,
            minWidth: 100
        }));
        
        console.log('Column definitions:', columnDefs);
        
        const gridOptions = {
            columnDefs,
            rowData: data.rows,
            rowSelection: 'single',
            defaultColDef: {
                flex: 1,
                minWidth: 100,
                editable: true,
                resizable: true
            },
            onCellValueChanged: (event) => {
                isDirty = true;
                const saveBtn = document.getElementById('save-btn');
                if (saveBtn) {
                    saveBtn.style.display = 'block';
                    saveBtn.style.opacity = '1';
                }
            }
        };
        
        const gridDiv = document.getElementById('grid-container');
        if (!gridDiv) {
            console.error('Grid container not found');
            return;
        }
        
        // Destroy previous grid if exists
        if (gridApi) {
            try {
                gridApi.destroy();
            } catch (e) {
                console.warn('Error destroying previous grid:', e);
            }
        }
        
        // Create new grid
        console.log('Creating AG Grid...');
        gridApi = agGrid.createGrid(gridDiv, gridOptions);
        
        console.log('Grid loaded successfully with', data.rows.length, 'rows');
        
    } catch (error) {
        console.error('Failed to load Excel data:', error);
        console.error('Error stack:', error.stack);
        alert('Failed to load Excel data: ' + error.message);
    }
}

async function saveExcelData() {
    if (!isDirty || !gridApi) return;
    
    const rowData = [];
    gridApi.forEachNode(node => rowData.push(node.data));
    
    try {
        await apiCall(`/projects/${currentProject}/excel`, {
            method: 'PUT',
            body: JSON.stringify({ rows: rowData })
        });
        
        isDirty = false;
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.style.display = 'none';
        }
        
        // Rebuild radar
        await apiCall(`/projects/${currentProject}/build`, { method: 'POST' });
        
        alert('Saved successfully!');
        
        // Reload radar if in view mode
        if (currentMode === 'view') {
            await loadRadar(currentProject);
        }
    } catch (error) {
        console.error('Failed to save:', error);
        alert('Failed to save: ' + error.message);
    }
}

function addRow() {
    if (!gridApi) return;
    
    const newRow = {};
    gridApi.getColumnDefs().forEach(col => {
        newRow[col.field] = '';
    });
    
    gridApi.applyTransaction({ add: [newRow] });
    isDirty = true;
    
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.style.display = 'block';
        saveBtn.style.opacity = '1';
    }
}

function deleteRow() {
    if (!gridApi) return;
    
    const selectedRows = gridApi.getSelectedRows();
    if (selectedRows.length === 0) {
        alert('Please select a row to delete');
        return;
    }
    
    if (confirm(`Delete ${selectedRows.length} row(s)?`)) {
        gridApi.applyTransaction({ remove: selectedRows });
        isDirty = true;
        
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn) {
            saveBtn.style.display = 'block';
            saveBtn.style.opacity = '1';
        }
    }
}

async function refreshGrid() {
    if (isDirty) {
        if (!confirm('You have unsaved changes. Reload anyway?')) {
            return;
        }
    }
    await loadExcelData();
    isDirty = false;
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.style.display = 'none';
    }
}

// ===== Radar Visualization =====
// (Reuse code from app.js - simplified version here)

function renderRadar(data) {
    const svg = d3.select('#radar');
    svg.selectAll('*').remove();
    
    const width = svg.node().getBoundingClientRect().width;
    const height = svg.node().getBoundingClientRect().height;
    const centerX = width / 2;
    const centerY = height / 2;
    
    const g = svg.append('g')
        .attr('transform', `translate(${centerX},${centerY})`);
    
    // Draw rings
    const maxRadius = Math.min(width, height) / 2 - 100;
    const ringCount = data.rings.length;
    const ringStep = maxRadius / ringCount;
    
    data.rings.forEach((ring, i) => {
        const radius = (i + 1) * ringStep;
        g.append('circle')
            .attr('class', 'ring-circle')
            .attr('r', radius);
        
        g.append('text')
            .attr('class', 'ring-label')
            .attr('y', -radius + 20)
            .text(ring.name);
    });
    
    // Draw quadrants
    const angleStep = (2 * Math.PI) / data.quadrants.length;
    data.quadrants.forEach((quadrant, i) => {
        const angle = i * angleStep;
        const labelRadius = maxRadius + 40;
        const x = Math.cos(angle + angleStep / 2) * labelRadius;
        const y = Math.sin(angle + angleStep / 2) * labelRadius;
        
        g.append('text')
            .attr('class', 'quadrant-label')
            .attr('x', x)
            .attr('y', y)
            .attr('text-anchor', 'middle')
            .text(quadrant.name);
    });
    
    // Draw entries
    data.entries.forEach(entry => {
        const ringIndex = data.rings.findIndex(r => r.id === entry.ring);
        const quadrantIndex = data.quadrants.findIndex(q => q.id === entry.quadrant);
        
        const ringRadius = ((ringIndex + 0.5) * ringStep) + (Math.random() - 0.5) * ringStep * 0.6;
        const angle = (quadrantIndex * angleStep) + (Math.random() * angleStep);
        
        const x = Math.cos(angle) * ringRadius;
        const y = Math.sin(angle) * ringRadius;
        
        const ring = data.rings[ringIndex];
        
        g.append('circle')
            .attr('class', 'radar-dot')
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', 8)
            .attr('fill', ring.color)
            .attr('stroke', '#333')
            .attr('stroke-width', entry.isNew ? 3 : 1.5)
            .style('cursor', 'pointer')
            .on('click', () => showDetail(entry));
        
        g.append('text')
            .attr('class', 'radar-label')
            .attr('x', x)
            .attr('y', y + 18)
            .attr('text-anchor', 'middle')
            .text(entry.name);
    });
}

function showDetail(entry) {
    if (currentMode !== 'view') return;
    
    document.getElementById('detail-name').textContent = entry.name;
    
    const ring = radarData.rings.find(r => r.id === entry.ring);
    const quadrant = radarData.quadrants.find(q => q.id === entry.quadrant);
    
    document.getElementById('detail-ring').textContent = ring.name;
    document.getElementById('detail-ring').style.background = ring.color;
    
    document.getElementById('detail-quadrant').textContent = quadrant.name;
    
    if (entry.status) {
        const status = radarData.statuses.find(s => s.id === entry.status);
        document.getElementById('detail-status').textContent = status.name;
        document.getElementById('detail-status').style.background = status.color;
        document.getElementById('detail-status').style.display = 'inline-block';
    } else {
        document.getElementById('detail-status').style.display = 'none';
    }
    
    document.getElementById('detail-description').innerHTML = entry.descriptionHtml || '<p>No description</p>';
    
    if (entry.link) {
        document.getElementById('detail-link').href = entry.link;
        document.getElementById('detail-link').textContent = 'View Link →';
        document.getElementById('detail-link').style.display = 'inline-block';
    } else {
        document.getElementById('detail-link').style.display = 'none';
    }
}

// ===== Event Listeners =====
document.addEventListener('DOMContentLoaded', () => {
    // Load projects on start
    loadProjects();
    
    // Mode switching
    document.getElementById('view-mode-btn').addEventListener('click', switchToViewMode);
    document.getElementById('edit-mode-btn').addEventListener('click', switchToEditMode);
    
    // Save button
    document.getElementById('save-btn').addEventListener('click', saveExcelData);
    
    // New project
    document.getElementById('new-project-btn').addEventListener('click', showNewProjectModal);
    document.getElementById('create-project-btn').addEventListener('click', createProject);
    document.getElementById('cancel-project-btn').addEventListener('click', hideNewProjectModal);
    
    // Edit actions
    document.getElementById('add-row-btn').addEventListener('click', addRow);
    document.getElementById('delete-row-btn').addEventListener('click', deleteRow);
    document.getElementById('refresh-grid-btn').addEventListener('click', refreshGrid);
    
    // Close detail
    document.getElementById('close-detail').addEventListener('click', () => {
        // Could hide detail panel or clear it
    });
    
    // Search
    document.getElementById('search').addEventListener('input', (e) => {
        // TODO: Implement search filtering
    });
    
    // Zoom controls
    document.getElementById('zoom-in').addEventListener('click', () => {
        // TODO: Implement zoom
    });
    document.getElementById('zoom-out').addEventListener('click', () => {
        // TODO: Implement zoom
    });
    document.getElementById('zoom-reset').addEventListener('click', () => {
        // TODO: Implement zoom reset
    });
    document.getElementById('export-png').addEventListener('click', () => {
        // TODO: Implement PNG export
    });
});

// Made with Bob
