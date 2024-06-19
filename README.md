# PomodoroBot

PomodoroBot is a Discord bot designed to help users manage their time using the Pomodoro technique. This bot allows users to start, stop, and manage Pomodoro sessions, track the time spent, and view leaderboards.

## Features

- **Bind to Channel**: Bind the bot to a specific voice channel.
- **Start Pomodoro Session**: Start a Pomodoro session with specified work and break times.
- **Stop Pomodoro Session**: Stop the current Pomodoro session.
- **Unbind and Reset**: Unbind the bot from the current channel and reset the database.
- **Check Time**: Check the total time spent by the user in the bound channel.
- **Leaderboard**: Display the top 10 users by time spent in the bound channel.
- **Help Command**: Display the list of available commands and their usage.

## Commands

- `/bind <channel_id>`: Bind the bot to a channel.
- `/start <work_time_in_minutes> <break_time_in_minutes>`: Start a Pomodoro session.
- `/stop`: Stop the current Pomodoro session.
- `/unbind`: Unbind the bot from the current channel and reset the database.
- `/time`: Check the total time spent in the bound channel.
- `/leaderboard`: Display the top 10 users by time spent in the bound channel.
- `/pomohelp`: Display the list of available commands and their usage.

## Usage Example

1. **Bind the Bot to a Channel**

    ```plaintext
    /bind <channel_id>
    ```

2. **Start a Pomodoro Session**

    ```plaintext
    /start 25 5
    ```

    This will start a Pomodoro session with 25 minutes of work and 5 minutes of break time.

3. **Stop the Current Pomodoro Session**

    ```plaintext
    /stop
    ```

4. **Unbind the Bot and Reset the Database**

    ```plaintext
    /unbind
    ```

5. **Check Total Time Spent**

    ```plaintext
    /time
    ```

6. **Display the Leaderboard**

    ```plaintext
    /leaderboard
    ```

7. **Display Help Message**

    ```plaintext
    /pomohelp
    ```

## Docker Setup

To run the bot using Docker, follow these steps:

1. **Build the Docker Image**

    ```bash
    docker build -t pomodorobot .
    ```

2. **Run the Docker Container**

    ```bash
    docker run -d --name pomodorobot -v $(pwd)/user_times.db:/app/user_times.db --env-file .env pomodorobot
    ```

    This command will run the bot in a Docker container and mount the SQLite database file from the host machine.

## Environment Variables

The bot requires a `.env` file with the following environment variable:

- `BOT_TOKEN`: Your Discord bot token.

## Database

The bot uses an SQLite database (`user_times.db`) to store user times. The database is initialized automatically when the bot starts.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
