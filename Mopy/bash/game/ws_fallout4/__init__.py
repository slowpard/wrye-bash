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
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2021 Wrye Bash Team
#  https://github.com/wrye-bash
#
# =============================================================================
"""GameInfo override for the Windows Store version of Fallout 4."""

from ..fallout4 import Fallout4GameInfo

class WSFallout4GameInfo(Fallout4GameInfo):
    displayName = u'Fallout 4 (WS)'
    fsName = u'Fallout 4 MS'
    appdata_name = u'Fallout 4 MS'
    my_games_name = u'Fallout 4 MS'
    regInstallKeys = ()
    game_detect_files = Fallout4GameInfo.game_detect_files + [u'appxmanifest.xml']
    game_detect_excludes = []

    class Ws(Fallout4GameInfo.Ws):
        publisher_name = u'Bethesda'
        win_store_name = u'BethesdaSoftworks.Fallout4-PC'

GAME_TYPE = WSFallout4GameInfo
