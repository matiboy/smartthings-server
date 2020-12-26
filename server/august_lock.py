import pysmartthings
import aiohttp

async def get_lock(session, token):
  api = pysmartthings.SmartThings(session, token)
  return await api.devices()