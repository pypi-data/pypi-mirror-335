import click
from .orchestratorlib import *
import yaml

#  Definition of the CLI commands
@click.group()
def cli():
    """Command-line interface to execute the quditto-orchestrator"""
    pass

# Command to start the qkd-orchestator
# This install the necessary packages on the quditto nodes, and executethe requiered scripts
@cli.command()
@click.argument('config_file', required=True, type=click.File(mode='r'))
@click.argument('inv_file', required=True, type=click.File(mode='r'))

def start(config_file, inv_file):
    """execute an emulated QKD network based on a configuration file (yaml)"""
    
    yaml_config_file = yaml.safe_load(config_file.read())
    yaml_inv_file =  yaml.safe_load(inv_file.read())
    
    # Install the quditto_node requirements and place the topology for the qkd network to simulate (in every node)
    orchestratorlib.install(config_file=yaml_config_file, inv_file=yaml_inv_file)
    
    # Once configured, lets run the quditto_node
    orchestratorlib.run(inv_file=yaml_inv_file)

# Command to stop the simulated qkd-network stopping the python scripts

@cli.command()
@click.argument('inv_file', required=True, type=click.File(mode='r'))

def stop(inv_file):
    """ Function to stop the DT of a QKD Network """
    yaml_inv_file = yaml.safe_load(inv_file.read())
    orchestratorlib.stop(inv_file = yaml_inv_file)

if __name__ == "__main__":
    cli()