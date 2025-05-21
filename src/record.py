import discord
from discord.ext import commands
import asyncio

# Set up your bot’s intents.
intents = discord.Intents.default()
intents.message_content = True  # Needed to read message content for commands.

# Create the bot (using "!" as the command prefix).
bot = commands.Bot(command_prefix="!", intents=intents)

# -----------------------------------------------------------------------------
# A custom audio sink class that “receives” raw Opus packets.
#
# In Pycord (or similar forks), a sink class can be used to process incoming
# voice data. Here we simply collect raw data (per user) into bytearrays.
# In a real implementation you might decode the Opus data to PCM (and then
# write a WAV file) or use ffmpeg to convert it.
# -----------------------------------------------------------------------------
class AudioRecorder(discord.AudioSink):
    def __init__(self):
        super().__init__()
        # Dictionary to store recorded data per user (keyed by user ID).
        self.audio_data = {}

    # The write() method is called with each chunk of audio data.
    # (The method signature and behavior may vary with the fork/version you use.)
    def write(self, data: bytes, user: discord.Member) -> None:
        if user.id not in self.audio_data:
            self.audio_data[user.id] = bytearray()
        self.audio_data[user.id].extend(data)

# Global variables to hold the current recording state.
recording = False
recorder = None

# -----------------------------------------------------------------------------
# Bot event and commands
# -----------------------------------------------------------------------------
@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")

@bot.command()
async def join(ctx):
    """Joins the voice channel you’re in."""
    if ctx.author.voice is None:
        await ctx.send("You are not in a voice channel!")
        return

    channel = ctx.author.voice.channel
    try:
        vc = await channel.connect()
        await ctx.send(f"Joined **{channel}**!")
    except Exception as e:
        await ctx.send(f"Failed to join voice channel: {e}")

@bot.command()
async def toggle(ctx):
    """
    Toggles voice recording on/off in the current voice channel.
    When turning off, the recorded raw audio data for each user is saved
    to a separate file (named <userID>_recording.opus).
    """
    global recording, recorder
    vc = ctx.voice_client
    if vc is None:
        await ctx.send("I'm not connected to a voice channel!")
        return

    if not recording:
        # Start recording:
        recorder = AudioRecorder()
        try:
            vc.listen(recorder)
        except Exception as e:
            await ctx.send(f"Error starting recording: {e}")
            return
        recording = True
        await ctx.send("Recording **started**!")
    else:
        # Stop recording:
        vc.stop_listening()
        recording = False

        # Save recorded data for each user to a file.
        # (This writes raw Opus packets; you may want to convert them to WAV/MP3.)
        saved_files = []
        for user_id, data in recorder.audio_data.items():
            filename = f"{user_id}_recording.opus"
            try:
                with open(filename, "wb") as f:
                    f.write(data)
                saved_files.append(filename)
            except Exception as e:
                await ctx.send(f"Error saving file for user {user_id}: {e}")

        if saved_files:
            await ctx.send("Recording **stopped** and saved to files:\n" +
                           "\n".join(saved_files))
        else:
            await ctx.send("Recording stopped but no data was recorded.")

@bot.command()
async def leave(ctx):
    """Disconnects from the voice channel."""
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel!")
    else:
        await ctx.send("I'm not in a voice channel!")

# -----------------------------------------------------------------------------
# Run the bot (replace YOUR_BOT_TOKEN with your bot's token)
# -----------------------------------------------------------------------------
bot.run("YOUR_BOT_TOKEN")
