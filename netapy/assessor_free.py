import ast

class Assessor():

    # Definitions, e.g. "footpath" <=> OSM tags
    def __init__(self):

        # Conditions as objects
        self.is_segregated = lambda x: any(key for key, value in x.items() if
                                      'segregated' in key and value == 'yes')  # and no "nos" in segregated, zB 4746913 hat cycleway:left:segregated = no !
        self.is_footpath = lambda x: x.get("highway") in ["footway", "pedestrian"]
        self.is_not_accessible = lambda x: x.get("access") == "no"
        self.use_sidepath = lambda x: any(key for key, value in x.items() if 'bicycle' in key and value == 'use_sidepath')

        self.is_indoor = lambda x: x.get('indoor') == 'yes'
        self.is_path = lambda x: x.get("highway") in ["path"]
        self.is_track = lambda x: x.get("highway") in ["track"]

        self.can_walk_right = lambda x: (x.get("foot") in ["yes", "designated"]
                                    or any(
                    key for key, value in x.items() if 'right:foot' in key and value in ['yes', 'designated'])
                                    or x.get("sidewalk") in ["yes", "separated", "both", "right", "left"]
                                    or x.get("sidewalk:right") in ["yes", "separated", "both", "right"]
                                    or x.get("sidewalk:both") in ["yes", "separated", "both"])

        self.can_walk_left = lambda x: (x.get("foot") in ["yes", "designated"]
                                   or any(
                    key for key, value in x.items() if 'left:foot' in key and value in ['yes', 'designated'])
                                   or x.get("sidewalk") in ["yes", "separated", "both", "right", "left"]
                                   or x.get("sidewalk:left") in ["yes", "separated", "both", "left"]
                                   or x.get("sidewalk:both") in ["yes", "separated", "both"])

        self.can_bike = lambda x: (x.get("bicycle") in ["yes", "designated"]
                              and x.get("highway") not in ['motorway', 'motorway_link'])  # should we add permissive?

        self.cannot_bike = lambda x: (x.get("bicycle") in ["no", "dismount", 'use_sidepath'] or
                                 x.get("highway") in ['corridor', 'motorway', 'motorway_link', 'trunk', 'trunk_link'] or
                                 x.get("access") in ['customers'])

        self.is_obligated_segregated = lambda x: (
                ('traffic_sign' in x.keys() and isinstance(x['traffic_sign'], str) and '241' in x['traffic_sign'])
                or ('traffic_sign:forward' in x.keys() and isinstance(x['traffic_sign:forward'], str) and '241' in x[
            'traffic_sign:forward'])
        )

        self.is_designated = lambda x: x.get("bicycle") == "designated"

        self.is_bicycle_designated_left = lambda x: ((self.is_designated(x) or
                                                 (x.get("cycleway:left:bicycle") == "designated")) or
                                                (x.get("cycleway:bicycle") == "designated"))

        self.is_bicycle_designated_right = lambda x: (self.is_designated(x) or
                                                 (x.get("cycleway:right:bicycle") == "designated") or
                                                 (x.get("cycleway:bicycle") == "designated"))

        self.is_pedestrian_designated_left = lambda x: (x.get("foot") == "designated" or
                                                   x.get("sidewalk:left:foot") == "designated" or
                                                   x.get("sidewalk:foot") == "designated")

        self.is_pedestrian_designated_right = lambda x: (x.get("foot") == "designated" or
                                                    x.get("sidewalk:right:foot") == "designated" or
                                                    x.get("sidewalk:foot") == "designated")

        self.is_service_tag = lambda x: x.get("highway") in ["service"]  # , "living_street"]
        self.is_agricultural = lambda x: x.get("motor_vehicle") in ["agricultural", "forestry"]
        self.is_accessible = lambda x: x.get("access") is None or not self.is_not_accessible(x)
        self.is_smooth = lambda x: x.get("tracktype") is None or x.get("tracktype") in ["grade1", "grade2"]
        self.is_vehicle_allowed = lambda x: x.get("motor_vehicle") is None or x.get("motor_vehicle") != "no"

        self.is_service = lambda x: (self.is_service_tag(x) or
                                (self.is_agricultural(x) and self.is_accessible(x)) or
                                (self.is_path(x) and self.is_accessible(x)) or
                                (self.is_track(x) and self.is_accessible(x) and self.is_smooth(x) and self.is_vehicle_allowed(
                                    x))) and not self.is_designated(x)

        self.can_cardrive = lambda x: x.get("highway") in ["motorway", "trunk", "primary", "secondary", "tertiary",
                                                  "unclassified", "road",
                                                  "residential", "living_street",
                                                  "primary_link", "secondary_link", "tertiary_link", 'motorway_link',
                                                  'trunk_link']

        self.is_path_not_forbidden = lambda x: ((x.get("highway") in ["cycleway", "track", "path"])
                                           and not self.cannot_bike(x))

        self.is_bikepath_right = lambda x: (x.get("highway") in ["cycleway"]
                                       or (any(
                    key for key, value in x.items() if 'right:bicycle' in key and value in ['designated'])
                                           and not any(key for key, value in x.items() if key == 'cycleway:right:lane'))
                                       or x.get("cycleway") in ["track", "sidepath", "crossing"]
                                       or x.get("cycleway:right") in ["track", "sidepath", "crossing"]
                                       or x.get("cycleway:both") in ["track", "sidepath", "crossing"]
                                       or any(
                    key for key, value in x.items() if 'right:traffic_sign' in key and value in ['237']))
        self.is_bikepath_left = lambda x: (x.get("highway") in ["cycleway"]
                                      or (any(
                    key for key, value in x.items() if 'left:bicycle' in key and value in ['designated'])
                                          and not any(key for key, value in x.items() if key == 'cycleway:left:lane'))
                                      or x.get("cycleway") in ["track", "sidepath", "crossing"]
                                      or x.get("cycleway:left") in ["track", "sidepath", "crossing"]
                                      or x.get("cycleway:both") in ["track", "sidepath", "crossing"]
                                      or any(
                    key for key, value in x.items() if 'left:traffic_sign' in key and value in ['237']))

        ##infrastructure designated for pedestrians

        self.is_pedestrian_right = lambda x: ((self.is_footpath(x) and not self.can_bike(x) and not self.is_indoor(x))
                                          or (self.is_path(x) and self.can_walk_right(x) and not self.can_bike(x) and not self.is_indoor(x)))
        self.is_pedestrian_left = lambda x: ((self.is_footpath(x) and not self.can_bike(x) and not self.is_indoor(x))
                                        or (self.is_path(x) and self.can_walk_left(x) and not self.can_bike(x) and not self.is_indoor(x)))
        ### Begin categories


        self.is_cycle_highway = lambda x: (x.get("cycle_highway") == "yes")

        ##bicycle_road
        self.is_bikeroad = lambda x: (x.get("bicycle_road") == "yes" or x.get("cyclestreet") == "yes")

        ##Straßenbegleitender Radweg benutzungspflichtig
        self.is_bikelane_right = lambda x: (x.get("cycleway") in ["lane", "shared_lane"]
                                       or x.get("cycleway:right") in ["lane", "shared_lane"]
                                       or x.get("cycleway:both") in ["lane", "shared_lane"]
                                       or any(
                    key for key, value in x.items() if 'right:lane' in key and value in ['exclusive']))

        self.is_bikelane_left = lambda x: (x.get("cycleway") in ["lane", "shared_lane"]
                                      or x.get("cycleway:left") in ["lane", "shared_lane"]
                                      or x.get("cycleway:both") in ["lane", "shared_lane"]
                                      or any(
                    key for key, value in x.items() if 'left:lane' in key and value in ['exclusive']))

        ##schutzstreifen/radfahrstreifen
        ##bus
        self.is_buslane_right = lambda x: (x.get("cycleway") == "share_busway"
                                      or x.get("cycleway:right") == "share_busway"
                                      or x.get("cycleway:both") == "share_busway")
        self.is_buslane_left = lambda x: (x.get("cycleway") == "share_busway"
                                     or x.get("cycleway:left") == "share_busway"
                                     or x.get("cycleway:both") == "share_busway")

    # Maps an OSM way to a Radsim cycling infrastructure category.
    #
    # @param `sides` The category complexity, e.g. either `bicycle_way` or `bicycle_way_right_no[ne]_left`:
    # @param `x` The OSM way to categorize.
    # @returns The Radsim category as String, e.g. `bicycle_way_right_no_left`.
    def set_value(self, x, sides = "double"):

        # ------------ conditions ------------

        # `bicycle_way` (right/left)
        conditions_b_way_right = [
            self.is_bikepath_right(x) and not self.can_walk_right(x),  # 0 and 1
            self.is_bikepath_right(x) and self.is_segregated(x),  # 0 and 2
            self.can_bike(x) and (self.is_path(x) or self.is_track(x)) and not self.can_walk_right(x),  # and not is_footpath, #3, 4, 1
            self.can_bike(x) and (self.is_track(x) or self.is_footpath(x) or self.is_path(x)) and self.is_segregated(x),  # b_way_right_5 #3, 6, 2
            self.can_bike(x) and self.is_obligated_segregated(x),  # 3,7
            self.is_bicycle_designated_right and self.is_pedestrian_designated_right(x) and self.is_segregated(x)
        ]
        conditions_b_way_left = [
            self.is_bikepath_left(x) and not self.can_walk_left(x),  # 0 and 1
            self.is_bikepath_left(x) and self.is_segregated(x),  # 0 and 2
            self.can_bike(x) and (self.is_path(x) or self.is_track(x)) and not self.can_walk_left(x),  # and not is_footpath, #3, 4, 1
            self.can_bike(x) and (self.is_track(x) or self.is_footpath(x) or self.is_path(x)) and self.is_segregated(x),  # b_way_right_5 #3, 6, 2
            self.can_bike(x) and self.is_obligated_segregated(x),  # 3,7
            self.is_bicycle_designated_left and self.is_pedestrian_designated_left(x) and self.is_segregated(x)
        ]

        # `mixed_way` (right/left)
        conditions_mixed_right = [
            self.is_bikepath_right(x) and self.can_walk_right(x) and not self.is_segregated(x),  # 0 and 1 and 2
            self.is_footpath(x) and self.can_bike(x) and not self.is_segregated(x),  # 3 and 4 and 2
            (self.is_path(x) or self.is_track(x)) and self.can_bike(x) and self.can_walk_right(x) and not self.is_segregated(x)  # 5 and 4 and 1 and 2
        ]
        conditions_mixed_left = [
            self.is_bikepath_left(x) and self.can_walk_left(x) and not self.is_segregated(x),  # 0 and 1 and 2
            self.is_footpath(x) and self.can_bike(x) and not self.is_segregated(x),  # 3 and 4 and 2
            (self.is_path(x) or self.is_track(x)) and self.can_bike(x) and self.can_walk_left(x) and not self.is_segregated(x)  # 5 and 4 and 1 and 2
        ]

        # `mit_road` (right/left)
        conditions_mit_right = [
            self.can_cardrive(x) and not self.is_bikepath_right(x) and not self.is_bikeroad(x) and not self.is_footpath(x) and not self.is_bikelane_right(x) and not self.is_buslane_right(x)
            and not self.is_path(x) and not self.is_track(x) and not self.cannot_bike(x),
        ]
        conditions_mit_left = [
            self.can_cardrive(x) and not self.is_bikepath_left(x) and not self.is_bikeroad(x) and not self.is_footpath(x) and not self.is_bikelane_left(x) and not self.is_buslane_left(x)
            and not self.is_path(x) and not self.is_track(x) and not self.cannot_bike(x),
        ]

        # Map to complex categories (w/ right_left) - relevant for OSM -> Radsim Mapping
        if sides == "double":

            # Map function
            def get_infra(x):

                if ('access' in x.values() and self.is_not_accessible(x)) or ('tram' in x.values() and x['tram'] == 'yes'):
                    return 'no'  # unpacked from "service"
                # remove service right away

                if self.is_service(x):
                    return "service_misc"

                if self.is_cycle_highway(x):
                    return "cycle_highway"

                #### 3 # new option: "bicycle_road"
                if self.is_bikeroad(x):
                    return "bicycle_road"

                #### 1
                elif any(conditions_b_way_right):
                    if any(conditions_b_way_left):
                        return "bicycle_way_both"
                    elif self.is_bikelane_left(x):
                        return "bicycle_way_right_lane_left"
                    elif self.is_buslane_left(x):
                        return "bicycle_way_right_bus_left"
                    elif any(conditions_mixed_left):
                        return "bicycle_way_right_mixed_left"
                    elif any(conditions_mit_left):
                        return "bicycle_way_right_mit_left"
                    elif self.is_pedestrian_left(x):
                        return "bicycle_way_right_pedestrian_left"
                    else:
                        return "bicycle_way_right_no_left"

                elif any(conditions_b_way_left):
                    if self.is_bikelane_right(x):
                        return "bicycle_way_left_lane_right"
                    elif self.is_buslane_right(x):
                        return "bicycle_way_left_bus_right"
                    elif any(conditions_mixed_right):
                        return "bicycle_way_left_mixed_right"
                    elif any(conditions_mit_right):
                        return "bicycle_way_left_mit_right"
                    elif self.is_pedestrian_right(x):
                        return "bicycle_way_left_pedestrian_right"
                    else:
                        return "bicycle_way_left_no_right"

                #### 4 # Third option: "bicycle_lane"
                elif self.is_bikelane_right(x):
                    if self.is_bikelane_left(x):
                        return "bicycle_lane_both"
                    elif self.is_buslane_left(x):
                        return "bicycle_lane_right_bus_left"
                    elif any(conditions_mixed_left):
                        return "bicycle_lane_right_mixed_left"
                    elif any(conditions_mit_left):
                        return "bicycle_lane_right_mit_left"
                    elif self.is_pedestrian_left(x):
                        return "bicycle_lane_right_pedestrian_left"
                    else:
                        return "bicycle_lane_right_no_left"

                elif self.is_bikelane_left(x):
                    if self.is_buslane_right(x):
                        return "bicycle_lane_left_bus_right"
                    elif any(conditions_mixed_right):
                        return "bicycle_lane_left_mixed_right"
                    elif any(conditions_mit_right):
                        return "bicycle_lane_left_mit_right"
                    elif self.is_pedestrian_right(x):
                        return "bicycle_lane_left_pedestrian_right"
                    else:
                        return "bicycle_lane_left_no_right"

                #### 5 # Fourth option: "bus_lane"
                elif self.is_buslane_right(x):
                    if self.is_buslane_left(x):
                        return "bus_lane_both"
                    elif any(conditions_mixed_left):
                        return "bus_lane_right_mixed_left"
                    elif any(conditions_mit_left):
                        return "bus_lane_right_mit_left"
                    elif self.is_pedestrian_left(x):
                        return "bus_lane_right_pedestrian_left"
                    else:
                        return "bus_lane_right_no_left"

                elif self.is_buslane_left(x):
                    if any(conditions_mixed_right):
                        return "bus_lane_left_mixed_right"
                    elif any(conditions_mit_right):
                        return "bus_lane_left_mit_right"
                    elif self.is_pedestrian_right(x):
                        return "bus_lane_left_pedestrian_right"
                    else:
                        return "bus_lane_left_no_right"


                #### 2
                elif any(conditions_mixed_right):
                    if any(conditions_mixed_left):
                        return "mixed_way_both"
                    elif any(conditions_mit_left):
                        return "mixed_way_right_mit_left"
                    elif self.is_pedestrian_left(x):
                        return "mixed_way_right_pedestrian_left"
                    else:
                        return "mixed_way_right_no_left"

                elif any(conditions_mixed_left):
                    if any(conditions_mit_right):
                        return "mixed_way_left_mit_right"
                    elif self.is_pedestrian_right(x):
                        return "mixed_way_left_pedestrian_right"
                    else:
                        return "mixed_way_left_no_right"

                #### 6
                elif any(conditions_mit_right):
                    if any(conditions_mit_left):
                        return "mit_road_both"
                    elif self.is_pedestrian_left(x):
                        return "mit_road_right_pedestrian_left"
                    else:
                        return "mit_road_right_no_left"

                elif any(conditions_mit_left):
                    if self.is_pedestrian_right(x):
                        return "mit_road_left_pedestrian_right"
                    else:
                        return "mit_road_left_no_right"

                #### 8
                elif self.is_pedestrian_right(x) and (not 'indoor' in x.values() or (x['indoor'] != 'yes')):
                    if self.is_pedestrian_left(x) and (not 'indoor' in x.values() or (x['indoor'] != 'yes')):
                        if 'access' in x.values() and x['access'] == 'customers':
                            return "no"
                        else:
                            return "pedestrian_both"
                    else:
                        return "pedestrian_right_no_left"


                elif self.is_pedestrian_left(x) and (not 'indoor' in x.values() or (x['indoor'] != 'yes')):
                    if 'access' in x.values() and x['access'] == 'customers':
                        return "no"
                    else:
                        return "pedestrian_left_no_right"

                elif self.is_path_not_forbidden(x):
                    return "path_not_forbidden"

                #### Fallback option: "no"
                else:
                    return "no"

            return get_infra(x) # Validate NOT NULL

# Function to parse the custom OSM tags format
def parse_osm_tags(input_str):
    # Remove the surrounding braces
    if input_str.startswith('{') and input_str.endswith('}'):
        input_str = input_str[1:-1]
    else:
        raise ValueError("Input must start with '{' and end with '}'")
    # Split by commas to get key=value pairs
    items = input_str.split(',')
    tags = {}
    for item in items:
        # Split by '='
        key_value = item.strip().split('=')
        if len(key_value) != 2:
            raise ValueError(f"Invalid key=value pair: {item}")
        key, value = key_value
        key = key.strip()
        value = value.strip()
        tags[key] = value
    return tags

if __name__ == "__main__":
    assessor = Assessor()
    print("Please enter the OSM tags to test-map.")
    print("Enter the tags in the format:")
    print("{key1=value1, key2=value2, ...}")
    print("Example:")
    print("{highway=path, bicycle=designated}")
    user_input = input("Enter OSM tags: ")

    try:
        # Parse the input string using the custom parser
        test_tags = parse_osm_tags(user_input)
        result = assessor.set_value(test_tags)
        print()
        print(f"This maps to: {result}")
    except ValueError as e:
        print("Invalid input. Please enter the tags in the correct format.")
        print(f"Error: {e}")
