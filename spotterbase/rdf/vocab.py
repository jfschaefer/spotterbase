""" Commonly used RDF vocabularies (automatically generated) """

from spotterbase.rdf.base import Vocabulary, NameSpace, Uri


class AS(Vocabulary):
    """ Generated from https://raw.githubusercontent.com/w3c/activitystreams/master/vocabulary/activitystreams2.owl """

    NS = NameSpace(Uri('http://www.w3.org/ns/activitystreams#'), prefix='as:')

    # PROPERTIES
    # Specifies the accuracy around the point established by the longitude and latitude
    accuracy: Uri
    # Subproperty of as:attributedTo that identifies the primary actor
    actor: Uri
    # The altitude of a place
    altitude: Uri
    # Describes a possible inclusive answer or option for a question.
    anyOf: Uri
    attachment: Uri
    attachments: Uri
    # Identifies an entity to which an object is attributed
    attributedTo: Uri
    audience: Uri
    # Identifies the author of an object. Deprecated. Use as:attributedTo instead
    author: Uri
    bcc: Uri
    bto: Uri
    cc: Uri
    # The content of the object.
    content: Uri
    # Specifies the context within which an object exists or an activity was performed
    context: Uri
    current: Uri
    # Specifies the date and time the object was deleted
    deleted: Uri
    # On a Profile object, describes the object described by the profile
    describes: Uri
    downstreamDuplicates: Uri
    # The duration of the object
    duration: Uri
    # The ending time of the object
    endTime: Uri
    first: Uri
    # On a Tombstone object, describes the former type of the deleted object
    formerType: Uri
    generator: Uri
    # The display height expressed as device independent pixels
    height: Uri
    # The target URI of the Link
    href: Uri
    # A hint about the language of the referenced resource
    hreflang: Uri
    icon: Uri
    id: Uri
    image: Uri
    inReplyTo: Uri
    # Indentifies an object used (or to be used) to complete an activity
    instrument: Uri
    items: Uri
    last: Uri
    # The latitude
    latitude: Uri
    location: Uri
    # The longitude
    longitude: Uri
    # The MIME Media Type
    mediaType: Uri
    name: Uri
    next: Uri
    object: Uri
    objectType: Uri
    # Describes a possible exclusive answer or option for a question.
    oneOf: Uri
    # For certain activities, specifies the entity from which the action is directed.
    origin: Uri
    partOf: Uri
    prev: Uri
    preview: Uri
    provider: Uri
    # Specifies the date and time the object was published
    published: Uri
    # Specifies a radius around the point established by the longitude and latitude
    radius: Uri
    # A numeric rating (>= 0.0, <= 5.0) for the object
    rating: Uri
    # The RFC 5988 or HTML5 Link Relation associated with the Link
    rel: Uri
    # On a Relationship object, describes the type of relationship
    relationship: Uri
    replies: Uri
    result: Uri
    # In a strictly ordered logical collection, specifies the index position of the first item in the items list
    startIndex: Uri
    # The starting time of the object
    startTime: Uri
    # On a Relationship object, identifies the subject. e.g. when saying "John is connected to Sally", 'subject' refers to 'John'
    subject: Uri
    # A short summary of the object
    summary: Uri
    tag: Uri
    tags: Uri
    target: Uri
    to: Uri
    # The total number of items in a logical collection
    totalItems: Uri
    # Identifies the unit of measurement used by the radius, altitude and accuracy properties. The value can be expressed either as one of a set of predefined units or as a well-known common URI that identifies units.
    units: Uri
    # Specifies when the object was last updated
    updated: Uri
    upstreamDuplicates: Uri
    # Specifies a link to a specific representation of the Object
    url: Uri
    verb: Uri
    # Specifies the preferred display width of the content, expressed in terms of device independent pixels.
    width: Uri

    # CLASSES
    # Actor accepts the Object
    Accept: Uri
    # An Object representing some form of Action that has been taken
    Activity: Uri
    # To Add an Object or Link to Something
    Add: Uri
    # Actor announces the object to the target
    Announce: Uri
    # Represents a software application of any sort
    Application: Uri
    # To Arrive Somewhere (can be used, for instance, to indicate that a particular entity is currently located somewhere, e.g. a "check-in")
    Arrive: Uri
    # A written work. Typically several paragraphs long. For example, a blog post or a news article.
    Article: Uri
    # An audio file
    Audio: Uri
    Block: Uri
    # An ordered or unordered collection of Objects or Links
    Collection: Uri
    # A subset of items from a Collection
    CollectionPage: Uri
    # To Create Something
    Create: Uri
    # To Delete Something
    Delete: Uri
    # The actor dislikes the object
    Dislike: Uri
    # Represents a digital document/file of any sort
    Document: Uri
    # An Event of any kind
    Event: Uri
    # To flag something (e.g. flag as inappropriate, flag as spam, etc)
    Flag: Uri
    # To Express Interest in Something
    Follow: Uri
    # A Group of any kind.
    Group: Uri
    # Actor is ignoring the Object
    Ignore: Uri
    # An Image file
    Image: Uri
    # An Activity that has no direct object
    IntransitiveActivity: Uri
    # To invite someone or something to something
    Invite: Uri
    # To Join Something
    Join: Uri
    # To Leave Something
    Leave: Uri
    # To Like Something
    Like: Uri
    # Represents a qualified reference to another resource. Patterned after the RFC5988 Web Linking Model
    Link: Uri
    # The actor listened to the object
    Listen: Uri
    # A specialized Link that represents an @mention
    Mention: Uri
    # The actor is moving the object. The target specifies where the object is moving to. The origin specifies where the object is moving from.
    Move: Uri
    # A Short note, typically less than a single paragraph. A "tweet" is an example, or a "status update"
    Note: Uri
    Object: Uri
    # To Offer something to someone or something
    Offer: Uri
    # A variation of Collection in which items are strictly ordered
    OrderedCollection: Uri
    # An ordered subset of items from an OrderedCollection
    OrderedCollectionPage: Uri
    # A rdf:List variant for Objects and Links
    OrderedItems: Uri
    # An Organization
    Organization: Uri
    # A Web Page
    Page: Uri
    # A Person
    Person: Uri
    # A physical or logical location
    Place: Uri
    # A Profile Document
    Profile: Uri
    # A question of any sort.
    Question: Uri
    # The actor read the object
    Read: Uri
    # Actor rejects the Object
    Reject: Uri
    # Represents a Social Graph relationship between two Individuals (indicated by the 'a' and 'b' properties)
    Relationship: Uri
    # To Remove Something
    Remove: Uri
    # A service provided by some entity
    Service: Uri
    # Actor tentatively accepts the Object
    TentativeAccept: Uri
    # Actor tentatively rejects the object
    TentativeReject: Uri
    # A placeholder for a deleted object
    Tombstone: Uri
    # The actor is traveling to the target. The origin specifies where the actor is traveling from.
    Travel: Uri
    # To Undo Something. This would typically be used to indicate that a previous Activity has been undone.
    Undo: Uri
    # To Update/Modify Something
    Update: Uri
    # A Video document of any kind.
    Video: Uri
    # The actor viewed the object
    View: Uri


class DC(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_elements.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/elements/1.1/'), prefix='dc:')

    # PROPERTIES
    # An entity responsible for making contributions to the resource.
    contributor: Uri
    # The spatial or temporal topic of the resource, spatial applicability of the resource, or jurisdiction under which the resource is relevant.
    coverage: Uri
    # An entity primarily responsible for making the resource.
    creator: Uri
    # A point or period of time associated with an event in the lifecycle of the resource.
    date: Uri
    # An account of the resource.
    description: Uri
    # The file format, physical medium, or dimensions of the resource.
    format: Uri
    # An unambiguous reference to the resource within a given context.
    identifier: Uri
    # A language of the resource.
    language: Uri
    # An entity responsible for making the resource available.
    publisher: Uri
    # A related resource.
    relation: Uri
    # Information about rights held in and over the resource.
    rights: Uri
    # A related resource from which the described resource is derived.
    source: Uri
    # The topic of the resource.
    subject: Uri
    # A name given to the resource.
    title: Uri
    # The nature or genre of the resource.
    type: Uri


class DCAM(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_abstract_model.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/dcam/'), prefix='dcam:')

    # PROPERTIES
    # A suggested class for subjects of this property.
    domainIncludes: Uri
    # A relationship between a resource and a vocabulary encoding scheme which indicates that the resource is a member of a set.
    memberOf: Uri
    # A suggested class for values of this property.
    rangeIncludes: Uri

    # CLASSES
    # An enumerated set of resources.
    VocabularyEncodingScheme: Uri


class DCTERMS(Vocabulary):
    """ Generated from http://dublincore.org/2020/01/20/dublin_core_terms.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/terms/'), prefix='dcterms:')

    # PROPERTIES
    # A summary of the resource.
    abstract: Uri
    # Information about who access the resource or an indication of its security status.
    accessRights: Uri
    # The method by which items are added to a collection.
    accrualMethod: Uri
    # The frequency with which items are added to a collection.
    accrualPeriodicity: Uri
    # The policy governing the addition of items to a collection.
    accrualPolicy: Uri
    # An alternative name for the resource.
    alternative: Uri
    # A class of agents for whom the resource is intended or useful.
    audience: Uri
    # Date that the resource became or will become available.
    available: Uri
    # A bibliographic reference for the resource.
    bibliographicCitation: Uri
    # An established standard to which the described resource conforms.
    conformsTo: Uri
    # An entity responsible for making contributions to the resource.
    contributor: Uri
    # The spatial or temporal topic of the resource, spatial applicability of the resource, or jurisdiction under which the resource is relevant.
    coverage: Uri
    # Date of creation of the resource.
    created: Uri
    # An entity responsible for making the resource.
    creator: Uri
    # A point or period of time associated with an event in the lifecycle of the resource.
    date: Uri
    # Date of acceptance of the resource.
    dateAccepted: Uri
    # Date of copyright of the resource.
    dateCopyrighted: Uri
    # Date of submission of the resource.
    dateSubmitted: Uri
    # An account of the resource.
    description: Uri
    # A class of agents, defined in terms of progression through an educational or training context, for which the described resource is intended.
    educationLevel: Uri
    # The size or duration of the resource.
    extent: Uri
    # The file format, physical medium, or dimensions of the resource.
    format: Uri
    # A related resource that is substantially the same as the pre-existing described resource, but in another format.
    hasFormat: Uri
    # A related resource that is included either physically or logically in the described resource.
    hasPart: Uri
    # A related resource that is a version, edition, or adaptation of the described resource.
    hasVersion: Uri
    # An unambiguous reference to the resource within a given context.
    identifier: Uri
    # A process, used to engender knowledge, attitudes and skills, that the described resource is designed to support.
    instructionalMethod: Uri
    # A pre-existing related resource that is substantially the same as the described resource, but in another format.
    isFormatOf: Uri
    # A related resource in which the described resource is physically or logically included.
    isPartOf: Uri
    # A related resource that references, cites, or otherwise points to the described resource.
    isReferencedBy: Uri
    # A related resource that supplants, displaces, or supersedes the described resource.
    isReplacedBy: Uri
    # A related resource that requires the described resource to support its function, delivery, or coherence.
    isRequiredBy: Uri
    # A related resource of which the described resource is a version, edition, or adaptation.
    isVersionOf: Uri
    # Date of formal issuance of the resource.
    issued: Uri
    # A language of the resource.
    language: Uri
    # A legal document giving official permission to do something with the resource.
    license: Uri
    # An entity that mediates access to the resource.
    mediator: Uri
    # The material or physical carrier of the resource.
    medium: Uri
    # Date on which the resource was changed.
    modified: Uri
    # A statement of any changes in ownership and custody of the resource since its creation that are significant for its authenticity, integrity, and interpretation.
    provenance: Uri
    # An entity responsible for making the resource available.
    publisher: Uri
    # A related resource that is referenced, cited, or otherwise pointed to by the described resource.
    references: Uri
    # A related resource.
    relation: Uri
    # A related resource that is supplanted, displaced, or superseded by the described resource.
    replaces: Uri
    # A related resource that is required by the described resource to support its function, delivery, or coherence.
    requires: Uri
    # Information about rights held in and over the resource.
    rights: Uri
    # A person or organization owning or managing rights over the resource.
    rightsHolder: Uri
    # A related resource from which the described resource is derived.
    source: Uri
    # Spatial characteristics of the resource.
    spatial: Uri
    # A topic of the resource.
    subject: Uri
    # A list of subunits of the resource.
    tableOfContents: Uri
    # Temporal characteristics of the resource.
    temporal: Uri
    # A name given to the resource.
    title: Uri
    # The nature or genre of the resource.
    type: Uri
    # Date (often a range) of validity of a resource.
    valid: Uri

    # CLASSES
    # A resource that acts or has the power to act.
    Agent: Uri
    # A group of agents.
    AgentClass: Uri
    # A book, article, or other documentary resource.
    BibliographicResource: Uri
    # A digital resource format.
    FileFormat: Uri
    # A rate at which something recurs.
    Frequency: Uri
    # The extent or range of judicial, law enforcement, or other authority.
    Jurisdiction: Uri
    # A legal document giving official permission to do something with a resource.
    LicenseDocument: Uri
    # A system of signs, symbols, sounds, gestures, or rules used in communication.
    LinguisticSystem: Uri
    # A spatial region or named place.
    Location: Uri
    # A location, period of time, or jurisdiction.
    LocationPeriodOrJurisdiction: Uri
    # A file format or physical medium.
    MediaType: Uri
    # A media type or extent.
    MediaTypeOrExtent: Uri
    # A method by which resources are added to a collection.
    MethodOfAccrual: Uri
    # A process that is used to engender knowledge, attitudes, and skills.
    MethodOfInstruction: Uri
    # An interval of time that is named or defined by its start and end dates.
    PeriodOfTime: Uri
    # A physical material or carrier.
    PhysicalMedium: Uri
    # A material thing.
    PhysicalResource: Uri
    # A plan or course of action by an authority, intended to influence and determine decisions, actions, and other matters.
    Policy: Uri
    # Any changes in ownership and custody of a resource since its creation that are significant for its authenticity, integrity, and interpretation.
    ProvenanceStatement: Uri
    # A statement about the intellectual property rights (IPR) held in or over a resource, a legal document giving official permission to do something with a resource, or a statement about access rights.
    RightsStatement: Uri
    # A dimension or extent, or a time taken to play or execute.
    SizeOrDuration: Uri
    # A reference point against which other things can be evaluated or compared.
    Standard: Uri

    # OTHER
    # The set of regions in space defined by their geographic coordinates according to the DCMI Box Encoding Scheme.
    Box: Uri                            # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of classes specified by the DCMI Type Vocabulary, used to categorize the nature or genre of the resource.
    DCMIType: Uri                       # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of conceptual resources specified by the Dewey Decimal Classification.
    DDC: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of media types specified by the Internet Assigned Numbers Authority.
    IMT: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of codes listed in ISO 3166-1 for the representation of names of countries.
    ISO3166: Uri                        # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of conceptual resources specified by the Library of Congress Classification.
    LCC: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of labeled concepts specified by the Library of Congress Subject Headings.
    LCSH: Uri                           # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of labeled concepts specified by the Medical Subject Headings.
    MESH: Uri                           # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of conceptual resources specified by the National Library of Medicine Classification.
    NLM: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of time intervals defined by their limits according to the DCMI Period Encoding Scheme.
    Period: Uri                         # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of points in space defined by their geographic coordinates according to the DCMI Point Encoding Scheme.
    Point: Uri                          # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of tags, constructed according to RFC 1766, for the identification of languages.
    RFC1766: Uri                        # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of tags constructed according to RFC 3066 for the identification of languages.
    RFC3066: Uri                        # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of tags constructed according to RFC 4646 for the identification of languages.
    RFC4646: Uri                        # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of tags constructed according to RFC 5646 for the identification of languages.
    RFC5646: Uri                        # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of places specified by the Getty Thesaurus of Geographic Names.
    TGN: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of conceptual resources specified by the Universal Decimal Classification.
    UDC: Uri                            # a http://purl.org/dc/dcam/VocabularyEncodingScheme
    # The set of identifiers constructed according to the generic syntax for Uniform Resource Identifiers as specified by the Internet Engineering Task Force.
    URI: Uri                            # a http://www.w3.org/2000/01/rdf-schema#Datatype
    # The set of dates and times constructed according to the W3C Date and Time Formats Specification.
    W3CDTF: Uri                         # a http://www.w3.org/2000/01/rdf-schema#Datatype


class DCTYPES(Vocabulary):
    """ Generated from https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_type.ttl """

    NS = NameSpace(Uri('http://purl.org/dc/dcmitype/'), prefix='dctypes:')


    # CLASSES
    # An aggregation of resources.
    Collection: Uri
    # Data encoded in a defined structure.
    Dataset: Uri
    # A non-persistent, time-based occurrence.
    Event: Uri
    # A visual representation other than text.
    Image: Uri
    # A resource requiring interaction from the user to be understood, executed, or experienced.
    InteractiveResource: Uri
    # A series of visual representations imparting an impression of motion when shown in succession.
    MovingImage: Uri
    # An inanimate, three-dimensional object or substance.
    PhysicalObject: Uri
    # A system that provides one or more functions.
    Service: Uri
    # A computer program in source or compiled form.
    Software: Uri
    # A resource primarily intended to be heard.
    Sound: Uri
    # A static visual representation.
    StillImage: Uri
    # A resource consisting primarily of words for reading.
    Text: Uri


class FOAF(Vocabulary):
    """ Generated from http://xmlns.com/foaf/0.1/index.rdf """

    NS = NameSpace(Uri('http://xmlns.com/foaf/0.1/'), prefix='foaf:')

    # PROPERTIES
    # Indicates the name (identifier) associated with this online account.
    accountName: Uri
    # Indicates a homepage of the service provide for this online account.
    accountServiceHomepage: Uri
    # An AIM chat ID
    aimChatID: Uri
    # A location that something is based near, for some broadly human notion of near.
    based_near: Uri
    # A current project this person works on.
    currentProject: Uri
    # A depiction of some thing.
    depiction: Uri
    # A thing depicted in this representation.
    depicts: Uri
    # A checksum for the DNA of some thing. Joke.
    dnaChecksum: Uri
    # The family_name of some person.
    family_name: Uri
    # The first name of a person.
    firstName: Uri
    # An organization funding a project or person.
    fundedBy: Uri
    # A textual geekcode for this person, see http://www.geekcode.com/geek.html
    geekcode: Uri
    # The gender of this Agent (typically but not necessarily 'male' or 'female').
    gender: Uri
    # The given name of some person.
    givenname: Uri
    # Indicates an account held by this agent.
    holdsAccount: Uri
    # A homepage for some thing.
    homepage: Uri
    # An ICQ chat ID
    icqChatID: Uri
    # An image that can be used to represent some thing (ie. those depictions which are particularly representative of something, eg. one's photo on a homepage).
    img: Uri
    # A page about a topic of interest to this person.
    interest: Uri
    # A jabber ID for something.
    jabberID: Uri
    # A person known by this person (indicating some level of reciprocated interaction between the parties).
    knows: Uri
    # A logo representing some thing.
    logo: Uri
    # Something that was made by this agent.
    made: Uri
    # An agent that made this thing.
    maker: Uri
    # A personal mailbox, ie. an Internet mailbox associated with exactly one owner, the first owner of this mailbox. This is a 'static inverse functional property', in that  there is (across time and change) at most one individual that ever has any particular value for foaf:mbox.
    mbox: Uri
    # The sha1sum of the URI of an Internet mailbox associated with exactly one owner, the  first owner of the mailbox.
    mbox_sha1sum: Uri
    # Indicates a member of a Group
    member: Uri
    # Indicates the class of individuals that are a member of a Group
    membershipClass: Uri
    # An MSN chat ID
    msnChatID: Uri
    # A Myers Briggs (MBTI) personality classification.
    myersBriggs: Uri
    # A name for some thing.
    name: Uri
    # A short informal nickname characterising an agent (includes login identifiers, IRC and other chat nicknames).
    nick: Uri
    # A page or document about this thing.
    page: Uri
    # A project this person has previously worked on.
    pastProject: Uri
    # A phone,  specified using fully qualified tel: URI scheme (refs: http://www.w3.org/Addressing/schemes.html#tel).
    phone: Uri
    # A .plan comment, in the tradition of finger and '.plan' files.
    plan: Uri
    # The primary topic of some page or document.
    primaryTopic: Uri
    # A link to the publications of this person.
    publications: Uri
    # A homepage of a school attended by the person.
    schoolHomepage: Uri
    # A sha1sum hash, in hex.
    sha1: Uri
    # The surname of some person.
    surname: Uri
    # A theme.
    theme: Uri
    # A derived thumbnail image.
    thumbnail: Uri
    # A tipjar document for this agent, describing means for payment and reward.
    tipjar: Uri
    # Title (Mr, Mrs, Ms, Dr. etc)
    title: Uri
    # A topic of some page or document.
    topic: Uri
    # A thing of interest to this person.
    topic_interest: Uri
    # A weblog of some thing (whether person, group, company etc.).
    weblog: Uri
    # A work info homepage of some person; a page about their work for some organization.
    workInfoHomepage: Uri
    # A workplace homepage of some person; the homepage of an organization they work for.
    workplaceHomepage: Uri
    # A Yahoo chat ID
    yahooChatID: Uri

    # CLASSES
    # An agent (eg. person, group, software or physical artifact).
    Agent: Uri
    # A document.
    Document: Uri
    # A class of Agents.
    Group: Uri
    # An image.
    Image: Uri
    # An online account.
    OnlineAccount: Uri
    # An online chat account.
    OnlineChatAccount: Uri
    # An online e-commerce account.
    OnlineEcommerceAccount: Uri
    # An online gaming account.
    OnlineGamingAccount: Uri
    # An organization.
    Organization: Uri
    # A person.
    Person: Uri
    # A personal profile RDF document.
    PersonalProfileDocument: Uri
    # A project (a collective endeavour of some kind).
    Project: Uri


class RDF(Vocabulary):
    """ Generated from http://www.w3.org/1999/02/22-rdf-syntax-ns# """

    NS = NameSpace(Uri('http://www.w3.org/1999/02/22-rdf-syntax-ns#'), prefix='rdf:')

    # PROPERTIES
    # The base direction component of a CompoundLiteral.
    direction: Uri
    # The first item in the subject RDF list.
    first: Uri
    # The language component of a CompoundLiteral.
    language: Uri
    # The object of the subject RDF statement.
    object: Uri
    # The predicate of the subject RDF statement.
    predicate: Uri
    # The rest of the subject RDF list after the first item.
    rest: Uri
    # The subject of the subject RDF statement.
    subject: Uri
    # The subject is an instance of a class.
    type: Uri
    # Idiomatic property used for structured values.
    value: Uri

    # CLASSES
    # The class of containers of alternatives.
    Alt: Uri
    # The class of unordered containers.
    Bag: Uri
    # A class representing a compound literal.
    CompoundLiteral: Uri
    # The class of RDF Lists.
    List: Uri
    # The class of RDF properties.
    Property: Uri
    # The class of ordered containers.
    Seq: Uri
    # The class of RDF statements.
    Statement: Uri


class RDFS(Vocabulary):
    """ Generated from http://www.w3.org/2000/01/rdf-schema# """

    NS = NameSpace(Uri('http://www.w3.org/2000/01/rdf-schema#'), prefix='rdfs:')

    # PROPERTIES
    # A description of the subject resource.
    comment: Uri
    # A domain of the subject property.
    domain: Uri
    # The defininition of the subject resource.
    isDefinedBy: Uri
    # A human-readable name for the subject.
    label: Uri
    # A member of the subject resource.
    member: Uri
    # A range of the subject property.
    range: Uri
    # Further information about the subject resource.
    seeAlso: Uri
    # The subject is a subclass of a class.
    subClassOf: Uri
    # The subject is a subproperty of a property.
    subPropertyOf: Uri

    # CLASSES
    # The class of classes.
    Class: Uri
    # The class of RDF containers.
    Container: Uri
    # The class of container membership properties, rdf:_1, rdf:_2, ...,
    #                     all of which are sub-properties of 'member'.
    ContainerMembershipProperty: Uri
    # The class of RDF datatypes.
    Datatype: Uri
    # The class of literal values, eg. textual strings and integers.
    Literal: Uri
    # The class resource, everything.
    Resource: Uri


class OA(Vocabulary):
    """ Generated from http://www.w3.org/ns/oa.ttl """

    NS = NameSpace(Uri('http://www.w3.org/ns/oa#'), prefix='oa:')

    # PROPERTIES
    # The object of the relationship is the end point of a service that conforms to the annotation-protocol, and it may be associated with any resource.  The expectation of asserting the relationship is that the object is the preferred service for maintaining annotations about the subject resource, according to the publisher of the relationship.
    # 
    #   This relationship is intended to be used both within Linked Data descriptions and as the  rel  type of a Link, via HTTP Link Headers rfc5988 for binary resources and in HTML <link> elements.  For more information about these, please see the Annotation Protocol specification annotation-protocol.
    annotationService: Uri
    # The object of the predicate is a plain text string to be used as the content of the body of the Annotation.  The value MUST be an  xsd:string  and that data type MUST NOT be expressed in the serialization. Note that language MUST NOT be associated with the value either as a language tag, as that is only available for  rdf:langString .
    bodyValue: Uri
    # A object of the relationship is a copy of the Source resource's representation, appropriate for the Annotation.
    cachedSource: Uri
    # A object of the relationship is the canonical IRI that can always be used to deduplicate the Annotation, regardless of the current IRI used to access the representation.
    canonical: Uri
    # The end property is used to convey the 0-based index of the end position of a range of content.
    end: Uri
    # The object of the predicate is a copy of the text which is being selected, after normalization.
    exact: Uri
    # The object of the relationship is a resource that is a body of the Annotation.
    hasBody: Uri
    # The relationship between a RangeSelector and the Selector that describes the end position of the range.
    hasEndSelector: Uri
    # The purpose served by the resource in the Annotation.
    hasPurpose: Uri
    # The scope or context in which the resource is used within the Annotation.
    hasScope: Uri
    # The object of the relationship is a Selector that describes the segment or region of interest within the source resource.  Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasSelector: Uri
    # The resource that the ResourceSelection, or its subclass SpecificResource, is refined from, or more specific than. Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasSource: Uri
    # The relationship between a RangeSelector and the Selector that describes the start position of the range.
    hasStartSelector: Uri
    # The relationship between the ResourceSelection, or its subclass SpecificResource, and a State resource. Please note that the domain ( oa:ResourceSelection ) is not used directly in the Web Annotation model.
    hasState: Uri
    # The relationship between an Annotation and its Target.
    hasTarget: Uri
    # The relationship between an Annotation and a Motivation that describes the reason for the Annotation's creation.
    motivatedBy: Uri
    # The object of the property is a snippet of content that occurs immediately before the content which is being selected by the Selector.
    prefix: Uri
    # The object of the property is the language that should be used for textual processing algorithms when dealing with the content of the resource, including hyphenation, line breaking, which font to use for rendering and so forth.  The value must follow the recommendations of BCP47.
    processingLanguage: Uri
    # The relationship between a Selector and another Selector or a State and a Selector or State that should be applied to the results of the first to refine the processing of the source resource.
    refinedBy: Uri
    # A system that was used by the application that created the Annotation to render the resource.
    renderedVia: Uri
    # The timestamp at which the Source resource should be interpreted as being applicable to the Annotation.
    sourceDate: Uri
    # The end timestamp of the interval over which the Source resource should be interpreted as being applicable to the Annotation.
    sourceDateEnd: Uri
    # The start timestamp of the interval over which the Source resource should be interpreted as being applicable to the Annotation.
    sourceDateStart: Uri
    # The start position in a 0-based index at which a range of content is selected from the data in the source resource.
    start: Uri
    # The name of the class used in the CSS description referenced from the Annotation that should be applied to the Specific Resource.
    styleClass: Uri
    # A reference to a Stylesheet that should be used to apply styles to the Annotation rendering.
    styledBy: Uri
    # The snippet of text that occurs immediately after the text which is being selected.
    suffix: Uri
    # The direction of the text of the subject resource. There MUST only be one text direction associated with any given resource.
    textDirection: Uri
    # A object of the relationship is a resource from which the source resource was retrieved by the providing system.
    via: Uri

    # CLASSES
    # The class for Web Annotations.
    Annotation: Uri
    # A subClass of  as:OrderedCollection  that conveys to a consuming application that it should select one of the resources in the  as:items  list to use, rather than all of them.  This is typically used to provide a choice of resources to render to the user, based on further supplied properties.  If the consuming application cannot determine the user's preference, then it should use the first in the list.
    Choice: Uri
    # A CssSelector describes a Segment of interest in a representation that conforms to the Document Object Model through the use of the CSS selector specification.
    CssSelector: Uri
    # A resource which describes styles for resources participating in the Annotation using CSS.
    CssStyle: Uri
    # DataPositionSelector describes a range of data by recording the start and end positions of the selection in the stream. Position 0 would be immediately before the first byte, position 1 would be immediately before the second byte, and so on. The start byte is thus included in the list, but the end byte is not.
    DataPositionSelector: Uri
    # A class to encapsulate the different text directions that a textual resource might take.  It is not used directly in the Annotation Model, only its three instances.
    Direction: Uri
    # The FragmentSelector class is used to record the segment of a representation using the IRI fragment specification defined by the representation's media type.
    FragmentSelector: Uri
    # The HttpRequestState class is used to record the HTTP request headers that a client SHOULD use to request the correct representation from the resource.
    HttpRequestState: Uri
    # The Motivation class is used to record the user's intent or motivation for the creation of the Annotation, or the inclusion of the body or target, that it is associated with.
    Motivation: Uri
    # A Range Selector can be used to identify the beginning and the end of the selection by using other Selectors. The selection consists of everything from the beginning of the starting selector through to the beginning of the ending selector, but not including it.
    RangeSelector: Uri
    # Instances of the ResourceSelection class identify part (described by an oa:Selector) of another resource (referenced with oa:hasSource), possibly from a particular representation of a resource (described by an oa:State). Please note that ResourceSelection is not used directly in the Web Annotation model, but is provided as a separate class for further application profiles to use, separate from oa:SpecificResource which has many Annotation specific features.
    ResourceSelection: Uri
    # A resource which describes the segment of interest in a representation of a Source resource, indicated with oa:hasSelector from the Specific Resource. This class is not used directly in the Annotation model, only its subclasses.
    Selector: Uri
    # Instances of the SpecificResource class identify part of another resource (referenced with oa:hasSource), a particular representation of a resource, a resource with styling hints for renders, or any combination of these, as used within an Annotation.
    SpecificResource: Uri
    # A State describes the intended state of a resource as applied to the particular Annotation, and thus provides the information needed to retrieve the correct representation of that resource.
    State: Uri
    # A Style describes the intended styling of a resource as applied to the particular Annotation, and thus provides the information to ensure that rendering is consistent across implementations.
    Style: Uri
    # An SvgSelector defines an area through the use of the Scalable Vector Graphics [SVG] standard. This allows the user to select a non-rectangular area of the content, such as a circle or polygon by describing the region using SVG. The SVG may be either embedded within the Annotation or referenced as an External Resource.
    SvgSelector: Uri
    # The TextPositionSelector describes a range of text by recording the start and end positions of the selection in the stream. Position 0 would be immediately before the first character, position 1 would be immediately before the second character, and so on.
    TextPositionSelector: Uri
    # The TextQuoteSelector describes a range of text by copying it, and including some of the text immediately before (a prefix) and after (a suffix) it to distinguish between multiple copies of the same sequence of characters.
    TextQuoteSelector: Uri
    TextualBody: Uri
    # A TimeState records the time at which the resource's state is appropriate for the Annotation, typically the time that the Annotation was created and/or a link to a persistent copy of the current version.
    TimeState: Uri
    # An XPathSelector is used to select elements and content within a resource that supports the Document Object Model via a specified XPath value.
    XPathSelector: Uri

    # OTHER
    # An IRI to signal the client prefers to receive full descriptions of the Annotations from a container, not just their IRIs.
    PreferContainedDescriptions: Uri    # a http://www.w3.org/2000/01/rdf-schema#Resource
    # An IRI to signal that the client prefers to receive only the IRIs of the Annotations from a container, not their full descriptions.
    PreferContainedIRIs: Uri            # a http://www.w3.org/2000/01/rdf-schema#Resource
    # The motivation for when the user intends to provide an assessment about the Target resource.
    assessing: Uri                      # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to create a bookmark to the Target or part thereof.
    bookmarking: Uri                    # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to that classify the Target as something.
    classifying: Uri                    # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to comment about the Target.
    commenting: Uri                     # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to describe the Target, as opposed to a comment about them.
    describing: Uri                     # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to request a change or edit to the Target resource.
    editing: Uri                        # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to highlight the Target resource or segment of it.
    highlighting: Uri                   # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to assign an identity to the Target or identify what is being depicted or described in the Target.
    identifying: Uri                    # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to link to a resource related to the Target.
    linking: Uri                        # a http://www.w3.org/ns/oa#Motivation
    # The direction of text that is read from left to right.
    ltrDirection: Uri                   # a http://www.w3.org/ns/oa#Direction
    # The motivation for when the user intends to assign some value or quality to the Target.
    moderating: Uri                     # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to ask a question about the Target.
    questioning: Uri                    # a http://www.w3.org/ns/oa#Motivation
    # The motivation for when the user intends to reply to a previous statement, either an Annotation or another resource.
    replying: Uri                       # a http://www.w3.org/ns/oa#Motivation
    # The direction of text that is read from right to left.
    rtlDirection: Uri                   # a http://www.w3.org/ns/oa#Direction
    # The motivation for when the user intends to associate a tag with the Target.
    tagging: Uri                        # a http://www.w3.org/ns/oa#Motivation


class OWL(Vocabulary):
    """ Generated from http://www.w3.org/2002/07/owl# """

    NS = NameSpace(Uri('http://www.w3.org/2002/07/owl#'), prefix='owl:')

    # PROPERTIES
    # The property that determines the class that a universal property restriction refers to.
    allValuesFrom: Uri
    # The property that determines the predicate of an annotated axiom or annotated annotation.
    annotatedProperty: Uri
    # The property that determines the subject of an annotated axiom or annotated annotation.
    annotatedSource: Uri
    # The property that determines the object of an annotated axiom or annotated annotation.
    annotatedTarget: Uri
    # The property that determines the predicate of a negative property assertion.
    assertionProperty: Uri
    # The annotation property that indicates that a given ontology is backward compatible with another ontology.
    backwardCompatibleWith: Uri
    # The data property that does not relate any individual to any data value.
    bottomDataProperty: Uri
    # The object property that does not relate any two individuals.
    bottomObjectProperty: Uri
    # The property that determines the cardinality of an exact cardinality restriction.
    cardinality: Uri
    # The property that determines that a given class is the complement of another class.
    complementOf: Uri
    # The property that determines that a given data range is the complement of another data range with respect to the data domain.
    datatypeComplementOf: Uri
    # The annotation property that indicates that a given entity has been deprecated.
    deprecated: Uri
    # The property that determines that two given individuals are different.
    differentFrom: Uri
    # The property that determines that a given class is equivalent to the disjoint union of a collection of other classes.
    disjointUnionOf: Uri
    # The property that determines that two given classes are disjoint.
    disjointWith: Uri
    # The property that determines the collection of pairwise different individuals in a owl:AllDifferent axiom.
    distinctMembers: Uri
    # The property that determines that two given classes are equivalent, and that is used to specify datatype definitions.
    equivalentClass: Uri
    # The property that determines that two given properties are equivalent.
    equivalentProperty: Uri
    # The property that determines the collection of properties that jointly build a key.
    hasKey: Uri
    # The property that determines the property that a self restriction refers to.
    hasSelf: Uri
    # The property that determines the individual that a has-value restriction refers to.
    hasValue: Uri
    # The property that is used for importing other ontologies into a given ontology.
    imports: Uri
    # The annotation property that indicates that a given ontology is incompatible with another ontology.
    incompatibleWith: Uri
    # The property that determines the collection of classes or data ranges that build an intersection.
    intersectionOf: Uri
    # The property that determines that two given properties are inverse.
    inverseOf: Uri
    # The property that determines the cardinality of a maximum cardinality restriction.
    maxCardinality: Uri
    # The property that determines the cardinality of a maximum qualified cardinality restriction.
    maxQualifiedCardinality: Uri
    # The property that determines the collection of members in either a owl:AllDifferent, owl:AllDisjointClasses or owl:AllDisjointProperties axiom.
    members: Uri
    # The property that determines the cardinality of a minimum cardinality restriction.
    minCardinality: Uri
    # The property that determines the cardinality of a minimum qualified cardinality restriction.
    minQualifiedCardinality: Uri
    # The property that determines the class that a qualified object cardinality restriction refers to.
    onClass: Uri
    # The property that determines the data range that a qualified data cardinality restriction refers to.
    onDataRange: Uri
    # The property that determines the datatype that a datatype restriction refers to.
    onDatatype: Uri
    # The property that determines the n-tuple of properties that a property restriction on an n-ary data range refers to.
    onProperties: Uri
    # The property that determines the property that a property restriction refers to.
    onProperty: Uri
    # The property that determines the collection of individuals or data values that build an enumeration.
    oneOf: Uri
    # The annotation property that indicates the predecessor ontology of a given ontology.
    priorVersion: Uri
    # The property that determines the n-tuple of properties that build a sub property chain of a given property.
    propertyChainAxiom: Uri
    # The property that determines that two given properties are disjoint.
    propertyDisjointWith: Uri
    # The property that determines the cardinality of an exact qualified cardinality restriction.
    qualifiedCardinality: Uri
    # The property that determines that two given individuals are equal.
    sameAs: Uri
    # The property that determines the class that an existential property restriction refers to.
    someValuesFrom: Uri
    # The property that determines the subject of a negative property assertion.
    sourceIndividual: Uri
    # The property that determines the object of a negative object property assertion.
    targetIndividual: Uri
    # The property that determines the value of a negative data property assertion.
    targetValue: Uri
    # The data property that relates every individual to every data value.
    topDataProperty: Uri
    # The object property that relates every two individuals.
    topObjectProperty: Uri
    # The property that determines the collection of classes or data ranges that build a union.
    unionOf: Uri
    # The property that identifies the version IRI of an ontology.
    versionIRI: Uri
    # The annotation property that provides version information for an ontology or another OWL construct.
    versionInfo: Uri
    # The property that determines the collection of facet-value pairs that define a datatype restriction.
    withRestrictions: Uri

    # CLASSES
    # The class of collections of pairwise different individuals.
    AllDifferent: Uri
    # The class of collections of pairwise disjoint classes.
    AllDisjointClasses: Uri
    # The class of collections of pairwise disjoint properties.
    AllDisjointProperties: Uri
    # The class of annotated annotations for which the RDF serialization consists of an annotated subject, predicate and object.
    Annotation: Uri
    # The class of annotation properties.
    AnnotationProperty: Uri
    # The class of asymmetric properties.
    AsymmetricProperty: Uri
    # The class of annotated axioms for which the RDF serialization consists of an annotated subject, predicate and object.
    Axiom: Uri
    # The class of OWL classes.
    Class: Uri
    # The class of OWL data ranges, which are special kinds of datatypes. Note: The use of the IRI owl:DataRange has been deprecated as of OWL 2. The IRI rdfs:Datatype SHOULD be used instead.
    DataRange: Uri
    # The class of data properties.
    DatatypeProperty: Uri
    # The class of deprecated classes.
    DeprecatedClass: Uri
    # The class of deprecated properties.
    DeprecatedProperty: Uri
    # The class of functional properties.
    FunctionalProperty: Uri
    # The class of inverse-functional properties.
    InverseFunctionalProperty: Uri
    # The class of irreflexive properties.
    IrreflexiveProperty: Uri
    # The class of named individuals.
    NamedIndividual: Uri
    # The class of negative property assertions.
    NegativePropertyAssertion: Uri
    # This is the empty class.
    Nothing: Uri
    # The class of object properties.
    ObjectProperty: Uri
    # The class of ontologies.
    Ontology: Uri
    # The class of ontology properties.
    OntologyProperty: Uri
    # The class of reflexive properties.
    ReflexiveProperty: Uri
    # The class of property restrictions.
    Restriction: Uri
    # The class of symmetric properties.
    SymmetricProperty: Uri
    # The class of OWL individuals.
    Thing: Uri
    # The class of transitive properties.
    TransitiveProperty: Uri


class SKOS(Vocabulary):
    """ Generated from https://www.w3.org/2009/08/skos-reference/skos.rdf """

    NS = NameSpace(Uri('http://www.w3.org/2004/02/skos/core#'), prefix='skos:')

    # PROPERTIES
    # skos:prefLabel, skos:altLabel and skos:hiddenLabel are pairwise disjoint properties.
    altLabel: Uri
    broadMatch: Uri
    # Broader concepts are typically rendered as parents in a concept hierarchy (tree).
    broader: Uri
    broaderTransitive: Uri
    changeNote: Uri
    closeMatch: Uri
    definition: Uri
    editorialNote: Uri
    # skos:exactMatch is disjoint with each of the properties skos:broadMatch and skos:relatedMatch.
    exactMatch: Uri
    example: Uri
    hasTopConcept: Uri
    # skos:prefLabel, skos:altLabel and skos:hiddenLabel are pairwise disjoint properties.
    hiddenLabel: Uri
    historyNote: Uri
    inScheme: Uri
    # These concept mapping relations mirror semantic relations, and the data model defined below is similar (with the exception of skos:exactMatch) to the data model defined for semantic relations. A distinct vocabulary is provided for concept mapping relations, to provide a convenient way to differentiate links within a concept scheme from links between concept schemes. However, this pattern of usage is not a formal requirement of the SKOS data model, and relies on informal definitions of best practice.
    mappingRelation: Uri
    member: Uri
    # For any resource, every item in the list given as the value of the
    #       skos:memberList property is also a value of the skos:member property.
    memberList: Uri
    narrowMatch: Uri
    # Narrower concepts are typically rendered as children in a concept hierarchy (tree).
    narrower: Uri
    narrowerTransitive: Uri
    notation: Uri
    note: Uri
    # skos:prefLabel, skos:altLabel and skos:hiddenLabel are pairwise
    #       disjoint properties.
    prefLabel: Uri
    # skos:related is disjoint with skos:broaderTransitive
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
