[app]
title = FONTAMAT
package.name = fontamat
package.domain = org.fontanilles

# Indique que les sources sont dans le dossier courant
source.dir = .

# Version de l'application (OBLIGATOIRE)
version = 1.0.0

source.include_exts = py,png,jpg,kv,json,db
requirements = python3,kivy,requests,urllib3,idna,certifi,charset-normalizer
orientation = portrait
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
# (int) Android API to target
android.api = 33

# (int) Minimum API supported
android.min_api = 21

# (str) Android NDK version to use
android.ndk = 25b
# (int) Automatically accept SDK license
android.accept_sdk_license = True
