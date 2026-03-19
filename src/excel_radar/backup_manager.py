"""
Backup and maintenance manager for Excel Tech Radar.
Handles backup creation, restoration, cleanup, and data export/import.
"""
import json
import shutil
import zipfile
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import pandas as pd

from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class BackupInfo:
    """Information about a backup file."""
    project_id: str
    backup_path: Path
    timestamp: datetime
    size_bytes: int
    backup_type: str  # 'auto', 'manual', 'pre_update'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'project_id': self.project_id,
            'backup_path': str(self.backup_path),
            'timestamp': self.timestamp.isoformat(),
            'size_bytes': self.size_bytes,
            'size_mb': round(self.size_bytes / (1024 * 1024), 2),
            'backup_type': self.backup_type,
            'age_hours': round((datetime.now() - self.timestamp).total_seconds() / 3600, 1)
        }


class BackupManager:
    """Manages backups, cleanup, and data export/import."""
    
    def __init__(self, data_dir: Path, max_backups: int = 5, retention_days: int = 30):
        """
        Initialize the backup manager.
        
        Args:
            data_dir: Directory containing project files
            max_backups: Maximum number of backups to keep per project
            retention_days: Days to retain deleted files
        """
        self.data_dir = Path(data_dir)
        self.backup_dir = self.data_dir / '.backups'
        self.trash_dir = self.data_dir / '.trash'
        self.max_backups = max_backups
        self.retention_days = retention_days
        self.data_dir.mkdir(exist_ok=True)
        self.backup_dir.mkdir(exist_ok=True)
        self.trash_dir.mkdir(exist_ok=True)
        logger.info(f"BackupManager initialized: data_dir={data_dir}, backup_dir={self.backup_dir}, trash_dir={self.trash_dir}, max_backups={max_backups}, retention_days={retention_days}")
    
    def create_backup(self, project_id: str, backup_type: str = 'manual') -> Optional[Path]:
        """
        Create a timestamped backup of a project file.
        
        Args:
            project_id: Project identifier
            backup_type: Type of backup ('auto', 'manual', 'pre_update')
        
        Returns:
            Path to the backup file, or None if source doesn't exist
        """
        source_file = self.data_dir / f"{project_id}.xlsx"
        
        if not source_file.exists():
            logger.warning(f"Cannot create backup: source file not found: {source_file}", extra={'project_id': project_id})
            return None
        
        # Create timestamped backup in hidden .backups directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = self.backup_dir / f"{project_id}.xlsx.bak.{timestamp}"
        
        try:
            shutil.copy2(source_file, backup_file)
            size_mb = backup_file.stat().st_size / (1024 * 1024)
            logger.info(
                f"Created {backup_type} backup: {backup_file.name} ({size_mb:.2f} MB)",
                extra={'project_id': project_id, 'backup_type': backup_type}
            )
            
            # Cleanup old backups
            self._cleanup_old_backups(project_id)
            
            return backup_file
        except Exception as e:
            logger.error(f"Failed to create backup: {e}", exc_info=True, extra={'project_id': project_id})
            return None
    
    def restore_backup(self, project_id: str, backup_timestamp: Optional[str] = None) -> bool:
        """
        Restore a project from a backup.
        
        Args:
            project_id: Project identifier
            backup_timestamp: Specific backup timestamp (YYYYMMDD_HHMMSS), or None for latest
        
        Returns:
            True if restore successful, False otherwise
        """
        try:
            # Find backup file
            if backup_timestamp:
                backup_file = self.data_dir / f"{project_id}.xlsx.bak.{backup_timestamp}"
                if not backup_file.exists():
                    logger.error(f"Backup not found: {backup_file}", extra={'project_id': project_id})
                    return False
            else:
                # Get latest backup
                backups = self.list_backups(project_id)
                if not backups:
                    logger.error(f"No backups found for project: {project_id}", extra={'project_id': project_id})
                    return False
                backup_file = backups[0].backup_path
            
            # Create a backup of current file before restoring
            current_file = self.data_dir / f"{project_id}.xlsx"
            if current_file.exists():
                self.create_backup(project_id, backup_type='pre_restore')
            
            # Restore from backup
            shutil.copy2(backup_file, current_file)
            logger.info(
                f"Restored project from backup: {backup_file.name}",
                extra={'project_id': project_id}
            )
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore backup: {e}", exc_info=True, extra={'project_id': project_id})
            return False
    
    def list_backups(self, project_id: Optional[str] = None) -> List[BackupInfo]:
        """
        List all backups, optionally filtered by project.
        
        Args:
            project_id: Optional project identifier to filter by
        
        Returns:
            List of BackupInfo objects, sorted by timestamp (newest first)
        """
        pattern = f"{project_id}.xlsx.bak.*" if project_id else "*.xlsx.bak.*"
        backup_files = list(self.backup_dir.glob(pattern))
        
        backups = []
        for backup_file in backup_files:
            try:
                # Parse filename: project_id.xlsx.bak.YYYYMMDD_HHMMSS
                parts = backup_file.name.split('.bak.')
                if len(parts) != 2:
                    continue
                
                proj_id = parts[0].replace('.xlsx', '')
                timestamp_str = parts[1]
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                size_bytes = backup_file.stat().st_size
                
                # Determine backup type from metadata or default to 'auto'
                backup_type = 'auto'  # Could be enhanced with metadata file
                
                backups.append(BackupInfo(
                    project_id=proj_id,
                    backup_path=backup_file,
                    timestamp=timestamp,
                    size_bytes=size_bytes,
                    backup_type=backup_type
                ))
            except Exception as e:
                logger.warning(f"Failed to parse backup file: {backup_file.name}: {e}")
                continue
        
        # Sort by timestamp, newest first
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        return backups
    
    def delete_backup(self, project_id: str, backup_timestamp: str) -> bool:
        """
        Delete a specific backup.
        
        Args:
            project_id: Project identifier
            backup_timestamp: Backup timestamp (YYYYMMDD_HHMMSS)
        
        Returns:
            True if deleted successfully, False otherwise
        """
        backup_file = self.backup_dir / f"{project_id}.xlsx.bak.{backup_timestamp}"
        
        try:
            if backup_file.exists():
                backup_file.unlink()
                logger.info(f"Deleted backup: {backup_file.name}", extra={'project_id': project_id})
                return True
            else:
                logger.warning(f"Backup not found: {backup_file.name}", extra={'project_id': project_id})
                return False
        except Exception as e:
            logger.error(f"Failed to delete backup: {e}", exc_info=True, extra={'project_id': project_id})
            return False
    
    def _cleanup_old_backups(self, project_id: str):
        """
        Keep only the N most recent backup files for a project.
        
        Args:
            project_id: Project identifier
        """
        try:
            backups = self.list_backups(project_id)
            
            if len(backups) <= self.max_backups:
                return  # Nothing to clean up
            
            # Remove old backups beyond the limit
            for old_backup in backups[self.max_backups:]:
                old_backup.backup_path.unlink()
                logger.info(
                    f"Cleaned up old backup: {old_backup.backup_path.name}",
                    extra={'project_id': project_id}
                )
        except Exception as e:
            logger.error(f"Error cleaning up backups: {e}", exc_info=True, extra={'project_id': project_id})
    
    def cleanup_deleted_files(self) -> int:
        """
        Remove .deleted files older than retention_days.
        
        Returns:
            Number of files cleaned up
        """
        try:
            cutoff_time = datetime.now().timestamp() - (self.retention_days * 24 * 60 * 60)
            
            deleted_files = list(self.trash_dir.glob("*.deleted"))
            cleaned_count = 0
            
            for deleted_file in deleted_files:
                if deleted_file.stat().st_mtime < cutoff_time:
                    deleted_file.unlink()
                    cleaned_count += 1
                    logger.debug(f"Cleaned up old deleted file: {deleted_file.name}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old deleted files")
            
            return cleaned_count
        except Exception as e:
            logger.error(f"Error cleaning up deleted files: {e}", exc_info=True)
            return 0
    
    def cleanup_all_backups(self) -> Dict[str, Any]:
        """
        Run cleanup for all projects.
        
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            # Get all project IDs
            project_files = list(self.data_dir.glob("*.xlsx"))
            project_ids = [f.stem for f in project_files]
            
            stats: Dict[str, Any] = {
                'projects_processed': 0,
                'backups_removed': 0,
                'deleted_files_removed': 0
            }
            
            # Cleanup backups for each project
            for project_id in project_ids:
                backups_before = len(self.list_backups(project_id))
                self._cleanup_old_backups(project_id)
                backups_after = len(self.list_backups(project_id))
                
                removed = backups_before - backups_after
                if removed > 0:
                    stats['backups_removed'] += removed
                stats['projects_processed'] += 1
            
            # Cleanup deleted files
            stats['deleted_files_removed'] = self.cleanup_deleted_files()
            
            logger.info(f"Cleanup completed: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}", exc_info=True)
            return {'error': str(e)}
    
    def export_project(self, project_id: str, export_path: Optional[Path] = None) -> Optional[Path]:
        """
        Export a project with all its backups as a ZIP file.
        
        Args:
            project_id: Project identifier
            export_path: Optional custom export path, defaults to data_dir
        
        Returns:
            Path to the exported ZIP file, or None on failure
        """
        try:
            source_file = self.data_dir / f"{project_id}.xlsx"
            if not source_file.exists():
                logger.error(f"Project file not found: {source_file}", extra={'project_id': project_id})
                return None
            
            # Determine export path
            if export_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                export_path = self.data_dir / f"{project_id}_export_{timestamp}.zip"
            
            # Create ZIP file
            with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # Add main project file
                zipf.write(source_file, f"{project_id}.xlsx")
                
                # Add all backups
                backups = self.list_backups(project_id)
                for backup in backups:
                    zipf.write(backup.backup_path, backup.backup_path.name)
                
                # Add metadata
                metadata = {
                    'project_id': project_id,
                    'export_timestamp': datetime.now().isoformat(),
                    'backup_count': len(backups),
                    'backups': [b.to_dict() for b in backups]
                }
                zipf.writestr('metadata.json', json.dumps(metadata, indent=2))
            
            size_mb = export_path.stat().st_size / (1024 * 1024)
            logger.info(
                f"Exported project: {export_path.name} ({size_mb:.2f} MB, {len(backups)} backups)",
                extra={'project_id': project_id}
            )
            return export_path
            
        except Exception as e:
            logger.error(f"Failed to export project: {e}", exc_info=True, extra={'project_id': project_id})
            return None
    
    def import_project(self, zip_path: Path, overwrite: bool = False) -> Optional[str]:
        """
        Import a project from a ZIP export file.
        
        Args:
            zip_path: Path to the ZIP export file
            overwrite: Whether to overwrite existing project
        
        Returns:
            Project ID if successful, None otherwise
        """
        try:
            if not zip_path.exists():
                logger.error(f"Import file not found: {zip_path}")
                return None
            
            # Extract and read metadata
            with zipfile.ZipFile(zip_path, 'r') as zipf:
                # Read metadata
                metadata_str = zipf.read('metadata.json').decode('utf-8')
                metadata = json.loads(metadata_str)
                project_id = metadata['project_id']
                
                # Check if project exists
                target_file = self.data_dir / f"{project_id}.xlsx"
                if target_file.exists() and not overwrite:
                    logger.error(
                        f"Project already exists: {project_id}. Use overwrite=True to replace.",
                        extra={'project_id': project_id}
                    )
                    return None
                
                # Backup existing project if overwriting
                if target_file.exists():
                    self.create_backup(project_id, backup_type='pre_import')
                
                # Extract all files
                zipf.extractall(self.data_dir)
            
            logger.info(
                f"Imported project: {project_id} ({metadata['backup_count']} backups)",
                extra={'project_id': project_id}
            )
            return project_id
            
        except Exception as e:
            logger.error(f"Failed to import project: {e}", exc_info=True)
            return None
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics for the data directory.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            project_files = list(self.data_dir.glob("*.xlsx"))
            backup_files = list(self.backup_dir.glob("*.xlsx.bak.*"))
            deleted_files = list(self.trash_dir.glob("*.deleted"))
            
            def get_total_size(files: List[Path]) -> int:
                return sum(f.stat().st_size for f in files)
            
            project_size = get_total_size(project_files)
            backup_size = get_total_size(backup_files)
            deleted_size = get_total_size(deleted_files)
            total_size = project_size + backup_size + deleted_size
            
            stats = {
                'projects': {
                    'count': len(project_files),
                    'size_bytes': project_size,
                    'size_mb': round(project_size / (1024 * 1024), 2)
                },
                'backups': {
                    'count': len(backup_files),
                    'size_bytes': backup_size,
                    'size_mb': round(backup_size / (1024 * 1024), 2)
                },
                'deleted': {
                    'count': len(deleted_files),
                    'size_bytes': deleted_size,
                    'size_mb': round(deleted_size / (1024 * 1024), 2)
                },
                'total': {
                    'size_bytes': total_size,
                    'size_mb': round(total_size / (1024 * 1024), 2),
                    'size_gb': round(total_size / (1024 * 1024 * 1024), 2)
                },
                'data_dir': str(self.data_dir)
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}", exc_info=True)
            return {'error': str(e)}

# Made with Bob
