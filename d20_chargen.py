"""
Backend for generating d20 characters.

"""
import argparse
import random

ELITE_ARRAY = [15, 13, 12, 11, 10, 8]
PHYSICAL_STATS = ["str", "dex", "con"]
MENTAL_STATS = ["wis", "int", "cha"]
BASE_STATS = PHYSICAL_STATS + MENTAL_STATS

def handle_args():
    """
    Deal with the arguments using argparse.

    args:
        level: Character level
        --base_attack: base attack progression (good/fair/poor, fighter, etc)
        --good_saves: (takes 1+ argument) what saves are good (will, ref, fort)
        --favor: Stats to favor when rolling (and improving if --improve isn't
                    specified)
        --hitdie: size of hitdie (4, 6, 8, etc., but any integer will work)

    returns an argparse.ArgumentParser object

    """

    base_attack_help = """
    Base Attack Progression:
        Good: Fighter, Fair:Rogue/Cleric
        Poor: (anything else, Wizard progression)
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('level', help="Desired character level.", type=int)
    parser.add_argument('--base_attack', help=base_attack_help, type=str,
                        choices=["good", "fair", "poor", "fighter", "rogue",
                                 "cleric", "wizard"])
    parser.add_argument('--good_saves', help="List of good saves.", nargs="+",
                        choices=["fort", "ref", "will"])
    parser.add_argument('--favor', help="Stats to favor in stat selection.",
                        choices=BASE_STATS, nargs="+")
    parser.add_argument('--improve', choices=BASE_STATS, nargs="+",
                        help="Stats to increase with level. (default: favored)")
    parser.add_argument('--hitdie', type=int,
                        help="Size of hit die (e.g., 4, 6, 8, default: 4)")

    args = parser.parse_args()
    return args

def report(stats, level, attack_progression, good_saves, hitdie):
    """
    Generate the presentation of a generated character's stats.

    stats: dictionary of character's stats (i.e., {'str': 10})
    level: character's level
    attack_progression: good/fair/poor (fighter, rogue, wizard)
    good_saves: What saves are good saves for the character
    hitdie: Character's hitdie

    prints out the generated values, returns nothing

    """
    if hitdie is None:
        hitdie = 4
    if good_saves is None:
        good_saves = []
    print("str dex con wis int cha")
    print("%3s %3s %3s %3s %3s %3s" % (stats['str'],
                                       stats['dex'],
                                       stats['con'],
                                       stats['wis'],
                                       stats['int'],
                                       stats['cha']))
    print("%+3d %+3d %+3d %+3d %+3d %+3d" % (mod(stats['str']),
                                       mod(stats['dex']),
                                       mod(stats['con']),
                                       mod(stats['wis']),
                                       mod(stats['int']),
                                       mod(stats['cha'])))

    print('-' * 25)
    print("Attack:   %+3d" % (attack(level, attack_progression)
                              + mod(stats['str'])))
    print("Touch AC: %+3d" % (10 + mod(stats['dex'])))
    print("HP:      %4d" % generate_hp(stats, level, hitdie))
    print('-' * 25)
    print("Fortitude:%+3d" % (
        save(level, 'good' if 'fort' in good_saves else 'poor')
        + mod(stats['con'])))
    print("Reflex:   %+3d" % (
        save(level, 'good' if 'ref' in good_saves else 'poor')
        + mod(stats['dex'])))
    print("Willpower:%+3d" % (
        save(level, 'good' if 'will' in good_saves else 'poor')
        + mod(stats['wis'])))
    print('-' * 25)
    print("Class skills: %+3d (Cross-class: +0) + stat bonus" % level)

def raise_stats(stats, level, favored_stats):
    """
    Improve stats based on level.

    stats: dictionary of character's stats
    level: character level
    favored_stats: What stats to improve with additional stat points

    modifies the stats dictionary as necessary, returns nothing

    """
    bonus_stats = int(round(level / 4))
    for _ in range(0, bonus_stats):
        stat = choose_stat(favored_stats)
        stats[stat] += 1

def attack(level, attack_progression):
    """
    Calculate base attack bonus

    level: character_level
    attack_progression: good/bad/poor/fighter/rogue/wizard

    returns a number representing the current base attack value

    """
    if attack_progression in ["good", "fighter"]:
        return int(level)
    elif attack_progression in ["fair", "cleric", "rogue"]:
        return int(level*.75)
    else:
        return int(level/2)

def save(level, save_type):
    """
    Calculate a character's saves based off level

    level: character's level
    save_type: "good" or "poor"

    returns a number representing the current base save

    """
    if save_type == "good":
        return int(round(level/2)) + 2
    else:
        return int(round(level/3))

def mod(stat):
    """
    Calculate stat modifier from stat.

    stat: The score to generate the modifer for (e.g., 10) returns 0

    returns a number representing a stat modifier

    """
    return ((int(stat) - 10) / 2)

def choose_stat(favored_stats, unfavored_stats=None, exclude=None):
    """
    Select stats based on preference

    favored_stats: stats to favor during generation
    unfavored_stats: stats to avoid during generation
    exclude: stats to skip altogether (because they've already been generated)

    returns a random stat from the lists specified

    """
    favored = [f for f in favored_stats 
               if not exclude or f not in exclude]
    unfavored = None
    if unfavored_stats:
        unfavored = [u for u in unfavored_stats
                     if not exclude or u not in exclude]
    if not favored and not unfavored:
        return None
    elif not favored:
        favored = unfavored
        unfavored = None
    stat_list = (favored if not unfavored
                 else random.choice([favored, favored,
                                     unfavored]))
    return random.choice(stat_list)

def generate_hp(stats, level, hitdie):
    """
    Calculate hitpoints.

    stats: dictionary of character's stats.
    level: character level (how many levels to roll for)
    hitdie: size of hitdie

    returns a number representing rolled-up hp

    """
    if hitdie == None:
        hitdie = 4

    health = 0
    for _ in range(0, level):
        # add roll + con mod, or 1, whichever is higher
        health += max(1, random.randrange(0, hitdie) + 1 + mod(stats['con']))

    return health

def generate_stats(favored_stats, unfavored_stats, stat_list=None):
    """
    Generate stats.

    At the moment this only uses arrays, using the elite array by default or an
    array specified

    favored_stats: stats to favor during generation
    unfavored_stats: stats to disfavor during generation
    stat_list: array to use (e.g., [15, 13, 12, 11, 10, 8])

    returns a dictionary representing a generated list of stats

    """
    if stat_list == None:
        stat_list = ELITE_ARRAY
    stats = {}
    exclude = []
    for value in stat_list:
        stat = choose_stat(favored_stats, unfavored_stats, exclude)
        stats[stat] = value
        exclude += [stat]

    return stats
