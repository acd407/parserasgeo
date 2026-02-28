from .tools import split_by_n_str, fl_int

# Global debug, this is set when initializing StorageArea
DEBUG = False


class StorageArea(object):
    def __init__(self, debug=False):
        # Set global debug
        global DEBUG
        DEBUG = debug

        # Storage area components
        self.header = Header()
        self.surface_line = SurfaceLine()
        self.storage_type = StorageType()
        self.area = Area()
        self.min_elev = MinElev()
        self.is_2d = Is2D()
        self.point_generation_data = PointGenerationData()
        self.points_2d = Points2D()
        self.perimeter_time = PerimeterTime()
        self.mannings = Mannings()
        self.cell_volume_filter = CellVolumeFilter()
        self.cell_min_area_fraction = CellMinAreaFraction()
        self.face_profile_filter = FaceProfileFilter()
        self.face_area_elev_profile_filter = FaceAreaElevProfileFilter()
        self.face_area_elev_conveyance_ratio = FaceAreaElevConveyanceRatio()
        self.face_min_length_ratio = FaceMinLengthRatio()

        self.components = [
            self.header,
            self.surface_line,
            self.storage_type,
            self.area,
            self.min_elev,
            self.is_2d,
            self.point_generation_data,
            self.points_2d,
            self.perimeter_time,
            self.mannings,
            self.cell_volume_filter,
            self.cell_min_area_fraction,
            self.face_profile_filter,
            self.face_area_elev_profile_filter,
            self.face_area_elev_conveyance_ratio,
            self.face_min_length_ratio,
        ]

        self.geo_list = []  # holds all parts and unknown lines (as strings)

    def import_geo(self, line, geo_file):
        # Add the header first since we know this is the start of a storage area
        if self.header.test(line):
            line = self.header.import_geo(line, geo_file)
            self.geo_list.append(self.header)

        # Continue reading the storage area components in sequence
        try:
            while not self._is_new_feature(line):
                # Check for each component in order of appearance
                if self.surface_line and self.surface_line.test(line):
                    line = self.surface_line.import_geo(line, geo_file)
                    self.geo_list.append(self.surface_line)
                elif self.storage_type and self.storage_type.test(line):
                    line = self.storage_type.import_geo(line, geo_file)
                    self.geo_list.append(self.storage_type)
                elif self.area and self.area.test(line):
                    line = self.area.import_geo(line, geo_file)
                    self.geo_list.append(self.area)
                elif self.min_elev and self.min_elev.test(line):
                    line = self.min_elev.import_geo(line, geo_file)
                    self.geo_list.append(self.min_elev)
                elif self.is_2d and self.is_2d.test(line):
                    line = self.is_2d.import_geo(line, geo_file)
                    self.geo_list.append(self.is_2d)
                elif self.point_generation_data and self.point_generation_data.test(
                    line
                ):
                    line = self.point_generation_data.import_geo(line, geo_file)
                    self.geo_list.append(self.point_generation_data)
                elif self.points_2d and self.points_2d.test(line):
                    line = self.points_2d.import_geo(line, geo_file)
                    self.geo_list.append(self.points_2d)
                elif self.perimeter_time and self.perimeter_time.test(line):
                    line = self.perimeter_time.import_geo(line, geo_file)
                    self.geo_list.append(self.perimeter_time)
                elif self.mannings and self.mannings.test(line):
                    line = self.mannings.import_geo(line, geo_file)
                    self.geo_list.append(self.mannings)
                elif self.cell_volume_filter and self.cell_volume_filter.test(line):
                    line = self.cell_volume_filter.import_geo(line, geo_file)
                    self.geo_list.append(self.cell_volume_filter)
                elif self.cell_min_area_fraction and self.cell_min_area_fraction.test(
                    line
                ):
                    line = self.cell_min_area_fraction.import_geo(line, geo_file)
                    self.geo_list.append(self.cell_min_area_fraction)
                elif self.face_profile_filter and self.face_profile_filter.test(line):
                    line = self.face_profile_filter.import_geo(line, geo_file)
                    self.geo_list.append(self.face_profile_filter)
                elif (
                    self.face_area_elev_profile_filter
                    and self.face_area_elev_profile_filter.test(line)
                ):
                    line = self.face_area_elev_profile_filter.import_geo(line, geo_file)
                    self.geo_list.append(self.face_area_elev_profile_filter)
                elif (
                    self.face_area_elev_conveyance_ratio
                    and self.face_area_elev_conveyance_ratio.test(line)
                ):
                    line = self.face_area_elev_conveyance_ratio.import_geo(
                        line, geo_file
                    )
                    self.geo_list.append(self.face_area_elev_conveyance_ratio)
                elif self.face_min_length_ratio and self.face_min_length_ratio.test(
                    line
                ):
                    line = self.face_min_length_ratio.import_geo(line, geo_file)
                    self.geo_list.append(self.face_min_length_ratio)
                else:
                    # No matching component found - check if it's a new feature
                    if self._is_new_feature(line):
                        break
                    elif line.strip() == "":
                        # Empty line, add as text and continue
                        self.geo_list.append(line)
                        line = next(geo_file)
                        continue
                    else:
                        # Unknown line, add as text and continue
                        self.geo_list.append(line)
                        line = next(geo_file)

        except StopIteration:
            # End of file reached
            pass

        return line

    def _is_new_feature(self, line):
        """Check if line starts a new feature"""
        # Common indicators of new features in HEC-RAS geometry files
        feature_indicators = [
            "River Reach=",
            "Type RM Length L Ch R =",
            "Storage Area=",
            "SA/2D Flow Area=",
        ]
        return any(line.startswith(indicator) for indicator in feature_indicators)

    def __str__(self):
        s = ""
        for line in self.geo_list:
            s += str(line)
        return s

    @staticmethod
    def test(line):
        return Header.test(line)


class Header(object):
    def __init__(self):
        self.name = None
        self.description = None
        self.has_description = False

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:13] == "Storage Area=":
            return True
        return False

    def import_geo(self, line, geo_file):
        # Extract the storage area name and any additional data
        parts = line[13:].split(",", 2)  # Split after 'Storage Area='
        if len(parts) >= 1:
            self.name = parts[0].strip()
        if len(parts) >= 2:
            self.description = parts[1].strip()
            self.has_description = True
        else:
            self.description = ""

        if DEBUG:
            print("Importing Storage Area:", self.name)

        return next(geo_file)

    def __str__(self):
        if self.has_description:
            return f"Storage Area={self.name},{self.description},\n"
        else:
            return f"Storage Area={self.name},,\n"


class SurfaceLine(object):
    def __init__(self):
        self.count = None
        self.points = []  # [(x1, y1), (x2, y2), ... ]

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:20] == "Storage Area Surface":
            return True
        return False

    def import_geo(self, line, geo_file):
        # Extract number of surface line points
        parts = line.split("=")
        if len(parts) > 1:
            self.count = int(parts[1].strip())

        # Read the coordinate pairs
        line = next(geo_file)
        points_read = 0

        while points_read < self.count and line.strip():
            if line.strip() and not self._starts_new_storage_area_component(line):
                # Parse coordinates - typically formatted as continuous numbers without commas
                # Each line contains one coordinate pair for surface line
                line = line.rstrip()  # Keep leading spaces, only remove trailing newline
                if line:
                    # Try to split the line into a pair of coordinates
                    # For surface line, each line contains one coordinate pair
                    clean_line = line.replace(",", "")  # Remove any commas if present
                    # Parse fixed-width format - 16 chars per coordinate
                    coords = []
                    pos = 0
                    while pos < len(clean_line):
                        coord_chunk = clean_line[pos : pos + 16].strip()
                        if coord_chunk:
                            coords.append(coord_chunk)
                        pos += 16

                    # Group into pairs (x, y) - for surface line, there should be exactly 2 coordinates
                    if len(coords) >= 2 and points_read < self.count:
                        self.points.append((coords[0], coords[1]))
                        points_read += 1
            else:
                break  # Found a new storage area component or end of section

            if points_read < self.count:
                try:
                    line = next(geo_file)
                except StopIteration:
                    break  # End of file reached

        if DEBUG:
            print(f"Imported {len(self.points)} surface line points for storage area")

        # Return the next line after the surface line data
        try:
            return next(geo_file)
        except StopIteration:
            return line  # Return the last line if we're at the end of the file

    def _starts_new_storage_area_component(self, line):
        """Check if line starts a new storage area component"""
        storage_area_components = [
            "Storage Area Type=",
            "Storage Area Area=",
            "Storage Area Min Elev=",
            "Storage Area Is2D=",
            "Storage Area Point Generation Data=",
            "Storage Area 2D Points=",
            "River Reach=",
            "Type RM Length L Ch R =",
        ]
        return any(line.startswith(comp) for comp in storage_area_components)

    def __str__(self):
        s = f"Storage Area Surface Line= {self.count}\n"
        # Format points - one pair per line for surface line, 16 char width
        for i, point in enumerate(self.points):
            s += f"{point[0]:>16}{point[1]:>16}"
            if i < len(self.points) - 1:
                s += "\n"
        s += "\n"  # Add final newline
        return s


class StorageType(object):
    def __init__(self):
        self.type_value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:17] == "Storage Area Type=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=")
        if len(parts) > 1:
            self.type_value = int(parts[1].strip())
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Type= {self.type_value}\n"


class Area(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:18] == "Storage Area Area=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Area={self.value}\n"


class MinElev(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:21] == "Storage Area Min Elev=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Min Elev={self.value}\n"


class Is2D(object):
    def __init__(self):
        self.is_2d_flag = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line.startswith("Storage Area Is2D="):
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=")
        if len(parts) > 1:
            self.is_2d_flag = int(parts[1].strip())
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Is2D={self.is_2d_flag}\n"


class PointGenerationData(object):
    def __init__(self):
        self.data = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:28] == "Storage Area Point Generation":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.data = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Point Generation Data={self.data}\n"


class Points2D(object):
    def __init__(self):
        self.count = None
        self.points = []  # [(x1, y1), (x2, y2), ... ]

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if (
            stripped_line.startswith("Storage Area 2D Points=")
            and "PerimeterTime" not in stripped_line
        ):
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=")
        if len(parts) > 1:
            self.count = int(parts[1].strip())

        # Read the 2D points - typically formatted as continuous coordinate pairs
        line = next(geo_file)
        points_read = 0

        while points_read < self.count:
            if line.strip() and not self._starts_new_storage_area_component(line):
                # Process line with coordinates - fixed width format
                clean_line = line.rstrip().replace(
                    ",", ""
                )  # Remove any commas if present, but keep leading spaces
                # Parse fixed-width format - 16 chars per coordinate
                coords = []
                pos = 0
                while pos < len(clean_line):
                    coord_chunk = clean_line[pos : pos + 16].strip()
                    if coord_chunk:
                        coords.append(coord_chunk)
                    pos += 16

                # Group into pairs (x, y)
                for i in range(0, len(coords) - 1, 2):
                    if i + 1 < len(coords) and points_read < self.count:
                        self.points.append((coords[i], coords[i + 1]))
                        points_read += 1
            else:
                break  # Found a new storage area component or end of section

            if points_read < self.count:
                try:
                    line = next(geo_file)
                except StopIteration:
                    break  # End of file reached

        if DEBUG:
            print(f"Imported {len(self.points)} 2D points for storage area")

        # Return the next line after the 2D points data
        try:
            return next(geo_file)
        except StopIteration:
            return line  # Return the last line if we're at the end of the file

    def _starts_new_storage_area_component(self, line):
        """Check if line starts a new storage area component"""
        storage_area_components = [
            "Storage Area=",
            "River Reach=",
            "Type RM Length L Ch R =",
            "SA/2D Flow Area=",
        ]
        return any(line.startswith(comp) for comp in storage_area_components)

    def __str__(self):
        s = f"Storage Area 2D Points= {self.count}\n"
        # Format points - 2 pairs per line as seen in the example, 16 char width
        for i in range(0, len(self.points), 2):
            if i + 1 < len(self.points):
                s += f"{self.points[i][0]:>16}{self.points[i][1]:>16}{self.points[i + 1][0]:>16}{self.points[i + 1][1]:>16}\n"
            else:
                # This should only happen if there's an odd number of points, which shouldn't happen
                # since points should always come in pairs
                s += f"{self.points[i][0]:>16}{self.points[i][1]:>16}\n"
        return s


class PerimeterTime(object):
    def __init__(self):
        self.time_info = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:31] == "Storage Area 2D PointsPerimeterTime=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.time_info = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Storage Area 2D PointsPerimeterTime={self.time_info}\n"


class Mannings(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:20] == "Storage Area Mannings=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Storage Area Mannings={self.value}\n"


class CellVolumeFilter(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:32] == "2D Cell Volume Filter Tolerance=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Cell Volume Filter Tolerance={self.value}\n"


class CellMinAreaFraction(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:29] == "2D Cell Minimum Area Fraction=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Cell Minimum Area Fraction={self.value}\n"


class FaceProfileFilter(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:32] == "2D Face Profile Filter Tolerance=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Face Profile Filter Tolerance={self.value}\n"


class FaceAreaElevProfileFilter(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:43] == "2D Face Area Elevation Profile Filter Tolerance=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Face Area Elevation Profile Filter Tolerance={self.value}\n"


class FaceAreaElevConveyanceRatio(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:39] == "2D Face Area Elevation Conveyance Ratio=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Face Area Elevation Conveyance Ratio={self.value}\n"


class FaceMinLengthRatio(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        stripped_line = line.strip()
        if stripped_line[:24] == "2D Face Min Length Ratio=":
            return True
        return False

    def import_geo(self, line, geo_file):
        parts = line.split("=", 1)
        if len(parts) > 1:
            self.value = parts[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"2D Face Min Length Ratio={self.value}\n"