pyinstaller --onefile driver.spec
copy datamodel\*.xml dist /Y
copy fiberzone_afm_runtimeconfig.yml dist /Y
