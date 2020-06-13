class Settings:
    def __init__(self):
        self.create_game_emoji = '🎮'

        self.play_game_emoji = '▶️'
        self.join_game_emoji = '✅'
        self.cancel_game_emoji = '❌'

        self.start_game_emojis = [self.play_game_emoji, self.join_game_emoji, self.cancel_game_emoji]

        self.stop_game_emoji = '🛑'

        self.player1_circle_emoji = '🔴'
        self.player2_circle_emoji = '🔵'
        self.player3_circle_emoji = '🟢'
        self.player4_circle_emoji = '🟡'

        self.player_circles = [self.player1_circle_emoji, self.player2_circle_emoji, self.player3_circle_emoji, self.player4_circle_emoji]
        self.hex_player_colors = [0xFF0000, 0xadd8e6, 0x008000, 0xFFFF00]

        self.left_direction_emoji = '⬅️'
        self.right_direction_emoji = '➡️'
        self.down_direction_emoji = '⬇️'
        self.up_direction_emoji = '⬆️'

        self.letter_emojis = ['🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯']
        self.number_emojis = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']
        self.direction_emojis = [self.left_direction_emoji, self.right_direction_emoji, self.down_direction_emoji, self.up_direction_emoji]
        self.placement_emojis = [self.left_direction_emoji, self.right_direction_emoji, self.down_direction_emoji, self.up_direction_emoji, '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        self.confirm_placement_emoji = '👍'

        self.shoot_emoji = '🔫'

        self.sea_emoji = '🌊'
        self.ship1_emoji = '⛵'
        self.ship2_emoji = '🚤'
        self.ship3_emoji = '🛥️'
        self.ship4_emoji = '⛴️'
        self.ship5_emoji = '🚢'

        self.house_emoji = '🏠'
        
        self.switch_grid_emojis = [self.house_emoji, self.player1_circle_emoji, self.player2_circle_emoji, self.player3_circle_emoji, self.player4_circle_emoji]

        self.ingame_emojis = [self.stop_game_emoji, self.left_direction_emoji, self.right_direction_emoji, self.down_direction_emoji, self.up_direction_emoji, '🇦', '🇧', '🇨', '🇩', '🇪', '🇫', '🇬', '🇭', '🇮', '🇯', '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟', self.confirm_placement_emoji, self.house_emoji, self.player1_circle_emoji, self.player2_circle_emoji, self.player3_circle_emoji, self.player4_circle_emoji, self.shoot_emoji]

        self.question_emoji = '❓'
        self.miss_emoji = '🚫'
        self.fire_emoji = '🔥'

        self.skull_emoji = '☠️'
        self.trophy_emoji = '🏆'