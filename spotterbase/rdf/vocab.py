""" Commonly used RDF vocabularies (automatically generated) """

from spotterbase.rdf.uri import NameSpace, Vocabulary, Uri


class AS(Vocabulary):
    """ Generated from https://raw.githubusercontent.com/w3c/activitystreams/master/vocabulary/activitystreams2.owl """

    NS = NameSpace(Uri('http://www.w3.org/ns/activitystreams#'), prefix='as:')

    # PROPERTIES
    accuracy: Uri
    actor: Uri
    altitude: Uri
    anyOf: Uri
    attachment: Uri
    attachments: Uri
    attributedTo: Uri
    audience: Uri
    author: Uri
    bcc: Uri
    bto: Uri
    cc: Uri
    content: Uri
    context: Uri
    current: Uri
    deleted: Uri
    describes: Uri
    downstreamDuplicates: Uri
    duration: Uri
    endTime: Uri
    first: Uri
    formerType: Uri
    generator: Uri
    height: Uri
    href: Uri
    hreflang: Uri
    icon: Uri
    id: Uri
    image: Uri
    inReplyTo: Uri
    instrument: Uri
    items: Uri
    last: Uri
    latitude: Uri
    location: Uri
    longitude: Uri
    mediaType: Uri
    name: Uri
    next: Uri
    object: Uri
    objectType: Uri
    oneOf: Uri
    origin: Uri
    partOf: Uri
    prev: Uri
    preview: Uri
    provider: Uri
    published: Uri
    radius: Uri
    rating: Uri
    rel: Uri
    relationship: Uri
    replies: Uri
    result: Uri
    startIndex: Uri
    startTime: Uri
    subject: Uri
    summary: Uri
    tag: Uri
    tags: Uri
    target: Uri
    to: Uri
    totalItems: Uri
    units: Uri
    updated: Uri
    upstreamDuplicates: Uri
    url: Uri
    verb: Uri
    width: Uri

    # CLASSES
    Accept: Uri
    Activity: Uri
    Add: Uri
    Announce: Uri
    Application: Uri
    Arrive: Uri
    Article: Uri
    Audio: Uri
    Block: Uri
    Collection: Uri
    CollectionPage: Uri
    Create: Uri
    Delete: Uri
    Dislike: Uri
    Document: Uri
    Event: Uri
    Flag: Uri
    Follow: Uri
    Group: Uri
    Ignore: Uri
    Image: Uri
    IntransitiveActivity: Uri
    Invite: Uri
    Join: Uri
    Leave: Uri
    Like: Uri
    Link: Uri
    Listen: Uri
    Mention: Uri
    Move: Uri
    Note: Uri
    Object: Uri
    Offer: Uri
    OrderedCollection: Uri
    OrderedCollectionPage: Uri
    OrderedItems: Uri
    Organization: Uri
    Page: Uri
    Person: Uri
    Place: Uri
    Profile: Uri
    Question: Uri
    Read: Uri
    Reject: Uri
    Relationship: Uri
    Remove: Uri
    Service: Uri
    TentativeAccept: Uri
    TentativeReject: Uri
    Tombstone: Uri
    Travel: Uri
    Undo: Uri
    Update: Uri
    Video: Uri
    View: Uri


class DC(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_elements.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/elements/1.1/'), prefix='dc:')

    # PROPERTIES
    contributor: Uri
    coverage: Uri
    creator: Uri
    date: Uri
    description: Uri
    format: Uri
    identifier: Uri
    language: Uri
    publisher: Uri
    relation: Uri
    rights: Uri
    source: Uri
    subject: Uri
    title: Uri
    type: Uri


class DCTerms(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.nt """

    NS = NameSpace(Uri('http://purl.org/dc/terms/'), prefix='dcterms:')

    # PROPERTIES
    abstract: Uri
    accessRights: Uri
    accrualMethod: Uri
    accrualPeriodicity: Uri
    accrualPolicy: Uri
    alternative: Uri
    audience: Uri
    available: Uri
    bibliographicCitation: Uri
    conformsTo: Uri
    contributor: Uri
    coverage: Uri
    created: Uri
    creator: Uri
    date: Uri
    dateAccepted: Uri
    dateCopyrighted: Uri
    dateSubmitted: Uri
    description: Uri
    educationLevel: Uri
    extent: Uri
    format: Uri
    hasFormat: Uri
    hasPart: Uri
    hasVersion: Uri
    identifier: Uri
    instructionalMethod: Uri
    isFormatOf: Uri
    isPartOf: Uri
    isReferencedBy: Uri
    isReplacedBy: Uri
    isRequiredBy: Uri
    isVersionOf: Uri
    issued: Uri
    language: Uri
    license: Uri
    mediator: Uri
    medium: Uri
    modified: Uri
    provenance: Uri
    publisher: Uri
    references: Uri
    relation: Uri
    replaces: Uri
    requires: Uri
    rights: Uri
    rightsHolder: Uri
    source: Uri
    spatial: Uri
    subject: Uri
    tableOfContents: Uri
    temporal: Uri
    title: Uri
    type: Uri
    valid: Uri

    # CLASSES
    Agent: Uri
    AgentClass: Uri
    BibliographicResource: Uri
    FileFormat: Uri
    Frequency: Uri
    Jurisdiction: Uri
    LicenseDocument: Uri
    LinguisticSystem: Uri
    Location: Uri
    LocationPeriodOrJurisdiction: Uri
    MediaType: Uri
    MediaTypeOrExtent: Uri
    MethodOfAccrual: Uri
    MethodOfInstruction: Uri
    PeriodOfTime: Uri
    PhysicalMedium: Uri
    PhysicalResource: Uri
    Policy: Uri
    ProvenanceStatement: Uri
    RightsStatement: Uri
    SizeOrDuration: Uri
    Standard: Uri

    # OTHER
    Box: Uri
    DCMIType: Uri
    DDC: Uri
    IMT: Uri
    ISO3166: Uri
    LCC: Uri
    LCSH: Uri
    MESH: Uri
    NLM: Uri
    Period: Uri
    Point: Uri
    RFC1766: Uri
    RFC3066: Uri
    RFC4646: Uri
    RFC5646: Uri
    TGN: Uri
    UDC: Uri
    URI: Uri
    W3CDTF: Uri


class DCTypes(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_type.nt """

    NS = NameSpace(Uri('http://purl.org/dc/dcmitype/'), prefix='dctypes:')


    # CLASSES
    Collection: Uri
    Dataset: Uri
    Event: Uri
    Image: Uri
    InteractiveResource: Uri
    MovingImage: Uri
    PhysicalObject: Uri
    Service: Uri
    Software: Uri
    Sound: Uri
    StillImage: Uri
    Text: Uri


class DCAM(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_abstract_model.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/dcam/'), prefix='dcam:')

    # PROPERTIES
    domainIncludes: Uri
    memberOf: Uri
    rangeIncludes: Uri

    # CLASSES
    VocabularyEncodingScheme: Uri


class DCTERMS(Vocabulary):
    """ Generated from http://dublincore.org/2020/01/20/dublin_core_terms.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/terms/'), prefix='dcterms:')

    # PROPERTIES
    abstract: Uri
    accessRights: Uri
    accrualMethod: Uri
    accrualPeriodicity: Uri
    accrualPolicy: Uri
    alternative: Uri
    audience: Uri
    available: Uri
    bibliographicCitation: Uri
    conformsTo: Uri
    contributor: Uri
    coverage: Uri
    created: Uri
    creator: Uri
    date: Uri
    dateAccepted: Uri
    dateCopyrighted: Uri
    dateSubmitted: Uri
    description: Uri
    educationLevel: Uri
    extent: Uri
    format: Uri
    hasFormat: Uri
    hasPart: Uri
    hasVersion: Uri
    identifier: Uri
    instructionalMethod: Uri
    isFormatOf: Uri
    isPartOf: Uri
    isReferencedBy: Uri
    isReplacedBy: Uri
    isRequiredBy: Uri
    isVersionOf: Uri
    issued: Uri
    language: Uri
    license: Uri
    mediator: Uri
    medium: Uri
    modified: Uri
    provenance: Uri
    publisher: Uri
    references: Uri
    relation: Uri
    replaces: Uri
    requires: Uri
    rights: Uri
    rightsHolder: Uri
    source: Uri
    spatial: Uri
    subject: Uri
    tableOfContents: Uri
    temporal: Uri
    title: Uri
    type: Uri
    valid: Uri

    # CLASSES
    Agent: Uri
    AgentClass: Uri
    BibliographicResource: Uri
    FileFormat: Uri
    Frequency: Uri
    Jurisdiction: Uri
    LicenseDocument: Uri
    LinguisticSystem: Uri
    Location: Uri
    LocationPeriodOrJurisdiction: Uri
    MediaType: Uri
    MediaTypeOrExtent: Uri
    MethodOfAccrual: Uri
    MethodOfInstruction: Uri
    PeriodOfTime: Uri
    PhysicalMedium: Uri
    PhysicalResource: Uri
    Policy: Uri
    ProvenanceStatement: Uri
    RightsStatement: Uri
    SizeOrDuration: Uri
    Standard: Uri

    # OTHER
    Box: Uri
    DCMIType: Uri
    DDC: Uri
    IMT: Uri
    ISO3166: Uri
    LCC: Uri
    LCSH: Uri
    MESH: Uri
    NLM: Uri
    Period: Uri
    Point: Uri
    RFC1766: Uri
    RFC3066: Uri
    RFC4646: Uri
    RFC5646: Uri
    TGN: Uri
    UDC: Uri
    URI: Uri
    W3CDTF: Uri


class DCTYPES(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_type.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/dcmitype/'), prefix='dctypes:')


    # CLASSES
    Collection: Uri
    Dataset: Uri
    Event: Uri
    Image: Uri
    InteractiveResource: Uri
    MovingImage: Uri
    PhysicalObject: Uri
    Service: Uri
    Software: Uri
    Sound: Uri
    StillImage: Uri
    Text: Uri


class FOAF(Vocabulary):
    """ Generated from http://xmlns.com/foaf/0.1/index.rdf """

    NS = NameSpace(Uri('http://xmlns.com/foaf/0.1/'), prefix='foaf:')

    # PROPERTIES
    accountName: Uri
    accountServiceHomepage: Uri
    aimChatID: Uri
    based_near: Uri
    currentProject: Uri
    depiction: Uri
    depicts: Uri
    dnaChecksum: Uri
    family_name: Uri
    firstName: Uri
    fundedBy: Uri
    geekcode: Uri
    gender: Uri
    givenname: Uri
    holdsAccount: Uri
    homepage: Uri
    icqChatID: Uri
    img: Uri
    interest: Uri
    jabberID: Uri
    knows: Uri
    logo: Uri
    made: Uri
    maker: Uri
    mbox: Uri
    mbox_sha1sum: Uri
    member: Uri
    membershipClass: Uri
    msnChatID: Uri
    myersBriggs: Uri
    name: Uri
    nick: Uri
    page: Uri
    pastProject: Uri
    phone: Uri
    plan: Uri
    primaryTopic: Uri
    publications: Uri
    schoolHomepage: Uri
    sha1: Uri
    surname: Uri
    theme: Uri
    thumbnail: Uri
    tipjar: Uri
    title: Uri
    topic: Uri
    topic_interest: Uri
    weblog: Uri
    workInfoHomepage: Uri
    workplaceHomepage: Uri
    yahooChatID: Uri

    # CLASSES
    Agent: Uri
    Document: Uri
    Group: Uri
    Image: Uri
    OnlineAccount: Uri
    OnlineChatAccount: Uri
    OnlineEcommerceAccount: Uri
    OnlineGamingAccount: Uri
    Organization: Uri
    Person: Uri
    PersonalProfileDocument: Uri
    Project: Uri


class RDF(Vocabulary):
    """ Generated from http://www.w3.org/1999/02/22-rdf-syntax-ns# """

    NS = NameSpace(Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), prefix='rdf:')

    # PROPERTIES
    direction: Uri
    first: Uri
    language: Uri
    object: Uri
    predicate: Uri
    rest: Uri
    subject: Uri
    type: Uri
    value: Uri

    # CLASSES
    Alt: Uri
    Bag: Uri
    CompoundLiteral: Uri
    List: Uri
    Property: Uri
    Seq: Uri
    Statement: Uri

    # OTHER
    HTML: Uri
    JSON: Uri
    PlainLiteral: Uri
    XMLLiteral: Uri
    langString: Uri
    nil: Uri


class RDFS(Vocabulary):
    """ Generated from http://www.w3.org/2000/01/rdf-schema# """

    NS = NameSpace(Uri('http://www.w3.org/2000/01/rdf-schema#'), prefix='rdfs:')

    # PROPERTIES
    comment: Uri
    domain: Uri
    isDefinedBy: Uri
    label: Uri
    member: Uri
    range: Uri
    seeAlso: Uri
    subClassOf: Uri
    subPropertyOf: Uri

    # CLASSES
    Class: Uri
    Container: Uri
    ContainerMembershipProperty: Uri
    Datatype: Uri
    Literal: Uri
    Resource: Uri


class OWL(Vocabulary):
    """ Generated from http://www.w3.org/2002/07/owl# """

    NS = NameSpace(Uri('http://www.w3.org/2002/07/owl#'), prefix='owl:')

    # PROPERTIES
    allValuesFrom: Uri
    annotatedProperty: Uri
    annotatedSource: Uri
    annotatedTarget: Uri
    assertionProperty: Uri
    backwardCompatibleWith: Uri
    bottomDataProperty: Uri
    bottomObjectProperty: Uri
    cardinality: Uri
    complementOf: Uri
    datatypeComplementOf: Uri
    deprecated: Uri
    differentFrom: Uri
    disjointUnionOf: Uri
    disjointWith: Uri
    distinctMembers: Uri
    equivalentClass: Uri
    equivalentProperty: Uri
    hasKey: Uri
    hasSelf: Uri
    hasValue: Uri
    imports: Uri
    incompatibleWith: Uri
    intersectionOf: Uri
    inverseOf: Uri
    maxCardinality: Uri
    maxQualifiedCardinality: Uri
    members: Uri
    minCardinality: Uri
    minQualifiedCardinality: Uri
    onClass: Uri
    onDataRange: Uri
    onDatatype: Uri
    onProperties: Uri
    onProperty: Uri
    oneOf: Uri
    priorVersion: Uri
    propertyChainAxiom: Uri
    propertyDisjointWith: Uri
    qualifiedCardinality: Uri
    sameAs: Uri
    someValuesFrom: Uri
    sourceIndividual: Uri
    targetIndividual: Uri
    targetValue: Uri
    topDataProperty: Uri
    topObjectProperty: Uri
    unionOf: Uri
    versionIRI: Uri
    versionInfo: Uri
    withRestrictions: Uri

    # CLASSES
    AllDifferent: Uri
    AllDisjointClasses: Uri
    AllDisjointProperties: Uri
    Annotation: Uri
    AnnotationProperty: Uri
    AsymmetricProperty: Uri
    Axiom: Uri
    Class: Uri
    DataRange: Uri
    DatatypeProperty: Uri
    DeprecatedClass: Uri
    DeprecatedProperty: Uri
    FunctionalProperty: Uri
    InverseFunctionalProperty: Uri
    IrreflexiveProperty: Uri
    NamedIndividual: Uri
    NegativePropertyAssertion: Uri
    Nothing: Uri
    ObjectProperty: Uri
    Ontology: Uri
    OntologyProperty: Uri
    ReflexiveProperty: Uri
    Restriction: Uri
    SymmetricProperty: Uri
    Thing: Uri
    TransitiveProperty: Uri


class SKOS(Vocabulary):
    """ Generated from https://www.w3.org/2009/08/skos-reference/skos.rdf """

    NS = NameSpace(Uri('http://www.w3.org/2004/02/skos/core#'), prefix='skos:')

    # PROPERTIES
    altLabel: Uri
    broadMatch: Uri
    broader: Uri
    broaderTransitive: Uri
    changeNote: Uri
    closeMatch: Uri
    definition: Uri
    editorialNote: Uri
    exactMatch: Uri
    example: Uri
    hasTopConcept: Uri
    hiddenLabel: Uri
    historyNote: Uri
    inScheme: Uri
    mappingRelation: Uri
    member: Uri
    memberList: Uri
    narrowMatch: Uri
    narrower: Uri
    narrowerTransitive: Uri
    notation: Uri
    note: Uri
    prefLabel: Uri
    related: Uri
    relatedMatch: Uri
    scopeNote: Uri
    semanticRelation: Uri
    topConceptOf: Uri

    # CLASSES
    Collection: Uri
    Concept: Uri
    ConceptScheme: Uri
    OrderedCollection: Uri


class XSD(Vocabulary):
    NS = NameSpace(Uri('http://www.w3.org/2001/XMLSchema#'), prefix='xsd:')

    anyURI: Uri
    base64Binary: Uri
    boolean: Uri
    byte: Uri
    date: Uri
    dateTime: Uri
    dateTimeStamp: Uri
    dayTimeDuration: Uri
    decimal: Uri
    double: Uri
    float: Uri
    gDay: Uri
    gMonth: Uri
    gMonthDay: Uri
    gYear: Uri
    gYearMonth: Uri
    hexBinary: Uri
    int: Uri
    integer: Uri
    language: Uri
    long: Uri
    Name: Uri
    NCName: Uri
    NMTOKEN: Uri
    negativeInteger: Uri
    nonNegativeInteger: Uri
    nonPositiveInteger: Uri
    normalizedString: Uri
    positiveInteger: Uri
    short: Uri
    string: Uri
    time: Uri
    token: Uri
    unsignedByte: Uri
    unsignedInt: Uri
    unsignedLong: Uri
    unsignedShort: Uri
    yearMonthDuration: Uri
    precisionDecimal: Uri
