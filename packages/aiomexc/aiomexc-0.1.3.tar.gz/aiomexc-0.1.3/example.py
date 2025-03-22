import logging

from aiomexc import MexcClient, Credentials

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")

async def main():
    credentials = Credentials(
        access_key="mx0vglPOFUtoYJriFO",
        secret_key="03d5fee67c884e139f573ea835832d54",
    )

    client = MexcClient(credentials=credentials)

    r = await client.get_account_information()
    print(r)

    r = await client.delete_listen_key(listen_key="3f08f4ebf851f88693c7181ab9699dab3634ef3910ef4f8bc688d40a8513367d")
    print(r)

    await client.session.close()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
