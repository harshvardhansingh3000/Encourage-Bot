# **Encourage Bot**

Encourage Bot is a versatile and feature-rich Discord bot powered by AI, designed to enhance user interaction, automate tasks, and provide a personalized server experience. With features like smart reminders, music playback, moderation tools, and AI-driven conversation abilities, this bot is an all-in-one solution for Discord servers.

---

## **Features**

### 🤖 **AI-Powered Assistant**
- **Contextual Responses**: Provides responses tailored to the context.
- **Learning Capabilities**: Learns from conversations for better understanding.
- **Personalized Assistance**: Offers assistance based on user interaction.
- **Conversation History**: Maintains conversation history for improved communication.

### **Database Management (`CogDBMS`)**
- `!dbstatus`: Check the database connection status.
- `!track_activity @User`: Track activity patterns for a specific user.
- `!remember_context [text]`: Store a custom context for later use.
- `!show_rankings`: Display user activity rankings.
- `!set_reminder [delay] [task]`: Set smart reminders (`urgent`, `today`, `tomorrow`, `week`).
- `!categorize_message [message]`: Categorize a message's content.
- `!clear_context`: Clear stored conversation history.
- `!show_context [number]`: Show recent conversation history.
- `!avg_rating`: Get the average feedback rating.
- `!recent_feedback [number]`: Display recent feedback entries.

### **Embed Creation**
- `!create_embed`: Create an embed with custom input.
- `!server_info`: Display information about the server in an embed.
- `!random_cat_image`: Generate an embed with a cute cat image.

### **General Commands**
- `!hello`: Greet the bot.
- `!goodbye`: Say farewell.

### **Help Commands**
- `!help_command`: Show a list of all available commands.
- `!help_specific [command]`: Get detailed help for a specific command.

### **Interactive Components**
- `!menu`: Role selection menu.
- `!colors`: Color selection menu.
- `!game`: Start a button-clicking game.
- `!memory`: Play a memory-matching game.

### **Moderation**
- `!kick [@user]`: Kick a member.
- `!ban [@user]`: Ban a member.
- `!unban [@user]`: Unban a member.
- `!add_role [@user] [role]`: Add a role to a user.
- `!remove_role [@user] [role]`: Remove a role from a user.
- `!roleinfo`: Display details about a role.
- `!rolemembers [role]`: List all members with a specific role.

### **Music**
- `!join`: Bot joins your current voice channel.
- `!leave`: Bot leaves the voice channel.
- `!play [url]`: Play audio from a YouTube URL.
- `!volume [0-100]`: Adjust playback volume.
- `!pause`: Pause the current audio.
- `!resume`: Resume paused audio.
- `!stop`: Stop the audio playback.
- `!add [url]`: Add a YouTube URL to the queue.
- `!play_queue`: Play all audio files in the queue.
- `!play_playlist [url]`: Play a YouTube playlist.
- `!queue`: Display the current audio queue.
- `!song_info`: Show details about the currently playing song.
- `!now_playing`: Display playback progress.

### **Status Management**
- `!server_stats`: Display server member statistics.
- `!random_status`: Show a random bot status.

### **Suggestive Components**
- `!suggest [suggestion]`: Submit a suggestion.
- `!suggest list`: Display all active suggestions and their votes.
- `!suggest clear`: Clear all suggestions (Admin only).
- `!suggest help`: Get help with the suggestion system.

---

## **Requirements**
To run this bot, ensure the following are installed on your system:
1. **Python 3.12.7 or below**
2. **Required Libraries** (Install via `pip`):
   - discord.py
   - psycopg2
   - yt-dlp
   - Other dependencies (specified in `requirements.txt`):
     ```bash
     pip install -r requirements.txt
     ```
3. **Node.js Backend (Optional)** if used for extended functionality.
4. **PostgreSQL** (if utilizing database features).

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone https://github.com/yourusername/EncourageBot.git
cd EncourageBot
```
### **2. Set Up Environment Variables**
Create a `.env` file in the project directory and add the following:
```env
TOKEN=....
JOKEAPI =......
POSTGRES_DB=....
POSTGRES_USER=.....
POSTGRES_PASS=.....
POSTGRES_HOST=.....
POSTGRES_PORT=......
OPENAI_API_KEY=......
```

### **3. Add Required Audio File**
Add an audio file named `voice1.mp3` to the main directory. This is required for the `!join` command to function.

### **4. Install Dependencies**
Install the required Python libraries:
```bash
pip install -r requirements.txt
```

### 5. Install `libopus`
`libopus` is required for audio functionality. Follow these steps:

- **For Windows**:
  1. Download the `libopus` files from [this link](https://github.com/xiph/opus).
  2. Add the `.dll` file to your `PATH`.

- **For Linux**:
  ```bash
  sudo apt install libopus-dev
  ```
### 6. Install `ffmpeg`
`ffmpeg` is required for processing audio files. Follow these steps:

- **For Windows**:
  1. Download the `ffmpeg` binary from [ffmpeg.org](https://ffmpeg.org/).
  2. Extract the files and add the `bin` directory to your `PATH`.

- **For Linux**:
  ```bash
  sudo apt install ffmpeg
  ```
### 7. Run the Bot
Start the bot using:

```bash
python main.py
```

## Usage
Once the bot is running:

- Invite the bot to your server using its **OAuth2 URL**.
- Use `!help_command` to see a list of available commands.
- Try commands like `!hello`, `!play [url]`, `!kick @user`, and more!

---

## Contributing
We welcome contributions! Feel free to submit issues or pull requests to improve this bot.

---

## License
This project is licensed under the MIT License.


