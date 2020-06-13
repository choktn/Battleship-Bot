import discord
import random
from timer import Timer
from settings import Settings

settings = Settings()

class Player():
    def __init__(self, player, number, bot):
        self.user = player
        self.playernum = number
        self.playercircle = settings.player_circles[number] 
        self.bot = bot
        self.channel = None
        self.hitmissmsg = None
        self.firingmsg = None
        self.sunkmsg = None
        self.msg = None

        self.introtxt = None
        self.gametxt = None
        self.lettertxt = None
        self.numbertxt = None
        self.directiontxt = None
        self.optiontxt = None

        self.grid = [[Tile(settings, 'sea', None)]*11 for y in range(11)]
        self.hitgrid = [[Tile(settings, 'sea', None)]*11 for y in range(11)]
        for x in range(len(self.grid)):
            for y in range(len(self.grid[x])):
                if x == 0 and y == 0:
                    self.grid[x][y] = Tile(settings, 'circle', self.playernum)
                    self.hitgrid[x][y] = Tile(settings, 'circle', self.playernum)
                elif x == 0 and y > 0:
                    self.grid[x][y] = Tile(settings, 'letter', y-1)
                    self.hitgrid[x][y] = Tile(settings, 'letter', y-1)
                elif x > 0 and y == 0:
                    self.grid[x][y] = Tile(settings, 'number', x-1)
                    self.hitgrid[x][y] = Tile(settings, 'number', x-1)

        self.ready = False
        self.state = 'placing'

        self.currship = 0
        self.ships = [
            {'name': 'sailboat', 'units': 2, 'hits': 0, 'emoji': settings.ship1_emoji},
            {'name': 'speedboat', 'units': 3, 'hits': 0, 'emoji': settings.ship2_emoji},
            {'name': 'motorboat', 'units': 3, 'hits': 0, 'emoji': settings.ship3_emoji},
            {'name': 'ferry', 'units': 4, 'hits': 0, 'emoji': settings.ship4_emoji},
            {'name': 'ship', 'units': 5, 'hits': 0, 'emoji': settings.ship5_emoji}
        ]

        self.replace_react = False
        self.tempplacesx = []
        self.tempplacesy = []

        self.tempx = None
        self.tempy = None

        self.letter = None
        self.number = None
        self.direction = None

        self.opponentnum = None

    def get_grid(self, grid):
        grid_str = ""

        for x in range(len(grid)):
            if x != 0:
                grid_str += "\n"
            for y in range(len(grid[x])):
                grid_str += " " + grid[x][y].emoji + " "

        return grid_str

    async def place_ship(self, game):
        if self.ready:
            if self.currship != 4:
                self.tempx = None
                self.tempy = None
                self.tempplacesx = []
                self.tempplacesy = []

                self.currship += 1

                await self.update_placementtxt()

                await self.lettertxt.remove_reaction(self.letter, self.user)
                await self.numbertxt.remove_reaction(self.number, self.user)
                await self.directiontxt.remove_reaction(self.direction, self.user)

                self.letter = None
                self.number = None
                self.direction = None

                self.ready = False
            else:
                self.state = 'firing'

                await self.lettertxt.remove_reaction(self.letter, self.user)
                await self.numbertxt.remove_reaction(self.number, self.user)
                await self.directiontxt.delete()

                self.letter = None
                self.number = None
                self.direction = None

                count = 0
                for player in game.players:
                    if player.state == 'firing':
                        count += 1

                if count == len(game.players):
                    await self.optiontxt.delete()
                    self.optiontxt = None

                    for player in game.players:
                        embed = player.gametxt.embeds[0]

                        embed.color = settings.hex_player_colors[player.opponentnum]

                        embed.set_field_at(0, name='**Status**', value = '*Setting up games*', inline=False)

                        circles = ''
                        for i in range(len(game.players)):
                            if i != player.playernum:
                                circles += f' {game.players[i].playercircle} '

                        if player.playernum != self.playernum:
                            embed.insert_field_at(1, name = '**Instructions**', value = f'React with a **letter** and **number** coordinate to fire.\nReact with{circles}to switch grids. React with {settings.house_emoji} to see your own grid.\nReact with {settings.shoot_emoji} to confirm each shot.', inline=False)
                            embed.set_field_at(2, name = f"**{game.players[player.opponentnum].user.name}'s Grid**", value = game.players[player.opponentnum].get_grid(game.players[player.opponentnum].hitgrid), inline=True)
                            embed.insert_field_at(3, name = '**Ships Alive**', value = f'{settings.ship1_emoji} (2 units)\n{settings.ship2_emoji} (3 units)\n{settings.ship3_emoji} (3 units)\n{settings.ship4_emoji} (4 units)\n{settings.ship5_emoji} (5 units)', inline=True)
                        else:
                            embed.set_field_at(1, name = '**Instructions**', value = f'React with a **letter** and **number** coordinate to fire.\nReact with{circles}to switch grids. React with {settings.house_emoji} to see your own grid.\nReact with {settings.shoot_emoji} to confirm each shot.', inline=False)
                            embed.set_field_at(2, name = f"**{game.players[player.opponentnum].user.name}'s Grid**", value = game.players[player.opponentnum].get_grid(game.players[player.opponentnum].hitgrid), inline=True)
                            embed.set_field_at(3, name = '**Ships Alive**', value = f'{settings.ship1_emoji} (2 units)\n{settings.ship2_emoji} (3 units)\n{settings.ship3_emoji} (3 units)\n{settings.ship4_emoji} (4 units)\n{settings.ship5_emoji} (5 units)', inline=True)
 
                        await player.gametxt.edit(embed = embed)
                        
                        await player.gametxt.add_reaction(settings.house_emoji)
                        for i in range(len(game.players)):
                            if i != player.playernum:
                                await player.gametxt.add_reaction(game.players[i].playercircle)

                    game.firing = random.randint(0, len(game.players)-1)

                    for player in game.players:
                        embed = player.gametxt.embeds[0]

                        if player.playernum != game.firing:
                            embed.set_field_at(0, name='**Status**', value = f'*Waiting for*  {game.players[game.firing].playercircle} ***{game.players[game.firing].user.name}*** *to fire.*', inline=False)
                        else:
                            embed.set_field_at(0, name='**Status**', value = f'*Waiting for*  {player.playercircle} ***You*** *to fire.*', inline=False)

                        await player.gametxt.edit(embed = embed)

                        if player.playernum == game.firing:
                            player.optiontxt = await player.channel.send("*Shoot*")
                            await player.optiontxt.add_reaction(settings.shoot_emoji)
                            player.firingmsg = await player.channel.send(f'{player.user.mention} You are firing')

                    game.state = 'firing'
                else:
                    await self.optiontxt.delete()

                    self.optiontxt = None

                    embed = self.gametxt.embeds[0]

                    embed.remove_field(1)
                    embed.remove_field(2)
                    
                    await self.gametxt.edit(embed = embed)
                
                self.ready = False
        
        if self.optiontxt:
            await self.optiontxt.remove_reaction(settings.confirm_placement_emoji, self.user)

    async def shoot(self, game, opponent):
        if self.ready:
            await self.optiontxt.delete()
            await self.firingmsg.delete()
            self.optiontxt = None
            self.firingmsg = None

            sunkship = None
            defeated = None
            if opponent.grid[self.tempx][self.tempy].type == 'sea':
                opponent.grid[self.tempx][self.tempy] = Tile(settings, 'miss', None)
                opponent.hitgrid[self.tempx][self.tempy] = Tile(settings, 'miss', None)
            else:
                ship = None
                index = 0

                for i in range(len(opponent.ships)):
                    if opponent.ships[i]['name'] == opponent.grid[self.tempx][self.tempy].type:
                        ship = opponent.ships[i]
                        index = i

                        break

                ship['hits'] += 1
                if ship['hits'] == ship['units']:
                    del opponent.ships[index]

                    if len(opponent.ships) == 0:
                        defeated = True

                        game.playersalive.remove(opponent)
                        game.players[opponent.playernum].state = 'spectating'

                    sunkship = ship

                opponent.grid[self.tempx][self.tempy] = Tile(settings, 'hit', None)
                opponent.hitgrid[self.tempx][self.tempy] = Tile(settings, 'hit', None)

            currfiring = opponent.playernum

            if game.firing != len(game.players) - 1:
                game.firing += 1
            else:
                game.firing = 0
            while game.players[game.firing].state != 'firing':
                if game.firing != len(game.players) - 1:
                    game.firing += 1
                else:
                    game.firing = 0

            for player in game.players:
                if player.hitmissmsg:
                    await player.hitmissmsg.delete()
                    player.hitmissmsg = None

                if player.sunkmsg:
                    await player.sunkmsg.delete()
                    player.sunkmsg = None

                if player.msg:
                    await player.msg.delete()
                    player.msg = None
                
                result = None
                if opponent.grid[self.tempx][self.tempy].type == 'miss':
                    result = 'missed'
                else:
                    result = 'hit'

                if len(game.playersalive) != 1:
                    embed = player.gametxt.embeds[0]

                    shotmessage = ''
                    firingmessage = ''
                    
                    if player.playernum != self.playernum:
                        if player.playernum != currfiring:
                            shotmessage += f'{self.playercircle} ***{self.user.name}*** *shot* {game.players[opponent.playernum].playercircle} ***{opponent.user.name}*** *at*  {self.letter} {self.number} *and*  {opponent.grid[self.tempx][self.tempy].emoji} *{result}*!'
                            if sunkship:
                                shotmessage += f"\n{self.playercircle} ***{self.user.name}*** *sunk* {game.players[opponent.playernum].playercircle} ***{opponent.user.name}***'s  {ship['emoji']} {ship['name']}!"
                        
                        else:
                            shotmessage += f'{self.playercircle} ***{self.user.name}*** *shot* {game.players[player.playernum].playercircle} ***You*** *at*  {self.letter} {self.number} *and*  {opponent.grid[self.tempx][self.tempy].emoji} *{result}*!'
                            if sunkship:
                                shotmessage += f"\n{self.playercircle} ***{self.user.name}*** *sunk* {game.players[player.playernum].playercircle} ***Your***  {ship['emoji']} {ship['name']}!"

                    else:
                        shotmessage += f'{self.playercircle} ***You*** *shot* {game.players[opponent.playernum].playercircle} ***{opponent.user.name}*** *at*  {self.letter} {self.number} *and*  {opponent.grid[self.tempx][self.tempy].emoji} *{result}*!'
                        if sunkship:
                                shotmessage += f"\n{self.playercircle} ***You*** *sank* {game.players[opponent.playernum].playercircle} ***{opponent.user.name}***'s  {ship['emoji']} {ship['name']}!"
                        
                    if defeated:
                        if player.playernum != opponent.playernum:
                            shotmessage += f'\n{settings.skull_emoji} {game.players[opponent.playernum].playercircle} ***{opponent.user.name} has been defeated!*** {settings.skull_emoji}'
                        else:
                            shotmessage += f'\n{settings.skull_emoji} {game.players[opponent.playernum].playercircle} ***You have been defeated!*** {settings.skull_emoji}'
                                
                    if player.playernum != game.firing:
                        firingmessage += f'*Waiting for*  {game.players[game.firing].playercircle} ***{game.players[game.firing].user.name}*** *to fire.*'
                    else:
                        firingmessage += f'*Waiting for*  {game.players[player.playernum].playercircle} ***You*** *to fire.*'

                    embed.set_field_at(0, name='**Status**', value = f'{shotmessage}\n{firingmessage}', inline = False)

                    if defeated:
                        await player.gametxt.remove_reaction(game.players[opponent.playernum].playercircle, self.bot)
                        
                        if player.opponentnum == opponent.playernum:
                            if player.playernum == opponent.playernum:
                                await player.lettertxt.delete()
                                await player.numbertxt.delete()
                                
                                player.lettertxt = None
                                player.numbertxt = None
                            player.opponentnum = player.playernum

                    await player.switch_grid(game, game.players[player.opponentnum].playercircle)

                    await player.gametxt.edit(embed = embed)

                if len(game.playersalive) != 1:
                    if player.playernum == game.firing:
                        player.optiontxt = await player.channel.send("*Shoot*")
                        await player.optiontxt.add_reaction(settings.shoot_emoji)

                if player.playernum != self.playernum and player.playernum == currfiring:
                    player.hitmissmsg = await player.channel.send(f'{player.user.mention} {self.user.mention} shot you and {result}!')
                    
                    if sunkship:
                        player.sunkmsg = await player.channel.send(f'{player.user.mention} {self.user.mention} sunk one of your ships!')

                if player.playernum == self.playernum:
                    if result == 'hit':
                        player.hitmissmsg = await player.channel.send(f'{player.user.mention} Hit!')
                    else:
                        player.hitmissmsg = await player.channel.send(f'{player.user.mention} Missed!')

                    if sunkship:
                        player.sunkmsg = await player.channel.send(f'{player.user.mention} You sunk a ship!')

                if len(game.playersalive) != 1:
                    if player.playernum == game.firing:
                        player.firingmsg = await player.channel.send(f'{player.user.mention} You are firing')

                if defeated:
                    if player.playernum != opponent.playernum:
                        player.msg = await player.channel.send(f'{player.user.mention} {settings.skull_emoji} {opponent.user.mention} ***has been defeated!*** {settings.skull_emoji}')
                    else:
                        player.msg = await player.channel.send(f'{player.user.mention} {settings.skull_emoji} ***You have been defeated!*** You are now spectating. {settings.skull_emoji}')

                if len(game.playersalive) == 1:
                    await player.gametxt.delete()
                    if player.lettertxt:
                        await player.lettertxt.delete()
                    if player.numbertxt:
                        await player.numbertxt.delete()
                    if player.optiontxt:
                        await player.optiontxt.delete()

                    player.letter = None
                    player.number = None

                    if player.playernum != game.playersalive[0].playernum:
                        await player.channel.send(f'{player.user.mention} {settings.trophy_emoji} ***Congratulations to*** {game.playersalive[0].playercircle} ***{game.playersalive[0].user.name} for winning the game!*** {settings.trophy_emoji}')
                    else:
                        await player.channel.send(f'{player.user.mention} {settings.trophy_emoji} ***Congratulations to*** {player.playercircle} ***You for winning the game!*** {settings.trophy_emoji}')
                    
                    await player.channel.send(f'{player.user.mention} {settings.create_game_emoji} ***The game has ended and will close soon.*** {settings.create_game_emoji}')
                     
                    Timer(30, player.delete_channel)
            
            if self.tempx:
                self.tempx = None
            if self.tempy:
                self.tempy = None

    async def update_placement(self, emoji):
        if self.letter and self.number and self.direction:
            self.ready = False

            self.reset_placements()

            x = settings.number_emojis.index(self.number)
            y = settings.letter_emojis.index(self.letter)

            x += 1
            y += 1

            xlist = []
            ylist = []
            for i in range(self.ships[self.currship]['units']):
                if x > 0 and x < 11 and y > 0 and y < 11 and (self.grid[x][y].type == 'sea' or self.grid[x][y].type == self.ships[self.currship]['name']):
                    xlist.append(x)
                    ylist.append(y)
                else:
                    if emoji in settings.direction_emojis:
                        await self.directiontxt.remove_reaction(self.direction, self.user)

                        self.direction = None
                    elif emoji in settings.letter_emojis:
                        await self.lettertxt.remove_reaction(emoji, self.user)

                        self.letter = None
                    elif emoji in settings.number_emojis:
                        await self.numbertxt.remove_reaction(emoji, self.user)

                        self.number = None

                    await self.update_placementtxt()

                    return

                if self.direction == settings.left_direction_emoji:
                    y -= 1
                elif self.direction == settings.right_direction_emoji:
                    y += 1
                elif self.direction == settings.down_direction_emoji:
                    x += 1
                elif self.direction == settings.up_direction_emoji:
                    x -= 1

            for i in range(len(xlist)):
                self.grid[xlist[i]][ylist[i]] = Tile(settings, self.ships[self.currship]['name'], None)

                self.tempplacesx.append(xlist[i])
                self.tempplacesy.append(ylist[i])

            self.ready = True
        elif self.letter and self.number:
            self.ready = False

            x = settings.number_emojis.index(self.number)
            y = settings.letter_emojis.index(self.letter)

            x += 1
            y += 1

            if self.grid[x][y].type != 'sea':
                await self.directiontxt.remove_reaction(emoji, self.user)

                if emoji in settings.letter_emojis:
                    await self.lettertxt.remove_reaction(emoji, self.user)

                    self.letter = None
                elif emoji in settings.number_emojis:
                    await self.numbertxt.remove_reaction(emoji, self.user)

                    self.number = None
        else:
            self.ready = False

            self.reset_placements()

        await self.update_placementtxt()
    
    async def update_hit(self, opponent, emoji):
        if self.letter and self.number:
            self.ready = False

            if self.tempx and self.tempy:
                opponent.hitgrid[self.tempx][self.tempy] = Tile(settings, 'sea', None)

            self.tempx = settings.number_emojis.index(self.number)
            self.tempy = settings.letter_emojis.index(self.letter)

            self.tempx += 1
            self.tempy += 1

            if opponent.hitgrid[self.tempx][self.tempy].type == 'sea':
                opponent.hitgrid[self.tempx][self.tempy] = Tile(settings, 'mark', None)

                self.ready = True
            else:
                if emoji in settings.letter_emojis:
                    self.tempy = None

                    await self.lettertxt.remove_reaction(emoji, self.user)

                    self.letter = None
                elif emoji in settings.number_emojis:
                    self.tempx = None

                    await self.numbertxt.remove_reaction(emoji, self.user)

                    self.number = None
        else:
            self.ready = False

            if self.tempx and self.tempy:
                if opponent.hitgrid[self.tempx][self.tempy].type == 'mark':
                    opponent.hitgrid[self.tempx][self.tempy] = Tile(settings, 'sea', None)

        await self.update_hittxt(opponent)

    async def update_placementtxt(self):
        embed = self.gametxt.embeds[0]

        embed.set_field_at(2, name='**Your Grid**', value = self.get_grid(self.grid), inline=True)
        embed.set_field_at(3, name='**Placing**', value = f"{self.ships[self.currship]['emoji']} ({self.ships[self.currship]['units']} units)", inline=True)
        
        await self.gametxt.edit(embed = embed)
    
    async def update_hittxt(self, opponent):
        embed = self.gametxt.embeds[0]

        embed.set_field_at(2, name=f"**{opponent.user.name}'s Grid**", value = opponent.get_grid(opponent.hitgrid), inline=True)
        
        ships = ''
        for ship in opponent.ships:
            ships += f"{ship['emoji']} ({ship['units']} units)"
            ships += '\n'
        embed.set_field_at(3, name = '**Ships Alive**', value = ships, inline=True)

        await self.gametxt.edit(embed = embed)

    async def switch_grid(self, game, circle):
        if game.firing == self.playernum and self.tempx and self.tempy:
            game.players[self.opponentnum].hitgrid[self.tempx][self.tempy] = Tile(settings, 'sea', None)

        if circle != settings.house_emoji:
            self.opponentnum = settings.player_circles.index(circle)
        else:
            self.opponentnum = self.playernum

        oppponent = game.players[self.opponentnum]

        embed = self.gametxt.embeds[0]
        
        embed.color = settings.hex_player_colors[self.opponentnum]
        if self.opponentnum == self.playernum:
            embed.set_field_at(2, name='**Your Grid**', value = self.get_grid(self.grid), inline=True)
        elif self.state == 'spectating':
            embed.set_field_at(2, name = f"**{oppponent.user.name}'s Grid**", value = oppponent.get_grid(oppponent.grid), inline=True)
        else:
            embed.set_field_at(2, name = f"**{oppponent.user.name}'s Grid**", value = oppponent.get_grid(oppponent.hitgrid), inline=True)
        
        ships = ''
        for ship in oppponent.ships:
            ships += f"{ship['emoji']} ({ship['units']} units)"
            ships += '\n'
        embed.set_field_at(3, name = '**Ships Alive**', value = ships, inline=True)

        await self.gametxt.edit(embed = embed)

    def reset_placements(self):
        if self.tempplacesx:
            for i in range(len(self.tempplacesx)):
                self.grid[self.tempplacesx[i]][self.tempplacesy[i]] = Tile(settings, 'sea', None)

            self.tempplacesx = []
            self.tempplacesy = []

    async def delete_channel(self):
        await self.channel.delete()
        self.channel = None

class Tile():
    def __init__(self, settings, type, num):
        settings = settings

        self.type = type
        self.num = num

        self.emoji = None

        if self.type == 'circle':
            self.emoji = settings.player_circles[self.num]
        elif self.type == 'letter':
            self.emoji = settings.letter_emojis[self.num]
        elif self.type == 'number':
            self.emoji = settings.number_emojis[self.num]
        elif self.type == 'sea':
            self.emoji = settings.sea_emoji
        elif self.type == 'sailboat':
            self.emoji = settings.ship1_emoji
        elif self.type == 'speedboat':
            self.emoji = settings.ship2_emoji
        elif self.type == 'motorboat':
            self.emoji = settings.ship3_emoji
        elif self.type == 'ferry':
            self.emoji = settings.ship4_emoji
        elif self.type == 'ship':
            self.emoji = settings.ship5_emoji
        elif self.type == 'mark':
            self.emoji = settings.question_emoji
        elif self.type == 'miss':
            self.emoji = settings.miss_emoji
        elif self.type == 'hit':
            self.emoji = settings.fire_emoji


    


