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
pip install snowforge-package
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
from Snowforge.AWSIntegration import AWSIntegration

AWSIntegration.initialize(profile="default", verbose=True)
```

### 🔹 Connect to Snowflake

```python
from Snowforge.SnowflakeConnect import SnowflakeConnection

conn = SnowflakeConnection.establish_connection(user_name="your-user", account="your-account")
```

### 🔹 Use Logging

```python
from Snowforge.Logging import Debug

Debug.log("This is an info message", level='INFO')
Debug.log("This is an error message", level='ERROR')
```

### 🔹 Extract Data from an On-Prem Database

```python
import Snowforge.AWSIntegration as aws

def export_and_upload_table_data(extractor: ExtractorStrategy):

    #Fetch data from an on-prem system:
    query = extractor.extract_table_query("database.schema.table", "filter_column", "filter_value")
    full_path_to_file = extractor.export_table_to_file(query, output_path, file_format(optional))

    aws.upload_to_s3("bucket name", full_path_to_file, "key to store the file under in S3")

def main():
    from Snowforge.Extractors.NetezzaExtractor import NetezzaExtractor
    from Snowforge.Extractors.OracleExtractor import OracleExtractor
    from Snowforge.Extractors.PostgrSQLExtractor import PostgrSQLExtractor

    # Export and upload data from different source systems by exchanging the extractor strategy
    export_and_upload_table_data(NetezzaExtractor())
    export_and_upload_table_data(OracleExtractor())
    export_and_upload_table_data(PostgrSQLExtractor())

```

Since **Snowforge** follows a **strategy pattern**, it can be easily extended to support other **database systems** by implementing new extractor classes that conform to the `ExtractorStrategy` interface.

---

## 📜 License

This project is licensed under the **MIT License**.

---

## 👤 Author

Developed by **andreasheggelund@gmail.com**. Feel free to reach out for support, suggestions, or collaboration!
