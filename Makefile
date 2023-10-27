.PHONY: 

message ?= "update database"


upgrade:
	alembic revision --autogenerate -m {message}
	alembic upgrade head

downgrade:
	alembic downgrade -1

service:
	python main.py

test:
	python test.py

commit:
	git add .
	git commit

fmt:
	python -m black .