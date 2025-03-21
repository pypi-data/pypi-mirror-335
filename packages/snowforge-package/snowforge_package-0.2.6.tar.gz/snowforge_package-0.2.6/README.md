# 🚀 Snowforge - Powerful Data Integration

**Snowforge** is a Python package designed to streamline data integration and transfer between **AWS**, **Snowflake**, and various **on-premise database systems**. It provides efficient data extraction, logging, configuration management, and AWS utilities to support robust data engineering workflows.

---

## ✨ Features

- **AWS Integration**: Manage AWS S3 and Secrets Manager operations.
- **Snowflake Connection**: Establish and manage Snowflake connections effortlessly.
- **Advanced Logging**: Centralized logging system with colored output for better visibility.
- **Configuration Management**: Load and manage credentials from a TOML configuration file.
- **Data Mover Engine**: Parallel data processing and extraction strategies for efficiency.
- **Extensible Database Extraction**: Uses a **strategy pattern** to support multiple **on-prem database systems** (e.g., Netezza, Oracle, PostgreSQL, etc.).

---

## 📥 Installation

Install Snowforge using pip:

```sh
pip install snowforge
```

---

## ⚙️ Configuration

Snowforge requires a configuration file (`snowforge_config.toml`) to manage credentials for AWS and Snowflake. The package searches for the config file in the following locations:

1. Path specified in `SNOWFORGE_CONFIG_PATH` environment variable.
2. Current working directory.
3. `~/.config/snowforge_config.toml`
4. Package directory.

### Example `snowforge_config.toml` File

```toml
[AWS]
[default]
AWS_ACCESS_KEY = "your-access-key"
AWS_SECRET_KEY = "your-secret-key"
REGION = "us-east-1"

[SNOWFLAKE]
[default]
USERNAME = "your-username"
ACCOUNT = "your-account"
```

---

## 🚀 Quick Start

### 🔹 Initialize AWS Integration

```python
from snowforge.AWSIntegration import AWSIntegration

AWSIntegration.initialize(profile="default", verbose=True)
```

### 🔹 Connect to Snowflake

```python
from snowforge.SnowflakeConnect import SnowflakeConnection

conn = SnowflakeConnection.establish_connection(user_name="your-user", account="your-account")
```

### 🔹 Use Logging

```python
from snowforge.Logging import Debug

Debug.log("This is an info message", level='INFO')
Debug.log("This is an error message", level='ERROR')
```

### 🔹 Extract Data from an On-Prem Database

```python
from snowforge.Extractors.NetezzaExtractor import NetezzaExtractor

extractor = NetezzaExtractor()
query = extractor.extract_table_query("database.schema.table_name", "date_column", "01.01.2024")
print(query)
```

Since **Snowforge** follows a **strategy pattern**, it can be easily extended to support other **on-prem database systems** by implementing new extractor classes that conform to the `ExtractorStrategy` interface.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👤 Author

Developed by **andreasheggelund@gmail.com**. Feel free to reach out for support, suggestions, or collaboration!
