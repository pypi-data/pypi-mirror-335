from _pytest.python_api import raises

from cloud_sql.commandline import get_parameters


class TestCommandLine:
    def test_get_parameters(self):
        assert get_parameters([]) == {"command": None}

        with raises(SystemExit):
            get_parameters(["--help"])
