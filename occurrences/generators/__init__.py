from . import gbif, idigb, inat, mycp, muob

generators = {
    'gbif': gbif._Generator,
    'idigbio': idigb._Generator,
    'inaturalist': inat._Generator,
    'mushroomobserver': muob._Generator,
    'mycoportal': mycp._Generator,
}

def OccurrenceGenerators(classes=None):
    if classes is None:
        return generators.values()

    return [generators[c] for c in classes]
