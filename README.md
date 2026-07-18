# Hikari A.I.

Hikari A.I. is a multilingual Telegram bot that collects recent text messages from a group and turns them into an AI-generated chat digest. It can adapt the digest to the group's language and preferred tone, publish it on demand, and periodically generate digests for active groups.

> [!IMPORTANT]
> The bot processes names, usernames, Telegram user/chat IDs, reply context, and message text. Before using it in a real group, inform participants, obtain any consent required in your jurisdiction, and define an appropriate retention policy.

## Features

- Telegram bot built with [aiogram 3](https://docs.aiogram.dev/)
- AI summaries through the DeepSeek OpenAI-compatible API
- Five interface and digest languages: English, Russian, Kazakh, Ukrainian, and Chinese
- Three digest styles: automatic, cute, and cheeky
- Manual digest generation after at least 100 collected messages
- Per-group four-hour cooldown for manual digests
- Automatic digest task for active groups
- Per-group language and style settings
- Optional participant gender preference for digest context
- Admin panel with user/group statistics and broadcasts
- Local SQLite storage for users, groups, and cooldowns
- Bounded JSON message storage: up to 1,000 recent entries and approximately 25,000 characters
- API-key rotation when multiple DeepSeek keys are configured

## How it works

1. The bot receives text messages from Telegram groups.
2. It stores message metadata and text in a local `messages.json` runtime file.
3. When a digest is requested, the bot selects messages for that chat and removes numeric user/chat IDs before sending the payload to the AI provider. Names, usernames, message text, timestamps, and reply context remain in the request.
4. DeepSeek generates a Telegram-compatible HTML digest using the selected language and style prompt.
5. The bot sends the result to the group and attempts to pin its first part.
6. Successfully processed messages for that chat are removed from local message storage.

## Commands

| Command | Scope | Description |
| --- | --- | --- |
| `/digest` | Group | Generate a digest after 100 messages have been collected. Subject to a four-hour cooldown. |
| `/lang` | Group admins | Change the group language. |
| `/style` | Group admins | Choose automatic, cute, or cheeky digest style. |
| `/gender` | Group | Set the participant's gender hint used in stored digest context. |
| `/admin` | Private chat, configured admin only | Open statistics and broadcast controls. |

The bot also shows a language selector in private chat and an “Add to group” button after onboarding.

## Requirements

- Python 3.10 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- A [DeepSeek API](https://platform.deepseek.com/) key

## Installation

```bash
git clone https://github.com/polymathf/Hikari-A.I.git
cd Hikari-A.I

python -m venv .venv
```

Activate the virtual environment:

```bash
# Windows PowerShell
.venv\Scripts\Activate.ps1

# Linux or macOS
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Copy the environment template and fill in your own credentials:

```bash
# Windows PowerShell
Copy-Item .env.example .env

# Linux or macOS
cp .env.example .env
```

Required variables:

| Variable | Description |
| --- | --- |
| `BOT_TOKEN` | Telegram bot token issued by BotFather. |
| `ADMIN_ID` | Numeric Telegram user ID permitted to use `/admin`. |
| `DEEPSEEK_API_KEYS` | One DeepSeek key or several comma-separated keys used for rotation. |

Optional variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com` | OpenAI-compatible API base URL. |
| `DEEPSEEK_MODEL` | `deepseek-chat` | Model used for digest generation. |

Never put real credentials in source files or commit `.env`.

## Running the bot

```bash
python bot.py
```

On startup, the application creates the following local runtime files when needed:

- `users.db` — Telegram user IDs and selected interface languages
- `groups.db` — group IDs, language, status, creation time, and digest style
- `cooldowns.db` — command cooldowns per group
- `messages.json` — recent group messages and participant metadata

These files are intentionally excluded from Git because they may contain personal data.

## Project structure

```text
Hikari-A.I/
├── bot.py                  # Application entry point and polling setup
├── config.py               # Environment-based configuration and prompt mapping
├── digest.py               # AI client rotation, digest generation, and scheduler
├── requirements.txt        # Python dependencies
├── db/
│   ├── init_db.py          # SQLite schema initialization
│   ├── user.py             # User persistence
│   ├── group.py            # Group settings and status
│   ├── cooldown.py         # Command cooldown persistence
│   └── json_storage.py     # Bounded message storage
├── handlers/               # Telegram message, command, and callback handlers
├── routers/                # aiogram router registration
├── locales/languages.json  # Multilingual interface strings
├── prompts/                # Language- and style-specific AI prompts
└── utils/                  # Translation and HTML escaping helpers
```

## Privacy and security

- Keep `.env`, databases, message storage, logs, and backups out of version control.
- Revoke and replace a credential immediately if it has ever been committed, uploaded, or shared.
- The AI request excludes numeric `chat_id` and `user_id` fields, but it still includes names, usernames, message contents, timestamps, gender hints, admin status, and reply context.
- The default message store is local and unencrypted. Protect the host and restrict filesystem access.
- Review the prompts and provider's data-handling terms before production use.
- This repository does not implement user consent, deletion requests, encryption at rest, or a configurable retention period. Add the controls required for your deployment.
- The `cheeky` prompt intentionally asks the model for profanity and insulting language. Review or replace it before enabling that style in communities where harassment or unsafe content is a concern.

## Development notes

- The project uses long polling and in-memory FSM state, so pending admin broadcast state is lost after a restart.
- Runtime paths are relative to the current working directory. Start the bot from the repository root.
- Automatic scheduling runs inside the bot process; use a process manager such as systemd or Docker for reliable production restarts.
- There is currently no automated test suite.

## License

Distributed under the MIT License. See [LICENSE](LICENSE) for details.

## Disclaimer

This project is provided as-is. You are responsible for complying with Telegram's rules, the AI provider's terms, privacy laws, and consent requirements that apply to your deployment.
