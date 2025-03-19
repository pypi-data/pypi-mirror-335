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

from enum import Enum
from typing import Generic, List, Literal, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

from .csl_data import ModelItem

ISSN_PATTERN_STR = r'^[0-9]{4}-[0-9]{3}[0-9X]$'

class LicenseType(str, Enum):
    CC_BY_4_0 = 'cc_by_4_0'
    CC_BY_NC_ND_4_0 = 'cc_by_nc_nd_4_0'

class Kind(str, Enum):
    PUBLISHER = 'publisher'
    JOURNAL = 'journal'
    JOURNAL_VOLUME = 'journal_volume'
    JOURNAL_ISSUE = 'journal_issue'

class PublisherMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal[Kind.PUBLISHER]
    id: str
    name: str
    alternate_names: Optional[List[str]] = None
    variant_names: Optional[List[str]] = None

class JournalMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal[Kind.JOURNAL]
    id: str
    name: str
    alternate_names: Optional[List[str]] = None
    variant_names: Optional[List[str]] = None
    issn: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR)
    eissn: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR)
    issn_l: Optional[str] = Field(None, pattern=ISSN_PATTERN_STR)

class JournalVolumeMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal[Kind.JOURNAL_VOLUME]
    id: str
    name: str
    short_name: str

class JournalIssueMetadata(BaseModel):
    model_config = ConfigDict(extra='forbid')
    kind: Literal[Kind.JOURNAL_ISSUE]
    id: str
    name: str
    short_name: str
    publication_date: Optional[str] = None

ItemMetadata = TypeVar('ItemMetadata', bound=BaseModel)

class Item(BaseModel, Generic[ItemMetadata]):
    model_config = ConfigDict(extra='forbid')
    metadata: ItemMetadata

    def directory(self):
        return f'{self.metadata.id}'

    def file(self):
        return 'index.html'

    def path(self, breadcrumbs) -> str:
        # See also macros.html path(...)
        return f'{'/'.join(x.directory() for x in breadcrumbs)}/{self.file()}'

    def template(self) -> str:
        raise NotImplementedError('Item::template')

class JournalArticle(Item[ModelItem]):
    model_config = ConfigDict(extra='forbid')
    license_type: Optional[LicenseType] = None

    def template(self):
        return 'article.html'

class JournalIssue(Item[JournalIssueMetadata]):
    journal_articles: Optional[List[JournalArticle]] = list()

    def template(self):
        return 'issue.html'

class JournalVolume(Item[JournalVolumeMetadata]):
    journal_issues: Optional[List[JournalIssue]] = list()

    def template(self):
        return 'volume.html'

class Journal(Item[JournalMetadata]):
    journal_volumes: Optional[List[JournalVolume]] = list()
    logo: Optional[str] = None

    def template(self):
        return 'journal.html'

class Publisher(Item[PublisherMetadata]):
    journals: Optional[List[Journal]] = list()
    logo: Optional[str] = None

    def template(self):
        return 'publisher.html'

class Root(Item[Literal[None]]):
    publishers: Optional[List[Publisher]] = list()

    def directory(self):
        return ''

    def template(self):
        return 'home.html'
