# Docker variables
image_name=estimators-lib:latest
documentation_path=$(shell pwd)
container_name="container-for-docs"
SAGE=sage
PACKAGE=cryptographic_estimators
UNAME:=$(shell uname -m)

tools:
	@sage -python -m pip install setuptools==63.0 wheel==0.38.4 sphinx==5.3.0 furo prettytable scipy pytest pytest-xdist python-flint 

lib:
	@python3 setup.py install && sage -python -m pip install .

install:
	@make tools && make lib

docker-build-x86:
	@docker build -t ${image_name} .

docker-build-m1:
	@docker buildx build -t ${image_name} --platform linux/x86_64 .

docker-build:
ifeq ($(UNAME), arm64)
	@make docker-build-m1
else
	@make docker-build-x86
endif 

docker-run:
	@docker run -it --rm ${image_name}

testfast:
	@sage setup.py testfast

testall: install
	@sage setup.py testall

clean-docs:
	@rm -rf docs/build docs/source docs/make.bat docs/Makefile

create-sphinx-config:
	@sphinx-quickstart -q --sep -p TII-Estimators -a TII -l en --ext-autodoc docs

create-rst-files:
	@python3 scripts/create_documentation.py

create-html-docs:
	@sphinx-build -b html docs/source/ docs/build/html

doc:
	@make clean-docs && make create-sphinx-config && make create-rst-files && make create-html-docs

add-estimator:
	@python3 scripts/create_new_estimator.py && make add-copyright

append-new-estimator:
	@python3 scripts/append_estimator_to_input_dictionary.py

stop-container-and-remove:
	@docker stop $(container_name) && docker rm $(container_name)

generate-documentation:
	@docker exec container-for-docs make doc

mount-volume-and-run: 
	@docker run --name container-for-docs --mount type=bind,source=${documentation_path}/docs,target=/home/cryptographic_estimators/docs -d -it ${image_name} sh

pipeline-test:
	@docker run --name container-for-test -d -it ${image_name} sh && docker exec container-for-test sage -t --long -T 3600 --force-lib cryptographic_estimators && docker stop container-for-test && docker rm container-for-test

docker-doc: docker-build
	@make mount-volume-and-run && make generate-documentation && make stop-container-and-remove container_name="container-for-docs"

docker-test: docker-build
	@echo "Removing previous container...."
	@make stop-container-and-remove container_name="container-for-test" \
		|| true
	@echo "Creating container..."
	@docker run --name container-for-test -d -it ${image_name} sh \
		&& docker exec container-for-test sh -c " \
		sage -t --long --timeout 3600 --force-lib \
		# cryptographic_estimators/SDEstimator/ \
		cryptographic_estimators/DummyEstimator/ \
		cryptographic_estimators/LEEstimator/ \
		cryptographic_estimators/MAYOEstimator/ \
		cryptographic_estimators/MQEstimator/ \
		cryptographic_estimators/MREstimator/ \
		cryptographic_estimators/PEEstimator/ \
		cryptographic_estimators/PKEstimator/ \
		cryptographic_estimators/RegSDEstimator/ \
		cryptographic_estimators/SDFqEstimator/ \
		cryptographic_estimators/UOVEstimator/ \
		cryptographic_estimators/base_algorithm.py \
		cryptographic_estimators/base_constants.py \
		cryptographic_estimators/base_estimator.py \
		cryptographic_estimators/base_problem.py \
		cryptographic_estimators/estimation_renderer.py \
		cryptographic_estimators/helper.py \
		" \
		&& echo "All tests passed." \
		|| echo "Some test have failed, please see previous lines."
	@echo "Cleaning container..."
	@make stop-container-and-remove container_name="container-for-test"


docker-testfast: docker-build
	@echo "Removing previous container...."
	@make stop-container-and-remove container_name="container-for-test" \
		|| true
	@echo "Creating container..."
	@docker run --name container-for-test -d -it ${image_name} sh \
		&& docker exec container-for-test sh -c " \
		sage -t --timeout 3600 --force-lib \
		# cryptographic_estimators/SDEstimator/ \
		cryptographic_estimators/DummyEstimator/ \
		cryptographic_estimators/LEEstimator/ \
		cryptographic_estimators/MAYOEstimator/ \
		cryptographic_estimators/MQEstimator/ \
		cryptographic_estimators/MREstimator/ \
		cryptographic_estimators/PEEstimator/ \
		cryptographic_estimators/PKEstimator/ \
		cryptographic_estimators/RegSDEstimator/ \
		cryptographic_estimators/SDFqEstimator/ \
		cryptographic_estimators/UOVEstimator/ \
		cryptographic_estimators/base_algorithm.py \
		cryptographic_estimators/base_constants.py \
		cryptographic_estimators/base_estimator.py \
		cryptographic_estimators/base_problem.py \
		cryptographic_estimators/estimation_renderer.py \
		cryptographic_estimators/helper.py \
		" \
		&& echo "All tests passed." \
		|| echo "Some test have failed, please see previous lines."
	@echo "Cleaning container..."
	@make stop-container-and-remove container_name="container-for-test"

add-copyright:
	@python3 scripts/create_copyright.py

docker-pytest:
	@echo "Removing previous container...."
	@make stop-container-and-remove container_name="pytest-estimators" \
		|| true
	@echo "Creating container..."
	@docker run --name pytest-estimators -d -it ${image_name} sh \
		&& docker exec pytest-estimators sh -c " \
		pytest --doctest-modules -n auto -vv \
		tests/test_kat.py \
		cryptographic_estimators/SDEstimator/ \
		# cryptographic_estimators/DummyEstimator/ \
		# cryptographic_estimators/LEEstimator/ \
		# cryptographic_estimators/MAYOEstimator/ \
		# cryptographic_estimators/MQEstimator/ \
		# cryptographic_estimators/MREstimator/ \
		# cryptographic_estimators/PEEstimator/ \
		# cryptographic_estimators/PKEstimator/ \
		# cryptographic_estimators/RegSDEstimator/ \
		# cryptographic_estimators/SDFqEstimator/ \
		# cryptographic_estimators/UOVEstimator/ \
		# cryptographic_estimators/base_algorithm.py \
		# cryptographic_estimators/base_constants.py \
		# cryptographic_estimators/base_estimator.py \
		# cryptographic_estimators/base_problem.py \
		# cryptographic_estimators/estimation_renderer.py \
		# cryptographic_estimators/helper.py \
		" \
	@echo "Cleaning container..."
	@make stop-container-and-remove container_name="pytest-estimators"


docker-generate-kat: docker-build
	@docker run --name gen-tests-references -v ./tests:/home/cryptographic_estimators/tests --rm ${image_name} sh -c \
		"sage tests/external_estimators/generate_kat.py"
	@make docker-build

# docker-pytest:
# 	@echo "Removing previous container...."
# 	@make stop-container-and-remove container_name="pytest-estimators" \
# 		|| true
# 	@echo "Creating container..."
# 	@docker run --name pytest-estimators -d -it ${image_name} sh \
# 		&& docker exec pytest-estimators sh -c "sage --python3 -m pytest -n auto -vv \
# 		--cov-report xml:coverage.xml --cov=${PACKAGE} \
# 		&& ${SAGE} tests/SDFqEstimator/test_sdfq.sage \
# 		&& ${SAGE} tests/LEEstimator/test_le_beullens.sage \
# 		&& ${SAGE} tests/LEEstimator/test_le_bbps.sage \
# 		&& ${SAGE} tests/PEEstimator/test_pe.sage \
# 		&& ${SAGE} tests/PKEstimator/test_pk.sage" \
# 		&& echo "All tests passed." \
# 		|| echo "Some test have failed, please see previous lines."
# 	@echo "Cleaning container..."
# 	@make stop-container-and-remove container_name="pytest-estimators"

docker-pytest-cov:
	pytest -v --cov-report xml:coverage.xml --cov=${PACKAGE} tests/
