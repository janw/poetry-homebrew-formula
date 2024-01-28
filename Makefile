.PHONY: rich-codex
rich-codex:
	CLEAN_IMG_PATHS=./assets/*.svg \
	FORCE_COLOR="1" \
	TERMINAL_WIDTH="140" \
	TERMINAL_THEME=MONOKAI \
	NO_CONFIRM="true" \
	SKIP_GIT_CHECKS="true" \
	poetry run rich-codex
