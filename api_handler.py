import asyncio
import aiohttp
from typing import Dict
from config import DEFAULT_APIS
from utils import get_api_url, is_api_enabled, mongo

async def make_api_request(url: str, service: str) -> Dict:
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    # Remove developer fields
                    if "DEVELOPER" in data:
                        del data["DEVELOPER"]
                    if "developer" in data:
                        del data["developer"]
                    return data
                elif response.status == 404:
                    return {"error": "No data found (HTTP 404)"}
                else:
                    return {"error": f"API Error: HTTP {response.status}"}
    except asyncio.TimeoutError:
        return {"error": "Request timeout"}
    except aiohttp.ClientError as e:
        return {"error": f"Connection error: {str(e)}"}
    except Exception as e:
        return {"error": str(e)}

async def search_indian_number(number: str) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if len(number) < 10:
        return {"error": "Invalid number length"}
    
    blocked = mongo.get_blocked_number(number)
    if blocked:
        return {"error": f"Number blocked: {blocked.get('reason', 'Unknown')}"}
    
    if not is_api_enabled("num"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('num')}{number}"
    return await make_api_request(url, "num")

async def search_indian_aadhar(aadhar: str) -> Dict:
    aadhar = ''.join(filter(str.isdigit, aadhar))
    if len(aadhar) != 12:
        return {"error": "Invalid Aadhar length (12 digits required)"}
    if not is_api_enabled("aadhar"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('aadhar')}{aadhar}"
    return await make_api_request(url, "aadhar")

async def search_pak_number(number: str) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if len(number) < 10:
        return {"error": "Invalid Pakistan number"}
    if not is_api_enabled("pak_num"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('pak_num')}{number}"
    return await make_api_request(url, "pak_num")

async def search_pak_cnic(cnic: str) -> Dict:
    cnic = ''.join(filter(str.isdigit, cnic))
    if len(cnic) != 13:
        return {"error": "Invalid CNIC length (13 digits required)"}
    if not is_api_enabled("pak_cnic"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('pak_cnic')}{cnic}"
    return await make_api_request(url, "pak_cnic")

async def search_pak_police(number: str) -> Dict:
    number = ''.join(filter(str.isdigit, number))
    if not is_api_enabled("pak_police"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('pak_police')}{number}"
    return await make_api_request(url, "pak_police")

async def search_gst_billing(gstin: str) -> Dict:
    gstin = gstin.strip().upper()
    if len(gstin) != 15:
        return {"error": "Invalid GSTIN length (15 characters required)"}
    if not is_api_enabled("gst_billing"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('gst_billing')}{gstin}"
    return await make_api_request(url, "gst_billing")

async def search_pan_gst(pan: str) -> Dict:
    pan = pan.strip().upper()
    if len(pan) != 10:
        return {"error": "Invalid PAN length (10 characters required)"}
    if not is_api_enabled("pan_gst"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('pan_gst')}{pan}"
    return await make_api_request(url, "pan_gst")

async def search_aadhar_family(aadhar: str) -> Dict:
    aadhar = ''.join(filter(str.isdigit, aadhar))
    if len(aadhar) != 12:
        return {"error": "Invalid Aadhar length (12 digits required)"}
    if not is_api_enabled("aadhar_family"):
        return {"error": "API disabled by admin"}
    
    url = f"{get_api_url('aadhar_family')}{aadhar}"
    return await make_api_request(url, "aadhar_family")
