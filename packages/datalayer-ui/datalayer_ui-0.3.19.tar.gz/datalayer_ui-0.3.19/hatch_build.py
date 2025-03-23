# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

import glob
import os

from subprocess import check_call

import shutil

from pathlib import Path
from typing import Any

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


HERE = os.path.abspath(os.path.dirname(__file__))


def update_submodules():
    """You may run `git config --global submodule.recurse true`"""
    check_call(['git', 'submodule', 'update', '--init', '--recursive'], cwd=HERE)

def build_javascript():
    check_call(['yarn', 'install'], cwd=HERE)
    check_call(['yarn', 'build:webpack', '--mode=production'], cwd=HERE)

def strip_src(path):
    check_call(['./dev/strip-src.sh', path], cwd=HERE)

def copy_static():
    for file in glob.glob(r'./dist/*.js'):
        shutil.copy(file, './datalayer_ui/static/')


class JupyterBuildHook(BuildHookInterface):
    def initialize(self, version, build_data):
        if (Path("datalayer_ui/labextension/static/style.js")).exists():
            return
#        update_submodules()
        if self.target_name == 'editable':
            build_javascript()
            copy_static()
        elif self.target_name == 'wheel':
            build_javascript()
            copy_static()
        elif self.target_name == 'sdist':
            build_javascript()
            copy_static()

    def finalize(self, version: str, build_data: dict[str, Any], artifact_path: str) -> None:
        if self.target_name == 'sdist':
            strip_src(artifact_path)
