import os
import json
import pandas as pd

################################################################################
# Constant Value sets
################################################################################

# Global constants
COM_PRFX = "~"
MAX_COMM = 15
MAX_TRIM = 100
MAX_MESG = 160
VERSION = "20"

# Time map
timeMap = {
    'millisecond':.001,
    'msec':.001,
    'milliseconds':.001,
    'msecs':.001,
    'second':1,
    'sec':1,
    'seconds':1,
    'secs':1,
    'minute':60,
    'min':60,
    'minutes':60,
    'mins':60,
    'hour':3600,
    'hr':3600,
    'hours':3600,
    'hrs':3600,
    'day':86400,
    'days':86400,
    'week':604800,
    'weeks':604800
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

# Macro Map
macroMap = {}
if not os.path.exists("macro-dictionary.json"):
    with open("macro-dictionary.json", "w") as json_file:
        json.dump(macroMap, json_file)
with open("macro-dictionary.json") as json_file:
    macroMap = json.load(json_file)

# Dataframe
countryMap = {}
countryTmp = pd.read_csv("language-codes.csv").set_index("English").T.to_dict("list")
for k,v in countryTmp.items():
    for country in k.split(';'):
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
    country_code = None
    target = target.lower()

    if target in countryMap:
        country_code = countryMap[target]

    return country_code

# Simple num checker
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False