import asyncio
import json
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 允许 Dify 的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 常驻的 Stdio 进程管理
class StdioProcessManager:
    def __init__(self):
        self.proc = None
        self.queue = asyncio.Queue()

    async def start(self):
        if self.proc is None or self.proc.poll() is not None:
            self.proc = await asyncio.create_subprocess_exec(
                "uvx", "blender-mcp",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            asyncio.create_task(self._read_stdout())

    async def _read_stdout(self):
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            await self.queue.put(line.decode())

    async def write_stdin(self, data: str):
        if self.proc and self.proc.returncode is None:
            self.proc.stdin.write(data.encode())
            await self.proc.stdin.drain()

manager = StdioProcessManager()

@app.on_event("startup")
async def startup_event():
    await manager.start()

# 1. Dify 握手连接的本地端点 (GET /sse)
@app.get("/sse")
async def sse_endpoint(request: Request):
    session_id = str(uuid.uuid4())
    
    async def event_generator():
        # 发送初始化连接消息，并告知 Dify 后续发送控制命令的 POST 路由地址
        post_url = f"http://{request.headers.get('host')}/message?session_id={session_id}"
        yield f"event: endpoint\ndata: {post_url}\n\n"
        
        try:
            while True:
                try:
                    # 将 uvx blender-mcp 输出的标准流原封不动地通过 SSE 吐给 Dify
                    line = await asyncio.wait_for(manager.queue.get(), timeout=1.0)
                    yield f"event: message\ndata: {line.strip()}\n\n"
                except asyncio.TimeoutError:
                    if manager.proc.poll() is not None:
                        break
                    yield ": ping\n\n"
        except asyncio.CancelledError:
            pass

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 2. 接收 Dify 发送的控制指令并通过 Stdio 管道转发给客户端 (POST /message)
@app.post("/message")
async def message_endpoint(request: Request):
    body = await request.body()
    await manager.write_stdin(body.decode() + "\n")
    return "OK"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
