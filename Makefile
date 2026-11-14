.PHONY: test package

test:
	python3 -m unittest discover -s tests -v

package:
	@test -n "$(OUTPUT)" || { echo 'Set OUTPUT to an empty staging directory outside this checkout.' >&2; exit 2; }
	python3 scripts/package.py "$(OUTPUT)"
