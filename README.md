# JWBossScore

A powerful, highly customizable Scoreboard and Bossbar plugin for Endstone Minecraft servers. 
This plugin brings dynamic, per-player sidebars and server-wide bossbars with full placeholder support to your server without any flickering.

**⚠️ Requirements:**
This plugin **requires** [JWPlaceholderAPI](https://github.com/junggamyeon/JWPlaceholderAPI) to function. Make sure you install it on your server before using JWBossScore!

## 🚀 Features
- **Dynamic Scoreboard (Sidebar):** Display real-time stats for each player.
- **Customizable Bossbar:** Display a server-wide bossbar with custom colors, styles, and progress.
- **JWPlaceholderAPI Integration:** Use any registered placeholder (e.g., `%player_name%`, `%server_online%`, `%jweco_balance%`).
- **Flicker-Free:** Uses Endstone's native Objective and BossBar APIs for smooth updates.
- **Configurable Refresh Rates:** Control exactly how often the bossbar and scoreboard update to optimize server performance.

## 💻 Commands & Permissions
| Command | Aliases | Permission | Description |
|---|---|---|---|
| `/jwbossscore reload` | `/jwboss reload` | `jwbossscore.admin` | Reloads the `scoreboard.yml` and `bossbar.yml` configurations. |

## ⚙️ Configuration

When you first run the plugin, it will generate two configuration files in the `plugins/JWBossScore/` directory.

### 1. `scoreboard.yml`
Configure your sidebar here. You can use standard Endstone color codes (`§` or `&`) and any placeholders from JWPlaceholderAPI.

```yaml
enabled: true
display-name: "&b&lMy Server"
slot: "sidebar" # Can be sidebar, list, or belowname
ascending: true
lines:
  - "&7-------------------"
  - "&fPlayer: &e%player_name%"
  - "&fPing: &a%player_ping% ms"
  - ""
  - "&fMoney: &e$%jweco_balance_short%"
  - ""
  - "&fOnline: &a%server_online%&f/&a%server_max_players%"
  - "&7-------------------"
```

### 2. `bossbar.yml`
Configure the server-wide Bossbar.

```yaml
enabled: true
title: "&6&lWelcome to %server_name%, &e%player_name%&6!"
color: "blue"      # Options: pink, blue, red, green, yellow, purple, white
style: "solid"     # Options: solid, 6, 10, 12, 20 (segments)
progress: 1.0      # Float from 0.0 to 1.0
auto-refresh-seconds: 5 # How often the text updates
flags:
  - "darken_sky"
  # - "create_fog"
```

## 🔗 Supported Placeholders
Since JWBossScore is powered by [JWPlaceholderAPI](https://github.com/junggamyeon/JWPlaceholderAPI), you can use placeholders from any other plugin that registers an expansion.

**Built-in Examples:**
- `%player_name%`, `%player_ping%`, `%player_x%`, `%player_y%`, `%player_z%`, `%player_health%`
- `%server_online%`, `%server_max_players%`, `%server_name%`

**If you have [JWEconomy](https://github.com/junggamyeon/JWEconomy) installed:**
- `%jweco_balance%` (Shortened: 1.5M, 10k)
- `%jweco_balance_raw%` (Exact amount: 1500000.00)
