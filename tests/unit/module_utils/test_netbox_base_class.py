# -*- coding: utf-8 -*-
# Copyright: (c) 2019, Bruno Inec (@sweenu) <bruno@inec.fr>
# Copyright: (c) 2019, Mikhail Yohman (@FragmentedPacket) <mikhail.yohman@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# import unittest
# from units.compat import unittest
# from units.compat.mock import patch, MagicMock, Mock

import pytest
from unittest.mock import patch, MagicMock, Mock
from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.fragmentedpacket.netbox_modules.plugins.module_utils.netbox_utils import (
        NetboxModule,
    )
    from ansible_collections.fragmentedpacket.netbox_modules.plugins.module_utils.netbox_dcim import (
        NB_DEVICES,
    )

    MOCKER_PATCH_PATH = "ansible_collections.fragmentedpacket.netbox_modules.plugins.module_utils.netbox_utils.NetboxModule"
except ImportError:
    import sys

    sys.path.append("plugins/module_utils")
    from netbox_utils import NetboxModule
    from netbox_dcim import NB_DEVICES

    MOCKER_PATCH_PATH = "netbox_utils.NetboxModule"


@pytest.fixture
def fixture_arg_spec():
    return {
        "netbox_url": "http://netbox.local/",
        "netbox_token": "0123456789",
        "data": {
            "name": "Test Device1",
            "device_role": "Core Switch",
            "device_type": "Cisco Switch",
            "manufacturer": "Cisco",
            "site": "Test Site",
            "asset_tag": "1001",
        },
        "state": "present",
        "validate_certs": False,
    }


@pytest.fixture
def normalized_data():
    return {
        "name": "Test Device1",
        "device_role": "core-switch",
        "device_type": "cisco-switch",
        "manufacturer": "cisco",
        "site": "test-site",
        "asset_tag": "1001",
    }


@pytest.fixture
def mock_ansible_module(fixture_arg_spec):
    module = MagicMock(name="AnsibleModule")
    module.check_mode = False
    module.params = fixture_arg_spec

    return module


@pytest.fixture
def find_ids_return():
    return {
        "name": "Test Device1",
        "device_role": 1,
        "device_type": 1,
        "manufacturer": 1,
        "site": 1,
        "asset_tag": "1001",
    }


@pytest.fixture
def nb_obj_mock(mocker, normalized_data):
    nb_obj = mocker.Mock(name="nb_obj_mock")
    nb_obj.delete.return_value = True
    nb_obj.update.return_value = True
    nb_obj.update.side_effect = normalized_data.update
    nb_obj.serialize.return_value = normalized_data

    return nb_obj


@pytest.fixture
def endpoint_mock(mocker, nb_obj_mock):
    endpoint = mocker.Mock(name="endpoint_mock")
    endpoint.create.return_value = nb_obj_mock

    return endpoint


@pytest.fixture
def on_creation_diff(mock_netbox_module):
    return mock_netbox_module._build_diff(
        before={"state": "absent"}, after={"state": "present"}
    )


@pytest.fixture
def on_deletion_diff(mock_netbox_module):
    return mock_netbox_module._build_diff(
        before={"state": "present"}, after={"state": "absent"}
    )


@pytest.fixture
def mock_netbox_module(mocker, mock_ansible_module, find_ids_return):
    find_ids = mocker.patch("%s%s" % (MOCKER_PATCH_PATH, "._find_ids"))
    find_ids.return_value = find_ids_return
    netbox = NetboxModule(mock_ansible_module, NB_DEVICES, nb_client=True)

    return netbox


@pytest.fixture
def changed_serialized_obj(nb_obj_mock):
    changed_serialized_obj = nb_obj_mock.serialize().copy()
    changed_serialized_obj["name"] += " (modified)"

    return changed_serialized_obj


@pytest.fixture
def on_update_diff(mock_netbox_module, nb_obj_mock, changed_serialized_obj):
    return mock_netbox_module._build_diff(
        before={"name": "Test Device1"}, after={"name": "Test Device1 (modified)"}
    )


def test_init(mock_netbox_module, find_ids_return):
    """Test that we can get a real mock NetboxModule."""
    assert mock_netbox_module.data == find_ids_return


def test_normalize_data_returns_correct_data(mock_netbox_module):
    data = {
        "cluster": "Test Cluster",
        "device": "Test Device",
        "device_role": "Core Switch",
        "device_type": "Cisco Switch",
        "group": "Test Group1",
        "manufacturer": "Cisco",
        "nat_inside": "192.168.1.1/24",
        "nat_outside": "192.168.10.1/24",
        "platform": "Cisco IOS",
        "primary_ip": "192.168.1.1/24",
        "primary_ip4": "192.168.1.1/24",
        "primary_ip6": "2001::1/128",
        "rack": "Test Rack",
        "rack_group": "RacK_group",
        "rack_role": "Test Rack Role",
        "region": "Test Region_1",
        "rir": "Test RIR_One",
        "prefix_role": "TEst Role-1",
        "slug": "Test to_slug",
        "site": "Test Site",
        "tenant": "Test Tenant",
        "tenant_group": "Test Tenant Group",
        "time_zone": "America/Los Angeles",
        "vlan": "Test VLAN",
        "vlan_group": "Test VLAN Group",
        "vlan_role": "Access Role",
        "vrf": "Test VRF",
    }
    norm_data_expected = {
        "cluster": "Test Cluster",
        "device": "Test Device",
        "device_role": "core-switch",
        "device_type": "cisco-switch",
        "group": "test-group1",
        "manufacturer": "cisco",
        "nat_inside": "192.168.1.1/24",
        "nat_outside": "192.168.10.1/24",
        "platform": "cisco-ios",
        "primary_ip": "192.168.1.1/24",
        "primary_ip4": "192.168.1.1/24",
        "primary_ip6": "2001::1/128",
        "rack": "Test Rack",
        "rack_group": "rack_group",
        "rack_role": "test-rack-role",
        "region": "test-region_1",
        "rir": "test-rir_one",
        "prefix_role": "test-role-1",
        "slug": "test-to_slug",
        "site": "test-site",
        "tenant": "Test Tenant",
        "tenant_group": "test-tenant-group",
        "time_zone": "America/Los_Angeles",
        "vlan": "Test VLAN",
        "vlan_group": "test-vlan-group",
        "vlan_role": "Access Role",
        "vrf": "Test VRF",
    }
    norm_data = mock_netbox_module._normalize_data(data)

    assert norm_data == norm_data_expected


def test_to_slug_returns_valid_slug(mock_netbox_module):
    not_slug = "Test device-1_2"
    expected_slug = "test-device-1_2"
    convert_to_slug = mock_netbox_module._to_slug(not_slug)

    assert expected_slug == convert_to_slug


@pytest.mark.parametrize(
    "endpoint, app",
    [
        ("devices", "dcim"),
        ("device_roles", "dcim"),
        ("device_types", "dcim"),
        ("interfaces", "dcim"),
        ("manufacturers", "dcim"),
        ("platforms", "dcim"),
        ("racks", "dcim"),
        ("rack_groups", "dcim"),
        ("rack_roles", "dcim"),
        ("regions", "dcim"),
        ("sites", "dcim"),
        ("aggregates", "ipam"),
        ("ip_addresses", "ipam"),
        ("prefixes", "ipam"),
        ("roles", "ipam"),
        ("rirs", "ipam"),
        ("services", "ipam"),
        ("vlans", "ipam"),
        ("vlan_groups", "ipam"),
        ("vrfs", "ipam"),
        ("tenants", "tenancy"),
        ("tenant_groups", "tenancy"),
        ("clusters", "virtualization"),
    ],
)
def test_find_app_returns_valid_app(mock_netbox_module, endpoint, app):
    assert app == mock_netbox_module._find_app(endpoint), "app: %s, endpoint: %s" % (
        app,
        endpoint,
    )


def test_build_diff_returns_valid_diff(mock_netbox_module):
    before = "The state before"
    after = {"A": "more", "complicated": "state"}
    diff = mock_netbox_module._build_diff(before=before, after=after)

    assert diff == {"before": before, "after": after}


def test_create_netbox_object_check_mode_false(
    mock_netbox_module, endpoint_mock, normalized_data, on_creation_diff
):
    return_value = endpoint_mock.create().serialize()
    serialized_obj, diff = mock_netbox_module._create_netbox_object(
        endpoint_mock, normalized_data
    )
    assert endpoint_mock.create.called_once_with(normalized_data)
    assert serialized_obj.serialize() == return_value
    assert diff == on_creation_diff


def test_create_netbox_object_check_mode_true(
    mock_netbox_module, endpoint_mock, normalized_data, on_creation_diff
):
    mock_netbox_module.check_mode = True
    serialized_obj, diff = mock_netbox_module._create_netbox_object(
        endpoint_mock, normalized_data
    )
    assert endpoint_mock.create.not_called()
    assert serialized_obj == normalized_data
    assert diff == on_creation_diff


def test_delete_netbox_object_check_mode_false(
    mock_netbox_module, nb_obj_mock, on_deletion_diff
):
    mock_netbox_module.nb_object = nb_obj_mock
    diff = mock_netbox_module._delete_netbox_object()
    assert nb_obj_mock.delete.called_once()
    assert diff == on_deletion_diff


def test_delete_netbox_object_check_mode_true(
    mock_netbox_module, nb_obj_mock, on_deletion_diff
):
    mock_netbox_module.check_mode = True
    mock_netbox_module.nb_object = nb_obj_mock
    diff = mock_netbox_module._delete_netbox_object()
    assert nb_obj_mock.delete.not_called()
    assert diff == on_deletion_diff


def test_update_netbox_object_no_changes(mock_netbox_module, nb_obj_mock):
    mock_netbox_module.nb_object = nb_obj_mock
    unchanged_data = nb_obj_mock.serialize()
    serialized_object, diff = mock_netbox_module._update_netbox_object(unchanged_data)
    assert nb_obj_mock.update.not_called()
    assert serialized_object == unchanged_data
    assert diff is None


def test_update_netbox_object_with_changes_check_mode_false(
    mock_netbox_module, nb_obj_mock, changed_serialized_obj, on_update_diff
):
    mock_netbox_module.nb_object = nb_obj_mock
    serialized_obj, diff = mock_netbox_module._update_netbox_object(
        changed_serialized_obj
    )
    assert nb_obj_mock.update.called_once_with(changed_serialized_obj)
    assert serialized_obj == nb_obj_mock.serialize()
    assert diff == on_update_diff


def test_update_netbox_object_with_changes_check_mode_true(
    mock_netbox_module, nb_obj_mock, changed_serialized_obj, on_update_diff
):
    mock_netbox_module.nb_object = nb_obj_mock
    mock_netbox_module.check_mode = True
    updated_serialized_obj = nb_obj_mock.serialize().copy()
    updated_serialized_obj.update(changed_serialized_obj)

    serialized_obj, diff = mock_netbox_module._update_netbox_object(
        changed_serialized_obj
    )
    assert nb_obj_mock.update.not_called()
    assert serialized_obj == updated_serialized_obj
    assert diff == on_update_diff


@pytest.mark.parametrize(
    "endpoint, data, expected",
    [
        (
            "devices",
            {
                "status": "Active",
                "status": "Offline",
                "status": "Planned",
                "status": "Staged",
                "status": "Failed",
                "status": "Inventory",
                "face": "Front",
                "face": "Rear",
            },
            {
                "status": 1,
                "status": 0,
                "status": 2,
                "status": 3,
                "status": 4,
                "status": 5,
                "face": 0,
                "face": 1,
            },
        ),
        (
            "device_types",
            {"subdevice_role": "Parent", "subdevice_role": "Child"},
            {"subdevice_role": True, "subdevice_role": False},
        ),
        (
            "interfaces",
            {
                "form_factor": "1000base-t (1ge)",
                "mode": "Access",
                "mode": "Tagged",
                "mode": "Tagged all",
            },
            {"form_factor": 1000, "mode": 100, "mode": 200, "mode": 300},
        ),
        (
            "ip_addresses",
            {
                "status": "Active",
                "status": "Reserved",
                "status": "Deprecated",
                "status": "DHCP",
                "role": "Loopback",
                "role": "Secondary",
                "role": "Anycast",
                "role": "VIP",
                "role": "VRRP",
                "role": "HSRP",
                "role": "GLBP",
                "role": "CARP",
            },
            {
                "status": 1,
                "status": 2,
                "status": 3,
                "status": 5,
                "role": 10,
                "role": 20,
                "role": 30,
                "role": 40,
                "role": 41,
                "role": 42,
                "role": 43,
                "role": 44,
            },
        ),
        (
            "prefixes",
            {
                "status": "Active",
                "status": "Container",
                "status": "Reserved",
                "status": "Deprecated",
            },
            {"status": 1, "status": 0, "status": 2, "status": 3},
        ),
        (
            "racks",
            {
                "status": "Active",
                "status": "Planned",
                "status": "Reserved",
                "status": "Available",
                "status": "Deprecated",
                "outer_unit": "Inches",
                "outer_unit": "Millimeters",
                "type": "2-post Frame",
                "type": "4-post Frame",
                "type": "4-post Cabinet",
                "type": "Wall-mounted Frame",
                "type": "Wall-mounted Cabinet",
            },
            {
                "status": 3,
                "status": 2,
                "status": 0,
                "status": 1,
                "status": 4,
                "outer_unit": 2000,
                "outer_unit": 1000,
                "type": 100,
                "type": 200,
                "type": 300,
                "type": 1000,
                "type": 1100,
            },
        ),
        (
            "sites",
            {"status": "Active", "status": "Planned", "status": "Retired"},
            {"status": 1, "status": 2, "status": 4},
        ),
        (
            "vlans",
            {"status": "Active", "status": "Reserved", "status": "Deprecated"},
            {"status": 1, "status": 2, "status": 3},
        ),
    ],
)
def test_change_choices_id(mock_netbox_module, endpoint, data, expected):
    new_data = mock_netbox_module._change_choices_id(endpoint, data)
    assert new_data == expected


@pytest.mark.parametrize(
    "parent, module_data, expected",
    [
        (
            "aggregate",
            {
                "prefix": "192.168.0.0/16",
                "rir": "Example RIR",
                "date_added": "2019-01-18",
            },
            {"prefix": "192.168.0.0/16", "rir_id": 1},
        ),
        (
            "device",
            {"name": "Test Device", "status": "Active"},
            {"name": "Test Device"},
        ),
        (
            "device_bay",
            {"name": "Device Bay #1", "device": "test100"},
            {"name": "Device Bay #1", "device_id": 1},
        ),
        (
            "device_role",
            {
                "name": "Test Device Role",
                "slug": "test-device-role",
                "status": "Active",
            },
            {"slug": "test-device-role"},
        ),
        (
            "device_type",
            {
                "name": "Test Device Type",
                "slug": "test-device-type",
                "status": "Active",
            },
            {"slug": "test-device-type"},
        ),
        (
            "installed_device",
            {"name": "Test Device", "status": "Active"},
            {"name": "Test Device"},
        ),
        (
            "interface",
            {"name": "GigabitEthernet1", "device": "Test Device", "form_factor": 1000},
            {"name": "GigabitEthernet1", "device_id": 1},
        ),
        (
            "inventory_item",
            {
                "name": "10G-SFP+",
                "device": "test100",
                "serial": "1234",
                "asset_tag": "1234",
            },
            {"name": "10G-SFP+", "device_id": 1},
        ),
        (
            "ip_address",
            {
                "address": "192.168.1.1/24",
                "vrf": "Test VRF",
                "description": "Test description",
            },
            {"address": "192.168.1.1/24", "vrf_id": 1},
        ),
        (
            "prefix",
            {"prefix": "10.10.10.0/24", "vrf": "Test VRF", "status": "Reserved"},
            {"prefix": "10.10.10.0/24", "vrf_id": 1},
        ),
        ("prefix", {"parent": "10.10.0.0/16"}, {"prefix": "10.10.0.0/16"}),
        (
            "rack",
            {"name": "Test Rack", "slug": "test-rack", "site": "Test Site"},
            {"name": "Test Rack", "site_id": 1},
        ),
        (
            "rack_group",
            {"name": "Test Rack Group", "slug": "test-rack-group"},
            {"slug": "test-rack-group"},
        ),
        (
            "rack_role",
            {"name": "Test Rack Role", "slug": "test-rack-role"},
            {"slug": "test-rack-role"},
        ),
        (
            "region",
            {"name": "Test Region", "slug": "test-region"},
            {"slug": "test-region"},
        ),
        (
            "parent_region",
            {"name": "Parent Region", "slug": "parent-region"},
            {"slug": "parent-region"},
        ),
        (
            "rir",
            {"name": "Test RIR One", "slug": "test-rir-one"},
            {"slug": "test-rir-one"},
        ),
        (
            "site",
            {
                "name": "Test Site",
                "slug": "test-site",
                "asn": 65000,
                "contact_name": "John Smith",
            },
            {"slug": "test-site"},
        ),
        (
            "tenant",
            {"name": "Test Tenant", "description": "Test Description"},
            {"name": "Test Tenant"},
        ),
        (
            "tenant_group",
            {"name": "Test Tenant Group", "description": "Test Description"},
            {"name": "Test Tenant Group"},
        ),
    ],
)
def test_build_query_params_no_child(
    mock_netbox_module, mocker, parent, module_data, expected
):
    get_query_param_id = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._get_query_param_id")
    )
    get_query_param_id.return_value = 1
    query_params = mock_netbox_module._build_query_params(parent, module_data)
    assert query_params == expected


@pytest.mark.parametrize(
    "parent, module_data, child, expected",
    [
        (
            "primary_ip4",
            {
                "name": "test100",
                "serial": "FXS1001",
                "comments": "Temp device",
                "primary_ip4": {"address": "172.16.180.1/24", "vrf": "Test VRF"},
            },
            {"address": "172.16.180.1/24", "vrf": "Test VRF"},
            {"address": "172.16.180.1/24", "vrf_id": 1},
        ),
        (
            "primary_ip6",
            {
                "name": "test100",
                "serial": "FXS1001",
                "comments": "Temp device",
                "primary_ip4": {"address": "2001::1:1/64", "vrf": "Test VRF"},
            },
            {"address": "2001::1:1/64", "vrf": "Test VRF"},
            {"address": "2001::1:1/64", "vrf_id": 1},
        ),
        (
            "lag",
            {"name": "GigabitEthernet1", "device": 1, "lag": {"name": "port-channel1"}},
            {"name": "port-channel1"},
            {"device_id": 1, "form_factor": 200, "name": "port-channel1"},
        ),
        (
            "lag",
            {
                "name": "GigabitEthernet1",
                "device": "Test Device",
                "lag": {"name": "port-channel1"},
            },
            {"name": "port-channel1"},
            {"device": "Test Device", "form_factor": 200, "name": "port-channel1"},
        ),
        (
            "nat_inside",
            {
                "address": "10.10.10.1/24",
                "nat_inside": {"address": "192.168.1.1/24", "vrf": "Test VRF"},
            },
            {"address": "192.168.1.1/24", "vrf": "Test VRF"},
            {"address": "192.168.1.1/24", "vrf_id": 1},
        ),
        (
            "vlan",
            {
                "prefix": "10.10.10.0/24",
                "description": "Test Prefix",
                "vlan": {
                    "name": "Test VLAN",
                    "site": "Test Site",
                    "tenant": "Test Tenant",
                    "vlan_group": "Test VLAN group",
                },
            },
            {
                "name": "Test VLAN",
                "site": "Test Site",
                "tenant": "Test Tenant",
                "vlan_group": "Test VLAN group",
            },
            {"name": "Test VLAN", "site_id": 1, "tenant_id": 1},
        ),
        (
            "vlan_group",
            {
                "prefix": "10.10.10.0/24",
                "description": "Test Prefix",
                "vlan_group": {
                    "name": "Test VLAN Group",
                    "slug": "test-vlan-group",
                    "site": "Test Site",
                },
            },
            {"name": "Test VLAN Group", "slug": "test-vlan-group", "site": "Test Site"},
            {"slug": "test-vlan-group", "site_id": 1},
        ),
        (
            "untagged_vlan",
            {
                "prefix": "10.10.10.0/24",
                "description": "Test Prefix",
                "untagged_vlan": {"name": "Test VLAN", "site": "Test Site"},
            },
            {"name": "Test VLAN", "site": "Test Site"},
            {"name": "Test VLAN", "site_id": 1},
        ),
        (
            "vrf",
            {
                "prefix": "10.10.10.0/24",
                "description": "Test Prefix",
                "vrf": {"name": "Test VRF", "tenant": "Test Tenant"},
            },
            {"name": "Test VRF", "tenant": "Test Tenant"},
            {"name": "Test VRF", "tenant_id": 1},
        ),
    ],
)
def test_build_query_params_child(
    mock_netbox_module, mocker, parent, module_data, child, expected
):
    get_query_param_id = mocker.patch(
        "%s%s" % (MOCKER_PATCH_PATH, "._get_query_param_id")
    )
    get_query_param_id.return_value = 1
    query_params = mock_netbox_module._build_query_params(parent, module_data, child)
    assert query_params == expected
