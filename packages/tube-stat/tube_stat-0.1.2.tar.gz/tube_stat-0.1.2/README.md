# Tubestat

Python CLI tool to see London tube statuses from the command line.

## Installation

```console
pipx install tube-stat
```

Tubestat relies on a `config.json` file with the following format:

```json
{
  "APP": "<APPID>",
  "KEY": "<KEY>"
}
```

You will need to sign up for a developer API key and app name at [TFL](https://api.tfl.gov.uk/).

On Linux and Mac, the app looks for the following path:

`/Users/$HOME/.config/tubestat/config.json`

On Windows:

`/Users/$HOME/AppData/Roaming/tubestat/config.json`

## Usage

Return the status on all lines:

```console
tubestat
```

Return the status only on the Bakerloo line, for example:

```console
tubestat --line bakerloo
```

Return the status for both the Bakerloo and Central line, for example:

```console
tubestat --line bakerloo,central
```

All possible lines:

```console
"bakerloo"
"victoria"
"central"
"circle"
"district"
"hammersmith-city"
"jubilee"
"metropolitan"
"northern"
"piccadilly"
"waterloo-city"
"dlr"
"overground"
"tram"
"elizabeth"
```
