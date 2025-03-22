#!/bin/bash
set -e

# Nettoyer les builds précédents
rm -rf dist/ build/ *.egg-info/

# Construire le package
python -m pip install --upgrade build
python -m build

# Vérifier le package
python -m pip install --upgrade twine
python -m twine check dist/*

# Publier sur PyPI (décommenter pour publier)
echo "Pour publier sur PyPI, utilisez la commande suivante :"
echo "python -m twine upload dist/*"
echo
echo "Pour publier sur TestPyPI, utilisez la commande suivante :"
echo "python -m twine upload --repository testpypi dist/*" 