[app]

# (str) Title of your application
title = FONTAMAT

# (str) Package name
package.name = fontamat

# (str) Package domain (needed for android packaging)
package.domain = org.fontanilles

# (str) Source files to include (let it include python scripts, json, db, etc.)
source.include_exts = py,png,jpg,kv,json,db

# (list) Application requirements
# Ajoutez ici les bibliothèques Python utilisées par votre appli mobile
requirements = python3,kivy,requests,urllib3,idna,certifi,charset-normalizer

# (str) Supported orientations
orientation = portrait

# (list) Permissions
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2