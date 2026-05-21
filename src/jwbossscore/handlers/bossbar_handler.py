from typing import TYPE_CHECKING

from endstone.boss import BarColor, BarFlag, BarStyle, BossBar
from endstone.event import event_handler, EventPriority, PlayerJoinEvent, PlayerQuitEvent

if TYPE_CHECKING:
    from jwbossscore.main import JWBossScore

_COLOR_MAP = {
    "pink": BarColor.PINK,
    "blue": BarColor.BLUE,
    "red": BarColor.RED,
    "green": BarColor.GREEN,
    "yellow": BarColor.YELLOW,
    "purple": BarColor.PURPLE,
    "white": BarColor.WHITE,
}

_STYLE_MAP = {
    "solid": BarStyle.SOLID,
    "6": BarStyle.SEGMENTED_6,
    "10": BarStyle.SEGMENTED_10,
    "12": BarStyle.SEGMENTED_12,
    "20": BarStyle.SEGMENTED_20,
}

_FLAG_MAP = {
    "darken_sky": BarFlag.DARKEN_SKY,
    "create_fog": BarFlag.CREATE_FOG,
}


class BossbarHandler:

    def __init__(self, plugin: "JWBossScore") -> None:
        self._plugin = plugin
        self._bar: BossBar | None = None
        self._title_template: str = ""
        self._color: BarColor = BarColor.RED
        self._style: BarStyle = BarStyle.SOLID
        self._progress: float = 1.0
        self._auto_refresh_seconds: int = 5
        self._refresh_task_handle = None
        self._plugin.register_events(self)

    def load(self) -> None:
        cfg = self._plugin.bossbar_config
        if not cfg.get("enabled", False):
            self.disable()
            return

        self._title_template = cfg.get("title", "&6&lServer Info")
        color_str = str(cfg.get("color", "red")).lower()
        style_str = str(cfg.get("style", "solid"))
        self._color = _COLOR_MAP.get(color_str, BarColor.RED)
        self._style = _STYLE_MAP.get(style_str, BarStyle.SOLID)
        self._progress = float(cfg.get("progress", 1.0))

        flags_list = cfg.get("flags", [])
        bar_flags = []
        for f in flags_list:
            f_lower = str(f).lower().replace(" ", "_")
            if f_lower in _FLAG_MAP:
                bar_flags.append(_FLAG_MAP[f_lower])

        refresh_seconds = int(cfg.get("auto-refresh-seconds", 5))
        self._auto_refresh_seconds = max(0, refresh_seconds)

        self._bar = self._plugin.server.create_boss_bar(
            self._resolve_title(),
            self._color,
            self._style,
            bar_flags if bar_flags else None,
        )
        self._bar.progress = self._progress

        for player in self._plugin.server.online_players:
            self._bar.add_player(player)

        self._schedule_refresh()

    def _resolve_title(self) -> str:
        players = list(self._plugin.server.online_players)
        player = players[0] if players else None

        # Resolve placeholder via JWPlaceholderAPI
        resolved_title = self._plugin.papi.set_placeholders(player, self._title_template)
        return resolved_title.replace("&", "§")

    def _schedule_refresh(self) -> None:
        if self._refresh_task_handle:
            try:
                self._refresh_task_handle.cancel()
            except Exception:
                pass
            self._refresh_task_handle = None

        if self._auto_refresh_seconds <= 0:
            return

        def refresh_loop():
            if self._bar:
                self._bar.title = self._resolve_title()
                for player in self._plugin.server.online_players:
                    if player not in self._bar.players:
                        self._bar.add_player(player)
            self._refresh_task_handle = self._plugin.server.scheduler.run_task(
                self._plugin, refresh_loop, delay=self._auto_refresh_seconds * 20
            )

        self._refresh_task_handle = self._plugin.server.scheduler.run_task(self._plugin, refresh_loop, delay=20)

    def disable(self) -> None:
        if self._refresh_task_handle:
            try:
                self._refresh_task_handle.cancel()
            except Exception:
                pass
            self._refresh_task_handle = None

        if self._bar:
            try:
                self._bar.remove_all()
            except Exception:
                pass
            self._bar = None

    @event_handler(priority=EventPriority.NORMAL)
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        if self._bar:
            self._bar.add_player(event.player)

    @event_handler(priority=EventPriority.NORMAL)
    def on_player_quit(self, event: PlayerQuitEvent) -> None:
        if self._bar:
            try:
                self._bar.remove_player(event.player)
            except Exception:
                pass
