# Releasing new version
You need to be a maintainer to do this. When a new version is pushed to main, the deployment on pypi is started. 
The version is the git tag v0.n.m. setuptools_scm uses it for building and stores it in xgee/_version.py.
```
git submodule update --remote xgee/core
git add .
git commit
git tag v0.n.m
git pull
git push -o ci.skip
git push origin v0.n.m
```
(push option to skip pipeline to not run twice)

# Test locally
clone an xgee app, e.g. the xgee-example-application
```
git clone --recurse-submodules git@gitlab.com:xgee/xgee-example-app.git
```

### quickly test the files
relative imports need to match, so run as module from xgee-launcher-package folder
```
python -m xgee.xgee
```

### test the build

```
python -m build
```
create and activate a virtual environment  
install the just built package
```
pip install dist/XGEE... .whl
```
run xgee
```
xgee
```

