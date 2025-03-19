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

import os
from pathlib import Path
from typing import Optional

class AuAdapter(object):

    def __init__(self, root: Path):
        super().__init__()
        self._root = root

    def urls(self):
        for dirpath, dirnames, filenames in os.walk(self._root):
            dirnames.sort()
            filenames.sort()
            for name in filenames:
                if name == 'current':
                    path = Path(dirpath, name)
                    if path.parent.name == '#content':
                        candidate = path.parent.parent
                        parts = candidate.relative_to(self._root).parts
                        yield f'{parts[1]}://{parts[0]}/{"/".join(parts[2:])}'

    def path(self, url: str) -> Optional[Path]:
        actual, archsep, archpath = url.partition('!/')
        first, _, rest = actual.partition('://')
        parts = rest.split('/')
        candidate = Path(self._root, parts[0], first, *parts[1:], '#content', 'current')
        if archsep:
            candidate = Path(candidate.parent, 'current!', archpath)
        return candidate
