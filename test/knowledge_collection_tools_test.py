import dkg.utils.knowledge_collection_tools as kc_tools


class TestGroupNQuadsBySubject:
    def test_resource_object_quad(self):
        quads = [
            "<http://example.org/book1> <http://schema.org/author> <http://example.org/author1> .",
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]
