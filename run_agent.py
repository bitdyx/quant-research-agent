import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from quant_research_agent.cli import main
from quant_research_agent.gui.app import launch_gui
from quant_research_agent.web.app import launch_web


if __name__ == "__main__":
    if len(sys.argv) == 1:
        launch_web()
    else:
        main()
