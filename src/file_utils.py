"""
File Utilities - Shared helpers for file readiness detection
Used by both organizer and whatsapp_monitor (Dev2)
"""
import time
from pathlib import Path
from typing import Callable, Optional
import logging

logger = logging.getLogger(__name__)


def wait_for_file_ready(
    file_path: Path,
    max_wait_seconds: int = 30,
    check_interval_ms: int = 500,
    stable_checks: int = 2,
    progress_callback: Optional[Callable[[str], None]] = None
) -> bool:
    """
    Wait for file to be fully written (size stable)
    
    Args:
        file_path: Path to file to monitor
        max_wait_seconds: Maximum time to wait
        check_interval_ms: Interval between size checks
        stable_checks: Number of consecutive stable checks required
        progress_callback: Optional callback for progress updates
    
    Returns:
        True if file is ready, False if timeout
    """
    if not file_path.exists():
        if progress_callback:
            progress_callback(f"File not found: {file_path}")
        return False
    
    last_size = -1
    stable_count = 0
    max_checks = int(max_wait_seconds * 1000 / check_interval_ms)
    
    for check in range(max_checks):
        try:
            current_size = file_path.stat().st_size
            
            if current_size == 0:
                if progress_callback:
                    progress_callback(f"Waiting for file data... ({check * check_interval_ms / 1000:.1f}s)")
                time.sleep(check_interval_ms / 1000)
                continue
            
            if current_size == last_size:
                stable_count += 1
                if stable_count >= stable_checks:
                    logger.debug(f"File ready after {check * check_interval_ms / 1000:.1f}s: {file_path}")
                    return True
            else:
                stable_count = 0
            
            last_size = current_size
            
            if progress_callback and check % 10 == 0:
                progress_callback(f"File writing... {current_size} bytes ({check * check_interval_ms / 1000:.1f}s)")
            
        except (OSError, FileNotFoundError) as e:
            logger.warning(f"Error checking file {file_path}: {e}")
            stable_count = 0
        
        time.sleep(check_interval_ms / 1000)
    
    logger.warning(f"Timeout waiting for file: {file_path}")
    if progress_callback:
        progress_callback(f"Timeout waiting for file: {file_path}")
    return False


def is_valid_extension(file_path: Path, supported_extensions: list) -> bool:
    """Check if file has supported extension"""
    return file_path.suffix.lower() in [e.lower() for e in supported_extensions]


def get_file_hash(file_path: Path, algorithm: str = "md5") -> str:
    """Generate hash for duplicate detection"""
    import hashlib
    
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            hash_func.update(chunk)
    return hash_func.hexdigest()


class FileReadinessChecker:
    """Reusable file readiness checker with config"""
    
    def __init__(
        self,
        max_wait_seconds: int = 30,
        check_interval_ms: int = 500,
        stable_checks: int = 2
    ):
        self.max_wait_seconds = max_wait_seconds
        self.check_interval_ms = check_interval_ms
        self.stable_checks = stable_checks
    
    def wait_ready(self, file_path: Path, progress_callback: Optional[Callable[[str], None]] = None) -> bool:
        return wait_for_file_ready(
            file_path,
            self.max_wait_seconds,
            self.check_interval_ms,
            self.stable_checks,
            progress_callback
        )
    
    @classmethod
    def from_config(cls, config: dict) -> 'FileReadinessChecker':
        """Create checker from config dict"""
        whatsapp_config = config.get("whatsapp", {})
        return cls(
            max_wait_seconds=whatsapp_config.get("debounce_seconds", 30),
            check_interval_ms=whatsapp_config.get("size_check_interval_ms", 500),
            stable_checks=whatsapp_config.get("size_stable_checks", 2)
        )