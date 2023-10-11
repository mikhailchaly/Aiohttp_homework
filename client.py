import aiohttp
import asyncio


async def main():
    async with aiohttp.ClientSession() as session:
        # response = await session.post(
        #     "http://127.0.0.1:8080/advert",
        #         json={
        #             "title": "title_20",
        #             "description": "description_1",
        #             "owner": "owner_user_1",
        #         }
        # )
        # print(response.status)
        # print(await response.json())


        # response = await session.patch(
        #     "http://127.0.0.1:8080/advert/12",
        #         json={
        #             "title": "newffff",
        #             "description": "new_description_1",
        #             "owner": "owner_new_user_1",
        #         }
        # )
        # print(response.status)
        # print(await response.json())


        response = await session.get("http://127.0.0.1:8080/advert/12")
        print(response.status)
        print(await response.json())


        # response = await session.delete("http://127.0.0.1:8080/advert/5")
        # print(response.status)
        # print(await response.json())


asyncio.run(main())
