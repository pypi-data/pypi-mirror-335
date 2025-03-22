from abc import ABC, abstractmethod
from typing import Any, List, Dict
from python_sdk_remote.our_object import OurObject


class OurVectorDB(ABC):
    def __init__(self, host: str, port: int, username: str, password: str, buffer: Dict[str, List[OurObject]], buffer_size: int):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.buffer_size = buffer_size
        self.buffer = buffer

    @abstractmethod
    def connect(self) -> None:
        # Establish a connection to the database.
        pass

    @abstractmethod
    def insert(self, index_name: str, object: OurObject) -> str:
        # Insert a vector with metadata into the database.
        pass

    @abstractmethod
    def flush_buffer(self, index_name) -> None:
        # Flush the buffer to the database.
        pass

    @abstractmethod
    def delete_index(self, index_name: str, doc_id: str) -> None:
        # Delete a vector entry by ID.
        pass

    @abstractmethod
    def query(self, index_name: str, metadata: List[str]) -> List[Dict[str, Any]]:
        # Perform a vector similarity search and return top-k results.
        pass

    @abstractmethod
    def close_connection(self) -> None:
        # Close the database connection.
        pass

    @abstractmethod
    def update(self, index_name: str, doc_id: str, updated_object: OurObject, metadata: Dict[str, Any]) -> None:
        # Update an existing vector entry.
        pass
