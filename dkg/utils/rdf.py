# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Literal

from rdflib.plugins.parsers.nquads import NQuadsParser
from io import StringIO

from dkg.constants import CHUNK_BYTE_SIZE, PRIVATE_ASSERTION_PREDICATE
from dkg.exceptions import DatasetInputFormatNotSupported, InvalidDataset
from dkg.types import JSONLD, HexStr, NQuads
from dkg.utils.merkle import MerkleTree, hash_assertion_with_indexes
from pyld import jsonld
from dkg.constants import DEFAULT_RDF_FORMAT, DEFAULT_CANON_ALGORITHM
from rdflib import Graph, BNode, URIRef, Literal as RDFLiteral
from uuid import uuid4
from web3 import Web3
import math


def normalize_dataset(
    dataset: JSONLD | NQuads,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    output_format=DEFAULT_RDF_FORMAT,
    algorithm=DEFAULT_CANON_ALGORITHM,
) -> NQuads:
    normalization_options = {
        "algorithm": algorithm,
        "format": output_format,
    }

    match input_format.lower():
        case "json-ld" | "jsonld":
            pass
        case "n-quads" | "nquads":
            normalization_options["inputFormat"] = "application/n-quads"
        case _:
            raise DatasetInputFormatNotSupported(
                f"Dataset input format isn't supported: {input_format}. "
                "Supported formats: JSON-LD / N-Quads."
            )

    n_quads = jsonld.normalize(dataset, normalization_options)
    assertion = [quad for quad in n_quads.split("\n") if quad]

    if not assertion:
        raise InvalidDataset("Invalid dataset, no quads were extracted.")

    return assertion


def format_content(
    content: dict[Literal["public", "private"], JSONLD],
    type: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
) -> dict[str, dict[str, HexStr | NQuads | int]]:
    public_graph = {"@graph": []}

    if content.get("public", None):
        public_graph["@graph"].append(content["public"])

    if content.get("private", None):
        private_assertion = normalize_dataset(content["private"], type)
        private_assertion_id = MerkleTree(
            hash_assertion_with_indexes(private_assertion),
            sort_pairs=True,
        ).root

        public_graph["@graph"].append(
            {PRIVATE_ASSERTION_PREDICATE: private_assertion_id}
        )

    public_assertion = normalize_dataset(public_graph, type)

    return {
        "public": public_assertion,
        "private": private_assertion if content.get("private", None) else {},
    }


def is_empty_dict(dictionary: dict):
    return len(dictionary.keys()) == 0 and isinstance(dictionary, dict)


def format_dataset(
    content: dict,
    input_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    output_format=DEFAULT_RDF_FORMAT,
    algorithm=DEFAULT_CANON_ALGORITHM,
):
    private_assertion = None
    if content.get("private") and not is_empty_dict(content.get("private")):
        private_assertion = normalize_dataset(
            content.get("private"), input_format, output_format, algorithm
        )
    elif not content.get("public"):
        content = {"public": content}

    public_assertion = []
    if content.get("public"):
        public_assertion = normalize_dataset(
            content.get("public"), input_format, output_format, algorithm
        )

    if (
        public_assertion
        and len(public_assertion) == 0
        and private_assertion
        and len(private_assertion) == 0
    ):
        raise ValueError("File format is corrupted, no n-quads are extracted.")

    dataset = {"public": public_assertion}
    if private_assertion:
        dataset["private"] = private_assertion

    return dataset


def generate_missing_ids_for_blank_nodes(nquads_list: list[str]) -> list[str]:
    generated_ids = {}

    def replace_blank_node(term):
        # Handle blank nodes
        if isinstance(term, BNode):
            if str(term) not in generated_ids:
                generated_ids[str(term)] = URIRef(f"uuid:{str(uuid4())}")
            return generated_ids[str(term)]

        # Handle nested quads (RDF-star)
        if hasattr(term, "subject"):  # Check if term is a quad
            return Graph().quad(
                replace_blank_node(term.subject),
                replace_blank_node(term.predicate),
                replace_blank_node(term.object),
            )

        return term  # Return IRIs or Literals unchanged

    # Create a graph and parse the N-Quads
    g = Graph()
    g.parse(data="".join(nquads_list))

    # Create new graph for updated quads
    updated_graph = Graph()

    # Process each quad and replace blank nodes
    for quad in g:
        updated_quad = (
            replace_blank_node(quad[0]),  # subject
            replace_blank_node(quad[1]),  # predicate
            replace_blank_node(quad[2]),  # object
        )
        updated_graph.add(updated_quad)

    # Serialize back to N-Quads format and split into lines
    result = updated_graph.serialize(format="nquads").strip().split("\n")
    return [line for line in result if line]  # Remove empty


def group_nquads_by_subject(nquads_list: list[str], sort: bool = False):
    grouped = {}

    # Process each quad in original order
    for nquad in nquads_list:
        if not nquad.strip():  # Skip empty lines
            continue

        # Parse single quad
        g = Graph()
        g.parse(data=nquad, format="nquads")
        quad = next(iter(g))
        subject, predicate, obj = quad

        # Get subject key
        subject_key = (
            f"<<<{subject.subject}> <{subject.predicate}> <{subject.object}>>"
            if hasattr(subject, "subject")
            else f"<{subject}>"
        )

        # Initialize group if needed
        if subject_key not in grouped:
            grouped[subject_key] = []

        # Format object
        object_value = f'"{obj}"' if isinstance(obj, RDFLiteral) else f"<{obj}>"

        # Add quad to group
        quad_string = f"{subject_key} <{predicate}> {object_value} ."
        grouped[subject_key].append(quad_string)

    # Return grouped quads (sorted if requested)
    grouped_items = sorted(grouped.items()) if sort else grouped.items()
    return [quads for _, quads in grouped_items]


def split_into_chunks(quads, chunk_size_bytes=32):
    # Concatenate the quads with newline characters
    concatenated_quads = "\n".join(quads)

    # Encode the concatenated string to bytes
    encoded_bytes = concatenated_quads.encode("utf-8")

    # Split the encoded bytes into chunks
    chunks = []
    start = 0

    while start < len(encoded_bytes):
        end = min(start + chunk_size_bytes, len(encoded_bytes))
        chunk = encoded_bytes[start:end]
        chunks.append(chunk.decode("utf-8"))  # Decode bytes back to string
        start = end

    return chunks


def calculate_merkle_root(quads: list[str], chunk_size_bytes: int = CHUNK_BYTE_SIZE):
    chunks = split_into_chunks(quads, chunk_size_bytes)

    # Create leaves using solidityKeccak256 equivalent
    leaves = [
        bytes.fromhex(Web3.solidity_keccak(["string", "uint256"], [chunk, index]).hex())
        for index, chunk in enumerate(chunks)
    ]

    while len(leaves) > 1:
        next_level = []

        for i in range(0, len(leaves), 2):
            left = leaves[i]

            if i + 1 >= len(leaves):
                next_level.append(left)
                break

            right = leaves[i + 1]

            # Combine and sort the leaves
            combined = [left, right]
            combined.sort()

            # Calculate the hash of the combined leaves
            hash_value = Web3.keccak(b"".join(combined))
            next_level.append(hash_value)

        leaves = next_level

    return f"0x{leaves[0].hex()}"


def generate_named_node():
    return f"uuid:{uuid4()}"


def calculate_number_of_chunks(quads, chunk_size_bytes=CHUNK_BYTE_SIZE):
    # Concatenate the quads with newline characters
    concatenated_quads = "\n".join(quads)

    total_size_bytes = len(concatenated_quads.encode("utf-8"))

    # Calculate and return the number of chunks
    return math.ceil(total_size_bytes / chunk_size_bytes)
