import click
import os
import json 
import requests

TUBE_LINES = (
    "bakerloo", "victoria", "central", "circle", "district", "hammersmith-city",
    "jubilee", "metropolitan", "northern", "piccadilly", "waterloo-city", "dlr",
    "overground", "tram", "elizabeth"
)

def get_line_color(line: str) -> tuple[int, int, int]:
    match line:
        case "bakerloo":
            return (179, 99, 5)
        case "victoria":
            return (0, 152, 212)
        case "central":
            return (227, 32, 23)
        case "circle":
            return (255, 211, 0)
        case "district":
            return (0, 120, 42)
        case "elizabeth":
            return (89, 52, 146)
        case "hammersmith-city":
            return (243, 169, 187)
        case "jubilee":
            return (160, 165, 169)
        case "metropolitan":
            return (155, 0, 86)
        case "northern":
            return (0, 0, 0)
        case "piccadilly":
            return (0, 54, 136)
        case "waterloo-city":
            return (149, 205, 186)
        case "dlr":
            return (0, 164, 167)
        case "overground":
            return (238, 124, 14)
        case "tram":
            return (132, 184, 23)
        case _:
            return (128, 128, 128)

# Get user config
def get_config() -> dict:
    if os.name == "nt":
        config_path = os.path.join(os.getenv("APPDATA"), "tubestat", "config.json")
    else:
        config_path = os.path.join(os.path.expanduser("~"), ".config", "tubestat", "config.json")
    print(config_path)
    try:
        with open(config_path, "r") as r:
            json_data = json.load(r)
            return {"APP": json_data["APP"], "KEY": json_data["KEY"]}
    except Exception:
        raise click.ClickException(f'ensure that config.json exists and it is properly configured. Instructions are in the Readme')

@click.command()
@click.option("--line", default=None, help="comma separated tube lines, e.g bakerloo,central")
def cli(line):
    app_data = get_config()
    APP = app_data.get("APP")
    KEY = app_data.get("KEY")

    if line:
        requested_lines = line.split(",")
        invalid_lines = [l for l in requested_lines if l not in TUBE_LINES]
        if invalid_lines:
            raise click.ClickException(f'Invalid tube lines: {', '.join(invalid_lines)}')
        else:
            requested_lines = ','.join(requested_lines)
    else:
        requested_lines = ','.join(TUBE_LINES)
    
    req_url = f'https://api.tfl.gov.uk/Line/{requested_lines}/Status?app_id={APP}&app_key={KEY}'

    try:
        res = requests.get(req_url)
        res.raise_for_status()
    except Exception as e:
        raise click.ClickException(f'Invalid api call {e}')

    res_json = json.loads(res.text)
    print_str = ""
    
    for i, r in enumerate(res_json):
        if len(res_json) - 1 != i:
            line_break = "\n"
        else:
            line_break = ""
        line_colour = get_line_color(r["id"]) 
        print_str += f'{click.style(r["name"], bg=line_colour)}: {r["lineStatuses"][0]["statusSeverityDescription"]}{line_break}'
    click.echo(print_str)

if __name__ == "__main__":
    try:
        cli()
    except click.ClickException as e:
        click.echo(str(e), err=True)
        raise click.exceptions.Exit(1)
