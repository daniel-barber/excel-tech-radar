"""
Scheduled tasks for Excel Tech Radar maintenance.
Handles automated cleanup, backups, and monitoring.
"""
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Callable
from pathlib import Path

from .backup_manager import BackupManager
from .logging_config import get_logger

logger = get_logger(__name__)


class ScheduledTask:
    """Represents a scheduled task with interval and execution logic."""
    
    def __init__(
        self,
        name: str,
        interval_seconds: int,
        task_func: Callable,
        enabled: bool = True
    ):
        """
        Initialize a scheduled task.
        
        Args:
            name: Task name for logging
            interval_seconds: Interval between executions in seconds
            task_func: Function to execute
            enabled: Whether the task is enabled
        """
        self.name = name
        self.interval_seconds = interval_seconds
        self.task_func = task_func
        self.enabled = enabled
        self.last_run: Optional[datetime] = None
        self.next_run: Optional[datetime] = None
        self.run_count = 0
        self.error_count = 0
        
        if enabled:
            self.next_run = datetime.now() + timedelta(seconds=interval_seconds)
    
    def should_run(self) -> bool:
        """Check if the task should run now."""
        if not self.enabled or self.next_run is None:
            return False
        return datetime.now() >= self.next_run
    
    def execute(self):
        """Execute the task and update timing."""
        try:
            logger.info(f"Executing scheduled task: {self.name}")
            self.task_func()
            self.last_run = datetime.now()
            self.next_run = self.last_run + timedelta(seconds=self.interval_seconds)
            self.run_count += 1
            logger.info(f"Task completed: {self.name} (run #{self.run_count})")
        except Exception as e:
            self.error_count += 1
            logger.error(f"Task failed: {self.name}: {e}", exc_info=True)
            # Still schedule next run even on error
            self.next_run = datetime.now() + timedelta(seconds=self.interval_seconds)
    
    def to_dict(self) -> dict:
        """Convert task info to dictionary."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'interval_seconds': self.interval_seconds,
            'interval_hours': round(self.interval_seconds / 3600, 2),
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'run_count': self.run_count,
            'error_count': self.error_count
        }


class TaskScheduler:
    """Manages scheduled maintenance tasks."""
    
    def __init__(self, backup_manager: BackupManager):
        """
        Initialize the task scheduler.
        
        Args:
            backup_manager: BackupManager instance for cleanup operations
        """
        self.backup_manager = backup_manager
        self.tasks: list[ScheduledTask] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None
        logger.info("TaskScheduler initialized")
    
    def add_task(self, task: ScheduledTask):
        """Add a task to the scheduler."""
        self.tasks.append(task)
        logger.info(f"Added task: {task.name} (interval: {task.interval_seconds}s, enabled: {task.enabled})")
    
    def remove_task(self, task_name: str) -> bool:
        """Remove a task by name."""
        for i, task in enumerate(self.tasks):
            if task.name == task_name:
                self.tasks.pop(i)
                logger.info(f"Removed task: {task_name}")
                return True
        return False
    
    def enable_task(self, task_name: str) -> bool:
        """Enable a task by name."""
        for task in self.tasks:
            if task.name == task_name:
                task.enabled = True
                task.next_run = datetime.now() + timedelta(seconds=task.interval_seconds)
                logger.info(f"Enabled task: {task_name}")
                return True
        return False
    
    def disable_task(self, task_name: str) -> bool:
        """Disable a task by name."""
        for task in self.tasks:
            if task.name == task_name:
                task.enabled = False
                task.next_run = None
                logger.info(f"Disabled task: {task_name}")
                return True
        return False
    
    def get_task_status(self) -> list[dict]:
        """Get status of all tasks."""
        return [task.to_dict() for task in self.tasks]
    
    def _run_loop(self):
        """Main scheduler loop (runs in background thread)."""
        logger.info("Scheduler loop started")
        
        while self.running:
            try:
                # Check each task
                for task in self.tasks:
                    if task.should_run():
                        task.execute()
                
                # Sleep for 60 seconds before next check
                time.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}", exc_info=True)
                time.sleep(60)  # Continue after error
        
        logger.info("Scheduler loop stopped")
    
    def start(self):
        """Start the scheduler in a background thread."""
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        if not self.running:
            logger.warning("Scheduler not running")
            return
        
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Scheduler stopped")
    
    def is_running(self) -> bool:
        """Check if scheduler is running."""
        return self.running


def create_default_tasks(backup_manager: BackupManager, config) -> TaskScheduler:
    """
    Create a scheduler with default maintenance tasks.
    
    Args:
        backup_manager: BackupManager instance
        config: Configuration object
    
    Returns:
        TaskScheduler with default tasks configured
    """
    scheduler = TaskScheduler(backup_manager)
    
    # Task 1: Cleanup old backups and deleted files (daily)
    def cleanup_task():
        """Daily cleanup of old backups and deleted files."""
        stats = backup_manager.cleanup_all_backups()
        logger.info(f"Daily cleanup completed: {stats}")
    
    scheduler.add_task(ScheduledTask(
        name="daily_cleanup",
        interval_seconds=24 * 60 * 60,  # 24 hours
        task_func=cleanup_task,
        enabled=config.enable_scheduled_cleanup if hasattr(config, 'enable_scheduled_cleanup') else True
    ))
    
    # Task 2: Auto-backup all projects (weekly)
    def auto_backup_task():
        """Weekly automatic backup of all projects."""
        data_dir = backup_manager.data_dir
        project_files = list(data_dir.glob("*.xlsx"))
        backup_count = 0
        
        for project_file in project_files:
            if project_file.name.startswith('~$'):
                continue  # Skip temp files
            
            project_id = project_file.stem
            backup_path = backup_manager.create_backup(project_id, backup_type='auto')
            if backup_path:
                backup_count += 1
        
        logger.info(f"Auto-backup completed: {backup_count} projects backed up")
    
    scheduler.add_task(ScheduledTask(
        name="weekly_auto_backup",
        interval_seconds=7 * 24 * 60 * 60,  # 7 days
        task_func=auto_backup_task,
        enabled=config.enable_auto_backup if hasattr(config, 'enable_auto_backup') else False
    ))
    
    # Task 3: Storage monitoring (hourly)
    def storage_monitor_task():
        """Hourly storage monitoring and alerts."""
        stats = backup_manager.get_storage_stats()
        total_mb = stats['total']['size_mb']
        
        # Log storage stats
        logger.info(
            f"Storage stats: {stats['projects']['count']} projects, "
            f"{stats['backups']['count']} backups, "
            f"{total_mb:.2f} MB total"
        )
        
        # Alert if storage is high (could be extended with email/webhook)
        if total_mb > 1000:  # Alert if over 1GB
            logger.warning(f"High storage usage: {total_mb:.2f} MB")
    
    scheduler.add_task(ScheduledTask(
        name="storage_monitor",
        interval_seconds=60 * 60,  # 1 hour
        task_func=storage_monitor_task,
        enabled=config.enable_storage_monitoring if hasattr(config, 'enable_storage_monitoring') else True
    ))
    
    return scheduler

# Made with Bob
