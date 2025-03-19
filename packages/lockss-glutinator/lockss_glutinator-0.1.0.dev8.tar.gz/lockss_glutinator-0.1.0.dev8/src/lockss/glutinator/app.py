#!/usr/bin/env python3

# Copyright (c) 2000-2025, Board of Trustees of Leland Stanford Jr. University
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors
# may be used to endorse or promote products derived from this software without
# specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

# Mimicking what datamodel-codegen does, not sure if it's because of --target-python-version=3.9
from __future__ import annotations

import zipfile
from collections import ChainMap
import importlib.resources
import json
import shutil
import tarfile
from pathlib import Path
from typing import Any, List, Literal, Optional
import zipfile

from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel, Field
from split_file_reader import SplitFileReader
import yaml

import lockss.glutinator
from .item import Root, Publisher, Journal, JournalVolume, JournalIssue, JournalArticle

class GlutinatorConfigModel(BaseModel):
    kind: Literal['glutinator-configuration']
    id: str
    name: str
    source_aus: Optional[List[str]] = Field(None, alias='source-aus')

class GlutinatorApp(object):

    DEFAULT_CONFIG_FILE = 'glutinator.yaml'

    DEFAULT_GENERATE_STATIC_SITE_OUTPUT_DIRECTORY = 'static-site'

    DEFAULT_UNPACK_SOURCES_INPUT_DIRECTORY = 'sources'

    DEFAULT_UNPACK_SOURCES_OUTPUT_DIRECTORY = 'sources-unpacked'

    def __init__(self):
        super().__init__()
        self._config: Optional[GlutinatorConfigModel] = None
        self._env: Environment = None
        self._inventory: Root = None

    def generate_static_site(self,
                             inventory_file: Path,
                             # conffile: Path = DEFAULT_CONFIG_FILE,
                             base_url: str,
                             outdir: Path = DEFAULT_GENERATE_STATIC_SITE_OUTPUT_DIRECTORY,
                             exist_ok=True):
        if not exist_ok and outdir.exists():
            raise FileExistsError(f'{outdir!s}')
        outdir.mkdir(parents=True, exist_ok=exist_ok)
        with open(inventory_file, 'r') as fin:
            data = json.load(fin)
        data['metadata'] = None # FIXME oops Pydantic.dump_model_json(exclude_none=True)
        self._inventory = Root(**data)
        self._env = Environment(loader=PackageLoader("lockss.glutinator.resources.editorial"),
                                autoescape=select_autoescape())
        self._generate_static_site_home(outdir, base_url)
        with importlib.resources.path(lockss.glutinator.resources.editorial, 'assets') as assets:
            shutil.copytree(assets, f'{outdir}/assets', dirs_exist_ok=True)

    def unpack_sources(self,
                       conffile: Path = DEFAULT_CONFIG_FILE,
                       indir: Path = DEFAULT_UNPACK_SOURCES_INPUT_DIRECTORY,
                       outdir: Path = DEFAULT_UNPACK_SOURCES_OUTPUT_DIRECTORY,
                       exist_ok: bool = True):
        self._load_configuration(conffile)
        if not indir.exists():
            raise FileNotFoundError(f'{indir!s}')
        if not exist_ok and outdir.exists():
            raise FileExistsError(f'{outdir!s}')
        for nickname in (self._config.source_aus or list()):
            outsubdir = Path(outdir, nickname)
            outsubdir.mkdir(parents=True, exist_ok=exist_ok)
            single = Path(indir, f'{nickname}.tgz')
            if single.exists():
                with tarfile.open(single, 'r:gz') as tgz:
                    tgz.extractall(outsubdir)
            else:
                width = 0
                while width < 4:
                    if Path(indir, f'{nickname}.tgz.{0:0{width}d}').exists():
                        break
                    width = width + 1
                if width == 4:
                    raise FileNotFoundError(', '.join(f'{nickname}.tgz.{0:0{pad}d}' for pad in range(0, 4)))
                file_list = list()
                i = 0
                while True:
                    f = Path(indir, f'{nickname}.tgz.{i:0{width}d}')
                    if not f.exists():
                        break
                    file_list.append(f)
                    i = i + 1
                with SplitFileReader(file_list) as splitf, tarfile.open(fileobj=splitf, mode='r:gz') as tgz:
                    tgz.extractall(outsubdir)

    def _copy_article_file(self, artid: str, src, dst_dir):
        if not dst_dir.is_dir():
            raise RuntimeError(f'Destination must be a directory: {dst_dir!s}')
        proper_src_name, _, archive_name = str(src).partition('!/')

        if archive_name == '':
            actual_src_path = Path(src)
            actual_dst_path = Path(dst_dir, f'{artid}{actual_src_path.suffix}')
            shutil.copy2(actual_src_path, actual_dst_path)
        else:
            actual_src_path = Path(proper_src_name)
            adjusted_src_path = Path(proper_src_name.removesuffix('/#content/current'))
            adjusted_src_name = adjusted_src_path.name
            actual_dst_path = Path(dst_dir, f'{artid}{Path(archive_name).suffix}')
            if adjusted_src_name.endswith('.zip'):
                with zipfile.ZipFile(actual_src_path, 'r') as zip:
                    zip.extract(archive_name, dst_dir)
                    adjusted_dst_path = Path(dst_dir, Path(archive_name).name)
                    adjusted_dst_path.rename(actual_dst_path)
            else:
                raise NotImplementedError(f'No archive file implementation available: {src!s}')

    def _generate_static_site_home(self,
                                   outdir: Path,
                                   base_url: str):
        root = self._inventory
        template = self._env.get_template(root.template())
        context = ChainMap(dict(base_url=base_url,
                                breadcrumbs=[root],
                                current=root,
                                parent_path='', # None?
                                # is_local=True,
                                # local_base=f'file://{outdir}',
                                menu=[root.publishers]))
        template.stream(context).dump(f'{outdir}{root.path(context['breadcrumbs'])}')
        for publisher in root.publishers:
            self._generate_static_site_publisher(outdir, publisher, context)

    def _generate_static_site_journal(self,
                                      outdir: Path,
                                      journal: Journal,
                                      parent_context: ChainMap):
        template = self._env.get_template(journal.template())
        context = parent_context.new_child(dict(breadcrumbs=[*parent_context['breadcrumbs'], journal],
                                                current=journal,
                                                parent_path=f'{parent_context['parent_path']}/{journal.directory()}',
                                                menu=[*parent_context['menu'], journal.journal_volumes]))
        joudir = Path(outdir, parent_context['parent_path'].removeprefix('/'), journal.directory())
        joudir.mkdir(exist_ok=True)
        template.stream(context).dump(f'{outdir}{journal.path(context['breadcrumbs'])}')
        if journal.logo is not None and journal.logo.startswith('file::'):
            shutil.copy2(journal.logo.removeprefix('file::'), joudir)
        for journal_volume in journal.journal_volumes:
            self._generate_static_site_journal_volume(outdir, journal_volume, context)

    def _generate_static_site_journal_article(self,
                                              outdir: Path,
                                              journal_article: JournalArticle,
                                              parent_context: ChainMap):
        template = self._env.get_template(journal_article.template())
        context = parent_context.new_child(dict(breadcrumbs=[*parent_context['breadcrumbs'], journal_article],
                                                current=journal_article,
                                                parent_path=f'{parent_context['parent_path']}/{journal_article.directory()}', # Note: same menu as volume
                                                menu_collapsed=True)) # ...but collapsed
        # FIXME parent_path is a vestigial mess, should use Item path(...)
        artdir = Path(outdir, parent_context['parent_path'].removeprefix('/'), journal_article.directory())
        artdir.mkdir(exist_ok=True)
        template.stream(context).dump(f'{outdir}{journal_article.path(context['breadcrumbs'])}')
        for filekey, filevalue in journal_article.metadata.custom.items():
            if filekey.startswith('file::'):
                filetype = filekey.removeprefix('file::')
                filedir = Path(artdir, filetype)
                filedir.mkdir(exist_ok=True)
                self._copy_article_file(journal_article.metadata.id, filevalue, filedir)

    def _generate_static_site_journal_issue(self,
                                            outdir: Path,
                                            journal_issue: JournalIssue,
                                            parent_context: ChainMap):
        template = self._env.get_template(journal_issue.template())
        context = parent_context.new_child(dict(breadcrumbs=[*parent_context['breadcrumbs'], journal_issue],
                                                current=journal_issue,
                                                parent_path=f'{parent_context['parent_path']}/{journal_issue.directory()}')) # Note: same menu as volume
        Path(outdir, parent_context['parent_path'].removeprefix('/'), journal_issue.directory()).mkdir(exist_ok=True)
        template.stream(context).dump(f'{outdir}{journal_issue.path(context['breadcrumbs'])}')
        for journal_article in journal_issue.journal_articles:
            self._generate_static_site_journal_article(outdir, journal_article, context)

    def _generate_static_site_journal_volume(self,
                                             outdir: Path,
                                             journal_volume: JournalVolume,
                                             parent_context: ChainMap):
        template = self._env.get_template(journal_volume.template())
        context = parent_context.new_child(dict(breadcrumbs=[*parent_context['breadcrumbs'], journal_volume],
                                                current=journal_volume,
                                                parent_path=f'{parent_context['parent_path']}/{journal_volume.directory()}',
                                                menu=[*parent_context['menu'], journal_volume.journal_issues]))
        Path(outdir, parent_context['parent_path'].removeprefix('/'), journal_volume.directory()).mkdir(exist_ok=True)
        template.stream(context).dump(f'{outdir}{journal_volume.path(context['breadcrumbs'])}')
        for journal_issue in journal_volume.journal_issues:
            self._generate_static_site_journal_issue(outdir, journal_issue, context)

    def _generate_static_site_publisher(self,
                                        outdir: Path,
                                        publisher: Publisher,
                                        parent_context: ChainMap):
        template = self._env.get_template(publisher.template())
        context = parent_context.new_child(dict(breadcrumbs=[*parent_context['breadcrumbs'], publisher],
                                                current=publisher,
                                                parent_path=f'{parent_context['parent_path']}/{publisher.directory()}',
                                                menu=[*parent_context['menu'], publisher.journals]))
        pubdir = Path(outdir, parent_context['parent_path'].removeprefix('/'), publisher.directory())
        pubdir.mkdir(exist_ok=True)
        template.stream(context).dump(f'{outdir}{publisher.path(context['breadcrumbs'])}')
        if publisher.logo is not None and publisher.logo.startswith('file::'):
            shutil.copy2(publisher.logo.removeprefix('file::'), pubdir)
        for journal in publisher.journals:
            self._generate_static_site_journal(outdir, journal, context)

    def _load_configuration(self, path: Path):
        loaded_obj = self._load_json_or_yaml(path)
        self._config = GlutinatorConfigModel(**loaded_obj)

    def _load_json_or_yaml(self, path: Path) -> Any:
        with path.open('r') as fin:
            if path.suffix == '.json':
                return json.load(fin)
            else:
                return yaml.safe_load(fin)
