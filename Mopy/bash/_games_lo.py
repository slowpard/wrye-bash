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
#  Wrye Bash copyright (C) 2005-2009 Wrye, 2010-2024 Wrye Bash Team
#  https://github.com/wrye-bash
#  Mopy/bash/games.py copyright (C) 2016 Utumno: Original design
#
# =============================================================================
"""Load order handling backend featuring a LoGame hierarchy implementing base
load order handling, and _LoFile hierarchy for reading and writing load order
files. Imported in the game package for defining specific LoGame overrides (to
keep this file readable and avoid the need of a factory), and in load_order.py,
where it is initialized and used to implement the load order API."""
##: multiple backups? fixes can happen in rapid succession, so preserving
# several older files in a directory would be useful (maybe limit to some
# number, e.g. 5 older versions)
from __future__ import annotations

__author__ = 'Utumno'

import re
import time
from collections import defaultdict
from functools import partial

from . import bass, bolt, env, exception
from .bolt import AFile, FName, Path, dict_sort
from .ini_files import get_ini_type_and_encoding

# Typing
LoTuple = tuple[FName, ...]
LoList = LoTuple | list[FName] | None
_ParsedLo = tuple[list[FName], list[FName]]

class _LoFile(AFile):
    """A file holding load order information (plugins.txt/loadorder.txt but
    also ini files for INIGame). We need to be careful in case sensitive
    file systems and backup could use more work but that's a proud beta."""
    def __init__(self, star, path, *args, **kwargs):
        self._star = star
        super().__init__(self._resolve_case_ambiguity(path), *args, **kwargs)

    def parse_modfile(self, mod_infos, *,
            __re_plugins_txt_comment=re.compile(b'^#.*')) -> _ParsedLo:
        """Parse loadorder.txt and plugins.txt files with or without stars.

        Return two lists which are identical except when _star is True,
        whereupon the second list is the load order while the first the
        active plugins. In all other cases use the first list, which is
        either the list of active mods (when parsing plugins.txt) or the
        load order (when parsing loadorder.txt)
        :type mod_infos: bosh.ModInfos"""
        with self.abs_path.open('rb') as ins:
            #--Load Files
            active, modnames = [], []
            for line in ins:
                # Oblivion/Skyrim saves the plugins.txt file in cp1252 format
                # It wont accept filenames in any other encoding
                modname = __re_plugins_txt_comment.sub(b'', line.strip())
                if not modname: continue
                # use raw strings below
                is_active_ = not self._star or modname.startswith(b'*')
                if self._star and is_active_: modname = modname[1:]
                try:
                    test = bolt.decoder(modname, encoding=u'cp1252')
                except UnicodeError:
                    bolt.deprint(f'{modname!r} failed to properly decode')
                    continue
                mod_g_path = FName(test)
                if mod_g_path.fn_ext == '.ghost':  # Vortex keeps the .ghost extension!
                    mod_g_path = mod_g_path.fn_body
                if mod_g_path not in mod_infos:  # TODO(ut): is this really needed??
                    # The automatic encoding detector could have returned
                    # an encoding it actually wasn't.  Luckily, we
                    # have a way to double check: modInfos.data
                    for encoding in bolt.encodingOrder:
                        try: # FName does not accept bytes
                            test2 = str(modname, encoding)
                            if test2 in mod_infos:
                                mod_g_path = FName(test2)
                                break
                        except UnicodeError:
                            pass
                modnames.append(mod_g_path)
                if is_active_: active.append(mod_g_path)
        self.do_update() # update the cache info
        return active, modnames

    @staticmethod
    def _resolve_case_ambiguity(lo_file_path: Path):
        """Third-party tools like LOOT do not all use the same case for
        plugins.txt and loadorder.txt. This method returns the canonical
        path for the specified load order file path and cleans up multiple
        load order files in the same dir by using the one with the newest
        mtime and deleting the older ones."""
        lo_dir, lo_fname = lo_file_path.head, lo_file_path.stail
        matching_paths = [lo_dir.join(t_fname) for t_fname in lo_dir.ilist()
                          if t_fname == lo_fname]
        if len(matching_paths) > 1:
            matching_paths.sort(key=lambda tp: tp.mtime, reverse=True)
            filenames = [p.stail for p in matching_paths]
            bolt.deprint(f'Resolving ambiguous {lo_fname} case (found '
                         f'{filenames}) to newest file ({filenames[0]})')
            for p in matching_paths[1:]:
                try:
                    p.remove()
                except OSError:
                    bolt.deprint(f'Failed to remove {p} while resolving '
                                 f'{lo_fname} ambiguous case', traceback=True)
            return matching_paths[0]
        return matching_paths[0] if matching_paths else lo_file_path

    def write_modfile(self, lord, active):
        try:
            self.__write_plugins(lord, active)
        except OSError:
            env.clear_read_only(self.abs_path)
            self.__write_plugins(lord, active)

    def __write_plugins(self, lord, active):
        active_set = frozenset(active)
        with self.abs_path.open('wb') as out:
            for mod in (self._star and lord) or active:
                # Ok, this seems to work for Oblivion, but not for Skyrim,
                # which seems to refuse to have any non-cp1252 named file in
                # plugins.txt. Even activating through the SkyrimLauncher
                # doesn't work.
                try:
                    star = f'{"*" if self._star and mod in active_set else ""}'
                    out.write(f'{star}{mod}\r\n'.encode('cp1252'))
                except UnicodeEncodeError:
                    bolt.deprint(f'{mod} failed to properly encode and was '
                                 f'skipped for inclusion in load order file')

    def upd_on_swap(self, old_dir, new_dir):
        pl_path = self.abs_path
        # Save plugins.txt inside the old (saves) directory
        try: self.fs_copy(self._resolve_case_ambiguity(
            old_dir.join(pl_path.stail)))
        except FileNotFoundError: pass # no plugins.txt to save
        # Move the new plugins.txt here for use
        move = self._resolve_case_ambiguity(new_dir.join(pl_path.stail))
        try: # copy will not change mtime, bad
            move.copyTo(pl_path, set_time=time.time())
            return True
        except FileNotFoundError:
            return False

    def create_backup(self):
        pl_path = self.abs_path
        try:
            self.fs_copy(pl_path.backup)
        except FileNotFoundError:
            bolt.deprint(f'Tried to back up {pl_path}, but it did not exist')
        except OSError:
            bolt.deprint(f'Failed to back up {pl_path}', traceback=True)

class FixInfo(object):
    """Encapsulate info on load order and active lists fixups."""
    def __init__(self):
        self.lo_removed = set()
        self.lo_added = set()
        self.lo_duplicates = set()
        self.lo_reordered = ([], [])
        # active mods corrections
        self.act_removed = set()
        self.act_added = set()
        self.act_duplicates = set()
        self.act_reordered = ()
        self.act_order_differs_from_load_order = u''
        self.master_not_active = False
        self.missing_must_be_active = []
        self.selectedExtra = []
        self.act_header = u''

    def lo_changed(self):
        return bool(self.lo_removed or self.lo_added or self.lo_duplicates or
                    any(self.lo_reordered))

    def act_changed(self):
        return bool(
            self.act_removed or self.act_added or self.act_duplicates or
            self.act_reordered or self.act_order_differs_from_load_order or
            self.master_not_active or self.missing_must_be_active or
            self.selectedExtra)

    def lo_deprint(self):
        self._warn_lo()
        self._warn_active()
        if rem := (self.lo_removed | self.act_removed):
            from .bosh import modInfos
            modInfos.warn_missing_lo_act = rem

    def _warn_lo(self):
        if not self.lo_changed(): return
        added = _pl(self.lo_added) or u'None'
        removed = _pl(self.lo_removed) or u'None'
        duplicates = f'lo_duplicates({_pl(self.lo_duplicates)}), ' \
            if self.lo_duplicates else u''
        reordered = u'(No)' if not any(self.lo_reordered) else _pl(
            self.lo_reordered[0], u'from:\n', joint=u'\n') + _pl(
            self.lo_reordered[1], u'\nto:\n', joint=u'\n')
        bolt.deprint(f'Fixed Load Order: {added=}, {removed=}, '
                     f'{duplicates=}, reordered {reordered}')

    def _warn_active(self):
        if not self.act_header: return
        msg = [self.act_header]
        if self.act_removed:
            msg.append('Active list contains mods not present in Data '
                       'directory, invalid and/or corrupted:')
            msg.append(', '.join(self.act_removed))
        if self.master_not_active:
            msg.append(f'{self.master_not_active} not present in active mods')
        for path in self.missing_must_be_active:
            msg.append(f'{path} not present in active list while present in '
                       f'Data folder')
        msg += self.act_order_differs_from_load_order
        if self.selectedExtra:
            msg.append('Active list contains more plugins than allowed - the '
                       'following plugins will be deactivated:')
            msg.append(', '.join(self.selectedExtra))
        if self.act_duplicates:
            msg.append('Removed duplicate entries from active list:')
            msg.append(', '.join(self.act_duplicates))
        if len(self.act_reordered) == 2: # from, to
            msg.append('Reordered active plugins with fixed order from:')
            msg.extend(self.act_reordered[0])
            msg.append('to:')
            msg.extend(self.act_reordered[1])
        bolt.deprint('\n'.join(msg))

class LoGame:
    """API for setting, getting and validating the active plugins and the
    load order (of all plugins) according to the game engine (in principle)."""
    must_be_active_if_present: LoTuple = ()
    max_espms = 255
    max_esls = 0
    _star = False # whether plugins.txt uses a star to denote an active plugin

    def __init__(self, mod_infos, plugins_txt_path: Path, *,
                 plugins_txt_type=_LoFile, **kwargs):
        """:type mod_infos: bosh.ModInfos"""
        self._plugins_txt = plugins_txt_type(self._star, plugins_txt_path)
        self.mod_infos = mod_infos # this is bosh.ModInfos, must be up to date
        self.master_path = mod_infos._master_esm
        if self.master_path in self.must_be_active_if_present:
            raise SyntaxError("Don't include the game master in "
                              "must_be_active_if_present!")

    # API ---------------------------------------------------------------------
    def get_load_order(self, cached_load_order: LoList,
            cached_active_ordered: LoList, fix_lo) -> tuple[LoTuple, LoTuple]:
        """Get and validate current load order and active plugins information.

        Meant to fetch at once both load order and active plugins
        information as validation usually depends on both. If the load order
        read is invalid (messed up loadorder.txt, game's master redated out
        of order, etc) it will attempt fixing and saving them before returning.
        The caller is responsible for passing a valid cached value in. If you
        pass a cached value for either parameter this value will be returned
        unchanged, possibly validating the other one based on stale data.
        NOTE: modInfos must exist and be up to date for validation."""
        if cached_load_order is not None and cached_active_ordered is not None:
            raise ValueError('get_load_order called with both cached values')
        lo, active = self._cached_or_fetch(cached_load_order,
                                           cached_active_ordered)
        # for timestamps we use modInfos so we should not get an invalid
        # load order (except redated master). For text based games however
        # the fetched order could be in whatever state, so get this fixed
        if cached_load_order is None: ##: if not should we assert is valid ?
            self._fix_load_order(lo, fix_lo=fix_lo)
        # having a valid load order we may fix active too if we fetched them
        fixed_active = cached_active_ordered is None and \
            self._fix_active_plugins(active, lo, fix_lo, on_disc=True)
        self._save_fixed_load_order(fix_lo, fixed_active, lo, active)
        return tuple(lo), tuple(active)

    def _cached_or_fetch(self, cached_load_order, cached_active):
        # we need to override this bit for AsteriskGame to parse the file once
        if cached_active is None: # first get active plugins
            cached_active = self._fetch_active_plugins()
        # we need active plugins fetched to check for desync in load order
        if cached_load_order is None:
            cached_load_order = self._fetch_load_order(cached_load_order,
                                                       cached_active)
        return list(cached_load_order), list(cached_active)

    def _save_fixed_load_order(self, fix_lo, fixed_active, lo, active):
        if fix_lo.lo_changed():
            self._backup_load_order()
            self._persist_load_order(lo, None) # active is not used here

    def set_load_order(self, lord, active, previous_lord=None,
                       previous_active=None, fix_lo=None):
        """Set the load order and/or active plugins (or just validate if
        previous_* is None). The different way each game handles this and how
        it modifies common data structures necessitate that info on previous
        (cached) state is passed in, usually for both active plugins and
        load order. For instance, in the case of asterisk games, plugins.txt
        is the common structure for defining both the global load order and
        which plugins are active. The logic is as follows:
        - at least one of `lord` or `active` must be not None, otherwise no
        much use in calling this function anyway - raise ValueError if not.
        - if lord is not None pass it through _fix_load_order. That might
        change it. If, after fixing it, it is the same as `previous_lord`
        then we won't do anything regarding it (no mtime, loadorder.txt etc).
        - if load order is actually being set we need info on active plugins.
        In case active is None we do need to have previous_active - otherwise
        a ValueError is raised.
        - otherwise we determine if active needs change (for TESIV if
        plugins were deleted we need to rewrite plugins.txt - for asterisk
        games we always need to rewrite the plugins.txt for any load order
        change, as it is stored there)
        - we then validate active plugins against lord or previous_lord - if
        we were not setting the load order we need previous_lord here otherwise
        a ValueError is raised.
        By now we should have a lord and active lists to set, if we are not in
        dry run mode.
        :returns the (possibly fixed) lord and active lists
        """
        if lord is active is None:
            raise ValueError('Load order or active must be not None')
        dry_run = previous_lord is previous_active is None
        if quiet := fix_lo is None: fix_lo = FixInfo() # will be discarded
        setting_lo = lord is not None
        if setting_lo:
            # fix the load order - lord is modified in place, hence test below
            self._fix_load_order(lord, fix_lo, not quiet)
            setting_lo = previous_lord != lord
        setting_active = active is not None
        if setting_lo and not setting_active:
            # changing load order - must test if active plugins must change too
            if previous_active is None: # active is None
                raise ValueError(
                    'You must pass info on active when setting load order')
            setting_active = previous_lord is None # we must check active
            if not setting_active: # does active need change due to lo changes?
                prev = set(previous_lord)
                new = set(lord)
                dltd = prev - new
                common = prev & new
                reordered = any(x != y for x, y in
                                zip((x for x in previous_lord if x in common),
                                    (x for x in lord if x in common)))
                setting_active = self._must_update_active(dltd, reordered)
            if setting_active: active = list(previous_active) # active was None
        if setting_active:
            if lord is previous_lord is None:
                raise ValueError(
                    u'You need to pass a load order in to set active plugins')
            # a load order is needed for all games to validate active against
            test = lord if setting_lo else previous_lord
            self._fix_active_plugins(active, test, fix_lo, on_disc=False)
        lord = lord if setting_lo else previous_lord
        active = active if setting_active else previous_active
        if lord is None or active is None: # sanity check
            raise Exception('Returned load order and active must be not None')
        if not dry_run: # else just return the (possibly fixed) lists
            self._persist_if_changed(active, lord, previous_active,
                                     previous_lord)
        return lord, active # return what we set or was previously set

    def pinned_mods(self):
        """Returns a set of plugin names that may not be reordered by the
        user."""
        return {self.master_path}

    # Conflicts - only for timestamp games
    def has_load_order_conflict(self, mod_name): return False
    def has_load_order_conflict_active(self, mod_name, active): return False

    @classmethod
    def _must_update_active(cls, deleted_plugins, reordered):
        raise NotImplementedError

    def request_cache_update(self, cached_load_order, cached_active): # one use
        """Return a pair of values for passing to get_load_order."""
        update_act = cached_active is None or self._plugins_txt.do_update()
        active = None if update_act else cached_active
        return None, active # Timestamp just calculate load order from modInfos

    # Handle active plugins file (always exists)
    def swap(self, old_dir, new_dir):
        """Save current plugins into oldPath directory and load plugins from
        newPath directory (if present)."""
        return self._plugins_txt.upd_on_swap(old_dir, new_dir)

    def _backup_active_plugins(self):
        """This method should make a backup of whatever file is storing the
        active plugins list."""
        self._plugins_txt.create_backup()

    def _fetch_active_plugins(self):
        try:
            active, _lo = self._plugins_txt.parse_modfile(self.mod_infos)
            return active
        except FileNotFoundError:
            return []

    def _persist_active_plugins(self, active, lord):
        self._write_plugins_txt(active, active)

    def _write_plugins_txt(self, lord, active):
        self._plugins_txt.write_modfile(lord, active)
        self._plugins_txt.do_update()

    def get_lo_files(self) -> list[Path]:
        """Returns the paths of the files used by this game for storing load
        order information."""
        return [self._plugins_txt.abs_path] # base case

    def _backup_load_order(self):
        pass # timestamps, no file to backup

    # ABSTRACT ----------------------------------------------------------------
    def _fetch_load_order(self, cached_load_order: LoTuple | None,
                          cached_active: LoTuple):
        raise NotImplementedError

    def _persist_load_order(self, lord, active):
        """Persist the fixed lord to disk - will break conflicts for
        timestamp games."""
        raise NotImplementedError(f'{type(self)} does not define '
                                  f'_persist_load_order')

    def _persist_if_changed(self, active, lord, previous_active,
                            previous_lord):
        # Override for fallout4 to write the file once and oblivion to save
        # active only if needed. Both active and lord must not be None.
        raise NotImplementedError

    # VALIDATION --------------------------------------------------------------
    def _fix_load_order(self, lord: list[FName], fix_lo, _mtime_order=True):
        """Fix inconsistencies between given loadorder and actually installed
        mod files as well as impossible load orders. We need a refreshed
        bosh.modInfos reflecting the contents of Data/.

        Called in get_load_order() to fix a newly fetched LO and in
        set_load_order() to check if a load order passed in is valid. Needs
        rethinking as saving load and active should be an atomic operation."""
        old_lord = lord[:]
        # game's master might be out of place (if using timestamps for load
        # ordering or a manually edited loadorder.txt) so move it up
        master_name = self.master_path
        # Tracks if fix_lo.lo_reordered needs updating
        lo_order_changed = any(fix_lo.lo_reordered)
        cached_minfs = self.mod_infos
        try:
            mdex = lord.index(master_name)
            if mdex > 0:
                bolt.deprint(f'{master_name} has index {mdex} (must be 0)')
                lord.remove(master_name)
                lord.insert(0, master_name)
                lo_order_changed = True
        except ValueError:
            if master_name not in cached_minfs:
                raise exception.BoltError(
                    f'{master_name} is missing or corrupted')
            fix_lo.lo_added = {master_name}
        # below do not apply to timestamp method (except if we are passed in a
        # saved load order for validation or to restore)
        loadorder_set = set(lord)
        mods_set = set(cached_minfs)
        fix_lo.lo_removed = loadorder_set - mods_set # may remove corrupted mods
        # present in text file, we are supposed to take care of that
        fix_lo.lo_added |= mods_set - loadorder_set
        # Remove non existent plugins from load order
        lord[:] = [x for x in lord if x not in fix_lo.lo_removed]
        ol = lord[:] # take a snapshot used in checking master block reordering
        for mod in fix_lo.lo_added: # Append new plugins to load order
            if mod == master_name:
                lord.insert(0, master_name)
                bolt.deprint(f'{master_name} inserted to Load order')
            else: # append all to the end, even esms, will be reordered below
                lord.append(mod)
        # See if any esm files are loaded below an esp and reorder as necessary
        lord.sort(key=lambda m: not cached_minfs[m].in_master_block())
        # check if any of the existing mods were moved in/out the master block
        lo_order_changed |= ol != [x for x in lord if x not in fix_lo.lo_added]
        fix_lo.lo_duplicates = self._check_for_duplicates(lord)
        # end textfile get
        lo_order_changed |= self._order_fixed(lord)
        if lo_order_changed:
            fix_lo.lo_reordered = old_lord, lord

    def _fix_active_plugins(self, acti, lord, fix_active, on_disc):
        # filter plugins not present in modInfos - this will disable
        # corrupted too! Preserve acti order
        # Throw out files that aren't on disk as well as .esu files, which must
        # never be active
        cached_minfs = self.mod_infos
        acti_filtered = [x for x in acti if x in cached_minfs
                         and x.fn_ext != u'.esu']
        # Use sets to avoid O(n) lookups due to lists
        acti_filtered_set = set(acti_filtered)
        lord_set = set(lord)
        fix_active.act_removed = set(acti) - acti_filtered_set
        if self.master_path not in acti_filtered_set:
            acti_filtered.insert(0, self.master_path)
            acti_filtered_set.add(self.master_path)
            fix_active.master_not_active = self.master_path
        for path in self.must_be_active_if_present:
            if path in lord_set and path not in acti_filtered_set:
                fix_active.missing_must_be_active.append(path)
        # order - affects which mods are chopped off if > 255 (the ones that
        # load last) - won't trigger saving but for Skyrim
        fix_active.act_order_differs_from_load_order += \
            self._check_active_order(acti_filtered, lord)
        for index_of_first_esp, act in enumerate(acti_filtered):
            if not cached_minfs[act].in_master_block(): break
        else: # no masters *not even the game master* - previous behavior
            ##: disallow this for games that allow deactivating the master esm?
            index_of_first_esp = 0
        # insert after the last master
        acti_filtered[index_of_first_esp:index_of_first_esp] = (
            fix_active.missing_must_be_active)
        # Check for duplicates - NOTE: this modifies acti_filtered!
        fix_active.act_duplicates = self._check_for_duplicates(acti_filtered)
        # check if we have more than 256 active mods
        drop_espms, drop_esls = self.check_active_limit(acti_filtered)
        disable = drop_espms | drop_esls
        # update acti in place - this must always be done, since acti may
        # contain files that are no longer on disk (i.e. not in acti_filtered)
        acti[:] = [x for x in acti_filtered if x not in disable]
        if disable: # chop off extra
            cached_minfs.selectedExtra = fix_active.selectedExtra = [
                x for x in acti_filtered if x in disable]
        before_reorder = acti[:] # with overflowed plugins removed
        if self._order_fixed(acti):
            fix_active.act_reordered = (before_reorder, acti)
        if fix_active.act_changed():
            if on_disc: # used when getting active and found invalid, fix 'em!
                # Notify user and backup previous plugins.txt
                fix_active.act_header = 'Invalid Plugin txt corrected:'
                self._backup_active_plugins()
                self._persist_active_plugins(acti, lord)
            else: # active list we passed in when setting load order is invalid
                fix_active.act_header = 'Invalid active plugins list corrected:'
            return True # changes, saved if loading plugins.txt
        return False # no changes, not saved

    def check_active_limit(self, acti_filtered):
        acti_filtered_regular = []
        acti_filtered_esl = []
        for m in acti_filtered:
            mi = self.mod_infos[m]
            if mi.is_esl():
                acti_filtered_esl.append(m)
            elif not mi.is_overlay():
                # Overlay plugins take up no LO slot, so skip them entirely
                acti_filtered_regular.append(m)
        return (set(acti_filtered_regular[self.max_espms:]),
                set(acti_filtered_esl[self.max_esls:]))

    def _fixed_order_plugins(self):
        """Returns a list of plugins that must have the order they have in this
        list. The list may only contain plugins that are actually present in
        the Data folder."""
        return [self.master_path, *(x for x in self.must_be_active_if_present
                                    if x in self.mod_infos)]

    def _order_fixed(self, lord_or_acti):
        # This may be acti, so don't force-activate fixed-order plugins
        # (plugins with a missing LO when this is lord will already have had a
        # load order set earlier in _fix_load_order)
        la_set = set(lord_or_acti)
        fixed_order = [p for p in self._fixed_order_plugins() if p in la_set]
        if not fixed_order: return False # nothing to do
        fixed_order_set = set(fixed_order)
        filtered_lo = [x for x in lord_or_acti if x not in fixed_order_set]
        lo_with_fixed = [*fixed_order, *filtered_lo]
        if lord_or_acti != lo_with_fixed:
            lord_or_acti[:] = lo_with_fixed
            return True
        return False

    @staticmethod
    def _check_active_order(acti, lord):
        dex_dict = {mod: index for index, mod in enumerate(lord)}
        acti.sort(key=dex_dict.__getitem__)
        return u''

    # HELPERS -----------------------------------------------------------------
    @staticmethod
    def _check_for_duplicates(plugins_list: list[FName]):
        mods, duplicates, j = set(), set(), 0
        mods_add = mods.add
        duplicates_add = duplicates.add
        for i, mod in enumerate(plugins_list[:]):
            if mod in mods:
                del plugins_list[i - j]
                j += 1
                duplicates_add(mod)
            else:
                mods_add(mod)
        return duplicates

    # INITIALIZATION ----------------------------------------------------------
    @classmethod
    def parse_ccc_file(cls): pass

    def print_lo_paths(self):
        """Prints the paths that will be used and what they'll be used for.
        Useful for debugging."""
        acti_lo = self.get_lo_files()
        bolt.deprint('Using the following load order files:')
        if len(acti_lo) == 2 and acti_lo[0] == acti_lo[1]:
            bolt.deprint(f' - Load order and active plugins: {acti_lo[0]}')
        else:
            bolt.deprint(f' - Active plugins: {acti_lo.pop(0)}')
            if acti_lo:
                bolt.deprint(f' - Load order: {acti_lo.pop(0)}')

def _mk_ini(ini_key, star, ini_fpath):
    """Creates a new IniFile from the specified bolt.Path object."""
    # We don't support OBSE INIs here, only regular IniFile objects
    ini_type, ini_encoding = get_ini_type_and_encoding(ini_fpath)
    class _IniLoFile(_LoFile, ini_type):
        def __init__(self, ini_key, *args, **kwargs):
            super().__init__(*args, **kwargs)
            _ini, self._section, self._key_fmt = ini_key

        def parse_modfile(self, mod_infos, *, __re=None) -> _ParsedLo:
            """Read the section specified in self._section and return all
            its values as FName objects. Handles missing INI file and an
            absent section gracefully."""
            # Returned format is dict[FName, tuple[str, int]], we want the
            # unicode (i.e. the mod names)
            section_mapping = self.get_setting_values(self._section, {})
            # Sort by line number, then convert the values to FNames and return
            section_vals = dict_sort(section_mapping, values_dex=[1])
            out = [FName(v[0]) for k, v in section_vals]
            self.do_update() # update the cached info
            return out, out

        def write_modfile(self, lord, active):
            """Write out the lord/active using the section/key format attrs."""
            section_contents = {self._key_fmt % {'lo_idx': i}: lo_mod for
                                i, lo_mod in enumerate(lord)}
            # Remove any existing section - also prevents duplicate sections
            # with different case
            self.saveSettings({self._section: section_contents},
                              skip_sections={self._section.lower()})

        def upd_on_swap(self, old_dir, new_dir):
            # If there's no INI inside the old (saves) directory, copy it
            old_ini = self._resolve_case_ambiguity(old_dir.join(ini_key[0]))
            if not old_ini.is_file():
                self.fs_copy(old_ini)
            # Read from the new INI if it exists and write to our main INI
            move_ini = self._resolve_case_ambiguity(new_dir.join(ini_key[0]))
            if move_ini.is_file():
                loact = _mk_ini(ini_key, self._star, move_ini).parse_modfile(
                    None)
                self.write_modfile(*loact)
                return True
            return False
    return _IniLoFile(ini_key, star, ini_fpath, ini_encoding)

class INIGame(LoGame):
    """Class for games which use an INI section to determine parts of the load
    order. Meant to be used in multiple inheritance with other LoGame types, be
    sure to put INIGame first, so its init runs first in order to initialize
    the plugins txt (currently) as a _IniLoFile instance. It is currently
    used with TimeStampGame and could in principle be used with TextfileGame
    too, but we are not looking forward to that. It can't be used with
    AsteriskGame, makes no sense.

    To use an INI section to specify active plugins, change ini_key_actives.
    To use an INI section to specify load order, change ini_key_lo. You can
    also specify both if the game uses an INI for everything.
    Format for them is (INI Name, section, entry format string).
    The entry format string receives a format argument, %(lo_idx)s, which
    corresponds to the load order position of the mod written as a value.
    For example, (u'test.ini', u'Mods', u'Mod%(lo_idx)s') would result in
    something like this:
        [Mods]
        Mod0=FirstMod.esp
        Mod1=SecondMod.esp"""
    # The INI keys, see class docstring for more info
    ini_key_actives = None
    ini_key_lo = None

    def __init__(self, mod_infos, plugins_txt_path, **kwargs):
        """Creates a new INIGame instance. plugins_txt_path does not have to
        be specified if INIGame will manage active plugins."""
        if self.__class__.ini_key_actives:
            kwargs['plugins_txt_path'] = self.ini_dir_actives.join(
                self.ini_key_actives[0])
            kwargs['plugins_txt_type'] = partial(_mk_ini, self.ini_key_actives)
        else: kwargs['plugins_txt_path'] = plugins_txt_path
        if self.__class__.ini_key_lo:
            kwargs.update({ # we must come just before TextfileGame in the MRO
                'loadorder_txt_path': self.ini_dir_lo.join(self.ini_key_lo[0]),
                'lo_txt_type': partial(_mk_ini, self.ini_key_lo)})
        super().__init__(mod_infos, **kwargs)

    # INI directories, override if needed
    @property
    def ini_dir_actives(self) -> Path:
        """Returns the directory containing the actives INI. Defaults to the
        game path."""
        return bass.dirs[u'app']

    @property
    def ini_dir_lo(self) -> Path:
        """Returns the directory containing the load order INI. Defaults to the
        game path."""
        return bass.dirs[u'app']

    # Misc overrides
    @classmethod
    def _must_update_active(cls, deleted_plugins, reordered):
        if cls.ini_key_actives is not None:
            return True # Assume order is important for the INI
        return super()._must_update_active(deleted_plugins, reordered)

class TimestampGame(LoGame):
    """Oblivion and other games where load order is set using modification
    times."""
    # Intentionally imprecise mtime cache
    _mtime_mods: defaultdict[int, set[Path]] = defaultdict(set)

    @classmethod
    def _must_update_active(cls, deleted_plugins, reordered): return deleted_plugins

    def has_load_order_conflict(self, mod_name):
        ti = int(self.mod_infos[mod_name].ftime)
        return ti in self._mtime_mods and len(self._mtime_mods[ti]) > 1

    def has_load_order_conflict_active(self, mod_name, active):
        ti = int(self.mod_infos[mod_name].ftime)
        return self.has_load_order_conflict(mod_name) and bool(
            (self._mtime_mods[ti] - {mod_name}) & active)

    # Abstract overrides ------------------------------------------------------
    def __calculate_mtime_order(self, mods=None): # excludes corrupt mods
        # sort case insensitive (for time conflicts)
        mods = sorted(self.mod_infos if mods is None else mods)
        mods.sort(key=lambda x: self.mod_infos[x].ftime)
        mods.sort(key=lambda x: not self.mod_infos[x].in_master_block())
        return mods

    def _fetch_load_order(self, cached_load_order, cached_active):
        self._rebuild_mtimes_cache() ##: will need that tweaked for lock load order
        return self.__calculate_mtime_order()

    def _persist_load_order(self, lord, active):
        assert set(self.mod_infos) == set(lord) # (lord must be valid)
        if not lord: return
        current = self.__calculate_mtime_order()
        # break conflicts
        older = self.mod_infos[current[0]].ftime # initialize to game master
        for i, mod in enumerate(current[1:]):
            info = self.mod_infos[mod]
            if info.ftime == older: break
            older = info.ftime
        else: mod = i = None # define i to avoid warning below
        if mod is not None: # respace this and next mods in 60 sec intervals
            for mod in current[i + 1:]:
                info = self.mod_infos[mod]
                older += 60.0
                info.setmtime(older)
        restamp = []
        for ordered, mod in zip(lord, current):
            if ordered == mod: continue
            restamp.append((ordered, self.mod_infos[mod].ftime))
        for ordered, modification_time in restamp:
            self.mod_infos[ordered].setmtime(modification_time)
        # rebuild our cache
        self._rebuild_mtimes_cache()

    def _rebuild_mtimes_cache(self):
        self._mtime_mods.clear()
        for mod, info in self.mod_infos.items():
            self._mtime_mods[int(info.ftime)].add(mod)

    def _persist_if_changed(self, active, lord, previous_active,
                            previous_lord):
        if previous_lord is None or previous_lord != lord:
            self._persist_load_order(lord, active)
        if previous_active is None or set(previous_active) != set(active):
            self._persist_active_plugins(active, lord)

    # Other overrides ---------------------------------------------------------
    def _fix_load_order(self, lord, fix_lo, _mtime_order=True):
        """If _mtime_order is True, the load order will be sorted by mtime -
        previous behavior (see clients) but may not be what we want in all
        cases."""
        super()._fix_load_order(lord, fix_lo)
        if _mtime_order and fix_lo.lo_added:
            lord[:] = self.__calculate_mtime_order(mods=lord)

class _TextFileLo(LoGame):
    """Common code for games that use a text file to store the load order."""

    def pinned_mods(self):
        return {self.master_path, *self.must_be_active_if_present}

    def _backup_load_order(self):
        """This method should make a backup of whatever file is storing the
        load order plugins list."""
        self.get_lo_file().create_backup()

    def get_lo_file(self): # AsteriskGame - has a single lo/actives file
        return self._plugins_txt

    def get_lo_files(self):
        return [*super().get_lo_files(), self.get_lo_file().abs_path]

class TextfileGame(_TextFileLo):

    def __init__(self, mod_infos, plugins_txt_path, loadorder_txt_path: Path,
                 *, lo_txt_type=_LoFile, **kwargs):
        super().__init__(mod_infos, plugins_txt_path, **kwargs)
        self._loadorder_txt = lo_txt_type(self._star, loadorder_txt_path)

    def request_cache_update(self, cached_load_order, cached_active):
        _lo, act = super().request_cache_update(cached_load_order, cached_active)
        active_changed = act is None
        # if active changed, refetch load order to check for desync
        # will also return True if file was deleted
        lo_changed = (active_changed or cached_load_order is None or
                      self._loadorder_txt.do_update())
        return (None if lo_changed else cached_load_order,
                None if active_changed else cached_active)

    @classmethod
    def _must_update_active(cls, deleted_plugins, reordered):
        return deleted_plugins or reordered

    def swap(self, old_dir, new_dir):
        swapped_pl = super().swap(old_dir, new_dir)
        return self._loadorder_txt.upd_on_swap(old_dir, new_dir) or swapped_pl

    def get_lo_file(self):
        return self._loadorder_txt

    # Abstract overrides ------------------------------------------------------
    def _fetch_load_order(self, cached_load_order,
            cached_active: tuple[FName] | list[FName]):
        """Read data from loadorder.txt file. If loadorder.txt does not
        exist create it and try reading plugins.txt so the load order of the
        user is preserved (note it will create the plugins.txt if not
        existing). Additional mods should be added by caller who should
        anyway call _fix_load_order. If cached_active is passed, the relative
        order of mods will be corrected to match their relative order in
        cached_active."""
        pl_path = self._plugins_txt.abs_path
        try: #--Read file
            _acti, lo = self._loadorder_txt.parse_modfile(self.mod_infos)
        except FileNotFoundError:
            mods = cached_active or []
            if cached_active is not None and not pl_path.exists():
                self._write_plugins_txt(cached_active, cached_active)
                bolt.deprint(f'Created {pl_path} based on cached info')
            elif cached_active is None and pl_path.exists():
                mods = self._fetch_active_plugins() # will add Skyrim.esm
            self._persist_load_order(mods, mods)
            bolt.deprint(f'Created {self._loadorder_txt.abs_path}')
            return mods
        # handle desync with plugins txt
        if cached_active is not None:
            cached_active_copy = cached_active[:]
            cached_active_set = set(cached_active)
            active_in_lo = [x for x in lo if x in cached_active_set]
            lo_dex = {x: i for i, x in enumerate(lo)}
            while active_in_lo:
                # Use list(), we may modify cached_active_copy and active_in_lo
                for i, (ordered, current) in list(enumerate(
                        zip(cached_active_copy, active_in_lo))):
                    if ordered != current:
                        if ordered not in lo:
                            # Mod is in plugins.txt, but not in loadorder.txt;
                            # just drop it from the copy for now, we'll check
                            # if it's really missing in _fix_active_plugins
                            cached_active_copy.remove(ordered)
                            break
                        for j, x in enumerate(active_in_lo[i:]):
                            if x == ordered: break
                            # x should be above ordered
                            to = lo_dex[ordered] + 1 + j
                            # make room
                            lo_dex = {x: (i if i < to else i + 1) for x, i in
                                 lo_dex.items()}
                            lo_dex[x] = to # bubble them up !
                        active_in_lo.remove(ordered)
                        cached_active_copy = cached_active_copy[i + 1:]
                        active_in_lo = active_in_lo[i:]
                        break
                else: break
            fetched_lo = lo[:]
            lo.sort(key=lo_dex.get)
            if lo != fetched_lo:
                # We fixed a desync, make a backup and write the load order
                self._backup_load_order()
                self._persist_load_order(lo, lo)
                bolt.deprint(f'Corrected {self._loadorder_txt.abs_path} '
                    f'(order of mods differed from their order in {pl_path})')
        return lo

    def _fetch_active_plugins(self):
        """Fetch what's in the plugins.txt - if something shouldn't be there,
        remove it and rewrite the plugins.txt."""
        act = super()._fetch_active_plugins()
        if self.master_path in act: # remove master_path from plugins.txt
            bolt.deprint(f'Removing {self.master_path} from '
                         f'{self._plugins_txt.abs_path}')
            self._backup_active_plugins() #we removed master_path back up first
            act = self._persist_active_plugins(act, act)
        # Prepend the game master - should be present and is always active
        return [self.master_path, *act]

    def _persist_load_order(self, lord, active):
        self._loadorder_txt.write_modfile(lord, lord)
        self._loadorder_txt.do_update()

    def _persist_active_plugins(self, active, lord):
        active_filtered = [x for x in active if x != self.master_path]
        super()._persist_active_plugins(active_filtered, active_filtered)
        return active_filtered

    def _persist_if_changed(self, active, lord, previous_active,
                            previous_lord):
        if previous_lord is None or previous_lord != lord:
            self._persist_load_order(lord, active)
        if previous_active is None or previous_active != active:
            self._persist_active_plugins(active, lord)

    # Validation overrides ----------------------------------------------------
    @staticmethod
    def _check_active_order(acti, lord):
        dex_dict = {mod: index for index, mod in enumerate(lord)}
        old = acti[:]
        acti.sort(key=dex_dict.__getitem__) # all present in lord
        if acti != old: # active mods order that disagrees with lord ?
            return f'Active list order of plugins ({_pl(old)}) differs from ' \
                   f'supplied load order ({_pl(acti)})'
        return u''

class AsteriskGame(_TextFileLo):
    """_TextFileLo storing also active state in the lo file - active plugins
    are marked with a star."""

    max_espms = 254
    max_esls = 4096 # hard limit, game runs out of fds sooner, testing needed
    # Creation Club content file - if empty, indicates that this game has no CC
    _ccc_filename = u''
    # Hardcoded list used if the file specified above does not exist or could
    # not be read
    _ccc_fallback = ()
    _star = True

    def _active_entries_to_remove(self):
        """Return a set of plugin names that should not be written into the LO
        file that stores active plugins."""
        return self.pinned_mods()

    def request_cache_update(self, *args):
        if None in args or self._plugins_txt.do_update():
            return None, None
        return args

    def _cached_or_fetch(self, cached_load_order, cached_active):
        # read the file once
        return self._fetch_load_order(cached_load_order, cached_active)

    @classmethod
    def _must_update_active(cls, deleted_plugins, reordered): return True

    # Abstract overrides ------------------------------------------------------
    def _fetch_active_plugins(self) -> list[FName]:
        raise NotImplementedError # no override for AsteriskGame

    def _fetch_load_order(self, cached_load_order, cached_active):
        """Read data from plugins.txt file. If plugins.txt does not exist
        create it. Discards information read if cached_* is passed in,
        but due to our ultimate caller being get_load_order *at least one* is
        None."""
        try:
            active, lo = self._plugins_txt.parse_modfile(self.mod_infos)
            lo = lo if cached_load_order is None else cached_load_order
            if cached_active is None:  # we fetched active, clean it up
                rem_from_acti = self._active_entries_to_remove()
                if any_dropped := ({*active, *lo} & rem_from_acti):
                    bolt.deprint(f'Removing {_pl(sorted(any_dropped))} from '
                                 f'{self._plugins_txt.abs_path}')
                    # We removed plugins that don't belong here, back up first
                    self._backup_active_plugins()
                    lo, active = self._persist_load_order(lo, active)
                # Prepend all present fixed-order plugins that can't be in the
                # plugins txt to the active and lord lists
                sorted_rem = [x for x in self._fixed_order_plugins() if
                              x in rem_from_acti]
                ##: we rewrite lo here even if cached_load_order is passed in
                active, lo = [*sorted_rem, *active], [*sorted_rem, *lo]
            else:
                active = cached_active
        except FileNotFoundError:
            # Create it if it doesn't exist
            must_be_active = self._fixed_order_plugins()
            lo = cached_load_order or must_be_active
            self._persist_load_order(lo, active := cached_active or must_be_active)
            bolt.deprint(f'Created {self._plugins_txt.abs_path}')
        return lo, active

    def _persist_load_order(self, lord, active):
        rem_from_acti = self._active_entries_to_remove()
        lord = [x for x in lord if x not in rem_from_acti]
        active = [x for x in active if x not in rem_from_acti]
        self._write_plugins_txt(lord, active)
        return lord, active

    def _persist_active_plugins(self, active, lord):
        return self._persist_load_order(lord, active)

    def _save_fixed_load_order(self, fix_lo, fixed_active, lo, active):
        if fixed_active: return # plugins.txt already saved
        if fix_lo.lo_changed():
            self._backup_load_order()
            self._persist_load_order(lo, active)

    def _persist_if_changed(self, active, lord, previous_active,
                            previous_lord):
        if (previous_lord is None or previous_lord != lord) or (
                previous_active is None or previous_active != active):
            self._persist_load_order(lord, active)

    @classmethod
    def parse_ccc_file(cls):
        if not cls._ccc_filename: return # Abort if this game has no CC
        ccc_path = bass.dirs[u'app'].join(cls._ccc_filename)
        try:
            with open(ccc_path, 'rb') as ins:
                ccc_contents = []
                for ccc_line in ins.readlines():
                    try:
                        ccc_dec = bolt.decoder(ccc_line, encoding=u'cp1252')
                        ccc_contents.append(FName(ccc_dec.strip()))
                    except UnicodeError:
                        bolt.deprint(f'Failed to decode CCC entry {ccc_line}')
                        continue
                cls.must_be_active_if_present += tuple(ccc_contents)
        except OSError as e:
            if not isinstance(e, FileNotFoundError):
                bolt.deprint(f'Failed to open {ccc_path}', traceback=True)
            bolt.deprint(f'{cls._ccc_filename} does not exist or could not be '
                         f'read, falling back to hardcoded CCC list')
            cls.must_be_active_if_present += cls._ccc_fallback

# Print helpers
def _pl(it, legend='', joint=', '):
    return legend + joint.join(it)
