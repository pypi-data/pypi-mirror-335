from .auth import login
import getpass
import os


async def main():
    username = input("Username: ")
    password = getpass.getpass("Password: ")

    token = await login(username, password)
    os.environ["ACCESS_TOKEN"] = token.access_token
    print(f"export ACCESS_TOKEN={token.access_token}")


def run():
    import asyncio

    asyncio.run(main())


if __name__ == "__main__":
    run()
