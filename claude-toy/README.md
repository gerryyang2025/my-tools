# Claude Toy — AI Coding Agent Control-Flow Example

`claude-toy` is a **full AI Coding Agent control-flow program** that demonstrates how to implement the loop “user question → model thinks → call tools → observe results → continue or end” with OpenAI API + Function Calling. It is suitable as a reference for understanding the agent main loop, tool calls, and conversation history.

---

## Principles: Why AI Coding Agents Look Like This

Whether you use Claude Code, Cursor, or Cline, after a while you notice a very stable shared pattern:

- You state a goal.
- The system reads some code or environment info.
- The model produces a “next action”.
- If that action needs to touch the outside world, it invokes a tool.
- When the tool finishes, its result is fed back to the model.
- The cycle repeats; humans can step in at any point.

This continues until the model decides “the task is done.” One crucial point: **the system itself does not know whether the task is done.** The stopping condition is not decided by program logic; it is the LLM choosing, in some response, not to call any more tools.

From an engineering perspective, if you try to describe any AI Coding Agent’s behavior in pseudo-code, it almost always collapses to something like:

```
while not done:
    observation = collect_context()
    action = llm(observation)
    if action is tool_call:
        result = execute(action)
        append_to_context(result)
    else:
        done = True
```

This is not one product’s implementation choice—it is the natural shape of all such systems.

The reason is simple: as long as the “decision logic” lives inside the model and the LLM is stateless, the only way to simulate “ongoing thinking” is to keep replaying context. An agent is essentially **using a loop to simulate continuity.**

---

## Overview

| Module | Role |
|--------|------|
| **Tool definitions** | Four callable tools: run command, read file, write file, list directory |
| **Tool schemas** | Describe tool names, parameters, and descriptions in OpenAI Function Calling format |
| **Agent loop** | Outer REPL takes user input; inner loop runs Think → Act → Observe until a final reply |

Overall behavior: the user types a natural-language task; the model decides whether to call tools, which ones, and how to proceed from results, until it stops calling tools and returns a text reply.

---

## Control Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Outer loop (REPL)                                               │
│  User types "exit"/"quit"/"q" → exit; else append to messages     │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│  Inner loop (agent think / act / observe)                         │
│                                                                   │
│  1. Think  Call chat.completions.create(messages, tools)          │
│  2. If response has tool_calls:                                   │
│       → Run each tool_call’s local function in order              │
│       → Append results as role="tool" messages to messages       │
│       → Go back to step 1                                         │
│  3. If no tool_calls:                                             │
│       → Treat as final reply; print message.content; exit loop    │
└───────────────────────────────┬─────────────────────────────────┘
                                ▼
                         Back to outer loop, wait for next input
```

Main idea: **as long as the model keeps returning `tool_calls`, execution stays in the inner loop**, feeding each tool result back as a new message for multi-step “think → act → observe”.

---

## Tools

| Tool | Role | Notes |
|------|------|--------|
| `execute_bash` | Run shell command | For tests, installs, file ops; 30s timeout; output truncated after 2000 chars |
| `read_file` | Read file | Returns content with line numbers (for precise edits) |
| `write_file` | Write file | Create or overwrite; parent dirs created if missing |
| `list_files` | List directory | Recursive listing; skips dotfiles; up to 50 entries |

The code exposes both **callable functions** (`execute_bash`, `read_file`, etc.) and **OpenAI-style JSON schemas** (`TOOLS_SCHEMA`). `AVAILABLE_FUNCTIONS` maps names to implementations and is used to dispatch on `tool_call.function.name`.

---

## System Prompt and Guidelines

The system prompt sets the model as an “intelligent coding assistant” and defines:

1. **Inspect before editing**: Use `list_files` or `read_file` to understand project layout and file contents before changing code.
2. **Verify after editing**: After edits, run code or tests via `execute_bash` when possible.
3. **Style**: Keep answers short and focused on the task.

These guidelines are injected via `system_prompt` at the start of `messages` and apply for the whole session.

---

## API Config

API settings come from **`openai_config.json` in the same directory** (if present). Missing fields fall back to env vars or defaults. This file is in `.gitignore` so it is not committed and does not leak `api_key`. Use **`provider`** to choose the backend; all options use the same config file.

**First-time setup**: Install dependencies and prepare config (one-time):

```bash
cd claude-toy
./setup.sh
# Edit openai_config.json: set provider, api_key, base_url, model (see table below)
```

`setup.sh` installs dependencies from `claude-toy/requirements.txt` and, if `openai_config.json` is missing, copies from **`openai_config.sample.json`**. Edit the copied file to match your chosen provider.

**Provider combinations** (all in one `openai_config.json`):

| provider   | base_url                           | model          | notes |
|------------|-------------------------------------|----------------|-------|
| `openai`   | `https://api.openai.com/v1`         | `gpt-4o`       | OpenAI |
| `openai`   | `https://api.minimaxi.com/v1`       | `MiniMax-M2.1` | MiniMax (OpenAI API); [doc](https://platform.minimaxi.com/docs/api-reference/text-openai-api) |
| `anthropic`| `https://api.minimaxi.com/anthropic` | `MiniMax-M2.1` | MiniMax (Anthropic API, [recommended](https://platform.minimaxi.com/docs/api-reference/text-anthropic-api)) |

**`openai_config.json` fields**:

| Field | Description | Optional |
|-------|-------------|----------|
| `provider` | `"openai"` (default when omitted) or `"anthropic"` | Yes; or env `CLAUDE_TOY_PROVIDER`. If unset, treated as `openai` (OpenAI API path). |
| `api_key` | API key for the chosen provider | Yes; env `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` |
| `base_url` | API base URL; see table above per provider | Yes |
| `model` | Model name; see table above | Yes; env `CLAUDE_TOY_MODEL` |

---

## Dependencies and Run

- **Dependencies**: `openai` (OpenAI path) and `anthropic` (Anthropic path). Run `./setup.sh` from the `claude-toy` dir, or `pip install -r requirements.txt`.
- **Config**: Use `openai_config.json` in the same dir (see above), or set env vars `OPENAI_API_KEY` and optionally `CLAUDE_TOY_MODEL`.

Quick start:

```bash
cd claude-toy
./setup.sh          # install deps, copy openai_config.sample.json → openai_config.json if missing
# edit openai_config.json: provider, api_key, base_url, model
./claude-toy        # or: python claude-toy
```

At the REPL, type your task in natural language; type `exit`, `quit`, or `q` to exit.

**Usage example**

![claude-toy usage example](../asserts/claude_toy.png)

---

## Code Structure

The script is organized for readability and reuse:

**REPL (Read–Eval–Print Loop)**  
REPL stands for Read–Eval–Print Loop: (1) **Read** — read one line of user input from the terminal; (2) **Eval** — process it (in claude-toy: send to model + tool execution); (3) **Print** — print the result; (4) **Loop** — go back to Read. Common examples: Python’s `python`, Node’s `node`, Lisp REPLs. In claude-toy, the REPL is the outer loop: prompt `👤 You:`, read a line, run one agent turn (possibly with tool calls), print `🤖 Thinking` / `🤖 Reply`, then prompt again until the user types `exit` / `quit` / `q`.

| Layer | Role |
|-------|------|
| **Config** | Load `openai_config.json`; `_openai_client()`, `_anthropic_client()`, `_use_anthropic()`, `_is_minimax()` |
| **Tools** | `web_search`, `fetch_url`, `execute_bash`, `read_file`, `write_file`, `list_files` plus `run_tool(name, args)` as the single entry point used by both API paths |
| **Schemas** | `TOOLS_SCHEMA` (OpenAI), `AVAILABLE_FUNCTIONS`, `_anthropic_tools()` (derived from `TOOLS_SCHEMA`) |
| **REPL** | `_read_user_input() -> (content_or_None, exit_requested)`, `_print_banner()`, shared prompt constants |
| **Agent loops** | `_run_openai_loop()` and `_run_anthropic_loop(system_prompt)`; helpers `_openai_assistant_message_for_history()`, `_openai_thinking_text()` for MiniMax |
| **Entry** | `run_toy_claude()` chooses provider and runs the corresponding loop |

Constants such as `MAX_AGENT_ITERATIONS`, `MAX_TOKENS`, `PROMPT_USER`, `PROMPT_THINKING`, `PROMPT_REPLY`, `EXIT_COMMANDS` are defined in one place and reused.

---

## Implementation Notes

1. **Message layout**: `messages` contains `system`, `user`, `assistant`, and `tool` entries; each tool result is appended as a message with `role="tool"` and `tool_call_id` so the model can match calls to results.
2. **Tool dispatch**: Both OpenAI and Anthropic paths call `run_tool(name, args)`; it looks up `AVAILABLE_FUNCTIONS[name]` and returns the result string or an error message.
3. **Loop exit**: The inner loop exits when the model stops returning `tool_calls`; then the final reply is printed and the loop `break`s.

To extend with multi-agent flows, planning + execution, or other APIs, keep this Think → Act → Observe loop, add tools and schemas, and call `run_tool()` from the new path as needed.
