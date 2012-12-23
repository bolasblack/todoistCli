.PHONY : install uninstall clean

define clean-folder
	-rm *.pyc
	-rm todoist.zip
endef

install :
	pip install -r requirements.txt
	zip todoist.zip  todoistSDK.py
	cat zipheader.unix todoistCli.py > todoist
	echo "\nEND_OF_PYTHON_CODE" >> todoist
	cat todoist.zip  >> todoist
	chmod +x todoist
	mv todoist /usr/sbin/
	$(clean-folder)

uninstall :
	$(clean-folder)
	rm /usr/sbin/todoist

clean :
	$(clean-folder)
