**File (mostly picture) sorting script / UI application**

Runs on Windows, Linux, macOS

To run sources on Linux:
```
sudo apt-get install python3 python3-tk magic
virtualenv -r python3 .virtualenvs/file-sort
.virtualenvs/file-sort/bin/pip install -r REQUIREMENTS
.virtualenvs/file-sort/bin/python FileSorter.py
```
To run sources on macOS:
```
brew install python3
brew install libmagic
virtualenv -r python3 .virtualenvs/file-sort
.virtualenvs/file-sort/bin/pip install -r REQUIREMENTS
.virtualenvs/file-sort/bin/python FileSorter.py
```

Assembling application for macOS:
```
rm -rf build dist
.virtualenvs/file-sort/bin/python setup.py py2app
```


Icon made by Creaticca Creative Agency from www.flaticon.com is licensed by CC 3.0 BY
