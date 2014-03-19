# -*- coding: utf-8 -*-
from datetime import datetime
import os
import sys

# if needed, create possum/settings.py
CONF = os.path.join("..", "possum", "settings.py")
CONF_TEMPLATE = os.path.join("..", "possum", "settings_production.py")
if not os.path.isfile(CONF):
    import shutil
    shutil.copyfile(CONF_TEMPLATE, CONF)

sys.path.append('..')
os.environ['DJANGO_SETTINGS_MODULE'] = 'possum.settings'

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.doctest',
              'sphinx.ext.inheritance_diagram', 'sphinx.ext.todo',
              'sphinx.ext.coverage']

templates_path = ['_templates']
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'
project = u'Possum'
copyright = u'2008-%d, Bonnegent Sébastien' % datetime.now().year

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.
# version = '0.4'
# The full version, including alpha/beta/rc tags.
# release = '0.4'
release = '0.5'

language = 'fr'
today_fmt = '%B %d, %Y'
exclude_trees = ['_build']

# The reST default role (used for this markup: `text`) to use for all documents.
# default_role = None
default_role = 'obj'

# If true, '()' will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []


# -- Options for HTML output ---------------------------------------------------

# The theme to use for HTML and HTML Help pages.  Major themes that come with
# Sphinx are currently 'default' and 'sphinxdoc'.
html_theme = 'default'

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {}
# html_theme_options = {
#    "stickysidebar": "true",
# }

# Add any paths that contain custom themes here, relative to this directory.
# html_theme_path = []

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
# html_title = None
# html_title = "Possum"
# html_title = "Documentation"
html_title = "%s %s" % (project, release)

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = None
html_logo = "../possum/base/static/images/bandeau-192.png"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = None
# html_favicon = "../possum/images/favicon.ico"
# html_favicon = "../possum/static/images/favicon.png"
html_favicon = "../possum/base/static/images/favicon.ico"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
# html_sidebars = {}
html_sidebars = {
    '**': ['globaltoc.html', 'searchbox.html', 'ohloh.html'],
}
#    '**': ['globaltoc.html', 'localtoc.html', 'searchbox.html'],
#    'using/windows': ['windowssidebar.html', 'searchbox.html'],

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_use_modindex = True
html_use_modindex = False

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
# html_show_sourcelink = True
html_show_sourcelink = False

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'Possumdoc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
# latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
# latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'Possum.tex', u'Possum Documentation',
   u'Bonnegent Sébastien', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
# latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
# latex_use_parts = False

# Additional stuff for the LaTeX preamble.
# latex_preamble = ''

# Documents to append as an appendix to all manuals.
# latex_appendices = []

# If false, no module index is generated.
# latex_use_modindex = True
