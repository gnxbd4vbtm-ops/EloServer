import os
import asyncio
import aiohttp
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Optional, List, Dict, Any
import logging
import math


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

API_BASE = os.getenv("API_BASE", "http://localhost:8000/api/v1")



GAMEMODES = ["overall", "vanilla", "mace", "nethPot", "uhc", "diaPot", "sword", "axe"]
EMBED_COLORS = {
    "elite": discord.Color.purple(),
    "adept": discord.Color.blue(),
    "apprentice": discord.Color.green(),
    "master": discord.Color.red(),
    "diamond": discord.Color.from_rgb(0, 195, 255),
    "gold": discord.Color.gold(),
    "silver": discord.Color.light_grey(),
    "bronze": discord.Color.from_rgb(205, 127, 50),
    "default": discord.Color.dark_grey()
}

class ELOBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(command_prefix="!", intents=intents)
        self.session: Optional[aiohttp.ClientSession] = None

    async def setup_hook(self):
        """Setup hook for async initialization"""
        self.session = aiohttp.ClientSession()
        await self.tree.sync()
        logger.info("✅ Bot setup complete")

    async def close(self):
        """Cleanup on shutdown"""
        if self.session:
            await self.session.close()
        await super().close()

    async def api_request(self, endpoint: str) -> Dict[str, Any]:
        """Make API request with error handling"""
        url = f"{API_BASE}/{endpoint.lstrip('/')}"
        try:
            async with self.session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                resp.raise_for_status()
                return await resp.json()
        except asyncio.TimeoutError:
            raise Exception("Request timed out")
        except aiohttp.ClientError as e:
            raise Exception(f"API request failed: {e}")

bot = ELOBot()

def calculate_rank(elo: int) -> str:
    """Calculate rank based on ELO (same as models.py)"""
    if elo < 0:
        return "still smarter and better than Declan"
    elif elo < 100:
        return "a cute but dumb cat"
    elif elo < 200:
        return "Tier 09 - Combat Apprentice III"
    elif elo < 400:
        return "Tier 08 - Combat Apprentice II"
    elif elo < 600:
        return "Tier 07 - Combat Apprentice I"
    elif elo < 800:
        return "Tier 06 - Combat Adept III"
    elif elo < 1000:
        return "Tier 05 - Combat Adept II"
    elif elo < 1400:
        return "Tier 04 - Combat Adept I"
    elif elo < 1800:
        return "Tier 03 - Elite II"
    elif elo < 2200:
        return "Tier 02 - Elite I"
    elif elo < 2400:
        return "Tier 01 - Contender"
    else:
        return "get a life"

def get_rank_color(rank: str) -> discord.Color:
    """Get embed color based on rank"""
    rank_lower = rank.lower()
    if "elite" in rank_lower:
        return EMBED_COLORS["elite"]
    elif "adept" in rank_lower:
        return EMBED_COLORS["adept"]
    elif "apprentice" in rank_lower:
        return EMBED_COLORS["apprentice"]
    elif "contender" in rank_lower:
        return EMBED_COLORS["master"]
    elif "dumb cat" in rank_lower:
        return EMBED_COLORS["bronze"]
    else:
        return EMBED_COLORS["default"]

async def gamemode_autocomplete(
    interaction: discord.Interaction,
    current: str
) -> List[app_commands.Choice[str]]:
    """Autocomplete for gamemode selection"""
    return [
        app_commands.Choice(name=gm, value=gm)
        for gm in GAMEMODES
        if current.lower() in gm.lower()
    ]

@bot.event
async def on_ready():
    """Bot ready event"""
    logger.info(f"🤖 {bot.user} is online and ready!")
    logger.info(f"🌐 Connected to {len(bot.guilds)} guilds")

@bot.tree.command(name="elo", description="Get ELO stats for a Minecraft player")
@app_commands.autocomplete(gamemode=gamemode_autocomplete)
async def get_elo(
    interaction: discord.Interaction,
    ign: str,
    gamemode: Optional[str] = None
):
    """Get ELO information for a player"""
    await interaction.response.defer()

    try:
        data = await bot.api_request(f"elo/{ign}/")
    except Exception as e:
        return await interaction.followup.send(f"❌ Failed to fetch ELO data: {e}")

    entries = data.get(ign, [])
    if not entries:
        return await interaction.followup.send(f"❌ Player '{ign}' not found")

    
    if gamemode:
        entries = [e for e in entries if e["gamemode"].lower() == gamemode.lower()]
        if not entries:
            return await interaction.followup.send(f"❌ No {gamemode} data for '{ign}'")

    
    embed = discord.Embed(
        title=f"🎮 ELO Stats — {ign}",
        color=get_rank_color(entries[0]["rank"]),
        timestamp=discord.utils.utcnow()
    )

    for entry in entries:
        embed.add_field(
            name=f"🏆 {entry['gamemode'].title()}",
            value=(
                f"**ELO:** `{entry['elo']:,}`\n"
                f"**Rank:** {entry['rank']}\n"
                f"**Cat:** {entry['cat']}\n"
                f"**Last Updated:** <t:{int(discord.utils.parse_time(entry['last_updated']).timestamp())}:R>"
            ),
            inline=True
        )

    embed.set_footer(text="MCR ELO System")
    await interaction.followup.send(embed=embed)

async def fetch_leaderboard_page(gamemode: str, api_page: int) -> tuple[List[Dict], bool]:
    """Fetch leaderboard data for a page, return entries and has_next flag"""
    try:
        data = await bot.api_request(f"leaderboard/{gamemode}/?page={api_page}")
        entries = data.get(gamemode, [])
        has_next = len(entries) == 100
        return entries, has_next
    except Exception:
        return [], False

@bot.tree.command(name="leaderboard", description="View ELO leaderboard with pagination")
@app_commands.autocomplete(gamemode=gamemode_autocomplete)
async def leaderboard(
    interaction: discord.Interaction,
    gamemode: str,
    page: Optional[int] = 1
):
    """Display leaderboard for a gamemode"""
    await interaction.response.defer()

    if page < 1:
        page = 1

    entries, has_next = await fetch_leaderboard_page(gamemode, page)
    if not entries:
        return await interaction.followup.send(f"❌ No {gamemode} leaderboard data found")

    
    embed = create_leaderboard_embed(gamemode, page, entries[:10], (page-1)*100 + 1)

    
    view = LeaderboardView(gamemode, page, entries, has_next)
    await interaction.followup.send(embed=embed, view=view)

def create_leaderboard_embed(gamemode: str, api_page: int, players: List[Dict], start_rank: int) -> discord.Embed:
    """Create leaderboard embed for given players"""
    embed = discord.Embed(
        title=f"🏆 {gamemode.title()} Leaderboard",
        description=f"API Page {api_page}",
        color=get_rank_color(players[0]["rank"]) if players else EMBED_COLORS["default"],
        timestamp=discord.utils.utcnow()
    )

    for i, player in enumerate(players, start=start_rank):
        embed.add_field(
            name=f"
            value=(
                f"**ELO:** `{player['elo']:,}`\n"
                f"**Rank:** {player['rank']}\n"
                f"**Cat:** {player['cat']}"
            ),
            inline=False
        )
        if i < start_rank + len(players) - 1:  
            embed.add_field(name="ㅤ", value="─" * 30, inline=False)

    embed.set_footer(text="MCR ELO System")
    return embed

class LeaderboardView(discord.ui.View):
    """Navigation view for leaderboard pages"""
    def __init__(self, gamemode: str, api_page: int, entries: List[Dict], has_next_api_page: bool):
        super().__init__(timeout=300)
        self.gamemode = gamemode
        self.api_page = api_page
        self.entries = entries
        self.has_next_api_page = has_next_api_page
        self.discord_page = 0
        self.per_discord_page = 10
        self.max_discord_pages = math.ceil(len(entries) / self.per_discord_page)

        self.update_buttons()

    def update_buttons(self):
        """Update button states"""
        self.prev.disabled = self.discord_page <= 0
        self.next.disabled = (self.discord_page >= self.max_discord_pages - 1) and not self.has_next_api_page

    def get_current_embed(self) -> discord.Embed:
        """Get embed for current discord page"""
        start = self.discord_page * self.per_discord_page
        end = start + self.per_discord_page
        page_entries = self.entries[start:end]

        embed = discord.Embed(
            title=f"🏆 {self.gamemode.title()} Leaderboard",
            description=f"API Page {self.api_page} • Discord Page {self.discord_page + 1}/{self.max_discord_pages}",
            color=get_rank_color(page_entries[0]["rank"]) if page_entries else EMBED_COLORS["default"],
            timestamp=discord.utils.utcnow()
        )

        for i, player in enumerate(page_entries, start=start + (self.api_page-1)*100 + 1):
            embed.add_field(
                name=f"
                value=(
                    f"**ELO:** `{player['elo']:,}`\n"
                    f"**Rank:** {player['rank']}\n"
                    f"**Cat:** {player['cat']}"
                ),
                inline=False
            )

        embed.set_footer(text="MCR ELO System")
        return embed

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.secondary)
    async def prev(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.discord_page > 0:
            self.discord_page -= 1
        elif self.api_page > 1:
            
            await interaction.response.defer()
            await leaderboard.callback(interaction, self.gamemode, self.api_page - 1)
            return

        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_embed(), view=self)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.secondary)
    async def next(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.discord_page < self.max_discord_pages - 1:
            self.discord_page += 1
        elif self.has_next_api_page:
            
            await interaction.response.defer()
            await leaderboard.callback(interaction, self.gamemode, self.api_page + 1)
            return

        self.update_buttons()
        await interaction.response.edit_message(embed=self.get_current_embed(), view=self)

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    """Simple ping command"""
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"Bot latency: {latency}ms",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="help", description="Show available commands")
async def help_command(interaction: discord.Interaction):
    """Help command"""
    embed = discord.Embed(
        title="🤖 MCR ELO Bot Help",
        description="Available commands:",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="/elo <ign> [gamemode]",
        value="Get ELO stats for a player. Optional gamemode filter.",
        inline=False
    )

    embed.add_field(
        name="/leaderboard <gamemode> [page]",
        value="View paginated leaderboard for a gamemode.",
        inline=False
    )

    embed.add_field(
        name="/ping",
        value="Check bot latency.",
        inline=False
    )

    embed.set_footer(text="MCR ELO System")
    await interaction.response.send_message(embed=embed)

if __name__ == "__main__":
    if not TOKEN:
        logger.error("❌ DISCORD_TOKEN not found in .env")
        exit(1)

    logger.info("🚀 Starting MCR ELO Bot...")
    bot.run(TOKEN)