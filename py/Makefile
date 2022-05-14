SHELL=/usr/bin/env bash

submission:
	tar -zcvf submissions/$$(printf "%(%Y%m%d_%H%M%S)T" -1)_$$(git rev-parse HEAD).tar.gz $$(git ls-files | grep -v '^submissions/')

.PHONY:	submission
