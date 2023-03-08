from spotterbase.concept_graphs.concept_resolver import ConceptResolver
import spotterbase.special_concepts.declarations as declarations

SBX_CONCEPT_RESOLVER: ConceptResolver = ConceptResolver([
    declarations.Identifier,
    declarations.IdentifierDeclaration,
    declarations.IdentifierOccurrence,
])
