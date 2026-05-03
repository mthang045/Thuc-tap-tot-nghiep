"""
MongoDB database layer for Legal AI Agent API.
Replaces PostgreSQL (Supabase) with MongoDB for unified database.

Usage:
    from src.db import get_db, init_db

    # In FastAPI startup:
    @app.on_event("startup")
    async def startup():
        init_db()

    # In sync code (same interface as old psycopg2 get_db):
    with get_db() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        row = cur.fetchone()
        print(row["used_quota"])  # dict-style access like RealDictCursor
        conn.commit()

MongoDB Collection Schema (mirrors old PostgreSQL tables):
    - companies: company accounts (plan, quota)
    - users: user accounts per company
    - api_keys: API keys per company
    - usage_logs: API call logs per company
    - chat_sessions: chat sessions
    - messages: chat messages
    - documents: uploaded documents
    - contracts: contract documents
    - templates: document templates
    - audit_logs: audit trail
    - law_documents: Vietnamese law metadata
    - law_chunks: law text chunks for search
    - document_annotations: DOCX annotation metadata
"""

import os
import re
import json
import hashlib
from datetime import datetime
from typing import Any, Dict, List, Optional
from contextlib import contextmanager

from dotenv import load_dotenv

load_dotenv()

# ============================================
# MongoDB Connection
# ============================================

_MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
_MONGODB_DB_NAME = os.getenv("MONGODB_DB", "legal_AI_db")

_client = None
_db = None


def get_mongo_client():
    """Get or create MongoDB client (singleton)."""
    global _client, _db
    if _client is None:
        import pymongo
        _client = pymongo.MongoClient(
            _MONGODB_URI,
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000,
        )
        _client.admin.command("ping")
        _db = _client[_MONGODB_DB_NAME]
    return _db


def _ensure_indexes():
    """Create MongoDB indexes on startup."""
    db = get_mongo_client()

    db.companies.create_index("name")
    db.companies.create_index("plan")

    db.users.create_index("email", unique=True)
    db.users.create_index("company_id")
    db.users.create_index("role")

    db.api_keys.create_index([("key_hash", 1), ("key_prefix", 1)])
    db.api_keys.create_index("company_id")
    db.api_keys.create_index("is_active")

    db.usage_logs.create_index("company_id")
    db.usage_logs.create_index([("company_id", 1), ("created_at", -1)])

    db.chat_sessions.create_index("company_id")
    db.chat_sessions.create_index("user_id")
    db.chat_sessions.create_index([("user_id", 1), ("company_id", 1), ("status", 1)])
    db.chat_sessions.create_index([("user_id", 1), ("company_id", 1), ("last_message_at", -1)])

    db.messages.create_index("session_id")
    db.messages.create_index([("session_id", 1), ("created_at", 1)])
    db.messages.create_index([("session_id", 1), ("company_id", 1)])

    db.documents.create_index("company_id")
    db.documents.create_index([("company_id", 1), ("created_at", -1)])

    db.contracts.create_index("company_id")
    db.contracts.create_index([("company_id", 1), ("created_at", -1)])

    db.templates.create_index("company_id")
    db.templates.create_index([("company_id", 1), ("is_default", 1)])
    db.templates.create_index("name")

    db.audit_logs.create_index([("company_id", 1), ("created_at", -1)])

    try:
        db.law_documents.create_index(
            [("title", "text"), ("content", "text")],
            default_language="vietnamese"
        )
    except Exception:
        pass
    db.law_documents.create_index("law_number")
    db.law_documents.create_index([("domains", 1)])

    db.law_chunks.create_index("law_id")
    db.law_chunks.create_index([("content", "text")], default_language="vietnamese")
    db.law_chunks.create_index([("domains", 1)])

    db.document_annotations.create_index("document_id")

    print("MongoDB indexes ensured.")


def init_db():
    """Initialize MongoDB connection and create indexes. Call on startup."""
    try:
        get_mongo_client()
        _ensure_indexes()
        print(f"MongoDB connected: {_MONGODB_DB_NAME}")
    except Exception as e:
        print(f"MongoDB init error: {e}")


# ============================================
# MongoDB → psycopg2-compatible cursor wrapper
# Returns dict objects (like RealDictCursor) for dict-style access
# ============================================


class DictDoc(dict):
    """dict subclass that allows attribute access (row.column) AND key access (row['column'])."""
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __getitem__(self, key):
        # Normalize underscore/dash vs camelCase aliases
        val = dict.get(self, key)
        if val is not None:
            return val
        # Try common aliases
        alias_map = {
            "user_id": ["userId"],
            "company_id": ["companyId"],
            "is_active": ["isActive"],
            "monthly_quota": ["monthlyQuota"],
            "used_quota": ["usedQuota"],
            "last_used_at": ["lastUsedAt"],
            "created_at": ["createdAt"],
            "updated_at": ["updatedAt"],
            "last_message_at": ["lastMessageAt"],
            "message_count": ["messageCount"],
            "extracted_text": ["extractedText"],
            "doc_type": ["docType"],
            "file_path": ["filePath"],
            "file_size": ["fileSize"],
            "mime_type": ["mimeType"],
            "uploaded_by": ["uploadedBy"],
            "contract_type": ["contractType"],
            "start_date": ["startDate"],
            "end_date": ["endDate"],
            "law_id": ["lawId"],
            "chunk_id": ["chunkId"],
            "chunk_title": ["chunkTitle"],
            "content_preview": ["contentPreview"],
            "law_title": ["lawTitle"],
            "law_number": ["lawNumber"],
        }
        for alias in alias_map.get(key, []):
            val = dict.get(self, alias)
            if val is not None:
                return val
        return None


class MongoCursor:
    """
    MongoDB cursor wrapper that mimics psycopg2 RealDictCursor behavior.
    Returns dict-like objects accessible via row["column_name"] syntax.
    """

    def __init__(self, db):
        self.db = db
        self.sql = ""
        self.sql_upper = ""
        self.params: tuple = ()
        self._result: List[Dict[str, Any]] = []
        self._index = 0
        self._rowcount = -1

    def _param(self, idx: int) -> Any:
        """Get parameter by 1-based index."""
        if idx <= len(self.params):
            return self.params[idx - 1]
        return None

    def execute(self, sql: str = "", params: tuple = None):
        """Execute a SQL-like query mapped to MongoDB. Returns dict results."""
        if sql:
            self.sql = sql.strip()
        if params:
            self.params = params
        self.sql_upper = self.sql.upper()
        self._index = 0

        if self.sql_upper.startswith("INSERT"):
            self._exec_insert()
        elif self.sql_upper.startswith("UPDATE"):
            self._exec_update()
        elif self.sql_upper.startswith("DELETE"):
            self._exec_delete()
        elif self.sql_upper.startswith("SELECT"):
            self._exec_select()
        elif self.sql_upper.startswith("CREATE TABLE"):
            pass  # no-op for MongoDB

        self._rowcount = len(self._result)
        return self

    # ---- INSERT ----

    def _exec_insert(self):
        table, doc = self._parse_insert()
        if not (table and doc):
            self._result = []
            return

        col = self.db[table]
        if "RETURNING" in self.sql_upper:
            ret_col = self._parse_returning_col()
            result = col.insert_one(doc)
            if ret_col in ("id", "_id"):
                self._result = [DictDoc({"id": result.inserted_id})]
            else:
                self._result = [DictDoc({ret_col: doc.get(ret_col)})]
        else:
            col.insert_one(doc)
            self._result = []

    # ---- UPDATE ----

    def _exec_update(self):
        table, filter_q, update_ops = self._parse_update()
        if not (table and update_ops):
            self._result = []
            return
        self.db[table].update_many(filter_q, update_ops)
        self._result = []

    # ---- DELETE ----

    def _exec_delete(self):
        table, filter_q = self._parse_delete()
        if not table:
            self._result = []
            return
        self.db[table].delete_many(filter_q)
        self._result = []

    # ---- SELECT dispatcher ----

    def _exec_select(self):
        s = self.sql_upper
        if self._is_count():
            self._exec_count()
        elif "FROM users" in s and "JOIN companies" in s:
            self._exec_users_with_companies()
        elif "FROM api_keys" in s and "JOIN companies" in s:
            self._exec_api_keys_with_companies()
        elif "FROM chat_sessions" in s:
            self._exec_chat_sessions()
        elif "FROM messages" in s:
            self._exec_messages()
        elif "FROM documents" in s:
            self._exec_documents()
        elif "FROM contracts" in s:
            self._exec_contracts()
        elif "FROM law_chunks" in s and "JOIN law_documents" in s:
            self._exec_law_chunks_join()
        elif "FROM law_chunks" in s:
            self._exec_law_chunks()
        elif "FROM law_documents" in s:
            self._exec_law_documents()
        elif "FROM templates" in s:
            self._exec_templates()
        elif "FROM usage_logs" in s:
            self._exec_usage_logs()
        elif "FROM audit_logs" in s:
            self._exec_audit_logs()
        elif "FROM companies" in s:
            self._exec_companies()
        elif "FROM users" in s:
            self._exec_users()
        else:
            self._result = []

    # ---- Count ----

    def _is_count(self) -> bool:
        return bool(re.search(r"\bcount\(\*\)\b", self.sql, re.IGNORECASE))

    def _exec_count(self):
        m = re.search(r"FROM\s+(\w+)", self.sql, re.IGNORECASE)
        if m:
            count = self.db[m.group(1)].count_documents({})
            self._result = [DictDoc({"count": count})]
        else:
            self._result = [DictDoc({"count": 0})]

    # ---- users + companies JOIN ----

    def _exec_users_with_companies(self):
        user_id = self._param(1)
        user = self.db.users.find_one(self._id_filter(user_id))
        if not user:
            self._result = []
            return

        company = self.db.companies.find_one(self._id_filter(user.get("company_id")))
        self._result = [DictDoc({
            "user_id": user.get("_id") or user.get("id"),
            "company_id": user.get("company_id"),
            "role": user.get("role"),
            "company_name": company.get("name", "") if company else "",
            "plan": company.get("plan", "free") if company else "free",
            "monthly_quota": company.get("monthly_quota", 0) if company else 0,
            "used_quota": company.get("used_quota", 0) if company else 0,
        })]

    # ---- api_keys + companies JOIN ----

    def _exec_api_keys_with_companies(self):
        key_prefix = self._param(1)
        key_hash = self._param(2)
        key_doc = self.db.api_keys.find_one({
            "key_prefix": key_prefix,
            "key_hash": key_hash,
            "is_active": True,
        })
        if not key_doc:
            self._result = []
            return

        company = self.db.companies.find_one(self._id_filter(key_doc.get("company_id")))
        self._result = [DictDoc({
            "id": key_doc.get("_id") or key_doc.get("id"),
            "company_id": key_doc.get("company_id"),
            "permissions": key_doc.get("permissions", []),
            "rate_limit": key_doc.get("rate_limit", 60),
            "company_name": company.get("name", "") if company else "",
            "plan": company.get("plan", "free") if company else "free",
            "monthly_quota": company.get("monthly_quota", 0) if company else 0,
            "used_quota": company.get("used_quota", 0) if company else 0,
        })]

    # ---- chat_sessions ----

    def _exec_chat_sessions(self):
        if "INSERT INTO chat_sessions" in self.sql_upper:
            table, doc = self._parse_insert()
            if "RETURNING" in self.sql_upper:
                result = self.db.chat_sessions.insert_one(doc)
                self._result = [DictDoc({"id": result.inserted_id})]
            else:
                self.db.chat_sessions.insert_one(doc)
                self._result = []
            return

        user_id = self._param(1)
        company_id = self._param(2)

        query: Dict[str, Any] = {
            "user_id": user_id,
            "company_id": self._to_objectid_or_str(company_id),
        }
        # Extract fixed-value WHERE conditions
        agent_type = self._extract_fixed_value("agent_type")
        if agent_type:
            query["agent_type"] = agent_type
        status = self._extract_fixed_value("status")
        if status:
            query["status"] = status

        descending = "DESC" in self.sql_upper
        sort_col = "last_message_at"
        if "last_message_at" not in self.sql_upper:
            sort_col = "created_at"

        rows = list(
            self.db.chat_sessions.find(query)
            .sort(sort_col, -1 if descending else 1)
            .limit(1)
        )
        self._result = [DictDoc({"id": r.get("_id") or r.get("id")}) for r in rows]

        # Also handle UPDATE chat_sessions
        if self.sql_upper.startswith("UPDATE chat_sessions"):
            _, filter_q, update_ops, _ = self._parse_update()
            self.db.chat_sessions.update_many(filter_q, update_ops)
            self._result = []

    # ---- messages ----

    def _exec_messages(self):
        session_id = self._param(1)
        company_id = self._param(2)
        rows = list(
            self.db.messages.find({
                "session_id": session_id,
                "company_id": self._to_objectid_or_str(company_id),
            }).sort("created_at", 1).limit(50)
        )
        self._result = [DictDoc({"role": r.get("role"), "content": r.get("content")}) for r in rows]

    # ---- documents ----

    def _exec_documents(self):
        company_id = self._param(1)
        limit = self._extract_limit()
        rows = list(
            self.db.documents.find(
                {"company_id": self._to_objectid_or_str(company_id)}
            ).sort("created_at", -1).limit(limit)
        )
        self._result = [DictDoc({
            "name": r.get("name", ""),
            "extracted_text": r.get("extracted_text", ""),
            "doc_type": r.get("doc_type", ""),
            "analysis": r.get("analysis"),
            "file_path": r.get("file_path"),
            "mime_type": r.get("mime_type"),
            "company_id": r.get("company_id"),
            "id": r.get("_id") or r.get("id"),
        }) for r in rows]

    # ---- contracts ----

    def _exec_contracts(self):
        company_id = self._param(1)
        limit = self._extract_limit()
        rows = list(
            self.db.contracts.find({
                "company_id": self._to_objectid_or_str(company_id),
                "status": {"$ne": "deleted"},
            }).sort("created_at", -1).limit(limit)
        )
        self._result = [DictDoc({
            "name": r.get("name", ""),
            "contract_type": r.get("contract_type", ""),
            "extracted_text": r.get("extracted_text", ""),
            "parties": r.get("parties"),
            "start_date": r.get("start_date"),
            "end_date": r.get("end_date"),
            "notes": r.get("notes"),
            "status": r.get("status"),
            "id": r.get("_id") or r.get("id"),
        }) for r in rows]

    # ---- law_chunks + law_documents JOIN ----

    def _exec_law_chunks_join(self):
        ilike_match = re.search(r"lc\.content\s+ILIKE\s+%s", self.sql, re.IGNORECASE)
        if not ilike_match:
            self._result = []
            return

        pattern = self._param(1)
        if not pattern:
            self._result = []
            return
        keyword = pattern.strip("% ")

        domains_param = None
        if "domains &&" in self.sql_upper:
            domains_param = self._param(2)

        mongo_query: Dict[str, Any] = {"content": {"$regex": re.escape(keyword), "$options": "i"}}
        if domains_param:
            if isinstance(domains_param, str) and domains_param.startswith("{"):
                domains_list = [d.strip() for d in domains_param.strip("{}").split(",")]
                mongo_query["domains"] = {"$in": domains_list}
            elif isinstance(domains_param, list):
                mongo_query["domains"] = {"$in": domains_param}

        limit = self._extract_limit()
        chunks = list(self.db.law_chunks.find(mongo_query).limit(limit))

        law_ids = list(set(c.get("law_id") for c in chunks if c.get("law_id")))
        laws = {}
        for lid in law_ids:
            law = self.db.law_documents.find_one(self._id_filter(lid))
            if law:
                laws[lid] = law

        for chunk in chunks:
            law = laws.get(chunk.get("law_id"), {})
            title = law.get("title", "")
            if title.startswith("Bo Luat") or "Bộ luật" in title:
                priority = 0
            elif title.startswith("Luat ") or "Luật " in title:
                priority = 1
            elif "Nghi dinh" in title or "Nghị định" in title:
                priority = 2
            else:
                priority = 3

            self._result.append(DictDoc({
                "chunk_id": chunk.get("_id") or chunk.get("id"),
                "law_id": chunk.get("law_id"),
                "law_title": title,
                "law_number": law.get("law_number", ""),
                "article": chunk.get("article"),
                "chunk_title": chunk.get("title"),
                "content": chunk.get("content", ""),
                "domains": chunk.get("domains", []),
                "rank": 1.0,
                "priority": priority,
            }))

        self._result.sort(key=lambda x: (x.get("priority", 99), -len(x.get("content", ""))))

    # ---- law_chunks ----

    def _exec_law_chunks(self):
        if self._is_count():
            count = self.db.law_chunks.count_documents({})
            self._result = [DictDoc({"count": count})]
        else:
            self._result = []

    # ---- law_documents ----

    def _exec_law_documents(self):
        if self._is_count():
            count = self.db.law_documents.count_documents({})
            self._result = [DictDoc({"count": count})]
        else:
            self._result = []

    # ---- templates ----

    def _exec_templates(self):
        company_id = self._param(1)
        rows = list(self.db.templates.find(
            {"company_id": self._to_objectid_or_str(company_id)}
        ))
        self._result = [DictDoc(r) for r in rows]

    # ---- usage_logs ----

    def _exec_usage_logs(self):
        company_id = self._param(1)
        limit = self._extract_limit()
        rows = list(
            self.db.usage_logs.find(
                {"company_id": self._to_objectid_or_str(company_id)}
            ).sort("created_at", -1).limit(limit)
        )
        self._result = [DictDoc(r) for r in rows]

    # ---- audit_logs ----

    def _exec_audit_logs(self):
        company_id = self._param(1)
        limit = self._extract_limit()
        rows = list(
            self.db.audit_logs.find(
                {"company_id": self._to_objectid_or_str(company_id)}
            ).sort("created_at", -1).limit(limit)
        )
        self._result = [DictDoc(r) for r in rows]

    # ---- companies ----

    def _exec_companies(self):
        if self._is_count():
            count = self.db.companies.count_documents({})
            self._result = [DictDoc({"count": count})]
        else:
            rows = list(self.db.companies.find({}))
            self._result = [DictDoc(r) for r in rows]

    # ---- users ----

    def _exec_users(self):
        if "WHERE email =" in self.sql_upper:
            email = self._param(1)
            user = self.db.users.find_one({"email": email})
            self._result = [DictDoc({"id": user.get("_id") or user.get("id")})] if user else []
        elif "WHERE id =" in self.sql_upper or "WHERE id =" in self.sql:
            user_id = self._param(1)
            user = self.db.users.find_one(self._id_filter(user_id))
            self._result = [DictDoc(user)] if user else []
        else:
            rows = list(self.db.users.find({}))
            self._result = [DictDoc(r) for r in rows]

    # ---- Helper methods ----

    def _id_filter(self, val) -> Dict[str, Any]:
        """Build MongoDB _id filter, trying ObjectId first then string."""
        if val is None:
            return {}
        try:
            from bson import ObjectId
            if isinstance(val, str) and len(val) == 24:
                return {"_id": ObjectId(val)}
        except Exception:
            pass
        # Try _id field
        return {"_id": str(val)} if str(val) else {}

    def _to_objectid_or_str(self, val) -> Any:
        if val is None:
            return None
        try:
            from bson import ObjectId
            if isinstance(val, str) and len(val) == 24:
                return ObjectId(val)
        except Exception:
            pass
        return str(val)

    def _extract_limit(self) -> int:
        m = re.search(r"LIMIT\s+(\d+)", self.sql, re.IGNORECASE)
        return int(m.group(1)) if m else 20

    def _extract_fixed_value(self, col_name: str) -> Optional[str]:
        m = re.search(rf"{col_name}\s*=\s*['\"]?([\w-]+)['\"]?", self.sql, re.IGNORECASE)
        return m.group(1) if m else None

    def _parse_returning_col(self) -> str:
        m = re.search(r"RETURNING\s+(\w+)", self.sql, re.IGNORECASE)
        return m.group(1) if m else "id"

    # ---- Parse INSERT ----

    def _parse_insert(self) -> tuple:
        m = re.search(
            r"INSERT\s+INTO\s+(\w+)\s*\(([^)]+)\)\s*VALUES\s*\(([^)]+)\)",
            self.sql, re.IGNORECASE | re.DOTALL
        )
        if not m:
            return None, None
        table = m.group(1)
        cols = [c.strip() for c in m.group(2).split(",")]
        val_strs = [v.strip() for v in m.group(3).split(",")]
        doc = {}
        for col, val_str in zip(cols, val_strs):
            doc[col] = self._parse_value(val_str)
        return table, doc

    # ---- Parse UPDATE ----

    def _parse_update(self) -> tuple:
        m = re.search(
            r"UPDATE\s+(\w+)\s+SET\s+(.+?)\s+WHERE\s+(.+)",
            self.sql, re.IGNORECASE | re.DOTALL
        )
        if not m:
            return None, None, None
        table = m.group(1)
        set_clause = m.group(2)
        where = m.group(3)

        set_ops: Dict[str, Any] = {}
        pairs = re.findall(r"(\w+)\s*=\s*([^,]+?)(?:,|$)", set_clause, re.IGNORECASE)
        for col, val_str in pairs:
            col = col.strip()
            val_str = val_str.strip().rstrip(",")
            if col.lower() in ("now()", "now"):
                set_ops[col] = datetime.utcnow()
            else:
                set_ops[col] = self._parse_value(val_str)

        filter_q = self._parse_where(where)
        return table, filter_q, {"$set": set_ops}

    # ---- Parse DELETE ----

    def _parse_delete(self) -> tuple:
        m = re.search(
            r"DELETE\s+FROM\s+(\w+)(?:\s+WHERE\s+(.+))?",
            self.sql, re.IGNORECASE | re.DOTALL
        )
        if not m:
            return None, {}
        table = m.group(1)
        where = m.group(2) or ""
        return table, self._parse_where(where) if where.strip() else {}

    # ---- Parse WHERE ----

    def _parse_where(self, where_clause: str) -> Dict[str, Any]:
        query: Dict[str, Any] = {}
        if not where_clause.strip():
            return query
        conditions = re.split(r"\s+AND\s+", where_clause, re.IGNORECASE)
        idx = [1]
        for cond in conditions:
            cond = cond.strip()
            eq_m = re.search(r"(\w+)\s*=\s*%s", cond, re.IGNORECASE)
            if eq_m:
                query[eq_m.group(1)] = self._param(idx[0])
                idx[0] += 1
        return query

    # ---- Parse value ----

    def _parse_value(self, val_str: str) -> Any:
        val_str = val_str.strip()
        if val_str.lower() in ("now()", "now"):
            return datetime.utcnow()
        if val_str.lower() == "null":
            return None
        if val_str.lower() in ("true", "false"):
            return val_str.lower() == "true"
        if (val_str.startswith("'") and val_str.endswith("'")) or \
           (val_str.startswith('"') and val_str.endswith('"')):
            return val_str[1:-1]
        try:
            return int(val_str)
        except ValueError:
            try:
                return float(val_str)
            except ValueError:
                return val_str

    # ---- Cursor API ----

    def fetchone(self) -> Optional[Dict[str, Any]]:
        if not self._result:
            return None
        if self._index < len(self._result):
            row = self._result[self._index]
            self._index += 1
            return row
        return None

    def fetchall(self) -> List[Dict[str, Any]]:
        return self._result

    def fetchmany(self, size: int = None) -> List[Dict[str, Any]]:
        if not self._result:
            return []
        if size is None:
            size = 1
        start = self._index
        end = min(start + size, len(self._result))
        self._index = end
        return self._result[start:end]

    @property
    def rowcount(self) -> int:
        return self._rowcount

    @property
    def description(self) -> List:
        return []

    @property
    def lastrowid(self):
        return None

    def close(self):
        pass

    def __iter__(self):
        return iter(self._result)


class MongoConnection:
    """MongoDB connection wrapper, compatible with psycopg2 connection."""

    def __init__(self, db):
        self.db = db

    def cursor(self, cursor_factory=None):
        return MongoCursor(self.db)

    def commit(self):
        pass  # MongoDB auto-commits

    def close(self):
        pass

    def rollback(self):
        pass


@contextmanager
def get_db():
    """
    Context manager yielding MongoDB connection.
    Same interface as old psycopg2 `get_db()`.
    """
    db = get_mongo_client()
    conn = MongoConnection(db)
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
