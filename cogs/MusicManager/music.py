import re
import discord
import requests
from pytube import YouTube
from validators import url as is_valid_url

from bot import Bot


class Music:
    last_voice: discord.VoiceProtocol = None

    @classmethod
    async def connect(cls, channel: discord.VoiceChannel) -> discord.VoiceProtocol:
        bot = Bot.instance
        voice = discord.utils.get(bot.voice_clients, guild=channel.guild)
        if voice and voice.is_connected():
            await voice.move_to(channel)
        else:
            voice = await channel.connect()

        cls.last_voice = voice
        return voice

    @classmethod
    def search(cls, search_query: str, max_videos: int = 0) -> list:
        with requests.get(f"https://www.youtube.com/results?search_query={search_query}") as search:
            video_ids = re.findall(r"watch\?v=(\S{11})", search.content.decode())
            if max_videos > len(video_ids):
                max_videos = len(video_ids)

        return [f"https://www.youtube.com/watch?v={video_ids[video_id]}" for video_id in range(max_videos)]

    @classmethod
    def play(cls, url: str, voice: discord.VoiceClient = None):
        voice = voice or cls.last_voice
        if not is_valid_url(url):
            url = cls.search(url, 1)[0]

        yt = YouTube(url)
        audio = yt.streams.filter(only_audio=True).first()
        od = discord.FFmpegPCMAudio(audio.url)
        voice.play(od)

    @classmethod
    def resume(cls, voice: discord.VoiceClient = last_voice):
        voice.resume()

    @classmethod
    def stop(cls, voice: discord.VoiceClient = last_voice):
        voice.stop()

    @classmethod
    def pause(cls, voice: discord.VoiceClient = last_voice):
        voice.pause()
