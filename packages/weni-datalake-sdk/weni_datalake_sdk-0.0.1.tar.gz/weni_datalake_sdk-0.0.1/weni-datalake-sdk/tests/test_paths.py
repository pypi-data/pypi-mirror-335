from weni.paths.msg_path import MsgPath

def test_paths():
    assert MsgPath.get_table_name() == "messages"
