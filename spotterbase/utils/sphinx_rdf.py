"""A Sphinx extension for dealing with RDF and SB records."""
import json
from pathlib import Path
from typing import Optional

from docutils import nodes
from docutils.parsers.rst import directives
from rdflib import Graph
from sphinx.application import Sphinx
from sphinx.domains import Domain
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec
from sphinx.writers.html import HTMLTranslator

from spotterbase import __version__
from spotterbase.rdf import Triple, triples_to_nt_string, NameSpaceCollection, StandardNameSpaces
from spotterbase.rdf.from_rdflib import triples_from_graph
from spotterbase.rdf.serializer import triples_to_turtle
from spotterbase.rdf.visualize import triples_to_graphviz
from spotterbase.records.jsonld_support import JsonLdRecordConverter
from spotterbase.records.record import Record
from spotterbase.records.record_to_python_source import record_to_python_source


class rdfnode(nodes.General, nodes.Element):
    """Confusingly, this is a Sphinx node, corresponding to a small RDF graph (not a node in an RDF graph)."""


class AbstractRdfDirective(SphinxDirective):
    has_content = True
    required_arguments = 1
    optional_arguments = 0
    option_spec: OptionSpec = {
        'show': directives.unchanged,
    }

    _default_hide: set[str]
    _default_show: set[str]

    _format: str

    def run(self):
        node = rdfnode()
        changes = set(option.strip() for option in self.options.get('show', '').split())
        hide = set(self._default_hide)
        show = set(self._default_show)
        for change in changes:
            if change.startswith('--'):
                n = change[2:]
                if n in hide:
                    hide.remove(n)
                if n in show:
                    show.remove(n)
            elif change.startswith('-'):
                n = change[1:]
                hide.add(n)
                if n in show:
                    show.remove(n)
            elif change.startswith('+'):
                n = change[1:]
                show.add(n)
                if n in hide:
                    hide.remove(n)
            else:
                raise ValueError(f'Invalid show option: {change}')
        node['content'] = '\n'.join(self.content)
        node['format'] = self._format
        node['hide'] = hide
        node['show'] = show
        node['name'] = self.arguments[0]
        return [node]


class TurtleDirective(AbstractRdfDirective):
    _default_hide: set[str] = {'ntriples', 'graph'}
    _default_show: set = {'turtle'}
    _format = 'turtle'


class RecordDirective(AbstractRdfDirective):
    _default_hide: set[str] = {'ntriples', 'graph', 'turtle', 'python'}
    _default_show: set[str] = {'json'}
    _format: str = 'record'


class RdfDomain(Domain):
    name = 'rdf'
    label = 'RDF domain'

    roles: dict = {}
    directives = {
        'turtle': TurtleDirective,
        'record': RecordDirective,
    }
    initial_data: dict = {}
    indices: dict = {}

    def get_full_qualified_name(self, node):
        return f'rdf.{node.get("id")}'

    def get_objects(self):
        return []


def html_visit_rdfnode(self: HTMLTranslator, node: rdfnode) -> None:
    # self.body.append(f'<code>{node["content"]}</code>')
    jsonld: Optional[str] = None
    record: Optional[Record] = None
    if node['format'] == 'turtle':
        turtle = node['content']
        triples: list[Triple] = list(triples_from_graph(Graph().parse(data=turtle, format='turtle')))
        namespace_collection: Optional[NameSpaceCollection] = NameSpaceCollection.from_turtle(turtle)
    elif node['format'] == 'record':
        converter = JsonLdRecordConverter.default()
        jsonld = node['content']
        assert isinstance(jsonld, str)
        record = converter.json_ld_to_record(json_ld=json.loads(jsonld))
        triples = list(record.to_triples(use_blanknode_if_no_uri=True))
        turtle = triples_to_turtle(triples)
        namespace_collection = StandardNameSpaces
    else:
        raise ValueError(f'Unsupported format: {node["format"]}')

    ntriples = triples_to_nt_string(triples)

    open_ = ' open="open"'
    self.body.append('<div class="admonition">')

    if jsonld:
        self.body.append(f'<details{open_ if "json" in node["show"] else ""}><summary>View JSON</summary>')
        self.body.append(self.highlighter.highlight_block(jsonld, 'json'))
        self.body.append('</details>')

    if 'python' in node['show'] | node['hide']:
        assert record is not None
        self.body.append(f'<details{open_ if "python" in node["show"] else ""}>')
        self.body.append('<summary>View Python (auto-generated)</summary>')
        self.body.append(self.highlighter.highlight_block(record_to_python_source(record), 'python'))
        self.body.append('</details>')

    self.body.append(f'<details{open_ if "turtle" in node["show"] else ""}><summary>View Turtle</summary>')
    self.body.append(self.highlighter.highlight_block(turtle, 'turtle'))
    self.body.append('</details>')

    self.body.append(f'<details{open_ if "ntriples" in node["show"] else ""}><summary>View N-Triples</summary>')
    self.body.append(self.highlighter.highlight_block(ntriples, 'turtle'))
    self.body.append('</details>')

    graph = triples_to_graphviz(triples, namespace_collection, name=node['name'], relaxed_labels=True)
    graph.render(directory=Path(self.builder.outdir) / self.builder.imgpath, filename=node['name'],
                 format='svg', cleanup=True)
    rel_uri = f'{self.builder.imgpath}/{node["name"]}.svg'
    self.body.append(f'<details{open_ if "graph" in node["show"] else ""}><summary>View Graph</summary>')
    self.body.append(f'<div class="graphviz"><object data="{rel_uri}" type="image/svg+xml"></object></div></details>')

    self.body.append('</div>')

    raise nodes.SkipNode


def setup(app: Sphinx):
    # app.add_directive("sbrecord", SbRecordDirective)
    app.add_node(
        rdfnode,
        html=(html_visit_rdfnode, None),
    )
    app.add_domain(RdfDomain)
    return {
        'version': __version__,
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
