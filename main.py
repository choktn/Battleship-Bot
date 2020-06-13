import discord
from game import Game
from settings import Settings
from timer import Timer

settings = Settings()
games = []

bot_id = ''

def user_isplaying(user):
    global games

    if not games:
        return False

    for i in range(len(games)):
        if games[i].players:
            for j in range(len(games[i].players)):
                if games[i].players[j].user == user:
                    return True
    return False

def setup_get_game(id):
    for game in games:
        if id == game.setuptxt.id:
            return game
    return False

def ingame_get_game_and_player(payload):
    for i in range(len(games)):
        for j in range(len(games[i].players)):
            if payload.user_id == games[i].players[j].user.id:
                return games[i], games[i].players[j]
    return False, False


class MyClient(discord.Client):
    async def on_ready(self):
        print(f'Successfuly went online as {self.user}')
        
        await self.change_presence(activity=discord.Game(name="bb game"))

    async def on_message(self, message):
        channel = message.channel

        if message.content.startswith('bb game'):
            embed = discord.Embed(title = f'Welcome to {settings.ship5_emoji} **Battleship**!', color = 0x3285a8)
            embed.add_field(name = '📜 **Rules**', value = f'The objective of this game is to sink all of your opponents ships. Ships are laid out in a 10x10 grid and each turn you choose one coordinate to fire upon. If you successfully guess where all your opponents ships are, you win!\n\nThis game is entirely reaction controlled!\nReact with {settings.create_game_emoji} to start a queue for a new game!')
            mainmsg = await channel.send(embed = embed)
            await mainmsg.add_reaction(settings.create_game_emoji)

    async def on_raw_reaction_add(self, payload):
        if payload.user_id == self.user.id:
            return

        global games
        channel = await self.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)

        if payload.emoji.name == settings.create_game_emoji:
            if message.author == self.user:
                await message.remove_reaction(payload.emoji.name, payload.member)
                
                if not user_isplaying(payload.member):
                    setuptxt = await channel.send(f'{payload.member.mention} wants to play battleship. React with {settings.join_game_emoji} to join.\nTo {payload.member.mention}, react with {settings.play_game_emoji} to start the game. Reacting with {settings.cancel_game_emoji} will cancel the game.\n\nPlayers (1/4):\n{payload.member.mention}')
                    
                    for emoji in settings.start_game_emojis:
                        await setuptxt.add_reaction(emoji)
                    
                    games.append(Game(payload.member, self.get_guild(payload.guild_id), setuptxt, self.user))

        if payload.emoji.name in settings.start_game_emojis:
            currgame = setup_get_game(payload.message_id)

            if not currgame:
                return

            if payload.emoji.name == settings.play_game_emoji:
                if payload.member == currgame.creator and len(currgame.players) >= 2:
                    await currgame.start_game()
                else:
                    await currgame.setuptxt.remove_reaction(payload.emoji.name, payload.member)

            elif payload.emoji.name == settings.join_game_emoji and len(currgame.players) <= 4:
                if not user_isplaying(payload.member):
                    currgame.add_player(payload.member)
                    await currgame.update_players()
                else:
                    await currgame.setuptxt.remove_reaction(payload.emoji.name, payload.member)

            elif payload.emoji.name == settings.cancel_game_emoji:
                if payload.member == currgame.creator:
                    await currgame.setuptxt.delete()
                    games.remove(currgame)
                else:
                    await currgame.setuptxt.remove_reaction(payload.emoji.name, payload.member)

        elif payload.emoji.name in settings.ingame_emojis:

            currgame, currplayer = ingame_get_game_and_player(payload)

            if not currgame or payload.channel_id != currplayer.channel.id:
                return

            if payload.emoji.name == settings.stop_game_emoji:
                for player in currgame.players:
                    if player.user != currplayer.user:
                        await player.channel.send(f'{player.user.mention} {currplayer.user.mention} has stopped the game. The game will close shortly.')
                    else:
                        await player.channel.send(f'{player.user.mention} You have stopped the game. The game will close shortly.')

                    Timer(5, player.delete_channel)
                games.remove(currgame)
                
                return

            if payload.emoji.name in settings.letter_emojis:
                if currplayer.letter:
                    currplayer.replace_react = True
                    await currplayer.lettertxt.remove_reaction(currplayer.letter, payload.member)

                currplayer.letter = payload.emoji.name

            elif payload.emoji.name in settings.number_emojis:
                if currplayer.number:
                    currplayer.replace_react = True
                    await currplayer.numbertxt.remove_reaction(currplayer.number, payload.member)

                currplayer.number = payload.emoji.name
            
            elif payload.emoji.name in settings.direction_emojis:
                if currplayer.direction:
                    currplayer.replace_react = True
                    await currplayer.directiontxt.remove_reaction(currplayer.direction, payload.member)

                currplayer.direction = payload.emoji.name

            elif payload.emoji.name == settings.confirm_placement_emoji:
                await currplayer.place_ship(currgame)

            elif payload.emoji.name in settings.switch_grid_emojis:
                await currplayer.switch_grid(currgame, payload.emoji.name)

                await currplayer.gametxt.remove_reaction(payload.emoji.name, payload.member)

            elif payload.emoji.name == settings.shoot_emoji:
                if currgame.firing == currplayer.playernum and currplayer.opponentnum != currplayer.playernum:
                    await currplayer.shoot(currgame, currgame.players[currplayer.opponentnum])

                if len(currgame.playersalive) == 1:
                    games.remove(currgame)


            if currplayer.state == 'placing':
                await currplayer.update_placement(payload.emoji.name)

            if currplayer.state == 'firing':
                if currgame.firing == currplayer.playernum and currplayer.opponentnum != currplayer.playernum:
                    await currplayer.update_hit(currgame.players[currplayer.opponentnum], payload.emoji.name)
                else:
                    if currplayer.letter:
                        await currplayer.lettertxt.remove_reaction(currplayer.letter, payload.member)

                        currplayer.letter = None

                    if currplayer.number:
                        await currplayer.numbertxt.remove_reaction(currplayer.number, payload.member)

                        currplayer.number = None

                    
    async def on_raw_reaction_remove(self, payload):
        if payload.user_id == self.user.id:
            return

        if payload.emoji.name == settings.join_game_emoji:
            currgame = setup_get_game(payload.message_id)

            if not currgame:
                return

            if payload.user_id != currgame.creator.id:
                for player in currgame.players:
                    if payload.user_id == player.user.id:
                        currgame.players.remove(player)
                        await currgame.update_players()
                        
                        break
            
        if payload.emoji.name in settings.placement_emojis:
            currgame, currplayer = ingame_get_game_and_player(payload)
            
            if not currgame or payload.channel_id != currplayer.channel.id:
                return

            if not currplayer.replace_react:
                if payload.emoji.name in settings.letter_emojis:
                    currplayer.letter = None

                elif payload.emoji.name in settings.number_emojis:
                    currplayer.number = None
                
                elif payload.emoji.name in settings.direction_emojis:
                    currplayer.direction = None

                if currplayer.state == 'placing':
                    await currplayer.update_placement(payload.emoji.name)

                if currplayer.state == 'firing' and currgame.firing == currplayer.playernum and currplayer.opponentnum != currplayer.playernum:
                    await currplayer.update_hit(currgame.players[currplayer.opponentnum], payload.emoji.name)
                
                return
            else:
                currplayer.replace_react = False
                return

client = MyClient()
client.run(bot_id)
