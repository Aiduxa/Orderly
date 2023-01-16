__all__ = ['get_db_latency', 'fetch_guild', 'fetch_user', 'get_guild_adembed', 'update_guild_adembed', 'update_guild_invite_url', 'update_guild_adchannel', 'create_guild', 'create_user', 'update_user_activity_ranks', 'update_user_server_messages', 'update_user_server_last_message']

from asyncpg.pool import Pool
from time import time
from json import loads, dumps
from datetime import datetime

from .errors import DBGuildNotFound, DBUserNotFound
from .default import Default


def json_to_dict(data) -> dict:
	return dict(loads(data))


async def get_db_latency(pool: Pool) -> float:
	old: float = time()

	async with pool.acquire() as conn:
		await conn.execute("SELECT now()")

	return time() - old


async def fetch_guild(pool: Pool, guild_id: str | int) -> dict:
	guild_id = int(guild_id)

	async with pool.acquire() as conn:
		try:
			data = dict(await conn.fetchrow("SELECT * FROM servers WHERE id = $1", guild_id))
		except:
			raise DBGuildNotFound

	return data


async def create_guild(pool: Pool, guild_id: str | int, **kwargs) -> None:
	guild_id = int(guild_id)

	async with pool.acquire() as conn:
		await conn.execute(f"UPDATE servers SET id = $1", guild_id)


async def update_guild_adchannel(pool: Pool, guild_id: str | int, channel_id: str | int) -> None:
	async with pool.acquire() as conn:
		await conn.execute(f"UPDATE servers SET ad_channel = $1 WHERE id = $2", str(channel_id), int(guild_id))


async def get_guild_adembed(pool: Pool, server_id: int, field: str = None) -> dict | str:
	query: str = "SELECT ad_embed FROM servers WHERE id = $1"

	if field:
			query = f"SELECT ad_embed::json->>'{field}' FROM servers WHERE id = $1"
	
	async with pool.acquire() as connection:
		if field:
			return dict(await connection.fetchrow(query, server_id))["?column?"]
		else:
			return loads(dict(await connection.fetchrow(query, server_id))["ad_embed"])

async def update_guild_adembed(pool: Pool, server_id: int, embed: dict) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET ad_embed = $2 WHERE id = $1", server_id, dumps(embed))


async def update_guild_invite_url(pool: Pool, server_id: int, url: str) -> None:
	async with pool.acquire() as connection:
		await connection.execute("UPDATE servers SET guild_invite_url = $2 WHERE id = $1", server_id, url)


async def fetch_user(pool: Pool, user_id: str | int) -> dict:
	user_id = int(user_id)

	async with pool.acquire() as conn:
		try:
			data = dict(await conn.fetchrow("SELECT * FROM users WHERE id = $1", user_id))
		except:
			raise DBUserNotFound

	for key, value in data.items():
		if key in ["activity_ranks", "servers_messages", "servers_last_message"]:
			try:
				value = json_to_dict(value)
			except:
				value = {}

			data[key] = value

	return data


async def create_user(pool: Pool, user_id: str | int) -> dict:
	user_id = int(user_id)

	async with pool.acquire() as conn:
		await conn.execute("INSERT INTO users (id) VALUES ($1)", user_id)

	return await fetch_user(pool, user_id)


async def update_user_activity_ranks(pool: Pool, user_id: str | int, server_id: str | int, new_server_activity_rank: int, user_data: dict = None) -> None:
	user_id = int(user_id)
	server_id = str(server_id)

	if user_data == None:
		try:
			user_data = await fetch_user(pool, user_id)
		except DBUserNotFound:
			user_data = await create_user(pool, user_id)

	activity_ranks = user_data["activity_ranks"]

	activity_ranks[server_id] = new_server_activity_rank

	async with pool.acquire() as conn:
		await conn.execute("UPDATE users SET activity_ranks = $1 WHERE id = $2", dumps(activity_ranks), user_id)


async def update_user_server_messages(pool: Pool, user_id: str | int, server_id: str | int, new_messages: int, user_data: dict = None) -> None:
	user_id = int(user_id)
	server_id = str(server_id)

	if user_data == None:
		try:
			user_data = await fetch_user(pool, user_id)
		except DBUserNotFound:
			user_data = await create_user(pool, user_id)

	servers_messages = user_data["servers_messages"]

	servers_messages[server_id] = new_messages

	async with pool.acquire() as conn:
		await conn.execute("UPDATE users SET servers_messages = $1 WHERE id = $2", dumps(servers_messages), user_id)


async def update_user_server_last_message(pool: Pool, user_id: str | int, server_id: str | int, last_message: str | datetime, user_data: dict = None) -> None:
	user_id = int(user_id)
	server_id = str(server_id)
	last_message = datetime.strftime(last_message, Default.FORMAT)

	if user_data == None:
		try:
			user_data = await fetch_user(pool, user_id)
		except DBUserNotFound:
			user_data = await create_user(pool, user_id)

	servers_last_message = user_data["servers_last_message"]

	servers_last_message[server_id] = last_message

	async with pool.acquire() as conn:
		await conn.execute("UPDATE users SET servers_last_message = $1 WHERE id = $2", dumps(servers_last_message), user_id)