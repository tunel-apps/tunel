__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


schema_url = "https://json-schema.org/draft-07/schema/#"

# App schema and properties

appSettingsProperties = {
    "launcher": {"type": "string"},
    "script": {"type": "string"},
    "needs": {
        "type": "object",
        "properties": {
            "modules": {"type": "array", "items": {"type": "string"}},
            "args": {"type": "array", "items": {"type": "string"}},
        },
    },
}

app_schema = {
    "$schema": schema_url,
    "title": "Tunel App Schema",
    "type": "object",
    "required": [
        "launcher",
        "script",
    ],
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

slurm_launcher = {
    "type": "object",
    "required": [
        "memory",
        "time",
    ],
    "properties": {
        "memory": {"type": ["string", "number"]},
        "time": {"type": "string"},
        "paths": {"type": "array", "items": {"type": "string"}},
    },
    "additionalProperties": False,
}


launchers = {
    "type": "object",
    "required": [
        "singularity",
        "slurm",
    ],
    "properties": {"singularity": singularity_launcher, "slurm": slurm_launcher},
    "additionalProperties": False,
}

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
    "config_editor": {"type": "string", "enum": ["nano", "vim", "emacs", "atom"]},
    "apps_dirs": {"type": "array", "items": {"type": "string"}},
    "isolated_nodes": {"type": "boolean"},
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
        "isolated_nodes",
    ],
    "properties": settingsProperties,
    "additionalProperties": False,
}
