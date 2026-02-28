#!/usr/bin/env python3
"""
Test script to parse 2d.g01 file using parserasgeo library
"""

import sys
import os

# Add the parserasgeo module to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "parserasgeo"))

import parserasgeo as prg


def main():
    print("=" * 60)
    print("Testing parserasgeo library with 2d.g01 file")
    print("=" * 60)

    # Path to the 2d.g01 file
    geo_file = "leak.g01"

    # Check if the file exists
    if not os.path.isfile(geo_file):
        print(f"Error: File {geo_file} not found!")
        return 1

    try:
        # Parse the geometry file
        print(f"Parsing {geo_file}...")
        geo = prg.ParseRASGeo(geo_file)

        # Print some basic information about the file
        print(f"Successfully parsed {geo_file}")
        print(f"Total number of geometry elements: {len(geo.geo_list)}")

        # Count different types of elements
        cross_sections = geo.get_cross_sections()
        print(f"Number of cross sections: {len(cross_sections)}")

        # Count other elements
        river_reaches = sum(
            1
            for item in geo.geo_list
            if hasattr(item, "header") and hasattr(item.header, "river_name")
        )
        bridges = sum(1 for item in geo.geo_list if hasattr(item, "bridge_type"))
        culverts = sum(1 for item in geo.geo_list if hasattr(item, "culvert_type"))
        storage_areas = sum(
            1
            for item in geo.geo_list
            if hasattr(item, "header")
            and hasattr(item.header, "name")
            and hasattr(item, "surface_line")
        )

        print(f"Number of river reaches: {river_reaches}")
        print(f"Number of bridges: {bridges}")
        print(f"Number of culverts: {culverts}")
        print(f"Number of storage areas: {storage_areas}")

        # Print details about storage areas
        if storage_areas > 0:
            print("\nStorage Area Details:")
            for i, item in enumerate(geo.geo_list):
                # Check if this is a storage area by looking for storage area specific attributes
                if (
                    hasattr(item, "header")
                    and hasattr(item.header, "name")
                    and hasattr(item, "surface_line")
                ):
                    print(f"  Storage Area {i + 1}:")
                    print(f"    Name: {item.header.name}")
                    # Safely access is_2d attribute
                    if hasattr(item, "is_2d"):
                        if hasattr(item.is_2d, "is_2d_flag"):
                            print(f"    Is 2D: {item.is_2d.is_2d_flag}")
                        else:
                            print(f"    Is 2D: {item.is_2d}")
                    # Safely access surface_line count
                    if hasattr(item, "surface_line"):
                        if hasattr(item.surface_line, "count"):
                            print(f"    Surface Line Points: {item.surface_line.count}")
                        elif hasattr(item.surface_line, "__len__"):
                            print(f"    Surface Line Points: {len(item.surface_line)}")
                    # Safely access points_2d count
                    if hasattr(item, "points_2d"):
                        if hasattr(item.points_2d, "count"):
                            print(f"    2D Points: {item.points_2d.count}")
                        elif hasattr(item.points_2d, "__len__"):
                            print(f"    2D Points: {len(item.points_2d)}")
                    print()

        # Print details about the first few cross sections
        if cross_sections:
            print("\nFirst 3 cross sections:")
            for i, xs in enumerate(cross_sections[:3]):
                print(f"  Cross Section {i + 1}:")
                print(f"    River: {xs.river}, Reach: {xs.reach}")
                print(f"    Station: {xs.header.station}")
                print(f"    Description: {xs.description}")
                print()

        # Test writing to a new file
        output_file = "test_output.g01"
        print(f"Writing parsed data to {output_file}...")
        geo.write(output_file)
        print(f"Successfully wrote to {output_file}")

        return 0

    except Exception as e:
        print(f"Error parsing {geo_file}: {str(e)}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())