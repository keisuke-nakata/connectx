SHELL=/usr/bin/env bash

submission:
	# git archive --format=tar.gz --worktree-attributes HEAD > submissions/$$(printf "%(%Y%m%d_%H%M%S)T" -1)_$$(git rev-parse HEAD).tar.gz
	tar -zcvf submissions/$$(printf "%(%Y%m%d_%H%M%S)T" -1)_$$(git rev-parse HEAD).tar.gz $$(git ls-files | grep -v '^submissions/')

.PHONY:	submission
