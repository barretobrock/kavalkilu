PROJECT 		:= kavalkilu
PY_LIB_NAME 	:= kavalkilu
VENV_NAME 		:= kavkil
MAIN_BRANCH 	:= master


bump-patch:
	@echo "PPM path: '${PPM_ABS_PATH}'"
	sh "${PPM_ABS_PATH}" -d --cmd bump --level patch --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
bump-minor:
	@echo "PPM path: '${PPM_ABS_PATH}'"
	sh "${PPM_ABS_PATH}" -d --cmd bump --level minor --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
bump-major:
	@echo "PPM path: '${PPM_ABS_PATH}'"
	sh "${PPM_ABS_PATH}" -d --cmd bump --level major --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
pull:
	@echo "PPM path: '${PPM_ABS_PATH}'"
	sh "${PPM_ABS_PATH}" -d --cmd pull --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)
push:
	@echo "PPM path: '${PPM_ABS_PATH}'"
	sh "${PPM_ABS_PATH}" -d --cmd push --project $(PROJECT) --lib $(PY_LIB_NAME) --venv $(VENV_NAME) --main-branch $(MAIN_BRANCH)

debug-run:
	python3 run_debug.py
check:
	pre-commit run --all-files
install:
	# First-time install - use when lock file is stable
	poetry install -v
update:
	# Update lock file based on changed reqs
	poetry update -v

test:
	tox
rebuild-test:
	tox --recreate -e py311
