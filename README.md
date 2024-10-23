run tests:

docker-compose -f ./docker-compose-tests.yml up --build

.../src$ pytest -v -s tests/test_roles.py
...