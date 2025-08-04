from typing import Annotated
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

# SQLMODEL_DATABASE_URL = 'postgres://<username>:<password>@<ip-address/hostname>/<database_name>'

SQLMODEL_DATABASE_URL = 'postgres://jitu:jitu@localhost/test'

engine = create_engine(SQLMODEL_DATABASE_URL)
