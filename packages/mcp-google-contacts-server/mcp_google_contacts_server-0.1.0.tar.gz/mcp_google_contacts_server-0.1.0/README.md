# 📇 MCP Google Contacts Server

A Machine Conversation Protocol (MCP) server that provides Google Contacts functionality, allowing AI assistants to manage contacts, search your organization's directory, and interact with Google Workspace.

## ✨ Features

- List and search Google Contacts
- Create, update, and delete contacts
- Search Google Workspace directory
- View "Other Contacts" (people you've interacted with but haven't added)
- Access Google Workspace users in your organization

## 🚀 Installation

### 📋 Prerequisites

- Python 3.12 or higher
- Google account with contacts access
- Google Cloud project with People API enabled
- OAuth 2.0 credentials for Google API access

### 🧪 Using uv (Recommended)

1. Install uv if you don't have it already:
   ```bash
   pip install uv
   ```

2. Clone the repository:
   ```bash
   git clone https://github.com/rayanzaki/mcp-google-contacts-server.git
   cd mcp-google-contacts-server
   ```

3. Create a virtual environment and install dependencies:
   ```bash
   uv venv
   uv pip install -r requirements.txt
   ```

### 📦 Using pip

1. Clone the repository:
   ```bash
   git clone https://github.com/rayanzaki/mcp-google-contacts-server.git
   cd mcp-google-contacts-server
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 🔑 Authentication Setup

The server requires Google API credentials to access your contacts. You have several options:

### 🔐 Option 1: Using a credentials.json file

1. Create a Google Cloud project and enable the People API
2. Create OAuth 2.0 credentials (Desktop application type)
3. Download the credentials.json file
4. Place it in one of these locations:
   - The root directory of this project
   - Your home directory (~/google-contacts-credentials.json)
   - Specify its location with the `--credentials-file` argument

### 🔐 Option 2: Using environment variables

Set the following environment variables:
- `GOOGLE_CLIENT_ID`: Your Google OAuth client ID
- `GOOGLE_CLIENT_SECRET`: Your Google OAuth client secret
- `GOOGLE_REFRESH_TOKEN`: A valid refresh token for your account

## 🛠️ Usage

### 🏃‍♂️ Basic Startup

```bash
python main.py
# or
uv run main.py
```

This starts the server with the default stdio transport.

### ⚙️ Command Line Arguments

| Argument | Description | Default Value |
|----------|-------------|---------------|
| `--transport` | Transport protocol to use (`stdio` or `http`) | `stdio` |
| `--host` | Host for HTTP transport | `localhost` |
| `--port` | Port for HTTP transport | `8000` |
| `--client-id` | Google OAuth client ID (overrides environment variable) | - |
| `--client-secret` | Google OAuth client secret (overrides environment variable) | - |
| `--refresh-token` | Google OAuth refresh token (overrides environment variable) | - |
| `--credentials-file` | Path to Google OAuth credentials.json file | - |

### 📝 Examples

Start with HTTP transport:
```bash
python main.py --transport http --port 8080
```

Use specific credentials file:
```bash
python main.py --credentials-file /path/to/your/credentials.json
```

Provide credentials directly:
```bash
python main.py --client-id YOUR_CLIENT_ID --client-secret YOUR CLIENT_SECRET --refresh-token YOUR_REFRESH_TOKEN
```

## 🔌 Integration with MCP Clients

To use this server with MCP clients (like Anthropic's Claude with Cline), add it to your MCP configuration:

```json
{
  "mcpServers": {
    "google-contacts-server": {
      "command": "uv",
      "args": [
         "--directory",
         "/path/to/mcp-google-contacts-server",
         "run",
        "main.py"
      ],
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

## 🧰 Available Tools

This MCP server provides the following tools:

| Tool | Description |
|------|-------------|
| `list_contacts` | List all contacts or filter by name |
| `get_contact` | Get a contact by resource name or email |
| `create_contact` | Create a new contact |
| `update_contact` | Update an existing contact |
| `delete_contact` | Delete a contact by resource name |
| `search_contacts` | Search contacts by name, email, or phone number |
| `list_workspace_users` | List Google Workspace users in your organization's directory |
| `search_directory` | Search for people in the Google Workspace directory |
| `get_other_contacts` | Retrieve contacts from the 'Other contacts' section |

### 🔍 Detailed Tool Descriptions

#### 📋 `list_contacts`
Lists all your Google contacts or filters them by name.

**Parameters:**
- `name_filter` (optional): String to filter contacts by name
- `max_results` (optional): Maximum number of contacts to return (default: 100)

**Example:**
```python
list_contacts(name_filter="John", max_results=10)
```

#### 👤 `get_contact`
Retrieves detailed information about a specific contact.

**Parameters:**
- `identifier`: Resource name (people/*) or email address of the contact

**Example:**
```python
get_contact("john.doe@example.com")
# or
get_contact("people/c12345678901234567")
```

#### ➕ `create_contact`
Creates a new contact in your Google Contacts.

**Parameters:**
- `given_name`: First name of the contact
- `family_name` (optional): Last name of the contact
- `email` (optional): Email address of the contact
- `phone` (optional): Phone number of the contact

**Example:**
```python
create_contact(given_name="Jane", family_name="Smith", email="jane.smith@example.com", phone="+1-555-123-4567")
```

#### ✏️ `update_contact`
Updates an existing contact with new information.

**Parameters:**
- `resource_name`: Contact resource name (people/*)
- `given_name` (optional): Updated first name
- `family_name` (optional): Updated last name
- `email` (optional): Updated email address
- `phone` (optional): Updated phone number

**Example:**
```python
update_contact(resource_name="people/c12345678901234567", email="new.email@example.com")
```

#### 🗑️ `delete_contact`
Deletes a contact from your Google Contacts.

**Parameters:**
- `resource_name`: Contact resource name (people/*) to delete

**Example:**
```python
delete_contact(resource_name="people/c12345678901234567")
```

#### 🔍 `search_contacts`
Searches your contacts by name, email, or phone number.

**Parameters:**
- `query`: Search term to find in contacts
- `max_results` (optional): Maximum number of results to return (default: 10)

**Example:**
```python
search_contacts(query="john", max_results=5)
```

#### 🏢 `list_workspace_users`
Lists Google Workspace users in your organization's directory.

**Parameters:**
- `query` (optional): Search term to find specific users
- `max_results` (optional): Maximum number of results to return (default: 50)

**Example:**
```python
list_workspace_users(query="engineering", max_results=25)
```

#### 🔭 `search_directory`
Performs a targeted search of your organization's Google Workspace directory.

**Parameters:**
- `query`: Search term to find specific directory members
- `max_results` (optional): Maximum number of results to return (default: 20)

**Example:**
```python
search_directory(query="product manager", max_results=10)
```

#### 👥 `get_other_contacts`
Retrieves contacts from the 'Other contacts' section - people you've interacted with but haven't added to your contacts.

**Parameters:**
- `max_results` (optional): Maximum number of results to return (default: 50)

**Example:**
```python
get_other_contacts(max_results=30)
```

## 🔒 Permissions

When first running the server, you'll need to authenticate with Google and grant the necessary permissions to access your contacts. The authentication flow will guide you through this process.

## ❓ Troubleshooting

- **🔐 Authentication Issues**: Ensure your credentials are valid and have the necessary scopes
- **⚠️ API Limits**: Be aware of Google People API quota limits
- **📝 Logs**: Check the console output for error messages and debugging information

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
