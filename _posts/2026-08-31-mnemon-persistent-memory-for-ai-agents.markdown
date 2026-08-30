---
title: "Mnemon: Persistent Project Memory for AI Coding Agents"
date: 2026-08-31 10:00:00 -0700
last_modified_at: 2026-08-31 10:00:00 -0700
categories: [ "article", "tech", "ai", "mcp", "python", "sqlite" ]
author: paulushc
license: CC-BY-4.0
layout: post
description: "How Mnemon gives AI coding agents a persistent brain using a two-layer SQLite memory architecture — session memory, knowledge graph, and MCP integration."
permalink: /articles/mnemon-persistent-memory-for-ai-agents
header:
  teaser: /assets/2026/08/mnemon-cover.png
  overlay_image: /assets/2026/08/mnemon-cover.png
  overlay_filter: 0.5
  show_overlay_excerpt: false
resources:
  - title: "Mnemon GitHub Repository"
    url: "https://github.com/paulushcgcj/mnemon"
    icon: "code"
  - title: "Model Context Protocol"
    url: "https://modelcontextprotocol.io"
    icon: "link"
  - title: "aiosqlite Documentation"
    url: "https://aiosqlite.omnilib.dev/en/stable/"
    icon: "link"
  - title: "FastMCP — MCP Server Framework"
    url: "https://github.com/jlowin/fastmcp"
    icon: "code"
---

Mnemon is a local MCP server that gives AI coding agents persistent project memory. It stores branch-scoped session state and project-scoped knowledge in SQLite, then exposes that information through MCP tools and a CLI.

The goal is straightforward: a new coding session should begin with the project context, active work, and recorded decisions that Mnemon already knows—not with an empty conversation.

<!--more-->

## Why a new session starts from zero

An agent can use context from its current conversation, but that context is not automatically a durable project record. When a new session starts, the agent can inspect the repository, but it does not necessarily know which decisions were made, which task is blocked, or why a directory should not be changed.

That missing context is practical rather than abstract. A developer may need to re-explain:

- Which branch they're on and why
- What architectural decisions were made in the last sprint
- Which components depend on which
- What tasks are in progress, blocked, or completed
- What they learned from the last bug they fixed
- Which files are important and why

## The model: session memory plus project memory

Mnemon separates information that changes with active work from information that describes the project more generally. Both layers use one SQLite database at `~/.agent-memory/mnemon.db`.

**Session memory** is persistent and branch-scoped rather than ephemeral. It includes branch focus, tasks and their lifecycle, branch-specific decisions, global decisions, and session summaries. Switching branches changes which branch-scoped state is read, while the records remain stored in SQLite.

**Project memory** is the knowledge graph. It stores project-level entities, observations, and typed relationships. An entity can optionally have a branch filter, but entity names are unique within a project rather than independently duplicated for every branch.

![Mnemon's two-layer memory architecture: an AI or MCP client calls the Mnemon server, which reads and writes session memory and a knowledge graph in SQLite.](/assets/2026/08/memory/mnemon-two-layer-memory.png){: width="1406" height="446"}
> Diagram by Paulo Cruz, CC-BY-4.0.

The separation answers two different questions:

- Session memory: “What am I working on in this branch?”
- Project memory: “What exists in this project, and how is it related?”

## What the knowledge graph stores

An **entity** is something worth remembering: a component such as `PaymentService`, a concept such as a rate-limiting strategy, a file, a person, or a system. Each entity has a type, a name, and an importance score from 0.0 to 1.0.

**Observations** are normally appended rather than updated in place. They can also be explicitly deleted, so they are not an immutable audit history. If a fact changes, an agent can delete the stale observation and add a replacement.

**Relationships** are directed and typed. Mnemon includes relationship types such as `calls`, `implements`, `depends_on`, `owns`, `uses`, `extends`, and `triggers`, while also allowing custom types. A `calls` relationship from `OrderService` to `PaymentService` records the direction of that relationship.

During automatic context assembly, Mnemon applies an importance threshold of `0.4` and caps the graph contribution at 15 entities. This keeps the session-start context focused rather than dumping every recorded file, function, or component into the conversation.

## What happens when a session starts

The session-start path is the main user journey:

1. **Global project context** — the high-level description of what this project is
2. **Global decisions** — architectural decisions that apply everywhere, not just one branch
3. **Knowledge graph entities** — grouped by type and filtered by importance
4. **Branch focus** — what this specific branch is about, what the next steps are
5. **Branch decisions** — decisions scoped to this branch
6. **Tasks** — with status icons (todo, in-progress, blocked, done)
7. **Recent sessions** — what happened in previous sessions on this branch

The agent requests this context through `memory_read(project_id, branch)`. Mnemon derives the project identifier from the final two path components of the Git `origin` remote and detects the current branch with:

```bash
git rev-parse --abbrev-ref HEAD
```

The result is a Markdown context block that the MCP client can provide to the agent before work begins.

![Mnemon session lifecycle: a new session detects the project and branch, reads stored context, injects it into the agent, then records work through a summary or update.](/assets/2026/08/memory/mnemon-session-context-flow.png){: width="1306" height="451"}
> Diagram by Paulo Cruz, CC-BY-4.0.

## Branches, projects, and hierarchy

Mnemon supports parent-child project relationships for repositories that contain multiple services or related projects. Direct children can be listed with `project_list_children`; recursive descendants can be listed with `project_list_tree`.

The implementation uses SQLite `WITH RECURSIVE` CTEs to traverse the hierarchy. Cycle prevention happens before a proposed parent change is written: an ancestor query rejects self-parenting and ancestor cycles. The descendant queries themselves are traversal queries, not independent cycle detectors.

Project identity and branch detection come from Git context, while hierarchy operations let a developer inspect how projects relate. This makes the feature useful for monorepos without requiring a separate project registry.

## SQLite and the async boundary

The data layer uses `aiosqlite`. Mnemon opens managed SQLite connections asynchronously, enables WAL mode and foreign-key enforcement on those connections, and awaits database operations without blocking the event loop in the same way a synchronous call would.

This is an integration boundary rather than a guarantee of unrestricted database parallelism. Async operations avoid synchronous event-loop blocking, but SQLite still controls locking and concurrency.

WAL (Write-Ahead Logging) and foreign-key enforcement are enabled by Mnemon on each managed connection. WAL can allow readers to proceed while SQLite handles a write, but it does not remove SQLite's locking model.

The schema bootstrap uses idempotent DDL such as `CREATE TABLE IF NOT EXISTS` and `CREATE INDEX IF NOT EXISTS`. Re-running the current bootstrap is designed to be safe for existing objects; it is not a versioned migration system and does not provide rollback history.

## MCP and CLI interfaces

Mnemon exposes 15 tools through the Model Context Protocol, built with FastMCP. They cover reading context, persisting session work, maintaining the graph, and navigating projects:

- `memory_read` — the session-start brain dump
- `memory_summarize` — persist session-end summary, decisions, and task updates
- `memory_task_update` — update task status
- `memory_project_set_context` — update global project context
- `memory_log_commit` — record a commit in session history
- `memory_project_list` — list projects
- `project_set_parent` — set a project's parent
- `project_list_children` — list direct children
- `project_list_tree` — list descendants recursively
- `graph_entity_upsert` — create or update an entity
- `graph_observe` — add an observation
- `graph_relate` — add a typed relationship
- `graph_search` — search entity names and observations
- `graph_read` — read graph entities, observations, and relations
- `graph_forget` — delete graph records

The CLI is the human-facing entry point. `mnemon serve` starts the MCP server, while commands such as `read`, `graph`, and `prune` inspect or maintain local memory. Commit logging is available through `mnemon log-commit` and is intended to be usable from a Git hook; the current release does not install that hook automatically.

The `mnemon install` command copies a `SKILL.md` file to `.github/skills/mnemon/` in your repo. This tells the AI agent how to interact with the memory system — which tools to call, when to read, when to write, and how to format the data it stores. It's the bridge between the agent's understanding and Mnemon's API.

## Trade-offs and boundaries

Mnemon chooses a small local system over a broader infrastructure footprint.

**No vector search.** Entity search uses SQL `LIKE` queries rather than embeddings. That avoids an embedding model and vector database, but it also means search is based on stored text rather than semantic similarity.

**Single-file SQLite.** All projects share one local database by default. The default path is `~/.agent-memory/mnemon.db`, and `MNEMON_DB_PATH` can change it. The reviewed design is local-first and single-user; it does not provide replication, shared team memory, or cloud synchronization.

**Observations are append-oriented.** New facts are added rather than replacing existing rows in place, but records can be deleted. That gives agents an explicit correction path without claiming immutable history.

**Memory still depends on updates.** Mnemon reads and writes a live local SQLite database for its operations. Git supplies project and branch context, but the knowledge graph is not reconstructed automatically from repository files. If agents do not update the records, stored context can drift from the codebase.

These boundaries make Mnemon a reasonable fit for a developer who wants inspectable local memory and MCP integration without operating another service. They are less suitable if the requirement is shared, replicated, semantically searched team memory.

## Getting Started

Mnemon requires Python 3.11+. Install with uv:

```bash
uv tool install mnemonn
```

Initialize memory for your current repository:

```bash
mnemon init
mnemon install
```

Start the MCP server for agent integration:

```bash
mnemon serve
```

Or inspect your memory directly:

```bash
mnemon read
mnemon graph
mnemon prune --importance-below 0.3 --older-than-days 30
```

The package distribution is named `mnemonn`, while the installed executable is `mnemon`. Mnemon requires Python 3.11 or newer and has no external service requirement; its Python dependencies are installed with the package.

The database lives at `~/.agent-memory/mnemon.db` unless `MNEMON_DB_PATH` changes the location. It can be backed up or inspected with a SQLite client.

---

## Who Mnemon is for

Mnemon is for developers who want a new AI coding session to begin with durable project and branch context, while keeping that memory local and inspectable.

It is not a replacement for source control, documentation, or team collaboration infrastructure. Its value depends on agents and developers recording useful decisions, tasks, observations, and summaries as work progresses.

Mnemon is open source under the MIT license. The full source code is available on [GitHub](https://github.com/paulushcgcj/mnemon).
