# Configfacets - Python Client Library

## Overview

As applications scale and integrate with multiple systems, managing configurations becomes increasingly complex. Configfacets simplifies this with a Low-Code/No-Code configuration management system using plain JSON—no custom verbs, no complicated syntax. This Python client library facilitates seamless interaction with the Configfacets API, enabling efficient retrieval and management of configuration data.

Our key features are...

**Repositories & Versioning:**
Design configurations as modular, reusable components, store them in a centralized repository, and maintain full version control for better organization and tracking.

**Reusability:**
Add provider and community-contributed repositories as dependencies, reuse configuration templates, pass in customizable values to effortlessly set up and manage your application configurations.

**Collaboration:**
Invite users and teams to repository with precise role-based permissions—Admin, Collaborator, or Viewer—to control access and streamline contributions.

**REST APIs:**
Expose configurations through REST API endpoints. Generate static and dynamic configurations by leveraging facet filters and runtime configuration values in the request context.

**Organization Management:**
Our hierarchical design simplifies managing multi-level organizational structures, team hierarchies, roles, and responsibilities.

## Usage

### Installation

Ensure you have Python 3.6 or higher installed. Install the library using pip:

```
pip install configfacets
```

```
from configfacets.configuration import Configuration

config = Configuration(
    source="https://configfacets.com/apis/repos/configfacets/core-concepts/appconfigs/resources/collections/api-configurations/exec?format=json",
    sourceType="url",
    apiKey="<your_api_key>",
    postBody={"facets": ["env:prod", "cluster:aws", "region:east"]},
)
config.fetch()
resp = config.get_resp()

rabbitMQHost = config.get_value("rabbitmq.host")
rabbitMQPort = config.get_value("rabbitmq.port")

print("RabbitMQ Host:{}, Port:{}".format(rabbitMQHost, rabbitMQPort))
```

## API Reference

**Configuration**

- `__init__(self, source, sourceType, apiKey=None, postBody=None):` Initializes the configuration object with a source (URL or file) and source type.
- `fetch(self):` Fetches the configuration data from the source.
- `get_resp(self):` Returns the fetched configuration data.
- `get_value(self, key_path):` Retrieves the value for the specified key path.

## Contributing

We welcome contributions! Feel free to connect with us in our [Discord community](https://discord.gg/zWj3Rzud5s).
