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

import unittest

from ..utils import normalise_address, validate_address


class ValidateAddressTestCase(unittest.TestCase):
    def test_normal_address(self):
        user, server = validate_address("@moggers87@localhost")
        self.assertEqual(user, "moggers87")
        self.assertEqual(server, "localhost")

    def test_missing_first_at(self):
        user, server = validate_address("moggers87@localhost")
        self.assertEqual(user, "moggers87")
        self.assertEqual(server, "localhost")

    def test_no_ats(self):
        with self.assertRaises(ValueError):
            validate_address("no ats")

    def test_only_first_at(self):
        with self.assertRaises(ValueError):
            validate_address("@moggers87")

    def test_double_at(self):
        with self.assertRaises(ValueError):
            validate_address("@@moggers87")

        with self.assertRaises(ValueError):
            validate_address("moggers87@@localhost")


class NormaliseAddressTestCase(unittest.TestCase):
    def test_already_normalised(self):
        address = "@moggers87@localhost"
        result = normalise_address(address)
        self.assertEqual(address, result)

    def test_missing_first_at(self):
        expected = "@moggers87@localhost"
        address = "moggers87@localhost"
        result = normalise_address(address)
        self.assertEqual(expected, result)

    def test_bad_address(self):
        address = "moggers87"
        with self.assertRaises(ValueError):
            normalise_address(address)

    def test_separate(self):
        expected = "@moggers87@localhost"
        result = normalise_address("moggers87", "localhost")
        self.assertEqual(expected, result)
