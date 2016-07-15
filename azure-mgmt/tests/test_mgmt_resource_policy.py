﻿# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import unittest

import azure.mgmt.resource
from testutils.common_recordingtestcase import record
from tests.mgmt_testcase import HttpStatusCode, AzureMgmtTestCase


class MgmtResourcePolicyTest(AzureMgmtTestCase):

    def setUp(self):
        super(MgmtResourcePolicyTest, self).setUp()
        self.policy_client = self.create_mgmt_client(
            azure.mgmt.resource.PolicyClient
        )

    @record
    def test_policy_definition(self):
        self.create_resource_group()
        policy_name = self.get_resource_name('pypolicy')
        policy_assignment_name = self.get_resource_name('pypolicyassignment')

        definition = self.policy_client.policy_definitions.create_or_update(
            policy_name,
            {
                'policy_type':'Custom',
                'description':'Don\'t create a VM anywhere',
                'policy_rule':{  
                    'if':{  
                      'allOf':[  
                        {  
                          'source':'action',
                          'equals':'Microsoft.Compute/virtualMachines/write'
                        },
                        {  
                          'field':'location',
                          'in':[  
                            'eastus',
                            'eastus2',
                            'centralus'
                          ]
                        }
                      ]
                    },
                    'then':{  
                      'effect':'deny'
                    }
                }
            }
        )

        definition = self.policy_client.policy_definitions.get(
            definition.name
        )

        policies = list(self.policy_client.policy_definitions.list())
        self.assertGreater(len(policies), 0)

        # Policy Assignement - By Name
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            self.group_name
        )
        assignment = self.policy_client.policy_assignments.create(
            scope,
            policy_assignment_name,
            {
                'policy_definition_id': definition.id,
            }
        )

        assignment = self.policy_client.policy_assignments.get(
            assignment.scope,
            assignment.name
        )

        assignments = list(self.policy_client.policy_assignments.list())
        self.assertGreater(len(assignments), 0)

        assignments = list(self.policy_client.policy_assignments.list_for_resource_group(
            self.group_name
        ))
        self.assertEqual(len(assignments), 1)

        self.policy_client.policy_assignments.delete(
            scope,
            policy_assignment_name
        )

        # Policy Assignement - By Id
        scope = '/subscriptions/{}/resourceGroups/{}'.format(
            self.settings.SUBSCRIPTION_ID,
            self.group_name
        )
        policy_id = '{}/providers/Microsoft.Authorization/policyAssignments/{}'.format(
            scope,
            policy_assignment_name
        )
        assignment = self.policy_client.policy_assignments.create_by_id(
            policy_id,
            {
                'policy_definition_id': definition.id,
            }
        )            

        assignment = self.policy_client.policy_assignments.get_by_id(
            assignment.id,
        )

        self.policy_client.policy_assignments.delete_by_id(
            assignment.id
        )

        # Delete definitions
        self.policy_client.policy_definitions.delete(
            definition.name
        )


#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
