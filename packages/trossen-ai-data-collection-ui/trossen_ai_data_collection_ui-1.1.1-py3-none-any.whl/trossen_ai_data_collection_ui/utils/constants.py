from pathlib import Path

PACKAGE_ROOT = (
    Path(__file__).resolve().parent.parent
)  # Define the root directory of the package.

TROSSEN_AI_ROBOT_PATH = (
    PACKAGE_ROOT / "configs/robot/trossen_ai_robots.yaml"
)  # Path to the robot configuration YAML file.
TROSSEN_AI_TASK_PATH = (
    PACKAGE_ROOT / "configs/tasks.yaml"
)  # Path to the task configuration YAML file.
