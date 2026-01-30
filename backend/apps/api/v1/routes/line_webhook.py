"""
LINE Bot Webhook 處理器
接收來自 LINE Platform 的事件
"""
from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
import hmac
import hashlib
import base64
import json
import logging
from datetime import datetime
from apps.core.database import get_db
from apps.core.config import settings
from apps.models.user import User
from apps.core.services.line_service import line_bot_service

logger = logging.getLogger(__name__)
router = APIRouter(tags=["LINE Bot"])


def verify_signature(body: bytes, signature: str, channel_secret: str) -> bool:
    """驗證 LINE Webhook 簽名"""
    hash_value = hmac.new(
        channel_secret.encode('utf-8'),
        body,
        hashlib.sha256
    ).digest()
    expected_signature = base64.b64encode(hash_value).decode('utf-8')
    return hmac.compare_digest(signature, expected_signature)


@router.post("/line/webhook")
async def line_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    LINE Bot Webhook 端點
    接收用戶訊息、加入好友等事件
    """
    
    # 獲取請求內容
    body = await request.body()
    signature = request.headers.get('X-Line-Signature', '')
    
    # 驗證簽名（需要 LINE_CHANNEL_SECRET）
    channel_secret = settings.LINE_CHANNEL_SECRET if hasattr(settings, 'LINE_CHANNEL_SECRET') else ""
    if channel_secret and not verify_signature(body, signature, channel_secret):
        logger.warning("❌ LINE Webhook 簽名驗證失敗")
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    # 解析事件
    try:
        payload = json.loads(body)
        events = payload.get('events', [])
        
        for event in events:
            event_type = event.get('type')
            user_id = event.get('source', {}).get('userId')
            
            if not user_id:
                continue
            
            # 處理加入好友事件
            if event_type == 'follow':
                await handle_follow_event(user_id, db)
            
            # 處理取消好友事件
            elif event_type == 'unfollow':
                await handle_unfollow_event(user_id, db)
            
            # 處理訊息事件
            elif event_type == 'message':
                message_text = event.get('message', {}).get('text', '')
                await handle_message_event(user_id, message_text, db)
        
        return {"status": "ok"}
        
    except Exception as e:
        logger.error(f"❌ LINE Webhook 處理錯誤: {e}")
        return {"status": "error", "message": str(e)}


async def handle_follow_event(line_user_id: str, db: AsyncSession):
    """處理用戶加入好友事件"""
    logger.info(f"👥 用戶加入 LINE Bot: {line_user_id}")
    
    # 發送歡迎訊息
    welcome_message = """
🎉 歡迎使用 AuraTrade 股票通知！

請先完成以下步驟：
1️⃣ 登入 AuraTrade 網站
2️⃣ 進入「設定」頁面
3️⃣ 輸入您的 LINE User ID 並啟用通知

您的 LINE User ID:
{}

完成後，您將收到即時的：
📈 股價提醒通知
📰 新聞情緒分析
💰 交易記錄通知
    """.format(line_user_id).strip()
    
    await line_bot_service._send_push_message(line_user_id, welcome_message)


async def handle_unfollow_event(line_user_id: str, db: AsyncSession):
    """處理用戶取消好友事件"""
    logger.info(f"👋 用戶取消 LINE Bot: {line_user_id}")
    
    # 停用通知
    stmt = (
        update(User)
        .where(User.line_user_id == line_user_id)
        .values(line_notify_enabled=False)
    )
    await db.execute(stmt)
    await db.commit()


async def handle_message_event(line_user_id: str, message_text: str, db: AsyncSession):
    """處理用戶發送的訊息"""
    logger.info(f"💬 收到訊息 from {line_user_id}: {message_text}")
    
    # 檢查用戶是否已綁定
    stmt = select(User).where(User.line_user_id == line_user_id)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if message_text.lower() in ['help', '幫助', '指令']:
        help_message = """
📖 AuraTrade LINE Bot 指令

🔹 help / 幫助 - 顯示此訊息
🔹 status / 狀態 - 查看綁定狀態
🔹 id - 顯示您的 LINE User ID

💡 提示：請到 AuraTrade 網站設定通知
        """.strip()
        await line_bot_service._send_push_message(line_user_id, help_message)
    
    elif message_text.lower() in ['status', '狀態']:
        if user:
            status_msg = f"""
✅ 已綁定帳號

Email: {user.email}
通知狀態: {'🟢 已啟用' if user.line_notify_enabled else '🔴 已停用'}

您可以在網站設定中管理通知偏好。
            """.strip()
        else:
            status_msg = f"""
❌ 尚未綁定帳號

您的 LINE User ID:
{line_user_id}

請到 AuraTrade 網站「設定」頁面綁定。
            """.strip()
        await line_bot_service._send_push_message(line_user_id, status_msg)
    
    elif message_text.lower() == 'id':
        await line_bot_service._send_push_message(
            line_user_id,
            f"您的 LINE User ID:\n{line_user_id}"
        )
    
    else:
        # 預設回應
        await line_bot_service._send_push_message(
            line_user_id,
            "輸入「help」查看可用指令 📖"
        )


@router.get("/line/test-notification")
async def test_line_notification(
    line_user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """測試 LINE 通知功能（開發用）"""
    if not line_bot_service.is_configured():
        raise HTTPException(status_code=500, detail="LINE Bot 未設定")
    
    test_message = f"""
🧪 測試通知

這是一則測試訊息，確認 LINE Bot 正常運作。

時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """.strip()
    
    success = await line_bot_service._send_push_message(line_user_id, test_message)
    
    if success:
        return {"success": True, "message": "測試通知已發送"}
    else:
        raise HTTPException(status_code=500, detail="發送失敗")


@router.post("/line/bind-user")
async def bind_line_user(
    email: str,
    line_user_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    手動綁定 LINE User ID（開發用）
    用於沒有 Webhook 的情況
    """
    try:
        # 查找用戶
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        user = result.scalars().first()
        
        if not user:
            raise HTTPException(status_code=404, detail=f"找不到用戶: {email}")
        
        # 綁定 LINE User ID
        user.line_user_id = line_user_id
        user.line_notify_enabled = True
        await db.commit()
        
        logger.info(f"✅ 已綁定 LINE User ID: {email} -> {line_user_id}")
        
        # 發送歡迎訊息
        welcome_msg = f"""
🎉 綁定成功！

您的帳號已成功綁定 LINE 通知。

Email: {user.email}
狀態: 🟢 通知已啟用

現在您會收到：
📈 股價提醒通知
📰 新聞情緒分析
💰 交易記錄通知
        """.strip()
        
        await line_bot_service._send_push_message(line_user_id, welcome_msg)
        
        return {
            "success": True,
            "message": "綁定成功",
            "user": {
                "email": user.email,
                "line_user_id": user.line_user_id,
                "line_notify_enabled": user.line_notify_enabled
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 綁定失敗: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/line/user-status")
async def get_line_user_status(
    email: str,
    db: AsyncSession = Depends(get_db)
):
    """查詢用戶的 LINE 綁定狀態"""
    stmt = select(User).where(User.email == email)
    result = await db.execute(stmt)
    user = result.scalars().first()
    
    if not user:
        raise HTTPException(status_code=404, detail="找不到用戶")
    
    return {
        "email": user.email,
        "line_user_id": user.line_user_id,
        "line_notify_enabled": user.line_notify_enabled,
        "is_bound": bool(user.line_user_id),
        "status": "🟢 已綁定" if user.line_user_id else "🔴 未綁定"
    }
