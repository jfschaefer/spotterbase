from docutils import nodes
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import logging as sphinx_logging

sphinx_logger = sphinx_logging.getLogger(__name__)


class SbLinkWarnings(SphinxPostTransform):
    """nitpicky=True is too strict for me, this is essentially a restricted form under my control"""

    default_priority = 5

    def run(self):
        for node in self.document.findall(addnodes.pending_xref):
            target = node['reftarget']
            typ = node['reftype']

            def warn():
                sphinx_logger.warning(f'No {typ} target for {target}', location=node, type='ref', subtype=typ)

            if target.startswith('spotterbase.'):
                try:
                    domain = self.env.domains[node['refdomain']]
                except KeyError:
                    warn()
                    continue

                # if resolution works, we're good
                if domain.resolve_xref(
                    self.env, node.get('refdoc', self.env.docname), self.app.builder, typ, target, node,
                        nodes.TextElement('', ''),
                ):
                    continue

                # if it's private, it won't be documented
                module_name, obj_name = target.rsplit('.', 1)
                if obj_name.startswith('_'):
                    continue   # private, i.e. not documented (might be referenced as attribute type by autodoc)
                warn()


def setup(app: Sphinx):
    app.add_post_transform(SbLinkWarnings)
