from ..API.base import APIRegistryCMD

async def handle_api_command(api_name, nsfw, query, limit=1):
    api = APIRegistryCMD.get_api(api_name)
    if not api:
        raise ValueError(f"Unknown API: {api_name}")

    func = api['nsfw' if nsfw else 'sfw']

    if query:
        return await func(tag=query, limit=limit)
    else:
        return await func(limit=limit)

async def handle_tags_command(api_name):
    handler = APIRegistryCMD.get_tag_handler(api_name)
    if not handler:
        raise ValueError(f"Tag retrieval not supported for {api_name}")
    
    return await handler()
