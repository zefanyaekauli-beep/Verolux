"""
Alert Rate Limiter with Batching
Prevents alert fatigue by rate limiting and batching alerts per channel
"""
import time
import asyncio
from collections import defaultdict, deque
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AlertChannel(Enum):
    """Supported alert channels"""
    TELEGRAM = "telegram"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    SLACK = "slack"
    SMS = "sms"
    WEBHOOK = "webhook"


class AlertPriority(Enum):
    """Alert priority levels"""
    CRITICAL = "critical"  # Always send immediately
    HIGH = "high"          # Send immediately if under limit
    MEDIUM = "medium"      # Can be batched
    LOW = "low"            # Always batched


@dataclass
class Alert:
    """Alert data structure"""
    alert_id: str
    channel: AlertChannel
    camera_id: str
    priority: AlertPriority
    title: str
    message: str
    data: Dict
    timestamp: float = field(default_factory=time.time)
    snapshot_url: Optional[str] = None
    clip_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "channel": self.channel.value,
            "camera_id": self.camera_id,
            "priority": self.priority.value,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "timestamp": self.timestamp,
            "snapshot_url": self.snapshot_url,
            "clip_url": self.clip_url
        }


class AlertRateLimiter:
    """
    Rate limit alerts per channel with intelligent batching
    
    Features:
    - Per-channel rate limits
    - Priority-based sending
    - Automatic batching
    - Burst protection
    - Statistics tracking
    """
    
    def __init__(self):
        # Per channel limits (alerts per hour)
        self.limits = {
            AlertChannel.TELEGRAM: 20,
            AlertChannel.EMAIL: 10,
            AlertChannel.WHATSAPP: 15,
            AlertChannel.SLACK: 30,
            AlertChannel.SMS: 5,
            AlertChannel.WEBHOOK: 100
        }
        
        # Track recent alerts (sliding window)
        self.alert_history: Dict[str, deque] = defaultdict(
            lambda: deque(maxlen=200)
        )
        
        # Batching configuration
        self.batch_queues: Dict[str, List[Alert]] = defaultdict(list)
        self.batch_intervals = {
            AlertChannel.TELEGRAM: 300,   # 5 minutes
            AlertChannel.EMAIL: 600,      # 10 minutes
            AlertChannel.WHATSAPP: 300,   # 5 minutes
            AlertChannel.SLACK: 60,       # 1 minute
            AlertChannel.SMS: 900,        # 15 minutes
            AlertChannel.WEBHOOK: 30      # 30 seconds
        }
        
        # Max batch sizes
        self.max_batch_sizes = {
            AlertChannel.TELEGRAM: 10,
            AlertChannel.EMAIL: 20,
            AlertChannel.WHATSAPP: 10,
            AlertChannel.SLACK: 15,
            AlertChannel.SMS: 5,
            AlertChannel.WEBHOOK: 50
        }
        
        # Sender callbacks
        self._senders: Dict[AlertChannel, Callable] = {}
        
        # Statistics
        self.stats = {
            "sent": 0,
            "rate_limited": 0,
            "batched": 0,
            "errors": 0
        }
        
        # Background task
        self._batch_task: Optional[asyncio.Task] = None
        self._running = False
        
        logger.info("Alert rate limiter initialized")
    
    def register_sender(self, channel: AlertChannel, sender_func: Callable):
        """
        Register a sender function for a channel
        
        Args:
            channel: Alert channel
            sender_func: Async function that sends alerts
        """
        self._senders[channel] = sender_func
        logger.info(f"Registered sender for {channel.value}")
    
    def can_send_alert(self, channel: AlertChannel, camera_id: str) -> bool:
        """
        Check if alert can be sent without rate limiting
        
        Args:
            channel: Alert channel
            camera_id: Camera identifier
            
        Returns:
            True if alert can be sent
        """
        key = f"{channel.value}:{camera_id}"
        now = time.time()
        
        # Clean old alerts (older than 1 hour)
        history = self.alert_history[key]
        while history and now - history[0] > 3600:
            history.popleft()
        
        # Check limit
        limit = self.limits.get(channel, 10)
        return len(history) < limit
    
    async def send_alert(self, alert: Alert) -> bool:
        """
        Send alert with rate limiting and batching
        
        Args:
            alert: Alert to send
            
        Returns:
            True if alert was sent immediately, False if queued/batched
        """
        # Critical priority always sends immediately
        if alert.priority == AlertPriority.CRITICAL:
            return await self._send_immediate(alert)
        
        # Check rate limit
        if self.can_send_alert(alert.channel, alert.camera_id):
            # High priority sends if under limit
            if alert.priority == AlertPriority.HIGH:
                return await self._send_immediate(alert)
            
            # Medium priority can send or batch
            if alert.priority == AlertPriority.MEDIUM:
                # Send immediately if under 50% of limit
                key = f"{alert.channel.value}:{alert.camera_id}"
                current_count = len(self.alert_history[key])
                limit = self.limits.get(alert.channel, 10)
                
                if current_count < limit * 0.5:
                    return await self._send_immediate(alert)
                else:
                    self._add_to_batch(alert)
                    return False
            
            # Low priority always batched
            self._add_to_batch(alert)
            return False
        else:
            # Rate limited - add to batch
            self._add_to_batch(alert)
            self.stats["rate_limited"] += 1
            logger.warning(
                f"Alert rate limited for {alert.channel.value}:{alert.camera_id}, "
                f"added to batch"
            )
            return False
    
    async def _send_immediate(self, alert: Alert) -> bool:
        """Send alert immediately"""
        sender = self._senders.get(alert.channel)
        
        if not sender:
            logger.error(f"No sender registered for {alert.channel.value}")
            self.stats["errors"] += 1
            return False
        
        try:
            # Send alert
            await sender(alert)
            
            # Record in history
            key = f"{alert.channel.value}:{alert.camera_id}"
            self.alert_history[key].append(time.time())
            
            self.stats["sent"] += 1
            logger.info(f"Alert sent: {alert.alert_id} via {alert.channel.value}")
            return True
            
        except Exception as e:
            logger.error(f"Alert send error: {e}")
            self.stats["errors"] += 1
            return False
    
    def _add_to_batch(self, alert: Alert):
        """Add alert to batch queue"""
        key = f"{alert.channel.value}:{alert.camera_id}"
        self.batch_queues[key].append(alert)
        self.stats["batched"] += 1
        
        logger.debug(
            f"Alert added to batch: {alert.alert_id} "
            f"(queue size: {len(self.batch_queues[key])})"
        )
    
    async def start_batch_processor(self):
        """Start background batch processing task"""
        if self._running:
            logger.warning("Batch processor already running")
            return
        
        self._running = True
        self._batch_task = asyncio.create_task(self._batch_processor_loop())
        logger.info("Started alert batch processor")
    
    async def stop_batch_processor(self):
        """Stop background batch processing"""
        self._running = False
        
        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
        
        # Flush remaining batches
        await self._flush_all_batches()
        
        logger.info("Stopped alert batch processor")
    
    async def _batch_processor_loop(self):
        """Background task that processes batches"""
        while self._running:
            try:
                await asyncio.sleep(10)  # Check every 10 seconds
                await self._process_batches()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Batch processor error: {e}")
    
    async def _process_batches(self):
        """Process all batch queues"""
        now = time.time()
        
        for key, queue in list(self.batch_queues.items()):
            if not queue:
                continue
            
            try:
                channel_str, camera_id = key.split(":", 1)
                channel = AlertChannel(channel_str)
            except (ValueError, KeyError):
                logger.error(f"Invalid batch key: {key}")
                continue
            
            # Check if should flush
            if self._should_flush_batch(channel, queue, now):
                await self._flush_batch(channel, camera_id, queue)
    
    def _should_flush_batch(self, 
                           channel: AlertChannel,
                           queue: List[Alert],
                           now: float) -> bool:
        """Check if batch should be flushed"""
        if not queue:
            return False
        
        # Check batch size limit
        max_size = self.max_batch_sizes.get(channel, 10)
        if len(queue) >= max_size:
            return True
        
        # Check time interval
        oldest = queue[0].timestamp
        interval = self.batch_intervals.get(channel, 300)
        
        if now - oldest >= interval:
            return True
        
        return False
    
    async def _flush_batch(self, 
                          channel: AlertChannel,
                          camera_id: str,
                          queue: List[Alert]):
        """Flush a batch of alerts"""
        if not queue:
            return
        
        batch_size = len(queue)
        logger.info(
            f"Flushing batch for {channel.value}:{camera_id} "
            f"({batch_size} alerts)"
        )
        
        # Create batch summary alert
        summary_alert = self._create_batch_summary(channel, camera_id, queue)
        
        # Send summary
        await self._send_immediate(summary_alert)
        
        # Clear queue
        key = f"{channel.value}:{camera_id}"
        self.batch_queues[key].clear()
    
    def _create_batch_summary(self,
                             channel: AlertChannel,
                             camera_id: str,
                             alerts: List[Alert]) -> Alert:
        """Create summary alert for batch"""
        now = time.time()
        
        # Group by priority
        by_priority = defaultdict(list)
        for alert in alerts:
            by_priority[alert.priority].append(alert)
        
        # Build summary message
        title = f"📊 Alert Summary - Camera {camera_id}"
        
        message_parts = [
            f"**{len(alerts)} alerts** in the last batch:",
            ""
        ]
        
        # Add priority breakdown
        for priority in [AlertPriority.HIGH, AlertPriority.MEDIUM, AlertPriority.LOW]:
            count = len(by_priority[priority])
            if count > 0:
                emoji = "🔴" if priority == AlertPriority.HIGH else "🟡" if priority == AlertPriority.MEDIUM else "🟢"
                message_parts.append(f"{emoji} {priority.value.upper()}: {count}")
        
        message_parts.append("")
        
        # Add time range
        first_time = alerts[0].timestamp
        last_time = alerts[-1].timestamp
        duration = last_time - first_time
        
        message_parts.append(f"⏱️ Time range: {duration:.1f} seconds")
        
        # Add sample of recent alerts
        message_parts.append("")
        message_parts.append("**Recent alerts:**")
        
        for alert in alerts[-3:]:  # Last 3 alerts
            time_ago = now - alert.timestamp
            message_parts.append(f"• {alert.title} ({time_ago:.0f}s ago)")
        
        message = "\n".join(message_parts)
        
        # Create summary alert
        return Alert(
            alert_id=f"batch_{camera_id}_{int(now)}",
            channel=channel,
            camera_id=camera_id,
            priority=AlertPriority.MEDIUM,
            title=title,
            message=message,
            data={
                "batch_size": len(alerts),
                "priority_breakdown": {
                    p.value: len(by_priority[p])
                    for p in AlertPriority
                },
                "first_alert_time": first_time,
                "last_alert_time": last_time,
                "alerts": [a.to_dict() for a in alerts]
            },
            timestamp=now
        )
    
    async def _flush_all_batches(self):
        """Flush all pending batches"""
        logger.info("Flushing all pending batches...")
        
        for key, queue in list(self.batch_queues.items()):
            if queue:
                try:
                    channel_str, camera_id = key.split(":", 1)
                    channel = AlertChannel(channel_str)
                    await self._flush_batch(channel, camera_id, queue)
                except Exception as e:
                    logger.error(f"Error flushing batch {key}: {e}")
    
    def get_queue_status(self) -> dict:
        """Get status of all batch queues"""
        return {
            key: {
                "size": len(queue),
                "oldest_age": time.time() - queue[0].timestamp if queue else 0
            }
            for key, queue in self.batch_queues.items()
            if queue
        }
    
    def get_stats(self) -> dict:
        """Get rate limiter statistics"""
        total = self.stats["sent"] + self.stats["batched"]
        batch_rate = (self.stats["batched"] / total * 100) if total > 0 else 0
        
        return {
            "sent": self.stats["sent"],
            "rate_limited": self.stats["rate_limited"],
            "batched": self.stats["batched"],
            "errors": self.stats["errors"],
            "total_alerts": total,
            "batch_rate_percent": round(batch_rate, 2),
            "queue_status": self.get_queue_status()
        }
    
    def reset_stats(self):
        """Reset statistics (for testing)"""
        self.stats = {
            "sent": 0,
            "rate_limited": 0,
            "batched": 0,
            "errors": 0
        }


# Example sender implementations

async def send_telegram_alert(alert: Alert):
    """Example Telegram sender"""
    # TODO: Implement actual Telegram API call
    logger.info(f"Sending Telegram alert: {alert.title}")
    # import telegram
    # bot = telegram.Bot(token=TELEGRAM_TOKEN)
    # await bot.send_message(
    #     chat_id=CHAT_ID,
    #     text=f"**{alert.title}**\n{alert.message}",
    #     parse_mode='Markdown'
    # )


async def send_email_alert(alert: Alert):
    """Example Email sender"""
    # TODO: Implement actual email sending
    logger.info(f"Sending email alert: {alert.title}")
    # import aiosmtplib
    # from email.message import EmailMessage
    # msg = EmailMessage()
    # msg['Subject'] = alert.title
    # msg['From'] = FROM_EMAIL
    # msg['To'] = TO_EMAIL
    # msg.set_content(alert.message)
    # await aiosmtplib.send(msg, hostname=SMTP_HOST)


async def send_slack_alert(alert: Alert):
    """Example Slack sender"""
    # TODO: Implement actual Slack webhook
    logger.info(f"Sending Slack alert: {alert.title}")
    # import aiohttp
    # async with aiohttp.ClientSession() as session:
    #     await session.post(SLACK_WEBHOOK_URL, json={
    #         'text': f"*{alert.title}*\n{alert.message}"
    #     })


# Global instance
alert_rate_limiter = AlertRateLimiter()

# Register example senders (replace with actual implementations)
alert_rate_limiter.register_sender(AlertChannel.TELEGRAM, send_telegram_alert)
alert_rate_limiter.register_sender(AlertChannel.EMAIL, send_email_alert)
alert_rate_limiter.register_sender(AlertChannel.SLACK, send_slack_alert)



















