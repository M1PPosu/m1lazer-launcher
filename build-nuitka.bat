python.exe -m nuitka --output-filename=m1pplazer --standalone --nofollow-imports --onefile --remove-output --msvc=latest --windows-icon-from-ico=assets/icon.ico --no-pyi-file --windows-disable-console --include-data-files="assets/*=assets/" --assume-yes-for-downloads --output-dir=nuitka_output --enable-plugin=tk-inter main.py

