from typing import Any, Dict, Optional, TypeVar, Generic
import aiohttp
import asyncio
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class ApiResponse(Generic[T]):
    data: Optional[T]
    error: Optional[str]
    loading: bool

async def use_fetch(url: str, options: Dict[str, Any] = None) -> ApiResponse:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.request(
                method=options.get('method', 'GET'),
                url=url,
                headers=options.get('headers', {}),
                json=options.get('body')
            ) as response:
                data = await response.json()
                return ApiResponse(data=data, error=None, loading=False)
        except Exception as e:
            return ApiResponse(data=None, error=str(e), loading=False)
