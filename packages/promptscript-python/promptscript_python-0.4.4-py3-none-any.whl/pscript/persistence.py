# pscript/persistence.py

import logging
import os
from datetime import datetime
from filelock import FileLock
from pathlib import Path
from typing import Dict, List, Optional, Any
from .types import ExecutionEvent, TraceFile

logger = logging.getLogger(__name__)

class JSONPersistenceHandler:
    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.cwd() / '.promptscript'
        self.traces_dir = self.base_dir / 'traces'
        self.persistence_enabled = self._check_persistence_enabled()
        if self.persistence_enabled:
            self._init_directories()
    
    def _check_persistence_enabled(self) -> bool:
        # Check environment variable first (highest priority)
        env_disable = os.environ.get('PROMPTSCRIPT_DISABLE_TRACING', '').lower()
        if env_disable in ('1', 'true', 'yes', 'y', 'on'):
            logger.debug("Persistence disabled via PROMPTSCRIPT_DISABLE_TRACING environment variable")
            return False
            
        # Check config settings (medium priority)
        try:
            from .config import get_config
            config = get_config().get_config_dict()
            if config and 'persistence' in config and 'enabled' in config['persistence']:
                enabled = bool(config['persistence']['enabled'])
                if not enabled:
                    logger.debug("Persistence disabled via configuration setting")
                    return False
        except Exception as e:
            logger.debug(f"Could not check persistence config: {e}")
            
        # Check if directory is writable (lowest priority)
        try:
            if not self.base_dir.exists():
                parent_dir = self.base_dir.parent
                if not os.access(parent_dir, os.W_OK):
                    logger.warning(f"Parent directory {parent_dir} is not writable, disabling persistence")
                    return False
            elif not os.access(self.base_dir, os.W_OK):
                logger.warning(f"Directory {self.base_dir} is not writable, disabling persistence")
                return False
        except Exception as e:
            logger.warning(f"Error checking directory permissions, disabling persistence: {e}")
            return False
            
        return True
    
    def _init_directories(self) -> None:
        if not self.persistence_enabled:
            return
            
        try:
            self.base_dir.mkdir(exist_ok=True)
            self.traces_dir.mkdir(exist_ok=True)
        except (PermissionError, OSError) as e:
            logger.warning(f"Could not create persistence directories: {e}")
            self.persistence_enabled = False
    
    def _get_trace_path(self, timestamp: str, module_name: str) -> Path:
        clean_module_name = module_name.replace("/", "_").replace("\\", "_")
        if clean_module_name.endswith('.py'):
            clean_module_name = clean_module_name[:-3]
        return self.traces_dir / f"{timestamp}_{clean_module_name}.json"

    def save_event(self, event: ExecutionEvent, module_name: str, session_timestamp: str) -> None:
        if not self.persistence_enabled:
            return
            
        trace_path = self._get_trace_path(session_timestamp, module_name)
        lock_path = trace_path.with_suffix(trace_path.suffix + ".lock")
        
        with FileLock(str(lock_path)):
            try:
                if trace_path.exists() and os.path.getsize(trace_path) > 0:
                    try:
                        with trace_path.open('r', encoding='utf-8') as f:
                            trace_data = TraceFile.model_validate_json(f.read())
                    except Exception as e:
                        logger.error(f"Error loading trace file: {e}")
                        trace_data = TraceFile(
                            session_id=event.session_id,
                            module_name=module_name,
                            created_at=datetime.now(),
                            updated_at=datetime.now()
                        )
                else:
                    trace_data = TraceFile(
                        session_id=event.session_id,
                        module_name=module_name,
                        created_at=datetime.now(),
                        updated_at=datetime.now()
                    )

                for i, existing_event in enumerate(trace_data.events):
                    if existing_event.id == event.id:
                        trace_data.events[i] = event
                        break
                else:
                    trace_data.events.append(event)

                trace_data.updated_at = datetime.now()
                
                with trace_path.open('w', encoding='utf-8') as f:
                    f.write(trace_data.model_dump_json(indent=2))
                    
            except Exception as e:
                logger.error(f"Error saving to trace file {trace_path.name}: {e}")
                raise

    def get_trace_events(self, filename: str) -> List[ExecutionEvent]:
        if not self.persistence_enabled:
            return []
            
        trace_path = self.traces_dir / filename
        try:
            if not trace_path.exists():
                return []
            
            with trace_path.open('r', encoding='utf-8') as f:
                trace_data = TraceFile.model_validate_json(f.read())
            return trace_data.events
            
        except Exception as e:
            logger.error(f"Error loading trace file {filename}: {e}")
            raise

    def list_traces(self, pattern: Optional[str] = None) -> List[Dict[str, Any]]:
        if not self.persistence_enabled:
            return []
            
        traces = []
        for file_path in self.traces_dir.glob("*.json"):
            if pattern and pattern not in file_path.stem:
                continue
            try:
                with file_path.open('r', encoding='utf-8') as f:
                    trace_data = TraceFile.model_validate_json(f.read())
                traces.append({
                    'filename': file_path.name,
                    'module_name': trace_data.module_name,
                    'created_at': trace_data.created_at,
                    'updated_at': trace_data.updated_at,
                    'event_count': len(trace_data.events)
                })
            except Exception as e:
                logger.error(f"Error reading trace file {file_path.name}: {e}")
        return sorted(traces, key=lambda x: x['created_at'], reverse=True)