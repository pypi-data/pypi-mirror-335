import importlib
import logging
import os
import sys

import yaml


# region Utility Functions

def get_all_subclasses(cls):
    all_subclasses = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(get_all_subclasses(subclass))
    return all_subclasses


def load_yaml(yaml_path):
    with open(yaml_path, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    return yaml_data

def get_console_format(logger_name):
    if importlib.util.find_spec("torch") is None or importlib.util.find_spec("torch.distributed") is None:
        return f"[{logger_name}] %(asctime)s - %(levelname)s - %(message)s"
    rank_info = ""
    try:
        import torch.distributed as dist
        if dist.is_available() and dist.is_initialized():
            rank_info = f" - GPU {dist.get_rank()}"
    except RuntimeError:
        pass
    return f"[{logger_name}{rank_info}] %(asctime)s - %(levelname)s - %(message)s"

def _setup_logger(logger_name: str, gconfig, log_file="logger.log", debug=False, output_dir=None, run_name=None) -> logging.Logger:
    """
    Configure a logger for a specific module with handlers for both console and file output.

    Args:
        logger_name (str): Name of the logger, often based on the class or module name.
        gconfig (dict): Global configuration containing 'output_dir' and 'run_name'.
        log_file (str): Name of the log file.
        debug (bool): Debug mode enabled if True.

    Returns:
        logging.Logger: The configured logger instance.
    """
    logger = logging.getLogger(logger_name)

    config = gconfig
    logger.setLevel(logging.DEBUG if debug else logging.INFO)
    logger.propagate = False  # Empêche les logs de remonter à la racine

    console_format = get_console_format(logger_name)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG if debug else logging.INFO)
    console_formatter = logging.Formatter(console_format)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # File handler
    try:
        file_path = os.path.join(config["output_dir"] if not output_dir else output_dir,
                                 config["run_name"] if not run_name else run_name, log_file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        file_handler = logging.FileHandler(file_path, mode="w+")
        file_handler.setLevel(logging.DEBUG if debug else logging.INFO)
        file_formatter = logging.Formatter(console_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.debug("Can't create log file: %s", e)
        pass
    try:
        logging.getLogger("wandb").setLevel(logging.WARNING)
    except Exception:
        pass
    return logger

import typing_extensions

def _get_typing_attr(obj):
    name = getattr(obj, "_name", None)
    if name and hasattr(typing_extensions, name):
        return getattr(typing_extensions, name)
    return obj

# endregion
