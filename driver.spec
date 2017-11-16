# -*- mode: python -*-
block_cipher = None

import os
import PyInstaller.utils.hooks

CS_L1_NETCORE = "../cloudshell-L1-networking-core"

HOME = "C:\Github\cloudshell-L1-fiberzone_afm"

def add_data_files(related_path, root_path="."):

    path = os.path.join(root_path, related_path)
    templates = []
    for resp_temp_file in os.listdir(path):
        templates.append((os.path.join(related_path, resp_temp_file),
                          os.path.join(path, resp_temp_file),
                          "DATA"))
    return templates

a = Analysis(['main.py'],
             pathex=[os.path.join(HOME, "cloudshell-core"), os.path.join(HOME, "cloudshell-cli"),
             os.path.join(HOME, "cloudshell-L1-networking-core"), os.path.join(HOME, "cloudshell-L1-fiberzone_afm")],
             binaries=None,
             datas=PyInstaller.utils.hooks.collect_data_files('cloudshell.core.logger') + \
             PyInstaller.utils.hooks.collect_data_files('fiberzone_afm'),
             hiddenimports=PyInstaller.utils.hooks.collect_submodules('cloudshell-cli') + \
             PyInstaller.utils.hooks.collect_submodules('paramiko') + [
                "fiberzone_afm"
             ] + PyInstaller.utils.hooks.collect_submodules('cloudshell'),
             hookspath=["..\cloudshell-cli\."],
             runtime_hooks=None,
             excludes=["cloudshell.snmp", "cloudshell.shell", "cloudshell.networking"],
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries + add_data_files("cloudshell/layer_one/core/response/templates", CS_L1_NETCORE) + \
          add_data_files("cloudshell/layer_one/core/response/resource_info/templates", CS_L1_NETCORE),
          a.zipfiles,
          a.datas,
          name='FIBERZONE AFM',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          version='version.txt',
          icon=os.path.join(CS_L1_NETCORE, "img/icon.ico")
          )

# -*- mode: python -*-
block_cipher = None

import os
import PyInstaller.utils.hooks

HOME = "../"
DEPENDENCIES = "dependencies"

def add_data_files(related_path, root_path="."):

    path = os.path.join(root_path, related_path)
    templates = []
    for resp_temp_file in os.listdir(path):
        templates.append((os.path.join(related_path, resp_temp_file),
                          os.path.join(path, resp_temp_file),
                          "DATA"))
    return templates

a = Analysis(['main.py'],
             pathex=[os.path.join(DEPENDENCIES, ""), os.path.join(HOME, "cloudshell-L1-drivername")],
             binaries=None,
             datas=PyInstaller.utils.hooks.collect_data_files('cloudshell.core.logger') + \
             PyInstaller.utils.hooks.collect_data_files('drivername'),
             hiddenimports=PyInstaller.utils.hooks.collect_submodules('cloudshell-cli') + \
             PyInstaller.utils.hooks.collect_submodules('paramiko') + [
                "drivername"
             ] + PyInstaller.utils.hooks.collect_submodules('cloudshell'),
             hookspath=[DEPENDENCIES+"\."],
             runtime_hooks=None,
             excludes=["cloudshell.snmp", "cloudshell.shell", "cloudshell.networking"],
             win_no_prefer_redirects=None,
             win_private_assemblies=None,
             cipher=block_cipher)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries + add_data_files("cloudshell/layer_one/core/response/templates", DEPENDENCIES) + \
          add_data_files("cloudshell/layer_one/core/response/resource_info/templates", DEPENDENCIES),
          a.zipfiles,
          a.datas,
          name='DRIVERNAME',
          debug=False,
          strip=None,
          upx=True,
          console=True,
          version='version.txt',
          icon=os.path.join(".", "img/icon.ico")
          )

