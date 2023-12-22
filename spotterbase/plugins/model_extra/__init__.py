from spotterbase.plugins.model_extra import declarations
from spotterbase.plugins.model_extra.sbx import SBX, SBX_JSONLD_CONTEXT
from spotterbase.rdf import StandardNameSpaces
from spotterbase.records.jsonld_support import DefaultContexts
from spotterbase.records.record_class_resolver import RecordClassResolver, DefaultRecordClassResolver

SBX_RECORD_CLASS_RESOLVER: RecordClassResolver = RecordClassResolver([
    declarations.Identifier,
    declarations.IdentifierDeclaration,
    declarations.IdentifierOccurrence,
])


def load():
    for record_type in SBX_RECORD_CLASS_RESOLVER.record_class_iter():
        DefaultRecordClassResolver.add(record_type)

    StandardNameSpaces.add_namespace(SBX.NS)
    DefaultContexts.append(SBX_JSONLD_CONTEXT)
