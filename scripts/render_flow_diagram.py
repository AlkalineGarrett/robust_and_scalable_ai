from __future__ import annotations

from pathlib import Path

from graphviz import Digraph


def build_diagram() -> Digraph:
    dot = Digraph(
        name="assignment_agent_flow",
        format="png",
        graph_attr={
            "rankdir": "TB",
            "splines": "ortho",
            "nodesep": "0.35",
            "ranksep": "0.45",
            "fontname": "Helvetica",
            "fontsize": "16",
            "labelloc": "t",
            "label": "Assignment_agent template.py – Flow",
        },
        node_attr={
            "shape": "box",
            "style": "rounded,filled",
            "fontname": "Helvetica",
            "fontsize": "11",
            "fillcolor": "#E8F1FF",
            "color": "#2F6FED",
            "penwidth": "1.2",
        },
        edge_attr={"color": "#4B5563", "penwidth": "1.1", "arrowsize": "0.8"},
    )

    def node(node_id: str, label: str, *, fill: str | None = None, color: str | None = None, shape: str | None = None):
        attrs: dict[str, str] = {}
        if fill is not None:
            attrs["fillcolor"] = fill
        if color is not None:
            attrs["color"] = color
        if shape is not None:
            attrs["shape"] = shape
        dot.node(node_id, label, **attrs)

    # Main flow
    node("start", "Start script", fill="#E5E7EB", color="#6B7280")
    node("env", "Load env vars\\nOPENAI_API_KEY (required)")
    node("emb", "Create embeddings\\nOpenAIEmbeddings()")
    node("faiss", "Load FAISS vector store\\nFAISS.load_local('.', embeddings)")
    node("retriever", "Create retriever\\nvector.as_retriever(k=5)")

    # Tools
    tool_fill = "#FFF7ED"
    tool_color = "#C2410C"
    node("tool_retr", "Create tool\\namazon_product_search", fill=tool_fill, color=tool_color)
    node("tool_web", "Create tool\\nTavilySearch(max_results=5)", fill=tool_fill, color=tool_color)
    node("tools", "Assemble tools list\\n[amazon_product_search, search_tavily]")

    node("prompt", "Create local ReAct PromptTemplate")
    node("llms", "Init LLMs\\nChatOpenAI(streaming=True)")
    node("agent", "Create ReAct agent\\ncreate_react_agent(llm, tools, prompt)")
    node("exec", "Wrap in AgentExecutor\\nmax_iterations=25\\nhandle_parsing_errors")
    node("session_dict", "Init session_memory dict", fill="#E5E7EB", color="#6B7280")
    node("getmem", "get_memory(session_id)\\nreturns ChatMessageHistory", fill="#E5E7EB", color="#6B7280")
    node("history", "Wrap with RunnableWithMessageHistory\\ninput='input'\\nhistory='chat_history'")
    node("ui", "Build Gradio UI\\nTextbox + Button")
    node("launch", "Gradio launched on\\n0.0.0.0:7860", fill="#F3F4F6", color="#6B7280")

    node("submit", "User submits message", fill="#E5E7EB", color="#6B7280")
    node("chat", "chat_with_agent(user_input, request)")
    node("sid", "Derive session_id\\nrequest.session_hash or 'default'", fill="#E5E7EB", color="#6B7280")
    node("invoke", "agent_with_chat_history.invoke\\n{input: user_input}")

    # Branch
    node("branch", "Response has 'output'?", shape="diamond", fill="#FEF3C7", color="#92400E")
    node("post", "Post-process iteration-limit message", fill="#E5E7EB", color="#6B7280")
    node("return_ok", "Return output to Gradio", fill="#DCFCE7", color="#15803D")
    node("return_err", "Return error string", fill="#FEE2E2", color="#B91C1C")

    # Edges
    dot.edges(
        [
            ("start", "env"),
            ("env", "emb"),
            ("emb", "faiss"),
            ("faiss", "retriever"),
            ("retriever", "tool_retr"),
            ("tool_retr", "tool_web"),
            ("tool_web", "tools"),
            ("tools", "prompt"),
            ("prompt", "llms"),
            ("llms", "agent"),
            ("agent", "exec"),
            ("exec", "session_dict"),
            ("session_dict", "getmem"),
            ("getmem", "history"),
            ("history", "ui"),
            ("ui", "submit"),
            ("submit", "chat"),
            ("chat", "sid"),
            ("sid", "invoke"),
            ("invoke", "branch"),
            ("post", "return_ok"),
        ]
    )

    dot.edge("ui", "launch", style="dashed")
    dot.edge("branch", "post", label="Yes")
    dot.edge("branch", "return_err", label="No")
    dot.edge("return_ok", "submit", style="dashed", color="#9CA3AF")
    dot.edge("return_err", "submit", style="dashed", color="#9CA3AF")

    return dot


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    out_dir = repo_root / "docs"
    out_dir.mkdir(parents=True, exist_ok=True)

    out_base = out_dir / "flow_diagram"
    dot = build_diagram()
    rendered_path = dot.render(str(out_base), cleanup=True)
    print(f"Wrote {rendered_path}")


if __name__ == "__main__":
    main()

