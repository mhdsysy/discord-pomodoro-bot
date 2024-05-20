import discord
from discord.ext import commands, tasks
import asyncio
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
import sqlite3

# Load environment variables from .env file
load_dotenv()

# Retrieve the Discord token from environment variables
TOKEN = os.getenv('DISCORD_TOKEN')

# Set up intents for the bot to receive messages
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True  # Enable the message content intent

# Create an instance of the bot with a command prefix and intents
bot = commands.Bot(command_prefix='!', intents=intents)

# Initialize SQLite database
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

@bot.event
async def on_ready():
    """
    Event handler for when the bot has connected to Discord.
    This function is called when the bot is ready.
    """
    print(f'Bot {bot.user.name} has connected to Discord!')
    update_time_spent.start()

    # Send a message to the default channel to hint users about the !pomohelp command
    default_channel = discord.utils.get(bot.get_all_channels(), guild__name='YOUR_GUILD_NAME', name='general')
    if default_channel:
        await default_channel.send('Hello! Use the `!pomohelp` command to see what I can do!')

current_task = None
bound_channel_id = None

@bot.command(name='bind')
@commands.has_permissions(administrator=True)
async def bind(ctx, *args):
    """
    Command to bind the bot to a specific channel.
    Only administrators can use this command.
    """
    global bound_channel_id
    try:
        channel_id = int(args[0])
        print(f'Parsed argument - Channel ID: {channel_id}')
    except (IndexError, ValueError) as e:
        await ctx.send("""Invalid or missing channel ID. The command should look like this: `!bind <channel_id>`""")
        return

    channel = bot.get_channel(channel_id)
    if channel is None:
        await ctx.send("Invalid channel ID. Please provide a valid channel ID.")
        return

    bound_channel_id = channel_id
    await ctx.send(f"Bot bound to channel {channel.mention}.")
    print(f"Bot bound to channel ID: {bound_channel_id}")

@bot.command(name='start')
@commands.has_permissions(administrator=True)
async def start(ctx, *args):
    """
    Command to start a Pomodoro session.
    Only administrators can use this command.
    """
    global current_task, bound_channel_id
    if bound_channel_id is None:
        await ctx.send("No channel is bound. Use `!bind <channel_id>` to bind a channel first.")
        return

    try:
        work_time = int(args[0])
        break_time = int(args[1])
        print(f'Parsed arguments - Work time: {work_time}, Break time: {break_time}')
    except (IndexError, ValueError) as e:
        await ctx.send("""Some arguments are missing or invalid. The command should look like this: 
`!start` `<work_time_in_minutes>` `<break_time_in_minutes>`""")
        return

    if current_task is not None:
        await ctx.send("A Pomodoro session is already running. Please stop the current session before starting a new one.")
        return

    channel = bot.get_channel(bound_channel_id)
    if channel is None:
        await ctx.send("Invalid channel ID. Use `!bind <channel_id>` to bind a valid channel.")
        return

    async def pomodoro_session():
        """
        Function to manage the Pomodoro session.
        Alternates between work and break times.
        """
        global current_task, bound_channel_id
        try:
            await ctx.send(f"Pomodoro session started for {work_time} minutes of work and {break_time} minutes of break time.")
            while current_task is not None and bound_channel_id is not None:
                await channel.send(f"@here Pomodoro session started for {work_time} minute(s)!")
                await asyncio.sleep(work_time * 60)
                await channel.send(f"@here Pomodoro session ended! Break time for {break_time} minute(s)!")
                await asyncio.sleep(break_time * 60)
        except asyncio.CancelledError:
            await channel.send("Pomodoro session was stopped.")
            print("Pomodoro session was stopped.")
        finally:
            current_task = None
            bound_channel_id = None
            print("Pomodoro session task cleaned up.")

    current_task = asyncio.create_task(pomodoro_session())
    await ctx.send("Pomodoro session task created.")
    print("Pomodoro session task started.")

@bot.command(name='unbind')
@commands.has_permissions(administrator=True)
async def unbind(ctx):
    """
    Command to unbind the bot from the current channel and reset the database.
    Only administrators can use this command.
    """
    global bound_channel_id
    if bound_channel_id is None:
        await ctx.send("No channel is currently bound.")
        return

    bound_channel_id = None

    try:
        conn = sqlite3.connect('user_times.db')
        c = conn.cursor()
        c.execute('DELETE FROM user_times')
        conn.commit()
        await ctx.send("Bot has been unbound from the channel and the database has been reset.")
        print("Bot unbound and database reset.")
    except sqlite3.Error as e:
        await ctx.send("Error resetting the database.")
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

@bot.command(name='stop')
async def stop(ctx):
    """
    Command to stop the current Pomodoro session.
    """
    global current_task, bound_channel_id
    if bound_channel_id is None:
        await ctx.send("No channel is bound. Use `!bind <channel_id>` to bind a channel first.")
        return
    if current_task is None:
        await ctx.send("No Pomodoro session is currently running.")
        return
    current_task.cancel()
    await ctx.send("Pomodoro session stopped.")
    print("Pomodoro session stopped by user command.")

@tasks.loop(minutes=1)
async def update_time_spent():
    """
    Task to update the total time spent by each user in the bound channel.
    This runs every second.
    """
    global bound_channel_id, user_times
    if bound_channel_id is None:
        return
    channel = bot.get_channel(bound_channel_id)
    if channel is None:
        return
    try:
        conn = sqlite3.connect('user_times.db')
        c = conn.cursor()
        c.execute('BEGIN TRANSACTION')
        for member in channel.members:
            if member.bot:
                continue
            user_id = member.id
            elapsed = 60  # 1 minute in seconds
            c.execute('SELECT total_time FROM user_times WHERE user_id = ?', (user_id,))
            row = c.fetchone()
            if row is None:
                c.execute('INSERT INTO user_times (user_id, total_time) VALUES (?, ?)', (user_id, elapsed))
                print(f"Inserted new user {user_id} with elapsed time {elapsed} seconds.")
            else:
                total_time = row[0] + elapsed
                c.execute('UPDATE user_times SET total_time = ? WHERE user_id = ?', (total_time, user_id))
                print(f"Updated user {user_id} with new total time {total_time} seconds.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

@bot.command(name='time')
async def time(ctx):
    """
    Command to check the total time spent by the user in the bound channel.
    """
    if bound_channel_id is None:
        await ctx.send("No channel is bound. Use `!bind <channel_id>` to bind a channel first.")
        return
    member = ctx.author
    try:
        conn = sqlite3.connect('user_times.db')
        c = conn.cursor()
        c.execute('SELECT total_time FROM user_times WHERE user_id = ?', (member.id,))
        row = c.fetchone()
    except sqlite3.Error as e:
        await ctx.send("Error retrieving data.")
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()
    if row is None:
        await ctx.send(f"{member.display_name} has not spent any time in the bound channel.")
        print(f"User {member.id} has no recorded time in the bound channel.")
        return
    total_time_seconds = row[0]
    total_time_minutes = total_time_seconds / 60
    await ctx.send(f"{member.display_name} has spent {total_time_minutes:.2f} minutes in the bound channel.")
    print(f"User {member.id} has spent {total_time_minutes:.2f} minutes in the bound channel.")

@bot.command(name='leaderboard')
async def leaderboard(ctx):
    """
    Command to display the top 10 users by time spent in the bound channel.
    """
    if bound_channel_id is None:
        await ctx.send("No channel is bound. Use `!bind <channel_id>` to bind a channel first.")
        return

    try:
        conn = sqlite3.connect('user_times.db')
        c = conn.cursor()
        c.execute('SELECT user_id, total_time FROM user_times ORDER BY total_time DESC LIMIT 10')
        rows = c.fetchall()
    except sqlite3.Error as e:
        await ctx.send("Error retrieving leaderboard data.")
        print(f"Database error: {e}")
        return
    finally:
        if conn:
            conn.close()

    if not rows:
        await ctx.send("No data available to display the leaderboard.")
        print("No data available to display the leaderboard.")
        return

    leaderboard_message = "🏆 **Top 10 Users by Time Spent in Channel** 🏆\n"
    for idx, (user_id, total_time) in enumerate(rows, start=1):
        member = await bot.fetch_user(user_id)
        total_time_minutes = total_time / 60
        leaderboard_message += f"{idx}. {member.display_name} - {total_time_minutes:.2f} minutes\n"
        print(f"Leaderboard entry {idx}: User {user_id}, Time {total_time_minutes:.2f} minutes")

    await ctx.send(leaderboard_message)

@bot.command(name='pomohelp')
async def help_command(ctx):
    """
    Command to display the list of available commands and their usage.
    """
    help_message = """
    **Bot Commands:**
    `!bind <channel_id>` - Bind the bot to a channel.
    `!start <work_time_in_minutes> <break_time_in_minutes>` - Start a Pomodoro session.
    `!stop` - Stop the current Pomodoro session.
    `!unbind` - Unbind the bot from the current channel and reset the database.
    `!time` - Check the total time spent in the bound channel.
    `!leaderboard` - Display the top 10 users by time spent in the bound channel.
    """
    await ctx.send(help_message)
    print("Displayed help message.")

# Run the bot with the specified token
bot.run(TOKEN)
