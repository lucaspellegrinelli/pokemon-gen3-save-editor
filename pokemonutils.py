import pandas as pd

df_experience = pd.read_csv("data/experience.csv")
df_natures = pd.read_csv("data/natures.csv")
df_pokemon_species = pd.read_csv("data/pokemon_species.csv")
df_pokemon_stats = pd.read_csv("data/pokemon_stats.csv")
df_stats = pd.read_csv("data/stats.csv")


def calculate_hp_stat(base, iv, ev, level):
    return ((2 * base + iv + ev // 4) * level) // 100 + level + 10


def calculate_other_stat(stat, base, iv, ev, level, nature_name):
    nature = get_stat_multiplier(nature_name, stat)
    return int((((2 * base + iv + ev // 4) * level) // 100 + 5) * nature)


def game_nature_id_to_name(nature_id):
    natures = {
        0: "hardy",
        1: "lonely",
        2: "brave",
        3: "adamant",
        4: "naughty",
        5: "bold",
        6: "docile",
        7: "relaxed",
        8: "impish",
        9: "lax",
        10: "timid",
        11: "hasty",
        12: "serious",
        13: "jolly",
        14: "naive",
        15: "modest",
        16: "mild",
        17: "quiet",
        18: "bashful",
        19: "rash",
        20: "calm",
        21: "gentle",
        22: "sassy",
        23: "careful",
        24: "quirky",
    }

    return natures[nature_id]


def get_nature_increase_decrease(nature_name):
    nature = df_natures[df_natures["identifier"] == nature_name]
    incr_stat_id = nature["increased_stat_id"].values[0]
    decr_stat_id = nature["decreased_stat_id"].values[0]

    incr_stat = df_stats[df_stats["id"] == incr_stat_id]["identifier"].values[0]
    decr_stat = df_stats[df_stats["id"] == decr_stat_id]["identifier"].values[0]
    return incr_stat, decr_stat

def get_stat_multiplier(nature_name, stat_name):
    incr_stat, decr_stat = get_nature_increase_decrease(nature_name)
    if stat_name == incr_stat:
        return 1.1
    elif stat_name == decr_stat:
        return 0.9

    return 1.0

def get_pokemon_base_stats(pokemon_id):
    pokemon_stats = df_pokemon_stats[df_pokemon_stats["pokemon_id"] == pokemon_id]

    base_hp = pokemon_stats[pokemon_stats["stat_id"] == 1]["base_stat"].values[0]
    base_atk = pokemon_stats[pokemon_stats["stat_id"] == 2]["base_stat"].values[0]
    base_def = pokemon_stats[pokemon_stats["stat_id"] == 3]["base_stat"].values[0]
    base_spatk = pokemon_stats[pokemon_stats["stat_id"] == 4]["base_stat"].values[0]
    base_spdef = pokemon_stats[pokemon_stats["stat_id"] == 5]["base_stat"].values[0]
    base_speed = pokemon_stats[pokemon_stats["stat_id"] == 6]["base_stat"].values[0]

    return base_hp, base_atk, base_def, base_spatk, base_spdef, base_speed

def get_pokemon_max_xp(pokemon_id, level=100):
    pokemon_species = df_pokemon_species[df_pokemon_species["id"] == pokemon_id]
    growth_rate_id = pokemon_species["growth_rate_id"].values[0]
    experience = df_experience[df_experience["growth_rate_id"] == growth_rate_id]
    max_xp = experience[experience["level"] == level]["experience"].values[0]
    return max_xp
