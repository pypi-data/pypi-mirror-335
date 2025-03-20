import click
import json
import requests

@click.group()
def cli():
    """pifunc CLI tool"""
    pass

@cli.command()
@click.argument('service_name')
@click.option('--protocol', default='http', help='Protocol to use (http, mqtt, etc)')
@click.option('--args', default='{}', help='JSON arguments for the service')
def call(service_name, protocol, args):
    """Call a service with the specified arguments"""
    try:
        args_dict = json.loads(args)
    except json.JSONDecodeError:
        click.echo("Error: Invalid JSON arguments", err=True)
        raise click.Abort()
        
    try:
        if protocol == 'http':
            response = requests.post(
                f'http://localhost:8080/api/{service_name}',
                json=args_dict,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX status codes
            result = response.json()
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Protocol {protocol} not yet implemented")
            
    except requests.RequestException as e:
        click.echo(f"Error: HTTP request failed - {str(e)}", err=True)
        raise click.Abort()
    except Exception as e:
        click.echo(f"Error: {str(e)}", err=True)
        raise click.Abort()

def main():
    cli()

if __name__ == '__main__':
    main()
