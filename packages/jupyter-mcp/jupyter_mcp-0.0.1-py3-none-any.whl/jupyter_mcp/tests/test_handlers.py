# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import json

from jupyter_mcp.__version__ import __version__


async def test_config(jp_fetch):
    # When
    response = await jp_fetch("jupyter_mcp", "config")
    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "extension": "jupyter_mcp",
        "version": __version__
    }
