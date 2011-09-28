#!/usr/bin/python
#
# Copyright (c) 2011 Red Hat, Inc.
#
#
# This software is licensed to you under the GNU General Public
# License as published by the Free Software Foundation; either version
# 2 of the License (GPLv2) or (at your option) any later version.
# There is NO WARRANTY for this software, express or implied,
# including the implied warranties of MERCHANTABILITY,
# NON-INFRINGEMENT, or FITNESS FOR A PARTICULAR PURPOSE. You should
# have received a copy of GPLv2 along with this software; if not, see
# http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt.

# Python
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)) + "/../common/")
import testutil

import pulp.server.content.loader as plugin_loader
import pulp.server.content.types.database as types_db
from pulp.server.content.types.model import TypeDefinition
import pulp.server.managers.plugin as plugin_manager

# -- mocks --------------------------------------------------------------------

class MockImporter:
    @classmethod
    def metadata(cls):
        return {'types': ['mock_type']}

class MockDistributor:
    @classmethod
    def metadata(cls):
        return {'types': ['mock_type']}

# -- test cases ---------------------------------------------------------------

class PluginManagerTests(testutil.PulpTest):

    def setUp(self):
        testutil.PulpTest.setUp(self)

        plugin_loader._create_loader()

        # Configure content manager
        plugin_loader._LOADER.add_importer('MockImporter', MockImporter, {})
        plugin_loader._LOADER.add_distributor('MockDistributor', MockDistributor, {})

        # Create the manager instance to test
        self.manager = plugin_manager.PluginManager()

    def tearDown(self):
        testutil.PulpTest.tearDown(self)

        # Reset content manager
        plugin_loader._LOADER.remove_importer('MockImporter')
        plugin_loader._LOADER.remove_distributor('MockDistributor')

    def test_types(self):
        """
        Tests retrieving all types in the database.
        """

        # Setup
        type_def_1 = TypeDefinition('type-1', 'Type 1', 'Type 1', [], [], [])
        type_def_2 = TypeDefinition('type-2', 'Type 2', 'Type 2', [], [], [])

        types_db._create_or_update_type(type_def_1)
        types_db._create_or_update_type(type_def_2)

        # Test
        found_defs = self.manager.types()

        # Verify
        self.assertEqual(2, len(found_defs))

        for type_def in [type_def_1, type_def_2]:
            found_def = [t for t in found_defs if t['id'] == type_def.id][0]

            self.assertEqual(found_def['id'], type_def.id)
            self.assertEqual(found_def['display_name'], type_def.display_name)
            self.assertEqual(found_def['description'], type_def.description)
            self.assertEqual(found_def['unique_indexes'], type_def.unique_indexes)
            self.assertEqual(found_def['search_indexes'], type_def.search_indexes)
            self.assertEqual(found_def['child_types'], type_def.child_types)

    def test_types_no_types(self):
        """
        Tests an empty list is returned when no types are loaded.
        """

        # Test
        found_defs = self.manager.types()

        # Verify
        self.assertTrue(isinstance(found_defs, list))
        self.assertEqual(0, len(found_defs))

    def test_importers(self):
        """
        Tests retieving all importers.
        """

        # Test
        found = self.manager.importers()

        # Verify
        self.assertEqual(1, len(found))
        self.assertEqual('MockImporter', found.keys()[0])

    def test_importers_no_importers(self):
        """
        Tests an empty list is returned when no importers are present.
        """

        # Setup
        plugin_loader._LOADER.remove_importer('MockImporter')

        # Test
        found = self.manager.importers()

        # Verify
        self.assertTrue(isinstance(found, dict))
        self.assertEqual(0, len(found))

    def test_distributors(self):
        """
        Tests retrieving all distributors.
        """

        # Test
        found = self.manager.distributors()

        # Verify
        self.assertEqual(1, len(found))
        self.assertEqual('MockDistributor', found.keys()[0])

    def test_distributors_no_distributors(self):
        """
        Tests an empty list is returned when no distributors are present.
        """

        # Setup
        plugin_loader._LOADER.remove_distributor('MockDistributor')

        # Test
        found = self.manager.distributors()

        # Verify
        self.assertTrue(isinstance(found, dict))
        self.assertEqual(0, len(found))
