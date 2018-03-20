define cleanup
	sudo rm -rf build dist *.egg-info
endef

init:
	pip --user install -r requirements.txt

test: init
	nosetests --verbosity=2 --with-coverage --cover-package=velarium tests

clean:
	$(call cleanup)

install: test
	sudo python setup.py install

uninstall:
	sudo python setup.py install --record files.txt
	cat files.txt | xargs sudo rm -rf
	sudo rm files.txt
	$(call cleanup)

purge: uninstall
	rm -rf ~/.config/velarium/

reinstall: uninstall install

run: install
	velarium
