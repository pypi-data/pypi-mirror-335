import click
from .engine import convert as convert_engine
from .registry import ConverterRegistry, load_core_converters

# Load core converters (sources and targets)
load_core_converters()

# Load user-installed plugins
ConverterRegistry.load_plugins()

@click.group()
def cli():
    """cao: Convert Anything Offline"""
    pass

@cli.command()
@click.argument('input_path')
@click.argument('output_path')
def convert(input_path, output_path):
    """Convert a file from one format to another."""
    convert_engine(input_path, output_path)

@cli.command("from")
@click.argument('ext')
def list_possible_targets(ext):
    """List all target formats for a given input extension."""
    possible = ConverterRegistry.list_possible_targets(ext)
    if possible:
        click.echo(f"You can convert '{ext}' into:")
        for target in sorted(possible):
            click.echo(f"- {target}")
    else:
        click.echo(f"No known conversions for: {ext}")

@cli.group()
def plugin():
    """Manage plugins for cao"""
    pass

@plugin.command("list")
def list_plugins():
    """List installed plugins"""
    plugins = ConverterRegistry.list_plugins()
    if plugins:
        click.echo("Installed plugins:")
        for plugin in plugins:
            click.echo(f"- {plugin}")
    else:
        click.echo("No plugins installed.")

@plugin.command("install")
@click.argument("plugin_path")
def install_plugin(plugin_path):
    """Install a plugin from a local file"""
    result = ConverterRegistry.install_plugin(plugin_path)
    click.echo(result)

@plugin.command("remove")
@click.argument("plugin_name")
def remove_plugin(plugin_name):
    """Remove an installed plugin by name (without .py)"""
    result = ConverterRegistry.remove_plugin(plugin_name)
    click.echo(result)

@plugin.command("reload")
def reload_plugins():
    """Reload all installed plugins without restarting"""
    ConverterRegistry.load_plugins()
    click.echo("Plugins reloaded.")

@plugin.command("bundle")
@click.argument("output_zip", required=False)
def bundle_plugins(output_zip):
    """Bundle all installed plugins into a .zip"""
    zip_name = output_zip or "cao_plugins_bundle.zip"
    result = ConverterRegistry.bundle_plugins(zip_name)
    click.echo(result)

if __name__ == "__main__":
    cli()
