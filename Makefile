all:
	@echo what?


run:
	@sh scripts/runtest.sh


docs:
	@sh scripts/builddoc.sh


clean:
	rm -rf htmlcov
	rm -rf htmldoc
