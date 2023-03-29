from spotterbase.records.record_class_resolver import RecordClassResolver
import spotterbase.sbx.declarations as declarations

SBX_RECORD_CLASS_RESOLVER: RecordClassResolver = RecordClassResolver([
    declarations.Identifier,
    declarations.IdentifierDeclaration,
    declarations.IdentifierOccurrence,
])
