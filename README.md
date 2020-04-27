#### File (mostly picture) sorting script / UI application

Runs on macOS, Linux, Windows. Python 3.7 needed.

To run sources on Linux:
```
sudo apt-get install python3 python3-tk magic
virtualenv -p python3 .virtualenv
.virtualenv/bin/pip install -r REQUIREMENTS
.virtualenv/bin/python FileSorter.py
```
To run sources on macOS:
```
brew install python3
brew install libmagic
virtualenv -p python3 .virtualenv
.virtualenv/bin/pip install -r REQUIREMENTS
.virtualenv/bin/python FileSorter.py
```

```
# TODO list:
    - do visual path format constructing maybe
    - make an app for windows, macOS, linux. make instructions?
    - make instructions to run on windows
    - make option for considering hidden files
    - make option about what date to consider when sorting:
        file created, photo shot
    - more information in process output logs for user. maybe not
    - do something with TODOs in code
    - write some tests maybe
    - do not clear the fields when changing the language
    - add docker
```
Icon made by Creaticca Creative Agency from www.flaticon.com is licensed by CC 3.0 BY
