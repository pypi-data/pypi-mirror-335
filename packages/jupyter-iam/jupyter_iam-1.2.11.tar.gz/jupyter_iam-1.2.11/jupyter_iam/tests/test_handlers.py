# Copyright (c) 2023-2024 Datalayer, Inc.
#
# Datalayer License

import json

from jupyter_iam.__version__ import __version__


async def test_config(jp_fetch):
    # When
    response = await jp_fetch("jupyter_iam", "config")
    # Then
    assert response.code == 200
    payload = json.loads(response.body)
    assert payload == {
        "extension": "jupyter_iam",
        "version": __version__
    }
