import secrets
import string

# Extended list of natural elements (120 words)
NATURE_ELEMENTS = [
    # Flora, Trees & Flowers
    "Leaf", "Bloom", "Flora", "Cedar", "Lotus", "Pine", "Fern", "Willow", "Petal", "Birch",
    "Rose", "Orchid", "Maple", "Oak", "Moss", "Ivy", "Clover", "Daisy", "Jasmine", "Bamboo",
    "Cypress", "Spruce", "Redwood", "Alder", "Ash", "Aspen", "Beech", "Elm", "Hazel", "Laurel",
    "Poplar", "Rowan", "Walnut", "Yew", "Tulip", "Lily", "Violet", "Dahlia", "Poppy", "Iris",
    "Azalea", "Zinnia", "Sage", "Mint", "Thyme", "Basil", "Olive", "Aloe", "Peony", "Magnolia",
    
    # Water & Weather
    "River", "Breeze", "Ocean", "Frost", "Rain", "Storm", "Wave", "Mist", "Dew", "Brook",
    "Stream", "Tide", "Creek", "Glacier", "Ice", "Snow", "Hail", "Gale", "Cloud", "Surge",
    "Cove", "Bay", "Reef", "Lake", "Lagoon", "Gulf", "Fjord", "Cascade", "Current", "Geyser",
    
    # Earth, Minerals & Landforms
    "Stone", "Meadow", "Forest", "Desert", "Canyon", "Ridge", "Peak", "Valley", "Hill", "Cliff",
    "Dune", "Cave", "Grove", "Mountain", "Island", "Oasis", "Savanna", "Tundra", "Marsh", "Delta",
    "Pebble", "Boulder", "Quartz", "Amber", "Jade", "Coral", "Flint", "Basalt", "Garnet", "Topaz",
    
    # Sky & Celestial
    "Solar", "Star", "Aurora", "Nova", "Comet", "Eclipse", "Twilight", "Dawn", "Dusk", "Ember",
    "Spark", "Zephyr", "Horizon", "Lunar", "Cosmic", "Nebula", "Solstice", "Equinox", "Zenith", "Meteor"
]


def generate_password(length, use_upper, use_digits, use_symbols, use_nature=True):
    chars = string.ascii_lowercase
    if use_upper:
        chars += string.ascii_uppercase
    if use_digits:
        chars += string.digits
    if use_symbols:
        chars += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not chars and not use_nature:
        return "Select at least one character set or enable nature elements."

    target_len = max(int(length), 8)

    if use_nature:
        # Select an intact nature word
        word = secrets.choice(NATURE_ELEMENTS)
        if not use_upper:
            word = word.lower()

        # Adjust length if target is smaller than the word length
        if target_len < len(word):
            target_len = len(word)

        remaining_len = target_len - len(word)
        extra_chars = chars if chars else string.ascii_lowercase + string.digits

        # Place the INTACT word randomly within the password
        prefix_len = secrets.randbelow(remaining_len + 1)
        suffix_len = remaining_len - prefix_len

        prefix = "".join(secrets.choice(extra_chars) for _ in range(prefix_len))
        suffix = "".join(secrets.choice(extra_chars) for _ in range(suffix_len))

        return f"{prefix}{word}{suffix}"
    else:
        return "".join(secrets.choice(chars) for _ in range(target_len))