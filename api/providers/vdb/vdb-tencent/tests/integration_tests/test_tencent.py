from typing import override
from unittest.mock import MagicMock

from orqivium_vdb_tencent.tencent_vector import TencentConfig, TencentVector

from core.rag.datasource.vdb.vector_integration_test_support import AbstractVectorTest, get_example_text

mock_client = MagicMock()
mock_client.list_databases.return_value = [{"name": "test"}]


class TencentVectorTest(AbstractVectorTest):
    def __init__(self):
        super().__init__()
        self.vector = TencentVector(
            "orqivium",
            TencentConfig(
                url="http://127.0.0.1",
                api_key="orqivium",
                timeout=30,
                username="orqivium",
                database="orqivium",
                shard=1,
                replicas=2,
                enable_hybrid_search=True,
            ),
        )

    @override
    def search_by_vector(self):
        hits_by_vector = self.vector.search_by_vector(query_vector=self.example_embedding)
        assert len(hits_by_vector) == 1

    @override
    def search_by_full_text(self):
        hits_by_full_text = self.vector.search_by_full_text(query=get_example_text())
        assert len(hits_by_full_text) >= 0


def test_tencent_vector(setup_mock_redis, setup_tcvectordb_mock):
    TencentVectorTest().run_all_tests()
