"""
Xsql - A fast, secure, and simple database library for Python
Project: Xsql
Creator: Mohammad Taha Gorji
"""

import os
import sqlite3
import threading
from queue import Queue, Empty
import logging
from abc import ABC, abstractmethod
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("xsql")

class XsqlError(Exception):
    def __init__(self, message):
        super().__init__(message)

class BaseDriver(ABC):
    @abstractmethod
    def connect(self):
        raise NotImplementedError("connect method must be implemented.")

    @abstractmethod
    def execute(self, connection, query, params):
        raise NotImplementedError("execute method must be implemented.")

    @abstractmethod
    def commit(self, connection):
        raise NotImplementedError("commit method must be implemented.")

    @abstractmethod
    def rollback(self, connection):
        raise NotImplementedError("rollback method must be implemented.")

    @abstractmethod
    def close(self, connection):
        raise NotImplementedError("close method must be implemented.")

class XsqlDriver(BaseDriver):
    def __init__(self, db_path, **options):
        self.db_path = db_path
        self.options = options

    def connect(self):
        try:
            conn = sqlite3.connect(self.db_path, check_same_thread=False, **self.options)
            conn.execute("PRAGMA foreign_keys = ON")
            logger.debug("Xsql connection established.")
            return conn
        except sqlite3.Error as error:
            raise XsqlError(f"Error connecting to Xsql: {error}")

    def execute(self, connection, query, params):
        try:
            if params is None:
                params = ()
            return connection.execute(query, params)
        except sqlite3.Error as error:
            raise XsqlError(f"Error executing query on Xsql: {error}")

    def commit(self, connection):
        try:
            connection.commit()
        except sqlite3.Error as error:
            raise XsqlError(f"Error during commit on Xsql: {error}")

    def rollback(self, connection):
        try:
            connection.rollback()
        except sqlite3.Error as error:
            raise XsqlError(f"Error during rollback on Xsql: {error}")

    def close(self, connection):
        try:
            connection.close()
        except sqlite3.Error as error:
            raise XsqlError(f"Error closing Xsql connection: {error}")

class ConnWrapper:
    def __init__(self, conn, driver: BaseDriver):
        self.conn = conn
        self.driver = driver
        self.lock = threading.Lock()

    def exec_query(self, query, params=None):
        with self.lock:
            return self.driver.execute(self.conn, query, params)

    def do_commit(self):
        with self.lock:
            self.driver.commit(self.conn)

    def do_rollback(self):
        with self.lock:
            self.driver.rollback(self.conn)

    def do_close(self):
        with self.lock:
            self.driver.close(self.conn)

class ConnPool:
    def __init__(self, driver: BaseDriver, pool_size=5, timeout=30):
        self.driver = driver
        self.pool_size = pool_size
        self.timeout = timeout
        self.pool = Queue(maxsize=pool_size)
        self._init_pool()

    def _init_pool(self):
        for _ in range(self.pool_size):
            conn = self.driver.connect()
            wrapper = ConnWrapper(conn, self.driver)
            self.pool.put(wrapper)
        logger.info("Connection pool initialized with %s connections.", self.pool_size)

    def acquire(self):
        try:
            conn = self.pool.get(timeout=self.timeout)
            logger.debug("Acquired a connection from pool.")
            return conn
        except Empty:
            raise XsqlError("No available connection.")

    def release(self, conn: ConnWrapper):
        self.pool.put(conn)
        logger.debug("Connection returned to pool.")

    def close_all(self):
        while not self.pool.empty():
            conn = self.pool.get()
            conn.do_close()
        logger.info("All connections have been closed.")

class DBTransaction:
    def __init__(self, db, conn: ConnWrapper):
        self.db = db
        self.conn = conn
        self.active = True

    def __enter__(self):
        return self

    def exec_query(self, query, params=None):
        if not self.active:
            raise XsqlError("Transaction is inactive.")
        return self.conn.exec_query(query, params)

    def commit(self):
        if not self.active:
            raise XsqlError("Transaction is inactive.")
        self.conn.do_commit()
        self.active = False

    def rollback(self):
        if not self.active:
            raise XsqlError("Transaction is inactive.")
        self.conn.do_rollback()
        self.active = False

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            self.rollback()
        else:
            try:
                self.commit()
            except Exception as error:
                self.rollback()
                raise error
        self.db._return_conn(self.conn)
        return False

class Encryptor:
    def __init__(self, key: bytes, use_gpu: bool = False):
        if len(key) not in (16, 24, 32):
            raise XsqlError("Key must be 16, 24, or 32 bytes long.")
        self.key = key
        self.aesgcm = AESGCM(self.key)
        self.use_gpu = use_gpu
        self.gpu = None
        if self.use_gpu:
            try:
                import cupy as cp
                self.gpu = cp
                logger.info("GPU acceleration enabled for encryption.")
            except ImportError:
                self.gpu = None
                self.use_gpu = False
                logger.info("cupy not found; continuing with CPU.")

    def encrypt(self, data: bytes) -> bytes:
        nonce = os.urandom(12)
        if self.use_gpu and self.gpu:
            gpu_data = self.gpu.asarray(bytearray(data))
            data = bytes(gpu_data.get())
        cipher_text = self.aesgcm.encrypt(nonce, data, None)
        return nonce + cipher_text

    def decrypt(self, token: bytes) -> bytes:
        nonce = token[:12]
        cipher_text = token[12:]
        data = self.aesgcm.decrypt(nonce, cipher_text, None)
        if self.use_gpu and self.gpu:
            gpu_data = self.gpu.asarray(bytearray(data))
            data = bytes(gpu_data.get())
        return data

class Database:
    def __init__(self, driver: BaseDriver, pool_size=5, encryption: Encryptor = None):
        self.pool = ConnPool(driver, pool_size=pool_size)
        self.local = threading.local()
        self.encryptor = encryption

    def _get_conn(self) -> ConnWrapper:
        if hasattr(self.local, "conn"):
            return self.local.conn
        else:
            conn = self.pool.acquire()
            self.local.conn = conn
            return conn

    def _return_conn(self, conn: ConnWrapper):
        if hasattr(self.local, "conn"):
            del self.local.conn
        self.pool.release(conn)

    def execute(self, query, params=None):
        conn = self._get_conn()
        try:
            cursor = conn.exec_query(query, params)
            conn.do_commit()
            return cursor
        except Exception as error:
            conn.do_rollback()
            raise XsqlError(f"Error executing query: {error}")
        finally:
            self._return_conn(conn)

    def query(self, query, params=None):
        cursor = self.execute(query, params)
        return cursor.fetchall()

    def transaction(self):
        conn = self.pool.acquire()
        return DBTransaction(self, conn)

    def secure_insert(self, table: str, data: dict):
        cols = []
        placeholders = []
        values = []
        for col, val in data.items():
            cols.append(col)
            placeholders.append("?")
            if self.encryptor and isinstance(val, (str, bytes)):
                if isinstance(val, str):
                    val = val.encode('utf-8')
                enc_val = self.encryptor.encrypt(val)
                values.append(enc_val)
            else:
                values.append(val)
        query_str = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join(placeholders)})"
        self.execute(query_str, tuple(values))

    def secure_select(self, table: str, cols: list, encrypted_cols: list = None, where: str = "", where_params: tuple = ()):
        encrypted_cols = encrypted_cols or []
        col_str = ", ".join(cols)
        query_str = f"SELECT {col_str} FROM {table}"
        if where:
            query_str += f" WHERE {where}"
        cursor = self.execute(query_str, where_params)
        rows = cursor.fetchall()
        results = []
        for row in rows:
            row_dict = {}
            for idx, col in enumerate(cols):
                val = row[idx]
                if col in encrypted_cols and val is not None and self.encryptor:
                    try:
                        dec_val = self.encryptor.decrypt(val)
                        try:
                            dec_val = dec_val.decode('utf-8')
                        except UnicodeDecodeError:
                            pass
                        row_dict[col] = dec_val
                    except Exception as err:
                        raise XsqlError(f"Error decrypting column {col}: {err}")
                else:
                    row_dict[col] = val
            results.append(row_dict)
        return results

    def secure_update(self, table: str, data: dict, where: str, where_params: tuple):
        set_clause = []
        values = []
        for col, val in data.items():
            set_clause.append(f"{col} = ?")
            if self.encryptor and isinstance(val, (str, bytes)):
                if isinstance(val, str):
                    val = val.encode('utf-8')
                enc_val = self.encryptor.encrypt(val)
                values.append(enc_val)
            else:
                values.append(val)
        query_str = f"UPDATE {table} SET {', '.join(set_clause)} WHERE {where}"
        self.execute(query_str, tuple(values) + where_params)

    def close(self):
        self.pool.close_all()