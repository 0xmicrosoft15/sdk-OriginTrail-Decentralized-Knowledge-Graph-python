from uuid import uuid4


def generate_named_node():
    return f"uuid:{uuid4()}"
