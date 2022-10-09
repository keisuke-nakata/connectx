SHELL=/usr/bin/env bash

submission:
	tar -zcvf submissions/$$(printf "%(%Y%m%d_%H%M%S)T" -1)_$$(git rev-parse HEAD).tar.gz $$(git ls-files | grep -v '^submissions/')

# usage: KAGGLE_USERNAME=... KAGGLE_PASSWORD=... make download_log submission_id=...
download_log:
	python connectx/analyze_log/download_log.py $(submission_id) connectx/analyze_log/out

.PHONY:	submission download_log
