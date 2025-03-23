# potato.py Library

The `potato.py` library provides a set of utility functions for common tasks related to database connectivity, email notifications, file operations, and more. This README.md file serves as a guide on how to use the library after installing it from PyPI.

## Installation

To install the `potato.py` library, run the following command:

```bash
pip install potatopy
```

## Usage

Once the library is installed, you can use it in your Python project by importing the necessary modules:

```python
from potatopy import DatabaseConnector, EmailNotifier, Template
```

### Email Notifications

You can send emails using the `EmailNotifier` class.

```python
# Example Usage
email_params = {
    "sender": "your_email@gmail.com",
    "recipient": "recipient1@gmail.com;recipient2@gmail.com",
    "recipient_cc": "cc1@gmail.com;cc2@gmail.com",
    "subject": "Your Email Subject",
    "body": "<p>Your email body in HTML format</p>",
    "footer": "Additional email footer",
    "smtp_server": "your_smtp_server",
    "smtp_port": 587,  # or 21 depending on your need
}

email_notifier = EmailNotifier()
result = email_notifier.send_email(**email_params)
```

### File Operations

You can perform various file operations like listing files, reading CSV files, and moving directories with the `Template` class.

```python
# Example Usage
template = Template()

# List files in a folder
folder_path = "path/to/your/folder"
files = template.list_files_in_folder(folder_path)

# Read data from a CSV file
csv_file_path = "path/to/your/file.csv"
data = template.read_csv_file(csv_file_path)

# Move a directory to a new location
source_path = "path/to/your/source"
destination_path = "path/to/your/destination"
directory_name = "your_directory_name"
template.move_directory(source_path, destination_path, directory_name)

# Delete a directory
folder_to_delete = "path/to/your/folder"
template.delete_directory(folder_to_delete)

# Export data to a CSV file
data_table = your_data_table_widget  # Replace with your actual data table
export_path = "path/to/your/export/file.csv"
message = "Export successful!"
template.export_to_csv(data_table, export_path, message)
```

### Logging and Error Handling

You can initialize logging, log messages with dates, and handle errors.

```python
# Example Usage
template = Template()

# Initialize logging
log_file = "path/to/your/log/file.log"
template.logging_init(log_file)

# Log a message with date
template.logging_date("Your log message with date")

# Log a message without date
template.logging_message("Your log message without date")

# Handle errors
try:
    # Your code that may raise an exception
except Exception as e:
    template.handle_error(e)
```

### GUI Window Operations

You can manage the position and layout of GUI windows with the `Template` class.

```python
# Example Usage
template = Template()

# Set window position
root = your_root_window  # Replace with your actual root window
window = your_child_window  # Replace with your actual child window
width, height = 800, 600  # Set your window dimensions
template.set_window_position(root, window, width, height)

# Fix window position
template.fix_window_position(window, root)
```

### Database Connectivity

The library supports connections to PostgreSQL, MySQL, and Oracle databases.

#### PostgreSQL Connection

```python
# Example Usage
postgres_params = {
    "host": "your_host",
    "database": "your_database",
    "user": "your_user",
    "password": "your_password",
    "port": "your_port",
    "query": "your_query",
}

db_connector = DatabaseConnector()
connection = db_connector.connect_postgresql(**postgres_params)
result = connection.fetchall()
```

#### MySQL Connection

```python
# Example Usage
mysql_params = {
    "host": "your_host",
    "database": "your_database",
    "user": "your_user",
    "password": "your_password",
    "port": "your_port",
    "query": "your_query",
}

db_connector = DatabaseConnector()
connection = db_connector.connect_mysql(**mysql_params)
result = connection.fetchall()
```

#### Oracle Connection

```python
# Example Usage
oracle_params = {
    "host": "your_host",
    "database": "your_database",
    "user": "your_user",
    "password": "your_password",
    "port": "your_port",
    "query": "your_query",
}

db_connector = DatabaseConnector()
connection = db_connector.connect_oracle(**oracle_params)
result = connection.fetchall()
```

### FTP Operations

The `FTP` class provides functionality for interacting with an FTP server, including file uploads, downloads, deletions, file listing, renaming, existence checks, directory creation, and reading file contents.

```python
# Example Usage
ftp = FTP(host_name="your_ftp_host", user="your_ftp_user", password="your_ftp_password")

# Upload a file to the FTP server
local_src_path = "path/to/local/file.txt"
remote_dest_path = "path/to/remote/file.txt"
success = ftp.upload_file(local_src_path, remote_dest_path)
print(f"Upload Successful: {success}")

# Download a file from the FTP server
remote_src_path = "path/to/remote/file.txt"
local_dest_path = "path/to/local/file.txt"
success = ftp.download_file(remote_src_path, local_dest_path)
print(f"Download Successful: {success}")
```

## Miscellaneous

```python
# Example Usage
template = Template()

# Run a function at intervals
template.run_interval()

# Print a formatted message
template.print_message("OK", "Your information message")
template.print_message("NG", "Your error message")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
