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


def validate_address(address):
    """Take an address and split it into its local and server parts"""
    split_address = address.strip("@").split("@")
    if len(split_address) != 2:
        raise ValueError("This doens't look like a Mastodon address")
    return split_address


def normalise_address(local_or_address, server=None):
    """Take either an address or a local/server pair and return a string of the form @local@server"""
    if server is None:
        local, server = validate_address(local_or_address)
    else:
        local = local_or_address

    if "@" in local:
        raise ValueError("local contains @ but it should not")
    if "@" in server:
        raise ValueError("server contains @ but it should not")

    return "@{}@{}".format(local, server)
