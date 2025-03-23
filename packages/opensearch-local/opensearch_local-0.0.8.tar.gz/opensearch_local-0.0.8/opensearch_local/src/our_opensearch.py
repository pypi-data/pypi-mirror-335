import json
from typing import Dict, List
from opensearchpy import OpenSearch

from python_sdk_remote import utilities
from python_sdk_remote.our_object import OurObject
from .our_vector_db import OurVectorDb
from .utils import generate_index_body


class OurOpenSearch(OurVectorDb):
    def __init__(self, buffer_size=300):
        self.client = None
        self.host = utilities.our_get_env(key="OPENSEARCH_HOST")
        # OPENSEARCH_PORT Should come from outside, if not exists user OPENSEARCH_PORT_DEFAULT=9200 const
        self.port = 9200
        # hosts = [{"host": host, "port": 9200}]
        # TODO Should not be hard-coded should come from OPENSEARCH_ADMIN_USER environment variable with default of OPENSEARCH_ADMIN_USER_DEFAULT
        self.username = "admin"
        self.password = utilities.our_get_env(key="OPENSEARCH_INITIAL_ADMIN_PASSWORD")

        self.buffer: Dict[str, List[OurObject]] = {}

        # ! the buffer size is the number of objects that will be inserted into the buffer before flushing
        # need to consider changing this to the number of !bytes! that will be inserted into the buffer before flushing
        self.buffer_size = buffer_size

        OurVectorDb.__init__(self, self.host, self.port, self.username, self.password, self.buffer, self.buffer_size)

        self.connect()

    def connect(self):
        try:
            hosts = [{"host": self.host, "port": self.port}]
            self.client = OpenSearch(
                hosts=hosts,
                http_auth=(self.username, self.password),
                use_ssl=True,
                verify_certs=False,
                timeout=30
            )
        except Exception as e:
            print(f"Error connecting to OpenSearch: {e}")

    def insert(self, index_name, object):
        flushed = False
        if index_name not in self.buffer:
            self.buffer[index_name] = []
        self.create_index_if_not_exists(index_name)

        formatted_object = json.loads(object.to_json())
        self.buffer[index_name].append(formatted_object)

        if len(self.buffer[index_name]) >= self.buffer_size:
            response = self.flush_buffer(index_name=index_name)
            flushed = True
            return response, flushed
        # return a responnse that the data is inserted into the buffer and not yet flushed
        return {"status": "buffered",
                "index": index_name,
                "buffer_size": len(self.buffer[index_name]),
                "buffer_limit": self.buffer_size,
                }, flushed

    def flush_buffer(self, index_name):
        response = None
        action = {
                "index": {
                    "_index": index_name
                    }
                }

        bulk_json = self.payload_constructor(self.buffer[index_name], action)

        try:
            response = self.client.bulk(
                body=bulk_json,
                index=index_name,
            )
        except Exception as e:
            print(f"Error flushing buffer: {e}")

        self.buffer[index_name] = []

        return response

    def payload_constructor(self, data, action):
        payload_lines = []
        for datum in data:
            payload_lines.append(json.dumps(action))
            payload_lines.append(json.dumps(datum))

        return "\n".join(payload_lines)

    def create_index_if_not_exists(self, index_name):
        if not self.client.indices.exists(index=index_name):
            try:
                index_body = generate_index_body(object_type=index_name)
                self.client.indices.create(index=index_name, body=index_body)
            except Exception as e:
                print(f"Error creating index: {e}")

    def close_connection(self):
        if self.client:
            self.client.close()
            print("Connection to OpenSearch closed.")

    def delete_index(self, index_name):
        return self.client.delete(index=index_name)

    def delete_test_data(self, index_name):
        return self.client.delete_by_query(index=index_name, body={"query": {"term": {"is_test_data": True}}})

    def delete_by_term(self, index_name, term, value):
        return self.client.delete_by_query(index=index_name, body={"query": {"term": {term: value}}})

    def search(self, **kwargs):
        return self.client.search(**kwargs)

    def query(self, index_name, metadata):
        pass
        # return super().query(index_name, metadata)

    def update(self, index, id, body, params=None, headers=None):
        pass
        # return super().update(index, id, body, params, headers)


# the old way of the ingest_bulk method before adding our_vector_db.py
    # def create_ingest_bulk(self, object: list[our_object.OurObject]):
    #     for obj in object:
    #         if not isinstance(obj, our_object.OurObject):
    #             raise ValueError("Input must be an instance of OurObject")

    #     data = []

    #     for obj in object:
    #         data.append(json.loads(obj.to_json()))

    #     index_name = object[0].__class__.__name__.lower()

    #     try:
    #         self.create_index_if_not_exists(index_name)
    #     except Exception as e:
    #         print(f"Error creating index: {e}")

    #     action = {
    #             "index": {
    #                 "_index": index_name
    #                 }
    #             }

    #     bulk_json = self.payload_constructor(data, action)

    #     response = self.client.bulk(
    #         body=bulk_json,
    #         index=index_name,
    #     )

    #     # if len(bulk_json) < 500:
    #     #     response = opensearchpy.helpers.bulk(
    #     #         client=self.client,
    #     #         actions=bulk_json,
    #     #         index=index_name
    #     #     )
    #     # else:
    #     #     response = opensearchpy.helpers.bulk(
    #     #         client=self.client,
    #     #         actions=bulk_json,
    #     #         index=index_name,
    #     #         chunk_size=500
    #     #     )

    #     return response, len(bulk_json.split('\n')), len(data)
