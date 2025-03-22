import yaml
import json
import os
from PySide6.QtGui import QImage, QPainter
from trossen_ai_data_collection_ui.utils.constants import TROSSEN_AI_TASK_PATH, TROSSEN_AI_ROBOT_PATH
from lerobot.common.robot_devices.robots.configs import TrossenAIStationaryRobotConfig, TrossenAISoloRobotConfig
from lerobot.common.robot_devices.cameras.configs import IntelRealSenseCameraConfig
from lerobot.common.robot_devices.motors.configs import TrossenArmDriverConfig
import shutil

def set_image(widget: object, image: object) -> None:
    """
    Convert a BGR OpenCV image to RGB format and update the widget with the image.

    :param widget: The widget where the image will be displayed.
    :param image: The image data in OpenCV format (BGR).
    """
    widget.image = QImage(
        image.data, image.shape[1], image.shape[0], QImage.Format.Format_RGB888
    ).rgbSwapped()  # Convert BGR to RGB and swap channels.
    widget.update()  # Trigger a paint event to refresh the widget.


def paintEvent(widget: object, event: object) -> None:
    """
    Handle the widget's paint event to draw an image if available.

    :param widget: The widget to be painted.
    :param event: The paint event object.
    """
    if (
        hasattr(widget, "image") and widget.image is not None
    ):  # Check if the widget has an image.
        painter = QPainter(widget)  # Create a painter for the widget.
        painter.drawImage(
            widget.rect(), widget.image
        )  # Draw the image in the widget's rectangle.


def load_config(file_path: str = TROSSEN_AI_TASK_PATH) -> dict | None:
    """
    Load a YAML configuration file for tasks and return the parsed data as a dictionary.

    :param file_path: Path to the YAML configuration file. Defaults to TROSSEN_AI_TASK_PATH.
    :return: Parsed configuration data as a dictionary, or None if an error occurs.
    """
    try:
        with open(file_path, "r") as file:  # Open the file for reading.
            config_data = yaml.safe_load(file)  # Parse the YAML content.
        return config_data  # Return the parsed data.
    except FileNotFoundError:
        print(
            f"Error: The file '{file_path}' was not found."
        )  # Log file not found error.
        return None
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")  # Log YAML parsing error.
        return None


def get_last_episode_index(file_path):
        file_path = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'lerobot', file_path, 'meta', "episodes.jsonl")
        if not os.path.exists(file_path):
            return None  # Return None if file is missing

        last_entry = None
        
        # Read the file line by line (JSONL format)
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                last_entry = json.loads(line)  # Keep updating last_entry with the latest line

        if last_entry:
            return last_entry.get("episode_index", None)
        else:
            return None


def remove_corrupted_files(file_path):
        file_path = os.path.join(os.path.expanduser('~'), '.cache', 'huggingface', 'lerobot', file_path)
        if os.path.exists(file_path):
            shutil.rmtree(file_path)

def create_robot_config(robot_name):

    robot = load_config(TROSSEN_AI_ROBOT_PATH).get(robot_name)

    if robot_name == "trossen_ai_stationary":
        robot_config = TrossenAIStationaryRobotConfig(
                max_relative_target= None,
                mock=False,
                leader_arms={
                    "left":  TrossenArmDriverConfig(
                        ip=robot.get("leader_arms").get("left").get("ip"),
                        model=robot.get("leader_arms").get("left").get("model")),
                    "right": TrossenArmDriverConfig(
                        ip=robot.get("leader_arms").get("right").get("ip"),
                        model=robot.get("leader_arms").get("right").get("model")),
                },
                follower_arms={
                    "left":  TrossenArmDriverConfig(
                        ip=robot.get("follower_arms").get("left").get("ip"),
                        model=robot.get("follower_arms").get("left").get("model")),
                    "right": TrossenArmDriverConfig(
                        ip=robot.get("follower_arms").get("right").get("ip"),
                        model=robot.get("follower_arms").get("right").get("model")),
                },
                cameras={
                    "cam_high": IntelRealSenseCameraConfig(
                        serial_number=robot.get("cameras").get("cam_high").get('serial_number'), fps=30, width=640, height=480),
                    "cam_low": IntelRealSenseCameraConfig(
                        serial_number=robot.get("cameras").get("cam_low").get('serial_number'), fps=30, width=640, height=480),
                    "cam_left_wrist": IntelRealSenseCameraConfig(
                        serial_number=robot.get("cameras").get("cam_left_wrist").get('serial_number'), fps=30, width=640, height=480),
                    "cam_right_wrist": IntelRealSenseCameraConfig(
                        serial_number=robot.get("cameras").get("cam_right_wrist").get('serial_number'), fps=30, width=640, height=480),
                }
            )
        
    elif robot_name == "trossen_ai_solo":
        robot_config = TrossenAISoloRobotConfig(
            max_relative_target= None,
            mock=False,
            leader_arms = {
                "main": TrossenArmDriverConfig(
                    ip=robot.get("leader_arms").get("main").get("ip"),
                    model=robot.get("leader_arms").get("main").get("model")),
            },
            follower_arms = {
                "main": TrossenArmDriverConfig(
                    ip=robot.get("follower_arms").get("main").get("ip"),
                    model=robot.get("follower_arms").get("main").get("model")),
            },
            cameras = {
                "cam_high": IntelRealSenseCameraConfig(
                    serial_number=robot.get("cameras").get("cam_high").get('serial_number'), fps=30, width=640, height=480),
                "cam_wrist": IntelRealSenseCameraConfig(
                    serial_number=robot.get("cameras").get("cam_wrist").get('serial_number'), fps=30, width=640, height=480),
            }
        )
    elif robot_name == "trossen_ai_mobile":
        pass
    #TODO: Add support for Mobile Configurations
    
    return robot_config