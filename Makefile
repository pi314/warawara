.PHONY: what
what:
	@echo $$ make run
	@echo $$ make clean
	@echo $$ make htmldoc


.PHONY: run
run:
	@sh scripts/runtest.sh


.PHONY: clean
clean:
	@echo $$ rm -rf htmlcov
	@rm -rf htmlcov

	@echo $$ rm -rf htmldoc
	@rm -rf htmldoc


# =============================================================================
# - Prepare ruby and gem
#   $ brew install ruby
#
# - Add "/usr/local/opt/ruby/bin" into PATH
# - Add "$HOME/.local/share/gem/ruby/3.4.0/bin" into PATH
#
# - Download https://gist.github.com/pi314/27f6a2cf9343fd92ffadafbd4093b5a8 as gfm
#
# - Install dependencies
#   $ gem install --user-install redcarpet
# =============================================================================

HTMLDOC := htmldoc
GFM := scripts/gfm

.PHONY: htmldoc
htmldoc: ${HTMLDOC}/README.html $(patsubst doc/%.md,${HTMLDOC}/%.html,$(wildcard doc/*.md))

${HTMLDOC}/%.html: %.md Makefile ${GFM}
	@[ -d '${HTMLDOC}' ] || mkdir '${HTMLDOC}'
	@echo '$< -> $@'
	@'${GFM}' '$<' '$@'
	@sed -i '' 's|href="\(doc/\)\{0,1\}\(.*\).md"|href="\2.html"|' '$@'

vpath %.md doc
