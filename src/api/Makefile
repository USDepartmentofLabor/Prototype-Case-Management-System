freeze:
	pip freeze | grep -v "pkg-resources" > requirements.txt

run:
	flask run --host=0.0.0.0

deploy-dev:
	eb deploy eps-dev-api --profile default

deploy-demo:
	eb deploy eps-demo-api --profile default

test-full-with-conv:
	pytest --cov-report html --cov=app tests/

load-dev-dataset:
	flask load-dev-dataset http://localhost:5000

load-demo-dataset:
	flask load-demo-dataset http://localhost:5000

load-impaq-dataset:
	flask load-impaq-dataset http://localhost:5000

create-storage:
	mkdir /tmp/storage_files; touch /tmp/storage_files/KEEPME
