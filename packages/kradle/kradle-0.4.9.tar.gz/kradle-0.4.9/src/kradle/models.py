# kradle/models.py
from dataclasses import dataclass, field
from typing import Dict, List, Optional, TypedDict, Union
from enum import Enum
from datetime import datetime
from pprint import pformat
from dataclasses import asdict
import json


class MinecraftEvent(str, Enum):
    """
    Enumeration of all possible Minecraft bot event types captured from Mineflayer.

    This enum represents the various events that can occur during bot operation:
    - Idle state
    - Command execution
    - Chat and message interactions
    - Health-related events
    - Regular interval updates

    The event types correspond directly to Mineflayer bot events and are used to:
    1. Classify incoming events from the bot
    2. Trigger appropriate event handlers
    3. Update the observation state

    Event Sources:
        - bot.on('chat') -> CHAT
        - bot.on('message') -> MESSAGE
        - bot.on('health') -> HEALTH
        - bot.on('death') -> DEATH
        - Internal timer -> INTERVAL
        - Command system -> COMMAND_EXECUTED
        - Damage events -> DAMAGE
        - No active events for a while -> IDLE

    Technical Details:
        - Inherits from str for JSON serialization
        - Used as a key field in Observation class
        - Maps directly to Mineflayer event system
        - Case-sensitive string values
    """

    IDLE = "idle"
    COMMAND_EXECUTED = "command_executed"
    CHAT = "chat"
    MESSAGE = "message"
    HEALTH = "health"
    DEATH = "death"
    DAMAGE = "damage"
    INTERVAL = "interval"


class TimeOfDay(str, Enum):
    MORNING = "morning"
    AFTERNOON = "afternoon"
    EVENING = "evening"
    NIGHT = "night"


class Weather(str, Enum):
    CLEAR = "clear"
    RAIN = "rain"
    THUNDER = "thunder"


class GameMode(str, Enum):
    SURVIVAL = "survival"
    CREATIVE = "creative"
    ADVENTURE = "adventure"
    SPECTATOR = "spectator"


@dataclass
class ChatMessage:
    sender: str
    chat_msg: str


@dataclass
class ChallengeInfo:
    participant_id: str
    run_id: str
    task: str
    agent_modes: list
    js_functions: list
    available_events: list


@dataclass
class Observation:
    """
    Comprehensive representation of a Minecraft bot's state at a single point in time.
    Captures the complete state from the Mineflayer bot including location, surroundings,
    inventory, and events.

    Identity Attributes:
        name (str): Bot's username in the game
            Example: "Bot123"
        participant_id (str): Unique identifier for this bot instance
            Example: "uuid-1234-5678"
        run_id (str): Unique identifier for this Run
            Example: "1234-5678"
        observation_id (str): Unique identifier for this specific observation
            Example: "obs-1234-5678"
        past_observation_id (Optional[str]): Reference to previous observation
            Example: "obs-1234-5677"

    Event Information:
        event (str): Current event type from EventType enum
            Example: "chat", "death", "idle"
        idle (bool): Whether bot is currently idle
            Example: True if no active tasks
        executing (Optional[str]): Command currently being executed
            Example: "move forward", None if no command
        output (Optional[str]): Output from last executed command
            Example: "Successfully moved to coordinates"

    Location Data:
        position: Dict[str, float]
            Example: {"x": 123.45, "y": 64.0, "z": -789.01, "pitch": 45.0, "yaw": 90.0}

    Player State:
        health (float): Health points normalized to 0-1 range
            Example: 0.85 (17/20 hearts)
        hunger (float): Hunger points normalized to 0-1 range
            Example: 0.9 (18/20 food points)
        xp (float): Experience level
            Example: 30.0
        gamemode (GameMode): Current game mode enum
            Example: GameMode.SURVIVAL
        is_alive (bool): Whether bot is currently alive
            Example: True
        on_ground (bool): Whether bot is on solid ground
            Example: True
        equipped (str): Currently equipped item name
            Example: "diamond_sword"

    Environment State:
        biome (str): Current biome name
            Example: "plains", "desert", "forest"
        weather (Weather): Current weather enum
            Example: Weather.RAIN
        time (int): Minecraft time in ticks (0-24000)
            Example: 13000
        time_of_day (TimeOfDay): Time category enum
            Example: TimeOfDay.MORNING
        day_count (int): Number of in-game days passed
            Example: 42
        rain_state (float): Rain intensity from 0-1
            Example: 0.7
        thunder_state (float): Thunder intensity from 0-1
            Example: 0.0
        light_level (int): Block light level (0-15)
            Example: 14
        dimension (str): Current dimension name
            Example: "overworld", "nether", "end"

    World State:
        players (List[str]): Names of nearby players
            Example: ["Steve", "Alex"]
        blocks (List[str]): Visible block types in bot's range
            Example: ["stone", "dirt", "oak_log", "diamond_ore"]
        entities (List[str]): Nearby entity types
            Example: ["zombie", "sheep", "creeper"]
        craftable (List[str]): Items that can be crafted with current inventory
            Example: ["wooden_pickaxe", "torch", "crafting_table"]
        inventory (Dict[str, int]): Current inventory items and their counts
            Example: {"cobblestone": 64, "iron_ingot": 5}
        chat_messages (List[ChatMessage]): Recent chat messages
            Example: [ChatMessage(role="player", content="Hello")]

    Data Sources:
        - Location: bot.entity.position
        - Health/Hunger: bot.health, bot.food
        - Inventory: bot.inventory.items()
        - Blocks: bot.findBlocks() with range of 64 blocks
        - Entities: bot.nearbyEntities with range of 64 blocks
        - Weather: bot.world.weatherData
        - Time: bot.time.timeOfDay
        - Messages: bot.chat events

    Methods:
        from_event(data: Dict) -> Observation:
            Creates new Observation from raw event data
        get_summary() -> str:
            Returns formatted summary of current state
        to_json() -> str:
            Returns JSON serialized state
        __str__() -> str:
            Returns formatted string representation
    """

    # Identity fields
    name: str = ""
    participant_id: str = ""
    run_id: str = ""
    observation_id: str = ""
    past_observation_id: Optional[str] = None

    # Event info
    event: str = "idle"
    idle: bool = True
    executing: Optional[str] = None
    output: Optional[str] = None

    # Location
    position: Dict[str, float] = field(default_factory=dict)

    # Player state
    health: float = 1.0  # Normalized to 0-1 range
    hunger: float = 1.0  # Normalized to 0-1 range
    xp: float = 0.0
    gamemode: GameMode = GameMode.SURVIVAL
    is_alive: bool = True
    on_ground: bool = True
    equipped: str = ""

    # Environment
    biome: str = "plains"
    weather: Weather = Weather.CLEAR
    time: int = 0  # 0-24000
    time_of_day: TimeOfDay = TimeOfDay.MORNING
    day_count: int = 0
    rain_state: float = 0.0
    thunder_state: float = 0.0
    light_level: int = 15
    dimension: str = "overworld"

    # World state
    players: List[str] = field(default_factory=list)
    blocks: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    craftable: List[str] = field(default_factory=list)
    inventory: Dict[str, int] = field(default_factory=dict)
    chat_messages: List[ChatMessage] = field(default_factory=list)

    @classmethod
    def from_event(cls, data: Dict) -> "Observation":
        """Create state from event data with validation"""
        try:
            # Validate time range
            time = int(data.get("time", 0))
            if not 0 <= time <= 24000:
                time = time % 24000

            # Validate health/hunger are between 0-1
            health = float(data.get("health", 20))
            hunger = float(data.get("hunger", 20))
            health = max(0.0, min(1.0, health))
            hunger = max(0.0, min(1.0, hunger))

            return cls(
                # Identity
                name=str(data.get("name", "")),
                participant_id=str(data.get("participantId", "")),
                run_id=str(data.get("runId", "")),
                observation_id=str(data.get("observationId", "")),
                past_observation_id=data.get("past_observationid"),
                # Event
                event=str(data.get("event", "idle")),
                idle=bool(data.get("idle", True)),
                executing=data.get("executing"),
                output=data.get("output"),
                # Location
                position=data.get("position"),
                # Player State
                health=health,
                hunger=hunger,
                xp=float(data.get("xp", 0)),
                gamemode=GameMode(str(data.get("gamemode", "survival"))),
                is_alive=bool(data.get("is_alive", True)),
                on_ground=bool(data.get("on_ground", True)),
                equipped=str(data.get("equipped", "")),
                # Environment
                biome=str(data.get("biome", "plains")),
                weather=Weather(str(data.get("weather", "clear"))),
                time=time,
                time_of_day=TimeOfDay(str(data.get("timeOfDay", "morning"))),
                day_count=int(data.get("day_count", 0)),
                rain_state=float(data.get("rain_state", 0)),
                thunder_state=float(data.get("thunder_state", 0)),
                light_level=int(data.get("light_level", 15)),
                dimension=str(data.get("dimension", "overworld")),
                # World State
                players=list(data.get("players", [])),
                blocks=list(data.get("blocks", [])),
                entities=list(data.get("entities", [])),
                craftable=list(data.get("craftable", [])),
                inventory=dict(data.get("inventory", {})),
                chat_messages=[
                    ChatMessage(
                        sender=str(msg.get("sender", "unknown")),
                        chat_msg= ("to me: " if msg.get("dm", False) else " to general chat: ")  + str(msg.get("message", "")),
                    )
                    for msg in data.get("chat_messages", [])
                ],
            )
        except Exception as e:
            raise ValueError(f"Failed to parse state data: {str(e)}")

    def get_summary(self) -> str:
        """Returns a formatted summary of the observation state"""
        chat_msg_history = (
            "\n    - No messages"
            if not self.chat_messages
            else "".join(
                f"\n    - {msg.sender}: {msg.chat_msg}" for msg in self.chat_messages
            )
        )

        return f"""Player Status:
            - Health: {self.health*100}%
            - Hunger: {self.hunger*100}%
            - XP Level: {self.xp}
            - Gamemode: {self.gamemode}
            - Is Alive: {self.is_alive}
            - Equipment: {self.equipped}

            Location & Environment:
            - Position: x={self.x}, y={self.y}, z={self.z}
            - Dimension: {self.dimension}
            - Biome: {self.biome}
            - Time: {self.time_of_day}
            - Weather: {self.weather}
            - Light Level: {self.light_level}

            World State:
            - Nearby Blocks: {', '.join(self.blocks) if self.blocks else 'None'}
            - Nearby Entities: {', '.join(self.entities) if self.entities else 'None'}
            - Craftable Items: {', '.join(self.craftable) if self.craftable else 'None'}
            - Inventory: {json.dumps(self.inventory) if self.inventory else 'Empty'}

            Chat Messages:{chat_msg_history}

            Output from previous command: {self.output if self.output else 'None'}"""

    def __str__(self) -> str:
        """Clean, formatted string representation of all fields"""
        return pformat(asdict(self), indent=2, width=80, sort_dicts=False)

    def to_json(self) -> str:
        """Returns a JSON string representation of the observation."""
        return json.dumps(asdict(self), indent=4, default=str)



class InitParticipantResponse(TypedDict):
    """The response from the server when an agent is initialized."""
    listenTo: List[MinecraftEvent]
    # we may add more fields in the future

class ActionType(str, Enum):
    """The type of action to be taken by the agent."""
    CODE = "code"
    CHAT = "chat"

class ActionCode(TypedDict):
    code: str

class ActionChat(TypedDict):
    to: List[str]
    message: str

ActionData = Union[ActionCode, ActionChat]


class Action(TypedDict):
    """An action to be taken by the agent."""
    type: ActionType
    data: ActionData

class OnEventResponse(TypedDict):
    """The response from the server when an event is received."""
    actions: List[Action]
    # we may add more fields in the future

#TODO this should be generated from the ActionType schema
JSON_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "action",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to execute"
                },
                "message": {
                    "type": "string",
                    "description": "The chat message"
                }
            },
            "required": ["code", "message"],
            "additionalProperties": False
        }
    }
}


JSON_RESPONSE_FORMAT_COMPLEX = {
    "type": "array",
    "items": {
        "oneOf": [
            {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["code"]
                    },
                    "code": {
                        "type": "string",
                        "description": "The code to execute"
                    }
                },
                "required": ["type", "code"]
            },
            {
                "type": "object",
                "properties": {
                    "type": {
                        "type": "string",
                        "enum": ["chat"]
                    },
                    "message": {
                        "type": "string",
                        "description": "The chat message"
                    }
                },
                "required": ["type", "message"]
            }
        ]
    }
}
