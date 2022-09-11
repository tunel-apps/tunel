__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021-2022, Vanessa Sochat"
__license__ = "MPL 2.0"


schema_url = "https://json-schema.org/draft-07/schema/#"

# App schema and properties

arguments = {
    "type": "object",
    "required": ["name", "description"],
    "properties": {
        "name": {"type": "string"},
        "description": {"type": "string"},
        "split": {"type": ["null", "string"]},
    },
}

appSettingsProperties = {
    "launcher": {"type": "string"},
    "launchers_supported": {"type": "array", "items": {"type": "string"}},
    "script": {"type": "string"},
    "description": {"type": "string"},
    "args": {"type": "array", "items": arguments},
    "examples": {"type": ["array", "string"]},
    "commands": {
        "type": "object",
        "properties": {
            "post": {"type": "string"},
        },
    },
    "needs": {
        "type": "object",
        "properties": {
            "modules": {"type": "array", "items": {"type": "string"}},
            "socket": {"type": "boolean"},
            "xserver": {"type": "boolean"},
        },
    },
}

app_schema = {
    "$schema": schema_url,
    "title": "Tunel App Schema",
    "type": "object",
    "required": ["launcher", "script", "description"],
    "properties": appSettingsProperties,
    "additionalProperties": False,
}

# Launchers properties

singularity_launcher = {
    "type": "object",
    "required": [
        "paths",
    ],
    "properties": {
        "paths": {"type": "array", "items": {"type": "string"}},
        "environment": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}

# This is also shared by htcondor
slurm_launcher = {
    "type": "object",
    "required": [
        "memory",
        "time",
    ],
    "properties": {
        "memory": {"type": ["string", "number"]},
        "max_attempts": {"type": ["number", "null"]},
        "time": {"type": "string"},
        "paths": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}


launchers = {
    "type": "object",
    "required": [
        "htcondor",
        "singularity",
        "slurm",
    ],
    "properties": {
        "singularity": singularity_launcher,
        "slurm": slurm_launcher,
        "htcondor": slurm_launcher,
    },
    "additionalProperties": False,
}

shells = ["/bin/bash", "/bin/sh", "/bin/csh"]

# Currently all of these are required
settingsProperties = {
    "ssh_port": {"type": "number"},
    "launchers": launchers,
    "local_port": {"type": "number"},
    "remote_port": {"type": ["number", "null"]},
    "tunel_home": {"type": "string"},
    "tunel_remote_home": {"type": "string"},
    "tunel_remote_work": {"type": "string"},
    "tunel_remote_sockets": {"type": ["string", "null"]},
    "ssh_config": {"type": "string"},
    "ssh_sockets": {"type": "string"},
    "min_port": {"type": "number"},
    "max_port": {"type": "number"},
    "shell": {"type": "string", "enum": shells},
    "config_editor": {"type": "string", "enum": ["nano", "vim", "emacs", "atom"]},
    "apps_dirs": {"type": "array", "items": {"type": "string"}},
    "tunel_spinner": {"type": "string"},
}

settings = {
    "$schema": schema_url,
    "title": "Tunel Settings Schema",
    "type": "object",
    "required": [
        "apps_dirs",
        "local_port",
        "remote_port",
        "ssh_config",
        "ssh_sockets",
        "tunel_home",
        "tunel_remote_home",
        "min_port",
        "max_port",
        "config_editor",
    ],
    "properties": settingsProperties,
    "additionalProperties": False,
}
