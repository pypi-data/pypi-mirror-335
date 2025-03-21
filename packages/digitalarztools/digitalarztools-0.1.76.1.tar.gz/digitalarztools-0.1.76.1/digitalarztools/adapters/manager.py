import traceback
from contextlib import contextmanager
from typing import Union, List, Dict, Any, Generator
from urllib import parse

import pandas as pd
import geopandas as gpd
from dotenv import load_dotenv
from pydantic import BaseModel
from shapely import wkb, wkt
from sqlalchemy import Engine, create_engine, Select, text, MetaData, Table, Column, Integer, String, inspect, func, \
    select, QueuePool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker, Session, joinedload
from geoalchemy2 import WKBElement

from digitalarztools.utils.logger import da_logger

load_dotenv()
import logging

logging.disable(logging.WARNING)


class DBString(BaseModel):
    """
    Represents database connection string parameters.
    """
    host: str
    user: str
    password: str
    name: str
    port: str


"""
Usage: 
   DATABASES = {
        "cache_db": {
            "engine": "sqlite",
            "file_path": os.path.join(BASE_DIR, "dch_cache.sqlite")
        },
        "default": {
            "engine": "postgresql+pg8000",
            "host": os.environ.get("DB_HOST") if not IS_LOCAL else localhost,
            "name": os.environ.get("DCH_DB"),
            "port": os.environ.get("DB_PORT"),
            "user": os.environ.get("DB_USER"),
            "password": os.environ.get("DB_PASSWORD")
        },
    }
    config = DBParams( DATABASES['default']['engine'], DATABASES['default'])
    engine = DBManager.create_sql_alchemy_engine(config)
    manager = DBManager(engine)
    with manager.managed_session() as session:
        result = session.execute(text("SELECT * FROM dafastmap_dch.public.dch_map_info"))
        rows = result.fetchall()  # Fetch all rows
         print(len(rows))  # Count of rows
"""


class DBParams:
    """
    Encapsulates database connection parameters and engine type.
    """
    engine: str  # postgresql, sqlite
    con_str: DBString  # either provide file_path or DBString

    def __init__(self, engine: str, con_str: Union[dict, DBString]):
        """
        Initialize DBParams.

        :param engine: Database engine type (e.g., 'postgresql', 'sqlite').
        :param con_str: Connection string parameters, either a file path for SQLite
                        or a DBString object/dictionary for other databases.
        """
        self.engine = engine
        self.con_str = DBString(**con_str) if isinstance(con_str, dict) else con_str

    def __eq__(self, other):
        """
        Compare two DBString objects for equality based on their attributes.
        """
        if not isinstance(other, DBString):
            return False
        return (self.con_str.user == other.con_str.user and
                self.con_str.password == other.con_str.password and
                self.con_str.host == other.con_str.host and
                self.con_str.port == other.con_str.port and
                self.con_str.name == other.con_str.name)


class DBManager:
    """
    Manages database connections and provides methods for interacting with the database.
    """
    engine: Engine = None  # Class-level attribute to store the engine
    connection_params: DBParams = None
    def __init__(self, db_info: Union[DBParams, Engine]):
        """
        Initialize DBManager.

        :param db_info: Either DBParams to create a new engine or an existing Engine.
        """
        if isinstance(db_info, Engine):
            self.engine = db_info
        else:
            self.connection_params = db_info
            self.engine = self.create_sql_alchemy_engine(db_info)
        if self.engine is None:
            raise Exception("Failed to create SQL Alchemy engine")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_engine(self) -> Engine:
        """
        Return the SQLAlchemy Engine associated with this manager.
        """
        return self.engine

    def get_session(self) -> Session:
        """
        Create and return a new SQLAlchemy session from the session factory.
        """
        return self.SessionLocal()

    @contextmanager
    def managed_session(self) -> Generator[Session, None, None]:
        """
        Provide a transactional scope around a series of operations.

        Usage:
            with db_manager.managed_session() as session:
                result = session.query(MyModel).filter_by(name='John').first()
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Session rolled back due to an exception: {e}")
            raise
        finally:
            session.close()

    @staticmethod
    def create_sql_alchemy_engine(config: DBParams) -> Engine:
        """
        Create a SQLAlchemy engine with connection pooling and timeout settings.

        This method now reuses an existing engine if one has already been created.
        """
        if DBManager.engine is not None and DBManager.connection_params==config:  # Check if an engine already exists
            return DBManager.engine
        try:
            if config.engine in ["sqlite"]:
                db_string = f'{config.engine}:///{config.con_str}'
            else:
                params = config.con_str
                db_string = f'{config.engine}://{params.user}:{parse.quote(params.password)}@{params.host}:{params.port}/{params.name}'

            DBManager.engine = create_engine(  # Store the engine at the class level
                db_string,
                echo=False,  # Set to False in production
                poolclass=QueuePool,
                pool_size=10,  # Number of connections to keep open inside the pool
                max_overflow=5,  # Allow 10 extra connections if pool is full
                pool_timeout=30,  # Wait time before raising an error if pool is full
                pool_recycle=1200,  # Recycle connections every 30 minutes (to prevent stale connections)
                # pool_pre_ping=True,  # Check connections before use
                # connect_args={'connect_timeout': 100}
            )
            return DBManager.engine
        except Exception as e:
            traceback.print_exc()
            return None
        # else:
        #     return DBManager.engine  # Return the existing engine

    @classmethod
    def create_postgres_engine(cls, db_str: Union[DBString, dict]):
        """
        Create a PostgreSQL engine.
        """
        if isinstance(db_str, dict):
            db_str = DBString(**db_str)
        params = DBParams(engine='postgresql+psycopg2', con_str=db_str)
        return cls.create_sql_alchemy_engine(params)

    def exists(self, stmt: Select):
        """
        Check if a row exists based on the given SELECT statement.
        """
        with self.managed_session() as session:
            return session.execute(stmt).first() is not None

    def get_sqlalchemy_table(self, table_name, schema_name='public') -> Table:
        """
        Get a SQLAlchemy Table object.
        """
        try:
            metadata = MetaData()
            tbl: Table = Table(
                table_name,
                metadata,
                autoload_with=self.engine,
                schema=schema_name
            )
            return tbl
        except Exception as e:
            traceback.print_exc()
            return None

    def create_xyz_cache_table(self, table_name: str):
        """
        Create a table for XYZ cache data.
        """
        meta_data = MetaData()
        xyz_table = Table(table_name, meta_data,
                          Column('id', Integer, primary_key=True, autoincrement=True),
                          Column('x', Integer),
                          Column('y', Integer),
                          Column('z', Integer),
                          Column('mvt', String))
        meta_data.create_all(self.engine)
        return xyz_table

    def execute_query_as_one(self, query: Union[str, Select]):
        """
        Execute a query and return a single row.
        """
        try:
            with self.managed_session() as session:
                if isinstance(query, str):
                    query_obj = text(query)
                else:
                    query_obj = query
                # Apply eager loading options to the query
                query_obj = query_obj.options(joinedload('*'))
                row = session.execute(query_obj).scalar()
                return row
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            traceback.print_exc()
            return None

    def execute_stmt_as_df(self, stmt: Union[str, Select, Table]) -> pd.DataFrame:
        """
        Execute a statement and return the results as a Pandas DataFrame.
        """
        try:
            with self.managed_session() as session:
                if isinstance(stmt, Select):
                    rs = session.execute(stmt)
                elif isinstance(stmt, Table):
                    stmt = select(stmt)
                    rs = session.execute(stmt)
                else:  # Assuming stmt is a raw string
                    rs = session.execute(text(stmt))
                df = pd.DataFrame(rs.fetchall())
                if not df.empty:
                    df.columns = rs.keys()
                return df
        except SQLAlchemyError as e:
            print(f"Error executing statement: {e}")
            return pd.DataFrame()

    def get_query_data(self, query: Union[Table, Select, str]) -> Any:
        """
        Execute a query and return the results as a list of dictionaries.
        """
        try:
            with self.managed_session() as session:
                if isinstance(query, Table):
                    qs = session.query(query)
                    return qs.all()
                elif isinstance(query, Select):
                    rs = session.execute(query)
                    return rs.fetchall()
                else:
                    rs = session.execute(text(query))
                    return rs.fetchall()
        except SQLAlchemyError as e:
            print(f"Error executing query: {e}")
            return []

    def execute_dml(self, stmt):
        """
        Execute a DML statement (INSERT, UPDATE, DELETE).
        """
        try:
            with self.managed_session() as session:
                if isinstance(stmt, str):
                    stmt = text(stmt)
                session.execute(stmt)
                session.commit()
                return True
        except SQLAlchemyError:
            traceback.print_exc()
            return False

    def execute_ddl(self, stmt):
        """
        Execute a DDL statement (CREATE, ALTER, DROP).
        """
        try:
            with self.managed_session() as session:
                if isinstance(stmt, str):
                    stmt = text(stmt)
                session.execute(stmt)
                session.commit()
                print("DDL performed successfully")
                return True
        except Exception as e:
            traceback.print_exc()
            return False

    def table_to_df(self, tbl: Union[Table, str, Select]):
        """
        Convert a table or SELECT statement results to a Pandas DataFrame.
        """
        if isinstance(tbl, str):
            tbl = self.get_sqlalchemy_table(tbl)
        data = self.get_query_data(tbl)
        return pd.DataFrame(data)

    def get_tables(self):
        """
        Get all tables in the database.
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return list(metadata.tables.values())

    def get_tables_names(self):
        """
        Get names of all tables in the database.
        """
        metadata = MetaData()
        metadata.reflect(bind=self.engine)
        return list(metadata.tables.keys())

    @staticmethod
    def get_table_column_names(table: Table) -> list:
        """
        Get column names of a table.
        """
        if table is not None:
            return [col.name for col in inspect(table).columns]

    @staticmethod
    def get_table_column_types(table: Table) -> list:
        """
        Get column types of a table.
        """
        if table is not None:
            return [col.type for col in inspect(table).columns]

    def inspect_table(self, table_name, schema='public'):
        """
        Inspect a table and print its structure.
        """
        s_t = table_name.split(".")
        schema_name = s_t[0] if len(s_t) > 1 else "public"
        table_name = s_t[-1]
        tbl = self.get_sqlalchemy_table(table_name, schema_name)

        print(f"class {table_name.title().replace('_', '')}(DBBase):")
        print(f'\t__tablename__ = "{table_name}"')
        if schema_name != "public":
            print('\t__table_args__ = {"schema": "' + schema_name + '"}')
        for column in tbl.columns:
            col = f"db.{str(column.type).replace(' ', '_')}, nullable={column.nullable}"
            if column.default is not None:
                col += f", default={column.default}"
            if column.unique:
                col += f", default={column.unique}"
            print(f"\t{column.name}=Column({col})")

    def is_table(self, table_name):
        """
        Check if a table exists.
        """
        inspector = inspect(self.engine)
        return table_name in inspector.get_table_names()

    def con_2_dict(self):
        """
        Convert connection parameters to a dictionary.
        """
        engine = self.get_engine()
        return {
            'engine': engine.url.drivername,
            'host': engine.url.host,
            'port': engine.url.port,
            "user": engine.url.username,
            "password": engine.url.password,
            "db_name": engine.url.database
        }

    def execute_query_as_dict(self, query: Union[str, Select]) -> List[dict]:
        """
        Execute a query and return the results as a list of dictionaries.
        """
        df = self.execute_stmt_as_df(query)
        return df.to_dict(orient='records')

    def get_missing_dates(self, table_name: str, date_col_name: str, start_date: str, end_date: str,
                          id_col_name: str = None, id_col_value: str = None) -> pd.DataFrame:
        """
        Find missing dates in a date column within a specified range.

        :param table_name: Name of the table.
        :param date_col_name: Name of the date column.
        :param start_date: Start date in YYYY-MM-DD format.
        :param end_date: End date in YYYY-MM-DD format.
        :param id_col_name: Optional ID column name for filtering.
        :param id_col_value: Optional ID column value for filtering.
        :return: DataFrame containing the missing dates.
        """
        try:
            id_con = f"{id_col_name} = '{id_col_value}' AND " if id_col_name is not None else ""
            query = (f"WITH date_series AS ( "
                     f"SELECT generate_series('{start_date}'::date, '{end_date}'::date,'1 day'::interval) AS date),"
                     f"filtered_basin_data AS( SELECT {date_col_name} FROM {table_name} WHERE {id_con} "
                     f"{date_col_name} BETWEEN '{start_date}' AND '{end_date}')")
            query += (f"SELECT ds.date as dates FROM date_series ds LEFT JOIN filtered_basin_data fbd "
                      f"ON ds.date = fbd.{date_col_name} WHERE fbd.{date_col_name} IS NULL ORDER BY ds.date")
            df = self.execute_stmt_as_df(query)
            return df
        except:
            return pd.DataFrame()


class GeoDBManager(DBManager):
    @staticmethod
    def get_geometry_cols(table: Table) -> list:
        geom_cols = [col for col in list(table.columns) if 'geometry' in str(col.type)]
        return geom_cols

    def get_geom_col_srid(self, tbl, geom_col):
        try:
            with self.managed_session() as session:
                res = session.query(func.ST_SRID(tbl.c[geom_col.name])).first()
                return res[0] if len(res) > 0 else geom_col.type.srid if geom_col.type.srid != -1 else 0
        except Exception as e:
            srid = geom_col.type.srid if geom_col.type.srid != -1 else 0
            return srid

    @staticmethod
    def data_to_gdf(data, geom_col, srid=0, is_wkb=True):
        # data = list(data)
        # data = [row for row in data]
        if len(data) > 0:
            gdf = gpd.GeoDataFrame(data)
            # gdf = gdf.dropna(axis=0)
            if is_wkb:
                gdf["geom"] = gdf[geom_col].apply(
                    lambda x: wkb.loads(bytes(x.data)) if isinstance(x, WKBElement) else wkb.loads(x, hex=True))
            else:
                gdf["geom"] = gdf[geom_col].apply(lambda x: wkt.loads(str(x)))
            if geom_col != "geom":
                gdf = gdf.drop(geom_col, axis=1)
            gdf = gdf.set_geometry("geom")
            if srid != 0:
                gdf.crs = srid
            return gdf
        else:
            return gpd.GeoDataFrame()

    def table_to_gdf(self, tbl: Union[Table, str], geom_col_name="geom", limit=-1):
        if isinstance(tbl, str):
            tbl = self.get_sqlalchemy_table(tbl)
        geom_cols = self.get_geometry_cols(tbl)
        # data = self.get_all_data(tbl, limit)
        query = Select(tbl)
        data = self.get_query_data(query)
        geom_col = geom_cols[0]
        srid = self.get_geom_col_srid(tbl, geom_col)
        # geom_col_name = geom_col.name
        return self.data_to_gdf(data, geom_col_name, srid)

    def execute_query_as_gdf(self, query, srid, geom_col='geom', is_wkb=True):
        data = self.get_query_data(query)
        if data and len(data) > 0:
            return self.data_to_gdf(data, geom_col, srid, is_wkb)
        return gpd.GeoDataFrame()
        # df = self.execute_stmt_as_df(query)
        # gdf = gpd.GeoDataFrame(df, geometry=geom_col, crs=CRS.from_epsg(srid))
        # return gdf

    def get_spatial_table_names(self, schema=None) -> list:
        inspector = inspect(self.engine)
        # schema = 'public'
        table_names = []
        # table_names = inspector.get_table_names(schema=schema) + inspector.get_view_names(
        #     schema=schema) + inspector.get_materialized_view_names(schema=schema)
        for table_name in inspector.get_table_names(schema=schema):
            try:
                table = self.get_sqlalchemy_table(table_name)
                if table is not None:
                    geom_cols = self.get_geometry_cols(table)
                    if len(geom_cols) > 0:
                        table_names.append(table_name)
            except Exception as e:
                print("error in getting table", table_name)
        return table_names
