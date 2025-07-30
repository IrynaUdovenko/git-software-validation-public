def pytest_configure(config):
    # Local Git config (used in repo-local .git/config)
    config.local_git_username = "Local User"
    config.local_git_email = "local@example.com"
    config.local_commit_message = "Test commit"
    config.local_filename = "test.txt"

    # Global Git config (used for comparison or override scenarios)
    config.global_git_username = "Global User"
    config.global_git_email = "global@example.com"
