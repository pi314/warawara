#!/usr/bin/env sh
# =============================================================================
# - Prepare ruby and gem
#   $ brew install ruby
#
# - Add "/usr/local/opt/ruby/bin" into PATH
# - Add "$HOME/.local/share/gem/ruby/3.4.0/bin" into PATH
#
# - Download https://gist.github.com/Pysis868/6a42c95cfb410d5f384c2e8a97ce44f9 as gfm
# - Modify first line to "#!/usr/bin/env ruby"
#
# - Install dependencies
#   $ gem install --user-install redcarpet
# =============================================================================

HTMLDOC='htmldoc'
GFM='scripts/gfm'

[ -d "$HTMLDOC" ] || mkdir "$HTMLDOC"

"$GFM" README.md "$HTMLDOC/README.html"

find doc -name '*.md' \
    -exec sh -c "$GFM"' "{}" "'"$HTMLDOC"'/$(basename {} .md)".html' ';' \
    -exec sh -c 'echo "{}" "->" "'"$HTMLDOC"'/$(basename {} .md).html"' ';'
