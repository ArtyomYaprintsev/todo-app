app := APP_MAIN

run:
	$(if $(value $(app)),,$(error $$$(app) is not set))
	@echo "Run server $(app): '$(value $(app))' file"
	uvicorn $(value $(app)):app --reload
