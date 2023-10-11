import json
from typing import Type

from aiohttp import web
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from models import engine, Advert, Session, Base
from schema import CreateAdvert, UpdateAdvert


app = web.Application()


def validate(schema: Type[CreateAdvert] | Type[UpdateAdvert], json_data: dict):
    try:
        model = schema(**json_data)
        validate_data = model.model_dump(exclude_none=True)
    except ValidationError as er:
        pass
    return validate_data


async def orm_context(app: web.Application):
    print("START")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()
    print("SHUT DOWN")


@web.middleware
async def session_middeleware(request: web.Request, handler):
    async with Session() as session:
        request["session"] = session
        response = await handler(request)
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middeleware)


async def get_advert(advert_id: int, session: Session):
    advert = await session.get(Advert, advert_id)
    if advert is None:
        raise web.HTTPNotFound(
            text=json.dumps({"error": "user not found"}),
            content_type="application/json",
        )
    return advert


class AdvertView(web.View):
    @property  # теперь с сессией можно работать как со свойством(без скобок)
    def session(
        self,
    ) -> Session:  # то есть self.session, это и есть то что возращает метод session
        return self.request["session"]

    @property
    def advert_id(self) -> int:
        return int(self.request.match_info["advert_id"])

    async def get(self):
        advert = await get_advert(self.advert_id, self.session)
        return web.json_response(
            {
                "id": advert.id,
                "title": advert.title,
                "description": advert.description,
                "owner": advert.owner,
                "creation_time": advert.creation_time.isoformat(),
            }
        )

    async def post(self):
        json_data = validate(CreateAdvert, await self.request.json())
        advert = Advert(**json_data)
        try:
            self.session.add(advert)
            await self.session.commit()
        except IntegrityError:
            raise web.HTTPConflict(
                text=json.dumps({"error": "advert already axists"}),
                content_type="application/json",
            )
        return web.json_response({"id": advert.id})

    async def patch(self):
        json_data = validate(UpdateAdvert, await self.request.json())
        advert = await get_advert(self.advert_id, self.session)
        for field, value in json_data.items():
            setattr(advert, field, value)
        try:
            self.session.add(advert)
            await self.session.commit()
        except IntegrityError:
            raise web.HTTPConflict(
                text=json.dumps({"error": "advert already axists"}),
                content_type="application/json",
            )
        return web.json_response({"id": advert.id})

    async def delete(self):
        advert = await get_advert(self.advert_id, self.session)
        await self.session.delete(advert)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.post("/advert", AdvertView),
        web.get("/advert/{advert_id}", AdvertView),
        web.patch("/advert/{advert_id}", AdvertView),
        web.delete("/advert/{advert_id}", AdvertView),
    ]
)

web.run_app(app)
