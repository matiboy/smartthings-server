import argparse
import logging
import sys
from aiohttp import web
import aiohttp
import asyncio

from august_lock import get_lock

routes = web.RouteTableDef()
logger = None
TOKEN = ''
API_KEY = ''

@routes.get('/')
async def hello(request):
  return {"hello": "Welcome to Mat & Audry's"}

async def load_lock(session):
  try:
    lock = await get_lock(session, TOKEN)
  except aiohttp.client.ClientResponseError as ex:
    logger.debug("Failed to get lock with status %s", ex.status)
    if ex.status == 401:
      raise web.HTTPForbidden(text="Invalid Smartthings token")
    raise ex
  if not lock:
    raise web.HTTPServiceUnavailable(text="No device with locking capabilities found")
  return lock

async def refresh_lock(lock):
  await lock.status.refresh()
  return {"status": lock.status.lock}

async def process_lock(unlock):
  async with aiohttp.ClientSession() as session:
    lock = await load_lock(session)
    fn = lock.unlock
    if not unlock:
      logger.debug("Locking")
      fn = lock.lock
    await fn()
    await asyncio.sleep(5)
    return await refresh_lock(lock)

@routes.get('/open')
async def open_lock(_):
  return await process_lock(unlock=True)

@routes.get('/close')
async def open_lock(_):
  return await process_lock(unlock=False)

@routes.get('/status')
async def get_lock_status(_):
  async with aiohttp.ClientSession() as session:
    lock = await load_lock(session)
    return await refresh_lock(lock)

@web.middleware
async def all_json(request, handler):
  response = await handler(request)
  return web.json_response(response)

@web.middleware
async def api_key_auth(request, handler):
  logger.debug(API_KEY, request.headers)
  if request.headers.get('API-Key') != API_KEY:
    raise web.HTTPForbidden(text="Invalid API key")
  return await handler(request)


if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='SmartThings server')
  parser.add_argument('--token', dest='token', type=str,
                      help='SmartThings API token')
  parser.add_argument('--api-key', dest='key',
                      help='API key to authenticate to this server')
  parser.add_argument('--port', dest='port', default=8001,
                      help='Port to listen on')
  parser.add_argument('--debug', dest='debug', action='store_true',
                      help='Set logging level to debug')

  args = parser.parse_args()

  # Set up logging
  if args.debug:
    logging.basicConfig(level=logging.DEBUG)
    logging.debug("Logging set to debug level")
  logger = logging.getLogger(__name__)
  # Checks before starting
  if not args.token:
    logger.critical("SmartThings token not provided, shutting down")
    sys.exit(1)
  if not args.key:
    logger.critical("Missing API Key, server would be open. Shutting down")
    sys.exit(1)

  API_KEY = args.key
  TOKEN = args.token


  app = web.Application(middlewares=[api_key_auth, all_json])
  app.add_routes(routes)
  web.run_app(app, port=args.port)

