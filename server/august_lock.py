import pysmartthings
import logging

logger = logging.getLogger(__name__)

async def get_devices(session, token):
  api = pysmartthings.SmartThings(session, token)
  return await api.devices()

async def get_lock(session, token):
  devices = await get_devices(session, token)
  for device in devices:
    if 'lock' in device.capabilities:
      logger.debug("Device %s has capabilities %s", device, device.capabilities)
      return device