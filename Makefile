mac-first-install: 
	brew install python@3.9
	python3.9 -m venv .venv 
	. .venv/bin/activate && python3.9 -m pip install --upgrade pip
	pip install -r requirements.txt
