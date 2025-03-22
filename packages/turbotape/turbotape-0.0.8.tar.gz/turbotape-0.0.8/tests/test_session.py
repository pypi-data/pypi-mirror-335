import json
import os
from unittest.mock import patch

from turbotape.session import (
    try_environment_token,
    create_tape_session,
)


TEST_USER_KEY = 'user_key_eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiLvv73vv73vv73vv73vv73vv71IXHUwMDAxK28iLCJzY29wZSI6InVrX3YxIiwidHlwZSI6IlVTRVJfQVBJX0tFWSJ9.KtVPcZXwRnlCsI-Nih4M9-PxL8kwpufyif8ltryGzJM'
class TestSession:

    def test_try_environment_token(self):
        # Set environment variable
        vars = {
            "TAPE_API_KEY": TEST_USER_KEY,
        }
        with patch.dict('os.environ', vars):
            assert TEST_USER_KEY == try_environment_token()["access_token"]
            assert "bearer" == try_environment_token()["token_type"]

    def test_try_environment_token_not_set(self):
        assert None == try_environment_token()