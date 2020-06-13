import discord
from player import Player
from settings import Settings

settings = Settings()

class Game():
    def __init__(self, player, guild, setuptxt, bot):
        self.creator = player
        self.guild = guild
        self.setuptxt = setuptxt
        self.bot = bot

        self.players = []
        self.add_player(player)
        self.playersalive = []

        self.firing = None

    def add_player(self, player):
        self.players.append(Player(player, len(self.players), self.bot))

    async def update_players(self):
        players = ""
        for player in self.players:
            players += player.user.mention + "\n"
        await self.setuptxt.edit(content = f'{self.creator.mention} wants to play battleship. React with {settings.join_game_emoji} to join.\nTo {self.creator.mention}, react with {settings.play_game_emoji} to start the game. Reacting with {settings.cancel_game_emoji} will cancel the game.\n\nPlayers ({len(self.players)}/4):\n{players}')

    async def start_game(self):
        await self.setuptxt.delete()

        self.playercount = len(self.players)

        for player in self.players:
            self.playersalive.append(player)

            overwrites = {
                self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                self.bot: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                player.user: discord.PermissionOverwrite(read_messages=True, send_messages=False),
            }
            player.channel = await self.guild.create_text_channel('battleship-ingame', overwrites=overwrites)

            player.introtxt = await player.channel.send(player.user.mention)

            players = ""
            for user in self.players:
                if user != player:
                    players += f'{settings.player_circles[user.playernum]} **{user.user.name}**\n'
                else:
                    players += f'{settings.player_circles[user.playernum]} **You**\n'

            embed = discord.Embed(title = f'Welcome to {settings.ship5_emoji} **Battleship**!', color = settings.hex_player_colors[self.players.index(player)])
            embed.add_field(name = '📜 **Rules**', value = f'The objective of this game is to sink all of your opponents ships. Ships are laid out in a 10x10 grid and each turn you choose one coordinate to fire upon. If you successfully guess where all your opponents ships are, you win!\n\n- *Be sure to keep track of the status message to see the game state.*\n- *This game tries to prevent user error as much as possible. If an action does not do anything, there may be an error with your input or you may not be allowed to execute it at that time.*\n\nThis game is entirely reaction controlled!\nReact with {settings.stop_game_emoji} to stop the game.')
            embed.add_field(name = '**Players**', value = players)
            await player.introtxt.edit(embed = embed)
            await player.introtxt.add_reaction(settings.stop_game_emoji)

            embed = discord.Embed(title = '***Battleship***', color = settings.hex_player_colors[self.players.index(player)])
            embed.add_field(name='**Status**', value = '*Setting up games*', inline=False)
            player.gametxt = await player.channel.send(embed = embed)

        for player in self.players:
            player.lettertxt = await player.channel.send("*Letters*")
            for emoji in settings.letter_emojis:
                await player.lettertxt.add_reaction(emoji)

        for player in self.players:
            player.numbertxt = await player.channel.send("*Numbers*")
            for emoji in settings.number_emojis:
                await player.numbertxt.add_reaction(emoji)

        for player in self.players:
            player.directiontxt = await player.channel.send("*Directions*")
            for emoji in settings.direction_emojis:
                await player.directiontxt.add_reaction(emoji)

        for player in self.players:
            player.optiontxt = await player.channel.send("*Confirm*")
            await player.optiontxt.add_reaction(settings.confirm_placement_emoji)
        
        for player in self.players:
            embed = player.gametxt.embeds[0]
            embed.set_field_at(0, name='**Status**', value = '*Waiting for players to place ships*', inline=False)
            embed.insert_field_at(1, name='**Instructions**', value = f'React with a **letter** and **number** coordinate as well as a **direction** for each ship.\nThis will place the bottom of the ship at the coordinate pivoting towards the direction chosen.\nReact with {settings.confirm_placement_emoji} to confirm each ship.', inline=False)
            embed.insert_field_at(2, name='**Your Grid**', value = player.get_grid(player.grid), inline=True)
            embed.insert_field_at(3, name='**Placing**', value = f'{settings.ship1_emoji} (2 units)', inline=True)

            await player.gametxt.edit(embed=embed)

            player.state = 'placing'

        self.players[0].opponentnum = 1
        if len(self.players) == 2:
            self.players[1].opponentnum = 0
        if len(self.players) == 3:
            self.players[1].opponentnum = 2
            self.players[2].opponentnum = 0
        if len(self.players) == 4:
            self.players[1].opponentnum = 2
            self.players[2].opponentnum = 3
            self.players[3].opponentnum = 0

        self.state = 'placing'



