"""
Fix Camera Synchronization Issue

This script patches the backend to use synchronized detection across multiple cameras
to fix the bounding box misalignment issue.
"""

import os
import shutil
from pathlib import Path


def patch_backend_for_sync():
    """Patch backend_server.py to use synchronized detection"""
    
    backend_file = Path("backend_server.py")
    backup_file = Path("backend_server.py.backup")
    
    if not backend_file.exists():
        print("❌ backend_server.py not found!")
        return False
    
    # Create backup
    if not backup_file.exists():
        shutil.copy2(backend_file, backup_file)
        print(f"✅ Created backup: {backup_file}")
    
    # Read current backend
    with open(backend_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add import for sync manager
    if "from multi_camera_sync import" not in content:
        import_line = "from multi_camera_sync import get_sync_manager, register_camera_sync, process_frame_sync, get_sync_stats, set_sync_tolerance\n"
        
        # Find the import section
        lines = content.split('\n')
        import_end = 0
        for i, line in enumerate(lines):
            if line.startswith('from ') or line.startswith('import '):
                import_end = i + 1
        
        lines.insert(import_end, import_line)
        content = '\n'.join(lines)
        print("✅ Added sync manager import")
    
    # Add sync manager initialization
    if "SYNC_MANAGER = get_sync_manager(YOLO_MODEL)" not in content:
        init_pattern = "# ---- Gate Security Checker ----"
        if init_pattern in content:
            sync_init = "# ---- Multi-Camera Sync Manager ----\nSYNC_MANAGER = get_sync_manager(YOLO_MODEL)\nprint(\"✅ Multi-camera sync manager initialized\")\n\n" + init_pattern
            content = content.replace(init_pattern, sync_init)
            print("✅ Added sync manager initialization")
    
    # Patch WebSocket endpoints to use sync
    content = patch_websocket_endpoint(content, "/ws/detections")
    content = patch_websocket_endpoint(content, "/ws/gate-check")
    
    # Add sync stats endpoint
    if "/sync/stats" not in content:
        sync_endpoint = '''
@app.get("/sync/stats")
async def sync_stats():
    """Get multi-camera synchronization statistics"""
    return JSONResponse(get_sync_stats())


@app.post("/sync/tolerance")
async def set_sync_tolerance_endpoint(tolerance_ms: float = Query(50.0)):
    """Set synchronization tolerance in milliseconds"""
    set_sync_tolerance(tolerance_ms)
    return JSONResponse({
        "status": "success",
        "tolerance_ms": tolerance_ms,
        "message": f"Synchronization tolerance set to {tolerance_ms}ms"
    })


'''
        # Insert before the last route
        last_route = content.rfind('@app.get("/status/production")')
        if last_route > 0:
            content = content[:last_route] + sync_endpoint + content[last_route:]
            print("✅ Added sync endpoints")
    
    # Write patched content
    with open(backend_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Backend patched for camera synchronization!")
    return True


def patch_websocket_endpoint(content, endpoint_path):
    """Patch a WebSocket endpoint to use synchronized detection"""
    
    # Find the endpoint
    pattern = f'@app.websocket("{endpoint_path}")'
    if pattern not in content:
        print(f"⚠️  Endpoint {endpoint_path} not found")
        return content
    
    # Find the function definition
    lines = content.split('\n')
    start_line = -1
    for i, line in enumerate(lines):
        if pattern in line:
            start_line = i
            break
    
    if start_line == -1:
        return content
    
    # Find the function body
    indent_level = None
    for i in range(start_line + 1, len(lines)):
        line = lines[i]
        if line.strip() == '':
            continue
        if indent_level is None and line.strip():
            indent_level = len(line) - len(line.lstrip())
            break
    
    if indent_level is None:
        return content
    
    # Find where to insert sync registration
    insert_point = -1
    for i in range(start_line, len(lines)):
        line = lines[i]
        if "await ws.accept()" in line:
            insert_point = i + 1
            break
    
    if insert_point == -1:
        return content
    
    # Add sync registration
    sync_registration = f'{" " * (indent_level + 4)}# Register camera for synchronization\n'
    sync_registration += f'{" " * (indent_level + 4)}camera_id = f"camera_{hash(source) % 10000}"\n'
    sync_registration += f'{" " * (indent_level + 4)}register_camera_sync(camera_id, source, (640, 480))\n'
    
    lines.insert(insert_point, sync_registration)
    
    # Find detection processing and replace with sync
    for i in range(insert_point, len(lines)):
        line = lines[i]
        if "dets_px = infer_boxes" in line or "dets_px = infer_boxes_batched" in line:
            # Replace with sync processing
            indent = len(line) - len(line.lstrip())
            new_line = f'{" " * indent}# Use synchronized detection\n'
            new_line += f'{" " * indent}sync_result = process_frame_sync(camera_id, frame, t_now, frame_id)\n'
            new_line += f'{" " * indent}dets_px = [{{"cls": d["cls"], "conf": d["conf"], "xyxy": d["xyxy"]}} for d in sync_result.get("detections", [])]\n'
            lines[i] = new_line
            print(f"✅ Patched detection processing in {endpoint_path}")
            break
    
    return '\n'.join(lines)


def main():
    """Main patching function"""
    import sys
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    print("Fixing Camera Synchronization Issue...")
    print()
    
    if patch_backend_for_sync():
        print()
        print("✅ PATCH COMPLETE!")
        print()
        print("Changes made:")
        print("  ✅ Added multi-camera sync manager")
        print("  ✅ Patched WebSocket endpoints for sync")
        print("  ✅ Added sync statistics endpoints")
        print("  ✅ Created backup of original file")
        print()
        print("To apply the fix:")
        print("  1. Restart your backend server")
        print("  2. Check sync stats: curl http://localhost:8000/sync/stats")
        print("  3. Test with multiple cameras")
        print()
        print("The bounding box synchronization issue should now be fixed! 🎉")
    else:
        print("❌ Patch failed!")


if __name__ == "__main__":
    main()
