from app.qa_service import QAService


def main() -> None:
    service = QAService()
    print("博物馆知识问答系统已启动。输入问题开始提问，输入 exit / quit / 退出 结束。")
    print("示例：唐代有哪些文物？ / 这件文物的材质是什么？ / 和某件文物相似的文物有哪些？")

    try:
        while True:
            question = input("\n请输入问题> ").strip()
            if not question:
                continue
            if question.lower() in {"exit", "quit", "q"} or question in {"退出", "结束"}:
                print("已退出。")
                break

            token_gen, meta = service.ask_stream(question)
            print("\n回答：", end="", flush=True)
            for token in token_gen:
                print(token, end="", flush=True)
            print()

            # 打印其他信息（来源、相关文物、置信度）
            lines = ["", f"置信度：{meta.confidence:.2f}"]
            if meta.sources:
                lines.append("")
                lines.append("来源：")
                for idx, source in enumerate(meta.sources, 1):
                    suffix = f" - {source.detail}" if source.detail else ""
                    object_id = f" ({source.object_id})" if source.object_id else ""
                    lines.append(f"{idx}. [{source.type}] {source.title}{object_id}{suffix}")

            if meta.related_artifacts:
                lines.append("")
                lines.append("相关文物：")
                for idx, artifact in enumerate(meta.related_artifacts[:8], 1):
                    reason = []
                    if artifact.period:
                        reason.append(f"时期：{artifact.period}")
                    if artifact.material:
                        reason.append(f"材质：{artifact.material}")
                    if artifact.artifact_type:
                        reason.append(f"品类：{artifact.artifact_type}")
                    reason_text = "；".join(reason)
                    lines.append(f"{idx}. {artifact.title} ({artifact.object_id}) {reason_text}")

            print("\n".join(lines))
    finally:
        service.close()


if __name__ == "__main__":
    main()
