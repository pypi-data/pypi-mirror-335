# client_first_mcp.py
import asyncio
import os

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()
# Créer les paramètres pour une connexion stdio
server_params = StdioServerParameters(
    command="uvx",  # Exécutable
    args=["twilio-manager-mcp"],  # Arguments de ligne de commande
    env={
        "TWILIO_ACCOUNT_SID": os.getenv("TWILIO_ACCOUNT_SID", ""),
        "TWILIO_AUTH_TOKEN": os.getenv("TWILIO_AUTH_TOKEN", ""),
    },
)


async def run():
    print("Connexion au serveur MCP 'Mon Premier Serveur MCP'...")

    # Établir une connexion avec le serveur MCP
    async with stdio_client(server_params) as (read, write):
        # Créer une session client
        async with ClientSession(read, write) as session:
            # Initialiser la connexion
            await session.initialize()

            # Lister les outils disponibles
            tools = await session.list_tools()
            print(f"\nOutils disponibles sur le serveur:")
            for tool in tools:
                print(f"- {tool}")

            # Appeler l'outil get_user_context avec l'ID 42
            print("\nRécupération des informations de l'utilisateur avec ID=42...")
            user_info = await session.call_tool("get_user_context", arguments={"id": 42})
            print(f"Informations utilisateur: {user_info}")

            # Appeler l'outil get_user_money
            print("\nRécupération des informations bancaires...")
            money_info = await session.call_tool("get_user_money")
            print(f"Informations bancaires: {money_info}")

            # Calculer le solde total
            if isinstance(money_info, dict):
                total = sum(money_info.values())
                print(f"Solde total: {total} €")


if __name__ == "__main__":
    asyncio.run(run())
