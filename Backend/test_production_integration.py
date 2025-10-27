#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Production Features Integration
Verifies all production features are working correctly
"""
import sys
import time
import io

# Fix Windows encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

from colorama import init, Fore, Style

# Initialize colorama
init(autoreset=True)


def test_imports():
    """Test that all production modules can be imported"""
    print(f"\n{Fore.CYAN}Testing imports...{Style.RESET_ALL}")
    
    modules = {
        "video_source_manager": "VideoSourceManager",
        "event_deduplication": "EventDeduplicator",
        "alert_rate_limiter": "AlertRateLimiter",
        "model_registry": "ModelRegistry",
        "camera_calibration": "CameraCalibration"
    }
    
    results = {}
    
    for module_name, class_name in modules.items():
        try:
            module = __import__(module_name)
            cls = getattr(module, class_name)
            results[module_name] = True
            print(f"{Fore.GREEN}✅ {module_name:30} - OK{Style.RESET_ALL}")
        except Exception as e:
            results[module_name] = False
            print(f"{Fore.RED}❌ {module_name:30} - FAILED: {e}{Style.RESET_ALL}")
    
    return results


def test_redis_connection():
    """Test Redis connection for event deduplication"""
    print(f"\n{Fore.CYAN}Testing Redis connection...{Style.RESET_ALL}")
    
    try:
        import redis
        client = redis.from_url("redis://localhost:6379", socket_connect_timeout=2)
        client.ping()
        print(f"{Fore.GREEN}✅ Redis connection - OK{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.YELLOW}⚠️  Redis connection - NOT AVAILABLE: {e}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}   Event deduplication will use in-memory fallback{Style.RESET_ALL}")
        return False


def test_video_source_manager():
    """Test video source manager functionality"""
    print(f"\n{Fore.CYAN}Testing Video Source Manager...{Style.RESET_ALL}")
    
    try:
        from video_source_manager import VideoSourceManager, ResilientVideoSource
        
        # Create manager
        manager = VideoSourceManager()
        
        # Test adding a source (won't actually connect)
        print(f"  Creating test video source...")
        
        health = manager.get_all_health_status()
        print(f"{Fore.GREEN}✅ Video Source Manager - OK{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Video Source Manager - FAILED: {e}{Style.RESET_ALL}")
        return False


def test_event_deduplication():
    """Test event deduplication"""
    print(f"\n{Fore.CYAN}Testing Event Deduplication...{Style.RESET_ALL}")
    
    try:
        from event_deduplication import EventDeduplicator
        
        # Create deduplicator
        dedup = EventDeduplicator()
        
        # Test emitting event
        event1 = dedup.emit_event(
            camera_id="test_cam",
            event_type="test_event",
            event_data={"test": "data"},
            track_id=123
        )
        
        # Try duplicate (should be suppressed)
        event2 = dedup.emit_event(
            camera_id="test_cam",
            event_type="test_event",
            event_data={"test": "data"},
            track_id=123
        )
        
        # Get stats
        stats = dedup.get_stats()
        
        if event1 and not event2 and stats["suppressed"] > 0:
            print(f"  Emitted: {stats['emitted']}, Suppressed: {stats['suppressed']}")
            print(f"{Fore.GREEN}✅ Event Deduplication - OK{Style.RESET_ALL}")
            return True
        else:
            print(f"{Fore.YELLOW}⚠️  Event Deduplication - Unexpected behavior{Style.RESET_ALL}")
            return False
            
    except Exception as e:
        print(f"{Fore.RED}❌ Event Deduplication - FAILED: {e}{Style.RESET_ALL}")
        return False


def test_alert_rate_limiter():
    """Test alert rate limiter"""
    print(f"\n{Fore.CYAN}Testing Alert Rate Limiter...{Style.RESET_ALL}")
    
    try:
        from alert_rate_limiter import AlertRateLimiter, Alert, AlertChannel, AlertPriority
        
        # Create limiter
        limiter = AlertRateLimiter()
        
        # Register mock sender
        async def mock_sender(alert):
            pass
        
        limiter.register_sender(AlertChannel.TELEGRAM, mock_sender)
        
        # Get stats
        stats = limiter.get_stats()
        
        print(f"  Rate limits configured for {len(limiter.limits)} channels")
        print(f"{Fore.GREEN}✅ Alert Rate Limiter - OK{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Alert Rate Limiter - FAILED: {e}{Style.RESET_ALL}")
        return False


def test_model_registry():
    """Test model registry"""
    print(f"\n{Fore.CYAN}Testing Model Registry...{Style.RESET_ALL}")
    
    try:
        from model_registry import ModelRegistry
        
        # Create registry
        registry = ModelRegistry()
        
        # Get summary
        summary = registry.get_registry_summary()
        
        print(f"  Total models: {summary['total_models']}")
        print(f"  Active model: {summary.get('active_model', 'None')}")
        print(f"{Fore.GREEN}✅ Model Registry - OK{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Model Registry - FAILED: {e}{Style.RESET_ALL}")
        return False


def test_camera_calibration():
    """Test camera calibration"""
    print(f"\n{Fore.CYAN}Testing Camera Calibration...{Style.RESET_ALL}")
    
    try:
        from camera_calibration import CameraCalibration
        
        # Create calibration
        cal = CameraCalibration("test_camera")
        
        # Get status
        status = cal.get_calibration_status()
        
        print(f"  Profiles available: {len(status['profiles'])}")
        print(f"  Current profile: {status['current_profile']}")
        print(f"{Fore.GREEN}✅ Camera Calibration - OK{Style.RESET_ALL}")
        return True
    except Exception as e:
        print(f"{Fore.RED}❌ Camera Calibration - FAILED: {e}{Style.RESET_ALL}")
        return False


def main():
    """Run all integration tests"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print("Verolux Production Features Integration Test")
    print(f"{'='*60}{Style.RESET_ALL}\n")
    
    results = {}
    
    # Test imports
    import_results = test_imports()
    results["imports"] = all(import_results.values())
    
    # Test Redis
    results["redis"] = test_redis_connection()
    
    # Test each component
    results["video_source"] = test_video_source_manager()
    results["event_dedup"] = test_event_deduplication()
    results["alert_limiter"] = test_alert_rate_limiter()
    results["model_registry"] = test_model_registry()
    results["calibration"] = test_camera_calibration()
    
    # Summary
    print(f"\n{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
    
    total = len(results)
    passed = sum(results.values())
    failed = total - passed
    
    if passed == total:
        print(f"{Fore.GREEN}✅ ALL TESTS PASSED ({passed}/{total}){Style.RESET_ALL}")
        print(f"\n{Fore.GREEN}🎉 All production features are working!{Style.RESET_ALL}")
        print(f"\n{Fore.CYAN}Next steps:")
        print(f"  1. Start Redis: docker run -d -p 6379:6379 redis:latest")
        print(f"  2. Run backend: python backend_server.py")
        print(f"  3. Check status: http://localhost:8000/status/production")
        print(f"{Style.RESET_ALL}\n")
        return 0
    else:
        print(f"{Fore.YELLOW}⚠️  {passed}/{total} tests passed, {failed} failed{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Some features may not be available.")
        print(f"Check errors above and install missing dependencies.{Style.RESET_ALL}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Test cancelled by user{Style.RESET_ALL}")
        sys.exit(130)

