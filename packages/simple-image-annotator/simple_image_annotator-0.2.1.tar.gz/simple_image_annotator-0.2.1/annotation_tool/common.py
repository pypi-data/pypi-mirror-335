import enum
import os
from pathlib import Path
import time

import pandas as pd

APP_NAME = ".simple-image-annotator"
SAVE_INTERVAL_IN_SECONDS = 30
PATH_COLUMN_NAME = "ImagePath"
CONFIG_PATH = Path.home() / APP_NAME / "config.json"
IMAGE_FILE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"]
GROUP_CLASS_SEPARATOR = "[G:C]"
SUPPORTED_INDEX_FILE_EXTENSIONS = [".csv", ".parquet"]
SUPPORTED_OUTPUT_FILE_EXTENSIONS = [".csv", ".parquet"]

_CONFIG = None


class JumpType(enum.Enum):
    START = enum.auto()
    PREV = enum.auto()
    NEXT = enum.auto()
    END = enum.auto()
    FIRST_EMPTY = enum.auto()


class Rotation(enum.Enum):
    DEG_0 = 0
    DEG_90 = 90
    DEG_180 = 180
    DEG_270 = 270


def rotate(rotation: Rotation, clockwise: bool = True) -> Rotation:
    if clockwise:
        return Rotation((rotation.value + 90) % 360)
    return Rotation((rotation.value - 90) % 360)


def is_identity_mapping(mapping):
    return all(k == v for k, v in mapping.items())


def _init_config():
    from annotation_tool import model

    global _CONFIG
    _CONFIG = (
        model.Config.from_disk(CONFIG_PATH) if CONFIG_PATH.is_file() else model.Config()
    )
    return _CONFIG


def get_config():
    return _CONFIG if _CONFIG is not None else _init_config()


def write_config(cfg):
    global _CONFIG
    _CONFIG = cfg
    cfg.to_disk(CONFIG_PATH)


def invert_translation_dicts(translate_groups, translate_classes):
    invert_translate_groups = {v: k for k, v in translate_groups.items() if v}

    # Convert translate_classes to {old_group_name: {old_name: new_name}}
    invert_translate_classes = {}
    for new_group_name, class_dict in translate_classes.items():
        # Get the old group name using the group mapping
        old_group_name = translate_groups[new_group_name]
        if old_group_name is None:
            continue  # New group

        if old_group_name in invert_translate_classes:
            raise ValueError(f"Duplicate group name: {old_group_name}")

        invert_translate_classes[old_group_name] = {}
        for new_class_name, old_class_name in class_dict.items():
            if old_class_name is None:
                continue  # New class
            invert_translate_classes[old_group_name][old_class_name] = new_class_name

    return invert_translate_groups, invert_translate_classes


def df_from_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)

    if path.suffix.lower() == ".parquet":
        return pd.read_parquet(path)

    raise ValueError(f"Unsupported file format: {path.suffix}")


def find_images_in_directory(
    dir: Path, recursive: bool = False, timeout_ms: int = 1000
) -> list[Path]:
    start_time = time.time()
    image_files = []

    def check_timeout():
        if (time.time() - start_time) * 1000 > timeout_ms:
            raise TimeoutError(
                "Image listing exceeded the time limit of {} ms".format(timeout_ms)
            )

    def list_images(directory: Path):
        try:
            for entry in os.scandir(directory):
                if entry.is_dir() and recursive:
                    list_images(Path(entry.path))  # Recursively list images
                elif entry.is_file():
                    if Path(entry.path).suffix.lower() in IMAGE_FILE_EXTENSIONS:
                        image_files.append(Path(entry.path))
                check_timeout()
        except TimeoutError:
            raise
        except Exception as e:
            print(f"Error while listing files: {e}")

    list_images(dir)
    return image_files
