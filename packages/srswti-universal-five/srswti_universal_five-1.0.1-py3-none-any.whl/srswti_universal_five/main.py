import asyncio
import websockets
from .speech import SRSWTISpeech
from .signup import SRSWTISignup
from .home import SRSWTIHome
from .stt_socket import SRSWTISTT

async def main():
    servers = []
    servers.append(await websockets.serve(SRSWTISpeech().handle_reverse_websocket, "localhost", 8765))
    servers.append(await websockets.serve(SRSWTISignup().handle_signup_websocket, "localhost", 8766))
    servers.append(await websockets.serve(SRSWTIHome().handle_home_websocket, "localhost", 8767))
    servers.append(await websockets.serve(SRSWTISTT().handle_stt_websocket, "localhost", 8768))
    await asyncio.gather(*(server.wait_closed() for server in servers))

if __name__ == "__main__":
    asyncio.run(main())