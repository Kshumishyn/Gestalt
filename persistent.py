import pandas as pd

################################################################################
# Constant Value sets
################################################################################

# Global constants
COM_PRFX = "~"
MAX_COMM = 15
MAX_TRIM = 100
MAX_MESG = 160
VERSION = "18"

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

# Dataframe
countryTmp = pd.read_csv('language-codes.csv').set_index('English').T.to_dict('list')
countryMap = {}
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