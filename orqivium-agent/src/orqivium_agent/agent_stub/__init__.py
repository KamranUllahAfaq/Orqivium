"""Client-safe import root for Orqivium Agent Stub code.

The package intentionally avoids eager imports so sandbox CLI users can import
``orqivium_agent.agent_stub`` without pulling in FastAPI, Redis, JWE, or other
server-only dependencies. Import server helpers from ``orqivium_agent.agent_stub.server``
explicitly when running or embedding the stub server.
"""

__all__: list[str] = []
