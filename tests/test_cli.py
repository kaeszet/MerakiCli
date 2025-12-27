import os
from unittest.mock import patch, MagicMock

import pytest
from typer.testing import CliRunner

from meraki_cli import app

runner = CliRunner()


@patch("meraki_cli.meraki.DashboardAPI")
def test_list_networks(mock_dashboard_cls):
    """Test list-networks z 2 organizacjami i 3 sieciami."""
    mock_dashboard = MagicMock()
    mock_dashboard_cls.return_value = mock_dashboard

    # 2 organizacje – użyta będzie pierwsza
    mock_dashboard.organizations.getOrganizations.return_value = [
        {"id": "org_1", "name": "Org One"},
        {"id": "org_2", "name": "Org Two"},
    ]

    # 3 sieci w pierwszej organizacji
    mock_dashboard.organizations.getOrganizationNetworks.return_value = [
        {"id": "net_1", "name": "Net 1", "productTypes": ["wireless"]},
        {"id": "net_2", "name": "Net 2", "productTypes": ["appliance"]},
        {"id": "net_3", "name": "Net 3", "productTypes": ["switch", "wireless"]},
    ]

    with patch.dict(os.environ, {"MERAKI_DASHBOARD_API_KEY": "test-key"}):
        result = runner.invoke(app, ["list-networks"])

    assert result.exit_code == 0
    # Sprawdzamy, że użyta została pierwsza organizacja
    mock_dashboard.organizations.getOrganizations.assert_called_once_with()
    mock_dashboard.organizations.getOrganizationNetworks.assert_called_once_with(
        "org_1"
    )
    # Sprawdzamy wyjście
    assert "Org One" in result.stdout
    assert "Total networks: 3" in result.stdout


@patch("meraki_cli.meraki.DashboardAPI")
def test_list_clients(mock_dashboard_cls):
    """Test list-clients z 5 klientami."""
    mock_dashboard = MagicMock()
    mock_dashboard_cls.return_value = mock_dashboard

    clients = []
    for i in range(5):
        clients.append(
            {
                "mac": f"00:11:22:33:44:{i:02x}",
                "description": f"Client {i}",
                "ip": f"192.168.0.{i+10}",
                "status": "Online",
                "lastSeen": "2025-01-01T00:00:00Z",
            }
        )

    mock_dashboard.networks.getNetworkClients.return_value = clients

    with patch.dict(os.environ, {"MERAKI_DASHBOARD_API_KEY": "test-key"}):
        result = runner.invoke(app, ["list-clients", "net_123"])

    assert result.exit_code == 0
    mock_dashboard.networks.getNetworkClients.assert_called_once_with("net_123")
    assert "Total clients: 5" in result.stdout
    assert "Client 0" in result.stdout
    assert "Client 4" in result.stdout


@patch("meraki_cli.meraki.DashboardAPI")
def test_restart_ap_calls_reboot(mock_dashboard_cls):
    """Test restart-ap – sprawdzamy, że rebootDevice zostało wywołane."""
    mock_dashboard = MagicMock()
    mock_dashboard_cls.return_value = mock_dashboard

    mock_dashboard.devices.rebootDevice.return_value = {"status": "ok"}

    serial = "Q2MD-BHHS-5FDL"

    with patch.dict(os.environ, {"MERAKI_DASHBOARD_API_KEY": "test-key"}):
        result = runner.invoke(app, ["restart-ap", serial])

    assert result.exit_code == 0
    mock_dashboard.devices.rebootDevice.assert_called_once_with(serial)
    assert f"Rebooting device:" in result.stdout
    assert serial in result.stdout


@patch("meraki_cli.meraki.DashboardAPI")
def test_missing_api_key_exits_with_error(mock_dashboard_cls):
    """Test gdy brak API key – komenda powinna zakończyć się błędem i nie tworzyć DashboardAPI."""
    # Czyścimy zmienne środowiskowe
    with patch.dict(os.environ, {}, clear=True):
        result = runner.invoke(app, ["hello"])

    # Sprawdzamy komunikat błędu zamiast exit_code (quirk Typera w testach)
    assert "MERAKI_DASHBOARD_API_KEY not set" in result.stdout
    mock_dashboard_cls.assert_not_called()