#!/bin/bash

echo ________ pack before publishing ___________________
mkdir -p  ./data/installation_files/bin
mkdir -p  ./data/installation_files/codeframe
 cp README.org    ./data/installation_files/
 cp distcheck.sh    ./data/installation_files/
 cp requirements.txt    ./data/installation_files/
 cp .bumpversion.cfg    ./data/installation_files/
 cp setup.py    ./data/installation_files/
 cp .gitignore    ./data/installation_files/
 cp bin/codeframe    ./data/installation_files/bin/
 cp bin_codeframe.py    ./data/installation_files/
 cp codeframe/__init__.py    ./data/installation_files/codeframe/

echo ________twine check__________________
pip show twine
if [ "$?" != "0" ]; then
    pip3 install twine
fi
echo _____bumpversion check_______________

pip show bumpversion
if [ "$?" != "0" ]; then
    pip3 install bumpversion
fi
echo ______________ok_____________________

# rm dist/*
# echo _____________________________________
# python3 setup.py sdist
# echo _____________________________________
# twine check dist/*


echo ___________________markdown__________

#echo "D...  converting  to MARKDOWN automatically"
if [ -e README.org ]; then
   echo "D...  converting org to MARKDOWN automatically"
    pandoc README.org -o README.md
fi

echo ______________diff  bin directory____
echo .
echo diff bin_codeframe.py bin/codeframe
diff  bin_codeframe.py bin/codeframe
if [ "$?" != "0" ]; then

  echo X... difference bin and bin
  sleep 1
  echo I will overwrite NOW !!!!
  sleep 1
  cp  bin_codeframe.py bin/codeframe
else
    echo ... ok ... same
fi

echo _____________________________________

echo "#### - i will run"
echo "####        - git commit"
echo "####        - bumpversion patch"
echo "####        - bumpversion release"
echo "####        - twine upload !!!!!"
echo "####                                 ok?          ENTER then"
read a

echo ________________commit_______________

git commit -a -m "automatic commit  distcheck"

echo ____________pull_____________________

git pull origin --tags

echo ________________bump_________________

bumpversion patch

echo _____________________________________

bumpversion release

echo ________________remove_______________

rm dist/*

echo _____________setup check_____________

python3 setup.py sdist

if [ "$?" != "0" ]; then
    exit 1
fi

echo __________Twine check________________

twine check dist/*

if [ "$?" != "0" ]; then
    exit 1
fi

echo _____________________________________


echo "                                 ok? passed?  "
echo "                                 ok? passed?  "
echo " - check  correctness of download/url and email"
echo "                                 ok? passed?  ENTER then"
read a


echo _____________________________________

echo _____________________________________


echo " "
echo " "
echo SUGGESTIONS:=======================================================
#
echo "twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
echo "pip3 install --index-url https://test.pypi.org/simple/ notifator"
echo "pip3 install --index-url https://test.pypi.org/simple/ notifator --upgrade"
#
echo " "
echo "          real PyPI UPLOAD (after bumpversion release):"
echo "          real PyPI UPLOAD (after bumpversion release):"
echo "twine upload dist/*"
echo " ... "


echo _____________________________________
echo _____________________UPLOAD__________

twine  upload  dist/* #  --repository-url https://test.pypi.org/legacy/
if [ "$?" != "0" ]; then
    echo X... SOME ERROR APPEARED DURING UPLOAD
    echo pip3 install --upgrade twine requests-toolbelt
    echo pip3 install --upgrade twine requests-toolbelt
    echo pip3 install --upgrade twine requests-toolbelt
    exit 1
fi

echo _____________________________________
echo ____________________PUSH_________________

echo "i... pushing newly created tags to GITREPO"
git push origin  --tags
git push origin
echo ________________remove dist_______________

rm -rf dist
