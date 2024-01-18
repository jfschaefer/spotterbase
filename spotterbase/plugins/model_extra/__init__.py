from spotterbase.plugins.model_extra import context
from spotterbase.plugins.model_extra.declarations import DECL, DECL_JSONLD_CTX
import spotterbase.plugins.model_extra.declarations as declarations
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

    StandardNameSpaces.add_namespace(DECL.NS)
    DefaultContexts.append(DECL_JSONLD_CTX)
