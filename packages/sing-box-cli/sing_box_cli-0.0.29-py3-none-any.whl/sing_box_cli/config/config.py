import os
import platform
import shutil
from functools import lru_cache
from pathlib import Path

import httpx
import typer
from rich import print

from .utils import check_url, load_json_config, show_diff_config


class SingBoxConfig:
    def __init__(self) -> None:
        user = (
            os.environ.get("SUDO_USER")
            or os.environ.get("USER")
            or os.environ.get("USERNAME")
        )
        if not user:
            raise ValueError("❌ Unable to detect user name")

        self.user = user
        bin_filename = "sing-box.exe" if self.is_windows else "sing-box"
        bin_path = shutil.which(bin_filename)
        if not bin_path:
            raise FileNotFoundError(f"❌ {bin_filename} not found in PATH")

        self.bin_path = Path(bin_path)
        if self.is_windows:
            self.config_dir = Path(typer.get_app_dir("sing-box", roaming=True))
        else:
            # enable run cli without sudo
            self.config_dir = Path(f"~{self.user}/.config/sing-box").expanduser()

        self.config_file = self.config_dir / "config.json"
        self.subscription_file = self.config_dir / "subscription.txt"
        self.cache_db = self.config_dir / "cache.db"

        print(self)

    def init_directories(self) -> bool:
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            if not self.config_file.exists():
                self.config_file.write_text("{}")
                print(f"📁 Created empty config file: {self.config_file}")

            if not self.subscription_file.exists():
                self.subscription_file.touch()
                print(f"📁 Created subscription file: {self.subscription_file}")

            if not self.is_windows:
                shutil.chown(self.config_dir, user=self.user, group=self.user)
                shutil.chown(self.config_file, user=self.user, group=self.user)
                shutil.chown(self.subscription_file, user=self.user, group=self.user)
        except Exception as e:
            print(f"❌ Failed to initialize directories: {e}")
            return False
        return True

    @property
    def is_windows(self) -> bool:
        return platform.system() == "Windows"

    @property
    def sub_url(self) -> str:
        if not self.subscription_file.exists():
            return ""
        return self.subscription_file.read_text().strip()

    @property
    def api_base_url(self) -> str:
        config = load_json_config(self.config_file)
        url = (
            config.get("experimental", {})
            .get("clash_api", {})
            .get("external_controller", "")
        )
        if isinstance(url, str) and url:
            if not url.startswith("http"):
                url = f"http://{url}"
            return url
        return ""

    @property
    def api_secret(self) -> str:
        config = load_json_config(self.config_file)
        token = config.get("experimental", {}).get("clash_api", {}).get("secret", "")
        if isinstance(token, str) and token:
            return token
        return ""

    def update_config(self) -> bool:
        """download configuration from subscription URL and show differences"""
        if not self.sub_url:
            print("❌ No valid subscription URL found.")
            return False

        current_config = (
            self.config_file.read_text(encoding="utf-8")
            if self.config_file.exists()
            else "{}"
        )
        print(f"⌛ Updating configuration from {self.sub_url}")
        try:
            response = httpx.get(self.sub_url)
            response.raise_for_status()
            new_config = response.text
            self.config_file.write_text(new_config, encoding="utf-8")
            if not self.is_windows:
                shutil.chown(self.config_file, user=self.user, group=self.user)

            if current_config == new_config:
                print("📄 Configuration is up to date.")
            else:
                show_diff_config(current_config, new_config)

            return True
        except Exception as e:
            print(f"❌ Failed to update configuration: {e}")
            return False

    def add_subscription(self, url: str) -> bool:
        if not check_url(url):
            return False
        self.subscription_file.write_text(url.strip())
        print("📁 Subscription added successfully.")
        return True

    def show_config(self) -> None:
        print(self.config_file.read_text(encoding="utf-8"))

    def show_subscription(self) -> None:
        if self.sub_url:
            print(f"🔗 Current subscription URL: {self.sub_url}")
        else:
            print("❌ No subscription URL found.")

    def clean_cache(self) -> None:
        if self.cache_db.exists():
            self.cache_db.unlink()
            print("🗑️ Cache database removed.")
        else:
            print("❌ Cache database not found.")

    def __str__(self) -> str:
        info = (
            f"🔧 Using binary: {self.bin_path}\n"
            f"📄 Using configuration: {self.config_file}"
        )

        if self.is_windows:
            info += f"\n📁 Using installation directory: {self.config_dir}"
        return info


@lru_cache
def get_config() -> SingBoxConfig:
    config = SingBoxConfig()
    if not config.init_directories():
        raise FileNotFoundError("❌ Failed to initialize directories")
    return config
