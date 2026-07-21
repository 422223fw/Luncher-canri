[app]
title = CANRI Launcher
package.name = canrilauncher
package.domain = com.motlon
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt
source.exclude_dirs = .git,bin,.buildozer,sample_canri
version = 1.0.0
requirements = python3,kivy,requests,urllib3,certifi,charset-normalizer,idna
orientation = portrait
fullscreen = 0
android.permissions = INTERNET
android.api = 35
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
