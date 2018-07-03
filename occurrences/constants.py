# The most recent satellite data starts in 2002. We want at least a year and half worth of weather records,
# in order to account for future predictions. Which means June of 2003 is our earliest occurrence date.
MINIMUM_OCCURRENCE_TIME_SECONDS=1054425600
MINIMUM_OCCURRENCE_TIME_MILLISECONDS=1054425600000

# Worried about the size of the protected area reduction,
# and so think that 14 is the safest, though lower in resolution (600m) than I could have hoped.
STANDARD_S2_CELL_LEVEL = 14

MAX_COORDINATE_UNCERTAINTY_METERS = 64000


NorthAmericanMacroFungiFamilies = [
    'agaricaceae',
    "diplocystidiaceae",
    'geastraceae',
    'sclerodermataceae',
    'morchellaceae',
    'calostomataceae',
    'phelloriniaceae',
    'amanitaceae',
    'suillaceae',
    'paxillaceae',
    'gyroporaceae',
    'boletinellaceae',
    'boletaceae',
    'psathyrellaceae',
    'hygrophoraceae',
    'russulaceae',
    'tricholomataceae',
    'rickenellaceae',
    'mycenaceae',
    'cortinariaceae',
    'inocybaceae',
    'strophariaceae'
]