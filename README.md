# My Tools

A collection of AI-related tools and utilities.

## 📦 Tools

- **[claude-toy](claude-toy/README.md)** — AI Coding Agent control-flow example. Implements the loop “user question → model thinks → call tools → observe results” with OpenAI API or Anthropic API (e.g. MiniMax). REPL-style: type natural-language tasks, get tool-augmented replies. Suitable as a reference for agent main loop, tool calls, and conversation history.

- **[cursor-usage](cursor-usage/README.md)** — Python tool for analyzing Cursor API usage data. Provides insights into context size, token distribution, costs, and cache utilization. Accepts CSV usage exports; outputs visual dashboards (2×2 plots) and detailed text reports with recommendations.

- **[minimax-tts](minimax-tts/README.md)** — Python library for voice cloning and text-to-speech synthesis using the MiniMax API. Features include voice cloning from reference audio, TTS conversion with cloned voices, synchronous and async operation support, task management for audio retrieval, and CLI interface for quick testing.

- **[tencent-meeting](tencent-meeting/README.md)** — Python script to query Tencent Meeting info by Meeting Code and extract `meeting_id`. Configured via environment variables / local `.env` (secrets are not stored in source).

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).
