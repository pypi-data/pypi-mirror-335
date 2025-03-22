from typing import List, Dict, Any, Optional
import sqlite3
import pymongo
import redis
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import datetime

# SQLAlchemy Base
Base = declarative_base()

# Example SQLAlchemy Models
class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    posts = relationship('Post', back_populates='author')

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    content = Column(String(1000))
    author_id = Column(Integer, ForeignKey('users.id'))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    author = relationship('User', back_populates='posts')

class SQLiteDatabase:
    """SQLite database operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path

    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute SQL query and return results."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.description is None:
                conn.commit()
                return []
            
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def create_table(self, table_name: str, columns: Dict[str, str]):
        """Create a new table."""
        cols = [f"{name} {dtype}" for name, dtype in columns.items()]
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(cols)})"
        self.execute_query(query)

class SQLAlchemyDatabase:
    """SQLAlchemy ORM database operations."""
    
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)
        self.Session = sessionmaker(bind=self.engine)

    def create_tables(self):
        """Create all tables defined in models."""
        Base.metadata.create_all(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def add_user(self, username: str, email: str) -> User:
        """Add a new user."""
        with self.session_scope() as session:
            user = User(username=username, email=email)
            session.add(user)
            session.commit()
            return user

    def get_user_posts(self, user_id: int) -> List[Dict]:
        """Get all posts for a user."""
        with self.session_scope() as session:
            user = session.query(User).get(user_id)
            if user:
                return [{"id": post.id, "title": post.title, "content": post.content}
                       for post in user.posts]
            return []

class MongoDBClient:
    """MongoDB database operations."""
    
    def __init__(self, connection_string: str, database: str):
        self.client = pymongo.MongoClient(connection_string)
        self.db = self.client[database]

    def insert_one(self, collection: str, document: Dict) -> str:
        """Insert a single document."""
        result = self.db[collection].insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection: str, documents: List[Dict]) -> List[str]:
        """Insert multiple documents."""
        result = self.db[collection].insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def find_one(self, collection: str, query: Dict) -> Optional[Dict]:
        """Find a single document."""
        return self.db[collection].find_one(query)

    def find_many(self, collection: str, query: Dict) -> List[Dict]:
        """Find multiple documents."""
        return list(self.db[collection].find(query))

    def update_one(self, collection: str, query: Dict, update: Dict) -> int:
        """Update a single document."""
        result = self.db[collection].update_one(query, {'$set': update})
        return result.modified_count

    def delete_one(self, collection: str, query: Dict) -> int:
        """Delete a single document."""
        result = self.db[collection].delete_one(query)
        return result.deleted_count

class RedisClient:
    """Redis database operations."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, db: int = 0):
        self.client = redis.Redis(host=host, port=port, db=db)

    def set_value(self, key: str, value: str, expiry: Optional[int] = None):
        """Set a key-value pair with optional expiry."""
        self.client.set(key, value, ex=expiry)

    def get_value(self, key: str) -> Optional[str]:
        """Get value for a key."""
        value = self.client.get(key)
        return value.decode() if value else None

    def delete_key(self, key: str) -> bool:
        """Delete a key."""
        return bool(self.client.delete(key))

    def increment(self, key: str) -> int:
        """Increment a counter."""
        return self.client.incr(key)

    def add_to_set(self, key: str, *values: str):
        """Add values to a set."""
        self.client.sadd(key, *values)

    def get_set_members(self, key: str) -> List[str]:
        """Get all members of a set."""
        return [member.decode() for member in self.client.smembers(key)]

    def push_to_list(self, key: str, *values: str):
        """Push values to a list."""
        self.client.rpush(key, *values)

    def get_list_range(self, key: str, start: int = 0, end: int = -1) -> List[str]:
        """Get range of values from a list."""
        return [item.decode() for item in self.client.lrange(key, start, end)]

    def set_hash(self, key: str, mapping: Dict[str, str]):
        """Set multiple hash fields."""
        self.client.hmset(key, mapping)

    def get_hash(self, key: str) -> Dict[str, str]:
        """Get all fields in a hash."""
        result = self.client.hgetall(key)
        return {k.decode(): v.decode() for k, v in result.items()}
