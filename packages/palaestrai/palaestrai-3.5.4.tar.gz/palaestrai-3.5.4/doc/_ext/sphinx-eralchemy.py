from pathlib import Path
from typing import List

from docutils import nodes
from eralchemy2 import render_er
from sphinx.application import Sphinx
from sphinx.directives import SphinxDirective

import palaestrai.store.database_base as dbm


class ERAlchemy(SphinxDirective):
    def run(self) -> List[nodes.Node]:
        output_filename = "store_er_diagram.png"
        output_dir = Path(self.state.document.current_source).parent
        output_file_path = output_dir / output_filename

        render_er(input=dbm.Base, output=str(output_file_path))
        return [nodes.image(uri=output_filename)]


def setup(app: Sphinx):
    app.add_directive("eralchemy", ERAlchemy)
    return {
        "version": "0.1",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
