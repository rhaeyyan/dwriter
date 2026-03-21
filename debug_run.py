from dwriter.tui.app import DWriterApp
from dwriter.cli import AppContext
from dwriter.config import ConfigManager
from textual.logging import TextualHandler
import logging
import os
import sys

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[TextualHandler()]
)

try:
    # Setup mock context
    class MockDB:
        def get_all_logs(self): return []
        def get_all_projects(self): return []
        def get_weekly_kpis(self): return {}
    
    ctx = AppContext(
        db=MockDB(),
        log_manager=MockDB(),
        project_manager=MockDB(),
        query_service=MockDB(),
        todo_manager=MockDB(),
        config_manager=ConfigManager(),
    )
    
    app = DWriterApp(ctx)
    app.run(headless=True)
except Exception as e:
    print(f"FAILED TO RUN APP: {e}")
    import traceback
    traceback.print_exc()
