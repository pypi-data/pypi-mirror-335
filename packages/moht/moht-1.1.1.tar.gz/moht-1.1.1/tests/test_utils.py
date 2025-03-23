import os
import stat
from os import linesep, path, remove, sep
from pathlib import Path
from sys import platform
from tempfile import gettempdir
from unittest.mock import call, patch

from pytest import mark

from moht import utils


def test_parse_cleaning_success():
    err = ''
    out = f'{linesep}CLEANING: "FLG - Balmora\'s Underworld V1.1.esp" ...{linesep}' \
          f'Loaded cached Master: <DATADIR>/morrowind.esm{linesep}' \
          f'Loaded cached Master: <DATADIR>/tribunal.esm{linesep}' \
          f'Loaded cached Master: <DATADIR>/bloodmoon.esm{linesep}' \
          f' Cleaned duplicate record (STAT): in_dwrv_corr3_02{linesep}' \
          f' Cleaned redundant AMBI,WHGT from CELL: omaren ancestral tomb{linesep}' \
          f'Output saved in: "1/FLG - Balmora\'s Underworld V1.1.esp"{linesep}' \
          f'Original unaltered: "FLG - Balmora\'s Underworld V1.1.esp"{linesep}{linesep}' \
          f'Cleaning Stats for "FLG - Balmora\'s Underworld V1.1.esp":{linesep}' \
          f'                duplicate record:     1{linesep}' \
          f'             redundant CELL.AMBI:     1{linesep}' \
          f'             redundant CELL.WHGT:     1{linesep}'
    assert utils.parse_cleaning(out, err, "FLG - Balmora's Underworld V1.1.esp") == (True, 'saved')


def test_parse_cleaning_not_modified():
    err = ''
    out = """CLEANING: "FLG - Balmora's Underworld V1.1.esp" ...
Loaded cached Master: <DATADIR>/morrowind.esm
Loaded cached Master: <DATADIR>/tribunal.esm
Loaded cached Master: <DATADIR>/bloodmoon.esm
FLG - Balmora's Underworld V1.1.esp was not modified"""
    assert utils.parse_cleaning(out, err, "FLG - Balmora's Underworld V1.1.esp") == (False, 'not modified')


def test_parse_cleaning_no_1_master():
    err = """Use of uninitialized value in -s at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 6282.
Use of uninitialized value $curr_size in numeric eq (==) at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 6283.
Use of uninitialized value $curr_size in concatenation (.) or string at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 6287.
Cache Invalidated for: oaab_data.esm (curr_size == , prev_size == 1269934) at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 6287.

[ERROR (Caldera.esp): Master: oaab_data.esm not found in <DATADIR>]"""
    out = """CLEANING: "Caldera.esp" ...
Loaded cached Master: <DATADIR>/morrowind.esm
Loaded cached Master: <DATADIR>/tribunal.esm
Loaded cached Master: <DATADIR>/bloodmoon.esm
Loading Master: oaab_data.esm
Caldera.esp was not modified"""
    assert utils.parse_cleaning(out, err, 'Caldera.esp') == (False, 'oaab_data.esm not found')


def test_parse_cleaning_no_2_master():
    err = """[ERROR (Library of Vivec Overhaul - Full.esp): Master: tamriel_data.esm not found in <DATADIR>]
[ERROR (Library of Vivec Overhaul - Full.esp): Master: oaab_data.esm not found in <DATADIR>]"""
    out = """CLEANING: "Library of Vivec Overhaul - Full.esp" ...
Loading Master: morrowind.esm
Loading Master: tribunal.esm
Loading Master: bloodmoon.esm
Loading Master: tamriel_data.esm
Loading Master: oaab_data.esm
 Cleaned duplicate object instance (in_velothismall_ndoor_01 FRMR: 482716) from CELL: vivec, hall of wisdom
 Cleaned redundant AMBI,WHGT from CELL: vivec, hall of wisdom
 Cleaned redundant AMBI,WHGT from CELL: vivec, library of vivec
Output saved in: "1/Library of Vivec Overhaul - Full.esp"
Original unaltered: "Library of Vivec Overhaul - Full.esp"
Cleaning Stats for "Library of Vivec Overhaul - Full.esp":
       duplicate object instance:     1
             redundant CELL.AMBI:     2
             redundant CELL.WHGT:     2"""
    assert utils.parse_cleaning(out, err, 'Library of Vivec Overhaul - Full.esp') == (False, 'tamriel_data.esm not found**oaab_data.esm not found')


def test_parse_cleaning_check_bin_no_config_inifiles():
    err = """Can't locate Config/IniFiles.pm in @INC (you may need to install the Config::IniFiles module) (@INC contains: /usr/lib/perl5/5.36/site_perl /usr/share/perl5/site_perl /usr/lib/perl5/5.36/vendor_perl /usr/share/perl5/vendor_perl /usr/lib/perl5/5.36/core_perl /usr/share/perl5/core_perl) at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 107.
BEGIN failed--compilation aborted at /home/emc/git/Modding-OpenMW/modhelpertool/moht/resources/tes3cmd-0.37w line 107."""
    out = ''
    assert utils.parse_cleaning(out, err, 'Caldera.esp') == (False, 'Config::IniFiles module')


def test_parse_cleaning_check_bin_ok():
    err = """WARNING: Can't find "Data Files" directory, functionality reduced. You should first cd (change directory) to somewhere under where Morrowind is installed.
Usage: tes3cmd COMMAND OPTIONS plugin...
VERSION: 0.37w
tes3cmd is a low-level command line tool that can examine, edit, and delete
records from a TES3 plugin for Morrowind. It can also generate various patches
and clean plugins too.
COMMANDS
  active
    Add/Remove/List Plugins in your load order.
  clean
    Clean plugins of Evil GMSTs, junk cells, and more.
  common
    Find record IDs common between two plugins."""
    out = ''
    assert utils.parse_cleaning(out, err, 'Caldera.esp') == (True, 'Usage')


def test_run_cmd():
    tes3cmd = 'tes3cmd-0.37v.exe' if platform == 'win32' else 'tes3cmd-0.37w'
    up_res = f'..{sep}moht{sep}resources{sep}'
    plugin = 'some_plugin.esp'
    cmd = f'{path.join(utils.here(__file__), up_res, tes3cmd)} clean {plugin}'
    out, err = utils.run_cmd(cmd)
    cleaning, reason = utils.parse_cleaning(out, err, plugin)
    assert cleaning is False
    if reason == 'Not tes3cmd':
        assert out == f'{linesep}CLEANING: "{plugin}" ...{linesep}'
        assert f'FATAL ERROR ({plugin}): Invalid input file (No such file or directory)' in err
    else:
        assert reason == 'Config::IniFiles module'


@mark.parametrize('local_ver, out_err, result', [
    ('0.37.0', ("""Collecting tox==3.25.1
  Using cached tox-3.25.1-py2.py3-none-any.whl (85 kB)
Collecting wheel==0.37.1
  Using cached wheel-0.37.1-py2.py3-none-any.whl (35 kB)
Requirement already satisfied: pluggy>=0.12.0 in /home/emc/.pyenv/versions/3.10.5/envs/moth310/lib/python3.10/site-packages (from tox==3.25.1) (1.0.0)
Would install tox-3.25.1 wheel-0.37.1""", ''), (False, 'Update available: 0.37.1')),
    ('0.37.1', ('Requirement already satisfied: wheel==0.37.1 in /home/emc/.pyenv/versions/3.10.5/envs/moth310/lib/python3.10/site-packages (0.37.1)', ''), (True, 'No updates')),
])
def test_is_latest_ver_success(local_ver, out_err, result):
    with patch.object(utils, 'run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = out_err
        assert utils.is_latest_ver('wheel', current_ver=local_ver) == result
        run_cmd_mock.assert_called_once_with('pip install --dry-run --no-color --timeout 3 --retries 1 --progress-bar off --upgrade wheel')


@mark.parametrize('local_ver, effect, result', [
    ('0.37.1', [('', """Usage:
  pip install [options] <requirement specifier> [package-index-options] ...
  pip install [options] -r <requirements file> [package-index-options] ...
  pip install [options] [-e] <vcs project url> ...
  pip install [options] [-e] <local project path> ...
  pip install [options] <archive url/path> ...

no such option: --dry-run
"""), ('', '')], (True, 'Version check failed, unknown switch: --dry-run')),
    ('0.37.1', [('', """Usage:
  pip install [options] <requirement specifier> [package-index-options] ...
  pip install [options] -r <requirements file> [package-index-options] ...
  pip install [options] [-e] <vcs project url> ...
  pip install [options] [-e] <local project path> ...
  pip install [options] <archive url/path> ...

no such option: --dry-run
"""), ("""Package      Version
------------ -------
packaging    21.3
pip          22.2
wheel        0.37.1
platformdirs 2.5.2
pluggy       1.0.0
""", '')], (True, 'Version check failed, old pip: 22.2')),
])
def test_is_latest_ver_check_failed(local_ver, effect, result):
    with patch.object(utils, 'run_cmd', side_effect=effect) as run_cmd_mock:
        assert utils.is_latest_ver('wheel', current_ver=local_ver) == result
        run_cmd_mock.assert_has_calls([call('pip install --dry-run --no-color --timeout 3 --retries 1 --progress-bar off --upgrade wheel'),
                                       call('pip list')])


def test_here():
    assert utils.here(__file__) == path.abspath(path.dirname(__file__))
    assert utils.here('../log.py') == path.abspath(path.dirname('../log.py'))


def test_extract_filename_pathlib():
    assert utils.extract_filename(Path('/home/user/file.txt')) == 'file.txt'
    assert utils.extract_filename(Path('C:/Users/mplic/file.txt')) == 'file.txt'


@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
def test_extract_filename_string_linux():
    assert utils.extract_filename('/home/user/file.txt') == 'file.txt'


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_extract_filename_string_windows():
    assert utils.extract_filename('C:\\Users\\mplic\\file.txt') == 'file.txt'


def test_get_all_plugins():
    return_val = ('/home', ('user',), ('user2',)), ('/home/user', (), ('plugin1.esp', 'plugin2.esm')),
    with patch.object(utils, 'walk', return_value=return_val):
        assert utils.get_all_plugins(mods_dir='/home') == [Path('/home/user/plugin1.esp'), Path('/home/user/plugin2.esm')]


def test_get_required_esm():
    plugins = [Path('/home/user/OAAB - Foyada Mamaea.ESP'), Path("/home/user/Building Up Uvirith's Legacy1.1.ESP")]
    with patch.object(utils, 'run_cmd') as run_cmd_mock:
        run_cmd_mock.side_effect = [('Morrowind.esm\nTribunal.esm\n', ''),
                                    ('Morrowind.esm\nTribunal.esm\nBloodmoon.esm\nOAAB_Data.esm\n', '')]
        assert utils.get_required_esm(plugins=plugins, omwcwd='omwcwd') == {'Morrowind.esm', 'Tribunal.esm', 'Bloodmoon.esm', 'OAAB_Data.esm'}


def test_get_required_esm_not_on_plugin_list():
    plugins = [Path('/home/user/Aldruhn/Ald-ruhn.esp')]
    with patch.object(utils, 'run_cmd') as run_cmd_mock:
        run_cmd_mock.return_value = '', ''
        assert utils.get_required_esm(plugins=plugins, omwcwd='omwcwd') == set()


@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
@mark.parametrize('dir_path', ['/home/user/mods', Path('/home/user/mods')], ids=['string', 'path like object'])
def test_rm_dirs_with_subdirs_linux(dir_path):
    with patch.object(utils, 'rmtree') as rmtree_mock:
        utils.rm_dirs_with_subdirs(dir_path, ['plugin1', 'plugin2'])
        rmtree_mock.assert_has_calls([call(Path('/home/user/mods/plugin1'), ignore_errors=True),
                                      call(Path('/home/user/mods/plugin2'), ignore_errors=True)])


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
@mark.parametrize('dir_path', ['C:\\Users\\mplic\\mods', Path('C:\\Users\\mplic\\mods')], ids=['string', 'path like object'])
def test_rm_dirs_with_subdirs_windows(dir_path):
    with patch.object(utils, 'rmtree') as rmtree_mock:
        utils.rm_dirs_with_subdirs(dir_path, ['plugin1', 'plugin2'])
        rmtree_mock.assert_has_calls([call(Path('C:\\Users\\mplic\\mods\\plugin1'), ignore_errors=True),
                                      call(Path('C:\\Users\\mplic\\mods\\plugin2'), ignore_errors=True)])


def test_find_missing_esm():
    side_effect = [
        [
            ('/home', ('user1', 'user2'), ()),
            ('/home/user1', ('mods', 'datafiles'), ()),
            ('/home/user1/datafiles', ('plugin3',), ('plugin3.esm', 'plugin4.esm', 'plugin4.esm'))
        ],
        [
            ('/home', ('user1', 'user2'), ()),
            ('/home/user1', ('mods', 'datafiles'), ()),
            ('/home/user1/mods', (), ('plugin1.esm', 'plugin2.esm', 'plugin3.esp', 'plugin5.esm'))]
    ]
    with patch.object(utils, 'walk', side_effect=side_effect):
        result = utils.find_missing_esm(dir_path='/home/user1/mods',
                                        data_files='/home/user1/datafiles',
                                        esm_files={'plugin1.esm', 'plugin2.esm', 'plugin3.esm', 'plugin4.esm'})
        assert result == [Path('/home/user1/mods/plugin1.esm'),
                          Path('/home/user1/mods/plugin2.esm')]


def test_copy_filelist():
    with patch.object(utils, 'copy2') as copy2_mock:
        utils.copy_filelist(file_list=[Path('/home/user/mods/plugin1.esm'), Path('/home/user/mods/plugin2.esm')], dest_dir='/home/user/datafiles')
        copy2_mock.assert_has_calls([call(Path('/home/user/mods/plugin1.esm'), '/home/user/datafiles'),
                                     call(Path('/home/user/mods/plugin2.esm'), '/home/user/datafiles')])


@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
def test_rm_copied_extra_ems_linux():
    with patch.object(utils, 'remove') as remove_mock:
        utils.rm_copied_extra_esm(esm=[Path('/home/user/mods/plugin1.esm'), Path('/home/user/mods/plugin2.esm')], data_files='/home/user/datafiles')
        remove_mock.assert_has_calls([call('/home/user/datafiles/plugin1.esm'), call('/home/user/datafiles/plugin2.esm')])


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_rm_copied_extra_ems_windows():
    with patch.object(utils, 'remove') as remove_mock:
        utils.rm_copied_extra_esm(esm=[Path('C:\\Users\\mplic\\mods\\plugin1.esm'), Path('C:\\Users\\mplic\\mods\\plugin2.esm')], data_files='C:\\Users\\mplic\\datafiles')
        remove_mock.assert_has_calls([call('C:\\Users\\mplic\\datafiles\\plugin1.esm'), call('C:\\Users\\mplic\\datafiles\\plugin2.esm')])


def test_rm_copied_extra_esm_exception_handling():
    with patch.object(utils, 'remove', side_effect=FileNotFoundError):
        utils.rm_copied_extra_esm(esm=[Path('/home/user/mods/plugin1.esm'), Path('/home/user/mods/plugin2.esm')], data_files='/home/user/datafiles')


@mark.parametrize('args, result', [
    ((9.50, '%M:%S'), '00:09'),
    ((9.50, '%S'), '09'),
    ((19.24, '%M:%S'), '00:19'),
    ((19.24, '%S'), '19'),
    ((58.1, '%M:%S'), '00:58'),
    ((128.95, '%M:%S'), '02:08'),
    ((453.83, '%M:%S'), '07:33'),
    ((453.83, '%H:%M:%S'), '00:07:33'),
])
def test_get_string_duration(args, result):
    assert utils.get_string_duration(*args) == result


def test_read_write_yaml_cfg_file():
    test_tmp_yaml = path.join(gettempdir(), 'c.yaml')
    cfg = {'setting_1': {'setting_2': 2}}
    utils.write_config(cfg, test_tmp_yaml)
    d_cfg = utils.read_config(test_tmp_yaml)
    assert d_cfg == cfg
    with open(test_tmp_yaml, 'w+') as f:
        f.write(',')
    d_cfg = utils.read_config(test_tmp_yaml)
    assert len(d_cfg) == 0
    remove(test_tmp_yaml)


@mark.parametrize('args, result', [
    ('/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files', '/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'),
    ('/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files/', '/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'),
    (Path('/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'), '/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'),
])
@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
def test_parent_dir_linux_dir(args, result):
    with patch('moht.utils.path.isdir', return_value=True):
        assert utils.parent_dir(args) == result


@mark.parametrize('args, result', [
    ('/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files/Morrowind.esm', '/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'),
    (Path('/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files/Morrowind.esm'), '/home/emcek/.wine/drive_c/GOG Games/Morrowind/Data Files'),
    ('/home/emcek/clean/Abandoned_Flatv2-37854-V2/Abandoned_Flat_2_readme.rtf', '/home/emcek/clean/Abandoned_Flatv2-37854-V2'),
    (Path('/home/emcek/clean/Abandoned_Flatv2-37854-V2/Abandoned_Flat_2_readme.rtf'), '/home/emcek/clean/Abandoned_Flatv2-37854-V2'),
    ('/home/emcek/OpenMWMods/Architecture/OAABDwemerPavements/00 Core/OAAB Dwemer Pavements.ESP', '/home/emcek/OpenMWMods/Architecture/OAABDwemerPavements/00 Core'),
    (Path('/home/emcek/OpenMWMods/Architecture/OAABDwemerPavements/00 Core/OAAB Dwemer Pavements.ESP'), '/home/emcek/OpenMWMods/Architecture/OAABDwemerPavements/00 Core'),
])
@mark.skipif(condition=platform != 'linux', reason='Run only on Linux')
def test_parent_dir_linux_file(args, result):
    with patch('moht.utils.path.isdir', return_value=False):
        with patch('moht.utils.path.isfile', return_value=True):
            assert utils.parent_dir(args) == result


@mark.parametrize('args, result', [
    (r'S:\Program Files\GOG Games\Morrowind\Data Files', r'S:\Program Files\GOG Games\Morrowind\Data Files'),
    ('S:\\Program Files\\GOG Games\\Morrowind\\Data Files\\', r'S:\Program Files\GOG Games\Morrowind\Data Files'),
    (Path(r'S:\Program Files\GOG Games\Morrowind\Data Files'), r'S:\Program Files\GOG Games\Morrowind\Data Files'),
])
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_parent_dir_windows_dir(args, result):
    with patch('moht.utils.path.isdir', return_value=True):
        assert utils.parent_dir(args) == result


@mark.parametrize('args, result', [
    (r'S:\Program Files\Morrowind\Data Files\Morrowind.esm', r'S:\Program Files\Morrowind\Data Files'),
    (Path(r'S:\Program Files\Morrowind\Data Files\Morrowind.esm'), r'S:\Program Files\Morrowind\Data Files'),
    ('S:\\OpenMWMods\\Architecture\\OAABDwemerPavements\\00 Core\\OAAB Dwemer Pavements.ESP', 'S:\\OpenMWMods\\Architecture\\OAABDwemerPavements\\00 Core'),
    (Path('S:\\OpenMWMods\\Architecture\\OAABDwemerPavements\\00 Core\\OAAB Dwemer Pavements.ESP'), 'S:\\OpenMWMods\\Architecture\\OAABDwemerPavements\\00 Core'),
])
@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_parent_dir_windows_file(args, result):
    with patch('moht.utils.path.isdir', return_value=False):
        with patch('moht.utils.path.isfile', return_value=True):
            assert utils.parent_dir(args) == result


@mark.skipif(condition=platform != 'win32', reason='Run only on Windows')
def test_set_path_hidden_windows():
    hidden_file = path.join(gettempdir(), '.hidden.file')
    with open(hidden_file, 'w+') as f:
        f.write(',')
    assert not bool(os.stat(hidden_file).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    assert utils.set_path_hidden(hidden_file)
    assert bool(os.stat(hidden_file).st_file_attributes & stat.FILE_ATTRIBUTE_HIDDEN)
    remove(hidden_file)
