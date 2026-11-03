# VITUO — n8n Cloud + OpenAI (`gpt-4o-mini`) + Supabase `pgvector` + Google Workspace Diagnostic & Handover Hub

**Live Interactive Diagnostic Hub:** [https://dengel88.github.io/upwork/vituo-n8n-supabase-rag/](https://dengel88.github.io/upwork/vituo-n8n-supabase-rag/)  
**Architect:** Ayman K. | Synndicate AI (*Lead AI Systems Architect & Generative Media Producer*)

---

## Why 85%-Complete n8n Cloud + Supabase RAG Projects Stall (And How We Finish Them Cleanly)

When an n8n Cloud project integrating **OpenAI (`gpt-4o-mini` + `text-embedding-3-small`)**, **Supabase (`pgvector`)**, and **Google Workspace (Gmail, Google Calendar, Google Drive)** is 85% built, the remaining 15% almost always stalls on one of five specific integration issues:

1. **`pgvector` `match_documents` RPC Signature & Metadata Filter Mismatch**: n8n's native `@n8n/n8n-nodes-langchain.vectorStoreSupabase` node requires a specific SQL function signature (`query_embedding vector(1536), match_count int, filter jsonb`)—if `match_count` has no default or `filter` is missing, retrieval silently returns `0 rows` or throws `PGRST202`.
2. **Google OAuth2 Refresh Token Expiration (`invalid_grant`)**: Google Cloud apps left in "Testing" status expire refresh tokens every 7 days in n8n Cloud.
3. **Gmail Trigger Infinite Self-Reply Loops**: Triggering on unread messages without `-from:me` and thread-scoped memory causes duplicate agent replies.
4. **Google Calendar `$fromAI()` ISO-8601 Timezone Offset Bugs**: LLM tool calls passing bare dates without `-03:00` (`America/Argentina/Buenos_Aires`) book meetings 3 hours off.
5. **Google Drive Re-Index Vector Duplication**: Updating a Google Doc or PDF appends duplicate chunks into `public.documents` unless preceded by a native Supabase delete-by-`metadata->>file_id` step.

---

## Repository Contents

- `index.html` — Zero-build interactive **VITUO n8n Cloud + Supabase + Google Workspace Diagnostic & Handover Hub** with visual native node inspector, 5-point root-cause fix simulator, SQL generator, and 1-click JSON export.
- `workflows/supabase_rag_ingestion.json` — Native n8n Cloud workflow for Google Drive watching, binary conversion, vector deduplication, recursive chunking, and 1536-dim `text-embedding-3-small` insertion into Supabase.
- `workflows/google_workspace_agent.json` — Native n8n Cloud `Tools Agent` (`gpt-4o-mini`) with thread-scoped Postgres chat memory, Supabase Vector Store Tool, Google Calendar `$fromAI()` Tool, and Gmail Reply Tool (**zero brittle custom Code nodes**).
- `test_vituo_workflows.py` — Automated unit tests verifying native node compliance and codeword requirements.
- `PROPOSAL.md` — Fixed-price `$30` turnkey completion proposal starting with `VITUO`.
