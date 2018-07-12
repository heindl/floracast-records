from . import gbif, idigb, inat, mycp, muob

from .base import BaseOccurrenceGenerator
from typing import List

generators = {
    'gbif': gbif.Generator,
    'idigbio': idigb.Generator,
    'inaturalist': inat.Generator,
    'mushroomobserver': muob.Generator,
    'mycoportal': mycp.Generator,
}

def OccurrenceGenerators(classes=None): # type: (List[str]) -> List[BaseOccurrenceGenerator]
    if classes is None:
        return list(generators.values())

    return [generators[c] for c in classes]
