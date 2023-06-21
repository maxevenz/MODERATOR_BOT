import random
import discord


class Choice(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.value = None

    @discord.ui.button(label="Орел", style=discord.ButtonStyle.blurple)
    async def confirm(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = "орел"
        self.stop()

    @discord.ui.button(label="Решка", style=discord.ButtonStyle.blurple)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.value = "решка"
        self.stop()


class RockPaperScissors(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(
                label="Ножницы", description="Вы выбираете ножницы.", emoji="✂"
            ),
            discord.SelectOption(
                label="Камень", description="Вы выбираете камень.", emoji="🪨"
            ),
            discord.SelectOption(
                label="Бумага", description="Вы выбираете бумагу.", emoji="🧻"
            ),
        ]
        super().__init__(
            placeholder="Выбор за вами...",
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction: discord.Interaction):
        choices = {
            "камень": 0,
            "бумага": 1,
            "ножницы": 2,
        }
        user_choice = self.values[0].lower()
        user_choice_index = choices[user_choice]

        bot_choice = random.choice(list(choices.keys()))
        bot_choice_index = choices[bot_choice]

        result_embed = discord.Embed(color=0x9C84EF)
        result_embed.set_author(
            name=interaction.user.name, icon_url=interaction.user.avatar.url
        )

        if user_choice_index == bot_choice_index:
            if user_choice_index == 1:
                user_choice = 'бумагу'
            if bot_choice_index == 1:
                bot_choice = 'бумагу'
            result_embed.description = f"**Ничья!**\nВы выбрали {user_choice}, и я тоже выбрал {bot_choice}."
            result_embed.colour = 0xF59E42
        elif user_choice_index == 0 and bot_choice_index == 2:
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice}, а я {bot_choice}."
            result_embed.colour = 0x32CD32
        elif user_choice_index == 1 and bot_choice_index == 0:
            user_choice = 'бумагу'
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice}, а я {bot_choice}."
            result_embed.colour = 0x32CD32
        elif user_choice_index == 2 and bot_choice_index == 1:
            result_embed.description = f"**Вы выиграли!**\nВы выбрали {user_choice}, а я {bot_choice}."
            result_embed.colour = 0x32CD32
        else:
            if user_choice_index == 1:
                user_choice = 'бумагу'
            if bot_choice_index == 1:
                bot_choice = 'бумагу'
            result_embed.description = (
                f"**Я выиграл!**\nВы выбрали {user_choice}, а я {bot_choice}."
            )
            result_embed.colour = 0xE02B2B
            # не знаю почему ниже пайчарм выделяет ошибку, все на самом деле работает нормально и референс на месте
        await interaction.response.edit_message(
            embed=result_embed, content=None, view=None
        )


class RockPaperScissorsView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(RockPaperScissors())
