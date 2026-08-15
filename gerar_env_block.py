#!/usr/bin/env python3
"""
Gera bloco <environment_details> formatado
"""

import os
import glob
from datetime import datetime

def gerar_environment_block():
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")
    working_directory = os.getcwd()
    workspace_root = os.path.abspath(os.sep)
    active_file = os.path.basename(__file__)
    
    try:
        visible_files = sorted([os.path.basename(f) for f in glob.glob('*') if os.path.isfile(f)])[:5]
    except Exception:
        visible_files = []
    
    open_tabs = []
    
    block = f"""<environment_details>
Current time: {current_time}
Working directory: {working_directory}
Workspace root folder: {workspace_root}
Active file: {active_file}
Visible files:
  {chr(10).join('  ' + f for f in visible_files)}
Open tabs:
  {chr(10).join('  ' + t for t in open_tabs)}
</environment_details>"""
    
    return block

if __name__ == "__main__":
    print(gerar_environment_block())
