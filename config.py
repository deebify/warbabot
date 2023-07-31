#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "38394282-54cf-440d-803b-0e9a1478632e")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "z.U8Q~eeXLYBBqzcZEqqdRyQdUILLLRYeq_RPcbh")
