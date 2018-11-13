from . import gbif, idigb, inat, mycp, muob

from .base import BaseOccurrenceGenerator
from typing import List, Type

generators = {
    'gbif': gbif.Generator,
    'idigbio': idigb.Generator,
    'inaturalist': inat.Generator,
    'mushroomobserver': muob.Generator,
    'mycoportal': mycp.Generator,
}

OccurrenceSourceKeys = list(generators.keys())

def OccurrenceGenerators(classes=None): # type: (List[str]) -> List[Type[BaseOccurrenceGenerator]]
    if classes is None:
        return list(generators.values())

    return [generators[c] for c in classes]
