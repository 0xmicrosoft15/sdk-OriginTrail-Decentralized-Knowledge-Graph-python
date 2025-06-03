import dkg.utils.knowledge_collection_tools as kc_tools
import uuid


class TestGroupNQuadsBySubject:
    def test_resource_object_quad(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "author": {
        #     "@id": "http://example.org/author1"
        #   }
        # }
        quads = [
            "<http://example.org/book1> <http://schema.org/author> <http://example.org/author1> .",
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        print(grouped[0][0])
        print(quads[0])
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]

    def test_literal_object_quad(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "type": "Book",
        #   "title": "The Great Book"
        # }
        quads = [
            '<http://example.org/book1> <http://schema.org/title> "The Great Book" .',
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]

    def test_literal_object_quad_with_an_emoticon(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "type": "Book",
        #   "title": "The Great Book"
        # }
        quads = [
            '<http://example.org/book1> <http://schema.org/title> "The Great Book 😀" .',
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]

    def test_literal_with_escape_character(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "type": "Book",
        #   "title": "The Great Book \n"
        # }
        quads = [
            '<http://example.org/book1> <http://schema.org/title> "The Great Book \\n" .',
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]

    def test_literal_with_language_tags(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "type": "Book",
        #   "description": [
        #     {
        #       "@value": "A thrilling adventure novel.",
        #       "@language": "en"
        #     },
        #     {
        #       "@value": "Napeta pustolovska novela.",
        #       "@language": "sl"
        #     }
        #   ]
        # }
        quads = [
            '<http://example.org/book1> <http://schema.org/description> "A thrilling adventure novel."@en .',
            '<http://example.org/book1> <http://schema.org/description> "Napeta pustolovska novela."@sl .',
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
        assert quads[1] in grouped[0]
        assert quads[2] in grouped[0]

    def test_literal_with_language_and_escape_character(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": "http://schema.org",
        #   "@id": "http://example.org/book1",
        #   "type": "Book",
        #   "description": [
        #     {
        #       "@value": "A thrilling adventure novel. \n",
        #       "@language": "en"
        #     },
        #     {
        #       "@value": "Napeta pustolovska novela. \n",
        #       "@language": "sl"
        #     }
        #   ]
        # }
        quads = [
            '<http://example.org/book1> <http://schema.org/description> "A thrilling adventure novel. \n"@en .',
            '<http://example.org/book1> <http://schema.org/description> "Napeta pustolovska novela. \n"@sl .',
            "<http://example.org/book1> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Book> .",
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in [nquad.encode("unicode_escape") for nquad in grouped[0]]
        assert quads[1] in grouped[0]
        assert quads[2] in grouped[0]

    def test_literal_with_language_and_blank_node_subject(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": {
        #     "predicate": "http://example.org/predicate"
        #   },
        #   "@graph": [
        #     {
        #       "predicate": {
        #         "@value": "something",
        #         "@language": "en"
        #       }
        #     }
        #   ]
        # }

        subject = f"<uuid:{uuid.uuid4()}>"
        quads = [
            f'{subject} <http://example.org/predicate> "something"@en .',
        ]
        grouped = kc_tools.group_nquads_by_subject(quads)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
