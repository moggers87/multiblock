##
#
# Copyright (C) 2020 Matt Molyneaux
#
# This file is part of Multiblock.
#
# Multiblock is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Multiblock is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Multiblock.  If not, see <https://www.gnu.org/licenses/>.
#
##

import functools
import json
import pathlib
import tempfile

from mastodon import Mastodon

from . import __version__
from .utils import validate_address

DEFAULT_PATH = pathlib.Path("~/.config/multiblock/config.json").expanduser()
WEBSITE = "https://pypi.org/project/multiblock/"
SCOPES = [
    "read:blocks",      # read blocks and hidden domains
    "write:blocks",     # write blocks and hidden domains
    "read:mutes",       # read mutes
    "write:mutes",      # write mutes
    "read:accounts",    # verify the user has logged into the correct account
]


class Config:
    def __init__(self, path):
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
        self._path = path

    def __enter__(self):
        try:
            self._config_obj = json.load(open(self._path))
        except json.decoder.JSONDecodeError:
            self._config_obj = {}
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is None:
            self.save()

    def accounts(self):
        return self._config_obj

    def get_address(self, address):
        address = normalise_address(address)
        self._config_obj.setdefault(address, {})
        return address

    def add_account(self, address, access_token):
        address = self.get_address(address)
        self._config_obj[address]["access_token"] = access_token

    def remove_account(self, address):
        address = self.get_address(address)
        app = self.get_app(address)
        app.__api_request("POST", "/oauth/revoke", params={
            "client_id": app.client_id,
            "client_secret": app.client_secret,
            "token": app.access_token,
        })

        del self._config_obj[address]

    def clear_token(self, address):
        address = self.get_address(address)
        del self._config_obj[address]["access_token"]
        del self._config_obj[address]["client"]

    @functools.lru_cache(maxsize=None)
    def get_app(self, address):
        user, server = validate_address(address)
        address = self.get_address(user, server)
        self._config_obj[address].setdefault("server", {})
        server_cfg = self._config_obj[address]["server"]
        if "client" not in server_cfg:
            cid, secret = Mastodon.create_app(
                "Multiblock %s" % __version__,
                api_base_url=server,
                scopes=SCOPES,
                website=WEBSITE,
            )

            server_cfg["client"] = {"id": cid, "secret": secret, "scopes": SCOPES}

        app = Mastodon(
            client_id=server_cfg["client"]["id"],
            client_secret=server_cfg["client"]["secret"],
            api_base_url=server,
            access_token=self._config_obj[address].get("access_token"),
        )

        return app

    def get_auth_url(self, address):
        address = self.get_address(address)
        app = self.get_app(address)
        return app.auth_request_url(scopes=SCOPES, force_login=True)

    def log_in(self, address, code):
        user, server = validate_address(address)
        address = self.get_address(user, server)
        app = self.get_app(address)
        token = app.log_in(code=code, scopes=SCOPES)
        user_obj = app.account_verify_credentials()
        # verify user is the same as address
        if user != user_obj["acct"]:
            raise ValueError("Logged in with wrong account")
        return token

    def save(self):
        parent_dir = self._path.parent
        # maybe one day we can detect failed config files and tell the user about that?
        with tempfile.NamedTemporaryFile(dir=parent_dir, prefix="multiblock-config", delete=False, mode="w") as fp:
            json.dump(self._config_obj, fp)
            tmp_file = pathlib.Path(fp.name)
        self._path.unlink()
        self._path = tmp_file.rename(self._path)
