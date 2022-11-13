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
"""GameInfo override for Fallout 4."""

from os.path import join as _j

from .. import GameInfo, WS_COMMON_FILES
from ..patch_game import PatchGame
from ... import bolt

class Fallout4GameInfo(PatchGame):
    displayName = u'Fallout 4'
    fsName = u'Fallout4'
    altName = u'Wrye Flash'
    game_icon = u'fallout4_%u.png'
    bash_root_prefix = u'Fallout4'
    bak_game_name = u'Fallout4'
    my_games_name = u'Fallout4'
    appdata_name = u'Fallout4'
    launch_exe = u'Fallout4.exe'
    game_detect_includes = {'Fallout4.exe'}
    game_detect_excludes = WS_COMMON_FILES
    version_detect_file = u'Fallout4.exe'
    master_file = bolt.FName(u'Fallout4.esm')
    taglist_dir = u'Fallout4'
    loot_dir = u'Fallout4'
    loot_game_name = 'Fallout4'
    registry_keys = [(r'Bethesda Softworks\Fallout4', 'Installed Path')]
    nexusUrl = u'https://www.nexusmods.com/fallout4/'
    nexusName = u'Fallout 4 Nexus'
    nexusKey = u'bash.installers.openFallout4Nexus.continue'

    espm_extensions = GameInfo.espm_extensions | {u'.esl'}
    has_achlist = True
    check_esl = True
    plugin_name_specific_dirs = GameInfo.plugin_name_specific_dirs + [
        _j(u'meshes', u'actors', u'character', u'facegendata', u'facegeom'),
        _j(u'meshes', u'actors', u'character', u'facecustomization')]

    class Ck(GameInfo.Ck):
        ck_abbrev = u'CK'
        long_name = u'Creation Kit'
        exe = u'CreationKit.exe'
        image_name = u'creationkit%s.png'

    class Se(GameInfo.Se):
        se_abbrev = u'F4SE'
        long_name = u'Fallout 4 Script Extender'
        exe = u'f4se_loader.exe'
        ver_files = [u'f4se_loader.exe', u'f4se_steam_loader.dll']
        plugin_dir = u'F4SE'
        cosave_tag = u'F4SE'
        cosave_ext = u'.f4se'
        url = u'http://f4se.silverlock.org/'
        url_tip = u'http://f4se.silverlock.org/'

    class Ini(GameInfo.Ini):
        default_ini_file = u'Fallout4_default.ini'
        dropdown_inis = [u'Fallout4.ini', u'Fallout4Prefs.ini']
        resource_archives_keys = (
            u'sResourceIndexFileList', u'sResourceStartUpArchiveList',
            u'sResourceArchiveList', u'sResourceArchiveList2',
            u'sResourceArchiveListBeta'
        )

    class Ess(GameInfo.Ess):
        ext = u'.fos'

    class Bsa(GameInfo.Bsa):
        bsa_extension = u'.ba2'
        valid_versions = {0x01}

    class Psc(GameInfo.Psc):
        source_extensions = {u'.psc'}

    class Xe(GameInfo.Xe):
        full_name = u'FO4Edit'
        xe_key_prefix = u'fo4View'

    class Bain(GameInfo.Bain):
        data_dirs = GameInfo.Bain.data_dirs | {
            'f4se', # 3P: F4SE
            'interface',
            'lodsettings',
            'materials',
            'mcm', # 3P: FO4 MCM
            'misc',
            'programs',
            'scripts',
            'seq',
            'shadersfx',
            'strings',
            'tools', # 3P: BodySlide
            'vis',
        }
        no_skip_dirs = GameInfo.Bain.no_skip_dirs | {
            # This rule is to allow mods with string translation enabled.
            _j('interface', 'translations'): {'.txt'},
        }
        skip_bain_refresh = {u'fo4edit backups', u'fo4edit cache'}

    class Esp(GameInfo.Esp):
        canBash = True
        canEditHeader = True
        expanded_plugin_range = True
        extension_forces_flags = True
        max_lvl_list_size = 255
        validHeaderVersions = (0.95, 1.0)

    patchers = {
        'ImportObjectBounds', 'LeveledLists', 'TweakSettings',
    }

    bethDataFiles = {
        'dlccoast - geometry.csg',
        'dlccoast - main.ba2',
        'dlccoast - textures.ba2',
        'dlccoast - voices_de.ba2',
        'dlccoast - voices_en.ba2',
        'dlccoast - voices_es.ba2',
        'dlccoast - voices_fr.ba2',
        'dlccoast - voices_it.ba2',
        'dlccoast - voices_ja.ba2',
        'dlccoast.cdx',
        'dlccoast.esm',
        'dlcnukaworld - geometry.csg',
        'dlcnukaworld - main.ba2',
        'dlcnukaworld - textures.ba2',
        'dlcnukaworld - voices_de.ba2',
        'dlcnukaworld - voices_en.ba2',
        'dlcnukaworld - voices_es.ba2',
        'dlcnukaworld - voices_fr.ba2',
        'dlcnukaworld - voices_it.ba2',
        'dlcnukaworld - voices_ja.ba2',
        'dlcnukaworld.cdx',
        'dlcnukaworld.esm',
        'dlcrobot - geometry.csg',
        'dlcrobot - main.ba2',
        'dlcrobot - textures.ba2',
        'dlcrobot - voices_de.ba2',
        'dlcrobot - voices_en.ba2',
        'dlcrobot - voices_es.ba2',
        'dlcrobot - voices_fr.ba2',
        'dlcrobot - voices_it.ba2',
        'dlcrobot - voices_ja.ba2',
        'dlcrobot.cdx',
        'dlcrobot.esm',
        'dlcworkshop01 - geometry.csg',
        'dlcworkshop01 - main.ba2',
        'dlcworkshop01 - textures.ba2',
        'dlcworkshop02 - main.ba2',
        'dlcworkshop02 - textures.ba2',
        'dlcworkshop03 - geometry.csg',
        'dlcworkshop03 - main.ba2',
        'dlcworkshop03 - textures.ba2',
        'dlcworkshop03 - voices_de.ba2',
        'dlcworkshop03 - voices_en.ba2',
        'dlcworkshop03 - voices_es.ba2',
        'dlcworkshop03 - voices_fr.ba2',
        'dlcworkshop03 - voices_it.ba2',
        'dlcworkshop03 - voices_ja.ba2',
        'dlcworkshop01.cdx',
        'dlcworkshop01.esm',
        'dlcworkshop02.esm',
        'dlcworkshop03.cdx',
        'dlcworkshop03.esm',
        'fallout4 - animations.ba2',
        'fallout4 - geometry.csg',
        'fallout4 - interface.ba2',
        'fallout4 - materials.ba2',
        'fallout4 - meshes.ba2',
        'fallout4 - meshesextra.ba2',
        'fallout4 - misc.ba2',
        'fallout4 - nvflex.ba2',
        'fallout4 - shaders.ba2',
        'fallout4 - sounds.ba2',
        'fallout4 - startup.ba2',
        'fallout4 - textures1.ba2',
        'fallout4 - textures2.ba2',
        'fallout4 - textures3.ba2',
        'fallout4 - textures4.ba2',
        'fallout4 - textures5.ba2',
        'fallout4 - textures6.ba2',
        'fallout4 - textures7.ba2',
        'fallout4 - textures8.ba2',
        'fallout4 - textures9.ba2',
        'fallout4 - voices.ba2',
        'fallout4 - voices_de.ba2',
        'fallout4 - voices_es.ba2',
        'fallout4 - voices_fr.ba2',
        'fallout4 - voices_it.ba2',
        'fallout4 - voices_rep.ba2',
        'fallout4.cdx',
        'fallout4.esm',
    }

    # Function Info -----------------------------------------------------------
    # 0: no param; 1: int param; 2: FormID param; 3: float param
    # Third parameter is always sint32, so no need to specify here
    condition_function_data = {
        0:    ('GetWantBlocking', 0, 0),
        1:    ('GetDistance', 2, 0),
        5:    ('GetLocked', 0, 0),
        6:    ('GetPos', 0, 0),
        8:    ('GetAngle', 0, 0),
        10:   ('GetStartingPos', 0, 0),
        11:   ('GetStartingAngle', 0, 0),
        12:   ('GetSecondsPassed', 0, 0),
        14:   ('GetValue', 2, 0),
        18:   ('GetCurrentTime', 0, 0),
        24:   ('GetScale', 0, 0),
        25:   ('IsMoving', 0, 0),
        26:   ('IsTurning', 0, 0),
        27:   ('GetLineOfSight', 2, 0),
        32:   ('GetInSameCell', 2, 0),
        35:   ('GetDisabled', 0, 0),
        36:   ('MenuMode', 1, 0),
        39:   ('GetDisease', 0, 0),
        41:   ('GetClothingValue', 0, 0),
        42:   ('SameFaction', 2, 0),
        43:   ('SameRace', 2, 0),
        44:   ('SameSex', 2, 0),
        45:   ('GetDetected', 2, 0),
        46:   ('GetDead', 0, 0),
        47:   ('GetItemCount', 2, 0),
        48:   ('GetGold', 0, 0),
        49:   ('GetSleeping', 0, 0),
        50:   ('GetTalkedToPC', 0, 0),
        56:   ('GetQuestRunning', 2, 0),
        58:   ('GetStage', 2, 0),
        59:   ('GetStageDone', 2, 1),
        60:   ('GetFactionRankDifference', 2, 2),
        61:   ('GetAlarmed', 0, 0),
        62:   ('IsRaining', 0, 0),
        63:   ('GetAttacked', 0, 0),
        64:   ('GetIsCreature', 0, 0),
        65:   ('GetLockLevel', 0, 0),
        66:   ('GetShouldAttack', 2, 0),
        67:   ('GetInCell', 2, 0),
        68:   ('GetIsClass', 2, 0),
        69:   ('GetIsRace', 2, 0),
        70:   ('GetIsSex', 1, 0),
        71:   ('GetInFaction', 2, 0),
        72:   ('GetIsID', 2, 0),
        73:   ('GetFactionRank', 2, 0),
        74:   ('GetGlobalValue', 2, 0),
        75:   ('IsSnowing', 0, 0),
        77:   ('GetRandomPercent', 0, 0),
        79:   ('WouldBeStealing', 2, 0),
        80:   ('GetLevel', 0, 0),
        81:   ('IsRotating', 0, 0),
        84:   ('GetDeadCount', 2, 0),
        91:   ('GetIsAlerted', 0, 0),
        98:   ('GetPlayerControlsDisabled', 1, 1),
        99:   ('GetHeadingAngle', 2, 0),
        101:  ('IsWeaponMagicOut', 0, 0),
        102:  ('IsTorchOut', 0, 0),
        103:  ('IsShieldOut', 0, 0),
        106:  ('IsFacingUp', 0, 0),
        107:  ('GetKnockedState', 0, 0),
        108:  ('GetWeaponAnimType', 0, 0),
        109:  ('IsWeaponSkillType', 2, 0),
        110:  ('GetCurrentAIPackage', 0, 0),
        111:  ('IsWaiting', 0, 0),
        112:  ('IsIdlePlaying', 0, 0),
        116:  ('IsIntimidatedbyPlayer', 0, 0),
        117:  ('IsPlayerInRegion', 2, 0),
        118:  ('GetActorAggroRadiusViolated', 0, 0),
        122:  ('GetCrime', 2, 1),
        123:  ('IsGreetingPlayer', 0, 0),
        125:  ('IsGuard', 0, 0),
        127:  ('HasBeenEaten', 0, 0),
        128:  ('GetStaminaPercentage', 0, 0),
        129:  ('HasBeenRead', 0, 0),
        130:  ('GetDying', 0, 0),
        131:  ('GetSceneActionPercent', 2, 2),
        132:  ('WouldRefuseCommand', 2, 0),
        133:  ('SameFactionAsPC', 0, 0),
        134:  ('SameRaceAsPC', 0, 0),
        135:  ('SameSexAsPC', 0, 0),
        136:  ('GetIsReference', 2, 0),
        141:  ('IsTalking', 0, 0),
        142:  ('GetComponentCount', 2, 0),
        143:  ('GetCurrentAIProcedure', 0, 0),
        144:  ('GetTrespassWarningLevel', 0, 0),
        145:  ('IsTrespassing', 0, 0),
        146:  ('IsInMyOwnedCell', 0, 0),
        147:  ('GetWindSpeed', 0, 0),
        148:  ('GetCurrentWeatherPercent', 0, 0),
        149:  ('GetIsCurrentWeather', 2, 0),
        150:  ('IsContinuingPackagePCNear', 0, 0),
        152:  ('GetIsCrimeFaction', 2, 0),
        153:  ('CanHaveFlames', 0, 0),
        154:  ('HasFlames', 0, 0),
        157:  ('GetOpenState', 0, 0),
        159:  ('GetSitting', 0, 0),
        161:  ('GetIsCurrentPackage', 2, 0),
        162:  ('IsCurrentFurnitureRef', 2, 0),
        163:  ('IsCurrentFurnitureObj', 2, 0),
        170:  ('GetDayOfWeek', 0, 0),
        172:  ('GetTalkedToPCParam', 2, 0),
        175:  ('IsPCSleeping', 0, 0),
        176:  ('IsPCAMurderer', 0, 0),
        180:  ('HasSameEditorLocationAsRef', 2, 2),
        181:  ('HasSameEditorLocationAsRefAlias', 0, 2),
        182:  ('GetEquipped', 2, 0),
        185:  ('IsSwimming', 0, 0),
        190:  ('GetAmountSoldStolen', 0, 0),
        192:  ('GetIgnoreCrime', 0, 0),
        193:  ('GetPCExpelled', 2, 0),
        195:  ('GetPCFactionMurder', 2, 0),
        197:  ('GetPCEnemyofFaction', 2, 0),
        199:  ('GetPCFactionAttack', 2, 0),
        203:  ('GetDestroyed', 0, 0),
        214:  ('HasMagicEffect', 2, 0),
        215:  ('GetDefaultOpen', 0, 0),
        223:  ('IsSpellTarget', 2, 0),
        224:  ('GetVATSMode', 0, 0),
        225:  ('GetPersuasionNumber', 0, 0),
        226:  ('GetVampireFeed', 0, 0),
        227:  ('GetCannibal', 0, 0),
        228:  ('GetIsClassDefault', 2, 0),
        229:  ('GetClassDefaultMatch', 0, 0),
        230:  ('GetInCellParam', 2, 2),
        231:  ('GetPlayerDialogueInput', 0, 0),
        235:  ('GetVatsTargetHeight', 0, 0),
        237:  ('GetIsGhost', 0, 0),
        242:  ('GetUnconscious', 0, 0),
        244:  ('GetRestrained', 0, 0),
        246:  ('GetIsUsedItem', 2, 0),
        247:  ('GetIsUsedItemType', 2, 0),
        248:  ('IsScenePlaying', 2, 0),
        249:  ('IsInDialogueWithPlayer', 0, 0),
        250:  ('GetLocationCleared', 2, 0),
        254:  ('GetIsPlayableRace', 0, 0),
        255:  ('GetOffersServicesNow', 0, 0),
        258:  ('HasAssociationType', 2, 0),
        259:  ('HasFamilyRelationship', 2, 0),
        261:  ('HasParentRelationship', 2, 0),
        262:  ('IsWarningAbout', 2, 0),
        263:  ('IsWeaponOut', 0, 0),
        264:  ('HasSpell', 2, 0),
        265:  ('IsTimePassing', 0, 0),
        266:  ('IsPleasant', 0, 0),
        267:  ('IsCloudy', 0, 0),
        274:  ('IsSmallBump', 0, 0),
        277:  ('GetBaseValue', 2, 0),
        278:  ('IsOwner', 2, 0),
        280:  ('IsCellOwner', 2, 2),
        282:  ('IsHorseStolen', 0, 0),
        285:  ('IsLeftUp', 0, 0),
        286:  ('IsSneaking', 0, 0),
        287:  ('IsRunning', 0, 0),
        288:  ('GetFriendHit', 0, 0),
        289:  ('IsInCombat', 1, 0),
        300:  ('IsInInterior', 0, 0),
        304:  ('IsWaterObject', 0, 0),
        305:  ('GetPlayerAction', 0, 0),
        306:  ('IsActorUsingATorch', 0, 0),
        309:  ('IsXBox', 0, 0),
        310:  ('GetInWorldspace', 2, 0),
        312:  ('GetPCMiscStat', 0, 0),
        313:  ('GetPairedAnimation', 0, 0),
        314:  ('IsActorAVictim', 0, 0),
        315:  ('GetTotalPersuasionNumber', 0, 0),
        318:  ('GetIdleDoneOnce', 0, 0),
        320:  ('GetNoRumors', 0, 0),
        323:  ('GetCombatState', 0, 0),
        325:  ('GetWithinPackageLocation', 2, 0),
        327:  ('IsRidingMount', 0, 0),
        329:  ('IsFleeing', 0, 0),
        332:  ('IsInDangerousWater', 0, 0),
        338:  ('GetIgnoreFriendlyHits', 0, 0),
        339:  ('IsPlayersLastRiddenMount', 0, 0),
        353:  ('IsActor', 0, 0),
        354:  ('IsEssential', 0, 0),
        358:  ('IsPlayerMovingIntoNewSpace', 0, 0),
        359:  ('GetInCurrentLocation', 2, 0),
        360:  ('GetInCurrentLocationAlias', 0, 0),
        361:  ('GetTimeDead', 0, 0),
        362:  ('HasLinkedRef', 2, 0),
        365:  ('IsChild', 0, 0),
        366:  ('GetStolenItemValueNoCrime', 2, 0),
        367:  ('GetLastPlayerAction', 0, 0),
        368:  ('IsPlayerActionActive', 1, 0),
        370:  ('IsTalkingActivatorActor', 2, 0),
        372:  ('IsInList', 2, 0),
        373:  ('GetStolenItemValue', 2, 0),
        375:  ('GetCrimeGoldViolent', 2, 0),
        376:  ('GetCrimeGoldNonviolent', 2, 0),
        378:  ('IsOwnedBy', 2, 0),
        380:  ('GetCommandDistance', 0, 0),
        381:  ('GetCommandLocationDistance', 0, 0),
        390:  ('GetHitLocation', 0, 0),
        391:  ('IsPC1stPerson', 0, 0),
        396:  ('GetCauseofDeath', 0, 0),
        397:  ('IsLimbGone', 1, 0),
        398:  ('IsWeaponInList', 2, 0),
        402:  ('IsBribedbyPlayer', 0, 0),
        403:  ('GetRelationshipRank', 2, 0),
        # We set the second to 'unused' here to receive it as 4 bytes, which we
        # then handle inside _MelCtdaFo3.
        407:  ('GetVATSValue', 1, 0),
        408:  ('IsKiller', 2, 0),
        409:  ('IsKillerObject', 2, 0),
        410:  ('GetFactionCombatReaction', 2, 2),
        414:  ('Exists', 2, 0),
        415:  ('GetGroupMemberCount', 0, 0),
        416:  ('GetGroupTargetCount', 0, 0),
        426:  ('GetIsVoiceType', 2, 0),
        427:  ('GetPlantedExplosive', 0, 0),
        429:  ('IsScenePackageRunning', 0, 0),
        430:  ('GetHealthPercentage', 0, 0),
        432:  ('GetIsObjectType', 2, 0),
        434:  ('PlayerVisualDetection', 0, 0),
        435:  ('PlayerAudioDetection', 0, 0),
        437:  ('GetIsCreatureType', 1, 0),
        438:  ('HasKey', 2, 0),
        439:  ('IsFurnitureEntryType', 0, 0),
        444:  ('GetInCurrentLocationFormList', 2, 0),
        445:  ('GetInZone', 2, 0),
        446:  ('GetVelocity', 0, 0),
        447:  ('GetGraphVariableFloat', 0, 0),
        448:  ('HasPerk', 2, 0),
        449:  ('GetFactionRelation', 2, 0),
        450:  ('IsLastIdlePlayed', 2, 0),
        453:  ('GetPlayerTeammate', 0, 0),
        454:  ('GetPlayerTeammateCount', 0, 0),
        458:  ('GetActorCrimePlayerEnemy', 0, 0),
        459:  ('GetCrimeGold', 2, 0),
        463:  ('IsPlayerGrabbedRef', 2, 0),
        465:  ('GetKeywordItemCount', 2, 0),
        470:  ('GetDestructionStage', 0, 0),
        473:  ('GetIsAlignment', 1, 0),
        476:  ('IsProtected', 0, 0),
        477:  ('GetThreatRatio', 2, 0),
        479:  ('GetIsUsedItemEquipType', 1, 0),
        483:  ('GetPlayerActivated', 0, 0),
        485:  ('GetFullyEnabledActorsInHigh', 0, 0),
        487:  ('IsCarryable', 0, 0),
        488:  ('GetConcussed', 0, 0),
        491:  ('GetMapMarkerVisible', 0, 0),
        493:  ('PlayerKnows', 2, 0),
        494:  ('GetPermanentValue', 2, 0),
        495:  ('GetKillingBlowLimb', 0, 0),
        497:  ('CanPayCrimeGold', 2, 0),
        499:  ('GetDaysInJail', 0, 0),
        500:  ('EPAlchemyGetMakingPoison', 0, 0),
        501:  ('EPAlchemyEffectHasKeyword', 2, 0),
        503:  ('GetAllowWorldInteractions', 0, 0),
        506:  ('DialogueGetAv', 2, 0),
        507:  ('DialogueHasPerk', 2, 0),
        508:  ('GetLastHitCritical', 0, 0),
        510:  ('DialogueGetItemCount', 2, 0),
        511:  ('LastCrippledCondition', 2, 0),
        512:  ('HasSharedPowerGrid', 2, 0),
        513:  ('IsCombatTarget', 2, 0),
        515:  ('GetVATSRightAreaFree', 2, 0),
        516:  ('GetVATSLeftAreaFree', 2, 0),
        517:  ('GetVATSBackAreaFree', 2, 0),
        518:  ('GetVATSFrontAreaFree', 2, 0),
        519:  ('GetIsLockBroken', 0, 0),
        520:  ('IsPS3', 0, 0),
        521:  ('IsWindowsPC', 0, 0),
        522:  ('GetVATSRightTargetVisible', 2, 0),
        523:  ('GetVATSLeftTargetVisible', 2, 0),
        524:  ('GetVATSBackTargetVisible', 2, 0),
        525:  ('GetVATSFrontTargetVisible', 2, 0),
        528:  ('IsInCriticalStage', 0, 0),
        530:  ('GetXPForNextLevel', 0, 0),
        533:  ('GetInfamy', 2, 0),
        534:  ('GetInfamyViolent', 2, 0),
        535:  ('GetInfamyNonViolent', 2, 0),
        536:  ('GetTypeCommandPerforming', 0, 0),
        543:  ('GetQuestCompleted', 2, 0),
        544:  ('GetSpeechChallengeSuccessLevel', 0, 0),
        547:  ('IsGoreDisabled', 0, 0),
        550:  ('IsSceneActionComplete', 2, 2),
        552:  ('GetSpellUsageNum', 2, 0),
        554:  ('GetActorsInHigh', 0, 0),
        555:  ('HasLoaded3D', 0, 0),
        560:  ('HasKeyword', 2, 0),
        561:  ('HasRefType', 0, 0),
        562:  ('LocationHasKeyword', 2, 0),
        563:  ('LocationHasRefType', 0, 0),
        565:  ('GetIsEditorLocation', 2, 0),
        566:  ('GetIsAliasRef', 0, 0),
        567:  ('GetIsEditorLocationAlias', 0, 0),
        568:  ('IsSprinting', 0, 0),
        569:  ('IsBlocking', 0, 0),
        570:  ('HasEquippedSpell', 0, 0),
        571:  ('GetCurrentCastingType', 0, 0),
        572:  ('GetCurrentDeliveryType', 0, 0),
        574:  ('GetAttackState', 0, 0),
        576:  ('GetEventData', 0, 0),
        577:  ('IsCloserToAThanB', 2, 2),
        578:  ('LevelMinusPCLevel', 0, 0),
        580:  ('IsBleedingOut', 0, 0),
        584:  ('GetRelativeAngle', 2, 0),
        589:  ('GetMovementDirection', 0, 0),
        590:  ('IsInScene', 0, 0),
        591:  ('GetRefTypeDeadCount', 2, 0),
        592:  ('GetRefTypeAliveCount', 2, 0),
        594:  ('GetIsFlying', 0, 0),
        595:  ('IsCurrentSpell', 2, 0),
        596:  ('SpellHasKeyword', 0, 2),
        597:  ('GetEquippedItemType', 0, 0),
        598:  ('GetLocationAliasCleared', 0, 0),
        600:  ('GetLocationAliasRefTypeDeadCount', 0, 0),
        601:  ('GetLocationAliasRefTypeAliveCount', 0, 0),
        602:  ('IsWardState', 0, 0),
        603:  ('IsInSameCurrentLocationAsRef', 2, 2),
        604:  ('IsInSameCurrentLocationAsRefAlias', 0, 2),
        605:  ('LocationAliasIsLocation', 0, 2),
        606:  ('GetKeywordDataForLocation', 2, 2),
        608:  ('GetKeywordDataForAlias', 0, 2),
        610:  ('LocationAliasHasKeyword', 0, 2),
        611:  ('IsNullPackageData', 0, 0),
        612:  ('GetNumericPackageData', 1, 0),
        613:  ('IsPlayerRadioOn', 0, 0),
        614:  ('GetPlayerRadioFrequency', 0, 0),
        615:  ('GetHighestRelationshipRank', 0, 0),
        616:  ('GetLowestRelationshipRank', 0, 0),
        617:  ('HasAssociationTypeAny', 0, 0),
        618:  ('HasFamilyRelationshipAny', 0, 0),
        619:  ('GetPathingTargetOffset', 0, 0),
        620:  ('GetPathingTargetAngleOffset', 0, 0),
        621:  ('GetPathingTargetSpeed', 0, 0),
        622:  ('GetPathingTargetSpeedAngle', 0, 0),
        623:  ('GetMovementSpeed', 0, 0),
        624:  ('GetInContainer', 2, 0),
        625:  ('IsLocationLoaded', 2, 0),
        626:  ('IsLocationAliasLoaded', 0, 0),
        627:  ('IsDualCasting', 0, 0),
        629:  ('GetVMQuestVariable', 2, 0),
        630:  ('GetCombatAudioDetection', 0, 0),
        631:  ('GetCombatVisualDetection', 0, 0),
        632:  ('IsCasting', 0, 0),
        633:  ('GetFlyingState', 0, 0),
        635:  ('IsInFavorState', 0, 0),
        636:  ('HasTwoHandedWeaponEquipped', 0, 0),
        637:  ('IsFurnitureExitType', 0, 0),
        638:  ('IsInFriendStatewithPlayer', 0, 0),
        639:  ('GetWithinDistance', 2, 3),
        640:  ('GetValuePercent', 2, 0),
        641:  ('IsUnique', 0, 0),
        642:  ('GetLastBumpDirection', 0, 0),
        644:  ('GetInfoChallangeSuccess', 0, 0),
        645:  ('GetIsInjured', 0, 0),
        646:  ('GetIsCrashLandRequest', 0, 0),
        647:  ('GetIsHastyLandRequest', 0, 0),
        650:  ('IsLinkedTo', 2, 2),
        651:  ('GetKeywordDataForCurrentLocation', 2, 0),
        652:  ('GetInSharedCrimeFaction', 2, 0),
        654:  ('GetBribeSuccess', 0, 0),
        655:  ('GetIntimidateSuccess', 0, 0),
        656:  ('GetArrestedState', 0, 0),
        657:  ('GetArrestingActor', 0, 0),
        659:  ('HasVMScript', 0, 0),
        660:  ('GetVMScriptVariable', 0, 0),
        661:  ('GetWorkshopResourceDamage', 2, 0),
        664:  ('HasValidRumorTopic', 2, 0),
        672:  ('IsAttacking', 0, 0),
        673:  ('IsPowerAttacking', 0, 0),
        674:  ('IsLastHostileActor', 0, 0),
        675:  ('GetGraphVariableInt', 0, 0),
        678:  ('ShouldAttackKill', 2, 0),
        680:  ('GetActivationHeight', 0, 0),
        682:  ('WornHasKeyword', 2, 0),
        683:  ('GetPathingCurrentSpeed', 0, 0),
        684:  ('GetPathingCurrentSpeedAngle', 0, 0),
        691:  ('GetWorkshopObjectCount', 2, 0),
        693:  ('EPMagic_SpellHasKeyword', 2, 0),
        694:  ('GetNoBleedoutRecovery', 0, 0),
        696:  ('EPMagic_SpellHasSkill', 2, 0),
        697:  ('IsAttackType', 2, 0),
        698:  ('IsAllowedToFly', 0, 0),
        699:  ('HasMagicEffectKeyword', 2, 0),
        700:  ('IsCommandedActor', 0, 0),
        701:  ('IsStaggered', 0, 0),
        702:  ('IsRecoiling', 0, 0),
        703:  ('HasScopeWeaponEquipped', 0, 0),
        704:  ('IsPathing', 0, 0),
        705:  ('GetShouldHelp', 2, 0),
        706:  ('HasBoundWeaponEquipped', 0, 0),
        707:  ('GetCombatTargetHasKeyword', 2, 0),
        709:  ('GetCombatGroupMemberCount', 0, 0),
        710:  ('IsIgnoringCombat', 0, 0),
        711:  ('GetLightLevel', 0, 0),
        713:  ('SpellHasCastingPerk', 2, 0),
        714:  ('IsBeingRidden', 0, 0),
        715:  ('IsUndead', 0, 0),
        716:  ('GetRealHoursPassed', 0, 0),
        718:  ('IsUnlockedDoor', 0, 0),
        719:  ('IsHostileToActor', 2, 0),
        720:  ('GetTargetHeight', 2, 0),
        721:  ('IsPoison', 0, 0),
        722:  ('WornApparelHasKeywordCount', 2, 0),
        723:  ('GetItemHealthPercent', 0, 0),
        724:  ('EffectWasDualCast', 0, 0),
        725:  ('GetKnockStateEnum', 0, 0),
        726:  ('DoesNotExist', 0, 0),
        728:  ('GetPlayerWalkAwayFromDialogueScene', 0, 0),
        729:  ('GetActorStance', 0, 0),
        734:  ('CanProduceForWorkshop', 0, 0),
        735:  ('CanFlyHere', 0, 0),
        736:  ('EPIsDamageType', 1, 0),
        738:  ('GetActorGunState', 0, 0),
        739:  ('GetVoiceLineLength', 0, 0),
        741:  ('ObjectTemplateItem_HasKeyword', 2, 0),
        742:  ('ObjectTemplateItem_HasUniqueKeyword', 2, 0),
        743:  ('ObjectTemplateItem_GetLevel', 0, 0),
        744:  ('MovementIdleMatches', 0, 0),
        745:  ('GetActionData', 0, 0),
        746:  ('GetActionDataShort', 1, 0),
        747:  ('GetActionDataByte', 1, 0),
        748:  ('GetActionDataFlag', 1, 0),
        749:  ('ModdedItemHasKeyword', 2, 0),
        750:  ('GetAngryWithPlayer', 0, 0),
        751:  ('IsCameraUnderWater', 0, 0),
        753:  ('IsActorRefOwner', 2, 0),
        754:  ('HasActorRefOwner', 2, 0),
        756:  ('GetLoadedAmmoCount', 0, 0),
        757:  ('IsTimeSpanSunrise', 0, 0),
        758:  ('IsTimeSpanMorning', 0, 0),
        759:  ('IsTimeSpanAfternoon', 0, 0),
        760:  ('IsTimeSpanEvening', 0, 0),
        761:  ('IsTimeSpanSunset', 0, 0),
        762:  ('IsTimeSpanNight', 0, 0),
        763:  ('IsTimeSpanMidnight', 0, 0),
        764:  ('IsTimeSpanAnyDay', 0, 0),
        765:  ('IsTimeSpanAnyNight', 0, 0),
        766:  ('CurrentFurnitureHasKeyword', 2, 0),
        767:  ('GetWeaponEquipIndex', 0, 0),
        769:  ('IsOverEncumbered', 0, 0),
        770:  ('IsPackageRequestingBlockedIdles', 0, 0),
        771:  ('GetActionDataInt', 0, 0),
        772:  ('GetVATSRightMinusLeftAreaFree', 2, 0),
        773:  ('GetInIronSights', 2, 0),
        774:  ('GetActorStaggerDirection', 0, 0),
        775:  ('GetActorStaggerMagnitude', 0, 0),
        776:  ('WornCoversBipedSlot', 1, 0),
        777:  ('GetInventoryValue', 0, 0),
        778:  ('IsPlayerInConversation', 0, 0),
        779:  ('IsInDialogueCamera', 0, 0),
        780:  ('IsMyDialogueTargetPlayer', 0, 0),
        781:  ('IsMyDialogueTargetActor', 0, 0),
        782:  ('GetMyDialogueTargetDistance', 0, 0),
        783:  ('IsSeatOccupied', 2, 0),
        784:  ('IsPlayerRiding', 0, 0),
        785:  ('IsTryingEventCamera', 0, 0),
        786:  ('UseLeftSideCamera', 0, 0),
        787:  ('GetNoteType', 0, 0),
        788:  ('LocationHasPlayerOwnedWorkshop', 0, 0),
        789:  ('IsStartingAction', 0, 0),
        790:  ('IsMidAction', 0, 0),
        791:  ('IsWeaponChargeAttack', 0, 0),
        792:  ('IsInWorkshopMode', 0, 0),
        793:  ('IsWeaponChargingHoldAttack', 0, 0),
        794:  ('IsEncounterAbovePlayerLevel', 0, 0),
        795:  ('IsMeleeAttacking', 0, 0),
        796:  ('GetVATSQueuedTargetsUnique', 0, 0),
        797:  ('GetCurrentLocationCleared', 0, 0),
        798:  ('IsPowered', 0, 0),
        799:  ('GetTransmitterDistance', 0, 0),
        800:  ('GetCameraPlaybackTime', 0, 0),
        801:  ('IsInWater', 0, 0),
        802:  ('GetWithinActivateDistance', 2, 0),
        803:  ('IsUnderWater', 0, 0),
        804:  ('IsInSameSpace', 2, 0),
        805:  ('LocationAllowsReset', 0, 0),
        806:  ('GetVATSBackRightAreaFree', 2, 0),
        807:  ('GetVATSBackLeftAreaFree', 2, 0),
        808:  ('GetVATSBackRightTargetVisible', 2, 0),
        809:  ('GetVATSBackLeftTargetVisible', 2, 0),
        810:  ('GetVATSTargetLimbVisible', 2, 0),
        811:  ('IsPlayerListening', 3, 0),
        812:  ('GetPathingRequestedQuickTurn', 0, 0),
        813:  ('EPIsCalculatingBaseDamage', 0, 0),
        814:  ('GetReanimating', 0, 0),
        817:  ('IsInRobotWorkbench', 0, 0),
    }
    getvatsvalue_index = 407

    #--------------------------------------------------------------------------
    # Leveled Lists
    #--------------------------------------------------------------------------
    listTypes = (b'LVLI', b'LVLN', b'LVSP')

    #--------------------------------------------------------------------------
    # Import Inventory
    #--------------------------------------------------------------------------
    inventoryTypes = (b'NPC_', b'CONT')

    #--------------------------------------------------------------------------
    # Import Object Bounds
    #--------------------------------------------------------------------------
    object_bounds_types = {b'LVLI', b'LVLN', b'LVSP'}

    #--------------------------------------------------------------------------
    # Timescale Checker
    #--------------------------------------------------------------------------
    default_wp_timescale = 20

    # ------------------------------------------------------------------------------
    # Tweak Settings
    # ------------------------------------------------------------------------------
    settings_tweaks = {
        'GlobalsTweak_Timescale_Tes5',
        'GmstTweak_Actor_GreetingDistance',
        'GmstTweak_Actor_MaxCompanions',
        'GmstTweak_Actor_MaxJumpHeight',
        'GmstTweak_Actor_MerchantRestockTime',
        'GmstTweak_Actor_StrengthEncumbranceMultiplier',
        'GmstTweak_Actor_UnconsciousnessDuration',
        'GmstTweak_Actor_VerticalObjectDetection',
        'GmstTweak_AI_BumpReactionDelay',
        'GmstTweak_AI_ConversationChance_Interior',
        'GmstTweak_AI_ConversationChance_Tes5',
        'GmstTweak_AI_MaxActiveActors_Tes5',
        'GmstTweak_AI_MaxDeadActors',
        'GmstTweak_Combat_CriticalHitChance',
        'GmstTweak_Combat_DisableProjectileDodging',
        'GmstTweak_Combat_MaxActors_Tes5',
        'GmstTweak_Compass_RecognitionDistance',
        'GmstTweak_Gore_CombatDismemberPartChance_Fo4',
        'GmstTweak_Gore_CombatExplodePartChance_Fo4',
        'GmstTweak_Gore_CombatTorsoExplodeChance',
        'GmstTweak_Hacking_MaximumNumberOfWords',
        'GmstTweak_Msg_CarryingTooMuch',
        'GmstTweak_Msg_NoFastTravel',
        'GmstTweak_Msg_QuickLoad',
        'GmstTweak_Msg_QuickSave',
        'GmstTweak_Player_FallDamageThreshold',
        'GmstTweak_Player_FastTravelTimeMultiplier',
        'GmstTweak_Player_InventoryQuantityPrompt',
        'GmstTweak_Player_MaxDraggableWeight',
        'GmstTweak_Player_SprintingCost',
        'GmstTweak_Visuals_TerminalDisplayRate',
        'GmstTweak_Warning_ExteriorDistanceToHostiles',
        'GmstTweak_Warning_InteriorDistanceToHostiles',
    }

    top_groups = [
        b'GMST', b'KYWD', b'LCRT', b'AACT', b'TRNS', b'CMPO', b'TXST', b'GLOB',
        b'DMGT', b'CLAS', b'FACT', b'HDPT', b'EYES', b'RACE', b'SOUN', b'ASPC',
        b'MGEF', b'LTEX', b'ENCH', b'SPEL', b'ACTI', b'TACT', b'ARMO', b'BOOK',
        b'CONT', b'DOOR', b'INGR', b'LIGH', b'MISC', b'STAT', b'SCOL', b'MSTT',
        b'GRAS', b'TREE', b'FLOR', b'FURN', b'WEAP', b'AMMO', b'NPC_', b'LVLN',
        b'KEYM', b'ALCH', b'IDLM', b'NOTE', b'PROJ', b'HAZD', b'BNDS', b'TERM',
        b'LVLI', b'WTHR', b'CLMT', b'SPGD', b'RFCT', b'REGN', b'NAVI', b'CELL',
        b'WRLD', b'QUST', b'IDLE', b'PACK', b'CSTY', b'LSCR', b'LVSP', b'ANIO',
        b'WATR', b'EFSH', b'EXPL', b'DEBR', b'IMGS', b'IMAD', b'FLST', b'PERK',
        b'BPTD', b'ADDN', b'AVIF', b'CAMS', b'CPTH', b'VTYP', b'MATT', b'IPCT',
        b'IPDS', b'ARMA', b'ECZN', b'LCTN', b'MESG', b'DOBJ', b'DFOB', b'LGTM',
        b'MUSC', b'FSTP', b'FSTS', b'SMBN', b'SMQN', b'SMEN', b'DLBR', b'MUST',
        b'DLVW', b'EQUP', b'RELA', b'SCEN', b'ASTP', b'OTFT', b'ARTO', b'MATO',
        b'MOVT', b'SNDR', b'DUAL', b'SNCT', b'SOPM', b'COLL', b'CLFM', b'REVB',
        b'PKIN', b'RFGP', b'AMDL', b'LAYR', b'COBJ', b'OMOD', b'MSWP', b'ZOOM',
        b'INNR', b'KSSM', b'AECH', b'SCCO', b'AORU', b'SCSN', b'STAG', b'NOCM',
        b'LENS', b'GDRY', b'OVIS']

    @classmethod
    def init(cls, _package_name=None):
        super().init(_package_name or __name__)
        cls._validate_records(__name__)

    @classmethod
    def _validate_records(cls, package_name, plugin_form_vers=131):
        from .. import brec
        header_type = brec.RecordHeader
        header_type.valid_header_sigs |= {b'DIAL'}
        # DMGT\DNAM changed completely in Form Version 78 and it's not possible
        # to upgrade it (unless someone reverse engineers what the game does to
        # it when loading)
        header_type.skip_form_version_upgrade = {b'DMGT'}
        # package name is fallout4 here
        super()._validate_records(package_name, plugin_form_vers)
        cls.mergeable_sigs = set(cls.top_groups) - { # that's what it said
            b'CELL',
            b'LVSP', b'MATO',
            b'MATT', b'MESG', b'MGEF', b'MISC', b'MOVT', b'MSTT', b'MSWP',
            b'MUSC', b'MUST', b'NAVI', b'NOCM', b'NOTE', b'NPC_', b'OMOD',
            b'OTFT', b'OVIS', b'PACK', b'PKIN', b'PROJ', b'QUST', b'RACE',
            b'REGN', b'RELA', b'REVB', b'RFCT', b'RFGP', b'SCCO', b'SCEN',
            b'SCOL', b'SCSN', b'SMBN', b'SMEN', b'SMQN', b'SNCT', b'SNDR',
            b'SOPM', b'SOUN', b'SPEL', b'SPGD', b'STAG', b'STAT', b'TACT',
            b'TERM', b'TREE', b'TRNS', b'TXST', b'VTYP', b'WATR', b'WEAP',
            b'WRLD', b'WTHR', b'ZOOM'}
        brec.RecordType.simpleTypes = cls.mergeable_sigs

GAME_TYPE = Fallout4GameInfo
