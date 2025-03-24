import sqlite3
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

class CodeDB:
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def connect(self):
        """مدير الاتصال بالقاعدة باستخدام context manager"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except sqlite3.DatabaseError as e:
            conn.rollback()
            raise RuntimeError(f"Database error occurred: {e}")
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def execute(self, query: str, params: Optional[tuple] = ()) -> None:
        """تنفيذ استعلام بدون إرجاع بيانات"""
        with self.connect() as cursor:
            cursor.execute(query, params)

    def fetch(self, query: str, params: Optional[tuple] = ()) -> List[Dict[str, Any]]:
        """جلب بيانات"""
        with self.connect() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def create(self, table_name: str, **columns: str) -> None:
        """إنشاء جدول مع أعمدته مباشرة"""
        columns_str = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_str})"
        self.execute(query)

    def insert(self, table_name: str, **data: Any) -> None:
        """إدخال بيانات مباشرة"""
        columns = ', '.join(data.keys())
        values = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        self.execute(query, tuple(data.values()))

    def insert_bulk(self, table_name: str, data: List[Dict[str, Any]]) -> None:
        """إدخال بيانات متعددة دفعة واحدة"""
        if not data:
            return
        columns = ', '.join(data[0].keys())
        values = ', '.join(['?' for _ in data[0]])
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
        with self.connect() as cursor:
            cursor.executemany(query, [tuple(item.values()) for item in data])
    
    def update(self, table_name: str, where: str = None, **data: Any) -> None:
        """تحديث البيانات مباشرة"""
        set_clause = ', '.join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause}"
        if where:
            query += f" WHERE {where}"
        self.execute(query, tuple(data.values()))

    def delete(self, table_name: str, where: str = None) -> None:
        """حذف البيانات"""
        query = f"DELETE FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        self.execute(query)

    def select(self, table_name: str, where: Optional[str] = None, columns: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """استعلام بسيط لانتقاء بيانات"""
        columns_str = ', '.join(columns) if columns else '*'
        query = f"SELECT {columns_str} FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        return self.fetch(query)

    def count(self, table_name: str, where: Optional[str] = None) -> int:
        """حساب عدد السجلات"""
        query = f"SELECT COUNT(*) FROM {table_name}"
        if where:
            query += f" WHERE {where}"
        result = self.fetch(query)
        return result[0]['COUNT(*)'] if result else 0

    def exists(self, table_name: str, where: str) -> bool:
        """التحقق إذا كانت السجلات موجودة حسب شرط"""
        query = f"SELECT 1 FROM {table_name} WHERE {where} LIMIT 1"
        result = self.fetch(query)
        return bool(result)

    def drop_table(self, table_name: str) -> None:
        """حذف جدول كامل"""
        self.execute(f"DROP TABLE IF EXISTS {table_name}")

    def truncate(self, table_name: str) -> None:
        """مسح جميع البيانات من الجدول"""
        self.execute(f"DELETE FROM {table_name}")

    def schema(self, table_name: str) -> List[str]:
        """جلب الأعمدة في الجدول"""
        return [col[1] for col in self.fetch(f"PRAGMA table_info({table_name})")]

    def backup(self, backup_db_path: str) -> None:
        """نسخ احتياطي للقاعدة إلى ملف آخر"""
        with self.connect() as cursor:
            backup_conn = sqlite3.connect(backup_db_path)
            conn = sqlite3.connect(self.db_path)
            conn.backup(backup_conn)
            backup_conn.close()

    def restore(self, backup_db_path: str) -> None:
        """استعادة قاعدة البيانات من النسخة الاحتياطية"""
        with self.connect() as cursor:
            restore_conn = sqlite3.connect(backup_db_path)
            conn = sqlite3.connect(self.db_path)
            restore_conn.backup(conn)
            restore_conn.close()
            
    def create_index(self, table_name: str, index_name: str, columns: List[str]) -> None:
        """إنشاء فهرس لتحسين الأداء"""
        columns_str = ', '.join(columns)
        query = f"CREATE INDEX IF NOT EXISTS {index_name} ON {table_name} ({columns_str})"
        self.execute(query)
        
codb = CodeDB