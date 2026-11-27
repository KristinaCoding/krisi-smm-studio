
import os
from pathlib import Path

import psycopg
import streamlit as st
from psycopg.rows import dict_row


def get_database_url():
    url = os.environ.get("DATABASE_URL")

    if not url:
        try:
            url = st.secrets.get("DATABASE_URL")
        except (FileNotFoundError, KeyError):
            url = None

    if not url:
        raise RuntimeError(
            "DATABASE_URL is missing. "
            "Configure it in Streamlit Secrets."
        )

    return url


def connect():
    return psycopg.connect(
        get_database_url(),
        row_factory=dict_row,
        connect_timeout=10,
    )


def init_db():
    schema_path = Path(__file__).with_name(
        "schema_postgres.sql"
    )

    schema = schema_path.read_text(encoding="utf-8")

    with connect() as conn:
        for statement in schema.split(";"):
            if statement.strip():
                conn.execute(statement)
