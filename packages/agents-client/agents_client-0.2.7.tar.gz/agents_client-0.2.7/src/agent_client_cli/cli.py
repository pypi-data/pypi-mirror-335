import typer
import asyncio
import json
import os
import sys
import requests
from pathlib import Path
from typing import Optional, List
import configparser
import webbrowser
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rich_print
from agent_client import send_operation, upload_file, connect_websocket

# Constants
DEFAULT_CONFIG_DIR = os.path.expanduser("~/.agents-api")
CONFIG_FILE = os.path.join(DEFAULT_CONFIG_DIR, "config.ini")
TOKEN_FILE = os.path.join(DEFAULT_CONFIG_DIR, "auth_token.txt")
API_BASE_URL = "http://localhost:6665"  # Default, can be overridden in config

# Rich console for better output
console = Console()

# Create app with help text
app = typer.Typer(help="CLI to interact with the Agent API.")

def ensure_config_dir():
    """Ensure the config directory exists"""
    if not os.path.exists(DEFAULT_CONFIG_DIR):
        os.makedirs(DEFAULT_CONFIG_DIR, exist_ok=True)

def load_auth_token():
    """Load the auth token from the token file if it exists"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return None

def save_auth_token(token):
    """Save the auth token to the token file"""
    ensure_config_dir()
    with open(TOKEN_FILE, "w") as f:
        f.write(token)
    # Set permissions to user read/write only (600)
    os.chmod(TOKEN_FILE, 0o600)

def load_config():
    """Load configuration from the config file"""
    config = configparser.ConfigParser()
    
    if os.path.exists(CONFIG_FILE):
        config.read(CONFIG_FILE)
    
    if 'DEFAULT' not in config:
        config['DEFAULT'] = {}
    
    return config

def save_config(config):
    """Save configuration to the config file"""
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        config.write(f)
    # Set permissions to user read/write only (600)
    os.chmod(CONFIG_FILE, 0o600)

def get_base_url():
    """Get the API base URL from config"""
    config = load_config()
    return config['DEFAULT'].get('api_base_url', API_BASE_URL)

# Legacy commands preserved for backward compatibility
@app.command()
def send(
        operation: str = typer.Argument(..., help="The operation type (e.g. 'message')"),
        params: str = typer.Argument(..., help="JSON string of parameters"),
        api_key: str = typer.Option(None, help="Your API key"),
        agent_id: str = typer.Option(None, help="Your agent ID"),
):
    """
    Send an operation to the agent middleware.
    """
    # Prompt for API key and agent ID if not provided
    if api_key is None:
        api_key = typer.prompt("Enter your API key")
    
    if agent_id is None:
        agent_id = typer.prompt("Enter your agent ID")
        
    try:
        params_dict = json.loads(params)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Invalid JSON for params:[/bold red] {e}")
        raise typer.Exit(1)

    with console.status("Sending operation..."):
        try:
            response = send_operation(operation, params_dict, api_key, agent_id, base_url=get_base_url())
            console.print("[bold green]Operation Response:[/bold green]")
            console.print_json(json.dumps(response))
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def upload(
        file_path: str = typer.Argument(..., help="Path where the file should be saved on the server"),
        local_file: str = typer.Argument(..., help="Local file path to upload"),
        api_key: str = typer.Option(None, help="Your API key"),
        agent_id: str = typer.Option(None, help="Your agent ID"),
):
    """
    Upload a file to the agent middleware.
    """
    # Prompt for API key and agent ID if not provided
    if api_key is None:
        api_key = typer.prompt("Enter your API key")
    
    if agent_id is None:
        agent_id = typer.prompt("Enter your agent ID")
        
    try:
        with open(local_file, "rb") as f:
            with console.status(f"Uploading file {local_file}..."):
                response = upload_file(api_key, agent_id, file_path, f, base_url=get_base_url())
                console.print("[bold green]Upload Response:[/bold green]")
                console.print_json(json.dumps(response))
    except Exception as e:
        console.print(f"[bold red]Error uploading file:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def stream(
        api_key: str = typer.Option(None, help="Your API key"),
        agent_id: str = typer.Option(None, help="Your agent ID"),
):
    """
    Connect to the WebSocket endpoint to stream agent responses.
    """
    # Prompt for API key and agent ID if not provided
    if api_key is None:
        api_key = typer.prompt("Enter your API key")
    
    if agent_id is None:
        agent_id = typer.prompt("Enter your agent ID")
        
    async def run_stream():
        console.print("[bold blue]Connecting to websocket stream...[/bold blue]")
        console.print("[bold blue]Press Ctrl+C to stop.[/bold blue]")
        try:
            async for message in connect_websocket(agent_id, api_key, base_url=get_base_url()):
                console.print("[bold green]Received:[/bold green]")
                console.print_json(json.dumps(message))
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise

    try:
        asyncio.run(run_stream())
    except KeyboardInterrupt:
        console.print("[bold blue]Stream stopped.[/bold blue]")


# New auth token setup and commands

@app.command()
def setup():
    """
    Setup the CLI with your authentication token.
    
    This walks you through the process of creating and saving your secure auth token.
    """
    console.print(Panel.fit(
        "[bold blue]Welcome to the Agents API CLI Setup![/bold blue]\n\n"
        "This will help you set up authentication for the CLI.\n"
        "You'll need to create a secure auth token through the web interface."
    ))
    
    # Step 1: Ask if they want to open the browser
    open_browser = typer.confirm(
        "Would you like to open the token creation page in your browser?",
        default=True
    )
    
    if open_browser:
        auth_url = "https://api.levangielaboratories.com/secure-token"
        console.print(f"[bold blue]Opening:[/bold blue] {auth_url}")
        try:
            webbrowser.open(auth_url)
        except Exception:
            console.print(f"[bold yellow]Could not open browser automatically.[/bold yellow]")
        
    console.print(Panel(
        "1. Log in to your account\n"
        "2. Go to 'Security' or 'API Access' section\n"
        "3. Create a new CLI authentication token\n"
        "4. Download or copy the token"
    ))
    
    # Step 2: Ask for the token
    token_option = typer.prompt(
        "Do you have the token file downloaded (F) or copied to clipboard (C)?",
        default="F"
    ).upper()
    
    auth_token = None
    
    if token_option == "F":
        # Ask for the token file path
        token_file = typer.prompt(
            "Enter the path to your downloaded token file"
        )
        try:
            with open(token_file, "r") as f:
                auth_token = f.read().strip()
        except Exception as e:
            console.print(f"[bold red]Error reading token file:[/bold red] {str(e)}")
            raise typer.Exit(1)
    else:
        # Ask for the token directly
        auth_token = typer.prompt(
            "Paste your authentication token",
            hide_input=True
        )
    
    # Validate token format
    if not auth_token or ":" not in auth_token:
        console.print("[bold red]Invalid token format. Expected format: user_id:salt:token[/bold red]")
        raise typer.Exit(1)
        
    # Save the token
    save_auth_token(auth_token)
    console.print("[bold green]Authentication token saved successfully![/bold green]")
    
    # Set API base URL if needed
    set_base_url = typer.confirm(
        "Would you like to set a custom API base URL? (Default is http://localhost:6665)",
        default=False
    )
    
    if set_base_url:
        base_url = typer.prompt(
            "Enter the API base URL",
            default=API_BASE_URL
        )
        config = load_config()
        config['DEFAULT']['api_base_url'] = base_url
        save_config(config)
        console.print(f"[bold green]API base URL set to:[/bold green] {base_url}")
    
    console.print(Panel.fit(
        "[bold green]Setup complete![/bold green]\n\n"
        "You can now use the CLI commands without having to provide your auth token each time.\n"
        "Try running: [bold]agents-cli info[/bold] to test your authentication."
    ))


@app.command()
def config():
    """
    View or update CLI configuration.
    """
    current_config = load_config()
    
    # Show current configuration
    table = Table(title="Current Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="green")
    
    # Add rows for each config setting
    for key, value in current_config['DEFAULT'].items():
        table.add_row(key, value)
        
    # Add auth token status
    token = load_auth_token()
    table.add_row("Auth Token", "[green]Set[/green]" if token else "[red]Not Set[/red]")
    
    console.print(table)
    
    # Options to update
    update = typer.confirm("Do you want to update any settings?", default=False)
    if update:
        setting = typer.prompt("Which setting? (api_base_url, clear_token)")
        
        if setting == "api_base_url":
            new_value = typer.prompt("Enter new value", default=get_base_url())
            current_config['DEFAULT']['api_base_url'] = new_value
            save_config(current_config)
            console.print(f"[bold green]Updated api_base_url to:[/bold green] {new_value}")
            
        elif setting == "clear_token":
            confirm = typer.confirm("Are you sure you want to clear your saved auth token?", default=False)
            if confirm and os.path.exists(TOKEN_FILE):
                os.remove(TOKEN_FILE)
                console.print("[bold green]Auth token cleared.[/bold green]")
        
        else:
            console.print(f"[bold red]Unknown setting:[/bold red] {setting}")


# Commands for the new info endpoints

def get_auth_headers():
    """Get authentication token for API requests"""
    token = load_auth_token()
    if not token:
        console.print("[bold red]No authentication token found.[/bold red]")
        console.print("Please run 'agents-cli setup' to configure your auth token.")
        raise typer.Exit(1)
    
    return {
        "Content-Type": "application/json"
    }

def call_info_api(action, agent_id=None):
    """Make an API call to the info endpoint"""
    token = load_auth_token()
    if not token:
        console.print("[bold red]No authentication token found.[/bold red]")
        console.print("Please run 'agents-cli setup' to configure your auth token.")
        raise typer.Exit(1)
    
    base_url = get_base_url()
    url = f"{base_url}/info"
    
    payload = {
        "auth_token": token,
        "action": action
    }
    
    if agent_id:
        payload["agent_id"] = agent_id
    
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            console.print("[bold red]Authentication failed.[/bold red]")
            console.print("Your auth token may be invalid or expired.")
            console.print("Please run 'agents-cli setup' to configure a new auth token.")
        else:
            console.print(f"[bold red]API Error:[/bold red] {str(e)}")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        raise typer.Exit(1)


@app.command()
def info():
    """
    Get information about your account and agents.
    Also shows all available commands and how to use them.
    """
    # Get user credits first
    with console.status("Getting account information..."):
        credits_data = call_info_api("get_credits")
    
    rich_print(Panel.fit(
        f"[bold green]Account Credits:[/bold green] {credits_data.get('credits', 0)}\n"
        f"[bold blue]Add more credits:[/bold blue] {credits_data.get('add_credits_url', '')}"
    ))
    
    # Show all available commands grouped by category
    console.print("\n[bold white on blue] AGENTS API CLI COMMANDS [/bold white on blue]")
    
    # Account & Setup commands
    console.print("\n[bold yellow]-- SETUP & CONFIGURATION --[/bold yellow]")
    console.print("  [cyan]agents-cli setup[/cyan]")
    console.print("    Setup your CLI with an authentication token")
    console.print("    [dim]Example: agents-cli setup[/dim]")
    
    console.print("  [cyan]agents-cli config[/cyan]")
    console.print("    View or update your CLI configuration")
    console.print("    [dim]Example: agents-cli config[/dim]")
    
    # Information commands
    console.print("\n[bold yellow]-- INFORMATION COMMANDS --[/bold yellow]")
    console.print("  [cyan]agents-cli info[/cyan]")
    console.print("    Show account information and all available commands")
    console.print("    [dim]Example: agents-cli info[/dim]")
    
    console.print("  [cyan]agents-cli agents[/cyan]")
    console.print("    List all your agents with their status")
    console.print("    [dim]Example: agents-cli agents[/dim]")
    
    console.print("  [cyan]agents-cli api-keys[/cyan]")
    console.print("    List all your API keys")
    console.print("    [dim]Example: agents-cli api-keys[/dim]")
    
    console.print("  [cyan]agents-cli usage[/cyan]")
    console.print("    Show usage statistics for your account")
    console.print("    [dim]Example: agents-cli usage[/dim]")
    
    console.print("  [cyan]agents-cli agent-info <agent_id>[/cyan]")
    console.print("    Show detailed information about a specific agent")
    console.print("    [dim]Example: agents-cli agent-info 2f86289c-33c6-40d7-bfa6-cda143dcc094[/dim]")
    
    # Management commands
    console.print("\n[bold yellow]-- MANAGEMENT COMMANDS --[/bold yellow]")
    console.print("  [cyan]agents-cli create-key [--name KEY_NAME][/cyan]")
    console.print("    Create a new API key")
    console.print("    [dim]Example: agents-cli create-key --name \"My New Key\"[/dim]")
    
    console.print("  [cyan]agents-cli link <action>[/cyan]")
    console.print("    Get links to web resources (dashboard, billing, docs, etc.)")
    console.print("    [dim]Example: agents-cli link dashboard[/dim]")
    
    # Legacy commands
    console.print("\n[bold yellow]-- AGENT INTERACTION (LEGACY) --[/bold yellow]")
    console.print("  [cyan]agents-cli send <operation> <params_json> [--api-key KEY] [--agent-id ID][/cyan]")
    console.print("    Send an operation to an agent")
    console.print("    [dim]Example: agents-cli send message '{\"text\":\"Hello\"}' --api-key mykey --agent-id myagent[/dim]")
    
    console.print("  [cyan]agents-cli upload <server_path> <local_file> [--api-key KEY] [--agent-id ID][/cyan]")
    console.print("    Upload a file to an agent")
    console.print("    [dim]Example: agents-cli upload /data/file.txt ./local.txt --api-key mykey --agent-id myagent[/dim]")
    
    console.print("  [cyan]agents-cli stream [--api-key KEY] [--agent-id ID][/cyan]")
    console.print("    Connect to the WebSocket stream for an agent")
    console.print("    [dim]Example: agents-cli stream --api-key mykey --agent-id myagent[/dim]")
    
    # Final help note
    console.print("\n[bold white on green] NEED MORE HELP? [/bold white on green]")
    console.print("  Run any command with --help for more information")
    console.print("  [dim]Example: agents-cli create-key --help[/dim]")
    console.print("  Visit documentation at: https://api.levangielaboratories.com/docs")


@app.command()
def agents():
    """
    List all your agents.
    """
    with console.status("Fetching your agents..."):
        response = call_info_api("get_agents")
    
    if not response.get("agents"):
        console.print("[bold yellow]You don't have any agents yet.[/bold yellow]")
        return
    
    table = Table(title="Your Agents")
    table.add_column("Name", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Agent ID", style="magenta")
    table.add_column("API Key", style="blue")
    table.add_column("Credits", style="yellow")
    
    for agent in response.get("agents", []):
        # Format status with color
        status = agent.get("status", "unknown")
        status_formatted = f"[green]{status}[/green]" if status == "running" else f"[yellow]{status}[/yellow]"
        
        # Format credits
        credits = agent.get("agent_credits")
        credits_formatted = str(credits) if credits is not None else "-"
        
        table.add_row(
            agent.get("agent_name", "Unnamed"),
            status_formatted,
            agent.get("agent_id", ""),
            agent.get("api_key", "")[:10] + "..." if agent.get("api_key") else "",
            credits_formatted
        )
        
    console.print(table)


@app.command()
def api_keys():
    """
    List your API keys.
    """
    with console.status("Fetching your API keys..."):
        response = call_info_api("get_api_keys")
    
    if not response.get("api_keys"):
        console.print("[bold yellow]You don't have any API keys yet.[/bold yellow]")
        console.print("Use [bold]agents-cli create-key[/bold] to create a new API key.")
        return
    
    table = Table(title="Your API Keys")
    table.add_column("Name", style="cyan")
    table.add_column("Key", style="blue")
    table.add_column("Created", style="green")
    table.add_column("Last Used", style="yellow")
    
    for key in response.get("api_keys", []):
        # Mask most of the key for security
        key_value = key.get("key", "")
        masked_key = key_value[:10] + "..." if key_value else ""
        
        table.add_row(
            key.get("name", "Unnamed"),
            masked_key,
            key.get("created_at", ""),
            key.get("last_used", "-") or "-"
        )
        
    console.print(table)
    console.print("\nUse [bold]agents-cli create-key[/bold] to create a new API key.")


@app.command()
def usage():
    """
    Show usage statistics for your account.
    """
    with console.status("Fetching usage statistics..."):
        response = call_info_api("get_usage")
    
    # Display overall stats
    console.print("[bold]Overall Usage Statistics:[/bold]")
    console.print(f"[bold green]Total Cost:[/bold green] {response.get('total_cost', 0)}")
    console.print(f"[bold cyan]Average Cost Per Hour:[/bold cyan] {response.get('avg_cost_per_hr', 0)}")
    console.print(f"[bold blue]Average Cost Per Day:[/bold blue] {response.get('avg_cost_per_day', 0)}")
    console.print(f"[bold magenta]Average Cost Per Week:[/bold magenta] {response.get('avg_cost_per_week', 0)}")
    
    # Display agent usage table if available
    agents_usage = response.get("agents_usage", [])
    if agents_usage:
        console.print("\n[bold]Usage By Agent:[/bold]")
        table = Table()
        table.add_column("Agent", style="cyan")
        table.add_column("Credits Used", style="yellow")
        
        for agent in agents_usage:
            table.add_row(
                agent.get("agent_name", "Unknown"),
                str(agent.get("credits_used", 0))
            )
            
        console.print(table)
    else:
        console.print("\n[bold yellow]No usage data available yet.[/bold yellow]")


@app.command()
def agent_info(
    agent_id: str = typer.Argument(..., help="ID of the agent to get information about")
):
    """
    Show detailed information about a specific agent.
    """
    with console.status(f"Fetching information for agent {agent_id}..."):
        response = call_info_api("get_agent_info", agent_id=agent_id)
    
    if not response:
        console.print("[bold red]Agent not found or access denied.[/bold red]")
        return
    
    # Display basic info in a panel
    rich_print(Panel.fit(
        f"[bold blue]Agent Name:[/bold blue] {response.get('name', 'Unnamed')}\n"
        f"[bold green]Status:[/bold green] {response.get('container_status', 'Unknown')}\n"
        f"[bold cyan]API Key:[/bold cyan] {response.get('api_key', 'None')}\n"
        f"[bold magenta]ID:[/bold magenta] {response.get('id', 'Unknown')}"
    ))
    
    # Display more detailed information in a table
    table = Table(title="Agent Details")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    
    # Add all relevant properties to the table
    important_props = [
        ("description", "Description"),
        ("tags", "Tags"),
        ("port", "Port"),
        ("external_port", "External Port"),
        ("agent_credits", "Credits"),
        ("is_external", "Is External"),
        ("created_at", "Created At"),
        ("updated_at", "Last Updated")
    ]
    
    for key, label in important_props:
        if key in response:
            value = response[key]
            if value is None:
                value = "-"
            elif isinstance(value, bool):
                value = "Yes" if value else "No"
            table.add_row(label, str(value))
    
    console.print(table)


@app.command()
def create_key(
    name: str = typer.Option(None, help="Name for the new API key")
):
    """
    Create a new API key.
    """
    token = load_auth_token()
    if not token:
        console.print("[bold red]No authentication token found.[/bold red]")
        console.print("Please run 'agents-cli setup' to configure your auth token.")
        raise typer.Exit(1)
    
    # Prompt for key name if not provided
    if name is None:
        name = typer.prompt("Enter a name for the new API key", default="CLI Generated Key")
    
    base_url = get_base_url()
    url = f"{base_url}/createapikey"
    
    payload = {
        "auth_token": token,
        "key_name": name
    }
    
    with console.status("Creating new API key..."):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            key_info = response.json()
            
            console.print("[bold green]API Key Created Successfully![/bold green]")
            console.print(f"[bold]Name:[/bold] {key_info.get('name')}")
            console.print(f"[bold]Key:[/bold] {key_info.get('key')}")
            console.print(f"[bold]Created:[/bold] {key_info.get('created_at')}")
            
            # Important security note
            console.print("\n[bold red]Important:[/bold red] Save this key securely! It won't be shown again.")
            
            # Option to save to file
            save_to_file = typer.confirm("Would you like to save this key to a file?", default=False)
            if save_to_file:
                file_path = typer.prompt("Enter file path to save the key")
                try:
                    with open(file_path, "w") as f:
                        f.write(key_info.get('key', ''))
                    os.chmod(file_path, 0o600)  # Set permissions to user read/write only
                    console.print(f"[bold green]Key saved to:[/bold green] {file_path}")
                except Exception as e:
                    console.print(f"[bold red]Error saving key:[/bold red] {str(e)}")
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                console.print("[bold red]Authentication failed.[/bold red]")
                console.print("Your auth token may be invalid or expired.")
                console.print("Please run 'agents-cli setup' to configure a new auth token.")
            else:
                console.print(f"[bold red]API Error:[/bold red] {str(e)}")
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)


@app.command()
def link(
    action: str = typer.Argument(..., help="The resource to get a link for (e.g., dashboard, billing, docs)")
):
    """
    Get links to various resources in the web interface.
    """
    base_url = get_base_url()
    url = f"{base_url}/proxy"
    
    payload = {
        "action": action
    }
    
    with console.status(f"Getting link for {action}..."):
        try:
            response = requests.post(url, json=payload)
            response.raise_for_status()
            link_info = response.json()
            
            console.print(f"[bold green]Link for {action}:[/bold green] {link_info.get('link')}")
            
            # Ask if they want to open it
            open_link = typer.confirm("Open this link in your browser?", default=False)
            if open_link:
                try:
                    webbrowser.open(link_info.get('link'))
                except Exception:
                    console.print("[bold yellow]Could not open browser automatically.[/bold yellow]")
                    
        except requests.exceptions.HTTPError as e:
            console.print(f"[bold red]API Error:[/bold red] {str(e)}")
            if hasattr(e.response, 'text'):
                try:
                    error_detail = json.loads(e.response.text).get('detail', '')
                    console.print(f"[bold red]Details:[/bold red] {error_detail}")
                except:
                    pass
            raise typer.Exit(1)
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {str(e)}")
            raise typer.Exit(1)


if __name__ == "__main__":
    app()