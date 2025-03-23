import logging

import IPython
from IPython.core import magic_arguments

from dbox.templater import to_template

count = 0
log = logging.getLogger(__name__)


@magic_arguments.magic_arguments()
@magic_arguments.argument("--o", help="output variable for rendered result")
@magic_arguments.argument("--tpl", help="output variable for parsed template")
@magic_arguments.argument("--parse-only", action="store_true")
@magic_arguments.argument("--of", help="the file to write the output to in addition to output to stdout")
def jinja_magic(line: str, cell: str = None):
    ns = magic_arguments.parse_argstring(jinja_magic, line)
    ipy = IPython.get_ipython()
    global count  # noqa
    if not ns.o or not ns.tpl:
        count += 1
    ovar = ns.o or f"js{count}"
    tplvar = ns.tpl or f"tpl{count}"
    template = to_template(cell.lstrip())
    if ns.parse_only:
        ipy.push({tplvar: template})
        return
    s = template.render(ipy.ns_table["user_global"])
    print(s)
    log.debug("stored output to %s and template to %s", ovar, tplvar)
    ipy.push({ovar: s, tplvar: template})
