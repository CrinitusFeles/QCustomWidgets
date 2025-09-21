import os
from pathlib import Path

plugin_path = Path(__file__).parent / "plugins"
os.environ["PYSIDE_DESIGNER_PLUGINS"] = str(plugin_path)

# print(plugin_path)

def run_designer():
    os.system(f"cd { plugin_path } && pyside6-designer")


if __name__ == '__main__':
    run_designer()