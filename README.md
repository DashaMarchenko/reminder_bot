
# Telegram Reminder Bot

An asynchronous Telegram bot for scheduling reminders with
persistent SQLite storage and timezone-aware delivery.

Built with Python, aiogram, asyncio, and SQLite.

## Features

- Create reminders through an interactive Telegram interface
- Select dates using an inline calendar
- Set a preferred timezone for each user
- Convert local reminder times to UTC
- Handle daylight saving time transitions
- Store reminders persistently in SQLite
- Deliver overdue reminders after application restarts
- Submit bug reports to an administrator
- Run locally using long polling
- Automated tests using Python unittest

## Tech Stack

- Python 3.11
- aiogram 2.25.1
- asyncio
- SQLite
- FastAPI (webhook integration)
- zoneinfo
- unittest

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/DashaMarchenko/reminder_bot.git
cd reminder_bot
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure the bot

Copy `config/config.example.ini` to `config/config.ini`.

Set the following values:

- `BOT_TOKEN`: Telegram bot token obtained from BotFather
- `ADMIN_ID`: Telegram user ID of the administrator
- `HOST_URL`: Public HTTPS URL for webhook deployment

For local polling, a public HTTPS URL is not required.

Never commit your real bot token.

### 5. Start the bot

```bash
python run_polling.py
```

The bot will start receiving Telegram updates.

## Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Start interacting with the bot |
| `/timezone` | Select your preferred timezone |
| `/cancel` | Cancel the current operation |
| `/bug_report` | Send a bug report to the administrator |

Use the **Add reminder** button to create a reminder.

## How It Works

1. The user selects a date and enters a time.
2. The bot reads the user's configured timezone.
3. The local date and time are converted to UTC.
4. The reminder is stored in SQLite.
5. An asynchronous scheduler checks for due reminders.
6. The bot sends the Telegram message.
7. After successful delivery, the reminder is deleted.

## Running Tests

```bash
python -m unittest discover -s tests -p "test_*.py" -v
```

The test suite covers database operations, reminder scheduling,
timezone conversion, daylight saving time, API routes,
calendar generation, and Telegram handler registration.

## Project Structure

```text
app/           FastAPI application and webhook
calendars/     Interactive Telegram calendar
config/        Configuration loader and example
database/      SQLite database operations
handlers/      Telegram commands and conversations
tests/         Automated tests
bot_config.py  Shared bot configuration
buttons.py     Telegram keyboard definitions
schedule.py    Reminder delivery scheduler
run_polling.py Local polling entry point
```

## Current Limitations

- Designed primarily for a single running bot instance
- Reminder delivery follows an at-least-once approach
- Duplicate notifications are possible after certain failures
- Timezone selection currently offers a limited set of cities
- Ambiguous local times during DST transitions are rejected

## Future Improvements

- Atomic reminder claiming to support multiple workers
- Delivery status and retry management
- More timezone options
- Improved monitoring and error reporting
- Containerized deployment
