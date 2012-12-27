.PHONY : install uninstall clean

define clean-folder
	-rm *.pyc
	-rm todoist.zip
endef

install :
	pip install -r requirements.txt
	zip todoist.zip todoistCli.py todoistSDK.py
	cat zipheader.unix todoist.zip > todoist
	chmod +x todoist
	mv todoist /usr/sbin/
	$(clean-folder)

uninstall :
	$(clean-folder)
	rm /usr/sbin/todoist

debug :
	pip install -r requirements.txt
	zip todoist.zip todoistCli.py todoistSDK.py
	cat zipheader.unix todoist.zip > todoist
	chmod +x todoist
	$(clean-folder)

clean :
	$(clean-folder)
