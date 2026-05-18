# ==================== SSE 流式生成器 ====================
def _chat_stream_generator(data):
    """SSE 流式生成器 - 用于 /api/chat?stream=true"""
    import queue as q
    import threading
    import json
    from flask import Response

    token_queue = q.Queue()
    result_container = [None]
    error_container = [None]

    def callback(token):
        """LLM 流式回调：每收到一个 token 就放入队列"""
        if token:
            token_queue.put(token)

    def run_generation():
        """在线程中运行生成，完成后把结果放入 result_container"""
        try:
            from taiyi_llm_enhancer import get_enhancer, ReasoningMode
            enhancer = get_enhancer()

            message = data.get('message', '').strip()
            goal = data.get('goal')
            use_taiyi = data.get('use_taiyi_format', True)
            use_tool = data.get('use_tool', False)

            reasoning_mode = ReasoningMode.TOOL if use_tool else (
                ReasoningMode.TAIYI if use_taiyi else ReasoningMode.COT
            )

            response = enhancer.generate(
                question=message,
                goal=goal,
                reasoning_mode=reasoning_mode,
                use_taiyi_format=use_taiyi,
                enable_tool_call=use_tool,
                stream_callback=callback
            )
            result_container[0] = response
        except Exception as e:
            error_container[0] = str(e)
        finally:
            token_queue.put(None)  # 哨兵值：生成结束

    # 启动生成线程
    thread = threading.Thread(target=run_generation)
    thread.start()

    # 流式发送 token
    while True:
        token = token_queue.get()
        if token is None:
            break
        # SSE 格式：data: {...}\n\n
        try:
            yield f"data: {json.dumps({'token': token}, ensure_ascii=False)}\n\n"
        except Exception:
            pass

    # 等待线程结束
    thread.join()

    # 发送最终结果（含分析数据）
    if error_container[0]:
        yield f"data: {json.dumps({'done': True, 'error': error_container[0]}, ensure_ascii=False)}\n\n"
    elif result_container[0]:
        resp = result_container[0]
        analysis = {
            'unified_score': resp.unified_score,
            'taiyi_format': resp.taiyi_format,
            'formal_answer': resp.formal_answer[:300] if resp.formal_answer else '',
            'composite_answer': resp.composite_answer[:300] if resp.composite_answer else '',
            'unified_answer': resp.unified_answer[:300] if resp.unified_answer else '',
        }
        yield f"data: {json.dumps({'done': True, 'reply': resp.content, 'analysis': analysis}, ensure_ascii=False)}\n\n"
    else:
        yield f"data: {json.dumps({'done': True, 'error': '无响应'}, ensure_ascii=False)}\n\n"
