import discord
from discord import app_commands
from discord.ext import commands

TOKEN =

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

orders = {}
order_counter = 1

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Bot is online as {bot.user}")

@tree.command(name="create_order", description="Post a new order with status and customer")
@app_commands.describe(
    user="The customer who ordered",
    item="Item or service ordered",
    price="Price of the item",
    status="Initial status of the order"
)
@app_commands.choices(
    status=[
        app_commands.Choice(name="Processing", value="processing"),
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Done", value="done")
    ]
)
async def create_order(
    interaction: discord.Interaction,
    user: discord.Member,
    item: str,
    price: str,
    status: app_commands.Choice[str]
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    global order_counter
    order_id = order_counter
    order_counter += 1

    embed = discord.Embed(
        title=f"Order #{order_id}",
        color=discord.Color.from_str("#FFFFFF")

)

    embed.description = f"""
⠀⠀<:00pt_pnkheart:1341288093520498740> ⠀﹕⠀⠀**order⠀⠀lineup**⠀⠀<:2_bow:1341288110713077811> 
⠀⠀⠀⠀⠀⠀⠀{user.mention} {item}⠀⠀!
⠀⠀⠀⠀⠀⠀⠀1 order **₱ {price}**

⠀⠀⠀⠀⠀⠀⠀{status.name}
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀♡⠀⠀⠀⠀
"""

    message = await interaction.channel.send(embed=embed)
    await message.create_thread(name=f"Order #{order_id} - {user.name}")

    orders[order_id] = message.id

    await interaction.response.send_message(f"Order #{order_id} created for {user.mention}!", ephemeral=True)
    
@tree.command(name="edit_order", description="Edit the status of an existing order")
@app_commands.describe(
    order_id="The ID of the order to edit",
    status="New status for the order"
)
@app_commands.choices(
    status=[
        app_commands.Choice(name="Processing", value="processing"),
        app_commands.Choice(name="Pending", value="pending"),
        app_commands.Choice(name="Done", value="done")
    ]
)
async def edit_order(
    interaction: discord.Interaction,
    order_id: int,
    status: app_commands.Choice[str]
):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    if order_id not in orders:
        await interaction.response.send_message("Order ID not found.", ephemeral=True)
        return

    channel = interaction.channel
    message_id = orders[order_id]
    try:
        message = await channel.fetch_message(message_id)
        embed = message.embeds[0]

        lines = embed.description.split('\n')

        lines[-2] = f"⠀⠀⠀⠀⠀⠀⠀{status.name}" 

        embed.description = '\n'.join(lines)
        await message.edit(embed=embed)

        await interaction.response.send_message(f"Order #{order_id} updated to **{status.name}**.", ephemeral=True)

    except Exception as e:
        await interaction.response.send_message(f"Failed to edit the order: {e}", ephemeral=True)
        print(e)

bot.run(TOKEN)