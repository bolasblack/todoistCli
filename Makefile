.PHONY : install uninstall clean

define clean-folder
	-rm *.pyc
	-rm todoist.zip
endef

define build-file
	pip install -r requirements.txt
	python -c "import py_compile;py_compile.compile(r'todoistCli.py')"
	python -c "import py_compile;py_compile.compile(r'todoistSDK.py')"
	zip todoist.zip todoistCli.pyc todoistSDK.pyc
	cat zipheader.unix todoist.zip > todoist
	chmod +x todoist
endef

install :
	$(build-file)
	mv todoist /usr/sbin/
	$(clean-folder)

uninstall :
	$(clean-folder)
	rm /usr/sbin/todoist

debug :
	$(build-file)
	#$(clean-folder)

clean :
	$(clean-folder)
