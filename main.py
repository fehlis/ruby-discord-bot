import asyncio
import datetime
import discord
import achievement_parser as aparser
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = 'current-achievement-hunt'
GUILD_ID = 1242214818883178638  # get this from your server

CACHE_TIMEOUT_SECONDS = 60
POLL_EXOPHASE_INTERVAL_SECONDS = 60 * 2 # 2 minutes

# TODO List:
# - make the bot periodically check for changes:
#   - cache last dict to disk
#   - check for new achievements periodically
#   - if changes are detected, trigger /update to update pinned post
#   - OPTIONAL: post a message to the channel that an update was done
# - post a message to the channel when a game is finished
# - Implement simple caching to prevent excessive server polling
#   - remember "last update time"
#   - if query would be made within too short period, return cached data instead

class MyClient(discord.Client):
    async def on_ready(self):
        self.last_update_message = ""
        self.last_update = datetime.datetime.fromtimestamp(0)
        self.last_completion_check = datetime.datetime.fromtimestamp(0)
        self.cached_ruby_games = []
        
        print('Logged on as', self.user)
        guild = self.get_guild(GUILD_ID)
        if guild:
            # Find the channel by name
            self.channel = discord.utils.get(guild.channels, name=CHANNEL_NAME)
            if self.channel:
                # Print the channel ID
                print(f'Channel ID for {CHANNEL_NAME}: {self.channel.id}')
                
        # check for a pinned message to use it for indicator for our last update
        pinned_messages = await self.channel.pins()
        if pinned_messages:
            # Assume we want to edit the first pinned message
            pinned_message = pinned_messages[0]
            #TODO: might have to use created_at in case the pinned message was never edited
            #pinned_message.created_at
            self.last_update = pinned_message.edited_at
            self.last_completion_check = pinned_message.edited_at
                            
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self.periodic_update())                

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == '/post':
            await self.post(message)

        elif message.content == '/update':
            await self.update(message)
            
    async def post(self, message=None):
        ruby_games = self.update_games_cached()
        postmsg = aparser.generate_message(ruby_games)
        await self.channel.send(postmsg)
        print(f'posted message')
        if message:
            await message.channel.send('posted!')
            
    async def update(self, message=None):
        ruby_games = self.update_games_cached()
        postmsg = aparser.generate_message(ruby_games)
        if postmsg == self.last_update_message:
            print('no update needed.') 
            if message:
                await message.channel.send('no update needed.') 
            return
        
        self.last_update_message = postmsg

        # Retrieve the list of pinned messages
        pinned_messages = await self.channel.pins()
        if pinned_messages:
            # Assume we want to edit the first pinned message
            message_to_edit = pinned_messages[0]
            # Edit the message content
            await message_to_edit.edit(content=postmsg)
            print(f'Edited pinned message: {message_to_edit.id}')            
            if message:
                await message.channel.send('Updated!')                

    async def periodic_update(self):
        while True:
            print("polling exophase for changes...")
            await self.update()
            await asyncio.sleep(POLL_EXOPHASE_INTERVAL_SECONDS)

    def update_games_cached(self) -> list: 
        now = datetime.datetime.now(datetime.UTC)
        if abs(now - self.last_update).total_seconds() > CACHE_TIMEOUT_SECONDS:
            self.cached_ruby_games = aparser.parse_exophase()
            completed_games = aparser.get_completed(self.cached_ruby_games, self.last_completion_check)
            self.last_update = now
        else:
            print("using cached results")
        return self.cached_ruby_games

intents = discord.Intents.default()
#intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)
