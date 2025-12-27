import os
import typer
import meraki
from rich.console import Console
from rich.table import Table
from typing import Optional

app = typer.Typer()
console = Console()

def get_dashboard():
    api_key = os.getenv("MERAKI_DASHBOARD_API_KEY")
    if not api_key:
        console.print("[red]Error: MERAKI_DASHBOARD_API_KEY not set.[/red]")
        raise typer.Exit(1)
    return meraki.DashboardAPI(api_key, suppress_logging=True)

@app.command("hello")
def hello():
    """Test connection"""
    try:
        dashboard = get_dashboard()
        console.print("[green]API Connection: OK[/green]")
    except Exception as e:
        console.print(f"[red]API Connection: FAILED ({e})[/red]")

@app.command("list-networks")
def list_networks():
    """List all networks in organization"""
    try:
        dashboard = get_dashboard()
        
        # Get organizations
        orgs = dashboard.organizations.getOrganizations()
        if not orgs:
            console.print("[yellow]No organizations found.[/yellow]")
            return
        
        # Use first organization
        org_id = orgs[0]['id']
        org_name = orgs[0]['name']
        console.print(f"[cyan]Organization:[/cyan] {org_name} (ID: {org_id})")
        
        # Get networks for organization
        networks = dashboard.organizations.getOrganizationNetworks(org_id)
        
        if not networks:
            console.print("[yellow]No networks found.[/yellow]")
            return
        
        # Display networks in table
        table = Table(title="Networks")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Product Types", style="magenta")
        
        for network in networks:
            network_id = network.get('id', 'N/A')
            network_name = network.get('name', 'N/A')
            product_types = ', '.join(network.get('productTypes', []))
            table.add_row(network_id, network_name, product_types)
        
        console.print(table)
        console.print(f"\n[green]Total networks: {len(networks)}[/green]")
        
    except meraki.APIError as e:
        console.print(f"[red]Meraki API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command("list-clients")
def list_clients(network_id: str):
    """List clients in a network"""
    try:
        dashboard = get_dashboard()
        
        console.print(f"[cyan]Fetching clients for network:[/cyan] {network_id}")
        
        # Get clients for network
        clients = dashboard.networks.getNetworkClients(network_id)
        
        if not clients:
            console.print("[yellow]No clients found in this network.[/yellow]")
            return
        
        # Display clients in table
        table = Table(title="Network Clients")
        table.add_column("MAC", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("IP", style="magenta")
        table.add_column("Status", style="yellow")
        table.add_column("Last Seen", style="blue")
        
        for client in clients:
            mac = client.get('mac', 'N/A')
            description = client.get('description', 'N/A')
            ip = client.get('ip', 'N/A')
            status = client.get('status', 'N/A')
            last_seen = client.get('lastSeen', 'N/A')
            
            table.add_row(mac, description, ip, status, last_seen)
        
        console.print(table)
        console.print(f"\n[green]Total clients: {len(clients)}[/green]")
        
    except meraki.APIError as e:
        console.print(f"[red]Meraki API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command("list-devices")
def list_devices(network_id: str):
    """List devices in a network"""
    try:
        dashboard = get_dashboard()

        console.print(f"[cyan]Fetching devices for network:[/cyan] {network_id}")

        devices = dashboard.networks.getNetworkDevices(network_id)

        if not devices:
            console.print("[yellow]No devices found in this network.[/yellow]")
            return

        table = Table(title="Network Devices")
        table.add_column("Serial", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Model", style="magenta")
        table.add_column("MAC", style="yellow")

        for device in devices:
            serial = device.get("serial", "N/A")
            name = device.get("name", "N/A")
            model = device.get("model", "N/A")
            mac = device.get("mac", "N/A")
            table.add_row(serial, name, model, mac)

        console.print(table)
        console.print(f"\n[green]Total devices: {len(devices)}[/green]")

    except meraki.APIError as e:
        console.print(f"[red]Meraki API Error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

@app.command("restart-ap")
def restart_ap(
    serial: str,
    network_id: Optional[str] = typer.Option(None, "--network-id", help="List available devices before restart")
):
    """Restart an access point by serial number"""
    try:
        dashboard = get_dashboard()
        
        # If network_id provided, list devices first
        if network_id:
            console.print(f"[cyan]Listing devices in network:[/cyan] {network_id}\n")
            
            try:
                devices = dashboard.networks.getNetworkDevices(network_id)
                
                if not devices:
                    console.print("[yellow]No devices found in this network.[/yellow]")
                    return
                
                # Display devices in table
                table = Table(title="Available Devices")
                table.add_column("Serial", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Model", style="magenta")
                table.add_column("MAC", style="yellow")
                
                for device in devices:
                    dev_serial = device.get('serial', 'N/A')
                    dev_name = device.get('name', 'N/A')
                    dev_model = device.get('model', 'N/A')
                    dev_mac = device.get('mac', 'N/A')
                    
                    table.add_row(dev_serial, dev_name, dev_model, dev_mac)
                
                console.print(table)
                console.print(f"\n[green]Total devices: {len(devices)}[/green]\n")
                
            except meraki.APIError as e:
                console.print(f"[red]Failed to list devices: {e}[/red]")
                raise typer.Exit(1)
        
        # Reboot the device
        console.print(f"[cyan]Rebooting device:[/cyan] {serial}")
        
        response = dashboard.devices.rebootDevice(serial)
        
        console.print(f"[green]✓ Device {serial} reboot initiated successfully![/green]")
        
        if response:
            console.print(f"[dim]Response: {response}[/dim]")
        
    except meraki.APIError as e:
        console.print(f"[red]Meraki API Error: {e}[/red]")
        console.print("[yellow]Hint: Check if the serial number is correct.[/yellow]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()