import asyncio
import winsdk.windows.devices.geolocation as wdg

async def getCoords():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return [pos.coordinate.latitude, pos.coordinate.longitude]

async def getAddr():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    return pos.civic_address

def getUserCoords():
    try:
        return asyncio.run(getCoords())
    except PermissionError:
        print("ERROR: You need to allow applications to access you location in Windows settings")

def getUserAddress():
    try:
        addr = asyncio.run(getAddr())
        return {
            "country": addr.country,
            "city": addr.city,
            "postalcode": addr.postal_code,
            "state": addr.state,
        }
    except PermissionError:
        print("ERROR: You need to allow applications to access you location in Windows settings")

async def getLoc():
    locator = wdg.Geolocator()
    pos = await locator.get_geoposition_async()
    caddr = pos.civic_address
    address = {
            "country": caddr.country,
            "city": caddr.city,
            "postalcode": caddr.postal_code,
            "state": caddr.state,
        }
    return {
        "long": pos.coordinate.longitude,
        "lat": pos.coordinate.latitude,
        "civivaddress": address
    }

def getUserLocation():
    try:
        #return asyncio.run(getCoords())
        return {}
    except PermissionError:
        print("ERROR: You need to allow applications to access you location in Windows settings")