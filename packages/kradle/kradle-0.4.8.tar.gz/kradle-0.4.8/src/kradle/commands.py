# kradle/commands.py
from enum import Enum
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import re


@dataclass
class CommandParams:
    """Parameters for Minecraft commands"""

    player_name: Optional[str] = None
    closeness: Optional[float] = None
    follow_dist: Optional[float] = None
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    type: Optional[str] = None
    search_range: Optional[float] = None
    distance: Optional[float] = None
    name: Optional[str] = None
    item_name: Optional[str] = None
    num: Optional[int] = None
    recipe_name: Optional[str] = None
    seconds: Optional[int] = None
    message: Optional[str] = None
    mode_name: Optional[str] = None
    on: Optional[bool] = None


class MinecraftCommands(Enum):
    """All available Minecraft commands from actionsList"""

    # Movement and Navigation
    STOP = "!stop"
    GOTOPLAYER = '!goToPlayer("{player_name}", {closeness})'
    FOLLOWPLAYER = '!followPlayer("{player_name}", {follow_dist})'
    GOTOCOORDINATES = "!goToCoordinates({x}, {y}, {z}, {closeness})"
    SEARCHFORBLOCK = '!searchForBlock("{type}", {search_range})'
    SEARCHFORENTITY = '!searchForEntity("{type}", {search_range})'
    MOVEAWAY = "!moveAway({distance})"

    # Location Memory
    REMEMBERHERE = '!rememberHere("{name}")'
    GOTOREMEMBEREDPLACE = '!goToRememberedPlace("{name}")'

    # Inventory Management
    GIVEPLAYER = '!givePlayer("{player_name}", "{item_name}", {num})'
    CONSUME = '!consume("{item_name}")'
    EQUIP = '!equip("{item_name}")'
    PUTINCHEST = '!putInChest("{item_name}", {num})'
    TAKEFROMCHEST = '!takeFromChest("{item_name}", {num})'
    VIEWCHEST = "!viewChest"
    DISCARD = '!discard("{item_name}", {num})'

    # Resource Collection and Crafting
    COLLECTBLOCKS = '!collectBlocks("{type}", {num})'
    CRAFTRECIPE = '!craftRecipe("{recipe_name}", {num})'
    SMELTITEM = '!smeltItem("{item_name}", {num})'
    CLEARFURNACE = "!clearFurnace"

    # Block Placement and Interaction
    PLACEHERE = '!placeHere("{type}")'
    ACTIVATE = '!activate("{type}")'

    # Combat
    ATTACK = '!attack("{type}")'
    ATTACKPLAYER = '!attackPlayer("{player_name}")'

    # Basic Actions
    GOTOBED = "!goToBed"
    STAY = "!stay({seconds})"

    # Communication
    CHAT = '!chat("{message}")'
    WHISPER = '!whisper("{player_name}", "{message}")'

    # Game Modes and Settings
    SETMODE = '!setMode("{mode_name}", {on})'

    def get_param_names(self) -> List[str]:
        """Extract parameter names from the command string"""
        if not self.value.endswith(")"):
            return []

        # Find all {param_name} patterns in the string
        matches = re.findall(r"{([^}]*)}", self.value)
        return matches

    def __call__(self, *args, **kwargs) -> str:
        """
        Execute the command with given parameters.
        Supports both positional and keyword arguments.

        Examples:
            # Positional args:
            CONSUME("apple")
            GIVEPLAYER("Steve", "diamond", 1)

            # Keyword args:
            CONSUME(item_name="apple")
            GIVEPLAYER(player_name="Steve", item_name="diamond", num=1)
        """
        if not self.value.endswith(")"):  # Commands with no parameters
            return self.value

        param_names = self.get_param_names()

        # Convert positional args to keyword args if provided
        if args:
            if len(args) != len(param_names):
                raise ValueError(
                    f"Command {self.name} expects {len(param_names)} arguments "
                    f"({', '.join(param_names)}), but got {len(args)}"
                )
            # Merge positional args with any provided keyword args
            kwargs.update(zip(param_names, args))

        params = CommandParams(**kwargs)
        return self.value.format_map(vars(params))
