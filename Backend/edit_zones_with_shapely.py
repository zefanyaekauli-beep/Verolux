#!/usr/bin/env python3
"""
Zone Editor with Shapely
Edit gate zones using shapely geometry operations
"""
import json
import os
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union
import numpy as np

class ZoneEditor:
    def __init__(self, config_dir="config"):
        self.config_dir = config_dir
        
    def load_zone(self, zone_file):
        """Load zone from JSON file"""
        path = os.path.join(self.config_dir, zone_file)
        with open(path, 'r') as f:
            return json.load(f)
    
    def save_zone(self, zone_file, zone_data):
        """Save zone to JSON file"""
        path = os.path.join(self.config_dir, zone_file)
        with open(path, 'w') as f:
            json.dump(zone_data, f, indent=2)
    
    def polygon_from_coords(self, coords):
        """Create shapely polygon from coordinates"""
        return Polygon(coords)
    
    def coords_from_polygon(self, polygon):
        """Get coordinates from shapely polygon"""
        return list(polygon.exterior.coords[:-1])  # Remove duplicate last point
    
    def visualize_zones(self, frame_width=640, frame_height=480):
        """Create visualization of current zones"""
        import cv2
        
        # Create blank image
        img = np.zeros((frame_height, frame_width, 3), dtype=np.uint8)
        
        # Load zones
        gate_zone = self.load_zone("gate_A1_polygon.json")
        guard_zone = self.load_zone("guard_anchor_A1_polygon.json")
        
        # Convert normalized coordinates to pixel coordinates
        gate_pixels = []
        for x, y in gate_zone["polygon"]:
            px = int(x * frame_width)
            py = int(y * frame_height)
            gate_pixels.append([px, py])
        
        guard_pixels = []
        for x, y in guard_zone["polygon"]:
            px = int(x * frame_width)
            py = int(y * frame_height)
            guard_pixels.append([px, py])
        
        # Draw zones
        cv2.fillPoly(img, [np.array(gate_pixels)], (0, 100, 0))  # Green gate area
        cv2.fillPoly(img, [np.array(guard_pixels)], (100, 0, 0))  # Blue guard area
        
        # Draw outlines
        cv2.polylines(img, [np.array(gate_pixels)], True, (0, 255, 0), 2)
        cv2.polylines(img, [np.array(guard_pixels)], True, (255, 0, 0), 2)
        
        # Add labels
        cv2.putText(img, "GATE AREA", (gate_pixels[0][0], gate_pixels[0][1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, "GUARD AREA", (guard_pixels[0][0], guard_pixels[0][1] - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        
        return img
    
    def resize_zone(self, zone_file, scale_factor):
        """Resize zone by scale factor around its centroid"""
        zone_data = self.load_zone(zone_file)
        polygon = self.polygon_from_coords(zone_data["polygon"])
        
        # Get centroid
        centroid = polygon.centroid
        
        # Scale around centroid
        scaled_polygon = polygon.scale(scale_factor, scale_factor, origin=centroid)
        
        # Update coordinates
        zone_data["polygon"] = self.coords_from_polygon(scaled_polygon)
        
        # Save back
        self.save_zone(zone_file, zone_data)
        print(f"✅ Resized {zone_file} by factor {scale_factor}")
    
    def move_zone(self, zone_file, dx, dy):
        """Move zone by offset"""
        zone_data = self.load_zone(zone_file)
        polygon = self.polygon_from_coords(zone_data["polygon"])
        
        # Translate
        moved_polygon = polygon.translate(dx, dy)
        
        # Update coordinates
        zone_data["polygon"] = self.coords_from_polygon(moved_polygon)
        
        # Save back
        self.save_zone(zone_file, zone_data)
        print(f"✅ Moved {zone_file} by ({dx}, {dy})")
    
    def create_custom_zone(self, zone_file, coords, zone_type="custom", description="Custom zone"):
        """Create a new zone with custom coordinates"""
        zone_data = {
            "zone_id": zone_file.replace(".json", ""),
            "zone_type": zone_type,
            "polygon": coords,
            "description": description,
            "normalized": True
        }
        
        self.save_zone(zone_file, zone_data)
        print(f"✅ Created custom zone: {zone_file}")
    
    def merge_zones(self, zone1_file, zone2_file, output_file):
        """Merge two zones using shapely union"""
        zone1_data = self.load_zone(zone1_file)
        zone2_data = self.load_zone(zone2_file)
        
        polygon1 = self.polygon_from_coords(zone1_data["polygon"])
        polygon2 = self.polygon_from_coords(zone2_data["polygon"])
        
        # Union
        merged = unary_union([polygon1, polygon2])
        
        if isinstance(merged, Polygon):
            merged_coords = self.coords_from_polygon(merged)
            
            merged_data = {
                "zone_id": output_file.replace(".json", ""),
                "zone_type": "merged",
                "polygon": merged_coords,
                "description": f"Merged {zone1_file} and {zone2_file}",
                "normalized": True
            }
            
            self.save_zone(output_file, merged_data)
            print(f"✅ Merged zones into {output_file}")
        else:
            print("❌ Merged result is not a single polygon")

def demo_zone_editing():
    """Demonstrate zone editing capabilities"""
    print("🔧 Zone Editor with Shapely")
    print("=" * 40)
    
    editor = ZoneEditor()
    
    # Show current zones
    print("\n📐 Current zones:")
    gate_zone = editor.load_zone("gate_A1_polygon.json")
    guard_zone = editor.load_zone("guard_anchor_A1_polygon.json")
    
    print(f"Gate area: {gate_zone['polygon']}")
    print(f"Guard area: {guard_zone['polygon']}")
    
    # Example operations
    print("\n🛠️  Available operations:")
    print("1. editor.resize_zone('gate_A1_polygon.json', 1.2)  # Make 20% larger")
    print("2. editor.move_zone('gate_A1_polygon.json', 0.1, 0.0)  # Move right")
    print("3. editor.create_custom_zone('custom_zone.json', [[0.5,0.5],[0.6,0.5],[0.6,0.6],[0.5,0.6]])")
    print("4. editor.merge_zones('gate_A1_polygon.json', 'guard_anchor_A1_polygon.json', 'merged.json')")
    
    # Create visualization
    print("\n📊 Creating zone visualization...")
    try:
        img = editor.visualize_zones()
        cv2.imwrite("zone_visualization.jpg", img)
        print("✅ Saved zone_visualization.jpg")
    except ImportError:
        print("⚠️  OpenCV not available for visualization")

def interactive_zone_editor():
    """Interactive zone editor"""
    print("\n🎮 Interactive Zone Editor")
    print("=" * 40)
    
    editor = ZoneEditor()
    
    while True:
        print("\nOptions:")
        print("1. View current zones")
        print("2. Resize gate zone")
        print("3. Move gate zone")
        print("4. Resize guard zone")
        print("5. Move guard zone")
        print("6. Create custom zone")
        print("7. Show visualization")
        print("8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            gate_zone = editor.load_zone("gate_A1_polygon.json")
            guard_zone = editor.load_zone("guard_anchor_A1_polygon.json")
            print(f"Gate area: {gate_zone['polygon']}")
            print(f"Guard area: {guard_zone['polygon']}")
        
        elif choice == "2":
            try:
                scale = float(input("Enter scale factor (e.g., 1.2 for 20% larger): "))
                editor.resize_zone("gate_A1_polygon.json", scale)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "3":
            try:
                dx = float(input("Enter X offset (-0.1 to 0.1): "))
                dy = float(input("Enter Y offset (-0.1 to 0.1): "))
                editor.move_zone("gate_A1_polygon.json", dx, dy)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "4":
            try:
                scale = float(input("Enter scale factor (e.g., 1.2 for 20% larger): "))
                editor.resize_zone("guard_anchor_A1_polygon.json", scale)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "5":
            try:
                dx = float(input("Enter X offset (-0.1 to 0.1): "))
                dy = float(input("Enter Y offset (-0.1 to 0.1): "))
                editor.move_zone("guard_anchor_A1_polygon.json", dx, dy)
            except ValueError:
                print("❌ Invalid number")
        
        elif choice == "6":
            print("Enter 4 points as x,y coordinates:")
            coords = []
            for i in range(4):
                coord_str = input(f"Point {i+1} (x,y): ")
                try:
                    x, y = map(float, coord_str.split(','))
                    coords.append([x, y])
                except ValueError:
                    print("❌ Invalid format. Use: x,y")
                    break
            if len(coords) == 4:
                filename = input("Enter filename (e.g., custom_zone.json): ")
                editor.create_custom_zone(filename, coords)
        
        elif choice == "7":
            try:
                img = editor.visualize_zones()
                cv2.imshow("Zone Visualization", img)
                print("Press any key to close visualization...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
            except ImportError:
                print("⚠️  OpenCV not available for visualization")
        
        elif choice == "8":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "interactive":
        interactive_zone_editor()
    else:
        demo_zone_editing()
        
        # Ask if user wants interactive mode
        response = input("\nWould you like to enter interactive mode? (y/n): ")
        if response.lower() == 'y':
            interactive_zone_editor()















