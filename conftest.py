'''pytest configuration module'''
import pytest # pylint: disable=import-error

# configure setup to skip slow tests by default (without --slow flag)
def pytest_runtest_setup(item):
    """Skip tests if they are marked as slow and --slow is not given"""
    if getattr(item.obj, 'slow', None) and not item.config.getvalue('slow'):
        pytest.skip('slow tests not requested')

# add '--slow' flag to enable the slow tests, but default to False/disabled
def pytest_addoption(parser):
    '''Add --slow option'''
    parser.addoption('--slow', action='store_true', default=False,
                     help='Also run slow tests')

