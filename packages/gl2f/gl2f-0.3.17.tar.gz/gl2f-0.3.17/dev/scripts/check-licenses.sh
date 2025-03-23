pipdeptree --packages gl2f -f | grep -v gl2f | sed 's/ //g' | sed -e 's/==.*//g' | xargs pip-licenses -f markdown --order license --packages
