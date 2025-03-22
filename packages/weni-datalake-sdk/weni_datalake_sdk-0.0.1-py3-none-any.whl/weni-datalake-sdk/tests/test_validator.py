import pytest
from weni.paths.msg_path import MsgPath
from weni.utils.exceptions import ValidationError
from weni.paths.validator import validate_path

class FakePath:
    @staticmethod
    def get_table_name():
        return "invalid_table"

def test_validate_path_success():
    try:
        validate_path(MsgPath)
    except ValidationError:
        pytest.fail("validate_path got a error!")

def test_validate_path_fail():
    with pytest.raises(ValidationError, match="Path 'invalid_table' is not valid."):
        validate_path(FakePath)
