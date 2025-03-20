# sphinx-apidoc src/ --force -F -d 10 --separate -H nanoml -A "Shubhashis Roy Dipta" -o ./docs/source --ext-autodoc --ext-viewcode --ext-githubpages
sphinx-apidoc src/ --force -d 10 --separate -H nanoml -A "Shubhashis Roy Dipta" -o ./docs/source --ext-autodoc --ext-viewcode --ext-githubpages

sphinx-build -b html docs/source docs/