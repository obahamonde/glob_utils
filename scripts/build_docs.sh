sphinx-quickstart docs
sphinx-apidoc  -o docs glob_utils
curl https://raw.githubusercontent.com/obahamonde/glob_utils/main/scripts/conf > docs/conf.py
cd docs
make html
cd ..
mv docs/build/html/ .
rm -rf docs