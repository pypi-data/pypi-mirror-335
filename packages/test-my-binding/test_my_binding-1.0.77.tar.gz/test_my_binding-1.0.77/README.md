# Test My Binding

A test repository for CGAL binding using nanobind.



## License

This project is licensed under the GNU Lesser General Public License v3 (LGPLv3).


## Build Many Linux

pip install "cibuildwheel==2.23.1" && python -m cibuildwheel --platform linux --output-dir dist

## Upload to PyPI build_pypi.yml result




Update the version in all files:
- pyproject.toml
- src/test_my_binding/init.py
- CHANGELOG.md

git tag -a v1.0.51 -m "Release version 1.0.51 (Platform-specific builds)" && git push origin v1.0.51

Go to PyPI and add a Trusted Publisher:
- Visit https://pypi.org/manage/account/publishing/
- Click "Add a new trusted publisher"
- Fill in the details:
    - Owner: petrasvestartas
    - Repository name: test_my_binding
    - Workflow name: pypi.yml
    - Environment: pypi

## Run cibuildwheel locally

sudo apt-get update
sudo apt-get install docker.io
sudo systemctl start docker
sudo systemctl enable docker
wget https://dist.nuget.org/win-x86-commandline/latest/nuget.exe -O ~/.cache/cibuildwheel/nuget.exe
chmod +x ~/.cache/cibuildwheel/nuget.exe
export PATH=$PATH:~/.cache/cibuildwheel

pip install cibuildwheel==2.23.1
python -m cibuildwheel --platform linux --output-dir wheelhouse .
python -m cibuildwheel --platform windows --output-dir wheelhouse .