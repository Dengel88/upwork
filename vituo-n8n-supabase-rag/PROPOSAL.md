VITUO

Live diagnostic hub and native n8n JSON templates I put together for your stack:
https://dengel88.github.io/upwork/vituo-n8n-supabase-rag/

Hi,

I work with this exact setup (n8n Cloud, GPT-4o-mini, Supabase pgvector, and Google Workspace APIs) regularly. Since your workflows are already mostly built, I can jump into your n8n Cloud and Supabase accounts today, fix the remaining bugs using native nodes only, test everything end-to-end, and write clear handover notes.

You can check the link above to see a similar native n8n + Supabase RAG + Gmail/Calendar architecture I built and how I document workflows for clients.

Here is what I usually check and fix first on this stack:

1. Supabase pgvector retrieval: making sure the `public.documents` vector dimensions (1536 for `text-embedding-3-small`) and the `match_documents(query_embedding, match_count, filter)` RPC function match what n8n's native Supabase Vector Store node expects, plus adding a pre-delete step by `file_id` before re-indexing Drive files so you don't get duplicate chunks.
2. Native n8n AI Agent and Google tools: replacing any fragile custom Code nodes with native n8n nodes (`Tools Agent`, `Supabase Vector Store`, `Google Calendar`, `Gmail`, `Google Drive`), adding `-from:me` filters on Gmail triggers to prevent reply loops, and locking the timezone offset on Calendar tool calls.
3. Short maintenance docs: a simple 1-page guide per workflow explaining what each node group does, how to re-authenticate Google OAuth if a token expires, and how to test changes safely.

I'm good with the $30 fixed price for the whole task and can have it tested and documented within 24 hours after NDA and access.

Best,
Ayman
