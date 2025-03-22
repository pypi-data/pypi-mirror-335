# Auto-generated documentation for world

world_docs = {
    "getBiomeName": {
        "desc": """Get the name of the biome the bot is in.""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": ("string", """- The name of the biome."""),
        "example": """let biome = world.getBiomeName(bot);""",
    },
    "getCraftableItems": {
        "desc": """Get a list of all items that can be crafted with the bot's current inventory.""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": ("string[]", """- A list of all items that can be crafted."""),
        "example": """let craftableItems = world.getCraftableItems(bot);""",
    },
    "getInventoryCounts": {
        "desc": """Get an object representing the bot's inventory.""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": (
            "object",
            """- An object with item names as keys and counts as values.""",
        ),
        "example": """let inventory = world.getInventoryCounts(bot);
let oakLogCount = inventory[\'oak_log\'];
let hasWoodenPickaxe = inventory[\'wooden_pickaxe\'] > 0;""",
    },
    "getNearbyBlockTypes": {
        "desc": """Get a list of all nearby block names.""",
        "params": [
            ("bot", "Bot", """"""),
            ("distance", "number", """"""),
        ],
        "returns": ("string[]", """- A list of all nearby blocks."""),
        "example": """let blocks = world.getNearbyBlockTypes(bot);""",
    },
    "getNearbyEntityTypes": {
        "desc": """Get a list of all nearby mob types.""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": ("string[]", """- A list of all nearby mobs."""),
        "example": """let mobs = world.getNearbyEntityTypes(bot);""",
    },
    "getNearbyPlayerNames": {
        "desc": """Get a list of all nearby player names.""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": ("string[]", """- A list of all nearby players."""),
        "example": """let players = world.getNearbyPlayerNames(bot);""",
    },
    "getNearestBlock": {
        "desc": """Get the nearest block of the given type.""",
        "params": [
            ("bot", "Bot", """"""),
            ("block_type", "string", """"""),
            ("distance", "number", """"""),
        ],
        "returns": ("Block", """- The nearest block of the given type."""),
        "example": """let coalBlock = world.getNearestBlock(bot, \'coal_ore\', 16);""",
    },
    "getNearestBlocks": {
        "desc": """Get a list of the nearest blocks of the given types.""",
        "params": [
            ("bot", "Bot", """"""),
            ("block_types", "string[]", """"""),
            ("distance", "number", """"""),
            ("count", "number", """"""),
        ],
        "returns": ("Block[]", """- The nearest blocks of the given type."""),
        "example": """let woodBlocks = world.getNearestBlocks(bot, [\'oak_log\', \'birch_log\'], 16, 1);""",
    },
    "getNearestFreeSpace": {
        "desc": """Get the nearest empty space with solid blocks beneath it of the given size.""",
        "params": [
            ("bot", "Bot", """"""),
            ("size", "number", """"""),
            ("distance", "number", """"""),
        ],
        "returns": (
            "Vec3",
            """- The south west corner position of the nearest free space.""",
        ),
        "example": """let position = world.getNearestFreeSpace(bot, 1, 8);""",
    },
    "getPosition": {
        "desc": """Get your position in the world (Note that y is vertical).""",
        "params": [
            ("bot", "Bot", """"""),
        ],
        "returns": (
            "Vec3",
            """- An object with x, y, and x attributes representing the position of the bot.""",
        ),
        "example": """let position = world.getPosition(bot);
let x = position.x;""",
    },
    "isClearPath": {
        "desc": """Check if there is a path to the target that requires no digging or placing blocks.""",
        "params": [
            ("bot", "Bot", """"""),
            ("target", "Entity", """"""),
        ],
        "returns": ("boolean", """- True if there is a clear path, false otherwise."""),
        "example": None,
    },
}
