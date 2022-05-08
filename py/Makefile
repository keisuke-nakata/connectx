SHELL=/usr/bin/env bash

submission:
	git archive --format=tar.gz HEAD > submissions/$$(printf "%(%Y%m%d_%H%M%S)T" -1)_$$(git rev-parse HEAD).tar.gz

.PHONY:	submission
