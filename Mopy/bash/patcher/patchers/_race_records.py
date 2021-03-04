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
"""Temp module, contains the Race Records patcher. It imports the tweak classes
from multitweak_races.py."""

from __future__ import print_function

import random
import re
from collections import defaultdict, Counter

# Internal
from .multitweak_races import *
from ..base import ListPatcher, ModLoader
from ... import bosh, bush
from ...bolt import GPath, deprint
from ...brec import MelObject, strFid
from ...exception import BoltError
from ...patcher.base import AMultiTweaker

# Utilities & Constants -------------------------------------------------------
def _find_vanilla_eyes():
    """Converts vanilla default_eyes to use long FormIDs and returns the
    result."""
    def _conv_fid(rc_fid): return GPath(rc_fid[0]), rc_fid[1]
    ret = {}
    for race_fid, race_eyes in bush.game.default_eyes.iteritems():
        new_key = _conv_fid(race_fid)
        new_val = [_conv_fid(eye_fid) for eye_fid in race_eyes]
        ret[new_key] = new_val
    return ret

_main_master = GPath(bush.game.master_file)

#------------------------------------------------------------------------------
# Race Records ----------------------------------------------------------------
#------------------------------------------------------------------------------
class RaceRecordsPatcher(AMultiTweaker, ListPatcher, ModLoader):
    """Race patcher - we inherit from AMultiTweaker to use tweak_instances."""
    patcher_group = u'Special'
    patcher_order = 40
    _read_sigs = (b'RACE', b'EYES', b'HAIR', b'NPC_')
    _tweak_classes = {
        RaceTweak_BiggerOrcsAndNords, RaceTweak_MergeSimilarRaceHairs,
        RaceTweak_MergeSimilarRaceEyes, RaceTweak_PlayableEyes,
        RaceTweak_PlayableHairs, RaceTweak_SexlessHairs, RaceTweak_AllEyes,
        RaceTweak_AllHairs,
    }

    def __init__(self, p_name, p_file, p_sources, enabled_tweaks):
        # NB: call the ListPatcher __init__ not the AMultiTweaker one!
        super(AMultiTweaker, self).__init__(p_name, p_file, p_sources)
        self.races_data = {b'EYES': [], b'HAIR': []}
        self.raceData = defaultdict(dict) #--Race eye meshes, hair,eyes
        #--Restrict srcs to active/merged mods.
        self.srcs = [x for x in self.srcs if x in p_file.allSet]
        self.isActive = True #--Always enabled to support eye filtering
        self.eye_mesh = {}
        self.scanTypes = {b'RACE', b'EYES', b'HAIR', b'NPC_'}
        self.vanilla_eyes = _find_vanilla_eyes()
        self.enabled_tweaks = enabled_tweaks

    def initData(self,progress):
        """Get data from source files."""
        # HACK - wholesale copy of MultiTweaker.initData, see #494
        # Has to come before the srcs check, because of isActive nonsense this
        # patcher will still run and blow up in scanModFile otherwise
        self._tweak_dict = t_dict = defaultdict(lambda: ([], []))
        for tweak in self.enabled_tweaks: # type: MultiTweakItem
            for read_sig in tweak.tweak_read_classes:
                t_dict[read_sig][tweak.supports_pooling].append(tweak)
        if not self.isActive or not self.srcs: return
        self.loadFactory = self._patcher_read_fact(by_sig=[b'RACE'])
        progress.setFull(len(self.srcs))
        cachedMasters = {}
        for index,srcMod in enumerate(self.srcs):
            if srcMod not in bosh.modInfos: continue
            srcInfo = bosh.modInfos[srcMod]
            srcFile = self._mod_file_read(srcInfo)
            bashTags = srcInfo.getBashTags()
            if b'RACE' not in srcFile.tops: continue
            tmp_race_data = defaultdict(dict) #so as not to carry anything over!
            if u'R.ChangeSpells' in bashTags and u'R.AddSpells' in bashTags:
                raise BoltError(
                    u'WARNING mod %s has both R.AddSpells and R.ChangeSpells '
                    u'tags - only one of those tags should be on a mod at '
                    u'one time' % srcMod)
            for race in srcFile.tops[b'RACE'].getActiveRecords():
                tempRaceData = tmp_race_data[race.fid]
                raceData = self.raceData[race.fid]
                if u'R.AddSpells' in bashTags:
                    tempRaceData[u'AddSpells'] = race.spells
                if u'R.ChangeSpells' in bashTags:
                    raceData[u'spellsOverride'] = race.spells
            for master in srcInfo.masterNames:
                if not master in bosh.modInfos: continue  # or break
                # filter mods
                if master in cachedMasters:
                    masterFile = cachedMasters[master]
                else:
                    masterInfo = bosh.modInfos[master]
                    masterFile = self._mod_file_read(masterInfo)
                    if b'RACE' not in masterFile.tops: continue
                    cachedMasters[master] = masterFile
                for race in masterFile.tops[b'RACE'].getActiveRecords():
                    if race.fid not in tmp_race_data: continue
                    tempRaceData = tmp_race_data[race.fid]
                    raceData = self.raceData[race.fid]
                    if u'AddSpells' in tempRaceData:
                        raceData.setdefault(u'AddSpells', []) ##: set?
                        for spell in tempRaceData[u'AddSpells']:
                            if spell not in race.spells:
                                if spell not in raceData[u'AddSpells']:
                                    raceData[u'AddSpells'].append(spell)
                        del tempRaceData[u'AddSpells']
                    for race_key in tempRaceData:
                        if tempRaceData[race_key] != getattr(race, race_key):
                            raceData[race_key] = tempRaceData[race_key]
            progress.plus()

    def scanModFile(self, modFile, progress):
        """Add appropriate records from modFile."""
        races_data = self.races_data
        eye_mesh = self.eye_mesh
        if not (set(modFile.tops) & self.scanTypes): return
        srcEyes = {record.fid for record in modFile.tops[b'EYES'].getActiveRecords()}
        #--Eyes, Hair
        for top_grup_sig in (b'EYES', b'HAIR'):
            patchBlock = self.patchFile.tops[top_grup_sig]
            id_records = patchBlock.id_records
            for record in modFile.tops[top_grup_sig].getActiveRecords():
                races_data[top_grup_sig].append(record.fid)
                if record.fid not in id_records:
                    patchBlock.setRecord(record.getTypeCopy())
        #--Npcs with unassigned eyes
        patchBlock = self.patchFile.tops[b'NPC_']
        id_records = patchBlock.id_records
        for record in modFile.tops[b'NPC_'].getActiveRecords():
            if not record.eye and record.fid not in id_records:
                patchBlock.setRecord(record.getTypeCopy())
        #--Race block
        patchBlock = self.patchFile.tops[b'RACE']
        id_records = patchBlock.id_records
        for record in modFile.tops[b'RACE'].getActiveRecords():
            if record.fid not in id_records:
                patchBlock.setRecord(record.getTypeCopy())
            if not record.rightEye or not record.leftEye:
                # Don't complain if the FULL is missing, that probably means
                # it's an internal or unused RACE
                if record.full:
                    deprint(u'No right and/or no left eye recorded in race '
                        u'%s, from mod %s' % (record.full, modFile.fileInfo))
                continue
            for eye in record.eyes:
                if eye in srcEyes:
                    eye_mesh[eye] = (record.rightEye.modPath.lower(),
                                     record.leftEye.modPath.lower())
        # HACK - wholesale copy of MultiTweaker.scanModFile, see #494
        rec_pool = defaultdict(set)
        common_tops = set(modFile.tops) & set(self._tweak_dict)
        for curr_top in common_tops:
            # Need to give other tweaks a chance to do work first
            for o_tweak in self._tweak_dict[curr_top][0]:
                o_tweak.tweak_scan_file(modFile, self.patchFile)
            # Now we can collect all records that poolable tweaks are
            # interested in
            pool_record = rec_pool[curr_top].add
            poolable_tweaks = self._tweak_dict[curr_top][1]
            if not poolable_tweaks: continue # likely complex type, e.g. CELL
            for record in modFile.tops[curr_top].getActiveRecords():
                for p_tweak in poolable_tweaks: # type: MultiTweakItem
                    if p_tweak.wants_record(record):
                        pool_record(record)
                        break # Exit as soon as a tweak is interested
        # Finally, copy all pooled records in one fell swoop
        for top_grup_sig, pooled_records in rec_pool.iteritems():
            if pooled_records: # only copy if we could pool
                self.patchFile.tops[top_grup_sig].copy_records(pooled_records)

    def buildPatch(self,log,progress):
        """Updates races as needed."""
        debug = False
        tweak_data = self.races_data
        if not self.isActive: return
        patchFile = self.patchFile
        keep = patchFile.getKeeper()
        if b'RACE' not in patchFile.tops: return
        racesPatched = []
        racesSorted = []
        racesFiltered = []
        mod_npcsFixed = defaultdict(set)
        reProcess = re.compile(
            u'(?:dremora)|(?:akaos)|(?:lathulet)|(?:orthe)|(?:ranyu)',
            re.I | re.U)
        #--Import race info
        for race in patchFile.tops[b'RACE'].records:
            #~~print 'Building',race.eid
            raceData = self.raceData.get(race.fid, None)
            if not raceData: continue
            raceChanged = False
            #--spells
            if u'spellsOverride' in raceData:
                race.spells = raceData[u'spellsOverride']
            if u'AddSpells' in raceData:
                raceData[u'spells'] = race.spells
                for spell in raceData[u'AddSpells']:
                    raceData[u'spells'].append(spell)
                race.spells = raceData[u'spells']
            #--Changed
            if raceChanged:
                racesPatched.append(race.eid)
                keep(race.fid)
        #--Eye Mesh filtering
        eye_mesh = self.eye_mesh
        try:
            blueEyeMesh = eye_mesh[(_main_master, 0x27308)]
        except KeyError:
            print(u'error getting blue eye mesh:')
            print(u'eye meshes:', eye_mesh)
            raise
        argonianEyeMesh = eye_mesh[(_main_master, 0x3e91e)]
        if debug:
            print(u'== Eye Mesh Filtering')
            print(u'blueEyeMesh',blueEyeMesh)
            print(u'argonianEyeMesh',argonianEyeMesh)
        for eye in (
            (_main_master, 0x1a), #--Reanimate
            (_main_master, 0x54bb9), #--Dark Seducer
            (_main_master, 0x54bba), #--Golden Saint
            (_main_master, 0x5fa43), #--Ordered
            ):
            eye_mesh.setdefault(eye,blueEyeMesh)
        def setRaceEyeMesh(race,rightPath,leftPath):
            race.rightEye.modPath = rightPath
            race.leftEye.modPath = leftPath
        for race in patchFile.tops[b'RACE'].records:
            if debug: print(u'===', race.eid)
            if not race.eyes: continue  #--Sheogorath. Assume is handled
            # correctly.
            if not race.rightEye or not race.leftEye: continue #--WIPZ race?
            if re.match(u'^117[a-zA-Z]', race.eid, flags=re.U): continue  #--
            #  x117 race?
            raceChanged = False
            mesh_eye = {}
            for eye in race.eyes:
                if eye not in eye_mesh:
                    deprint(
                        _(u'Mesh undefined for eye %s in race %s, eye removed '
                          u'from race list.') % (
                            strFid(eye), race.eid,))
                    continue
                mesh = eye_mesh[eye]
                if mesh not in mesh_eye:
                    mesh_eye[mesh] = []
                mesh_eye[mesh].append(eye)
            currentMesh = (
                race.rightEye.modPath.lower(), race.leftEye.modPath.lower())
            try:
                maxEyesMesh = sorted(mesh_eye, key=lambda a: len(mesh_eye[a]),
                                     reverse=True)[0]
            except IndexError:
                maxEyesMesh = blueEyeMesh
            #--Single eye mesh, but doesn't match current mesh?
            if len(mesh_eye) == 1 and currentMesh != maxEyesMesh:
                setRaceEyeMesh(race,*maxEyesMesh)
                raceChanged = True
            #--Multiple eye meshes (and playable)?
            if debug:
                for mesh,eyes in mesh_eye.iteritems():
                    print(mesh)
                    for eye in eyes: print(u' ',strFid(eye))
            if len(mesh_eye) > 1 and (race.flags.playable or race.fid == (
                    _main_master, 0x038010)):
                #--If blueEyeMesh (mesh used for vanilla eyes) is present,
                # use that.
                if blueEyeMesh in mesh_eye and currentMesh != argonianEyeMesh:
                    setRaceEyeMesh(race,*blueEyeMesh)
                    race.eyes = mesh_eye[blueEyeMesh]
                    raceChanged = True
                elif argonianEyeMesh in mesh_eye:
                    setRaceEyeMesh(race,*argonianEyeMesh)
                    race.eyes = mesh_eye[argonianEyeMesh]
                    raceChanged = True
                #--Else figure that current eye mesh is the correct one
                elif currentMesh in mesh_eye:
                    race.eyes = mesh_eye[currentMesh]
                    raceChanged = True
                #--Else use most popular eye mesh
                else:
                    setRaceEyeMesh(race,*maxEyesMesh)
                    race.eyes = mesh_eye[maxEyesMesh]
                    raceChanged = True
            if raceChanged:
                racesFiltered.append(race.eid)
                keep(race.fid)
            if race.full:
                tweak_data[race.full.lower()] = {'hairs': race.hairs,
                                                 'eyes': race.eyes,
                                                 'relations': race.relations}
        # HACK - wholesale copy of MultiTweaker.buildPatch, see #494, plus
        # lightly edited for race patcher nonsense
        self.patchFile.races_data = tweak_data
        for tweak in self.enabled_tweaks: # type: MultiTweakItem
            tweak.prepare_for_tweaking(self.patchFile)
        common_tops = set(self.patchFile.tops) & set(self._tweak_dict)
        keep = self.patchFile.getKeeper()
        tweak_counter = defaultdict(Counter)
        for curr_top in common_tops:
            top_dict = self._tweak_dict[curr_top]
            # Need to give other tweaks a chance to do work first
            for o_tweak in top_dict[False]:
                o_tweak.tweak_build_patch(log, tweak_counter[o_tweak],
                                          self.patchFile)
            poolable_tweaks = top_dict[True]
            if not poolable_tweaks: continue  # likely complex type, e.g. CELL
            for record in self.patchFile.tops[curr_top].getActiveRecords():
                for p_tweak in poolable_tweaks:  # type: MultiTweakItem
                    # Check if this tweak can actually change the record - just
                    # relying on the check in scanModFile is *not* enough.
                    # After all, another tweak or patcher could have made a
                    # copy of an entirely unrelated record that *it* was
                    # interested in that just happened to have the same record
                    # type
                    if p_tweak.wants_record(record):
                        # Give the tweak a chance to do its work, and remember
                        # that we now want to keep the record. Note that we
                        # can't break early here, because more than one tweak
                        # may want to touch this record
                        p_tweak.tweak_record(record)
                        keep(record.fid)
                        tweak_counter[p_tweak][record.fid[0]] += 1
        # We're done with all tweaks, give them a chance to clean up and do any
        # finishing touches (e.g. injecting records for GMST tweaks)
        for tweak in self.enabled_tweaks:
            tweak.finish_tweaking(self.patchFile)
        #--Sort Eyes/Hair
        final_eyes = {}
        defaultMaleHair = {}
        defaultFemaleHair = {}
        eyeNames  = {x.fid: x.full for x in patchFile.tops[b'EYES'].records}
        hairNames = {x.fid: x.full for x in patchFile.tops[b'HAIR'].records}
        maleHairs = {x.fid for x in patchFile.tops[b'HAIR'].records
                     if not x.flags.notMale}
        femaleHairs = {x.fid for x in patchFile.tops[b'HAIR'].records
                       if not x.flags.notFemale}
        for race in patchFile.tops[b'RACE'].records:
            if (race.flags.playable or race.fid == (
                    _main_master, 0x038010)) and race.eyes:
                final_eyes[race.fid] = [x for x in
                                        self.vanilla_eyes.get(race.fid, [])
                                        if x in race.eyes]
                if not final_eyes[race.fid]:
                    final_eyes[race.fid] = [race.eyes[0]]
                defaultMaleHair[race.fid] = [x for x in race.hairs if
                                             x in maleHairs]
                defaultFemaleHair[race.fid] = [x for x in race.hairs if
                                               x in femaleHairs]
                race.hairs.sort(key=lambda x: hairNames.get(x))
                race.eyes.sort(key=lambda x: eyeNames.get(x))
                racesSorted.append(race.eid)
                keep(race.fid)
        #--Npcs with unassigned eyes/hair
        for npc in patchFile.tops[b'NPC_'].records:
            if npc.fid == (_main_master, 0x000007): continue  #
            # skip player
            if npc.full is not None and npc.race == (
                    _main_master, 0x038010) and not reProcess.search(
                    npc.full): continue
            raceEyes = final_eyes.get(npc.race)
            random.seed(npc.fid[1]) # make it deterministic
            if not npc.eye and raceEyes:
                npc.eye = random.choice(raceEyes)
                mod_npcsFixed[npc.fid[0]].add(npc.fid)
                keep(npc.fid)
            raceHair = (
                (defaultMaleHair, defaultFemaleHair)[npc.flags.female]).get(
                npc.race)
            if not npc.hair and raceHair:
                npc.hair = random.choice(raceHair)
                mod_npcsFixed[npc.fid[0]].add(npc.fid)
                keep(npc.fid)
            if not npc.hairLength:
                npc.hairLength = random.random()
                mod_npcsFixed[npc.fid[0]].add(npc.fid)
                keep(npc.fid)
        #--Done
        log.setHeader(u'= ' + self._patcher_name)
        self._srcMods(log)
        log(u'\n=== ' + _(u'Merged'))
        if not racesPatched:
            log(u'. ~~%s~~' % _(u'None'))
        else:
            for eid in sorted(racesPatched):
                log(u'* ' + eid)
        log(u'\n=== ' + _(u'Eyes/Hair Sorted'))
        if not racesSorted:
            log(u'. ~~%s~~' % _(u'None'))
        else:
            for eid in sorted(racesSorted):
                log(u'* ' + eid)
        log(u'\n=== ' + _(u'Eye Meshes Filtered'))
        if not racesFiltered:
            log(u'. ~~%s~~' % _(u'None'))
        else:
            log(_(u"In order to prevent 'googly eyes', incompatible eyes have "
                  u'been removed from the following races.'))
            for eid in sorted(racesFiltered):
                log(u'* ' + eid)
        if mod_npcsFixed:
            log(u'\n=== ' + _(u'Eyes/Hair Assigned for NPCs'))
            for srcMod in sorted(mod_npcsFixed):
                log(u'* %s: %d' % (srcMod, len(mod_npcsFixed[srcMod])))
        for tweak in self.enabled_tweaks: # type: MultiTweakItem
            tweak.tweak_log(log, tweak_counter[tweak])
