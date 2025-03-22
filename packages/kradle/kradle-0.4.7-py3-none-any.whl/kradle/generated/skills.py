# Auto-generated documentation for skills

skills_docs = {
    "activateNearestBlock": {
        "desc": """Activate the nearest block of the given type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("type", "string", """the type of block to activate."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the block was activated, false otherwise.""",
        ),
        "example": """await skills.activateNearestBlock(bot, "lever");""",
    },
    "attackEntity": {
        "desc": """Attack mob of the given type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("entity", "Entity", """the entity to attack."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the entity was attacked, false if interrupted""",
        ),
        "example": """await skills.attackEntity(bot, entity);""",
    },
    "attackNearest": {
        "desc": """Attack mob of the given type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("mobType", "string", """the type of mob to attack."""),
            (
                "kill",
                "boolean",
                """whether or not to continue attacking until the mob is dead. Defaults to true.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the mob was attacked, false if the mob type was not found.""",
        ),
        "example": """await skills.attackNearest(bot, "zombie", true);""",
    },
    "avoidEnemies": {
        "desc": """Move a given distance away from all nearby enemy mobs.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("distance", "number", """the distance to move away."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the bot moved away, false otherwise.""",
        ),
        "example": """await skills.avoidEnemies(bot, 8);""",
    },
    "breakBlockAt": {
        "desc": """Break the block at the given position. Will use the bot's equipped item.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("x", "number", """the x coordinate of the block to break."""),
            ("y", "number", """the y coordinate of the block to break."""),
            ("z", "number", """the z coordinate of the block to break."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the block was broken, false otherwise.""",
        ),
        "example": """let position = world.getPosition(bot);
await skills.breakBlockAt(bot, position.x, position.y - 1, position.x);""",
    },
    "clearNearestFurnace": {
        "desc": """Clears the nearest furnace of all items.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the furnace was cleared, false otherwise.""",
        ),
        "example": """await skills.clearNearestFurnace(bot);""",
    },
    "collectBlock": {
        "desc": """Collect one of the given block type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("blockType", "string", """the type of block to collect."""),
            ("num", "number", """the number of blocks to collect. Defaults to 1."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the block was collected, false if the block type was not found.""",
        ),
        "example": """await skills.collectBlock(bot, "oak_log");""",
    },
    "craftRecipe": {
        "desc": """Attempt to craft the given item name from a recipe. May craft many items.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("itemName", "string", """the item name to craft."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the recipe was crafted, false otherwise.""",
        ),
        "example": """await skills.craftRecipe(bot, "stick");""",
    },
    "defendSelf": {
        "desc": """Defend yourself from all nearby hostile mobs until there are no more.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("range", "number", """the range to look for mobs. Defaults to 8."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the bot found any enemies and has killed them, false if no entities were found.""",
        ),
        "example": """await skills.defendSelf(bot);""",
    },
    "discard": {
        "desc": """Discard the given item.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("itemName", "string", """the item or block name to discard."""),
            (
                "num",
                "number",
                """the number of items to discard. Defaults to -1, which discards all items.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was discarded, false otherwise.""",
        ),
        "example": """await skills.discard(bot, "oak_log");""",
    },
    "eat": {
        "desc": """Eat the given item. If no item is given, it will eat the first food item in the bot's inventory.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("item", "string", """the item to eat."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was eaten, false otherwise.""",
        ),
        "example": """await skills.eat(bot, "apple");""",
    },
    "equip": {
        "desc": """Equip the given item to the proper body part, like tools or armor.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("itemName", "string", """the item or block name to equip."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was equipped, false otherwise.""",
        ),
        "example": """await skills.equip(bot, "iron_pickaxe");""",
    },
    "followPlayer": {
        "desc": """Follow the given player endlessly. Will not return until the code is manually stopped.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("username", "string", """the username of the player to follow."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the player was found, false otherwise.""",
        ),
        "example": """await skills.followPlayer(bot, "player");""",
    },
    "giveToPlayer": {
        "desc": """Give one of the specified item to the specified player""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("itemType", "string", """the name of the item to give."""),
            (
                "username",
                "string",
                """the username of the player to give the item to.""",
            ),
            ("num", "number", """the number of items to give. Defaults to 1."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was given, false otherwise.""",
        ),
        "example": """await skills.giveToPlayer(bot, "oak_log", "player1");""",
    },
    "goToBed": {
        "desc": """Sleep in the nearest bed.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the bed was found, false otherwise.""",
        ),
        "example": """await skills.goToBed(bot);""",
    },
    "goToNearestBlock": {
        "desc": """Navigate to the nearest block of the given type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("blockType", "string", """the type of block to navigate to."""),
            (
                "min_distance",
                "number",
                """the distance to keep from the block. Defaults to 2.""",
            ),
            ("range", "number", """the range to look for the block. Defaults to 64."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the block was reached, false otherwise.""",
        ),
        "example": """await skills.goToNearestBlock(bot, "oak_log", 64, 2);""",
    },
    "goToPlayer": {
        "desc": """Navigate to the given player.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("username", "string", """the username of the player to navigate to."""),
            ("distance", "number", """the goal distance to the player."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the player was found, false otherwise.""",
        ),
        "example": """await skills.goToPlayer(bot, "player");""",
    },
    "goToPosition": {
        "desc": """Navigate to the given position.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            (
                "x",
                "number",
                """the x coordinate to navigate to. If null, the bot's current x coordinate will be used.""",
            ),
            (
                "y",
                "number",
                """the y coordinate to navigate to. If null, the bot's current y coordinate will be used.""",
            ),
            (
                "z",
                "number",
                """the z coordinate to navigate to. If null, the bot's current z coordinate will be used.""",
            ),
            (
                "distance",
                "number",
                """the distance to keep from the position. Defaults to 2.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the position was reached, false otherwise.""",
        ),
        "example": """let position = world.world.getNearestBlock(bot, "oak_log", 64).position;
await skills.goToPosition(bot, position.x, position.y, position.x + 20);""",
    },
    "moveAway": {
        "desc": """Move away from current position in any direction.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("distance", "number", """the distance to move away."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the bot moved away, false otherwise.""",
        ),
        "example": """await skills.moveAway(bot, 8);""",
    },
    "pickupNearbyItems": {
        "desc": """Pick up all nearby items.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the items were picked up, false otherwise.""",
        ),
        "example": """await skills.pickupNearbyItems(bot);""",
    },
    "placeBlock": {
        "desc": """Place the given block type at the given position. It will build off from any adjacent blocks. Will fail if there is a block in the way or nothing to build off of.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("blockType", "string", """the type of block to place."""),
            ("x", "number", """the x coordinate of the block to place."""),
            ("y", "number", """the y coordinate of the block to place."""),
            ("z", "number", """the z coordinate of the block to place."""),
            (
                "placeOn",
                "string",
                """the preferred side of the block to place on. Can be 'top', 'bottom', 'north', 'south', 'east', 'west', or 'side'. Defaults to bottom. Will place on first available side if not possible.""",
            ),
            (
                "dontCheat",
                "boolean",
                """overrides cheat mode to place the block normally. Defaults to false.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the block was placed, false otherwise.""",
        ),
        "example": """let p = world.getPosition(bot);
await skills.placeBlock(bot, "oak_log", p.x + 2, p.y, p.x);
await skills.placeBlock(bot, "torch", p.x + 1, p.y, p.x, \'side\');""",
    },
    "putInChest": {
        "desc": """Put the given item in the nearest chest.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("itemName", "string", """the item or block name to put in the chest."""),
            (
                "num",
                "number",
                """the number of items to put in the chest. Defaults to -1, which puts all items.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was put in the chest, false otherwise.""",
        ),
        "example": """await skills.putInChest(bot, "oak_log");""",
    },
    "smeltItem": {
        "desc": """Puts 1 coal in furnace and smelts the given item name, waits until the furnace runs out of fuel or input items.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            (
                "itemName",
                "string",
                """the item name to smelt. Ores must contain "raw" like raw_iron.""",
            ),
            ("num", "number", """the number of items to smelt. Defaults to 1."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was smelted, false otherwise. Fail""",
        ),
        "example": """await skills.smeltItem(bot, "raw_iron");
await skills.smeltItem(bot, "beef");""",
    },
    "stay": {
        "desc": """Stay in the current position until interrupted. Disables all modes.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            (
                "seconds",
                "number",
                """the number of seconds to stay. Defaults to 30. -1 for indefinite.""",
            ),
        ],
        "returns": ("Promise<boolean>", """true if the bot stayed, false otherwise."""),
        "example": """await skills.stay(bot);""",
    },
    "takeFromChest": {
        "desc": """Take the given item from the nearest chest.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            (
                "itemName",
                "string",
                """the item or block name to take from the chest.""",
            ),
            (
                "num",
                "number",
                """the number of items to take from the chest. Defaults to -1, which takes all items.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the item was taken from the chest, false otherwise.""",
        ),
        "example": """await skills.takeFromChest(bot, "oak_log");""",
    },
    "tillAndSow": {
        "desc": """Till the ground at the given position and plant the given seed type.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            ("x", "number", """the x coordinate to till."""),
            ("y", "number", """the y coordinate to till."""),
            ("z", "number", """the z coordinate to till."""),
            (
                "plantType",
                "string",
                """the type of plant to plant. Defaults to none, which will only till the ground.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the ground was tilled, false otherwise.""",
        ),
        "example": """let position = world.getPosition(bot);
await skills.till(bot, position.x, position.y - 1, position.x);""",
    },
    "useDoor": {
        "desc": """Use the door at the given position.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
            (
                "door_pos",
                "Vec3",
                """the position of the door to use. If null, the nearest door will be used.""",
            ),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the door was used, false otherwise.""",
        ),
        "example": """let door = world.getNearestBlock(bot, "oak_door", 16).position;
await skills.useDoor(bot, door);""",
    },
    "viewChest": {
        "desc": """View the contents of the nearest chest.""",
        "params": [
            ("bot", "MinecraftBot", """reference to the minecraft bot."""),
        ],
        "returns": (
            "Promise<boolean>",
            """true if the chest was viewed, false otherwise.""",
        ),
        "example": """await skills.viewChest(bot);""",
    },
}
