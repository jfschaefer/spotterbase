import abc

from spotterbase.annotations.conversion_base_classes import JsonExportable, JsonImportable, TripleExportable


class Body(JsonExportable, JsonImportable, TripleExportable, abc.ABC):
    ...
