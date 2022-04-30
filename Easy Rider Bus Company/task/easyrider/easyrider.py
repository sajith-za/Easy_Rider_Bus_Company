from collections import defaultdict, Counter
import json
import re
import itertools
import time


# Write your awesome code here
def error_check(bus_dict1):
    error_dict = {key: 0 for key in bus_dict1[0].keys()}

    pattern_stop = re.compile(r"([A-Z][a-z]+\s)+(Road|Avenue|Boulevard|Street)$")
    pattern_time = re.compile(r"^[01]\d:[0-5]\d$")

    for obj in bus_dict1:
        for key, value in obj.items():

            if key in ("bus_id", "stop_id", "next_stop"):
                if not isinstance(value, int):
                    error_dict[key] += 1

            elif key in ("stop_name", "a_time"):
                if not isinstance(value, str):
                    error_dict[key] += 1

                else:
                    match = re.match(pattern_stop, value) if key == "stop_name" \
                        else re.match(pattern_time, value)

                    if match is None:
                        error_dict[key] += 1

            elif key == "stop_type" and value not in ("S", "O", "F", ""):
                error_dict[key] += 1

    print("Format validation:", sum(error_dict.values()))
    for key1, item1 in error_dict.items():
        if key1 in ("stop_name", "stop_type", "a_time"):
            print(key1 + ":", item1)


def bus_stop_list(bus_dict2):
    bus_stop = defaultdict(list)
    bus_identifier = 0
    stop_identifier = 0

    for obj in bus_dict2:
        for key, value in obj.items():

            if key == "bus_id":
                bus_identifier = value

            if key == "stop_id":
                stop_identifier = value

            if bus_identifier != 0 and stop_identifier != 0:
                bus_stop[bus_identifier].append(stop_identifier)

                bus_identifier = 0
                stop_identifier = 0
    print("Line names and number of stops:")

    for key, value in bus_stop.items():
        print(f'bus_id: {key}, stops: {len(Counter(value).keys())}')

    print(bus_stop)


def bus_name_list(bus_dict2):
    bus_name = defaultdict(list)
    bus_stop_type = defaultdict(list)
    bus_arrival_time = defaultdict(list)

    bus_identifier = 0
    stop_name = None
    stop_type = None
    arrival_time = None

    # Not sure now to optimise this, hence re-using / redoing this code
    for obj in bus_dict2:
        for key, value in obj.items():

            if key == "bus_id":
                bus_identifier = value

            if key == "stop_name":
                stop_name = value

            if key == "stop_type":
                stop_type = value

            if key == "a_time":
                arrival_time = time.strptime(value, '%H:%M')

            if bus_identifier != 0:
                if stop_name is not None:
                    bus_name[bus_identifier].append(stop_name)
                    stop_name = None

                if stop_type is not None:
                    bus_stop_type[bus_identifier].append(stop_type)
                    stop_type = None

                if arrival_time is not None:
                    bus_arrival_time[bus_identifier].append(arrival_time)
                    arrival_time = None
                    bus_identifier = 0

    # Next step would be to zip the two dictionaries and do the analysis

    stage4_checks(bus_stop_type, bus_name)
    # stage5_checks(bus_name, bus_arrival_time)


def stage5_checks(bus_name, bus_arrival_time):
    arrival_test = {}
    default_time = time.strptime('01:00', '%H:%M')

    # 1st Test time is set at 1 o' clock as first travel time is actually at 8AM
    x_time = default_time

    for (k, v1), v2 in zip(bus_arrival_time.items(), bus_name.values()):

        for v4, v5 in zip(v1, v2):

            # Checking if next stop's time is less than the previously read one
            if v4 <= x_time:
                arrival_test[k] = v5
                break

            x_time = v4

        # Change in bus routes thus setting x-time to default value
        x_time = default_time

    print("Arrival time test:")
    for k, v in arrival_test.items():
        print(f'bus_id line {k}: wrong time on station {v}')
    else:
        print('OK' if not arrival_test else "")


def stage4_checks(bus_stop_type, bus_name):
    # Step 1: Testing First Condition - that there is one start and one end stop for the stops
    test = check_bus_start_stop(bus_stop_type)
    if test != 0:
        print(f"There is no start or end stop for the line: {test}.")
        return

    # Step 2: Carrying out analysis to identify start, transition and stop stations
    start_list = set()
    transition_list = set()
    finish_list = set()
    on_demand_list = set()

    # Creating zips to link bus stops to bus stop types
    for v1, v2 in zip(bus_name.values(), bus_stop_type.values()):

        for v3, v4 in zip(v1, v2):
            # Checking the start stops
            if v4 == "S":
                start_list.add(v3)

            # Check finish stops
            if v4 == "F":
                finish_list.add(v3)

            if v4 == "O":
                on_demand_list.add(v3)

    # Find in the intersections of the different routes
    my_iter = itertools.combinations(bus_name.values(), 2)
    route_combinations = list(my_iter)

    for route in route_combinations:
        transition_list.update(set(route[0]) & set(route[1]))

    """ Commenting out stage 4 requirements
    
    print(f'Start stops: {len(start_list)} {sorted(list(start_list))}')
    print(f'Transfer stops: {len(transition_list)} {sorted(list(transition_list))}')
    print(f'Finish stops: {len(finish_list)} {sorted(list(finish_list))}')
    """

    terminal_stations = (start_list | transition_list | finish_list)
    intersection_test = terminal_stations & on_demand_list
    print("On demand stops test:")
    print("OK" if len(intersection_test) == 0 \
              else f'Wrong stop type: {sorted(list(intersection_test))}')


def check_bus_start_stop(buses):
    counter = 0

    """ Assigning 2 to a start and 3 to stop, in order to ensure
        that the start stops aren't double counted for check
    """
    for k, v in buses.items():
        for elements in v:
            if elements == "S":
                counter += 2
            elif elements == "F":
                counter += 3

        if counter != 5:
            return k
        else:
            counter = 0
    pass

    return 0


if __name__ == '__main__':
    test_string = '''
[
    {
        "bus_id": 512,
        "stop_id": 4,
        "stop_name": "Bourbon Street",
        "next_stop": 6,
        "stop_type": "S",
        "a_time": "08:13"
    },
    {
        "bus_id": 512,
        "stop_id": 6,
        "stop_name": "Sunset Boulevard",
        "next_stop": 0,
        "stop_type": "F",
        "a_time": "08:16"
    }
]
    '''
    # Using test string for now otherwise use input()
    bus_dict = json.loads(input())
    # error_check(bus_dict)
    # bus_stop_list(bus_dict)
    bus_name_list(bus_dict)
