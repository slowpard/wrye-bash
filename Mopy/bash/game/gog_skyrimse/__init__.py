# -*- coding: utf-8 -*-
#
# GPL License and Copyright Notice ============================================
#  This file is part of Wrye Bash.
#
#  Wrye Bash is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation, either version 3
#  of the License, or (at your option) any later version.
#
#  Wrye Bash is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with Wrye Bash.  If not, see <https://www.gnu.org/licenses/>.
#
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2022 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================
"""GameInfo override for the GOG version of Skyrim SE."""
from ..skyrimse import SkyrimSEGameInfo
from ..gog_game import GOGMixin

class GOGSkyrimSEGameInfo(GOGMixin, SkyrimSEGameInfo):
    displayName = 'Skyrim Special Edition (GOG)'
    fsName = 'Skyrim Special Edition GOG'
    my_games_name = 'Skyrim Special Edition GOG'
    appdata_name = 'Skyrim Special Edition GOG'
    registry_keys = [(r'GOG.com\Games\1711230643', 'path'),
                     (r'GOG.com\Games\1162721350', 'path')]

GAME_TYPE = GOGSkyrimSEGameInfo