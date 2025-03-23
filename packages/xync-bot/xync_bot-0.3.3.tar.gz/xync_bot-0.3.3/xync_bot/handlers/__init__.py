from aiogram.types import User
from aiogram.utils.web_app import WebAppUser
from xync_schema import models


async def user_upsert(u: User | WebAppUser, blocked: bool = None) -> tuple[User, bool]:
    user_in: models.User.Upd = await models.User.tg2in(u, blocked)
    return await models.User.update_or_create(user_in.model_dump(exclude_none=True, exclude={"id"}), id=u.id)
