# Hologres MCP Server
Hologres MCP Server serves as a universal interface between AI Agents and Hologres databases. It enables seamless communication between AI Agents and Hologres, helping AI Agents retrieve Hologres database metadata and execute SQL operations.

## Configuration
### Mode 1: Using Local File
#### Download
Download from Github
```shell
git clone https://github.com/aliyun/alibabacloud-hologres-mcp-server.git
```
#### MCP Integration
Add the following configuration to the MCP client configuration file:
```json
"mcpServers": {
  "hologres-mcp-server": {
    "command": "uv",
    "args": [
      "--directory",
      "/path/to/alibabacloud-hologres-mcp-server",
      "run",
      "hologres-mcp-server"
    ],
    "env": {
      "HOLOGRES_HOST": "host",
      "HOLOGRES_PORT": "port",
      "HOLOGRES_USER": "access_id",
      "HOLOGRES_PASSWORD": "access_key",
      "HOLOGRES_DATABASE": "database"
    }
  }
}
```

### Mode 2: Using PIP Mode
#### Installation
Install MCP Server using the following package:
```bash
pip install hologres-mcp-server
```

#### MCP Integration
Add the following configuration to the MCP client configuration file:
```json
  "mcpServers": {
    "hologres-mcp-server": {
      "command": "uv",
      "args": [
        "run",
        "--with",
        "hologres-mcp-server",
        "hologres-mcp-server"
      ],
      "env": {
        "HOLOGRES_HOST": "host",
        "HOLOGRES_PORT": "port",
        "HOLOGRES_USER": "access_id",
        "HOLOGRES_PASSWORD": "access_key",
        "HOLOGRES_DATABASE": "database"
      }
    }
  }
```

## Components
### Tools
* `execute_sql`: Execute queries in Hologres

* `analyze_table`: Collect table statistics

* `get_query_plan`: Get query plan

* `get_execution_plan`: Get execution plan

### Resources
#### Built-in Resources
* `hologres:///schemas`: Get all schemas in the database

* `hologres:///system_info/missing_stats_tables`: Retrieve tables lacking statistics

#### Resource Templates
* `hologres:///{schema}/tables`: List all tables in a schema

* `hologres:///{schema}/{table}/ddl`: Get table DDL

* `hologres:///{schema}/{table}/statistic`: Show collected table statistics

* `hologres:///system_info/latest_query_log/{row_limits}`: Get recent query logs

* `hologres:///system_info/user_query_log/{user}`: Get specific user's query logs

* `hologres:///system_info/application_query_log/{application}`: Get specific application's query logs

### Prompts
None at this time