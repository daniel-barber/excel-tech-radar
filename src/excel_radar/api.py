"""
Flask API server for Excel Tech Radar management.
Provides REST endpoints for managing radar projects and entries.
"""
import json
import re
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import pandas as pd
from openpyxl import Workbook, load_workbook

from .loader import auto_discover_config, load_excel, validate_entries
from .builder import build_radar_json


class RadarAPI:
    """Flask API for radar management."""
    
    def __init__(self, data_dir: str = "data", dist_dir: str = "dist"):
        self.app = Flask(__name__)
        CORS(self.app)  # Enable CORS for frontend
        
        self.data_dir = Path(data_dir)
        self.dist_dir = Path(dist_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)
        
        self._register_routes()
    
    def _build_radar_for_project(self, project_id: str) -> Dict[str, Any]:
        """Helper to build radar JSON for a project."""
        excel_file = self.data_dir / f"{project_id}.xlsx"
        
        # Determine sheet name
        try:
            xls = pd.ExcelFile(excel_file)
            sheet_name = 'Radar' if 'Radar' in xls.sheet_names else xls.sheet_names[0]
        except:
            sheet_name = 'Sheet1'
        
        # Auto-discover config
        config = auto_discover_config(
            excel_path=excel_file,
            sheet_name=sheet_name,
            title=project_id.replace('_', ' ')
        )
        
        # Load and validate entries
        raw_entries = load_excel(excel_file, sheet_name, config, allow_duplicates=False)
        entries = validate_entries(raw_entries)
        
        # Build radar JSON (to temp path, we'll return the dict)
        temp_json = self.dist_dir / 'temp_radar.json'
        radar_data = build_radar_json(config, entries, temp_json)
        
        return radar_data
    
    def _register_routes(self):
        """Register all API routes."""
        
        @self.app.route('/api/projects', methods=['GET'])
        def list_projects():
            """List all radar projects (Excel files in data/)."""
            try:
                projects = []
                for excel_file in self.data_dir.glob('*.xlsx'):
                    if excel_file.name.startswith('~$'):  # Skip temp files
                        continue
                    
                    stat = excel_file.stat()
                    
                    # Try to read display name from Excel properties
                    display_name = None
                    try:
                        wb = load_workbook(excel_file, read_only=True)
                        if wb.properties and wb.properties.title:
                            display_name = wb.properties.title
                        wb.close()
                    except Exception as e:
                        pass
                    
                    # Fallback to filename-based name if no stored display name
                    if not display_name:
                        # Use filename directly, just replace underscores with spaces
                        # Don't apply .title() as it would change "Stadt-ZH" to "Stadt-Zh"
                        display_name = excel_file.stem.replace('_', ' ')
                    
                    projects.append({
                        'id': excel_file.stem,
                        'name': display_name,
                        'filename': excel_file.name,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
                
                # Sort by modified date (newest first)
                projects.sort(key=lambda x: x['modified'], reverse=True)
                
                return jsonify({'projects': projects})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>', methods=['GET'])
        def get_project(project_id: str):
            """Get project details and radar data."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                radar_data = self._build_radar_for_project(project_id)
                return jsonify(radar_data)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/rename', methods=['POST'])
        def rename_project(project_id: str):
            """Rename a project (rename the Excel file)."""
            try:
                old_file = self.data_dir / f"{project_id}.xlsx"
                if not old_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                data = request.json
                new_name = data.get('new_name')
                
                if not new_name:
                    return jsonify({'error': 'new_name is required'}), 400
                
                # Validate filename (no special characters except underscore, hyphen, and space)
                # Remove .xlsx extension for validation if present
                name_to_validate = new_name.replace('.xlsx', '')
                if not re.match(r'^[a-zA-Z0-9_\- ]+$', name_to_validate):
                    return jsonify({'error': 'Project name can only contain letters, numbers, spaces, underscores, and hyphens'}), 400
                
                # Ensure .xlsx extension
                if not new_name.endswith('.xlsx'):
                    new_name += '.xlsx'
                
                new_file = self.data_dir / new_name
                
                # Check if target already exists
                if new_file.exists():
                    return jsonify({'error': 'A project with that name already exists'}), 400
                
                # Rename the file
                old_file.rename(new_file)
                
                return jsonify({
                    'success': True,
                    'old_name': f"{project_id}.xlsx",
                    'new_name': new_name
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/excel', methods=['GET'])
        def get_excel_data(project_id: str):
            """Get raw Excel data as JSON for editing."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                # Read Excel - try to get first sheet or 'Radar' sheet
                try:
                    # Try 'Radar' sheet first (our standard)
                    df = pd.read_excel(excel_file, sheet_name='Radar')
                except:
                    try:
                        # Try first sheet
                        df = pd.read_excel(excel_file, sheet_name=0)
                    except:
                        # Try 'Sheet1' as fallback
                        df = pd.read_excel(excel_file, sheet_name='Sheet1')
                
                # Replace NaN/inf with None for valid JSON
                df = df.replace([float('nan'), float('inf'), float('-inf')], None)
                
                # Convert to records (list of dicts)
                records = df.to_dict('records')
                
                # Get column names
                columns = df.columns.tolist()
                
                # Use Flask's jsonify which handles None properly
                return jsonify({
                    'columns': columns,
                    'rows': records,
                    'rowCount': len(records)
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/excel', methods=['PUT'])
        def update_excel_data(project_id: str):
            """Update Excel data from JSON."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                data = request.json
                rows = data.get('rows', [])
                
                if not rows:
                    return jsonify({'error': 'No rows provided'}), 400
                
                # Determine sheet name from original file
                try:
                    xls = pd.ExcelFile(excel_file)
                    sheet_name = 'Radar' if 'Radar' in xls.sheet_names else xls.sheet_names[0]
                except:
                    sheet_name = 'Sheet1'
                
                # Create DataFrame from rows
                df = pd.DataFrame(rows)
                
                # Backup original file
                backup_file = excel_file.with_suffix('.xlsx.bak')
                shutil.copy2(excel_file, backup_file)
                
                # Write to Excel
                df.to_excel(excel_file, sheet_name=sheet_name, index=False)
                
                # Rebuild radar
                radar_data = self._build_radar_for_project(project_id)
                
                # Write radar.json to dist
                radar_json_file = self.dist_dir / 'radar.json'
                with open(radar_json_file, 'w') as f:
                    json.dump(radar_data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': f'Updated {len(rows)} rows',
                    'radar': radar_data
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/rows', methods=['POST'])
        def add_row(project_id: str):
            """Add a new row to Excel."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                row_data = request.json
                
                # Determine sheet name
                try:
                    xls = pd.ExcelFile(excel_file)
                    sheet_name = 'Radar' if 'Radar' in xls.sheet_names else xls.sheet_names[0]
                except:
                    sheet_name = 'Sheet1'
                
                # Read existing data
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                # Ensure all required columns exist
                required_cols = ['name', 'ring', 'quadrant', 'status', 'description', 'tags', 'link', 'linkName']
                for col in required_cols:
                    if col not in df.columns:
                        df[col] = pd.Series(dtype='object')
                
                # Append new row
                new_row = pd.DataFrame([row_data])
                df = pd.concat([df, new_row], ignore_index=True)
                
                # Write back
                df.to_excel(excel_file, sheet_name=sheet_name, index=False)
                
                # Rebuild radar
                radar_data = self._build_radar_for_project(project_id)
                
                # Write radar.json to dist
                radar_json_file = self.dist_dir / 'radar.json'
                with open(radar_json_file, 'w') as f:
                    json.dump(radar_data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': 'Row added',
                    'radar': radar_data
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/rows/<int:row_index>', methods=['DELETE'])
        def delete_row(project_id: str, row_index: int):
            """Delete a row from Excel."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                # Determine sheet name
                try:
                    xls = pd.ExcelFile(excel_file)
                    sheet_name = 'Radar' if 'Radar' in xls.sheet_names else xls.sheet_names[0]
                except:
                    sheet_name = 'Sheet1'
                
                # Read existing data
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if row_index < 0 or row_index >= len(df):
                    return jsonify({'error': 'Invalid row index'}), 400
                
                # Drop row
                df = df.drop(row_index).reset_index(drop=True)
                
                # Write back
                df.to_excel(excel_file, sheet_name=sheet_name, index=False)
                
                # Rebuild radar and return updated data
                radar_data = self._build_radar_for_project(project_id)
                
                # Write radar.json to dist
                radar_json_file = self.dist_dir / 'radar.json'
                with open(radar_json_file, 'w') as f:
                    json.dump(radar_data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': 'Row deleted',
                    'radar': radar_data
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/rows/<int:row_index>', methods=['PUT'])
        def update_row(project_id: str, row_index: int):
            """Update a single row in Excel."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'File not found'}), 404
                
                row_data = request.json
                
                # Determine sheet name
                try:
                    xls = pd.ExcelFile(excel_file)
                    sheet_name = 'Radar' if 'Radar' in xls.sheet_names else xls.sheet_names[0]
                except:
                    sheet_name = 'Sheet1'
                
                # Read existing data
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if row_index < 0 or row_index >= len(df):
                    return jsonify({'error': 'Invalid row index'}), 400
                
                # Update the row - handle data type conversions
                # Add missing columns if they don't exist
                for key in row_data.keys():
                    if key not in df.columns:
                        # Add column with empty string default and explicit string dtype
                        df[key] = pd.Series([''] * len(df), dtype='object')
                
                # First pass: convert column types if needed
                # Convert any numeric columns that should be strings
                string_fields = ['name', 'ring', 'quadrant', 'status', 'description', 'tags', 'link', 'linkName', 'customer', 'owner']
                for key in string_fields:
                    if key in df.columns and pd.api.types.is_numeric_dtype(df[key]):
                        df[key] = df[key].astype('object')
                
                # Also check incoming data for string values going to numeric columns
                for key, value in row_data.items():
                    if key in df.columns:
                        # If trying to set a string value (including empty string) to a numeric column, convert column to object first
                        if isinstance(value, str) and pd.api.types.is_numeric_dtype(df[key]):
                            df[key] = df[key].astype('object')
                
                # Second pass: set values
                for key, value in row_data.items():
                    if key in df.columns:
                        # Convert tags array to comma-separated string
                        if key == 'tags' and isinstance(value, list):
                            value = ', '.join(value) if value else ''
                        # Convert boolean to proper format
                        elif key == 'isNew' and isinstance(value, bool):
                            value = value
                        # Handle None/null/empty values based on column dtype
                        elif value is None or value == '':
                            # For numeric columns, use None (becomes NaN in pandas)
                            if pd.api.types.is_numeric_dtype(df[key]):
                                value = None
                            # For string columns, use empty string
                            else:
                                value = ''
                        
                        try:
                            df.at[row_index, key] = value
                        except Exception as e:
                            # Log the error with details
                            print(f"Error setting {key}={value} (type: {type(value)}, dtype: {df[key].dtype}): {e}")
                            raise ValueError(f"Invalid value '{value}' for dtype '{df[key].dtype}'")
                
                # Backup original file
                backup_file = excel_file.with_suffix('.xlsx.bak')
                shutil.copy2(excel_file, backup_file)
                
                # Write back
                df.to_excel(excel_file, sheet_name=sheet_name, index=False)
                
                # Rebuild radar
                radar_data = self._build_radar_for_project(project_id)
                
                return jsonify({
                    'success': True,
                    'message': 'Row updated',
                    'radar': radar_data
                })
            except Exception as e:
                import traceback
                traceback.print_exc()
                return jsonify({'error': str(e)}), 500
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects', methods=['POST'])
        def create_project():
            """Create a new radar project."""
            try:
                data = request.json
                project_name = data.get('name', 'New Radar')
                template = data.get('template', 'default')
                
                # Sanitize project name for filename (allow alphanumeric, hyphens, and underscores)
                project_id = project_name.lower().replace(' ', '_')
                project_id = ''.join(c for c in project_id if c.isalnum() or c in ('_', '-'))
                
                excel_file = self.data_dir / f"{project_id}.xlsx"
                
                # Check if exists
                if excel_file.exists():
                    return jsonify({'error': 'Project already exists'}), 400
                
                # Create new Excel with template
                wb = Workbook()
                ws = wb.active
                ws.title = 'Sheet1'
                
                # Store the original display name in document properties
                wb.properties.title = project_name
                
                # Add headers based on template
                if template == 'default':
                    headers = ['name', 'ring', 'quadrant', 'status', 'description', 'tags', 'link', 'linkName']
                    ws.append(headers)
                    # No sample rows - start with empty project
                
                wb.save(excel_file)
                
                return jsonify({
                    'success': True,
                    'project': {
                        'id': project_id,
                        'name': project_name,
                        'filename': excel_file.name,
                    }
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>', methods=['DELETE'])
        def delete_project(project_id: str):
            """Delete a radar project."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                # Move to trash (rename with .deleted suffix)
                deleted_file = excel_file.with_suffix('.xlsx.deleted')
                excel_file.rename(deleted_file)
                
                return jsonify({'success': True, 'message': 'Project deleted'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/download', methods=['GET'])
        def download_project(project_id: str):
            """Download Excel file."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                return send_file(
                    excel_file,
                    as_attachment=True,
                    download_name=f"{project_id}.xlsx"
                )
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/projects/<project_id>/build', methods=['POST'])
        def build_project(project_id: str):
            """Build radar JSON for a project."""
            try:
                excel_file = self.data_dir / f"{project_id}.xlsx"
                if not excel_file.exists():
                    return jsonify({'error': 'Project not found'}), 404
                
                radar_data = self._build_radar_for_project(project_id)
                
                # Write to dist
                radar_json_file = self.dist_dir / 'radar.json'
                with open(radar_json_file, 'w') as f:
                    json.dump(radar_data, f, indent=2)
                
                return jsonify({
                    'success': True,
                    'message': 'Radar built successfully',
                    'radar': radar_data
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        # Serve static files
        @self.app.route('/')
        def index():
            """Serve unified interface."""
            web_dir = Path(__file__).parent.parent.parent / 'web'
            return send_from_directory(str(web_dir), 'unified.html')
        
        @self.app.route('/<path:path>')
        def static_files(path):
            """Serve static files from web/ or dist/."""
            # Get absolute paths
            web_dir = Path(__file__).parent.parent.parent / 'web'
            dist_dir = Path(__file__).parent.parent.parent / 'dist'
            
            # Try web/ first, then dist/
            web_file = web_dir / path
            if web_file.exists():
                return send_from_directory(str(web_dir), path)
            
            dist_file = dist_dir / path
            if dist_file.exists():
                return send_from_directory(str(dist_dir), path)
            
            return jsonify({'error': 'File not found'}), 404
    
    def run(self, host='127.0.0.1', port=5173, debug=True):
        """Run the Flask server."""
        print(f"🚀 Starting Radar API server on http://{host}:{port}")
        print(f"📁 Data directory: {self.data_dir.absolute()}")
        print(f"📦 Dist directory: {self.dist_dir.absolute()}")
        self.app.run(host=host, port=port, debug=debug)


def create_api(data_dir: str = "data", dist_dir: str = "dist") -> Flask:
    """Create and return Flask app instance."""
    api = RadarAPI(data_dir=data_dir, dist_dir=dist_dir)
    return api.app

# Made with Bob
