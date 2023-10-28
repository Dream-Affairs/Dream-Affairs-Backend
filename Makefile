.PHONY: 

message ?= "update database"


upgrade:
	alembic revision --autogenerate -m {message}
	alembic upgrade head

downgrade:
	alembic downgrade -1

service:
	python3 main.py

test:
	python3 pytest 

commit:
	git add .
	git commit

fmt:
	python -m black .