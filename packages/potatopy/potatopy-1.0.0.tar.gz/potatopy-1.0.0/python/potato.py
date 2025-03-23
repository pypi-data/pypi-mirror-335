import configparser
import psycopg2
import mysql.connector
import cx_Oracle
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy import create_engine
import os
import ftplib
import re
import traceback
import logging
import json
import csv
import shutil
from tkinter import messagebox


class Config:
    """Handles reading configuration from a config file."""

    def __init__(self, config_file):
        self.config = configparser.ConfigParser()
        self.config.read(config_file, encoding='utf-8')

    def get(self, section, key):
        return self.config.get(section, key)


class Database:
    """Base class for handling database connections."""

    def __init__(self, db_url):
        self.engine = create_engine(db_url)

    def execute(self, query, values=None, fetch=None, many=False):
        with self.engine.connect() as conn:
            with conn.begin():
                result = conn.execute(
                    query, values) if values else conn.execute(query)
                if fetch == "one":
                    return result.fetchone()
                elif fetch == "many":
                    return result.fetchmany()
                elif fetch == "all":
                    return result.fetchall()


class PostgreSQL(Database):
    """Handles PostgreSQL database connections and operations."""

    def __init__(self, database, host, user, password, port=5432):
        db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        super().__init__(db_url)


class MySQL(Database):
    """Handles MySQL database connections and operations."""

    def __init__(self, database, host="localhost", user="root", password="root"):
        db_url = f"mysql+mysqlconnector://{user}:{password}@{host}/{database}"
        super().__init__(db_url)


class OracleDB:
    """Handles Oracle database connections and operations."""

    def __init__(self, dsn, user, password):
        self.connection = cx_Oracle.connect(
            user=user, password=password, dsn=dsn)

    def execute(self, query, fetch=None):
        with self.connection.cursor() as cursor:
            cursor.execute(query)
            if fetch == "one":
                return cursor.fetchone()
            elif fetch == "many":
                return cursor.fetchmany()
            elif fetch == "all":
                return cursor.fetchall()

    def close(self):
        self.connection.close()


class EmailService:
    """Handles email sending with SMTP."""

    def send_email(self, sender, recipient, subject, body, smtp_server, smtp_port, recipient_cc=""):
        try:
            recipients = recipient.split(';')
            recipients_cc = recipient_cc.split(';') if recipient_cc else []

            msg = MIMEMultipart()
            msg["Subject"] = subject
            msg["From"] = sender
            msg["To"] = ";".join(recipients)
            if recipients_cc:
                msg["CC"] = ";".join(recipients_cc)

            msg.attach(MIMEText(body, "html"))

            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.sendmail(sender, recipients +
                                recipients_cc, msg.as_string())

            return True
        except Exception as e:
            print(f"Email sending error: {e}")
            return False


logging.basicConfig(level=logging.ERROR)


class FTP:
    def __init__(self, host: str, user: str, password: str):
        self.host = host
        self.user = user
        self.password = password

    def _connect(self):
        """Create an FTP connection."""
        return ftplib.FTP(self.host, self.user, self.password)

    def upload_file(self, local_path: str, remote_path: str) -> bool:
        """Upload a file to the FTP server."""
        if not os.path.exists(local_path):
            logging.error(f"File not found: {local_path}")
            return False
        try:
            with self._connect() as ftp:
                self.make_dir(os.path.dirname(remote_path))
                with open(local_path, 'rb') as f:
                    ftp.storbinary(f'STOR {remote_path}', f)
            return True
        except Exception as e:
            logging.error(f"Upload failed: {e}\n{traceback.format_exc()}")
            return False

    def download_file(self, remote_path: str, local_path: str) -> bool:
        """Download a file from the FTP server."""
        try:
            with self._connect() as ftp:
                if not self.exists(remote_path):
                    logging.error(f"Remote file not found: {remote_path}")
                    return False

                os.makedirs(os.path.dirname(local_path), exist_ok=True)
                with open(local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {remote_path}', f.write)
            return True
        except Exception as e:
            logging.error(f"Download failed: {e}\n{traceback.format_exc()}")
            return False

    def delete_file(self, remote_path: str) -> bool:
        """Delete a file from the FTP server."""
        try:
            with self._connect() as ftp:
                if self.exists(remote_path):
                    ftp.delete(remote_path)
                    return True
                logging.error(f"File does not exist: {remote_path}")
        except Exception as e:
            logging.error(f"Deletion failed: {e}\n{traceback.format_exc()}")
        return False

    def list_files(self, remote_dir: str) -> list:
        """List files in a remote directory."""
        try:
            with self._connect() as ftp:
                return ftp.nlst(remote_dir)
        except Exception as e:
            logging.error(
                f"Failed to list files: {e}\n{traceback.format_exc()}")
            return []

    def rename(self, old_path: str, new_path: str, overwrite: bool = False) -> bool:
        """Rename or move a file on the FTP server."""
        try:
            with self._connect() as ftp:
                if not self.exists(old_path):
                    logging.error(f"File not found: {old_path}")
                    return False

                if overwrite and self.exists(new_path):
                    self.delete_file(new_path)

                ftp.rename(old_path, new_path)
                return True
        except Exception as e:
            logging.error(f"Rename failed: {e}\n{traceback.format_exc()}")
            return False

    def exists(self, remote_path: str) -> bool:
        """Check if a file or directory exists on the FTP server."""
        try:
            with self._connect() as ftp:
                # If the file exists, this won't raise an error.
                ftp.size(remote_path)
                return True
        except ftplib.error_perm:
            return False  # File does not exist
        except Exception as e:
            logging.error(f"Existence check failed: {e}")
            return False

    def make_dir(self, remote_dir: str) -> bool:
        """Create directories recursively on the FTP server."""
        parts = remote_dir.strip("/").split("/")
        path = ""
        try:
            with self._connect() as ftp:
                for part in parts:
                    path += f"/{part}"
                    if not self.exists(path):
                        ftp.mkd(path)
            return True
        except Exception as e:
            logging.error(
                f"Directory creation failed: {e}\n{traceback.format_exc()}")
            return False


class Template:
    def __init__(self):
        self.db_connector = DatabaseConnector()
        self.email_notifier = EmailConfig()
        self.button_icon = ButtonIcon()
        self.custom_table = None
        self.selected_column = 0

    def config(self, section, value):
        return self.configuration.get(section, value)

    def load_localization(self, lang_code):
        """Load localization file."""
        try:
            with open(f'{lang_code}.json', 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            logging.error(f"Localization load failed: {e}")
            return {}

    def list_files(self, folder_path):
        """List all files in a folder."""
        return [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))] if os.path.isdir(folder_path) else []

    def read_csv(self, file_path):
        """Read a CSV file into a list."""
        try:
            with open(file_path, newline='') as csvfile:
                return list(csv.reader(csvfile))
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
        except Exception as e:
            logging.error(f"CSV read failed: {e}")
        return []

    def move_directory(self, src, dest, filename):
        """Move a directory."""
        dest_path = os.path.join(dest, filename)
        if os.path.exists(dest_path):
            shutil.rmtree(dest_path)
        shutil.move(src, dest)

    def delete_directory(self, folder_path):
        """Delete a directory."""
        try:
            shutil.rmtree(folder_path)
            logging.info(f"Deleted: {folder_path}")
        except FileNotFoundError:
            logging.error(f"Folder not found: {folder_path}")
        except Exception as e:
            logging.error(f"Error deleting folder: {e}")

    def export_to_csv(self, data_table, file_path, message):
        """Export data to a CSV file."""
        try:
            with open(file_path, "w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.writer(csv_file)
                writer.writerow([data_table.heading(col)["text"]
                                for col in data_table["columns"]])
                for row_id in data_table.get_children():
                    writer.writerow(data_table.item(row_id, "values"))
            messagebox.showinfo("INFO", message)
        except Exception as e:
            logging.error(f"CSV export failed: {e}")

    def db_execute(self, query, params, commit=False):
        """Execute a database query."""
        try:
            db_conn = self.db_connector.connect_postgresql(**params)
            if commit:
                db_conn.commit(query)
                return "OK"
            return db_conn.fetchall(query)
        except Exception as e:
            logging.error(f"Database error: {e}")
            return str(e)


if __name__ == "__main__":
    app = Template()
    app.run_interval()
