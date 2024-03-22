from sqlalchemy import select, and_, delete
from sqlalchemy.orm import selectinload
from typing import List
from datetime import datetime
from src.database.models import Url, UrlRecheckRequest
from sqlalchemy.ext.asyncio import AsyncSession
import pytz

class AsyncDatabaseManager:
    _instance = None
    _is_initialized = False

    def __new__(cls, async_session=None, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(AsyncDatabaseManager, cls).__new__(cls)
        return cls._instance


    def __init__(self, async_session: AsyncSession = None, *args, **kwargs):
        if not self._is_initialized:
            if not async_session:
                raise ValueError('AsyncDatabaseManager must be initialized with an async session first.')
            self.async_session = async_session
            self._is_initialized = True


    async def create_url(self, url_string: str, is_valid: bool) -> Url:
        async with self.async_session() as session:
            url = Url(url_string=url_string, is_valid=is_valid)
            session.add(url)
            await session.commit()
            return url


    async def get_url_with_id(self, url_id: str) -> Url:
        async with self.async_session() as session:
            query = select(Url).filter(Url.id == url_id).options(selectinload(Url.recheck_request))
            result = await session.execute(query)
            url = result.scalars().first()
            return url if url else None
    

    async def get_urls(self, 
                       only_valids=False, 
                       only_unvalids=False, 
                       only_with_recheck_request=False, 
                       only_with_out_recheck_request=False,
                       only_after: datetime = None,
                       only_before: datetime = None) -> List[Url]:
        async with self.async_session() as session:
            query = select(Url)
            
            if only_valids:
                query = query.filter(Url.is_valid == True)
            if only_unvalids:
                query = query.filter(Url.is_valid == False)
            if only_with_recheck_request:
                query = query.filter(Url.recheck_request.has())
            if only_with_out_recheck_request:
                query = query.filter(~Url.recheck_request.has())

            if only_after and only_before:
                query = query.filter(and_(Url.checked_date > only_after, Url.checked_date < only_before))
            elif only_after:
                query = query.filter(Url.checked_date > only_after)
            elif only_before:
                query = query.filter(Url.checked_date < only_before)

            query = query.options(selectinload(Url.recheck_request))

            result = await session.execute(query)
            urls = result.scalars().all()
            return urls
    

    async def create_recheck_request(self, from_user_id: str, url_id: int) -> UrlRecheckRequest:
        async with self.async_session() as session:
            url_query = select(Url).filter(Url.id == url_id)
            url_result = await session.execute(url_query)
            url = url_result.scalars().first()

            if not url:
                return None

            recheck_request = UrlRecheckRequest(from_user_id=from_user_id, url_id=url_id)
            session.add(recheck_request)
            await session.commit()
            await session.refresh(recheck_request)

            recheck_request.url = url

            return recheck_request
    
    async def get_recheck_request_with_id(self, recheck_request_id: int) -> UrlRecheckRequest:
        async with self.async_session() as session:
            query = select(
                UrlRecheckRequest
                ).filter(
                    UrlRecheckRequest.id == recheck_request_id
                    ).options(selectinload(UrlRecheckRequest.url))
            result = await session.execute(query)
            recheck_request = result.scalars().first()
            return recheck_request
    

    async def get_recheck_requests(self, from_user_id: str = None,
                                only_checked: bool = False,
                                only_not_checked: bool = False,
                                only_new_valid: bool = False,
                                only_new_unvalid: bool = False,
                                only_request_date_after: datetime = None,
                                only_checked_date_after: datetime = None) -> List[UrlRecheckRequest]:
        async with self.async_session() as session:
            query = select(
                UrlRecheckRequest
                ).options(
                    selectinload(
                        UrlRecheckRequest.url
                        ))

            if from_user_id:
                query = query.filter(UrlRecheckRequest.from_user_id == from_user_id)
            if only_checked:
                query = query.filter(UrlRecheckRequest.is_checked == True)
            if only_not_checked:
                query = query.filter(UrlRecheckRequest.is_checked == False)
            if only_new_valid:
                query = query.filter(and_(UrlRecheckRequest.is_checked == True, UrlRecheckRequest.new_is_valid == True))
            if only_new_unvalid:
                query = query.filter(and_(UrlRecheckRequest.is_checked == True, UrlRecheckRequest.new_is_valid == False))
            if only_request_date_after:
                query = query.filter(UrlRecheckRequest.request_date > only_request_date_after)
            if only_checked_date_after:
                query = query.filter(and_(UrlRecheckRequest.is_checked == True, UrlRecheckRequest.checked_date > only_checked_date_after))

            result = await session.execute(query)
            recheck_requests = result.scalars().all()
            return recheck_requests
    

    async def update_recheck_request(self, recheck_request_id: int, new_is_valid: bool) -> UrlRecheckRequest:
        async with self.async_session() as session:
            query = select(
                UrlRecheckRequest
                ).filter(
                    UrlRecheckRequest.id == recheck_request_id
                    ).options(
                        selectinload(UrlRecheckRequest.url)
                    )
            result = await session.execute(query)
            recheck_request = result.scalars().first()
            
            if recheck_request is None:
                return None
            
            recheck_request.new_is_valid = new_is_valid
            recheck_request.is_checked = True
            recheck_request.checked_date = datetime.now(pytz.timezone('Asia/Tehran'))

            await session.commit()
            await session.refresh(recheck_request)
            
            return recheck_request
    

    async def delete_url(self, url_id: int) -> bool:
        async with self.async_session() as session:
            url_query = select(Url).filter(Url.id == url_id)
            url_result = await session.execute(url_query)
            url = url_result.scalars().first()
            
            if not url:
                return False
            
            await session.delete(url)
            await session.commit()
            
            return True
        

    async def delete_all_url(self) -> None:
        async with self.async_session() as session:
            await session.execute(delete(Url))
            await session.commit()

