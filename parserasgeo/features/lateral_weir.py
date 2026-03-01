from .tools import (
    fl_int,
)  #  , split_by_n_str, pad_left, print_list_by_group, split_block_obs, split_by_n
from .description import Description


class Header(object):
    def __init__(self):
        self.station = None
        self.node_type = None
        self.value1 = None
        self.value2 = None
        self.value3 = None

    @staticmethod
    def test(line):
        if line[:23] == "Type RM Length L Ch R =":
            if line[24:25] == "6":
                return True
        return False

    def import_geo(self, line, geo_file):
        fields = line[23:].split(",")
        # print line, fields
        assert len(fields) == 5
        # vals = [fl_int(x) for x in fields]
        # Node type and cross section id
        self.node_type = fl_int(fields[0])
        self.station = fl_int(fields[1])
        # TODO: Not sure what these are yet
        self.value1 = fields[2].strip()
        self.value2 = fields[3].strip()
        self.value3 = fields[4].strip()
        return next(geo_file)

    def __str__(self):
        s = "Type RM Length L Ch R = "
        s += str(self.node_type) + " ,"
        s += "{:<8}".format(str(self.station)) + ","
        s += (
            str(self.value1)
            + ","
            + str(self.value2)
            + ","
            + str(self.value3).rstrip()
            + "\n"
        )
        return s


class LateralWeirNodeName(object):
    def __init__(self):
        self.name = None

    @staticmethod
    def test(line):
        if line.startswith("Node Name="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.name = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Node Name={self.name}\n"


class LateralWeirLastEditedTime(object):
    def __init__(self):
        self.time = None

    @staticmethod
    def test(line):
        if line.startswith("Node Last Edited Time="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.time = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Node Last Edited Time={self.time}\n"


class LateralWeirSS(object):
    def __init__(self):
        self.values = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir SS="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.values = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir SS={self.values}\n"


class LateralWeirSE(object):
    def __init__(self):
        self.num_points: int = 0
        self.station_elevation_points = []

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir SE="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.num_points = int(line.split("=", 1)[1].strip())

        # If there are points to read, process them here
        if self.num_points > 0:
            from .tools import split_by_n_str

            # Read the specified number of data points
            points_read = 0
            while points_read < self.num_points:
                line = next(geo_file)
                
                # Check if this line starts a new feature
                if self._is_new_feature(line):
                    # Put the line back by raising StopIteration to signal end
                    raise StopIteration
                
                coords = split_by_n_str(line.rstrip(), 8)
                for i in range(0, len(coords), 2):
                    if i + 1 < len(coords) and points_read < self.num_points:
                        self.station_elevation_points.append(
                            (coords[i].strip(), coords[i + 1].strip())
                        )
                        points_read += 1

        # Return the next line so the main parser can continue processing
        try:
            return next(geo_file)
        except StopIteration:
            # If there's no more data, return an empty string or indicate end
            return ""

    def _is_new_feature(self, line):
        """Check if line starts a new feature"""
        # Common indicators of new features in HEC-RAS geometry files
        feature_indicators = [
            "River Reach=",
            "Type RM Length L Ch R =",  # New river reach/cross section
            "Storage Area=",
            "SA/2D Flow Area=",
            "Lateral Weir Pos=",  # New lateral weir
            "Culvert=",
            "Bridge=",
            "Inline Structure=",
            "Junction=",
            "Boundary=",
        ]
        stripped_line = line.strip()
        return any(stripped_line.startswith(indicator) for indicator in feature_indicators)

    def __str__(self):
        result = f"Lateral Weir SE={self.num_points} \n"
        from .tools import print_list_by_group

        # Flatten station/elevation pairs
        sta_elev_list = [x for tup in self.station_elevation_points for x in tup]
        # Format in groups with 8 character width and 10 columns per line
        if sta_elev_list:
            result += print_list_by_group(sta_elev_list, 8, 10)
        return result


class LateralWeirOverflowMethod2D(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("LW OverFlow Method 2D="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"LW OverFlow Method 2D={self.value}\n"


class LateralWeirOverflowVelocity2D(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("LW OverFlow Use Velocity Into 2D="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"LW OverFlow Use Velocity Into 2D={self.value}\n"


class LateralWeirWSCriteria(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir WSCriteria="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir WSCriteria={self.value} \n"


class LateralWeirFlapGates(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Flap Gates="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Flap Gates={self.value} \n"


class LateralWeirHagersEQN(object):
    def __init__(self):
        self.values = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Hagers EQN="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.values = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Hagers EQN= {self.values},,,,,\n"


class LateralWeirType(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Type="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Type={self.value} \n"


class LateralWeirConnectionPosDist(object):
    def __init__(self):
        self.values = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Connection Pos and Dist="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.values = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Connection Pos and Dist={self.values}\n"


class LateralWeirPosition(object):
    def __init__(self):
        self.position = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Pos="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.position = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Pos={self.position} \n"


class LateralWeirEnd(object):
    def __init__(self):
        self.end_values = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir End="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.end_values = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir End={self.end_values}\n"


class LateralWeirDistance(object):
    def __init__(self):
        self.distance = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Distance="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.distance = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Distance={self.distance}\n"


class LateralWeirTWMultipleXS(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir TW Multiple XS="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir TW Multiple XS={self.value}\n"


class LateralWeirWD(object):
    def __init__(self):
        self.width = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir WD="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.width = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir WD={self.width}\n"


class LateralWeirCoef(object):
    def __init__(self):
        self.coefficient = None

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Coef="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.coefficient = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"Lateral Weir Coef={self.coefficient}\n"


class LateralWeirDivRC(object):
    def __init__(self):
        self.value = None

    @staticmethod
    def test(line):
        if line.startswith("LW Div RC="):
            return True
        return False

    def import_geo(self, line, geo_file):
        self.value = line.split("=", 1)[1].strip()
        return next(geo_file)

    def __str__(self):
        return f"LW Div RC={self.value}\n"


class LateralWeirCenterline(object):
    def __init__(self):
        self.num_points = None
        self.points = []  # [(x1,y1),(x2,y2),(x3,y3),...] Values are currently stored as strings

    @staticmethod
    def test(line):
        if line.startswith("Lateral Weir Centerline="):
            return True
        return False

    def import_geo(self, line, geo_file):
        from .tools import split_by_n_str

        self.num_points = int(line.split("=", 1)[1].strip())

        # Read centerline coordinates - they come in groups of 16 character width coordinates
        points_read = 0
        while points_read < self.num_points:
            line = next(geo_file)
            
            # Check if this line starts a new feature
            if self._is_new_feature(line):
                # Put the line back by raising StopIteration to signal end
                raise StopIteration
            
            # Split the line into chunks of 16 characters for coordinates
            coords = split_by_n_str(line.rstrip(), 16)
            # Group coordinates into pairs (x, y)
            for i in range(0, len(coords), 2):
                if i + 1 < len(coords) and points_read < self.num_points:
                    self.points.append((coords[i].rstrip(), coords[i + 1].rstrip()))
                    points_read += 1

        # Return the next line so the main parser can continue processing
        try:
            return next(geo_file)
        except StopIteration:
            # If there's no more data, return an empty string or indicate end
            return ""

    def _is_new_feature(self, line):
        """Check if line starts a new feature"""
        # Common indicators of new features in HEC-RAS geometry files
        feature_indicators = [
            "River Reach=",
            "Type RM Length L Ch R =",  # New river reach/cross section
            "Storage Area=",
            "SA/2D Flow Area=",
            "Lateral Weir Pos=",  # New lateral weir
            "Culvert=",
            "Bridge=",
            "Inline Structure=",
            "Junction=",
            "Boundary=",
        ]
        stripped_line = line.strip()
        return any(stripped_line.startswith(indicator) for indicator in feature_indicators)

    def __str__(self):
        from .tools import pad_left

        s = f"Lateral Weir Centerline={self.num_points}\n"
        # Format coordinates in pairs, 16 characters wide, right aligned
        # Process pairs of coordinates (x, y) and put them on lines
        for i in range(0, len(self.points), 2):  # 2 pairs per line (4 coordinates)
            line_coords = self.points[i : i + 2]
            line_str = ""
            for pair in line_coords:
                x_coord = pad_left(pair[0], 16)
                y_coord = pad_left(pair[1], 16)
                line_str += x_coord + y_coord
            s += line_str + "\n"
        return s


class LateralWeir(object):
    def __init__(self, river, reach):
        self.river = river
        self.reach = reach

        # Initialize all Lateral Weir components
        self.header = Header()
        self.description = Description()
        self.node_name = LateralWeirNodeName()
        self.last_edited_time = LateralWeirLastEditedTime()
        self.pos = LateralWeirPosition()
        self.end = LateralWeirEnd()
        self.distance = LateralWeirDistance()
        self.tw_multiple_xs = LateralWeirTWMultipleXS()
        self.wd = LateralWeirWD()
        self.coef = LateralWeirCoef()
        self.overflow_method_2d = LateralWeirOverflowMethod2D()
        self.overflow_velocity_2d = LateralWeirOverflowVelocity2D()
        self.ws_criteria = LateralWeirWSCriteria()
        self.flap_gates = LateralWeirFlapGates()
        self.hagers_eqn = LateralWeirHagersEQN()
        self.ss = LateralWeirSS()
        self.se = LateralWeirSE()
        self.type = LateralWeirType()
        self.connection_pos_dist = LateralWeirConnectionPosDist()
        self.div_rc = LateralWeirDivRC()
        self.centerline = LateralWeirCenterline()

        # Define all parts that can be parsed
        self.parts = [
            self.header,
            self.description,
            self.node_name,
            self.last_edited_time,
            self.pos,
            self.end,
            self.distance,
            self.tw_multiple_xs,
            self.wd,
            self.coef,
            self.overflow_method_2d,
            self.overflow_velocity_2d,
            self.ws_criteria,
            self.flap_gates,
            self.hagers_eqn,
            self.ss,
            self.se,
            self.type,
            self.connection_pos_dist,
            self.div_rc,
            self.centerline,
        ]

        self.geo_list = []  # holds all parts and unknown lines (as strings)

    def import_geo(self, line, geo_file):
        # Process all parts until we've processed everything
        while line and self.parts:
            # Check if this line starts a new feature
            if self._is_new_feature(line):
                # Stop processing this lateral weir and return the line
                return line
            
            found_part = False
            for part in self.parts[:]:  # Use slice to iterate over a copy
                if hasattr(part, "test") and part.test(line):
                    # Special handling for LateralWeirSE to track number of points for station elevation
                    if isinstance(part, LateralWeirSE):
                        line = part.import_geo(line, geo_file)
                        # After importing, store reference to the processed SE part
                        self.parts.remove(part)
                        self.geo_list.append(part)
                        found_part = True
                        break
                    # Special handling for LateralWeirCenterline to track number of points for coordinates
                    elif isinstance(part, LateralWeirCenterline):
                        line = part.import_geo(line, geo_file)
                        # After importing, store reference to the processed centerline part
                        self.parts.remove(part)
                        self.geo_list.append(part)
                        found_part = True
                        break
                    else:
                        try:
                            line = part.import_geo(line, geo_file)
                        except StopIteration:
                            self.parts.remove(part)
                            self.geo_list.append(part)
                            break
                        self.parts.remove(part)
                        self.geo_list.append(part)
                        found_part = True
                        break

            if not found_part:
                # If no part matched, we might have reached the end or an unknown line
                # Store the line as-is and continue
                self.geo_list.append(line)
                try:
                    line = next(geo_file)
                except StopIteration:
                    break
            else:
                # Continue with the next line
                pass

        # Handle any remaining parts if needed
        # This could happen if the file ends but there are still unprocessed parts
        for remaining_part in self.parts[:]:
            self.parts.remove(remaining_part)
            self.geo_list.append(remaining_part)

    def _is_new_feature(self, line):
        """Check if line starts a new feature"""
        # Common indicators of new features in HEC-RAS geometry files
        feature_indicators = [
            "River Reach=",
            "Type RM Length L Ch R =",  # New river reach/cross section
            "Storage Area=",
            "SA/2D Flow Area=",
            "Lateral Weir Pos=",  # New lateral weir
            "Culvert=",
            "Bridge=",
            "Inline Structure=",
            "Junction=",
            "Boundary=",
        ]
        stripped_line = line.strip()
        return any(stripped_line.startswith(indicator) for indicator in feature_indicators)

    def __str__(self):
        s = ""
        # Build the string with proper ordering based on the original file format
        # Only add components that have been properly initialized
        
        # Add header if it has meaningful data
        if self.header and hasattr(self.header, 'station') and self.header.station is not None:
            s += str(self.header)
        
        # Add node name if it has meaningful data
        if self.node_name and hasattr(self.node_name, 'name') and self.node_name.name is not None:
            s += str(self.node_name)
        
        # Add last edited time if it has meaningful data
        if self.last_edited_time and hasattr(self.last_edited_time, 'time') and self.last_edited_time.time is not None:
            s += str(self.last_edited_time)
        
        # Add position if it has meaningful data
        if self.pos and hasattr(self.pos, 'pos') and self.pos.pos is not None:
            s += str(self.pos)
        
        # Add end if it has meaningful data
        if self.end and hasattr(self.end, 'end_values') and self.end.end_values is not None:
            s += str(self.end)
        
        # Add distance if it has meaningful data
        if self.distance and hasattr(self.distance, 'distance') and self.distance.distance is not None:
            s += str(self.distance)
        
        # Add TW multiple XS if it has meaningful data
        if self.tw_multiple_xs and hasattr(self.tw_multiple_xs, 'tw_multiple_xs') and self.tw_multiple_xs.tw_multiple_xs is not None:
            s += str(self.tw_multiple_xs)
        
        # Add WD if it has meaningful data
        if self.wd and hasattr(self.wd, 'width') and self.wd.width is not None:
            s += str(self.wd)
        
        # Add coefficient if it has meaningful data
        if self.coef and hasattr(self.coef, 'coefficient') and self.coef.coefficient is not None:
            s += str(self.coef)
        
        # Add overflow method 2D if it has meaningful data
        if self.overflow_method_2d and hasattr(self.overflow_method_2d, 'overflow_method') and self.overflow_method_2d.overflow_method is not None:
            s += str(self.overflow_method_2d)
        
        # Add overflow velocity 2D if it has meaningful data
        if self.overflow_velocity_2d and hasattr(self.overflow_velocity_2d, 'velocity') and self.overflow_velocity_2d.velocity is not None:
            s += str(self.overflow_velocity_2d)
        
        # Add WS criteria if it has meaningful data
        if self.ws_criteria and hasattr(self.ws_criteria, 'ws_criteria') and self.ws_criteria.ws_criteria is not None:
            s += str(self.ws_criteria)
        
        # Add flap gates if it has meaningful data
        if self.flap_gates and hasattr(self.flap_gates, 'flap_gates') and self.flap_gates.flap_gates is not None:
            s += str(self.flap_gates)
        
        # Add hagers equation if it has meaningful data
        if self.hagers_eqn and hasattr(self.hagers_eqn, 'hagers_eqn') and self.hagers_eqn.hagers_eqn is not None:
            s += str(self.hagers_eqn)
        
        # Add SS if it has meaningful data
        if self.ss and hasattr(self.ss, 'values') and self.ss.values is not None:
            s += str(self.ss)
        
        # Add type if it has meaningful data
        if self.type and hasattr(self.type, 'weir_type') and self.type.weir_type is not None:
            s += str(self.type)
        
        # Add connection pos dist if it has meaningful data
        if self.connection_pos_dist and hasattr(self.connection_pos_dist, 'connection_pos_dist') and self.connection_pos_dist.connection_pos_dist is not None:
            s += str(self.connection_pos_dist)
        
        # Add SE if it has meaningful data
        if self.se and hasattr(self.se, 'num_points') and self.se.num_points is not None:
            s += str(self.se)
        
        # Add centerline if it has meaningful data
        if self.centerline and hasattr(self.centerline, 'num_points') and self.centerline.num_points is not None:
            s += str(self.centerline)
        
        # Add LW Div RC if it has meaningful data
        if self.div_rc and hasattr(self.div_rc, 'div_rc') and self.div_rc.div_rc is not None:
            s += str(self.div_rc)

        return s

    @staticmethod
    def test(line):
        return Header.test(line)