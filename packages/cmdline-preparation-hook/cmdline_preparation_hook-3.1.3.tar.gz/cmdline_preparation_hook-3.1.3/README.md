# cmdline-preparation-hook

Pytest hook for custom argument handling and Allure reporting. This plugin allows you to add arguments before running a test.

The hook is written to update Pytest library to replace the old fixture:

@pytest.hookimpl(tryfirst=True)  
def pytest_cmdline_preparse(args):

For local installation, open a terminal in the root folder and run the following commands in sequence:

* cd pytest_hook
* pip install -e .