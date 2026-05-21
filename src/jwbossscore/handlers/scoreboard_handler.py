from typing import TYPE_CHECKING
from endstone.scoreboard import Criteria, DisplaySlot, ObjectiveSortOrder, RenderType
from endstone.event import event_handler, EventPriority, PlayerJoinEvent, PlayerQuitEvent

if TYPE_CHECKING:
    from jwbossscore.main import JWBossScore


def _translate_colors(text: str) -> str:
    if not isinstance(text, str):
        return str(text)
    return text.replace("&", "§")


class ScoreboardHandler:
    _OBJ_NAME = "jw_sb"

    def __init__(self, plugin: "JWBossScore") -> None:
        self._plugin = plugin
        self._sessions: dict = {}
        self._lines: list[str] = []
        self._display_name: str = ""
        self._slot: DisplaySlot = DisplaySlot.SIDE_BAR
        self._ascending: bool = True
        self._enabled: bool = False
        self._update_task = None
        self._plugin.register_events(self)

    @property
    def _config(self) -> dict:
        return self._plugin.scoreboard_config

    def load(self) -> None:
        cfg = self._config
        if not cfg.get("enabled", False):
            self.disable()
            return

        self._display_name = cfg.get("display-name", "§6§lInfo")
        slot_str = cfg.get("slot", "sidebar").lower()
        self._slot = {
            "sidebar": DisplaySlot.SIDE_BAR,
            "list": DisplaySlot.PLAYER_LIST,
            "belowname": DisplaySlot.BELOW_NAME,
        }.get(slot_str, DisplaySlot.SIDE_BAR)

        self._ascending = cfg.get("ascending", True)
        self._lines = [line for line in cfg.get("lines", []) if line is not False]
        self._enabled = True

        self._schedule_update()

    def _create_session(self, player):
        uid = player.unique_id
        self._destroy_session(player)

        scoreboard = self._plugin.server.create_scoreboard()
        player.scoreboard = scoreboard

        sort_order = (
            ObjectiveSortOrder.ASCENDING
            if self._ascending
            else ObjectiveSortOrder.DESCENDING
        )

        objective = scoreboard.add_objective(
            self._OBJ_NAME,
            Criteria.DUMMY,
            _translate_colors(self._display_name),
            RenderType.INTEGER,
        )
        objective.set_display(self._slot, sort_order)

        self._sessions[uid] = {
            "scoreboard": scoreboard,
            "objective": objective,
        }

    def _destroy_session(self, player):
        session = self._sessions.pop(player.unique_id, None)
        if session is not None:
            try:
                session["scoreboard"].clear_slot(self._slot)
            except Exception:
                pass
        try:
            player.scoreboard = self._plugin.server.scoreboard
        except Exception:
            pass

    def _update_player(self, player):
        uid = player.unique_id
        session = self._sessions.get(uid)
        if session is None:
            self._create_session(player)
            session = self._sessions.get(uid)
            if session is None:
                return

        scoreboard = session["scoreboard"]
        objective = session["objective"]

        try:
            objective.display_name = _translate_colors(self._display_name)
        except Exception:
            pass

        try:
            for entry in list(scoreboard.entries):
                scoreboard.reset_scores(entry)
        except Exception:
            pass

        total = len(self._lines)

        for i, raw_line in enumerate(self._lines):
            # Parse placeholders via JWPlaceholderAPI
            text = self._plugin.papi.set_placeholders(player, raw_line)
            entry = _translate_colors(text)

            entry = entry + (" " * i)

            try:
                score = objective.get_score(entry)
                score.value = total - i
            except Exception:
                pass

    def _schedule_update(self):
        if self._update_task:
            return

        def task():
            if not self._enabled:
                self._update_task = None
                return
            for player in list(self._plugin.server.online_players):
                try:
                    self._update_player(player)
                except Exception:
                    pass

            self._update_task = self._plugin.server.scheduler.run_task(
                self._plugin, task, delay=20
            )

        self._update_task = self._plugin.server.scheduler.run_task(self._plugin, task, delay=20)

    def disable(self):
        self._enabled = False
        if self._update_task:
            self._update_task.cancel()
            self._update_task = None
        for player in list(self._plugin.server.online_players):
            try:
                self._destroy_session(player)
            except Exception:
                pass
        self._sessions.clear()

    @event_handler(priority=EventPriority.NORMAL)
    def on_player_join(self, event: PlayerJoinEvent):
        if not self._enabled:
            return
        player = event.player
        self._create_session(player)
        self._update_player(player)

    @event_handler(priority=EventPriority.NORMAL)
    def on_player_quit(self, event: PlayerQuitEvent):
        self._destroy_session(event.player)
