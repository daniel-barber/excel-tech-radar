# Phase 3: Unified Interface - Implementation Guide

## Overview
This document describes the unified interface for Excel Tech Radar that combines project management, Excel editing, and radar visualization in a single web application.

## ✅ Completed Components

### 1. Backend API (src/excel_radar/api.py)
Complete Flask REST API with the following endpoints:

- **GET /api/projects** - List all radar projects
- **GET /api/projects/:id** - Get project radar data
- **GET /api/projects/:id/excel** - Get Excel data as JSON
- **PUT /api/projects/:id/excel** - Update Excel data
- **POST /api/projects/:id/rows** - Add new row
- **DELETE /api/projects/:id/rows/:index** - Delete row
- **POST /api/projects** - Create new project
- **DELETE /api/projects/:id** - Delete project
- **GET /api/projects/:id/download** - Download Excel file
- **POST /api/projects/:id/build** - Build radar JSON

### 2. CLI Command (src/excel_radar/cli.py)
Added `excel-radar serve` command to start the unified interface server:

```bash
excel-radar serve --host 127.0.0.1 --port 5173
```

### 3. Dependencies (pyproject.toml)
Added Flask and Flask-CORS to dependencies.

## 🚧 Remaining Work

### Frontend Implementation

You need to create a new unified interface that replaces the current simple viewer. Here's the recommended approach:

#### Option 1: Enhance Current Interface (Recommended)
Modify the existing `web/index.html`, `web/app.js`, and `web/style.css` to add:

1. **Left Sidebar** (250px wide):
   - Project list loaded from `/api/projects`
   - "New Radar" button
   - Click project to switch active radar
   - Show active project with highlight

2. **Center Area** (keep existing radar visualization):
   - Current D3 radar visualization
   - Zoom controls (already implemented)
   - Export button (already implemented)

3. **Right Panel** (300px wide, toggleable):
   - **View Mode**: Show entry details (already implemented)
   - **Edit Mode**: Spreadsheet grid for editing Excel data

4. **Top Bar**:
   - View/Edit mode toggle button
   - Active project name
   - Save button (in edit mode)

#### Option 2: Use AG Grid for Excel Editing
AG Grid Community Edition provides a powerful spreadsheet-like interface:

```html
<!-- Add to index.html -->
<script src="https://cdn.jsdelivr.net/npm/ag-grid-community/dist/ag-grid-community.min.js"></script>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-grid.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/ag-grid-community/styles/ag-theme-alpine.css">
```

```javascript
// Initialize AG Grid
const gridOptions = {
    columnDefs: columns.map(col => ({ field: col, editable: true })),
    rowData: rows,
    onCellValueChanged: (event) => {
        // Mark as dirty, enable save button
    }
};

const grid = new agGrid.Grid(gridElement, gridOptions);
```

## 📐 Recommended Layout

```
┌─────────────────────────────────────────────────────────────┐
│  Excel Tech Radar                    [View] [Edit]  [Save]  │
├──────────┬──────────────────────────────────────┬───────────┤
│          │                                      │           │
│ Projects │         Radar Visualization          │  Details  │
│          │                                      │    or     │
│ • Proj 1 │              [Radar]                 │   Grid    │
│ • Proj 2 │                                      │  Editor   │
│ • Proj 3 │         [Zoom Controls]              │           │
│          │                                      │           │
│ [+ New]  │                                      │           │
│          │                                      │           │
└──────────┴──────────────────────────────────────┴───────────┘
```

## 🎨 CSS Structure

```css
.app-container {
    display: grid;
    grid-template-columns: 250px 1fr 300px;
    grid-template-rows: 60px 1fr;
    height: 100vh;
}

.app-header {
    grid-column: 1 / -1;
    /* Top bar */
}

.sidebar {
    grid-row: 2;
    /* Project list */
}

.main-content {
    grid-row: 2;
    /* Radar visualization */
}

.right-panel {
    grid-row: 2;
    /* Details or editor */
}
```

## 🔄 Data Flow

### View Mode
1. User selects project from sidebar
2. Frontend calls `GET /api/projects/:id`
3. Radar data loaded and visualized
4. Click entry → show details in right panel

### Edit Mode
1. User clicks "Edit" button
2. Frontend calls `GET /api/projects/:id/excel`
3. Excel data loaded into AG Grid
4. User edits cells
5. Click "Save" → `PUT /api/projects/:id/excel`
6. Backend rebuilds radar automatically
7. Frontend reloads radar visualization

### Create New Project
1. User clicks "+ New" button
2. Modal dialog asks for project name
3. Frontend calls `POST /api/projects`
4. New project appears in sidebar
5. Switch to new project automatically

## 🚀 Quick Start

### 1. Start the Server
```bash
# Install dependencies (if not already installed)
pip install -e .

# Start unified interface server
excel-radar serve
```

### 2. Access the Interface
Open browser to: http://127.0.0.1:5173

### 3. Test API Endpoints
```bash
# List projects
curl http://127.0.0.1:5173/api/projects

# Get project data
curl http://127.0.0.1:5173/api/projects/horizon_cadence_transformed

# Get Excel data
curl http://127.0.0.1:5173/api/projects/horizon_cadence_transformed/excel
```

## 📝 Implementation Checklist

- [ ] Create left sidebar component
- [ ] Add project list with API integration
- [ ] Implement project switcher
- [ ] Add "New Radar" dialog
- [ ] Integrate AG Grid for Excel editing
- [ ] Add View/Edit mode toggle
- [ ] Implement save functionality
- [ ] Add loading states and error handling
- [ ] Style with modern UI (match current radar colors)
- [ ] Test all CRUD operations
- [ ] Add keyboard shortcuts (Ctrl+S to save, etc.)
- [ ] Add confirmation dialogs for delete operations
- [ ] Implement undo/redo for edits
- [ ] Add export options (Excel, JSON, PNG)

## 🎯 Next Steps

1. **Immediate**: Modify `web/index.html` to add the 3-column layout
2. **Then**: Add project list sidebar with API calls
3. **Then**: Integrate AG Grid for editing
4. **Finally**: Polish UI and add all features

## 💡 Tips

- Keep the current radar visualization code intact
- Use CSS Grid for layout (easier than flexbox for this)
- Add loading spinners for API calls
- Use localStorage to remember last selected project
- Add keyboard shortcuts for power users
- Consider adding a "Recent Projects" section
- Add search/filter for large project lists

## 🐛 Known Issues

- API has some TypeScript linter warnings (harmless, openpyxl types)
- Need to handle concurrent edits (add optimistic locking)
- Large Excel files may be slow (consider pagination)

## 📚 Resources

- [AG Grid Documentation](https://www.ag-grid.com/javascript-data-grid/)
- [Flask-CORS Documentation](https://flask-cors.readthedocs.io/)
- [D3.js Examples](https://observablehq.com/@d3/gallery)