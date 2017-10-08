# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Command for listing instance groups."""
from googlecloudsdk.api_lib.compute import base_classes
from googlecloudsdk.api_lib.compute import instance_groups_utils
from googlecloudsdk.api_lib.compute import lister
from googlecloudsdk.calliope import base


def _Args(parser):
  """Adds flags common to all release tracks."""
  parser.display_info.AddFormat("""\
        table(
          name,
          location():label=LOCATION,
          location_scope():label=SCOPE,
          network.basename(),
          isManaged:label=MANAGED,
          size:label=INSTANCES
        )""")
  lister.AddMultiScopeListerFlags(parser, zonal=True, regional=True)


@base.ReleaseTracks(base.ReleaseTrack.GA)
class List(base.ListCommand):
  """List Google Compute Engine instance groups."""

  @staticmethod
  def Args(parser):
    _Args(parser)
    # TODO(b/36050942): deprecate --only-managed and --only-unmanaged flags.
    managed_args_group = parser.add_mutually_exclusive_group()
    managed_args_group.add_argument(
        '--only-managed',
        action='store_true',
        help='If provided, a list of managed instance groups will be returned.')
    managed_args_group.add_argument(
        '--only-unmanaged',
        action='store_true',
        help=('If provided, a list of unmanaged instance groups '
              'will be returned.'))

  def ComputeDynamicProperties(self, args, items, holder):
    mode = instance_groups_utils.InstanceGroupFilteringMode.ALL_GROUPS
    if args.only_managed:
      mode = (instance_groups_utils.InstanceGroupFilteringMode
              .ONLY_MANAGED_GROUPS)
    elif args.only_unmanaged:
      mode = (instance_groups_utils.InstanceGroupFilteringMode
              .ONLY_UNMANAGED_GROUPS)
    return instance_groups_utils.ComputeInstanceGroupManagerMembership(
        compute_holder=holder,
        items=items,
        filter_mode=mode)

  def Run(self, args):
    holder = base_classes.ComputeApiHolder(self.ReleaseTrack())
    client = holder.client

    request_data = lister.ParseMultiScopeFlags(args, holder.resources)

    list_implementation = lister.MultiScopeLister(
        client,
        zonal_service=client.apitools_client.instanceGroups,
        regional_service=client.apitools_client.regionInstanceGroups,
        aggregation_service=client.apitools_client.instanceGroups)

    return self.ComputeDynamicProperties(
        args, lister.Invoke(request_data, list_implementation), holder)


@base.ReleaseTracks(base.ReleaseTrack.BETA, base.ReleaseTrack.ALPHA)
class ListBetaAlpha(List):
  """List Google Compute Engine managed instance groups."""

  @staticmethod
  def Args(parser):
    _Args(parser)

  def ComputeDynamicProperties(self, args, items, holder):
    return instance_groups_utils.ComputeInstanceGroupManagerMembership(
        compute_holder=holder,
        items=items,
        filter_mode=instance_groups_utils.InstanceGroupFilteringMode.ALL_GROUPS)


List.detailed_help = base_classes.GetMultiScopeListerHelp(
    'instance groups', (base_classes.ScopeType.regional_scope,
                        base_classes.ScopeType.zonal_scope))
ListBetaAlpha.detailed_help = List.detailed_help