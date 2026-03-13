"""
Offline Fallback Dungeon Engine
================================
Used automatically when GEMINI_API_KEY is missing or invalid.
Provides a fully playable experience with handcrafted room descriptions,
atmospheric combat narration, event text, and item flavour — no AI required.
"""

import random
from typing import Optional


# ---------------------------------------------------------------------------
# ROOM DESCRIPTIONS  (keyed by direction moved)
# ---------------------------------------------------------------------------

ROOM_POOL: dict[str, list[str]] = {
    "north": [
        "You push open a heavy iron door. The corridor beyond is slick with moisture, "
        "torchlight flickering across walls etched with old warnings in a dead language.",
        "The passage narrows as you head north. Bones crunch underfoot — animal or human, "
        "it's hard to say. A cold draft carries the smell of deep earth.",
        "You emerge into a vaulted chamber. Pillars rise into darkness above. "
        "At the centre sits a stone altar, long since stripped of offerings.",
        "A low archway opens into a flooded antechamber. The water is ankle-deep and black. "
        "Something ripples near the far wall and goes still.",
        "The north passage slopes downward steeply. Mold creeps up the walls in vivid purple blooms. "
        "You hear distant, rhythmic dripping — or footsteps.",
        "You enter a guard post long abandoned. Rusted weapons hang on the walls. "
        "A toppled lantern has scorched a black scar across the floor.",
    ],
    "south": [
        "Heading south, the ceiling drops. You duck beneath collapsed stonework "
        "and squeeze into a narrow gallery. Carved faces line the walls, mouths open in silence.",
        "The southern corridor opens into a chapel. Defaced frescoes stare down at you. "
        "Candles — recently lit — flicker on a crumbling altar.",
        "You backtrack into a storeroom. Rotted crates spill their contents: "
        "broken pottery, spoiled rations, a single intact vial glinting in the dark.",
        "The passage south ends in a cave-in. You find a gap just wide enough to squeeze through. "
        "On the other side: a crypt, its stone slabs pushed open from within.",
        "A mosaic floor depicts a battle between men and shadow-creatures. "
        "Several tiles have been deliberately pried up. The shadows seem to win.",
    ],
    "east": [
        "The eastern hall is long and lined with iron cages. "
        "Most are empty. One is not — but whatever is inside doesn't move.",
        "You step into a library. Shelves sag under the weight of mildewed tomes. "
        "Pages flutter in a wind that has no source.",
        "A laboratory stretches before you, tables covered in shattered glassware. "
        "A bubbling flask sits undisturbed among the wreckage, glowing faintly amber.",
        "The east passage leads to a balcony overlooking a vast underground cavern. "
        "Far below, something luminous moves through the dark like a slow tide.",
        "You find an armoury. Most weapons have rusted to uselessness. "
        "But the rack in the corner holds something that still catches the light.",
    ],
    "west": [
        "Going west, you pass through a collapsed throne room. "
        "The throne remains — massive, black stone, carved with serpents devouring each other.",
        "The western path winds through a natural cave. Crystal formations jut from the walls, "
        "humming faintly at a frequency that makes your back teeth ache.",
        "You enter a kitchen. Cauldrons hang cold over dead hearths. "
        "A calendar on the wall is marked three years ago — last entry: 'They came at dawn.'",
        "A scriptorium. Dried ink pots, quills turned to dust. "
        "One desk holds a journal, still legible. The final words: 'Do not go deeper.'",
        "The west corridor terminates at a portcullis — raised, but groaning under its own weight. "
        "You slide beneath it quickly. It holds.",
    ],
}

DEAD_ENDS = [
    "The passage ends abruptly at a collapsed wall. Rubble blocks any further progress. "
    "You'll have to turn back.\nDEAD_END",
    "A door here is sealed with a mechanism you can't decipher. "
    "It doesn't budge. Dead end.\nDEAD_END",
    "The corridor simply stops — finished mid-construction, as if the builders "
    "abandoned the work in a hurry. Nothing but bare stone ahead.\nDEAD_END",
    "An underground lake blocks your path. The water is still and opaque. "
    "You have no way across. Dead end.\nDEAD_END",
]

# ---------------------------------------------------------------------------
# FLOOR DESCRIPTIONS
# ---------------------------------------------------------------------------

FLOORS: dict[int, str] = {
    1: """Floor 1: The Gatehouse of Ash

You stand at the threshold. The entrance tunnel reeks of char and old smoke —
something burned here, long ago, and was never cleaned up. Flakes of ash drift
lazily from the ceiling.

  Notable areas:
  • The Warden's Post — a shattered guardroom, its occupant long gone
  • The Ash Corridor — a long hall dusted grey, with drag marks in the soot
  • The Locked Vestibule — a heavy door with a keyhole shaped like a skull

You stand at the entrance to the dungeon. The air is thick and wrong.
Somewhere ahead, something exhales — slow and patient.
Danger lurks in the darkness. Tread carefully.""",

    2: """Floor 2: The Drowned Cellars

Water seeps through every crack here. The stone glistens. Your boots splash
in shallow puddles that were not here a week ago, judging by the waterline
stains climbing the walls.

  Notable areas:
  • The Flooded Gallery — a corridor half-submerged, things floating beneath the surface
  • The Cistern Room — a vast tank, cracked, slowly draining into something below
  • The Mold Garden — a chamber choked with luminous fungal growths

You stand at the top of a slick staircase. The smell of rot is overwhelming.
Below, the water reflects your torchlight back at you — and something else moves in it.""",

    3: """Floor 3: The Catacombs of Sorrow

The dead are stacked floor to ceiling in alcoves carved from the rock.
Thousands of them. Not all of them are staying still.

  Notable areas:
  • The Bone Gallery — a corridor of skulls arranged with unsettling precision
  • The Mourning Chapel — a small room where candles somehow still burn
  • The Sealed Tomb — a door marked with a warning none of the dead can read anymore

You stand at the catacomb entrance. The silence here is absolute — then broken,
rhythmically, by the sound of something dragging itself across stone.""",

    4: """Floor 4: The Forge of Black Iron

Heat radiates from the walls. The forges here still burn — fed by what, you
cannot tell. The workers who once toiled here left in a hurry; half-made weapons
still sit in the quench tanks.

  Notable areas:
  • The Grand Furnace — a roaring kiln, its fuel unknown, its output unknowable
  • The Weapon Racks — rows of blades too dark to be ordinary steel
  • The Slag Pits — bubbling pools of cooling metal concealing who knows what

You stand before the forge gates, iron hot to the touch.
The hammering you heard from above has stopped. Something noticed you arrive.""",

    5: """Floor 5: The Throne of the Fallen King

You have reached it. The final chamber of the upper keep — a vast, cold hall
where a dead king still sits upon his throne, crown fused to his skull by centuries
of rust and malice. His court stands around him: skeletal courtiers frozen mid-bow,
mid-laugh, mid-scream.

  Notable areas:
  • The Throne Dais — the king sits here. He is watching you.
  • The Court Chamber — a ring of frozen undead courtiers. Some still move.
  • The Vault Door — behind the throne, a door that leads to something older still.

You stand at the edge of the great hall. The king's empty sockets track your movement.
This floor is the most dangerous yet. Nothing here died quietly.""",
}

DEFAULT_FLOOR = """Floor {floor}: The Deep Dark

No cartographer has mapped this level. The dungeon shifts here — corridors that
weren't there before, rooms that change when you aren't looking.

  Notable areas:
  • An area of absolute darkness — your torch dims and dies, then relights
  • A chamber of mirrors, each reflecting a different version of you
  • A passage that slopes downward forever

You stand at the edge of the unknown. The dungeon breathes around you.
Whatever lives this deep has never seen the surface."""


# ---------------------------------------------------------------------------
# COMBAT NARRATION
# ---------------------------------------------------------------------------

COMBAT_HIT_PLAYER: list[str] = [
    "Your blade finds a gap in its defences",
    "You drive forward with a fierce strike",
    "A precise thrust connects cleanly",
    "You feint left and slash hard",
    "With a battle cry, you bring your weapon down",
]

COMBAT_MISS_PLAYER: list[str] = [
    "Your swing goes wide",
    "It sidesteps your clumsy lunge",
    "You overextend and nearly lose your footing",
    "The strike glances off harmlessly",
]

COMBAT_CRIT_PLAYER: list[str] = [
    "You find the perfect opening — a devastating blow!",
    "Time slows. Your strike lands with brutal precision!",
    "A CRITICAL HIT — it reels from the impact!",
]

COMBAT_HIT_ENEMY: list[str] = [
    "It retaliates with surprising speed",
    "A wild swing catches you off-guard",
    "It lunges forward, claws raking your side",
    "The creature's attack is relentless",
]

COMBAT_MISS_ENEMY: list[str] = [
    "It swings wide — you dodge back just in time",
    "Its attack thuds into the wall beside you",
    "You parry the blow at the last second",
]

COMBAT_CRIT_ENEMY: list[str] = [
    "It lands a devastating blow — you stagger!",
    "A CRITICAL HIT — the impact rattles your bones!",
    "It strikes true. You feel the damage deeply.",
]

VICTORY_LINES: list[str] = [
    "It crumples to the ground with a final, rattling breath.",
    "The creature collapses. The dungeon is silent once more.",
    "It falls. Whatever drove it dissolves with it.",
    "With a last spasm, it goes still. You stand over its remains.",
    "It lets out one final screech, then nothing.",
]

DEATH_LINES: list[str] = [
    "The darkness closes in. Your last thought is of the surface.",
    "You fall. The dungeon does not mourn you.",
    "Your vision narrows to a point of cold light, then even that goes out.",
    "The last thing you hear is laughter echoing in the deep.",
]

# ---------------------------------------------------------------------------
# TRAP NARRATION
# ---------------------------------------------------------------------------

TRAP_NARRATIONS: dict[str, str] = {
    "Spike Pit": (
        "The floor gives way beneath your foot with a sickening crack. "
        "Iron spikes bite upward. You wrench yourself free, trailing blood."
    ),
    "Poison Dart": (
        "A faint click — then fire in your neck. You pull the dart out, "
        "but the toxin is already in your blood, burning cold."
    ),
    "Fire Trap": (
        "Flames erupt from hidden vents in the floor. "
        "You throw yourself sideways. Your sleeve catches briefly before you smother it."
    ),
    "Falling Stone": (
        "A grinding rumble above — you dive forward as a stone slab crashes "
        "where you just stood. Dust fills your lungs."
    ),
    "Arcane Rune": (
        "Your boot brushes a symbol carved into the floor. It detonates in silence — "
        "a wave of invisible force that flings you into the wall."
    ),
}

# ---------------------------------------------------------------------------
# TREASURE NARRATION
# ---------------------------------------------------------------------------

TREASURE_NARRATIONS = [
    "Behind a loose stone, a niche — someone's emergency cache, never retrieved.",
    "A skeleton slumped in the corner still clutches a leather satchel.",
    "A locked chest sits incongruously in the middle of the corridor. "
    "The lock is broken. Someone got here first — but left something behind.",
    "A hidden alcove, revealed by a draft against your cheek. Inside: supplies.",
    "You nearly step on it — a bundle wrapped in oilcloth, half-buried in debris.",
]

TREASURE_EMPTY = (
    "You find a cache — but someone got here first. "
    "Your pack is full anyway. You leave it."
)

# ---------------------------------------------------------------------------
# PASSAGE NARRATION
# ---------------------------------------------------------------------------

PASSAGE_NARRATIONS = [
    "You notice a section of wall that doesn't quite match the rest. "
    "Pressing it reveals a hidden passage beyond. Type /n /s /e /w to explore.",
    "A draft from nowhere leads your eye to a narrow gap between two slabs — "
    "a secret path, known only to those who look closely.",
    "Behind a rotted tapestry: a door, unmarked, unlocked, waiting.",
    "A shallow step on the floor is a pressure plate — but instead of a trap, "
    "it slides open a panel revealing a shortcut deeper in.",
]

# ---------------------------------------------------------------------------
# ITEM USE NARRATION
# ---------------------------------------------------------------------------

ITEM_USE_NARRATIONS: dict[str, list[str]] = {
    "potion": [
        "You uncork the vial and drink it fast. Warmth floods your chest. "
        "The pain recedes.\nHP_RESTORED: {effect}",
        "Bitter and thick, but effective. The wounds knit closed.\nHP_RESTORED: {effect}",
        "You force it down. Whatever is in it tastes like iron and old herbs — "
        "but the effect is immediate.\nHP_RESTORED: {effect}",
    ],
    "weapon": [
        "You weigh the {name} in your hand. It's well-balanced. Better than what you had.\nWEAPON_EQUIPPED: {name}",
        "You swap out your old weapon for the {name}. "
        "The grip feels right.\nWEAPON_EQUIPPED: {name}",
        "You equip the {name}. The difference is immediately apparent — "
        "this will do real damage.\nWEAPON_EQUIPPED: {name}",
    ],
    "armor": [
        "You pull the {name} on over your existing gear. "
        "The extra protection is reassuring.\nARMOR_EQUIPPED: {name}",
        "The {name} fits well enough. You feel less exposed.\nARMOR_EQUIPPED: {name}",
    ],
    "misc": [
        "You examine the {name} carefully. Useful — you tuck it away securely.",
        "The {name} might come in handy. You stow it in your pack.",
    ],
    "key": [
        "You hold the {name} up to the light. The teeth are unusual. "
        "There must be a lock somewhere that fits this.",
        "The {name} is old but intact. You pocket it carefully.",
    ],
}

# ---------------------------------------------------------------------------
# AMBUSH INTRO NARRATION
# ---------------------------------------------------------------------------

AMBUSH_NARRATIONS = [
    "A shadow detaches from the wall — not a shadow at all.",
    "You hear the attack before you see it. Barely.",
    "Something drops from the ceiling directly in your path.",
    "From a doorway you hadn't noticed, it lunges.",
    "The torch flickers out for one second. When it returns, you're not alone.",
]

# ---------------------------------------------------------------------------
# LEVEL UP NARRATION
# ---------------------------------------------------------------------------

LEVELUP_LINES = [
    "Something shifts in you — a hardening, a sharpening. You feel stronger.",
    "The dungeon has tested you and found you worthy. For now.",
    "Pain has become a teacher. You are better for it.",
    "You can feel the difference. More capable. More dangerous.",
]


# ---------------------------------------------------------------------------
# PUBLIC API
# ---------------------------------------------------------------------------

class FallbackEngine:
    """
    Fully offline dungeon engine.
    Provides the same interface as GeminiClient.generate()
    so the rest of the server works without any code changes.
    """

    def generate_floor(self, floor: int) -> str:
        if floor in FLOORS:
            return FLOORS[floor]
        return DEFAULT_FLOOR.format(floor=floor)

    def generate_movement(self, direction: str, floor: int) -> str:
        # 15% chance of dead end
        if random.randint(1, 100) <= 15:
            return random.choice(DEAD_ENDS)

        dir_key = direction.lower()
        pool = ROOM_POOL.get(dir_key, ROOM_POOL["north"])
        return random.choice(pool)

    def generate_combat_round(
        self,
        player_name: str,
        enemy_name: str,
        p_dmg: int,
        e_dmg: int,
        p_crit: bool,
        e_crit: bool,
        enemy_hp: int,
        player_hp: int,
        player_max_hp: int,
    ) -> str:
        if p_crit:
            p_line = random.choice(COMBAT_CRIT_PLAYER)
        elif p_dmg > 0:
            p_line = random.choice(COMBAT_HIT_PLAYER)
        else:
            p_line = random.choice(COMBAT_MISS_PLAYER)

        if e_crit:
            e_line = random.choice(COMBAT_CRIT_ENEMY)
        elif e_dmg > 0:
            e_line = random.choice(COMBAT_HIT_ENEMY)
        else:
            e_line = random.choice(COMBAT_MISS_ENEMY)

        return (
            f"  {p_line} — dealing {p_dmg} damage to the {enemy_name}.\n"
            f"  {e_line} — you take {e_dmg} damage.\n"
        )

    def generate_victory(self, enemy_name: str) -> str:
        return f"  {random.choice(VICTORY_LINES)}"

    def generate_death(self, enemy_name: str) -> str:
        return f"  {random.choice(DEATH_LINES)}"

    def generate_trap(self, trap_name: str, damage: int) -> str:
        narration = TRAP_NARRATIONS.get(
            trap_name,
            f"A trap activates! You take {damage} damage.",
        )
        return narration

    def generate_treasure(self, item_name: str, full: bool = False) -> str:
        if full:
            return TREASURE_EMPTY
        base = random.choice(TREASURE_NARRATIONS)
        return f"{base}\n  You find: {item_name}"

    def generate_passage(self) -> str:
        return random.choice(PASSAGE_NARRATIONS)

    def generate_ambush(
        self, enemy_name: str, enemy_hp: int, enemy_atk: int, enemy_def: int
    ) -> str:
        intro = random.choice(AMBUSH_NARRATIONS)
        return (
            f"\n  ⚠  AMBUSH! {intro}\n"
            f"  A {enemy_name} blocks your path!\n"
            f"  Enemy HP: {enemy_hp}  ATK: {enemy_atk}  DEF: {enemy_def}\n"
            f"  Type /fight to attack, /flee to attempt escape, /use <item> to use an item."
        )

    def generate_item_use(self, item_name: str, item_type: str, effect: int) -> str:
        pool = ITEM_USE_NARRATIONS.get(item_type, ITEM_USE_NARRATIONS["misc"])
        template = random.choice(pool)
        return template.format(name=item_name, effect=effect)

    def generate_levelup(self) -> str:
        return random.choice(LEVELUP_LINES)

    def generate(self, prompt: str, history: Optional[list] = None) -> str:
        """
        Drop-in replacement for GeminiClient.generate().
        Parses the prompt type from keywords and routes to the right generator.
        """
        p = prompt.lower()

        if "new dungeon floor" in p or ("floor" in p and "dramatic" in p):
            floor = 1
            for word in prompt.split():
                if word.isdigit():
                    floor = int(word)
                    break
            return self.generate_floor(floor)

        for direction in ("north", "south", "east", "west"):
            if f"moves {direction}" in p or f"move: {direction}" in p or direction in p:
                return self.generate_movement(direction, floor=1)

        if "uses" in p or "item" in p:
            return random.choice(ITEM_USE_NARRATIONS["misc"])

        # Generic fallback for anything else
        return random.choice(
            [
                "The dungeon holds its breath. Nothing stirs — for now.",
                "Silence. Then: a distant sound, like something heavy being dragged.",
                "The torchlight wavers. You are alone. For the moment.",
                "Stone and shadow. The dungeon offers no answers, only darkness.",
                "You listen. The dungeon listens back.",
            ]
        )


fallback = FallbackEngine()