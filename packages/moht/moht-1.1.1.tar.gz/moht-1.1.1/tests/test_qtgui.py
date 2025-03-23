from argparse import Namespace

from PySide6.QtCore import Qt

from moht.qtgui import MohtQtGui


def test_switch_tes3cmd_version(qtbot):
    mohtgui = MohtQtGui(Namespace(yamlfile=''))
    mohtgui.show()
    qtbot.addWidget(mohtgui)

    qtbot.mouseClick(mohtgui.rb_37, Qt.LeftButton)
    assert 'tes3cmd-0.37' in mohtgui.le_tes3cmd.text()
    qtbot.mouseClick(mohtgui.rb_40, Qt.LeftButton)
    assert 'tes3cmd-0.40-pre_rel2' in mohtgui.le_tes3cmd.text()
