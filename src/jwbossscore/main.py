from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING
import yaml

from endstone.plugin import Plugin
from endstone.command import Command, CommandSender

from jwbossscore.handlers.scoreboard_handler import ScoreboardHandler
from jwbossscore.handlers.bossbar_handler import BossbarHandler


class JWBossScore(Plugin):
    api_version = "0.11"
    prefix = "§6§l[JWBossScore]§r"
    version = "1.0.0"
    description = "Scoreboard and Bossbar plugin using JWPlaceholderAPI."
    authors = ["JWDev"]
    depend = ["jwplaceholderapi"]

    commands = {
        "jwbossscore": {
            "description": "Reload JWBossScore configuration.",
            "usages": ["/jwbossscore reload"],
            "permissions": ["jwbossscore.admin"],
            "aliases": ["jwboss"]
        }
    }

    permissions = {
        "jwbossscore.admin": {
            "description": "Allows reloading JWBossScore",
            "default": "op"
        }
    }

    def _load_config(self, filename: str) -> dict:
        config_path = self.data_folder / filename
        if not config_path.exists():
            resource_path = Path(__file__).parent / "resources" / filename
            if resource_path.exists():
                with resource_path.open("r", encoding="utf-8") as f:
                    default_cfg = f.read()
                self.data_folder.mkdir(parents=True, exist_ok=True)
                with config_path.open("w", encoding="utf-8") as f:
                    f.write(default_cfg)
            else:
                return {}

        with config_path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}

    def on_load(self) -> None:
        self.scoreboard_config = self._load_config("scoreboard.yml")
        self.bossbar_config = self._load_config("bossbar.yml")

    def on_enable(self) -> None:
        self.papi = self.server.plugin_manager.get_plugin("jwplaceholderapi")
        if not self.papi:
            self.logger.error("jwplaceholderapi is required but not found!")
            self.server.plugin_manager.disable_plugin(self)
            return

        self.scoreboard_handler = ScoreboardHandler(self)
        self.bossbar_handler = BossbarHandler(self)

        self.register_events(self)

        self.scoreboard_handler.load()
        self.bossbar_handler.load()

    def on_disable(self) -> None:
        if hasattr(self, "scoreboard_handler"):
            self.scoreboard_handler.disable()
        if hasattr(self, "bossbar_handler"):
            self.bossbar_handler.disable()

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        if args and args[0].lower() == "reload":
            self.scoreboard_handler.disable()
            self.bossbar_handler.disable()
            
            self.scoreboard_config = self._load_config("scoreboard.yml")
            self.bossbar_config = self._load_config("bossbar.yml")
            
            self.scoreboard_handler.load()
            self.bossbar_handler.load()
            
            sender.send_message(f"{self.prefix} Configuration reloaded.")
            return True
        return False
