import dkg.utils.knowledge_collection_tools as kc_tools
from rdflib import Dataset, URIRef, Literal
import uuid
import re
import pytest


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
        grouped = kc_tools.group_nquads_by_subject(quads, sort=True)
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
        grouped = kc_tools.group_nquads_by_subject(quads, sort=True)
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
        grouped = kc_tools.group_nquads_by_subject(quads, sort=True)
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
        grouped = kc_tools.group_nquads_by_subject(quads, sort=True)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]
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
        grouped = kc_tools.group_nquads_by_subject(quads, sort=True)
        assert len(grouped) == 1
        assert quads[0] in grouped[0]


class TestGenerateMissingIdsForBlankNodes:
    def test_blank_node_replacement(self):
        # JSON-LD equivalent of the quads being tested:
        #
        # {
        #   "@context": {
        #     "relatedTo": "http://example.org/relatedTo"
        #   },
        #   "@id": "http://example.org/document/1",
        #   "relatedTo": {}
        # }

        nquads_array = [
            "<http://example.org/document/1> <http://example.org/relatedTo> _:c14n0 .",
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(nquad for nquad in updated_quads if nquad.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 1

        o = None

        for s, p, o_val, _ in d.quads(
            (
                URIRef("http://example.org/document/1"),
                URIRef("http://example.org/relatedTo"),
                None,
            )
        ):
            o = o_val

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(o, URIRef)
        assert uuid_regex.match(str(o))

    def test_shared_blank_node_replacement(self):
        # Equivalent JSON-LD structure:
        #
        # {
        #   "@context": { "is": "http://example.org/is" },
        #   "@graph": [
        #     {
        #       "@id": "http://example.org/subject1",
        #       "is": { "@id": "_:sharedBlank" }
        #     },
        #     {
        #       "@id": "http://example.org/subject2",
        #       "is": { "@id": "_:sharedBlank" }
        #     }
        #   ]
        # }

        nquads_array = [
            "<http://example.org/subject1> <http://example.org/is> _:c14n0 .",
            "<http://example.org/subject2> <http://example.org/is> _:c14n0 .",
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(nquad for nquad in updated_quads if nquad.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 2

        o1 = None
        o2 = None

        for s, p, o, _ in d.quads(
            (
                URIRef("http://example.org/subject1"),
                URIRef("http://example.org/is"),
                None,
            )
        ):
            o1 = o
        for s, p, o, _ in d.quads(
            (
                URIRef("http://example.org/subject2"),
                URIRef("http://example.org/is"),
                None,
            )
        ):
            o2 = o

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(o1, URIRef)
        assert isinstance(o2, URIRef)

        assert uuid_regex.match(str(o1))
        assert uuid_regex.match(str(o2))

        assert str(o1) == str(o2)

    def test_subject_blank_node_replacement(self):
        # Equivalent JSON-LD structure:
        #
        # {
        #   "@context": { "ex": "http://example.org/" },
        #   "@graph": [
        #     {
        #       "ex:name": "John Doe"
        #     }
        #   ]
        # }

        nquads_array = [
            '_:c14n0 <http://example.org/name> "John Doe" .',
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(nquad for nquad in updated_quads if nquad.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 1

        s = None

        for subj, pred, obj_val, _ in d.quads(
            (None, URIRef("http://example.org/name"), Literal("John Doe"))
        ):
            s = subj

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(s, URIRef)
        assert uuid_regex.match(str(s))

    def test_occuring_subject_blank_node_replacement(self):
        # Equivalent JSON-LD:
        #
        # {
        #   "@context": { "ex": "http://example.org/" },
        #   "@graph": [
        #     {
        #       "ex:name": "John Doe",
        #       "ex:sex": "male"
        #     }
        #   ]
        # }

        nquads_array = [
            '_:c14n0 <http://example.org/name> "John Doe" .',
            '_:c14n0 <http://example.org/sex> "male" .',
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(q for q in updated_quads if q.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 2

        s1 = None
        s2 = None

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/name"), Literal("John Doe"))
        ):
            s1 = s

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/sex"), Literal("male"))
        ):
            s2 = s

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(s1, URIRef)
        assert isinstance(s2, URIRef)
        assert uuid_regex.match(str(s1))
        assert uuid_regex.match(str(s2))
        assert s1 == s2

    def test_different_blank_subjects_have_different_uuids(self):
        # Equivalent JSON-LD:
        #
        # {
        #   "@context": { "ex": "http://example.org/" },
        #   "@graph": [
        #     {
        #       "ex:hasName": "Alice",
        #       "ex:sex": "male"
        #     },
        #     {
        #       "ex:hasName": "Bob",
        #       "ex:sex": "female"
        #     }
        #   ]
        # }

        nquads_array = [
            '_:c14n0 <http://example.org/sex> "male" .',
            '_:c14n0 <http://example.org/hasName> "Bob" .',
            '_:c14n1 <http://example.org/sex> "female" .',
            '_:c14n1 <http://example.org/hasName> "Alice" .',
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(q for q in updated_quads if q.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 4

        s1 = None
        s2 = None
        s3 = None
        s4 = None

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/hasName"), Literal("Bob"))
        ):
            s1 = s

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/sex"), Literal("male"))
        ):
            s2 = s

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/hasName"), Literal("Alice"))
        ):
            s3 = s

        for s, p, o, _ in d.quads(
            (None, URIRef("http://example.org/sex"), Literal("female"))
        ):
            s4 = s

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(s1, URIRef)
        assert isinstance(s2, URIRef)
        assert uuid_regex.match(str(s1))
        assert uuid_regex.match(str(s2))
        assert s1 == s2

        assert isinstance(s3, URIRef)
        assert isinstance(s4, URIRef)
        assert uuid_regex.match(str(s3))
        assert uuid_regex.match(str(s4))
        assert s3 == s4

        assert s1 != s3

    def test_blank_node_used_as_object_and_subject_has_same_uuid(self):
        # Equivalent JSON-LD:
        #
        # {
        #   "@context": "http://schema.org",
        #   "review": {
        #     "reviewBody": "Excellent book!"
        #   }
        # }

        nquads_array = [
            '_:c14n0 <http://schema.org/reviewBody> "Excellent book!" .',
            "_:c14n1 <http://schema.org/review> _:c14n0 .",
        ]

        updated_quads = kc_tools.generate_missing_ids_for_blank_nodes(nquads_array)
        all_nquads = "\n".join(q for q in updated_quads if q.strip())

        d = Dataset()
        d.parse(data=all_nquads, format="nquads")

        quad_count = sum(1 for _ in d.quads())
        assert quad_count == 2

        s1 = None
        s2 = None
        o2 = None

        for s, p, o, _ in d.quads(
            (None, URIRef("http://schema.org/reviewBody"), Literal("Excellent book!"))
        ):
            s1 = s

        for s, p, o, _ in d.quads((None, URIRef("http://schema.org/review"), None)):
            s2 = s
            o2 = o

        uuid_regex = re.compile(r"^uuid:[0-9a-fA-F\-]{36}$")

        assert isinstance(s1, URIRef)
        assert uuid_regex.match(str(s1))

        assert isinstance(s2, URIRef)
        assert uuid_regex.match(str(s2))

        assert isinstance(o2, URIRef)
        assert uuid_regex.match(str(o2))

        assert str(s1) != str(s2)
        assert str(o2) == str(s1)

    def test_creating_new_graphs_error(self):
        # {
        #  "@context": {
        #    "kjdh@base": "https://example.org/",
        #    "name": "http://schema.org/name",
        #    "knows": {
        #      "@id": "http://schema.org/knows",
        #      "@type": "@id"
        #    },
        #    "Person": "http://schema.org/Person"
        #  },
        #  "@graph": [
        #    {
        #      "@type": "Person",
        #      "name": "Alice",
        #      "knows": [
        #        {
        #          "@id": "_:bob"
        #        },
        #        {
        #          "@id": "_:carol"
        #        }
        #      ]
        #    },
        #    {
        #      "@id": "_:bob",
        #      "@graph": [
        #        {
        #          "@type": "Person",
        #          "name": "Bob"
        #        }
        #      ]
        #    },
        #    {
        #      "@id": "_:carol",
        #      "@graph": [
        #        {
        #          "@type": "Person",
        #          "name": "Carol"
        #        }
        #      ]
        #    }
        #  ]
        # }

        nquads_array = [
            '_:c14n2 <http://schema.org/name> "Carol" _:c14n0 .',
            "_:c14n2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n0 .",
            "_:c14n3 <http://schema.org/knows> _:c14n0 .",
            "_:c14n3 <http://schema.org/knows> _:c14n1 .",
            '_:c14n3 <http://schema.org/name> "Alice" .',
            "_:c14n3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .",
            '_:c14n4 <http://schema.org/name> "Bob" _:c14n1 .',
            "_:c14n4 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n1 .",
        ]
        with pytest.raises(kc_tools.UnsupportedJSONLD) as exc:
            raise kc_tools.UnsupportedJSONLD(nquads_array)

        expected_message = """Unsupported JSON-LD input detected

After parsing the JSON-LD input, the parser detected creation of new named graphs.
The DKG does not support custom named graphs.

Problematic Quads:

1. _:c14n2 <http://schema.org/name> "Carol" _:c14n0 .
2. _:c14n2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n0 .
3. _:c14n4 <http://schema.org/name> "Bob" _:c14n1 .
4. _:c14n4 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n1 .

Full Parsed N-Quads Array:

_:c14n2 <http://schema.org/name> "Carol" _:c14n0 .
_:c14n2 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n0 .
_:c14n3 <http://schema.org/knows> _:c14n0 .
_:c14n3 <http://schema.org/knows> _:c14n1 .
_:c14n3 <http://schema.org/name> "Alice" .
_:c14n3 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> .
_:c14n4 <http://schema.org/name> "Bob" _:c14n1 .
_:c14n4 <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/Person> _:c14n1 ."""

        assert exc.value.message.strip() == expected_message


class TestCalculateMerkleRoot:
    def test_calculate_merkle_root_with_example_data(self):
        """Test calculate_merkle_root function with real-world example data."""
        quads = [
            '<urn:us-cities:info:new-york> <http://schema.org/area> "468.9 sq mi" .',
            '<urn:us-cities:info:new-york> <http://schema.org/name> "New York" .',
            '<urn:us-cities:info:new-york> <http://schema.org/population> "8,336,817" .',
            '<urn:us-cities:info:new-york> <http://schema.org/state> "New York" .',
            "<urn:us-cities:info:new-york> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> <http://schema.org/City> .",
            '<uuid:6fd70e74-369d-4398-bdf3-1f25bfbf551c> <https://ontology.origintrail.io/dkg/1.0#privateMerkleRoot> "0xaac2a420672a1eb77506c544ff01beed2be58c0ee3576fe037c846f97481cefd" .',
            "<https://ontology.origintrail.io/dkg/1.0#metadata-hash:0x5cb6421dd41c7a62a84c223779303919e7293753d8a1f6f49da2e598013fe652> <https://ontology.origintrail.io/dkg/1.0#representsPrivateResource> <uuid:e0367b5c-a594-4131-8870-746f5551fa36> .",
            "<https://ontology.origintrail.io/dkg/1.0#metadata-hash:0x6a2292b30c844d2f8f2910bf11770496a3a79d5a6726d1b2fd3ddd18e09b5850> <https://ontology.origintrail.io/dkg/1.0#representsPrivateResource> <uuid:4ccd8930-90d4-4d6d-9aba-150fca68e18d> .",
            "<https://ontology.origintrail.io/dkg/1.0#metadata-hash:0xc1f682b783b1b93c9d5386eb1730c9647cf4b55925ec24f5e949e7457ba7bfac> <https://ontology.origintrail.io/dkg/1.0#representsPrivateResource> <uuid:0bb24334-91b8-431c-917a-c6c868325277> .",
        ]

        merkle_root = kc_tools.calculate_merkle_root(quads)

        # Expected merkle root for this dataset
        expected_merkle_root = (
            "0x897442f7db61619b9f272c69d787975f169d0624d7f08c216017c3218c8ea5da"
        )

        # Verify the result matches the expected value
        assert merkle_root == expected_merkle_root
