import configparser
import importlib.resources
import logging
import os
from functools import wraps
from pathlib import Path
import typer
from neptun.model.responses import ConfigResponse
from neptun import SUCCESS, CONFIG_KEY_NOT_FOUND_ERROR, __app_name__, DIR_ERROR, FILE_ERROR
import json

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config/config.ini"

with importlib.resources.path('neptun.config', 'default.json') as default_json_path:
    DEFAULT_CONFIG_FILE_PATH = default_json_path

try:
    with open(DEFAULT_CONFIG_FILE_PATH) as f:
        DEFAULT_CONFIG = json.load(f)
except FileNotFoundError:
    DEFAULT_CONFIG = None


def singleton(cls):
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def ensure_latest_config(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        self.config.read(self.config_file_path)
        return method(self, *args, **kwargs)
    return wrapper


@singleton
class ConfigManager:
    def __init__(self, config_file_path=CONFIG_FILE_PATH):
        self.config_file_path = config_file_path
        self.config = configparser.ConfigParser()
        self._ensure_config_file_exists()

    def set_config_file_path(self, path: str):
        self.config_file_path = path
        self._ensure_config_file_exists()
        self.config.read(self.config_file_path)

    def search_for_configuration_and_configure(self):
        current_working_directory = Path(f"{os.getcwd()}/{__app_name__}-config.json")

        confid_data = json.load(open(Path(current_working_directory))) if Path(current_working_directory).exists() else None

        return self._write_default_config(config_file_path=confid_data)

    def _write_default_config(self, config_file_path=DEFAULT_CONFIG):
        """Write the default configuration to the file."""
        with open(self.config_file_path, 'w') as configfile:
            self._write_section(configfile, "", config_file_path)
        logging.info(f"Writing complete!")

    def write_provided_custom_config(self, path: str):
        """Write the provided configuration to the file."""
        with open(path, 'w') as configfile:
            self._write_section(configfile, "", DEFAULT_CONFIG)

    def _write_section(self, file, parent_section, section_dict, level=0):
        """Write a section and its nested sections to the file."""
        for key, value in section_dict.items():
            section_name = f"{parent_section}.{key}" if parent_section else key
            if isinstance(value, dict):
                file.write(f"\n[{section_name}]\n")
                self._write_section(file, section_name, value, level + 1)
            else:
                file.write(f"{key} = {value}\n")

    def _ensure_config_file_exists(self):
        """Ensure the configuration directory and file exist."""
        if not CONFIG_DIR_PATH.exists():
            CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE_PATH.parent.exists():
            CONFIG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE_PATH.exists():
            CONFIG_FILE_PATH.touch()
            self._write_default_config()
        else:
            if os.stat(CONFIG_FILE_PATH).st_size == 0:
                self._write_default_config()

    @ensure_latest_config
    def read_config(self, section: str, key: str) -> str:
        return self.config[section][key]

    @ensure_latest_config
    def write_config(self, section: str, key: str, value: str):
        if section not in self.config:
            self.config.add_section(section)

        self.config[section][key] = value

        with open(self.config_file_path, 'w') as configfile:
            self.config.write(configfile)

    @ensure_latest_config
    def update_config(self, section: str, key: str, value: str) -> ConfigResponse:
        if section in self.config.sections() and key in self.config[section].keys():
            self.config[section][key] = value

            with open(self.config_file_path, 'w') as configfile:
                self.config.write(configfile)

            return SUCCESS
        else:
            return CONFIG_KEY_NOT_FOUND_ERROR

    @ensure_latest_config
    def delete_config(self, section: str, key: str):
        if section in self.config and key in self.config[section]:
            self.config.remove_option(section, key)

            with open(self.config_file_path, 'w') as configfile:
                self.config.write(configfile)

            print(f"Configuration '{key}' removed from section '{section}'")
        else:
            print(f"Configuration '{key}' in section '{section}' does not exist")

    @ensure_latest_config
    def list_sections(self):
        sections = self.config.sections()
        print("Sections:")
        for section in sections:
            print(f"  {section}")

        return sections

    @ensure_latest_config
    def list_keys(self, section: str):
        if section in self.config:
            keys = self.config[section].keys()
            print(f"Keys in section '{section}':")
            for key in keys:
                print(f"  {key}")

            return keys
        else:
            print(f"Section '{section}' does not exist")
            return []

    @ensure_latest_config
    def update_config_dynamically(self, query: str) -> ConfigResponse:
        section_value, rest = query.split('=', 1)

        value = rest
        key = section_value.split('.')[-1]
        section = '.'.join(section_value.split('.')[:-1])

        return self.update_config(section, key, value)

    def update_with_fallback(self) -> ConfigResponse:
        try:
            self._write_default_config()
            return SUCCESS
        except FileNotFoundError:
            return DIR_ERROR

    def update_authentication(self, id, session_cookie, email):
        self.write_config("auth.user", "id", str(id))
        self.write_config("auth.user", "email", str(email))
        self.write_config("auth", "neptun_session_cookie", str(session_cookie))
        return SUCCESS

    def update_active_chat(self, id, name, model):
        self.write_config("active_chat", "chat_id", str(id))
        self.write_config("active_chat", "chat_name", str(name))
        self.write_config("active_chat", "model", str(model))
        return SUCCESS

    @ensure_latest_config
    def get_config_as_dict(self) -> dict:
        return {section: dict(self.config[section]) for section in self.config.sections()}

    @classmethod
    def init_app(cls, db_path: str) -> int:
        config_code = cls._init_config_file()
        if config_code != SUCCESS:
            return config_code
        return SUCCESS

    @staticmethod
    def _init_config_file() -> int:
        """Ensure the configuration directory and file are created."""
        try:
            CONFIG_DIR_PATH.mkdir(parents=True, exist_ok=True)
        except OSError:
            return DIR_ERROR
        try:
            CONFIG_FILE_PATH.touch(exist_ok=True)
        except OSError:
            return FILE_ERROR
        return SUCCESS


# Example usage
if __name__ == "__main__":

    config_manager_ini = ConfigManager()
    config_manager_ini.update_config_dynamically("auth.user.id=penis")

    config_manager_ini.list_sections()
    print(config_manager_ini.read_config("auth.user", "id"))
    config_manager_ini.update_config("auth.user", "id", "hallo")

