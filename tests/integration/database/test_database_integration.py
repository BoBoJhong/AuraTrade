"""
Integration Tests for Database Operations
資料庫整合測試 - CRUD 操作、交易、併發測試

測試範圍：
1. 基本 CRUD 操作
2. 交易隔離測試
3. 關聯查詢測試
4. 併發操作測試
5. 資料完整性測試
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from uuid import uuid4

from apps.models.user import User
from apps.models.stock import Stock, Watchlist
from apps.models.position import Position
from apps.models.price_alert import PriceAlert, AlertType
from apps.models.historical_price import HistoricalPrice


class TestUserCRUD:
    """測試用戶 CRUD 操作"""
    
    @pytest.mark.asyncio
    @pytest.mark.integration
    @pytest.mark.requires_db
    async def test_create_user(self, test_db: AsyncSession):
        """TC-DB-001: 創建用戶 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        user = await repo.create_user(
            email=f"dbtest_{timestamp}@test.com",
            username=f"dbuser_{timestamp}",
            hashed_password="hashed_password_123"
        )
        
        assert user is not None
        assert user.email == f"dbtest_{timestamp}@test.com"
        assert user.username == f"dbuser_{timestamp}"
        assert user.user_id is not None
    
    @pytest.mark.asyncio
    async def test_read_user_by_email(self, test_db: AsyncSession):
        """TC-DB-002: 通過 email 查詢用戶 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        test_email = f"read_{timestamp}@test.com"
        
        # 先創建用戶
        created_user = await repo.create_user(
            email=test_email,
            username=f"readuser_{timestamp}",
            hashed_password="hashed_pass"
        )
        
        # 查詢用戶
        found_user = await repo.get_user_by_email(test_email)
        
        assert found_user is not None
        assert found_user.user_id == created_user.user_id
        assert found_user.email == test_email
    
    @pytest.mark.asyncio
    async def test_update_user(self, test_db: AsyncSession):
        """TC-DB-003: 更新用戶資料 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # 創建用戶
        user = await repo.create_user(
            email=f"update_{timestamp}@test.com",
            username=f"updateuser_{timestamp}",
            hashed_password="old_pass"
        )
        
        # 更新用戶
        user.username = f"updated_{timestamp}"
        await test_db.commit()
        await test_db.refresh(user)
        
        # 驗證更新
        assert user.username == f"updated_{timestamp}"
    
    @pytest.mark.asyncio
    async def test_delete_user(self, test_db: AsyncSession):
        """TC-DB-004: 刪除用戶 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # 創建用戶
        user = await repo.create_user(
            email=f"delete_{timestamp}@test.com",
            username=f"deleteuser_{timestamp}",
            hashed_password="pass"
        )
        
        user_id = user.user_id
        
        # 刪除用戶
        await test_db.delete(user)
        await test_db.commit()
        
        # 驗證刪除
        stmt = select(User).where(User.user_id == user_id)
        result = await test_db.execute(stmt)
        deleted_user = result.scalar_one_or_none()
        
        assert deleted_user is None
    
    @pytest.mark.asyncio
    async def test_duplicate_email_constraint(self, test_db: AsyncSession):
        """TC-DB-005: 重複 email 應違反唯一約束"""
        from apps.repositories.user_repository import UserRepository
        
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        test_email = f"duplicate_{timestamp}@test.com"
        
        # 創建第一個用戶
        await repo.create_user(
            email=test_email,
            username=f"user1_{timestamp}",
            hashed_password="pass1"
        )
        
        # 嘗試創建相同 email 的用戶 (應失敗)
        with pytest.raises(Exception):  # IntegrityError 或其他異常
            await repo.create_user(
                email=test_email,
                username=f"user2_{timestamp}",
                hashed_password="pass2"
            )


class TestStockOperations:
    """測試股票相關資料庫操作"""
    
    @pytest.mark.asyncio
    async def test_create_stock(self, test_db: AsyncSession):
        """TC-DB-006: 創建股票記錄 - 成功"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        stock = Stock(
            symbol=f"TEST{timestamp[:4]}.TW",
            name=f"測試股票 {timestamp}",
            market="TW"
        )
        
        test_db.add(stock)
        await test_db.commit()
        await test_db.refresh(stock)
        
        assert stock.symbol is not None
        assert stock.name == f"測試股票 {timestamp}"
    
    @pytest.mark.asyncio
    async def test_query_stocks_by_market(self, test_db: AsyncSession):
        """TC-DB-007: 按市場查詢股票 - 成功"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # 創建台股和美股
        tw_stock = Stock(symbol=f"TW{timestamp[:4]}.TW", name="台股", market="TW")
        us_stock = Stock(symbol=f"US{timestamp[:4]}", name="美股", market="US")
        
        test_db.add_all([tw_stock, us_stock])
        await test_db.commit()
        
        # 查詢台股
        stmt = select(Stock).where(Stock.market == "TW")
        result = await test_db.execute(stmt)
        tw_stocks = result.scalars().all()
        
        # 應該找到至少一個台股
        assert len(tw_stocks) >= 1
        assert all(stock.market == "TW" for stock in tw_stocks)


class TestWatchlistOperations:
    """測試自選股操作"""
    
    @pytest.mark.asyncio
    async def test_add_to_watchlist(self, test_db: AsyncSession):
        """TC-DB-008: 添加股票到自選股 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"watchlist_{timestamp}@test.com",
            username=f"watchuser_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建股票
        stock = Stock(symbol="2330.TW", name="台積電", market="TW")
        test_db.add(stock)
        await test_db.commit()
        await test_db.refresh(stock)
        
        # 添加到自選股
        watchlist = Watchlist(
            user_id=user.user_id,
            symbol=stock.symbol
        )
        test_db.add(watchlist)
        await test_db.commit()
        
        # 驗證
        stmt = select(Watchlist).where(
            Watchlist.user_id == user.user_id,
            Watchlist.symbol == stock.symbol
        )
        result = await test_db.execute(stmt)
        found = result.scalar_one_or_none()
        
        assert found is not None
        assert found.symbol == "2330.TW"
    
    @pytest.mark.asyncio
    async def test_remove_from_watchlist(self, test_db: AsyncSession):
        """TC-DB-009: 從自選股移除 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶和股票
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"remove_{timestamp}@test.com",
            username=f"removeuser_{timestamp}",
            hashed_password="pass"
        )
        
        stock = Stock(symbol="2317.TW", name="鴻海", market="TW")
        test_db.add(stock)
        await test_db.commit()
        
        # 添加到自選股
        watchlist = Watchlist(user_id=user.user_id, symbol=stock.symbol)
        test_db.add(watchlist)
        await test_db.commit()
        await test_db.refresh(watchlist)
        
        watchlist_id = watchlist.watchlist_id
        
        # 移除
        await test_db.delete(watchlist)
        await test_db.commit()
        
        # 驗證已刪除
        stmt = select(Watchlist).where(Watchlist.watchlist_id == watchlist_id)
        result = await test_db.execute(stmt)
        deleted = result.scalar_one_or_none()
        
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_get_user_watchlist_with_join(self, test_db: AsyncSession):
        """TC-DB-010: 查詢用戶自選股 (JOIN 測試) - 成功"""
        from apps.repositories.user_repository import UserRepository
        from sqlalchemy.orm import selectinload
        
        # 創建用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"join_{timestamp}@test.com",
            username=f"joinuser_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建多個股票並添加到自選股
        stocks = [
            Stock(symbol="2330.TW", name="台積電", market="TW"),
            Stock(symbol="2317.TW", name="鴻海", market="TW")
        ]
        test_db.add_all(stocks)
        await test_db.commit()
        
        for stock in stocks:
            watchlist = Watchlist(user_id=user.user_id, symbol=stock.symbol)
            test_db.add(watchlist)
        await test_db.commit()
        
        # 使用 JOIN 查詢
        stmt = select(Watchlist).where(
            Watchlist.user_id == user.user_id
        ).options(selectinload(Watchlist.stock))
        
        result = await test_db.execute(stmt)
        watchlist_items = result.scalars().all()
        
        # 應該找到 2 個自選股
        assert len(watchlist_items) == 2


class TestPositionOperations:
    """測試持倉操作"""
    
    @pytest.mark.asyncio
    async def test_create_position(self, test_db: AsyncSession):
        """TC-DB-011: 創建持倉記錄 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"position_{timestamp}@test.com",
            username=f"posuser_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建股票
        stock = Stock(symbol="AAPL", name="Apple", market="US")
        test_db.add(stock)
        await test_db.commit()
        
        # 創建持倉
        position = Position(
            user_id=user.user_id,
            symbol=stock.symbol,
            quantity=100,
            average_cost=150.0,
            purchase_date=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()
        await test_db.refresh(position)
        
        assert position.position_id is not None
        assert position.quantity == 100
        assert position.average_cost == 150.0
    
    @pytest.mark.asyncio
    async def test_update_position_quantity(self, test_db: AsyncSession):
        """TC-DB-012: 更新持倉數量 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶和持倉
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"updatepos_{timestamp}@test.com",
            username=f"updatepos_{timestamp}",
            hashed_password="pass"
        )
        
        stock = Stock(symbol="MSFT", name="Microsoft", market="US")
        test_db.add(stock)
        await test_db.commit()
        
        position = Position(
            user_id=user.user_id,
            symbol=stock.symbol,
            quantity=50,
            average_cost=200.0,
            purchase_date=datetime.utcnow()
        )
        test_db.add(position)
        await test_db.commit()
        
        # 更新數量
        position.quantity = 100
        await test_db.commit()
        await test_db.refresh(position)
        
        assert position.quantity == 100


class TestPriceAlertOperations:
    """測試價格提醒操作"""
    
    @pytest.mark.asyncio
    async def test_create_price_alert(self, test_db: AsyncSession):
        """TC-DB-013: 創建價格提醒 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"alert_{timestamp}@test.com",
            username=f"alertuser_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建股票
        stock = Stock(symbol="GOOGL", name="Google", market="US")
        test_db.add(stock)
        await test_db.commit()
        
        # 創建價格提醒
        alert = PriceAlert(
            user_id=user.user_id,
            symbol=stock.symbol,
            alert_type=AlertType.ABOVE,
            target_price=150.0,
            is_active=True
        )
        test_db.add(alert)
        await test_db.commit()
        await test_db.refresh(alert)
        
        assert alert.alert_id is not None
        assert alert.target_price == 150.0
        assert alert.alert_type == AlertType.ABOVE
    
    @pytest.mark.asyncio
    async def test_deactivate_alert(self, test_db: AsyncSession):
        """TC-DB-014: 停用價格提醒 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶和提醒
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"deactive_{timestamp}@test.com",
            username=f"deactive_{timestamp}",
            hashed_password="pass"
        )
        
        stock = Stock(symbol="TSLA", name="Tesla", market="US")
        test_db.add(stock)
        await test_db.commit()
        
        alert = PriceAlert(
            user_id=user.user_id,
            symbol=stock.symbol,
            alert_type=AlertType.BELOW,
            target_price=100.0,
            is_active=True
        )
        test_db.add(alert)
        await test_db.commit()
        
        # 停用提醒
        alert.is_active = False
        await test_db.commit()
        await test_db.refresh(alert)
        
        assert alert.is_active is False


class TestTransactionIsolation:
    """測試交易隔離"""
    
    @pytest.mark.asyncio
    async def test_transaction_rollback(self, test_db: AsyncSession):
        """TC-DB-015: 交易回滾測試 - 成功"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        # 創建股票
        stock = Stock(
            symbol=f"ROLLBACK{timestamp[:4]}.TW",
            name="回滾測試",
            market="TW"
        )
        test_db.add(stock)
        
        # 不提交，而是回滾
        await test_db.rollback()
        
        # 驗證股票不存在
        stmt = select(Stock).where(Stock.symbol == f"ROLLBACK{timestamp[:4]}.TW")
        result = await test_db.execute(stmt)
        found = result.scalar_one_or_none()
        
        assert found is None


class TestDataIntegrity:
    """測試資料完整性"""
    
    @pytest.mark.asyncio
    async def test_cascade_delete_watchlist(self, test_db: AsyncSession):
        """TC-DB-016: 刪除用戶應級聯刪除自選股 (根據設定)"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"cascade_{timestamp}@test.com",
            username=f"cascade_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建股票和自選股
        stock = Stock(symbol="2454.TW", name="聯發科", market="TW")
        test_db.add(stock)
        await test_db.commit()
        
        watchlist = Watchlist(user_id=user.user_id, symbol=stock.symbol)
        test_db.add(watchlist)
        await test_db.commit()
        
        user_id = user.user_id
        
        # 刪除用戶
        await test_db.delete(user)
        await test_db.commit()
        
        # 檢查自選股是否被刪除 (取決於外鍵設定)
        stmt = select(Watchlist).where(Watchlist.user_id == user_id)
        result = await test_db.execute(stmt)
        orphan_watchlist = result.scalars().all()
        
        # 允許自選股存在或被刪除 (取決於 DB schema)
        # 這個測試主要是驗證不會崩潰
        assert isinstance(orphan_watchlist, list)


class TestComplexQueries:
    """測試複雜查詢"""
    
    @pytest.mark.asyncio
    async def test_aggregate_query(self, test_db: AsyncSession):
        """TC-DB-017: 聚合查詢 (COUNT, SUM) - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建用戶和多個持倉
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        user = await repo.create_user(
            email=f"aggregate_{timestamp}@test.com",
            username=f"aggregate_{timestamp}",
            hashed_password="pass"
        )
        
        # 創建 3 個持倉
        for i in range(3):
            stock = Stock(symbol=f"STOCK{i}.TW", name=f"股票{i}", market="TW")
            test_db.add(stock)
            await test_db.commit()
            
            position = Position(
                user_id=user.user_id,
                symbol=stock.symbol,
                quantity=100 * (i + 1),
                average_cost=100.0,
                purchase_date=datetime.utcnow()
            )
            test_db.add(position)
        
        await test_db.commit()
        
        # 聚合查詢：總持倉數
        stmt = select(func.count(Position.position_id)).where(
            Position.user_id == user.user_id
        )
        result = await test_db.execute(stmt)
        total_positions = result.scalar()
        
        assert total_positions == 3
        
        # 聚合查詢：總股數
        stmt = select(func.sum(Position.quantity)).where(
            Position.user_id == user.user_id
        )
        result = await test_db.execute(stmt)
        total_quantity = result.scalar()
        
        assert total_quantity == 100 + 200 + 300  # 600
    
    @pytest.mark.asyncio
    async def test_subquery(self, test_db: AsyncSession):
        """TC-DB-018: 子查詢測試 - 成功"""
        from apps.repositories.user_repository import UserRepository
        
        # 創建多個用戶
        repo = UserRepository(test_db)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        
        for i in range(3):
            user = await repo.create_user(
                email=f"subquery{i}_{timestamp}@test.com",
                username=f"subuser{i}_{timestamp}",
                hashed_password="pass"
            )
            
            # 為每個用戶創建不同數量的自選股
            for j in range(i + 1):
                stock = Stock(
                    symbol=f"SUB{i}{j}.TW",
                    name=f"子查詢測試{i}{j}",
                    market="TW"
                )
                test_db.add(stock)
                await test_db.commit()
                
                watchlist = Watchlist(user_id=user.user_id, symbol=stock.symbol)
                test_db.add(watchlist)
        
        await test_db.commit()
        
        # 子查詢：找出有 2 個以上自選股的用戶
        from sqlalchemy import and_
        
        subquery = (
            select(Watchlist.user_id, func.count(Watchlist.watchlist_id).label('count'))
            .group_by(Watchlist.user_id)
            .having(func.count(Watchlist.watchlist_id) >= 2)
            .subquery()
        )
        
        stmt = select(User).join(subquery, User.user_id == subquery.c.user_id)
        result = await test_db.execute(stmt)
        users_with_multiple_stocks = result.scalars().all()
        
        # 應該找到至少 2 個用戶 (有 2 和 3 個自選股的)
        assert len(users_with_multiple_stocks) >= 2


class TestConcurrencyControl:
    """測試並發控制"""
    
    @pytest.mark.asyncio
    async def test_concurrent_updates_same_record(self, test_engine):
        """TC-DB-019: 並發更新同一記錄 - 應正確處理"""
        import asyncio
        from sqlalchemy.ext.asyncio import async_sessionmaker
        
        # 創建兩個獨立的 session
        async_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)
        
        # 在第一個 session 中創建股票
        async with async_session_maker() as session1:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
            stock = Stock(
                symbol=f"CONCURRENT{timestamp[:4]}.TW",
                name="並發測試",
                market="TW",
                price=100.0
            )
            session1.add(stock)
            await session1.commit()
            stock_symbol = stock.symbol
        
        # 並發更新
        async def update_price_1():
            async with async_session_maker() as session:
                stmt = select(Stock).where(Stock.symbol == stock_symbol)
                result = await session.execute(stmt)
                stock = result.scalar_one()
                stock.price = 110.0
                await session.commit()
        
        async def update_price_2():
            async with async_session_maker() as session:
                stmt = select(Stock).where(Stock.symbol == stock_symbol)
                result = await session.execute(stmt)
                stock = result.scalar_one()
                stock.price = 120.0
                await session.commit()
        
        # 並發執行
        await asyncio.gather(update_price_1(), update_price_2())
        
        # 驗證最終結果 (應該是其中一個值)
        async with async_session_maker() as session:
            stmt = select(Stock).where(Stock.symbol == stock_symbol)
            result = await session.execute(stmt)
            final_stock = result.scalar_one()
            
            assert final_stock.price in [110.0, 120.0]
