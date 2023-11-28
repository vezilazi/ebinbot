import logging, os, discord, utils, asyncio

from discord.ext import commands
from datetime import datetime as dt

intents = discord.Intents.default()

intents.message_content = True


class LoggingFormatter(logging.Formatter):
    """
    A custom logging formatter that adds color and styling to log messages.

    Attributes:
        black (str): ANSI escape code for black color.
        red (str): ANSI escape code for red color.
        green (str): ANSI escape code for green color.
        yellow (str): ANSI escape code for yellow color.
        blue (str): ANSI escape code for blue color.
        gray (str): ANSI escape code for gray color.
        reset (str): ANSI escape code to reset color and styling.
        bold (str): ANSI escape code for bold styling.
        COLORS (dict): Mapping of log levels to color codes.

    Methods:
        format(record): Formats the log record with color and styling.

    """

    black = "\033[30m"
    red = "\033[31m"
    green = "\033[32m"
    yellow = "\033[33m"
    blue = "\033[34m"
    gray = "\033[37m"
    reset = "\033[0m"
    bold = "\033[1m"

    COLORS = {
        logging.DEBUG: gray + bold,
        logging.INFO: blue + bold,
        logging.WARNING: yellow + bold,
        logging.ERROR: red,
        logging.CRITICAL: red + bold,
    }

    def format(self, record):
        """
        Formats the log record with color and styling.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.

        """
        log_color = self.COLORS[record.levelno]
        format = "(black){asctime}(reset) (levelcolor){levelname:<8}(reset) (green){name}(reset) {message}"
        format = format.replace("(black)", self.black + self.bold)
        format = format.replace("(reset)", self.reset)
        format = format.replace("(levelcolor)", log_color)
        format = format.replace("(green)", self.green + self.bold)
        formatter = logging.Formatter(format, "%Y-%m-%d %H:%M:%S", style="{")
        return formatter.format(record)
    

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

# Console handler
console = logging.StreamHandler()
console.setFormatter(LoggingFormatter())
# File handler
file = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
file_formatter = logging.Formatter(
    "[{asctime}] [{levelname:<8}] {name}: {message}", "%Y-%m-%d %H:%M:%S", style="{"
)
file.setFormatter(file_formatter)

logger.addHandler(console)
logger.addHandler(file)


class Bot(commands.Bot):
    def __init__(self) -> None:
        self.config = utils.get_config()
        super().__init__(
            command_prefix=commands.when_mentioned_or(self.config["prefix"]),
            case_insensitive=True,
            intents=intents,
        )
        self.default_prefix = self.config["prefix"]
        self.remove_command("help")
        self.checks = utils.checks(self)
        self.logger = logger

    async def load_extensions(self) -> None:
        """
        The code in this function is executed when the bot is started
        """
        await self.load_extension("jishaku")
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                await self.load_extension(f"cogs.{file[:-3]}")

    async def is_owner(self, user: discord.User):
        if user.id in self.config["managers"]:
            return True
        
        return await super().is_owner(user)
    
    async def on_ready(self) -> None:
        print(f"{self.user.name} is online and ready to go at {dt.now()}!")
        self.invite = self.config["invite_link"]
        await self.load_extensions()
        activity = discord.Activity(
            type=discord.ActivityType.watching, name=f"{self.default_prefix}help"
        )
        await self.change_presence(status=discord.Status.dnd, activity=activity)


if __name__ == "__main__":
    bot = Bot()
    bot.run(bot.config["token"])
