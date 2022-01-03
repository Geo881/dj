pyenv: .python-version

.python-version: setup.cfg
	if [ -z "`pyenv virtualenvs | grep datajunction`" ]; then\
	    pyenv virtualenv datajunction;\
	fi
	if [ ! -f .python-version ]; then\
	    pyenv local datajunction;\
	fi
	pip install -e '.[testing]'
	touch .python-version

test: pyenv
	pytest --cov=src/datajunction -vv tests/ --doctest-modules src/datajunction

clean:
	pyenv virtualenv-delete datajunction

spellcheck:
	codespell -S "*.json" src/datajunction docs/*rst tests templates

requirements.txt: .python-version
	pip install --upgrade pip
	pip-compile --no-annotate

check:
	pre-commit run --all-files