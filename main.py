import discord
from discord.ext import commands
import json
import os

TOKEN = "DEIN_BOT_TOKEN_HIER"  # Ersetze dies mit deinem Bot-Token
bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())

# Datei für gespeicherte Accounts
DATA_FILE = "accounts.json"

# Lade bestehende Accounts oder erstelle eine leere Datei
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump([], f)

def load_accounts():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(DATA_FILE, "w") as f:
        json.dump(accounts, f, indent=4)

# Befehl, um einen neuen Account hinzuzufügen
@bot.command()
async def add_account(ctx, name: str, price: str, image: str, *, description: str):
    accounts = load_accounts()
    accounts.append({"name": name, "price": price, "image": image, "description": description, "sold": False})
    save_accounts(accounts)

    embed = discord.Embed(title=name, description=description, color=discord.Color.blue())
    embed.set_image(url=image)
    embed.add_field(name="Preis", value=price, inline=False)

    view = AccountView(name)
    message = await ctx.send(embed=embed, view=view)
    view.set_message(message)

# Befehl, um alle Accounts zu sehen
@bot.command()
async def list_accounts(ctx):
    accounts = load_accounts()
    if not accounts:
        await ctx.send("Es gibt keine Accounts.")
        return

    for account in accounts:
        embed = discord.Embed(title=account["name"], description=account["description"], color=discord.Color.green())
        embed.set_image(url=account["image"])
        embed.add_field(name="Preis", value=account["price"], inline=False)
        if account["sold"]:
            embed.set_footer(text="✅ Verkauft")

        view = AccountView(account["name"])
        message = await ctx.send(embed=embed, view=view)
        view.set_message(message)

# Befehl, um einen Account zu löschen
@bot.command()
async def remove_account(ctx, name: str):
    accounts = load_accounts()
    new_accounts = [acc for acc in accounts if acc["name"] != name]

    if len(new_accounts) == len(accounts):
        await ctx.send(f"Kein Account mit dem Namen {name} gefunden.")
        return

    save_accounts(new_accounts)
    await ctx.send(f"Account {name} wurde gelöscht.")

# Button-Logik
class AccountView(discord.ui.View):
    def __init__(self, account_name):
        super().__init__(timeout=None)
        self.account_name = account_name

    @discord.ui.button(label="Buy this Account", style=discord.ButtonStyle.green)
    async def buy_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f"{interaction.user.mention} möchte den Account **{self.account_name}** kaufen!", ephemeral=True)

    @discord.ui.button(label="Mark as Sold", style=discord.ButtonStyle.red)
    async def sold_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        accounts = load_accounts()
        for acc in accounts:
            if acc["name"] == self.account_name:
                acc["sold"] = True
                break
        save_accounts(accounts)

        await interaction.response.send_message(f"✅ **{self.account_name} wurde als verkauft markiert!**", ephemeral=True)

# Starte den Bot
bot.run(TOKEN)
