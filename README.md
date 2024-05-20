Here is the updated `README.md` file content including instructions for creating a virtual environment and installing dependencies from `requirements.txt`.

```markdown
# Pomodoro Discord Bot

This bot is designed to facilitate Pomodoro sessions within a Discord server. It includes commands for managing sessions, binding to channels, and tracking user activity.

## Features

- **Bind and Unbind**: Attach the bot to specific channels.
- **Start and Stop Pomodoro Sessions**: Admins can start and stop Pomodoro sessions.
- **Time Tracking**: Track the time users spend in the bound channel.
- **Leaderboard**: Display the top 10 users by time spent in the channel.
- **Help Command**: Display the list of available commands and their usage.

## Getting Started

### Prerequisites

- Python 3.6 or higher
- Discord.py library
- SQLite3
- `python-dotenv` library for managing environment variables

### Installation

1. **Clone the repository:**

    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Create a `.env` file in the root directory:**

    ```env
    DISCORD_TOKEN=your_discord_bot_token
    ```

4. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

5. **Run the bot:**

    ```bash
    python bot.py
    ```

## Commands

### Admin Commands

- `!bind <channel_id>`: Bind the bot to a specific channel. Only administrators can use this command.
- `!unbind`: Unbind the bot from the current channel and reset the database. Only administrators can use this command.
- `!start <work_time_in_minutes> <break_time_in_minutes>`: Start a Pomodoro session. Only administrators can use this command.
- `!stop`: Stop the current Pomodoro session. Only administrators can use this command.

### User Commands

- `!time`: Check the total time spent by the user in the bound channel.
- `!leaderboard`: Display the top 10 users by time spent in the bound channel.
- `!pomohelp`: Display the list of available commands and their usage.

## Code Overview

### Environment Setup

```python
from dotenv import load_dotenv
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
```

This part loads the environment variables from a `.env` file and retrieves the Discord bot token.

### Bot Initialization

```python
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)
```

The bot is initialized with specific intents to handle messages and message content.

### Database Initialization

```python
def init_db():
    try:
        conn = sqlite3.connect('user_times.db')
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS user_times (
                user_id INTEGER PRIMARY KEY,
                total_time REAL
            )
        ''')
        conn.commit()
        print("Database initialized successfully.")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

init_db()
```

An SQLite database is initialized to store user times.

### Event Handling

```python
@bot.event
async def on_ready():
    print(f'Bot {bot.user.name} has connected to Discord!')
    update_time_spent.start()

    default_channel = discord.utils.get(bot.get_all_channels(), guild__name='YOUR_GUILD_NAME', name='general')
    if default_channel:
        await default_channel.send('Hello! Use the `!pomohelp` command to see what I can do!')
```

This event handler runs when the bot is ready and starts the `update_time_spent` task.

### Commands

#### Bind Command

```python
@bot.command(name='bind')
@commands.has_permissions(administrator=True)
async def bind(ctx, *args):
    ...
```

This command binds the bot to a specific channel.

#### Start Command

```python
@bot.command(name='start')
@commands.has_permissions(administrator=True)
async def start(ctx, *args):
    ...
```

This command starts a Pomodoro session.

#### Unbind Command

```python
@bot.command(name='unbind')
@commands.has_permissions(administrator=True)
async def unbind(ctx):
    ...
```

This command unbinds the bot from the current channel and resets the database.

#### Stop Command

```python
@bot.command(name='stop')
async def stop(ctx):
    ...
```

This command stops the current Pomodoro session.

### Time Tracking Task

```python
@tasks.loop(minutes=1)
async def update_time_spent():
    ...
```

This task updates the total time spent by each user in the bound channel.

### User Commands

#### Time Command

```python
@bot.command(name='time')
async def time(ctx):
    ...
```

This command checks the total time spent by the user in the bound channel.

#### Leaderboard Command

```python
@bot.command(name='leaderboard')
async def leaderboard(ctx):
    ...
```

This command displays the top 10 users by time spent in the bound channel.

#### Help Command

```python
@bot.command(name='pomohelp')
async def help_command(ctx):
    ...
```

This command displays the list of available commands and their usage.

## Running the Bot

Run the bot using:

```bash
python bot.py
```

Make sure to keep your `.env` file secure and not share it publicly as it contains your bot token.

## Troubleshooting

- **Bot not responding**: Ensure the bot has the necessary permissions in the Discord server and the token is correctly specified.
- **Database issues**: Check the database file `user_times.db` for any corruption and ensure the bot has write permissions.

For further issues, check the console logs for error messages.
```

I will now provide you with a downloadable version of the `README.md` file.

[Download README.md](sandbox:/mnt/data/README.md)