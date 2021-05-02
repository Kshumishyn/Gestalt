import os
import json
import pandas as pd
import random
import discord
from discord.ext import commands, tasks


################################################################################
# Constant Value sets
################################################################################

# Global constants
COM_PRFX = "~"
MAX_PRVW = 18
MAX_MESG = 160
NOM_TOUT = 1800
VERSION = "23"

# Filenames
ERR_FILE = "error.log"
DAC_FILE = "discordAuth.code"
GAJ_FILE = "googleAuthcode.json"
MDJ_FILE = "macro-dictionary.json"
LCC_FILE = "language-codes.csv"

# Time map
timeMap = {
    "millisecond":.001,
    "msec":.001,
    "milliseconds":.001,
    "msecs":.001,
    "second":1,
    "sec":1,
    "seconds":1,
    "secs":1,
    "minute":60,
    "min":60,
    "minutes":60,
    "mins":60,
    "hour":3600,
    "hr":3600,
    "hours":3600,
    "hrs":3600,
    "day":86400,
    "days":86400,
    "week":604800,
    "weeks":604800
}

# Regional Emotes
regional_indicators = {   
    'a': '\N{REGIONAL INDICATOR SYMBOL LETTER A}', 'b': '\N{REGIONAL INDICATOR SYMBOL LETTER B}',
    'c': '\N{REGIONAL INDICATOR SYMBOL LETTER C}', 'd': '\N{REGIONAL INDICATOR SYMBOL LETTER D}',
    'e': '\N{REGIONAL INDICATOR SYMBOL LETTER E}', 'f': '\N{REGIONAL INDICATOR SYMBOL LETTER F}',
    'g': '\N{REGIONAL INDICATOR SYMBOL LETTER G}', 'h': '\N{REGIONAL INDICATOR SYMBOL LETTER H}',
    'i': '\N{REGIONAL INDICATOR SYMBOL LETTER I}', 'j': '\N{REGIONAL INDICATOR SYMBOL LETTER J}',
    'k': '\N{REGIONAL INDICATOR SYMBOL LETTER K}', 'l': '\N{REGIONAL INDICATOR SYMBOL LETTER L}',
    'm': '\N{REGIONAL INDICATOR SYMBOL LETTER M}', 'n': '\N{REGIONAL INDICATOR SYMBOL LETTER N}',
    'o': '\N{REGIONAL INDICATOR SYMBOL LETTER O}', 'p': '\N{REGIONAL INDICATOR SYMBOL LETTER P}',
    'q': '\N{REGIONAL INDICATOR SYMBOL LETTER Q}', 'r': '\N{REGIONAL INDICATOR SYMBOL LETTER R}',
    's': '\N{REGIONAL INDICATOR SYMBOL LETTER S}', 't': '\N{REGIONAL INDICATOR SYMBOL LETTER T}',
    'u': '\N{REGIONAL INDICATOR SYMBOL LETTER U}', 'v': '\N{REGIONAL INDICATOR SYMBOL LETTER V}',
    'w': '\N{REGIONAL INDICATOR SYMBOL LETTER W}', 'x': '\N{REGIONAL INDICATOR SYMBOL LETTER X}',
    'y': '\N{REGIONAL INDICATOR SYMBOL LETTER Y}', 'z': '\N{REGIONAL INDICATOR SYMBOL LETTER Z}'
}

# Time map
presenceList = [
    "the beginning.",
    "the gales.",
    "the waves.",
    "the howling.",
    "the silence.",
    "the flames.",
    "the kind.",
    "the unworthy.",
    "the sirens.",
    "the trees.",
    "the songs.",
    "the sand.",
    "the leaves.",
    "the rustling.",
    "the whispers.",
    "the buzz.",
    "the knocking.",
    "the abyss.",
    "the end."
]

# Nomination instance - Format: {(guildID, instance_name): {userID : nomination}}
nominationMap = {}

# Macro Map
macroMap = {}
if not os.path.exists(MDJ_FILE):
    with open(MDJ_FILE, "w") as json_file:
        json.dump(macroMap, json_file)
with open(MDJ_FILE) as json_file:
    macroMap = json.load(json_file)

# Dataframe
countryMap = {}
countryTmp = pd.read_csv(LCC_FILE).set_index("English").T.to_dict("list")
for k,v in countryTmp.items():
    for country in k.split(";"):
        countryMap[country.strip().lower()] = "".join(v)


################################################################################
# Function definitions
################################################################################

# Google's default translation function
def translate_text(target, text):
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    import six
    from google.cloud import translate_v2 as translate

    translate_client = translate.Client()

    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    return result["translatedText"]


# ISO-639-1 Language lookup function
def language_lookup(target):
    """Translates language name into 639-1 language code.
    """

    # Standardizes and defaults to None
    country_code = None
    target = target.lower()

    # Does lookup
    if target in countryMap:
        country_code = countryMap[target]

    return country_code


# Simple num checker
def isnumber(s):
    try:
        float(s)
        return True
    except ValueError:
        return False
