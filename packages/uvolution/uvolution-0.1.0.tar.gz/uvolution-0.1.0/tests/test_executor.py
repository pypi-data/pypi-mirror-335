from uvolution.utils.executor import CommandExecutor


def test_execution():
    assert CommandExecutor.execute('echo', return_statuscode=True) == 0
    assert CommandExecutor.execute('invalid', return_statuscode=True) != 0
