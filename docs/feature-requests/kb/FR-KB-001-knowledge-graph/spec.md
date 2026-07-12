---
id: FR-KB-001
title: "Knowledge-graph schema - node + edge taxonomy of the three systems, pluggable GraphStore, default relational l2_edge table in Postgres (no graph DB at MVP), dual role as engine rule source + RAG graph arm"
module: KB
priority: SHOULD
status: done
phase: P0
slice: 1
lang: python
effort_h: 12
owner: Stephen Cheng (Founder/CPO)
created: 2026-07-08
refs: [Claude-06 s3, strategy 4.1, strategy 5]
related_frs: [FR-KB-002, FR-KB-003, FR-KB-005, FR-RULE-001, FR-RAG-002, FR-PLAT-003]
depends_on: [FR-PLAT-001]
blocks: [FR-KB-002, FR-KB-005]
new_paths:
  - packages/tamthuc_kb/pyproject.toml
  - packages/tamthuc_kb/tamthuc_kb/__init__.py
  - packages/tamthuc_kb/tamthuc_kb/graph/__init__.py
  - packages/tamthuc_kb/tamthuc_kb/graph/taxonomy.py
  - packages/tamthuc_kb/tamthuc_kb/graph/models.py
  - packages/tamthuc_kb/tamthuc_kb/graph/store.py
  - packages/tamthuc_kb/tamthuc_kb/graph/seed.py
  - packages/tamthuc_kb/migrations/0001_l2_graph.sql
  - packages/tamthuc_kb/tests/test_graph_schema.py
  - packages/tamthuc_kb/tests/fixtures/graph_seed_sample.json
  - docs/contracts/knowledge-graph.schema.json
---

## §1 - Description (BCP-14 normative)

This FR defines the knowledge graph of Tam Thuc: the closed taxonomy of node kinds and edge relations that encode the primitives and relationships of the three systems, plus a pluggable storage layer whose default is a relational edge table in the shared Postgres. It is the birth of the `tamthuc_kb` Python package. This FR owns the graph shape and the store protocol; it does NOT own the classical text (that is FR-KB-003) nor the 150-200 interpretation patterns (that is FR-KB-002).

The node taxonomy SHALL be a closed enum covering: thiên can (天干), địa chi (地支), 60 giáp tý (六十甲子), ngũ hành (五行), bát quái (八卦), cửu cung (九宮), 12 thiên tướng (十二天將), cửu tinh (九星), bát môn (八門), bát thần (八神), 16 thần (十六神), cách cục (格局), khóa thể (課體), and thần sát (神煞). The edge taxonomy SHALL be a closed enum covering: ngũ hành sinh/khắc (生/剋); địa chi hình/xung/phá/hại/hợp (刑/沖/破/害/合); vị trí ký cung/lạc cung/lâm (寄宮/落宮/臨); and trạng thái thừa/vượng-tướng-hưu-tù-tử (乘/旺-相-休-囚-死). New kinds or relations SHALL be added by extending the enum and the contract schema, never by inventing free-text kinds at write time.

Storage SHALL be pluggable behind a `GraphStore` protocol. The MVP default SHALL be a relational edge table `l2_edge(src, rel, dst, attrs)` alongside an `l2_node(id, kind, ...)` table in the shared Postgres (FR-PLAT-003), matching the cyberos house pattern - no separate graph database is introduced at MVP. Neo4j, an RDF triple store, and a native property-graph adapter SHALL be reserved behind the same protocol so the store can be swapped later without touching callers. Every write SHALL validate that `kind` and `rel` are members of the closed enums; an unknown kind or relation SHALL be rejected, not stored.

The graph SHALL serve two consumers through one shape (Claude-06 s3): it is the structured rule source the deterministic layer reads (ngũ hành and địa chi relations that patterns reference), and it is one half of hybrid RAG retrieval - the graph arm that FR-KB-005 exposes and FR-RAG-002 fuses with the vector arm.

## §2 - Why this design (rationale for humans)

The three systems are not flat vocabularies; they are dense relational structures. Whether a cách cục is auspicious turns on whether one element sinh or khắc another, whether two địa chi are in hợp or in xung, whether a star sits in its own cung (lâm) or is lodged elsewhere (ký cung), and whether an element is vượng or tù in the current season. Encoding those relations once, as a graph the whole platform reads, keeps a single source of truth for "what relates to what" instead of scattering the same sinh/khắc table across three engines and the RAG prompt builder (Claude-06 s3).

The store is deliberately relational at MVP. The cyberos program already retired a dedicated graph database in favor of a relational `l2_edge` table because any managed Postgres can host it, it needs no second piece of stateful infrastructure to operate and back up, and the query shapes this product needs (one- and two-hop neighborhoods, filtered by kind and relation) are cheap in SQL. A graph DB buys multi-hop traversal we do not need at MVP and costs an extra system to run; the protocol keeps that door open without paying for it now. The closed-enum discipline on kinds and relations is the same instinct as the school-flag discipline elsewhere: the domain is finite and known, so encode it as a checked type and let a bad value fail loudly rather than accrete silently.

## §3 - Contract (schema / types / storage)

### Node and edge taxonomy (`tamthuc_kb/graph/taxonomy.py`)

```python
class NodeKind(str, Enum):
    thien_can = "thien_can"        # 天干
    dia_chi = "dia_chi"            # 地支
    giap_ty = "giap_ty"            # 六十甲子
    ngu_hanh = "ngu_hanh"          # 五行
    bat_quai = "bat_quai"          # 八卦
    cuu_cung = "cuu_cung"          # 九宮
    thien_tuong = "thien_tuong"    # 十二天將
    cuu_tinh = "cuu_tinh"          # 九星
    bat_mon = "bat_mon"            # 八門
    bat_than = "bat_than"          # 八神
    than_16 = "than_16"            # 十六神
    cach_cuc = "cach_cuc"          # 格局
    khoa_the = "khoa_the"          # 課體
    than_sat = "than_sat"          # 神煞

class EdgeRel(str, Enum):
    sinh = "sinh"; khac = "khac"                                  # 生 / 剋 (ngu hanh)
    hinh = "hinh"; xung = "xung"; pha = "pha"; hai = "hai"; hop = "hop"  # 刑/沖/破/害/合 (dia chi)
    ky_cung = "ky_cung"; lac_cung = "lac_cung"; lam = "lam"       # 寄宮/落宮/臨 (vi tri)
    thua = "thua"; trang_thai = "trang_thai"                      # 乘 / 旺-相-休-囚-死 (trang thai)
```

### Node and edge models (`tamthuc_kb/graph/models.py`)

```python
class Node(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str               # stable slug, e.g. "thien_can_giap", "ngu_hanh_moc", "dia_chi_ti"
    kind: NodeKind
    label: str            # display, e.g. "Giáp"
    label_han: str | None # 甲
    system: System        # qimen | liuren | taiyi | all (a primitive shared by all is "all")
    attrs: dict           # kind-specific, e.g. {"am_duong": "duong", "hanh": "moc"}

class Edge(BaseModel):
    model_config = ConfigDict(extra="forbid")
    src: str              # Node.id
    rel: EdgeRel
    dst: str              # Node.id
    attrs: dict           # qualifier, e.g. {"state": "vuong", "mua": "xuan"} for trang_thai
```

A `trạng thái` fact (Mộc is vượng in spring) is an edge `(ngu_hanh_moc, trang_thai, mua_xuan)` with `attrs={"state": "vuong"}`; a `thừa` fact (a thiên tướng riding a chi) is `(thien_tuong_x, thua, dia_chi_y)`. The state enum vượng/tướng/hưu/tù/tử lives in `attrs.state`, not as five separate relations, so the relation set stays small and the qualifier stays queryable.

### GraphStore protocol (`tamthuc_kb/graph/store.py`)

```python
class GraphStore(Protocol):
    def upsert_nodes(self, nodes: list[Node]) -> None: ...        # idempotent by Node.id
    def upsert_edges(self, edges: list[Edge]) -> None: ...        # idempotent by (src, rel, dst)
    def neighbors(self, node_id: str, rel: EdgeRel | None = None,
                  direction: str = "out") -> list[Edge]: ...      # one-hop, optional rel filter
    def relation(self, src: str, rel: EdgeRel, dst: str) -> Edge | None: ...
    def nodes_of_kind(self, kind: NodeKind, system: System | None = None) -> list[Node]: ...

class RelationalGraphStore:   # default (MVP): l2_node + l2_edge in the shared Postgres
    ...
class Neo4jGraphStore:  ...   # reserved, behind config
class RdfGraphStore:    ...   # reserved, behind config
```

### Relational storage (`packages/tamthuc_kb/migrations/0001_l2_graph.sql`)

```sql
create table l2_node (
  id      text primary key,
  kind    text not null,            -- checked against NodeKind at the app layer + check constraint
  label   text not null,
  label_han text,
  system  text not null default 'all',
  attrs   jsonb not null default '{}'
);
create table l2_edge (
  src   text not null references l2_node(id),
  rel   text not null,              -- checked against EdgeRel
  dst   text not null references l2_node(id),
  attrs jsonb not null default '{}',
  primary key (src, rel, dst)
);
create index l2_node_kind on l2_node(kind, system);
create index l2_edge_src on l2_edge(src, rel);
create index l2_edge_dst on l2_edge(dst, rel);
```

`kind` and `rel` carry SQL check constraints listing the closed enums so the database rejects a bad value even if a caller bypasses the app layer. Idempotency is by primary key on both tables (`id`; `(src, rel, dst)`).

## §4 - Acceptance criteria

1. `NodeKind` enumerates exactly the fourteen node kinds and `EdgeRel` exactly the relations listed in section 1; a test asserts the enum members against `docs/contracts/knowledge-graph.schema.json`, so the code and the contract cannot drift.
2. `upsert_nodes` / `upsert_edges` are idempotent: re-seeding the base taxonomy leaves node and edge counts unchanged.
3. Writing a node with a `kind` outside `NodeKind`, or an edge with a `rel` outside `EdgeRel`, is rejected by both the app-layer validator and the SQL check constraint (two independent guards).
4. `neighbors("ngu_hanh_moc", rel=EdgeRel.sinh, direction="out")` returns the Mộc-sinh-Hỏa edge; `relation("dia_chi_ti", EdgeRel.xung, "dia_chi_ngo")` returns the Tý-Ngọ xung edge.
5. The seeded base graph contains the ten thiên can, twelve địa chi, five ngũ hành with the full sinh and khắc cycles, and the địa chi hình/xung/phá/hại/hợp relations, each with its Han label.
6. `nodes_of_kind(NodeKind.cach_cuc)` returns cách cục nodes filtered by `system`, and a `RelationalGraphStore` and an in-memory stub return identical results on the fixture (backend parity).

## §5 - Verification

- `tests/test_graph_schema.py`: enum-vs-contract parity; node/edge round-trip with `extra="forbid"` rejecting unknown fields; idempotent re-seed; the two independent bad-enum guards; the neighbor and relation lookups from acceptance 4; the ngũ hành cycle completeness check.
- Backend parity: run the fixture through the `RelationalGraphStore` (against a test Postgres or a fake) and an `InMemoryGraphStore`, assert identical `neighbors` and `nodes_of_kind` results.
- Gates: `ruff check`, `ruff format --check`, `mypy tamthuc_kb`, `pytest packages/tamthuc_kb` (default suite uses the in-memory store; the Postgres path runs behind a marker when a test DB is present).

## §6 - Implementation skeleton

1. Create the `tamthuc_kb` package (`pyproject.toml`, `uv`-managed per FR-PLAT-001); this FR owns its birth, FR-KB-002/003/005 add modules.
2. `graph/taxonomy.py`: the `NodeKind` and `EdgeRel` closed enums with Han comments.
3. `graph/models.py`: `Node`, `Edge` Pydantic models with `extra="forbid"`.
4. `graph/store.py`: the `GraphStore` protocol, `RelationalGraphStore` (default), `InMemoryGraphStore` (tests), and reserved `Neo4jGraphStore` / `RdfGraphStore` stubs.
5. `graph/seed.py`: `seed_base_taxonomy(store)` writing the can/chi/ngũ hành primitives and their sinh/khắc and hình/xung/phá/hại/hợp relations from a committed data file.
6. Author `docs/contracts/knowledge-graph.schema.json` (source of truth for the node/edge shape and the enums) and `migrations/0001_l2_graph.sql`.

## §7 - Dependencies

Depends on FR-PLAT-001 (the Python workspace). Soft edge to FR-PLAT-003: the `l2_node` / `l2_edge` DDL is owned here (KB is the natural owner of the graph tables) but is applied through the PLAT migration runner and lives in the same shared Postgres; the hard `depends_on` stays PLAT-001 per the master catalog, and the coordination with PLAT-003 is a reconciliation note, not a build blocker. Blocks FR-KB-002 (pattern conditions reference graph node ids and relations) and FR-KB-005 (the hybrid-retrieval query API traverses this graph). Read at runtime by FR-RAG-002 (the graph arm of hybrid retrieval, via KB-005) and referenced by the deterministic relation logic that FR-CORE-007 and FR-RULE-002 encode.

## §8 - Example payloads

```json
// nodes
[ { "id": "ngu_hanh_moc", "kind": "ngu_hanh", "label": "Mộc", "label_han": "木", "system": "all", "attrs": {} },
  { "id": "ngu_hanh_hoa", "kind": "ngu_hanh", "label": "Hỏa", "label_han": "火", "system": "all", "attrs": {} },
  { "id": "dia_chi_ti",  "kind": "dia_chi",  "label": "Tý",  "label_han": "子", "system": "all", "attrs": {"hanh": "thuy"} },
  { "id": "dia_chi_ngo", "kind": "dia_chi",  "label": "Ngọ", "label_han": "午", "system": "all", "attrs": {"hanh": "hoa"} } ]
```

```json
// edges
[ { "src": "ngu_hanh_moc", "rel": "sinh", "dst": "ngu_hanh_hoa", "attrs": {} },
  { "src": "dia_chi_ti",  "rel": "xung", "dst": "dia_chi_ngo",  "attrs": {} },
  { "src": "ngu_hanh_moc", "rel": "trang_thai", "dst": "mua_xuan", "attrs": {"state": "vuong"} } ]
```

## §9 - Open questions

- Relational edge table vs a graph DB. Default for MVP: relational `l2_edge` in the shared Postgres, matching the cyberos pattern (one fewer stateful system to run and back up). Revisit only if a real query needs deep multi-hop traversal that SQL makes awkward; the `GraphStore` protocol keeps Neo4j/RDF swappable.
- Whether `trạng thái` (vượng/tướng/hưu/tù/tử) belongs on the graph at all or is computed per-cast by CORE. Default: store the canonical season-to-state table as graph edges (it is fixed reference data), and let the engine read it; a per-cast state is derived, not stored.
- Node id namespacing across systems. Default: primitives shared by all systems (can, chi, ngũ hành) are `system="all"` with a single id; system-specific nodes (a QiMen-only cách cục) carry the `system` tag and a system-prefixed id. Decide the exact prefix convention with FR-KB-002.

## §10 - Failure modes inventory

| Mode | Trigger | Required behavior |
|---|---|---|
| Free-text kind | a caller invents a `kind` not in the enum | rejected at the app layer and by the SQL check constraint; never stored |
| Relation explosion | vượng/tướng/hưu/tù/tử modeled as five relations | kept as one `trang_thai` relation with `attrs.state`; relation set stays closed and small |
| Duplicate on re-seed | upsert not keyed by primary key | idempotency by `id` and `(src, rel, dst)`; re-seed is a no-op |
| Silent graph-DB coupling | a caller assumes Cypher/traversal semantics | callers use the `GraphStore` protocol only; no store-specific query leaks past it |
| Orphan edge | edge references a missing node | foreign keys on `l2_edge(src)` / `l2_edge(dst)`; the write fails rather than dangling |
| Cross-system leak | a `system=all` query returns a QiMen-only node inappropriately | `nodes_of_kind` and neighbor queries filter by `system in {system, all}` |

## §11 - Notes

This FR is marked SHOULD, not MUST, at P0: the P0 end-to-end flow can run with the ngũ hành / địa chi relations that FR-CORE-007 encodes directly, and RAG-002 degrades to vector-only until FR-KB-005 activates the graph arm. But building the schema in P0 pays for itself immediately, because FR-KB-002's pattern conditions and FR-CORE-007's relation checks both want a single source of truth for "what relates to what". Keep the boundary clean: this FR owns the graph shape and store; FR-KB-002 fills the cách cục / khóa thể / thần sát nodes and the interpretation patterns; FR-KB-003 owns the classical text the citations resolve into. The package `tamthuc_kb` is shared with FR-KB-002/003/005; they extend it, so the knowledge base is one installable, mypy-clean unit.
