# Copyright (c) 2021-2024 Datalayer, Inc.
#
# Datalayer License

import pytest

pytest_plugins = ("jupyter_server.pytest_plugin", )


@pytest.fixture
def jp_server_config(jp_server_config):
    return {"ServerApp": {"jpserver_extensions": {"datalayer_ui": True}}}
