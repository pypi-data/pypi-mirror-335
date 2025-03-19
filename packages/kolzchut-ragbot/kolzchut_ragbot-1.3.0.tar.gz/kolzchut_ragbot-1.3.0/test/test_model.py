import unittest
from unittest.mock import patch, ANY
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
from ragbot.model import Model, index_from_page_id

search_json = {
   "script_score": {
       "query": {
           "exists": {
               "field": 'content-me5_large-v10'
           }
       },
       "script": {
           "source": f"cosineSimilarity(params.query_vector, 'content-me5_large-v10') + 1.0",
           "params": {
               "Query_vector": [0.0, 0.11, ]
           }
       }
   }
}


class TestModel(unittest.TestCase):

    @patch('elasticsearch.Elasticsearch')
    def test_create_index(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        expected_index_mapping = {
            'properties': {
                'last_update': {'type': 'date'},
                'me5_large-v10_content_vectors': {'type': 'dense_vector', 'dims': 1024},
                'title': {'type': 'text'}, 'doc_id': {'type': 'integer'}, 'content': {'type': 'text'}}
        }
        es_mock.indices.exists.return_value = False
        model.create_index()
        self.assertTrue(es_mock.indices.create.called)
        _, kwargs = es_mock.indices.create.call_args
        self.assertEqual(expected_index_mapping, kwargs.get("mappings"))

    @patch('elasticsearch.Elasticsearch')
    def test_create_index_false(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        es_mock.indices.exists.return_value = True
        model.create_index()
        self.assertTrue(es_mock.indices.create.not_called)

    @patch('elasticsearch.Elasticsearch')
    def test_create_or_update_document_no_delete(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        es_mock.search.return_value = {"hits": {"hits": []}}
        new_doc = {"doc_id": 1, "title": "title", "content": "content"}
        model.create_or_update_documents([new_doc], True)

        es_mock.search.assert_called_with(
            index=index_from_page_id(1),
            body={
                "query": {
                    "term": {
                        "doc_id": {"value": 1}
                    }
                }
            })
        self.assertTrue(es_mock.delete.call_count == 0)
        es_mock.index.called_once()

    @patch('elasticsearch.Elasticsearch')
    def test_create_or_update_document_but_delete(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        es_mock.search.return_value = {"hits": {"hits": [{"_id":"1","doc_id": 1, "title": "title", "content": "content"}]}}
        new_doc = {"doc_id": 1, "title": "edited", "content": "edited"}
        model.create_or_update_documents([new_doc], True)

        es_mock.search.assert_called_with(
            index=index_from_page_id(1),
            body={
                "query": {
                    "term": {
                        "doc_id": {"value": 1}
                    }
                }
            })
        self.assertTrue(es_mock.delete.call_count == 1)
        es_mock.index.called_once()

    @patch('elasticsearch.Elasticsearch')
    def test_create_or_update_document_delete_false(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        es_mock.search.return_value = {
            "hits": {"hits": [{"_id": "1", "doc_id": 1, "title": "title", "content": "content"}]}}
        new_doc = {"doc_id": 1, "title": "edited", "content": "edited"}
        model.create_or_update_documents([new_doc], False)

        self.assertEqual(0, es_mock.search.call_count)
        self.assertEqual(0, es_mock.delete.call_count)
        es_mock.index.called_once()

    @patch('elasticsearch.Elasticsearch')
    def test_search(self, EsMock):
        es_mock = EsMock()
        model = Model(es_mock)
        es_mock.search.return_value = {
            "hits": {
                "hits": [
                    {"_id": "1", "_source": {"field": "value1"}},
                    {"_id": "2", "_source": {"field": "value2"}}
                ]
            }
        }

        embedded_search = {
            "me5_large-v10": [0.1, 0.2, 0.3],
            "model2": [0.4, 0.5, 0.6]
        }

        results = model.search(embedded_search, size=2)

        expected_query = {
            "size": 2,
            "query": {
                "script_score": {
                    "query": {
                        "exists": {
                            "field": "doc_id_me5_large-v10_vectors"
                        }
                    },
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'doc_id_me5_large-v10_vectors') + 1.0",
                        "params": {
                            "query_vector": embedded_search["me5_large-v10"]
                        }
                    }
                }
            }
        }

        expected_results = {
            "doc_id": [
                {"_id": "1", "_source": {"field": "value1"}},
                {"_id": "2", "_source": {"field": "value2"}}
            ]
        }
        self.assertEqual(results["content"], expected_results["doc_id"])


if __name__ == '__main__':
    unittest.main()
