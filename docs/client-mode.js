// Client-Only Mode for GitHub Pages
// Adds LocalStorage-based project management and Excel file upload

// ===== Client-Only State =====
let hasBackend = false;
let clientProjects = {};

// ===== Backend Detection =====
async function detectBackend() {
    try {
        const response = await fetch('/api/health', { 
            method: 'GET',
            cache: 'no-cache'
        });
        hasBackend = response.ok;
    } catch (error) {
        hasBackend = false;
    }
    
    console.log(`Backend ${hasBackend ? 'detected' : 'not available'} - using ${hasBackend ? 'server' : 'client-only'} mode`);
    return hasBackend;
}

// ===== LocalStorage Management =====
function saveProjectsToStorage() {
    try {
        localStorage.setItem('radarProjects', JSON.stringify(clientProjects));
        console.log('Projects saved to LocalStorage:', Object.keys(clientProjects));
    } catch (error) {
        console.error('Failed to save to LocalStorage:', error);
        alert('Failed to save project. Storage may be full.');
    }
}

function loadProjectsFromStorage() {
    try {
        const stored = localStorage.getItem('radarProjects');
        if (stored) {
            clientProjects = JSON.parse(stored);
            console.log('Loaded projects from LocalStorage:', Object.keys(clientProjects));
        } else {
            clientProjects = {};
        }
    } catch (error) {
        console.error('Failed to load from LocalStorage:', error);
        clientProjects = {};
    }
}

function getClientProjects() {
    return Object.keys(clientProjects).map(id => ({
        id: id,
        name: clientProjects[id].name || id,
        modified: clientProjects[id].modified || new Date().toISOString()
    }));
}

function getClientProject(projectId) {
    return clientProjects[projectId]?.data || null;
}

function saveClientProject(projectId, data, name) {
    clientProjects[projectId] = {
        name: name || projectId,
        data: data,
        modified: new Date().toISOString()
    };
    saveProjectsToStorage();
}

function deleteClientProject(projectId) {
    delete clientProjects[projectId];
    saveProjectsToStorage();
}

function renameClientProject(oldId, newId, newName) {
    if (clientProjects[oldId]) {
        clientProjects[newId] = {
            ...clientProjects[oldId],
            name: newName || newId,
            modified: new Date().toISOString()
        };
        delete clientProjects[oldId];
        saveProjectsToStorage();
    }
}

// ===== Excel File Parsing =====
function parseExcelFile(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        reader.onload = function(e) {
            try {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, { type: 'array' });
                
                // Get the first sheet
                const firstSheetName = workbook.SheetNames[0];
                const worksheet = workbook.Sheets[firstSheetName];
                
                // Convert to JSON
                const jsonData = XLSX.utils.sheet_to_json(worksheet);
                
                // Transform to radar format
                const radarData = transformExcelToRadar(jsonData);
                
                resolve(radarData);
            } catch (error) {
                console.error('Excel parsing error:', error);
                reject(new Error('Failed to parse Excel file: ' + error.message));
            }
        };
        
        reader.onerror = function() {
            reject(new Error('Failed to read file'));
        };
        
        reader.readAsArrayBuffer(file);
    });
}

function transformExcelToRadar(jsonData) {
    // Extract unique rings and quadrants
    const rings = [...new Set(jsonData.map(row => row.ring || row.Ring).filter(Boolean))];
    const quadrants = [...new Set(jsonData.map(row => row.quadrant || row.Quadrant).filter(Boolean))];
    
    // Transform entries
    const entries = jsonData.map((row, index) => ({
        id: index + 1,
        name: row.name || row.Name || `Entry ${index + 1}`,
        ring: row.ring || row.Ring || rings[0] || 'Adopt',
        quadrant: row.quadrant || row.Quadrant || quadrants[0] || 'Tools',
        status: row.status || row.Status || 'new',
        description: row.description || row.Description || '',
        tags: row.tags || row.Tags || '',
        link: row.link || row.Link || '',
        linkName: row.linkName || row.LinkName || row.link_name || row.Link_Name || '',
        dealSize: row.dealSize || row.DealSize || row.deal_size || row.Deal_Size || '',
        propensityToWin: row.propensityToWin || row.PropensityToWin || row.propensity_to_win || row.Propensity_To_Win || '',
        strategic: row.strategic || row.Strategic || false
    }));
    
    return {
        rings: rings.map((name, index) => ({ name, color: getDefaultRingColor(index) })),
        quadrants: quadrants.map(name => ({ name })),
        entries: entries
    };
}

function getDefaultRingColor(index) {
    const colors = ['#93c47d', '#93d2c2', '#fbdb84', '#efafa9'];
    return colors[index % colors.length];
}

// ===== File Upload Handler =====
function setupFileUpload() {
    const importBtn = document.getElementById('import-project-btn');
    const modal = document.getElementById('import-project-modal');
    const closeBtn = document.getElementById('close-import-modal');
    const closeBtnBottom = document.getElementById('close-import-modal-btn');
    const fileInput = document.getElementById('file-input');
    const browseBtn = document.getElementById('browse-file-btn');
    const dropZone = document.getElementById('drop-zone');
    
    if (!importBtn || !modal) return;
    
    // Show modal
    importBtn.addEventListener('click', () => {
        modal.style.display = 'flex';
    });
    
    // Close modal
    const closeModal = () => {
        modal.style.display = 'none';
    };
    
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    if (closeBtnBottom) closeBtnBottom.addEventListener('click', closeModal);
    
    // Browse button
    if (browseBtn && fileInput) {
        browseBtn.addEventListener('click', () => {
            fileInput.click();
        });
    }
    
    // File input change
    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                await handleFileUpload(file);
                closeModal();
            }
        });
    }
    
    // Drag and drop
    if (dropZone) {
        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropZone.classList.add('drag-over');
        });
        
        dropZone.addEventListener('dragleave', () => {
            dropZone.classList.remove('drag-over');
        });
        
        dropZone.addEventListener('drop', async (e) => {
            e.preventDefault();
            dropZone.classList.remove('drag-over');
            
            const file = e.dataTransfer.files[0];
            if (file && (file.name.endsWith('.xlsx') || file.name.endsWith('.xls'))) {
                await handleFileUpload(file);
                closeModal();
            } else {
                alert('Please upload an Excel file (.xlsx or .xls)');
            }
        });
    }
}

async function handleFileUpload(file) {
    const uploadProgress = document.getElementById('upload-progress');
    const uploadStatus = document.getElementById('upload-status');
    const progressFill = document.getElementById('progress-fill');
    
    try {
        // Show progress
        if (uploadProgress) {
            uploadProgress.style.display = 'block';
            uploadStatus.textContent = 'Parsing Excel file...';
            progressFill.style.width = '30%';
        }
        
        // Parse Excel file
        const radarData = await parseExcelFile(file);
        
        if (uploadProgress) {
            uploadStatus.textContent = 'Saving project...';
            progressFill.style.width = '70%';
        }
        
        // Generate project ID from filename
        const projectId = file.name.replace(/\.(xlsx|xls)$/i, '').replace(/[^a-z0-9]/gi, '_').toLowerCase();
        const projectName = file.name.replace(/\.(xlsx|xls)$/i, '');
        
        // Save to LocalStorage
        saveClientProject(projectId, radarData, projectName);
        
        if (uploadProgress) {
            uploadStatus.textContent = 'Complete!';
            progressFill.style.width = '100%';
        }
        
        // Reload projects and select the new one
        await loadProjects();
        await selectProject(projectId);
        
        // Hide progress after a delay
        setTimeout(() => {
            if (uploadProgress) {
                uploadProgress.style.display = 'none';
                progressFill.style.width = '0%';
            }
        }, 1000);
        
    } catch (error) {
        console.error('File upload error:', error);
        alert('Failed to import file: ' + error.message);
        
        if (uploadProgress) {
            uploadProgress.style.display = 'none';
        }
    }
}

// ===== Export to Excel =====
function exportToExcel(projectId, radarData) {
    try {
        // Create worksheet data
        const wsData = radarData.entries.map(entry => ({
            name: entry.name,
            ring: entry.ring,
            quadrant: entry.quadrant,
            status: entry.status || '',
            description: entry.description || '',
            tags: entry.tags || '',
            link: entry.link || '',
            linkName: entry.linkName || '',
            dealSize: entry.dealSize || '',
            propensityToWin: entry.propensityToWin || '',
            strategic: entry.strategic || false
        }));
        
        // Create workbook
        const wb = XLSX.utils.book_new();
        const ws = XLSX.utils.json_to_sheet(wsData);
        
        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Radar Data');
        
        // Generate filename
        const filename = `${projectId}_${new Date().toISOString().split('T')[0]}.xlsx`;
        
        // Download
        XLSX.writeFile(wb, filename);
        
        console.log('Exported to Excel:', filename);
    } catch (error) {
        console.error('Export error:', error);
        alert('Failed to export to Excel: ' + error.message);
    }
}

// ===== Initialize Client Mode =====
async function initializeClientMode() {
    // Detect backend
    await detectBackend();
    
    if (!hasBackend) {
        console.log('Running in client-only mode');
        
        // Load projects from LocalStorage
        loadProjectsFromStorage();
        
        // Setup file upload
        setupFileUpload();
        
        // Add export button handler
        const saveBtn = document.getElementById('save-btn');
        if (saveBtn && currentMode === 'edit') {
            // Add export option
            const exportBtn = document.createElement('button');
            exportBtn.textContent = '📥 Export Excel';
            exportBtn.className = 'save-btn';
            exportBtn.style.marginLeft = '10px';
            exportBtn.addEventListener('click', () => {
                if (currentProjectId && radarData) {
                    exportToExcel(currentProjectId, radarData);
                }
            });
            saveBtn.parentNode.insertBefore(exportBtn, saveBtn.nextSibling);
        }
    }
}

// Export functions for use in main app
window.clientMode = {
    hasBackend: () => hasBackend,
    getProjects: getClientProjects,
    getProject: getClientProject,
    saveProject: saveClientProject,
    deleteProject: deleteClientProject,
    renameProject: renameClientProject,
    exportToExcel: exportToExcel,
    initialize: initializeClientMode
};

// Made with Bob
