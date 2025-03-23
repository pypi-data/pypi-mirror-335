## Installation of pip package:

First `pip install build` and `pip install twine`. Then set the environment variables`
```
export TWINE_USERNAME="__token__"
export TWINE_PASSWORD="API_KEY" 
```
Then build the package while you are in the [cmtqoUtilities](cmtqoUtilities) direcotry
```
python -m build
```
Then upload the package to your PyPi accounty by 
```
twine upload dist/* --non-interactive
```