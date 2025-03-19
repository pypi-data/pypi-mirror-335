import unittest
import importlib
from unittest.mock import patch, MagicMock, ANY
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))
import ragbot.engine
importlib.reload(ragbot.engine)
def build_test_engine(es_model, llm_client):
        reranker_model = MagicMock()
        reranker_tokenizer = MagicMock()
        models = MagicMock()
        return ragbot.engine.Engine(llms_client=llm_client, es_client=es_model, models=models,
                                      reranker_model=reranker_model, reranker_tokenizer=reranker_tokenizer)


class TestEngine(unittest.TestCase):

    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_update_title_summary(self, Elasticsearch, Model, LLMClient):
        list_of_docs = [
            {"doc_id": 1, 'title': 'title1', 'summary': 'summary1', 'content': 'content1'},
            {"doc_id": 2, 'title': 'title2', 'summary': 'summary2', 'content': 'content2'}
        ]

        es_client = Elasticsearch()
        es_model = Model(es_client)
        llm_client = LLMClient()
        engine = build_test_engine(es_model, llm_client)
        engine.update_docs(list_of_docs=list_of_docs, embed_only_fields=['title', 'summary'], delete_existing=False)
        es_model.create_or_update_documents.assert_called_once_with(list_of_docs, False)

    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_update_content_without_delete(self, Elasticsearch, Model, LLMClient):
        list_of_docs = [
            {"doc_id": 1, 'title': 'title1', 'summary': 'summary1', 'content': 'content1'},
            {"doc_id": 2, 'title': 'title2', 'summary': 'summary2', 'content': 'content2'}
        ]
        es_client = Elasticsearch()
        es_model = Model(es_client)
        llm_client = LLMClient()
        engine = build_test_engine(es_model, llm_client)
        engine.update_docs(list_of_docs, embed_only_fields=['content'], delete_existing=False)
        es_model.create_or_update_documents.assert_called_once_with(list_of_docs, False)

    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_update_content_with_delete(self, Elasticsearch, Model, LLMClient):
        list_of_docs = [
            {"doc_id": 1, 'title': 'title1', 'summary': 'summary1', 'content': 'content1'},
            {"doc_id": 2, 'title': 'title2', 'summary': 'summary2', 'content': 'content2'}
        ]
        reranker_model = MagicMock()
        reranker_tokenizer = MagicMock()
        llm_client = LLMClient()
        models = MagicMock()
        es_client = Elasticsearch()
        es_model = Model(es_client)
        engine = ragbot.engine.Engine(llms_client=llm_client, es_client=es_model, models=models,
                                      reranker_model=reranker_model, reranker_tokenizer=reranker_tokenizer)
        engine.update_docs(list_of_docs, embed_only_fields=['content'], delete_existing=True)
        es_model.create_or_update_documents.assert_called_once_with(list_of_docs, True)

    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_reciprocal_rank_fusion(self, Elasticsearch, Model, LLMClient):
        es_client = Elasticsearch()
        es_model = Model(es_client)
        llm_client = LLMClient()
        engine = build_test_engine(es_model, llm_client)

        ranking_lists = [
            [1, 2, 3],
            [2, 3, 4],
            [3, 4, 5]
        ]
        expected_fused_list = [3,2,4,1,5]
        fused_list = engine.reciprocal_rank_fusion(ranking_lists)
        self.assertEqual(fused_list, expected_fused_list)

    @patch.object(ragbot.engine.Engine, 'reciprocal_rank_fusion')
    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_search_documents(self, Elasticsearch, Model, LLMClient, mock_reciprocal_rank_fusion):
        llm_client = LLMClient()
        models = MagicMock()
        es_client = Elasticsearch()
        es_model = Model(es_client)
        es_model.search.return_value = {
                "title":[
                    {'_source': {'page_id': 1, 'title': 'title1'}},
                    {'_source': {'page_id': 2, 'title': 'title2'}},
                    {'_source': {'page_id': 3, 'title': 'title3'}},
                ],
                "summary":[
                    {'_source': {'page_id': 2, 'title': 'title2'}},
                    {'_source': {'page_id': 3, 'title': 'title3'}},
                    {'_source': {'page_id': 4, 'title': 'title4'}},
                ],
                "content":[
                    {'_source': {'page_id': 3, 'title': 'title3'}},
                    {'_source': {'page_id': 4, 'title': 'title4'}},
                    {'_source': {'page_id': 5, 'title': 'title5'}}
                ]
        }
        mock_reciprocal_rank_fusion.return_value = [3, 2, 4, 1, 5]
        engine = build_test_engine(es_model, llm_client)

        result = engine.search_documents("test query", 5)

        es_model.search.assert_called_once()
        self.assertEqual(mock_reciprocal_rank_fusion.return_value, [3, 2, 4, 1, 5])
        self.assertEqual([
            {'page_id': 3, 'title': 'title3'},
            {'page_id': 2, 'title': 'title2'},
            {'page_id': 4, 'title': 'title4'},
            {'page_id': 1, 'title': 'title1'},
            {'page_id': 5, 'title': 'title5'}
        ], result)

    @patch('ragbot.llm_client.LLMClient')
    @patch('ragbot.model.Model')
    @patch('elasticsearch.Elasticsearch')
    def test_answer_query(self, Elasticsearch, Model, LLMClient):
        es_client = Elasticsearch()
        es_model = Model(es_client)
        llm_client = LLMClient()
        engine = build_test_engine(es_model, llm_client)

        with patch.object(ragbot.engine.Engine, 'search_documents') as mock_search_documents:
            mock_search_documents.return_value = [
                {'page_id': 3, 'title': 'title3'},
                {'page_id': 2, 'title': 'title2'},
                {'page_id': 4, 'title': 'title4'},
                {'page_id': 1, 'title': 'title1'},
                {'page_id': 5, 'title': 'title5'}
            ]

            llm_client.answer.return_value = ('answer', 0.5, 100)
            actual_top_k_documents, actual_gpt_answer, actual_stats = engine.answer_query("test query", 5, 'gpt-4o')

            expected_top_k_documents = [
                {'page_id': 3, 'title': 'title3'},
                {'page_id': 2, 'title': 'title2'},
                {'page_id': 4, 'title': 'title4'},
                {'page_id': 1, 'title': 'title1'},
                {'page_id': 5, 'title': 'title5'}
            ]
            expected_gpt_answer = llm_client.answer.return_value[0]
            expected_stats = {
                "retrieval_time": 0,
                "gpt_model": 'gpt-4o',
                "gpt_time": llm_client.answer.return_value[1],
                "tokens": llm_client.answer.return_value[2]
            }

            self.assertEqual(expected_top_k_documents, actual_top_k_documents)
            self.assertEqual(expected_gpt_answer, actual_gpt_answer)
            self.assertEqual(expected_stats, actual_stats)


if __name__ == '__main__':
    unittest.main()

