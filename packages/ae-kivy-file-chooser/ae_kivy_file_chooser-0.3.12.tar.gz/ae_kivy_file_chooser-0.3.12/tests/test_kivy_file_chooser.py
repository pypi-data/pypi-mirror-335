""" unit tests """
from conftest import skip_gitlab_ci
from unittest.mock import patch, MagicMock

from ae.kivy_file_chooser import FileChooserPopup


def test_declaration():
    assert FileChooserPopup


class TestFileChooserPopup:
    def test_on_file_chooser_entry_added(self):
        class _FwTstAppClass:
            font_color = 'font_color'
            app_states = {'font_size': 66.99, 'selected_ink': 'selected_ink'}

        _frameworkTstApp = _FwTstAppClass()

        class _TstChildClass:
            color = "_tst_ini_color"
            font_size = -96
            height = 33

        class _TstFileListEntryChildClass(_TstChildClass):
            children = [_TstChildClass(), _TstChildClass()]

        class _TstFileListEntryClass:
            color_selected = "_tst_ini_ink"
            children = [_TstFileListEntryChildClass(), _TstChildClass()]
            height = -1.0

        class _TstFileIconEntryClass:
            color_selected = "_tst_ini_ink"
            children = [_TstChildClass(), _TstChildClass()]

        with patch('kivy.app.App.get_running_app', return_value = _frameworkTstApp):
            view_entries = [_TstFileListEntryClass(), _TstFileIconEntryClass()]
            FileChooserPopup.on_file_chooser_entry_added(view_entries)

        assert view_entries[0].color_selected == _FwTstAppClass.app_states['selected_ink']
        assert view_entries[0].color_selected == _frameworkTstApp.app_states['selected_ink']

        assert view_entries[0].children[0].children[1].color == _frameworkTstApp.font_color
        assert view_entries[0].children[0].children[1].font_size < 0

        assert view_entries[0].children[0].children[0].color == _frameworkTstApp.font_color
        assert view_entries[0].children[0].children[0].font_size < 0

        assert view_entries[1].children[1].color == _frameworkTstApp.font_color
        assert 0 < view_entries[1].children[1].font_size < 33

        assert view_entries[1].children[0].color == _frameworkTstApp.font_color
        assert 0 < view_entries[1].children[0].font_size < 33

    def test_register_file_path(self):
        class _TstMainAppClass:
            file_chooser_paths = []
            app_states = {}
            def change_app_state(self, var, val):
                self.app_states[var] = val

        _mainTstApp = _TstMainAppClass()

        tst_file_path = 'tstFilePath'
        FileChooserPopup.register_file_path(f"{tst_file_path}/tstFileName", _mainTstApp)

        assert _mainTstApp.app_states['file_chooser_initial_path'].endswith(tst_file_path)

        assert len(_mainTstApp.file_chooser_paths) == 1
        assert _mainTstApp.file_chooser_paths[0].endswith(tst_file_path)
        assert _mainTstApp.app_states['file_chooser_paths'] == _mainTstApp.file_chooser_paths
