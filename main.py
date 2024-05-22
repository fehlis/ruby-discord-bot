import asyncio
import discord
import achievement_parser as aparser
import os

TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL_NAME = 'current-achievement-hunt'
GUILD_ID = 1242214818883178638  # get this from your server

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
        print('Logged on as', self.user)
        guild = self.get_guild(GUILD_ID)
        if guild:
            # Find the channel by name
            self.channel = discord.utils.get(guild.channels, name=CHANNEL_NAME)
            if self.channel:
                # Print the channel ID
                print(f'Channel ID for {CHANNEL_NAME}: {self.channel.id}')

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == '/post':
            await self.post(message)

        elif message.content == '/update':
            await self.update(message)
            
    async def post(self, message):
        ruby_games = aparser.parse_exophase()
        postmsg = aparser.generate_message(ruby_games)
        await self.channel.send(postmsg)
        print(f'posted message')
        await message.channel.send('posted!')
            
    async def update(self, message):
        ruby_games = aparser.parse_exophase()
        postmsg = aparser.generate_message(ruby_games)
        
        # Retrieve the list of pinned messages
        pinned_messages = await self.channel.pins()
        if pinned_messages:
            # Assume we want to edit the first pinned message
            message_to_edit = pinned_messages[0]
            # Edit the message content
            await message_to_edit.edit(content=postmsg)
            print(f'Edited pinned message: {message_to_edit.id}')
            await message.channel.send('Updated!')                

intents = discord.Intents.default()
#intents.message_content = True
client = MyClient(intents=intents)
client.run(TOKEN)
