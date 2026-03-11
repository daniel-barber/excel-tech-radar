// Unified Interface JavaScript
// Combines project management, radar visualization, and Excel editing

// ===== Constants =====
const PROGRESS_UPLOAD_START = 30;
const PROGRESS_UPLOAD_COMPLETE = 70;
const PROGRESS_DONE = 100;
const ERROR_DISPLAY_TIMEOUT = 3000;

// ===== Global State =====
let currentProject = null;
let currentProjectId = null;
let radarData = null;
let gridApi = null;
let isDirty = false;
let currentMode = 'view'; // 'view' or 'edit'
let currentDetailEntry = null;
let isDetailDirty = false;          // Track unsaved changes in detail edit mode
let quillEditor = null;             // Quill rich text editor instance

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
        
        // Check URL hash for project selection
        const urlHash = window.location.hash;
        let projectToSelect = null;
        
        if (urlHash && urlHash.startsWith('#project=')) {
            const projectId = urlHash.substring(9); // Remove '#project='
            // Check if project exists
            const projectExists = data.projects.some(p => p.id === projectId);
            if (projectExists) {
                projectToSelect = projectId;
            }
        }
        
        // Auto-select project from URL or first project
        if (data.projects.length > 0 && !currentProject) {
            selectProject(projectToSelect || data.projects[0].id);
        }
    } catch (error) {
        projectList.innerHTML = '<div class="loading">Error loading projects</div>';
    }
}

async function selectProject(projectId) {
    // Check if already on this project
    if (currentProject === projectId) {
        return;
    }
    
    // Check for unsaved changes in edit mode (table editing)
    if (currentMode === 'edit' && isDirty) {
        const save = confirm('You have unsaved changes. Do you want to save before switching projects?');
        if (save) {
            try {
                await saveExcelData();
            } catch (error) {
                console.error('Failed to save:', error);
                const proceed = confirm('Failed to save. Switch anyway?');
                if (!proceed) return;
            }
        } else {
            const proceed = confirm('Discard unsaved changes and switch projects?');
            if (!proceed) return;
        }
    }
    
    // Check for unsaved changes in detail panel edit mode
    if (isDetailDirty) {
        const save = confirm('You have unsaved changes in the detail panel. Save before switching?');
        if (save) {
            // Try to save the detail panel changes
            try {
                await saveEditEntry(new Event('submit'));
            } catch (error) {
                console.error('Failed to save detail changes:', error);
                const proceed = confirm('Failed to save. Switch anyway?');
                if (!proceed) return;
            }
        } else {
            const proceed = confirm('Discard unsaved detail changes and switch projects?');
            if (!proceed) return;
        }
        isDetailDirty = false;
    }
    
    // Switch to view mode when changing projects
    if (currentMode === 'edit') {
        switchToViewMode();
    }
    
    // Update UI
    document.querySelectorAll('.project-item').forEach(item => {
        item.classList.toggle('active', item.dataset.projectId === projectId);
    });
    
    currentProject = projectId;
    currentProjectId = projectId;  // Set global project ID for API calls
    document.getElementById('active-project-name').textContent =
        projectId.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    
    // Update URL hash to persist project selection
    window.location.hash = `project=${projectId}`;
    
    // Reset dirty flag
    isDirty = false;
    const saveBtn = document.getElementById('save-btn');
    if (saveBtn) {
        saveBtn.style.display = 'none';
    }
    
    // Close detail panel when switching projects
    closeDetail();
    
    // Load radar data
    await loadRadar(projectId);
}

async function loadRadar(projectId) {
    try {
        radarData = await apiCall(`/projects/${projectId}`);
        renderRadar(radarData);
        updateFormDatalists(radarData);
    } catch (error) {
        console.error('Failed to load radar:', error);
    }
}

function updateFormDatalists(data) {
    if (!data) return;
    
    // Update rings select
    updateDatalist('edit-ring', data.rings, data.entries, 'ring');
    
    // Update quadrants select
    updateDatalist('edit-quadrant', data.quadrants, data.entries, 'quadrant');
    
    // Update deal size select
    updateDealSizeDatalist(data);
    
    // Update propensity to win select
    updatePropensityToWinDatalist(data);
}

function updateDatalist(elementId, configItems, entries, fieldName) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.warn(`Element not found: ${elementId}`);
        return;
    }
    
    // Helper function to normalize values for comparison (lowercase, remove spaces/hyphens/underscores)
    function normalizeForComparison(str) {
        return str.toLowerCase().replace(/[\s\-_]+/g, '');
    }
    
    // For rings, preserve config order; for others, collect all values
    let orderedValues = [];
    const configValueSet = new Set();
    const configValueMap = new Map(); // Map normalized -> original case
    
    // Add configured items first (from config.yml) - preserve order
    if (configItems && Array.isArray(configItems)) {
        configItems.forEach(item => {
            if (item.name) {
                orderedValues.push(item.name);
                const normalized = normalizeForComparison(item.name);
                configValueSet.add(normalized);
                configValueMap.set(normalized, item.name);
            }
        });
    }
    
    // Add unique values from entries (from Excel data) that aren't in config
    const additionalValues = new Set();
    if (entries && Array.isArray(entries)) {
        entries.forEach(entry => {
            const value = entry[fieldName];
            if (value && typeof value === 'string' && value.trim()) {
                const trimmedValue = value.trim();
                const normalized = normalizeForComparison(trimmedValue);
                // Only add if not in config (normalized comparison)
                if (!configValueSet.has(normalized)) {
                    additionalValues.add(trimmedValue);
                }
            }
        });
    }
    
    // For rings (edit-ring), keep config order; for others, sort additional values
    if (elementId === 'edit-ring') {
        // Rings: config order first, then sorted additional values
        const sortedAdditional = Array.from(additionalValues).sort();
        orderedValues = [...orderedValues, ...sortedAdditional];
    } else {
        // Quadrants/status: sort all values alphabetically
        orderedValues = [...orderedValues, ...Array.from(additionalValues)].sort();
    }
    
    console.log(`Populating ${elementId} with ${orderedValues.length} values:`, orderedValues);
    
    // Check if this is a select or input+datalist
    if (element.tagName === 'SELECT') {
        // Get current value before clearing
        const currentValue = element.value;
        
        // Update the select - keep the first "-- Select --" option
        const firstOption = element.options[0];
        element.innerHTML = '';
        element.appendChild(firstOption);
        
        orderedValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            option.textContent = value;
            element.appendChild(option);
        });
        
        // Restore previous value if it exists in the new options
        if (currentValue) {
            element.value = currentValue;
        }
    } else if (element.tagName === 'INPUT' && element.hasAttribute('list')) {
        // This is an input with a datalist
        const datalistId = element.getAttribute('list');
        let datalist = document.getElementById(datalistId);
        
        // Create datalist if it doesn't exist
        if (!datalist) {
            datalist = document.createElement('datalist');
            datalist.id = datalistId;
            element.parentNode.appendChild(datalist);
        }
        
        // Clear and populate datalist
        datalist.innerHTML = '';
        orderedValues.forEach(value => {
            const option = document.createElement('option');
            option.value = value;
            datalist.appendChild(option);
        });
    }
}

function updateDealSizeDatalist(data) {
    const select = document.getElementById('edit-dealsize');
    if (!select) {
        console.warn('Deal size select not found');
        return;
    }
    
    // Get deal sizes from config
    let dealSizes = [];
    if (data && data.dealSizes && Array.isArray(data.dealSizes) && data.dealSizes.length > 0) {
        console.log('Using config dealSizes:', data.dealSizes.map(d => d.name));
        dealSizes = data.dealSizes.map(d => d.name);
    } else {
        console.log('No config dealSizes found, using fallback');
        // Fallback to standard deal sizes
        dealSizes = ['< $100k', '$100k - $500k', '> $500k'];
    }
    
    console.log(`Populating edit-dealsize with ${dealSizes.length} values:`, dealSizes);
    
    // Get current value before clearing
    const currentValue = select.value;
    
    // Keep the first "-- Select Deal Size --" option
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);
    
    dealSizes.forEach(dealSize => {
        const option = document.createElement('option');
        option.value = dealSize;
        option.textContent = dealSize;
        select.appendChild(option);
    });
    
    // Restore previous value if it exists in the new options
    if (currentValue) {
        select.value = currentValue;
    }
}

function updatePropensityToWinDatalist(data) {
    const select = document.getElementById('edit-propensity');
    if (!select) {
        console.warn('Propensity to win select not found');
        return;
    }
    
    // Get propensity to win options from config
    let propensityOptions = [];
    if (data && data.propensityToWin && Array.isArray(data.propensityToWin) && data.propensityToWin.length > 0) {
        console.log('Using config propensityToWin:', data.propensityToWin.map(p => p.name));
        propensityOptions = data.propensityToWin.map(p => p.name);
    } else {
        console.log('No config propensityToWin found, using fallback');
        // Fallback to standard propensity options
        propensityOptions = ['Low', 'Medium', 'High'];
    }
    
    console.log(`Populating edit-propensity with ${propensityOptions.length} values:`, propensityOptions);
    
    // Get current value before clearing
    const currentValue = select.value;
    
    // Keep the first "-- Select Propensity --" option
    const firstOption = select.options[0];
    select.innerHTML = '';
    select.appendChild(firstOption);
    
    propensityOptions.forEach(propensity => {
        const option = document.createElement('option');
        option.value = propensity;
        option.textContent = propensity;
        select.appendChild(option);
    });
    
    // Restore previous value if it exists in the new options
    if (currentValue) {
        select.value = currentValue;
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

// ===== Dot Size Calculation =====
function calculateDotSize(entry, layout, allEntries) {
    if (entry.value && entry.value > 0) {
        // Size based on value
        const maxValue = Math.max(...allEntries.map(e => e.value || 0));
        if (maxValue > 0) {
            const normalized = entry.value / maxValue;
            const size = layout.dotMinSize + (layout.dotMaxSize - layout.dotMinSize) * normalized;
            console.log(`Entry: ${entry.name}, value: ${entry.value}, maxValue: ${maxValue}, normalized: ${normalized}, size: ${size}`);
            return size;
        }
    }
    const defaultSize = (layout.dotMinSize + layout.dotMaxSize) / 2;
    console.log(`Entry: ${entry.name}, no value, using default size: ${defaultSize}`);
    return defaultSize;
}

// ===== Radar Visualization =====
// (Reuse code from app.js - simplified version here)

function renderRadar(data, searchTerm = '') {
    const svg = d3.select('#radar');
    svg.selectAll('*').remove();
    
    const width = svg.node().getBoundingClientRect().width;
    const height = svg.node().getBoundingClientRect().height;
    const centerX = width / 2;
    const centerY = height / 2;
    
    // Add background rectangle for click detection
    svg.append('rect')
        .attr('width', width)
        .attr('height', height)
        .attr('fill', 'transparent')
        .style('cursor', 'default')
        .on('click', () => {
            // Close detail panel when clicking background
            if (document.getElementById('detail-view').classList.contains('active')) {
                closeDetail();
            }
        });
    
    const g = svg.append('g')
        .attr('transform', `translate(${centerX},${centerY})`);
    
    // Helper function to capitalize text
    function capitalize(str) {
        return str
            .split(' ')
            .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
            .join(' ');
    }
    
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
            .text(capitalize(ring.name));
    });
    
    // Draw quadrant divider lines
    const angleStep = (2 * Math.PI) / data.quadrants.length;
    data.quadrants.forEach((quadrant, i) => {
        const angle = i * angleStep;
        
        // Draw divider line from center to outer edge
        g.append('line')
            .attr('x1', 0)
            .attr('y1', 0)
            .attr('x2', Math.cos(angle) * maxRadius)
            .attr('y2', Math.sin(angle) * maxRadius)
            .attr('stroke', '#cbd5e1')
            .attr('stroke-width', 1.5)
            .attr('stroke-dasharray', '5,5');
    });
    
    // Draw quadrant labels
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
            .text(capitalize(quadrant.name));
    });
    
    // Filter entries based on search term
    const filteredEntries = searchTerm
        ? data.entries.filter(entry => {
            const searchLower = searchTerm.toLowerCase();
            return entry.name.toLowerCase().includes(searchLower) ||
                   (entry.tags && entry.tags.some(tag => tag.toLowerCase().includes(searchLower))) ||
                   (entry.descriptionHtml && entry.descriptionHtml.toLowerCase().includes(searchLower));
          })
        : data.entries;
    
    // Draw entries
    filteredEntries.forEach(entry => {
        const ringIndex = data.rings.findIndex(r => r.id === entry.ring);
        const quadrantIndex = data.quadrants.findIndex(q => q.id === entry.quadrant);
        
        const ringRadius = ((ringIndex + 0.5) * ringStep) + (Math.random() - 0.5) * ringStep * 0.6;
        const angle = (quadrantIndex * angleStep) + (Math.random() * angleStep);
        
        const x = Math.cos(angle) * ringRadius;
        const y = Math.sin(angle) * ringRadius;
        
        const ring = data.rings[ringIndex];
        
        const dotSize = calculateDotSize(entry, data.layout, data.entries);
        
        // Get color from propensityToWin, fallback to blue
        let dotColor = '#2196F3';  // Default blue color
        if (entry.propensityToWin && data.propensityToWin) {
            const propensity = data.propensityToWin.find(p => p.name === entry.propensityToWin);
            if (propensity && propensity.color) {
                dotColor = propensity.color;
            }
        }
        
        g.append('circle')
            .attr('class', 'radar-dot')
            .attr('data-entry-id', entry.id)
            .attr('data-entry-name', entry.name)
            .attr('cx', x)
            .attr('cy', y)
            .attr('r', dotSize)
            .attr('fill', dotColor)
            .attr('stroke', 'none')
            .style('cursor', 'pointer')
            .on('click', (event) => {
                event.stopPropagation();  // Prevent background click
                showDetail(entry);
            });
        
        // Add strategic indicator (dark blue center dot)
        if (entry.isStrategic) {
            g.append('circle')
                .attr('class', 'radar-dot-strategic')
                .attr('cx', x)
                .attr('cy', y)
                .attr('r', dotSize * 0.35)  // 35% of main dot size
                .attr('fill', '#1565C0')  // Dark blue
                .style('pointer-events', 'none');  // Don't interfere with click events
        }
        
        g.append('text')
            .attr('class', 'radar-label')
            .attr('data-entry-id', entry.id)
            .attr('x', x)
            .attr('y', y + dotSize + 10)
            .attr('text-anchor', 'middle')
            .text(entry.name);
    });
    
    // Show count of filtered results
    if (searchTerm && filteredEntries.length < data.entries.length) {
        console.log(`Showing ${filteredEntries.length} of ${data.entries.length} entries`);
    }
}

async function showDetail(entry) {
    // Check if we're in edit mode in the detail panel (not the global mode)
    const isEditingDetail = document.getElementById('detail-edit-mode').style.display !== 'none';
    
    // If editing with unsaved changes, ask user to save first
    if (isEditingDetail && isDetailDirty) {
        const save = confirm('You have unsaved changes. Do you want to save them before viewing another entry?\n\nClick OK to save, or Cancel to discard changes.');
        if (save) {
            // Save the current entry first - create a fake event object
            const fakeEvent = { preventDefault: () => {} };
            await saveEditEntry(fakeEvent);
            // Close edit mode
            cancelEditEntry();
            // Fall through to show the new entry
        } else {
            // Discard changes and show new entry
            cancelEditEntry();
            // Fall through to show the new entry
        }
    } else if (isEditingDetail) {
        // In edit mode but no changes - just close edit mode and show new entry
        cancelEditEntry();
        // Fall through to show the new entry
    }
    
    currentDetailEntry = entry;
    
    // Highlight selected dot and fade others
    d3.selectAll('.radar-dot')
        .each(function() {
            const entryName = d3.select(this).attr('data-entry-name');
            const isSelected = entryName === entry.name;
            
            d3.select(this)
                .style('opacity', isSelected ? 1 : 0.2)
                .attr('stroke-width', isSelected ? 4 : 0)
                .attr('stroke', isSelected ? '#3b82f6' : 'none');
        });
    
    d3.selectAll('.radar-label')
        .each(function() {
            const labelId = d3.select(this).attr('data-entry-id');
            const isSelected = labelId === entry.id;
            
            d3.select(this)
                .style('opacity', isSelected ? 1 : 0.2);
        });
    
    // Show detail view
    const detailView = document.getElementById('detail-view');
    detailView.classList.add('active');
    
    // Populate view mode
    document.getElementById('detail-name').textContent = entry.name;
    
    const ring = radarData.rings.find(r => r.id === entry.ring);
    const quadrant = radarData.quadrants.find(q => q.id === entry.quadrant);
    
    document.getElementById('detail-ring').textContent = ring ? ring.name : entry.ring;
    document.getElementById('detail-ring').style.background = ring ? ring.color : '#94a3b8';
    
    document.getElementById('detail-quadrant').textContent = quadrant ? quadrant.name : entry.quadrant;
    document.getElementById('detail-quadrant').style.background = '#64748b';
    document.getElementById('detail-quadrant').style.color = '#ffffff';
    
    // Tags - only show if there are actual tags (not empty array or string "[]")
    let hasTags = false;
    let tagsArray = [];
    
    if (entry.tags) {
        // Handle case where tags might be a string "[]" or actual array
        if (typeof entry.tags === 'string') {
            // If it's a string like "[]" or empty, skip it
            if (entry.tags.trim() && entry.tags !== '[]') {
                // Parse comma-separated tags
                tagsArray = entry.tags.split(',').map(t => t.trim()).filter(t => t);
                hasTags = tagsArray.length > 0;
            }
        } else if (Array.isArray(entry.tags)) {
            // Filter out empty strings and "[]"
            tagsArray = entry.tags.filter(tag => tag && tag !== '[]' && tag.trim() !== '');
            hasTags = tagsArray.length > 0;
        }
    }
    
    if (hasTags) {
        const tagsHtml = tagsArray.map(tag => `<span class="tag">${tag}</span>`).join('');
        document.getElementById('detail-tags').innerHTML = tagsHtml;
        document.getElementById('detail-tags-section').style.display = 'block';
    } else {
        document.getElementById('detail-tags-section').style.display = 'none';
    }
    
    // Description - only show if there's actual content
    const descriptionHtml = entry.descriptionHtml || '';
    const descriptionText = descriptionHtml.trim();
    
    if (descriptionText && descriptionText !== '<p></p>' && descriptionText !== '<p><br></p>') {
        document.getElementById('detail-description').innerHTML = descriptionHtml;
        document.getElementById('detail-description-section').style.display = 'block';
    } else {
        document.getElementById('detail-description-section').style.display = 'none';
    }
    
    // Link
    if (entry.link) {
        const linkElement = document.getElementById('detail-link');
        linkElement.href = entry.link;
        // Use linkName if available and not empty, otherwise show the URL
        linkElement.textContent = (entry.linkName && entry.linkName.trim()) ? entry.linkName : entry.link;
        document.getElementById('detail-link-section').style.display = 'block';
    } else {
        document.getElementById('detail-link-section').style.display = 'none';
    }
}

function closeDetail() {
    // Reset all dots to normal opacity and styling
    d3.selectAll('.radar-dot')
        .style('opacity', 1)
        .attr('stroke', 'none')
        .attr('stroke-width', 0);
    
    d3.selectAll('.radar-label')
        .style('opacity', 1);
    
    document.getElementById('detail-view').classList.remove('active');
    document.getElementById('detail-view-mode').style.display = 'block';
    document.getElementById('detail-edit-mode').style.display = 'none';
    currentDetailEntry = null;
}

function showEditEntryForm() {
    if (!currentDetailEntry) return;
    
    // Hide view mode, show edit mode
    document.getElementById('detail-view-mode').style.display = 'none';
    document.getElementById('detail-edit-mode').style.display = 'block';
    
    // Initialize Quill editor if not already initialized
    if (!quillEditor) {
        quillEditor = new Quill('#edit-description-editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    [{ 'header': [1, 2, 3, false] }],
                    ['bold', 'italic', 'underline', 'strike'],
                    ['link', 'code-block'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    ['clean']
                ]
            },
            placeholder: 'Enter description (supports rich text and HTML)...'
        });
        
        // Track changes in Quill editor
        quillEditor.on('text-change', () => {
            isDetailDirty = true;
        });
    }
    
    // Populate all datalists with config + Excel values FIRST
    updateFormDatalists(radarData);
    
    // Helper function to find matching option by normalizing both slug and display name
    function findMatchingOption(select, targetValue) {
        if (!targetValue) return '';
        
        const normalizedTarget = targetValue.toLowerCase().replace(/[\s\-_]+/g, '');
        
        for (let option of select.options) {
            const normalizedOption = option.value.toLowerCase().replace(/[\s\-_]+/g, '');
            if (normalizedOption === normalizedTarget) {
                return option.value;
            }
        }
        return '';
    }
    
    // THEN populate form with current entry data (after dropdowns are ready)
    document.getElementById('edit-name').value = currentDetailEntry.name;
    
    // Set ring - find matching display name for the slug
    const ringSelect = document.getElementById('edit-ring');
    const matchingRing = findMatchingOption(ringSelect, currentDetailEntry.ring);
    ringSelect.value = matchingRing;
    
    // Set quadrant
    document.getElementById('edit-quadrant').value = currentDetailEntry.quadrant;
    
    // Set deal size - check if entry has dealSize field directly, otherwise map from value
    const dealSizeSelect = document.getElementById('edit-dealsize');
    if (currentDetailEntry.dealSize) {
        // Entry has dealSize field directly (from Excel)
        dealSizeSelect.value = currentDetailEntry.dealSize;
    } else if (currentDetailEntry.value && radarData && radarData.dealSizes) {
        // Fall back to mapping from value field
        const matchingDealSize = radarData.dealSizes.find(d => d.value === currentDetailEntry.value);
        if (matchingDealSize) {
            dealSizeSelect.value = matchingDealSize.name;
        } else {
            dealSizeSelect.value = '';
        }
    } else {
        dealSizeSelect.value = '';
    }
    
    // Set propensity to win
    const propensitySelect = document.getElementById('edit-propensity');
    if (currentDetailEntry.propensityToWin) {
        propensitySelect.value = currentDetailEntry.propensityToWin;
    } else {
        propensitySelect.value = '';
    }
    
    // Handle tags - filter out empty arrays and string "[]"
    let tagsValue = '';
    if (Array.isArray(currentDetailEntry.tags) && currentDetailEntry.tags.length > 0) {
        // Filter out "[]" and empty strings from array
        const validTags = currentDetailEntry.tags.filter(tag =>
            tag && typeof tag === 'string' && tag.trim() !== '' && tag.trim() !== '[]'
        );
        if (validTags.length > 0) {
            tagsValue = validTags.join(', ');
        }
    } else if (typeof currentDetailEntry.tags === 'string') {
        // String value - check if it's "[]" or empty
        const trimmed = currentDetailEntry.tags.trim();
        if (trimmed && trimmed !== '[]') {
            tagsValue = trimmed;
        }
    }
    document.getElementById('edit-tags').value = tagsValue;
    
    // Set strategic checkbox
    const strategicCheckbox = document.getElementById('edit-strategic');
    strategicCheckbox.checked = currentDetailEntry.isStrategic === true;
    document.getElementById('edit-link-name').value = currentDetailEntry.linkName || '';
    document.getElementById('edit-link').value = currentDetailEntry.link || '';
    
    // Set Quill editor content (HTML)
    const descriptionHtml = currentDetailEntry.descriptionHtml || '';
    quillEditor.root.innerHTML = descriptionHtml;
    
    // Reset dirty flag when entering edit mode
    isDetailDirty = false;
    
    // Add change listeners to track edits
    const formInputs = document.querySelectorAll('#edit-entry-form input, #edit-entry-form textarea');
    formInputs.forEach(input => {
        input.addEventListener('input', () => {
            isDetailDirty = true;
        });
    });
}

function showNewEntryForm() {
    if (!currentProject) {
        alert('Please select a project first');
        return;
    }
    
    // Set up for new entry
    currentDetailEntry = null;
    
    // Show detail panel
    document.getElementById('detail-view').classList.add('active');
    
    // Show edit mode, hide view mode
    document.getElementById('detail-view-mode').style.display = 'none';
    document.getElementById('detail-edit-mode').style.display = 'block';
    
    // Initialize Quill editor if not already done
    if (!quillEditor) {
        quillEditor = new Quill('#edit-description-editor', {
            theme: 'snow',
            modules: {
                toolbar: [
                    ['bold', 'italic', 'underline'],
                    ['link'],
                    [{ 'list': 'ordered'}, { 'list': 'bullet' }],
                    ['clean']
                ]
            }
        });
        
        // Track changes in Quill editor
        quillEditor.on('text-change', () => {
            isDetailDirty = true;
        });
    }
    
    // Clear form
    document.getElementById('edit-name').value = '';
    document.getElementById('edit-ring').value = '';
    document.getElementById('edit-quadrant').value = '';
    document.getElementById('edit-dealsize').value = '';
    document.getElementById('edit-propensity').value = '';
    document.getElementById('edit-strategic').checked = false;
    document.getElementById('edit-tags').value = '';
    document.getElementById('edit-link-name').value = '';
    document.getElementById('edit-link').value = '';
    quillEditor.root.innerHTML = '';
    
    // Populate dropdowns
    updateFormDatalists(radarData);
    
    // Reset dirty flag
    isDetailDirty = false;
}

async function deleteEntry() {
    if (!currentDetailEntry || !currentProjectId) {
        alert('No entry selected');
        return;
    }
    
    const entryName = currentDetailEntry.name;
    
    // Confirmation dialog
    const confirmed = confirm(
        `⚠️ WARNING: This will permanently delete "${entryName}".\n\n` +
        `This action cannot be undone. Are you sure?`
    );
    
    if (!confirmed) {
        return;
    }
    
    try {
        // Get all Excel data to find row index
        const excelResponse = await apiCall(`/projects/${currentProjectId}/excel`);
        const allRows = excelResponse.rows || [];
        
        // Find the row index
        const rowIndex = allRows.findIndex(row => row.name === entryName);
        
        if (rowIndex === -1) {
            throw new Error('Entry not found in Excel data');
        }
        
        // Delete row via API
        const response = await apiCall(`/projects/${currentProjectId}/rows/${rowIndex}`, {
            method: 'DELETE'
        });
        
        // Update radar data from response
        if (response.radar) {
            radarData = response.radar;
            renderRadar(radarData);
        }
        
        // Close detail panel
        closeDetail();
        
        alert(`Entry "${entryName}" deleted successfully`);
        
    } catch (error) {
        console.error('Failed to delete entry:', error);
        alert('Failed to delete entry: ' + error.message);
    }
}

function cancelEditEntry() {
    // Reset dirty flag
    isDetailDirty = false;
    
    // Show view mode, hide edit mode
    document.getElementById('detail-view-mode').style.display = 'block';
    document.getElementById('detail-edit-mode').style.display = 'none';
}

async function saveEditEntry(event) {
    event.preventDefault();
    
    if (!currentProjectId) return;
    
    // Get HTML content from Quill editor
    const descriptionHtml = quillEditor ? quillEditor.root.innerHTML : '';
    
    // Get form data
    const dealSizeValue = document.getElementById('edit-dealsize').value;
    const propensityValue = document.getElementById('edit-propensity').value;
    const isStrategic = document.getElementById('edit-strategic').checked;
    
    const entryData = {
        name: document.getElementById('edit-name').value,
        ring: document.getElementById('edit-ring').value,
        quadrant: document.getElementById('edit-quadrant').value,
        dealSize: dealSizeValue || null,
        propensityToWin: propensityValue || null,
        isStrategic: isStrategic,
        tags: document.getElementById('edit-tags').value.split(',').map(t => t.trim()).filter(t => t),
        description: descriptionHtml,
        linkName: document.getElementById('edit-link-name').value || null,
        link: document.getElementById('edit-link').value || null
    };
    
    // Validate required fields (quadrant is optional)
    if (!entryData.name || !entryData.ring) {
        alert('Name and Ring are required fields.');
        return;
    }
    
    try {
        let response;
        const isNewEntry = !currentDetailEntry;
        
        if (isNewEntry) {
            // Creating a new entry - POST to /rows endpoint
            response = await apiCall(`/projects/${currentProjectId}/rows`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(entryData)
            });
        } else {
            // Updating existing entry - find row index and PUT
            const excelResponse = await apiCall(`/projects/${currentProjectId}/excel`);
            const allRows = excelResponse.rows || [];
            
            // Find the row index
            const rowIndex = allRows.findIndex(row => row.name === currentDetailEntry.name);
            
            if (rowIndex === -1) {
                throw new Error('Entry not found in Excel data');
            }
            
            // Update single row via API
            response = await apiCall(`/projects/${currentProjectId}/rows/${rowIndex}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(entryData)
            });
        }
        
        // Update radar data from response
        if (response.radar) {
            radarData = response.radar;
            renderRadar(radarData);
        }
        
        // Find the updated entry in the new radar data
        const updatedRadarEntry = radarData.entries.find(e => e.name === entryData.name);
        
        console.log('Updated entry from radar:', updatedRadarEntry);
        console.log('linkName:', updatedRadarEntry?.linkName);
        console.log('link:', updatedRadarEntry?.link);
        
        if (updatedRadarEntry) {
            // Update current entry reference
            currentDetailEntry = updatedRadarEntry;
            
            // Reset dirty flag after successful save
            isDetailDirty = false;
            
            // First switch back to view mode
            document.getElementById('detail-view-mode').style.display = 'block';
            document.getElementById('detail-edit-mode').style.display = 'none';
            
            // Then update the view mode with new data
            showDetail(updatedRadarEntry);
        }
        
        // Show success message (after mode switch to avoid UI glitch)
        const successMessage = isNewEntry ? 'Entry created successfully!' : 'Entry updated successfully!';
        setTimeout(() => {
            alert(successMessage);
        }, 100);
        
    } catch (error) {
        console.error('Error saving entry:', error);
        alert('Failed to save entry: ' + error.message);
    }
}

// ===== Event Listeners =====
document.addEventListener('DOMContentLoaded', () => {
    // Load projects on start
    loadProjects();
    
    // Handle browser back/forward navigation
    window.addEventListener('hashchange', () => {
        const urlHash = window.location.hash;
        if (urlHash && urlHash.startsWith('#project=')) {
            const projectId = urlHash.substring(9);
            if (projectId !== currentProject) {
                selectProject(projectId);
            }
        }
    });
    
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
    document.getElementById('close-detail').addEventListener('click', closeDetail);
    
    // New entry button
    document.getElementById('new-entry-btn').addEventListener('click', showNewEntryForm);
    
    // Edit entry button
    document.getElementById('edit-entry-btn').addEventListener('click', showEditEntryForm);
    
    // Delete entry button
    document.getElementById('delete-entry-btn').addEventListener('click', deleteEntry);
    
    // Cancel edit entry
    document.getElementById('cancel-edit-btn').addEventListener('click', cancelEditEntry);
    
    // Save edit entry form
    document.getElementById('edit-entry-form').addEventListener('submit', saveEditEntry);
    
    // Search functionality
    document.getElementById('search').addEventListener('input', (e) => {
        const searchTerm = e.target.value.trim();
        if (radarData) {
            renderRadar(radarData, searchTerm);
        }
    });
    
    // Export PNG functionality
    document.getElementById('export-png').addEventListener('click', exportRadarAsPNG);
    
    // Rename project functionality
    document.getElementById('rename-project-btn')?.addEventListener('click', renameProject);
    
    // Delete project functionality
    document.getElementById('delete-project-btn')?.addEventListener('click', deleteProject);
});

// ===== Rename Project Function =====
async function renameProject() {
    if (!currentProject) {
        alert('No project selected');
        return;
    }
    
    const currentName = currentProject.replace('.xlsx', '');
    const newName = prompt('Enter new project name:', currentName);
    
    if (!newName || newName.trim() === '') {
        return;  // User cancelled or entered empty name
    }
    
    if (newName === currentName) {
        return;  // No change
    }
    
    // Validate filename (no special characters except underscore, hyphen, and space)
    if (!/^[a-zA-Z0-9_\- ]+$/.test(newName)) {
        alert('Project name can only contain letters, numbers, spaces, underscores, and hyphens');
        return;
    }
    
    try {
        const response = await apiCall(`/projects/${currentProject}/rename`, {
            method: 'POST',
            body: JSON.stringify({ new_name: newName + '.xlsx' })
        });
        
        // Update current project reference
        currentProject = response.new_name;
        
        // Update UI
        document.getElementById('active-project-name').textContent = newName;
        
        // Reload project list to show new name
        await loadProjects();
        
        alert('Project renamed successfully!');
        
    } catch (error) {
        console.error('Failed to rename project:', error);
        alert('Failed to rename project: ' + error.message);
    }
}

// ===== Delete Project Function =====
async function deleteProject() {
    if (!currentProject) {
        alert('No project selected');
        return;
    }
    
    const projectName = currentProject.replace('.xlsx', '');
    
    // First confirmation
    const firstConfirm = confirm(
        `⚠️ WARNING: You are about to delete the project "${projectName}".\n\n` +
        `This action CANNOT be undone!\n\n` +
        `Click OK to continue, or Cancel to abort.`
    );
    
    if (!firstConfirm) {
        return;
    }
    
    // Second confirmation - require typing project name
    const typedName = prompt(
        `To confirm deletion, please type the project name exactly:\n\n"${projectName}"\n\n` +
        `Type the name and click OK to permanently delete this project:`
    );
    
    if (typedName !== projectName) {
        if (typedName !== null) {  // User didn't cancel
            alert('Project name did not match. Deletion cancelled.');
        }
        return;
    }
    
    try {
        await apiCall(`/projects/${currentProject}`, {
            method: 'DELETE'
        });
        
        // Clear current project
        currentProject = null;
        currentProjectId = null;
        radarData = null;
        
        // Clear UI
        document.getElementById('active-project-name').textContent = 'No project selected';
        document.getElementById('radar').innerHTML = '';
        
        // Switch to view mode
        switchToViewMode();
        
        // Reload project list
        await loadProjects();
        
        alert('Project deleted successfully!');
        
    } catch (error) {
        console.error('Failed to delete project:', error);
        alert('Failed to delete project: ' + error.message);
    }
}

// ===== PNG Export Function using html2canvas =====
async function exportRadarAsPNG() {
    try {
        const svg = document.getElementById('radar');
        
        if (!svg) {
            throw new Error('Radar SVG not found');
        }
        
        // Create a temporary container for export
        const exportContainer = document.createElement('div');
        exportContainer.style.position = 'fixed';
        exportContainer.style.left = '-9999px';
        exportContainer.style.top = '0';
        exportContainer.style.width = (svg.clientWidth + 80) + 'px';  // Add padding width
        exportContainer.style.height = (svg.clientHeight + 140) + 'px';  // Add padding + title height
        exportContainer.style.backgroundColor = '#ffffff';
        exportContainer.style.padding = '40px';
        exportContainer.style.fontFamily = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        
        // Add title with project name and timestamp
        const title = document.createElement('div');
        title.style.textAlign = 'center';
        title.style.marginBottom = '20px';
        
        // Use the full title from radarData.meta.title
        // This comes from the Excel filename (with correct capitalization preserved)
        let projectName = 'Technology Radar';
        if (radarData && radarData.meta && radarData.meta.title) {
            projectName = radarData.meta.title;
        } else if (currentProject) {
            // Fallback to filename
            projectName = currentProject.replace('.xlsx', '');
        }
        const now = new Date();
        const dateStr = now.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
        
        title.innerHTML = `
            <h2 style="margin: 0 0 8px 0; font-size: 24px; font-weight: 600; color: #1e293b;">
                ${projectName}
            </h2>
            <p style="margin: 0; font-size: 14px; color: #64748b;">
                Generated on ${dateStr} at ${timeStr}
            </p>
        `;
        
        // Clone the SVG
        const svgClone = svg.cloneNode(true);
        svgClone.style.display = 'block';
        svgClone.style.margin = '0 auto';
        svgClone.setAttribute('width', svg.clientWidth);
        svgClone.setAttribute('height', svg.clientHeight);
        
        exportContainer.appendChild(title);
        exportContainer.appendChild(svgClone);
        document.body.appendChild(exportContainer);
        
        // Use html2canvas to capture the container
        const canvas = await html2canvas(exportContainer, {
            backgroundColor: '#ffffff',
            scale: 2, // Higher quality
            logging: false,
            useCORS: true,
            allowTaint: true,
            width: svg.clientWidth + 80,
            height: svg.clientHeight + 140
        });
        
        // Remove temporary container
        document.body.removeChild(exportContainer);
        
        // Convert canvas to blob and download
        canvas.toBlob(function(blob) {
            if (!blob) {
                throw new Error('Failed to create image blob');
            }
            
            const link = document.createElement('a');
            const timestamp = new Date().toISOString().slice(0, 10);
            const downloadName = projectName.replace(/_/g, '-');
            link.download = `${downloadName}-${timestamp}.png`;
            link.href = URL.createObjectURL(blob);
            link.click();
            
            // Clean up
            setTimeout(() => URL.revokeObjectURL(link.href), 100);
        }, 'image/png');
        
    } catch (error) {
        console.error('Error exporting PNG:', error);
        alert('Failed to export PNG: ' + (error.message || 'Unknown error'));
    }
}

// ===== Import Project Modal =====
function showImportModal() {
    const modal = document.getElementById('import-project-modal');
    modal.style.display = 'flex';
    
    // Reset drop zone
    const dropZone = document.getElementById('drop-zone');
    const uploadProgress = document.getElementById('upload-progress');
    const dropZoneContent = dropZone.querySelector('.drop-zone-content');
    
    dropZoneContent.style.display = 'flex';
    uploadProgress.style.display = 'none';
}

function hideImportModal() {
    const modal = document.getElementById('import-project-modal');
    modal.style.display = 'none';
}

async function handleFileUpload(file) {
    if (!file) return;
    
    // Validate file type
    if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
        alert('Please upload an Excel file (.xlsx or .xls)');
        return;
    }
    
    const dropZone = document.getElementById('drop-zone');
    const uploadProgress = document.getElementById('upload-progress');
    const dropZoneContent = dropZone.querySelector('.drop-zone-content');
    const uploadStatus = document.getElementById('upload-status');
    const progressFill = document.getElementById('progress-fill');
    
    // Show progress
    dropZoneContent.style.display = 'none';
    uploadProgress.style.display = 'block';
    uploadStatus.textContent = 'Uploading...';
    progressFill.style.width = `${PROGRESS_UPLOAD_START}%`;
    
    try {
        // Create FormData
        const formData = new FormData();
        formData.append('file', file);
        
        // Upload file
        const response = await fetch('/api/projects/upload', {
            method: 'POST',
            body: formData
        });
        
        progressFill.style.width = `${PROGRESS_UPLOAD_COMPLETE}%`;
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        const result = await response.json();
        progressFill.style.width = `${PROGRESS_DONE}%`;
        uploadStatus.textContent = 'Upload successful! Refreshing projects...';
        
        // Wait a moment then refresh projects
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Refresh project list
        await loadProjects();
        
        // Close modal
        hideImportModal();
        
        // Show success message
        alert(`Project "${result.project_name}" imported successfully!`);
        
        // Load the new project
        if (result.project_id) {
            try {
                await selectProject(result.project_id);
            } catch (loadError) {
                console.error('Failed to load project after import:', loadError);
                alert(`Project imported successfully, but failed to load: ${loadError.message}`);
            }
        }
        
    } catch (error) {
        console.error('Upload error:', error);
        uploadStatus.textContent = 'Upload failed: ' + error.message;
        progressFill.style.width = '0%';
        
        // Show error and reset after delay
        setTimeout(() => {
            dropZoneContent.style.display = 'flex';
            uploadProgress.style.display = 'none';
        }, ERROR_DISPLAY_TIMEOUT);
    }
}

// Event listeners for import modal
document.getElementById('import-project-btn').addEventListener('click', showImportModal);
document.getElementById('close-import-modal').addEventListener('click', hideImportModal);
document.getElementById('close-import-modal-btn').addEventListener('click', hideImportModal);

// Close modal when clicking outside
document.getElementById('import-project-modal').addEventListener('click', (e) => {
    if (e.target.id === 'import-project-modal') {
        hideImportModal();
    }
});

// Drag and drop handlers
const dropZone = document.getElementById('drop-zone');

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('drag-over');
});

dropZone.addEventListener('dragleave', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
});

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

// Browse button handler
document.getElementById('browse-file-btn').addEventListener('click', () => {
    document.getElementById('file-input').click();
});

document.getElementById('file-input').addEventListener('change', (e) => {
    const files = e.target.files;
    if (files.length > 0) {
        handleFileUpload(files[0]);
    }
});

// Made with Bob
