from __future__ import annotations
from typing import Optional, Iterable, Tuple
from neo4j import GraphDatabase

class Neo4jConnector:
    def __init__(self, uri: str, user: str, password: str):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def write_graph(self, edges: Iterable[Tuple[str, str, str]]):
        """
        Write edges (u, v, rel_type) into Neo4j with simple labels.
        Nodes are labeled by their prefix before ':' (e.g., account:123 -> (:Account {id:'account:123'}))
        """
        def _label(node_id: str) -> str:
            prefix = (node_id.split(":")[0] or "Node").capitalize()
            return prefix

        cypher = """
        UNWIND $rows AS row
        MERGE (u:`%s` {id: row.u})
        MERGE (v:`%s` {id: row.v})
        MERGE (u)-[r:`%s`]->(v)
        """
        with self._driver.session() as session:
            for u, v, rel in edges:
                session.run(cypher % (_label(u), _label(v), rel), rows=[{"u": u, "v": v}])
