__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2021, Vanessa Sochat"
__license__ = "MPL 2.0"


schema_url = "https://json-schema.org/draft-07/schema/#"

# Currently all of these are required
settingsProperties = {
    "ssh_port": {"type": "number"},
    "local_port": {"type": "number"},
    "remote_port": {"type": ["number", "null"]},
    "tunel_home": {"type": "string"},
    "ssh_config": {"type": "string"},
    "min_port": {"type": "number"},
    "max_port": {"type": "number"},
    "config_editor": {"type": "string", "enum": ["nano", "vim", "emacs", "atom"]},
    "isolated_nodes": {"type": "boolean"},
}

settings = {
    "$schema": schema_url,
    "title": "Tunel Settings Schema",
    "type": "object",
    "required": [
        "local_port",
        "remote_port",
        "ssh_config",
        "tunel_home",
        "min_port",
        "max_port",
        "config_editor",
        "isolated_nodes",
    ],
    "properties": settingsProperties,
    "additionalProperties": False,
}

"""
# The simplest form of aliases is key/value pairs
aliases = {
    "type": "object",
    "patternProperties": {
        "\\w[\\w-]*": {"type": "string"},
    },
}


# Features in container.yaml can be boolean or null, as they need to be
# container technology agnostic
features = {
    "type": "object",
    "patternProperties": {"\\w[\\w-]*": {"type": ["boolean", "null"]}},
}

# container features can be null or a known string
container_features = {
    "type": "object",
    "properties": {
        "gpu": {
            "oneOf": [{"type": "null"}, {"type": "string", "enum": ["nvidia", "amd"]}]
        },
        "x11": {"oneOf": [{"type": "null"}, {"type": "string"}, {"type": "boolean"}]},
        "home": {"oneOf": [{"type": "null"}, {"type": "string"}]},
    },
}


# Or a list
aliases_list = {
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "name",
            "command",
        ],
        "properties": {
            "name": {"type": "string"},
            "command": {"type": "string"},
            "singularity_options": {"type": "string"},
            "docker_options": {"type": "string"},
        },
    },
}


latest = {
    "type": "object",
    "minProperties": 1,
    "maxProperties": 1,
    "patternProperties": {
        "\\w[\\w-]*": {"type": "string"},
    },
}

containerConfigProperties = {
    "latest": aliases,
    "docker": {"type": "string"},
    "gh": {"type": "string"},
    "url": {"type": "string"},
    "test": {"type": "string"},
    "maintainer": {"type": "string"},
    "description": {"type": "string"},
    "tags": aliases,
    "filter": {
        "type": "array",
        "items": {"type": "string"},
    },
    "env": aliases,
    "features": features,
    "aliases": {
        "oneOf": [
            aliases,
            aliases_list,
        ]
    },
}


containerConfig = {
    "$schema": schema_url,
    "title": "ContainerConfig Schema",
    "type": "object",
    "required": [
        "latest",
        "tags",
        "maintainer",
        "description",
    ],
    "properties": containerConfigProperties,
    "additionalProperties": False,
}


## Settings.yml (loads as json)

shells = ["/bin/bash", "/bin/sh", "/bin/csh"]
"""
