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

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, RootModel


class Type(Enum):
    ARTICLE = 'article'
    ARTICLE_JOURNAL = 'article-journal'
    ARTICLE_MAGAZINE = 'article-magazine'
    ARTICLE_NEWSPAPER = 'article-newspaper'
    BILL = 'bill'
    BOOK = 'book'
    BROADCAST = 'broadcast'
    CHAPTER = 'chapter'
    CLASSIC = 'classic'
    COLLECTION = 'collection'
    DATASET = 'dataset'
    DOCUMENT = 'document'
    ENTRY = 'entry'
    ENTRY_DICTIONARY = 'entry-dictionary'
    ENTRY_ENCYCLOPEDIA = 'entry-encyclopedia'
    EVENT = 'event'
    FIGURE = 'figure'
    GRAPHIC = 'graphic'
    HEARING = 'hearing'
    INTERVIEW = 'interview'
    LEGAL_CASE = 'legal_case'
    LEGISLATION = 'legislation'
    MANUSCRIPT = 'manuscript'
    MAP = 'map'
    MOTION_PICTURE = 'motion_picture'
    MUSICAL_SCORE = 'musical_score'
    PAMPHLET = 'pamphlet'
    PAPER_CONFERENCE = 'paper-conference'
    PATENT = 'patent'
    PERFORMANCE = 'performance'
    PERIODICAL = 'periodical'
    PERSONAL_COMMUNICATION = 'personal_communication'
    POST = 'post'
    POST_WEBLOG = 'post-weblog'
    REGULATION = 'regulation'
    REPORT = 'report'
    REVIEW = 'review'
    REVIEW_BOOK = 'review-book'
    SOFTWARE = 'software'
    SONG = 'song'
    SPEECH = 'speech'
    STANDARD = 'standard'
    THESIS = 'thesis'
    TREATY = 'treaty'
    WEBPAGE = 'webpage'


class NameVariable1(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    family: Optional[str] = None
    given: Optional[str] = None
    dropping_particle: Optional[str] = Field(None, alias='dropping-particle')
    non_dropping_particle: Optional[str] = Field(None, alias='non-dropping-particle')
    suffix: Optional[str] = None
    comma_suffix: Optional[Union[str, float, bool]] = Field(None, alias='comma-suffix')
    static_ordering: Optional[Union[str, float, bool]] = Field(
        None, alias='static-ordering'
    )
    literal: Optional[str] = None
    parse_names: Optional[Union[str, float, bool]] = Field(None, alias='parse-names')


class DateVariable1(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    date_parts: Optional[List[List[Union[str, float]]]] = Field(
        None, alias='date-parts', max_length=2, min_length=1
    )
    season: Optional[Union[str, float]] = None
    circa: Optional[Union[str, float, bool]] = None
    literal: Optional[str] = None
    raw: Optional[str] = None


class ModelItem(BaseModel):
    model_config = ConfigDict(
        extra='forbid',
    )
    type: Type
    id: Union[str, float]
    citation_key: Optional[str] = Field(None, alias='citation-key')
    categories: Optional[List[str]] = None
    language: Optional[str] = None
    journalAbbreviation: Optional[str] = None
    shortTitle: Optional[str] = None
    author: Optional[List[NameVariable1]] = None
    chair: Optional[List[NameVariable1]] = None
    collection_editor: Optional[List[NameVariable1]] = Field(
        None, alias='collection-editor'
    )
    compiler: Optional[List[NameVariable1]] = None
    composer: Optional[List[NameVariable1]] = None
    container_author: Optional[List[NameVariable1]] = Field(
        None, alias='container-author'
    )
    contributor: Optional[List[NameVariable1]] = None
    curator: Optional[List[NameVariable1]] = None
    director: Optional[List[NameVariable1]] = None
    editor: Optional[List[NameVariable1]] = None
    editorial_director: Optional[List[NameVariable1]] = Field(
        None, alias='editorial-director'
    )
    executive_producer: Optional[List[NameVariable1]] = Field(
        None, alias='executive-producer'
    )
    guest: Optional[List[NameVariable1]] = None
    host: Optional[List[NameVariable1]] = None
    interviewer: Optional[List[NameVariable1]] = None
    illustrator: Optional[List[NameVariable1]] = None
    narrator: Optional[List[NameVariable1]] = None
    organizer: Optional[List[NameVariable1]] = None
    original_author: Optional[List[NameVariable1]] = Field(
        None, alias='original-author'
    )
    performer: Optional[List[NameVariable1]] = None
    producer: Optional[List[NameVariable1]] = None
    recipient: Optional[List[NameVariable1]] = None
    reviewed_author: Optional[List[NameVariable1]] = Field(
        None, alias='reviewed-author'
    )
    script_writer: Optional[List[NameVariable1]] = Field(None, alias='script-writer')
    series_creator: Optional[List[NameVariable1]] = Field(None, alias='series-creator')
    translator: Optional[List[NameVariable1]] = None
    accessed: Optional[DateVariable1] = Field(
        None,
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    available_date: Optional[DateVariable1] = Field(
        None,
        alias='available-date',
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    event_date: Optional[DateVariable1] = Field(
        None,
        alias='event-date',
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    issued: Optional[DateVariable1] = Field(
        None,
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    original_date: Optional[DateVariable1] = Field(
        None,
        alias='original-date',
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    submitted: Optional[DateVariable1] = Field(
        None,
        description='The CSL input model supports two different date representations: an EDTF string (preferred), and a more structured alternative.',
        title='Date content model.',
    )
    abstract: Optional[str] = None
    annote: Optional[str] = None
    archive: Optional[str] = None
    archive_collection: Optional[str] = None
    archive_location: Optional[str] = None
    archive_place: Optional[str] = Field(None, alias='archive-place')
    authority: Optional[str] = None
    call_number: Optional[str] = Field(None, alias='call-number')
    chapter_number: Optional[Union[str, float]] = Field(None, alias='chapter-number')
    citation_number: Optional[Union[str, float]] = Field(None, alias='citation-number')
    citation_label: Optional[str] = Field(None, alias='citation-label')
    collection_number: Optional[Union[str, float]] = Field(
        None, alias='collection-number'
    )
    collection_title: Optional[str] = Field(None, alias='collection-title')
    container_title: Optional[str] = Field(None, alias='container-title')
    container_title_short: Optional[str] = Field(None, alias='container-title-short')
    dimensions: Optional[str] = None
    division: Optional[str] = None
    DOI: Optional[str] = None
    edition: Optional[Union[str, float]] = None
    event: Optional[str] = Field(
        None,
        description="[Deprecated - use 'event-title' instead. Will be removed in 1.1]",
    )
    event_title: Optional[str] = Field(None, alias='event-title')
    event_place: Optional[str] = Field(None, alias='event-place')
    first_reference_note_number: Optional[Union[str, float]] = Field(
        None, alias='first-reference-note-number'
    )
    genre: Optional[str] = None
    ISBN: Optional[str] = None
    ISSN: Optional[str] = None
    issue: Optional[Union[str, float]] = None
    jurisdiction: Optional[str] = None
    keyword: Optional[str] = None
    locator: Optional[Union[str, float]] = None
    medium: Optional[str] = None
    note: Optional[str] = None
    number: Optional[Union[str, float]] = None
    number_of_pages: Optional[Union[str, float]] = Field(None, alias='number-of-pages')
    number_of_volumes: Optional[Union[str, float]] = Field(
        None, alias='number-of-volumes'
    )
    original_publisher: Optional[str] = Field(None, alias='original-publisher')
    original_publisher_place: Optional[str] = Field(
        None, alias='original-publisher-place'
    )
    original_title: Optional[str] = Field(None, alias='original-title')
    page: Optional[Union[str, float]] = None
    page_first: Optional[Union[str, float]] = Field(None, alias='page-first')
    part: Optional[Union[str, float]] = None
    part_title: Optional[str] = Field(None, alias='part-title')
    PMCID: Optional[str] = None
    PMID: Optional[str] = None
    printing: Optional[Union[str, float]] = None
    publisher: Optional[str] = None
    publisher_place: Optional[str] = Field(None, alias='publisher-place')
    references: Optional[str] = None
    reviewed_genre: Optional[str] = Field(None, alias='reviewed-genre')
    reviewed_title: Optional[str] = Field(None, alias='reviewed-title')
    scale: Optional[str] = None
    section: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    supplement: Optional[Union[str, float]] = None
    title: Optional[str] = None
    title_short: Optional[str] = Field(None, alias='title-short')
    URL: Optional[str] = None
    version: Optional[str] = None
    volume: Optional[Union[str, float]] = None
    volume_title: Optional[str] = Field(None, alias='volume-title')
    volume_title_short: Optional[str] = Field(None, alias='volume-title-short')
    year_suffix: Optional[str] = Field(None, alias='year-suffix')
    custom: Optional[Dict[str, Any]] = Field(
        None,
        description='Used to store additional information that does not have a designated CSL JSON field. The custom field is preferred over the note field for storing custom data, particularly for storing key-value pairs, as the note field is used for user annotations in annotated bibliography styles.',
        examples=[
            {'short_id': 'xyz', 'other-ids': ['alternative-id']},
            {'metadata-double-checked': True},
        ],
        title='Custom key-value pairs.',
    )


class Model(RootModel[List[ModelItem]]):
    root: List[ModelItem] = Field(..., description='JSON schema for CSL input data')
