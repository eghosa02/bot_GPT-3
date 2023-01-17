import discord

class UI(discord.ui.View):
    reg:bool = None
    @discord.ui.button(label="retry", style=discord.ButtonStyle.gray, emoji="🔁")
    async def retry(self, interaction:discord.interactions, button:discord.ui.Button):
        self.reg = True
        for i in self.children:
            i.disabled = True
        self.stop()
        await interaction.response.defer()
    
    async def on_timeout(self):
        self.stop()