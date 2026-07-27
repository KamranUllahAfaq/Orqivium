from typing import override

from orqivium_vdb_baidu.baidu_vector import BaiduConfig, BaiduVector

from core.rag.datasource.vdb.vector_integration_test_support import AbstractVectorTest, get_example_text


class BaiduVectorTest(AbstractVectorTest):
    def __init__(self):
        super().__init__()
        self.vector = BaiduVector(
            "orqivium",
            BaiduConfig(
                endpoint="http://127.0.0.1:5287",
                account="root",
                api_key="orqivium",
                database="orqivium",
                shard=1,
                replicas=3,
            ),
        )

    @override
    def search_by_vector(self):
        hits_by_vector = self.vector.search_by_vector(query_vector=self.example_embedding)
        assert len(hits_by_vector) == 1

    @override
    def search_by_full_text(self):
        hits_by_full_text = self.vector.search_by_full_text(query=get_example_text())
        assert len(hits_by_full_text) == 0


def test_baidu_vector(setup_mock_redis, setup_baiduvectordb_mock):
    BaiduVectorTest().run_all_tests()
