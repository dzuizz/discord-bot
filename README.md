# discord-bot

A Python implementation of a Discord bot using the `discord.py` library.

## Features

- **Lonely Chat**: Provides motivational responses to lonely users.
- **Experience and Ranking System**: Tracks user messages and assigns ranks based on experience points.
- **Interactive Commands**: Includes commands such as `/ping`, `/chat`, `/rank`, and `/stats`.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `discord.py` library
- `python-dotenv` library

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/discord-bot.git
    cd discord-bot
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your environment variables:
    ```ini
    DISCORD_TOKEN=your_discord_token
    GUILD_ID=your_guild_id
    WELCOME_CHANNEL_ID=your_welcome_channel_id
    ```

### Usage

1. Run the bot:
    ```bash
    python main.py
    ```

2. The bot should now be connected to your Discord server. Use the following commands:

    - **/ping**: Responds with "Pong!"
    - **/chat**: Toggles your membership in the lonely list.
    - **/rank**: Checks your current rank.
    - **/stats**: Displays your current stats.

### File Structure

```plaintext
discord-bot/
│
├── main.py                # The main script to run the bot
├── responses.py           # Contains the `lonely_chat` function
├── database.json          # Stores user data (auto-generated)
├── .env                   # Environment variables
├── requirements.txt       # List of required packages
└── README.md              # This README file
```

### Code Overview

#### main.py

This is the main script that sets up and runs the Discord bot. Key sections include:

- **Environment Variables**: Loads Discord token and guild ID from a `.env` file.
- **Bot Setup**: Initializes the Discord client with appropriate intents.
- **Message Processing**: Handles user messages, updates experience points, and responds to lonely users.
- **Commands**: Defines several bot commands using `discord.app_commands.CommandTree`.

### List of (app) Commands

- **/ping**
- **/chat**
- **/rank**
- **/exp**
- **/messages**
- **/stats**

### Todos

- **/play** (music in voice channel)
- **/trivia**
- **/poll**
- **/remind**
- **/weather**
- **/translate**

### Contributing

Feel free to submit issues or pull requests. For major changes, please open an issue first to discuss what you would like to change.
