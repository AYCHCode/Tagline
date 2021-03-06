import os
import requests
import json

from planar import BoundingBox

from model import Tag, connect_to_db

# import logging
# logging.basicConfig()
# logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


api_key = os.environ['GOOGLE_DIRECTIONS_API_KEY']


# origin = '1523 8th St, Oakland, CA 94607'
# destination = '1555 40th St, Emeryville, CA 94608'

def find_tags_on_route(origin, destination):
    """Returns list of tags along user's input route."""

    route_coordinates = find_route_coordinates(origin, destination)

    bbox = find_bounding_box(route_coordinates)

    return query_tags(bbox)


###### HELPER FUNCTIONS ##########################################

def find_route_coordinates(origin, destination):
    """Returns list of coordinates for segments of route path from Google Maps"""

    payload = {'origin': origin,
            'destination': destination,
            # 'key': api_key,
            'mode':'walking'
            }

    r = requests.get(
        "https://maps.googleapis.com/maps/api/directions/json",
        params=payload)

    directions = r.json()

    #unravel json to identify the route segments for route
    route_segments = directions['routes'][0]['legs'][0]['steps']

    #then identify the lat/long sequence for the segments
    s = 'start_location'
    e = 'end_location'

    route_segment_coords = [(segment[s]['lat'], segment[s]['lng']) for segment in route_segments] + [(segment[e]['lat'], segment[e]['lng'])]

    return route_segment_coords



def find_bounding_box(route_coordinates):
    """Returns rough bounding box for given route coordinates to help query tags along route. 
    Currently draws a rectangle around each set of long/lat points that make a path segment. 

    >>> find_bounding_box([(37,122),(36,123),(36,122)])
    [BoundingBox([(35.999, 121.999), (37.001, 123.001)]), BoundingBox([(35.999, 121.999), (36.001, 123.001)])]
    >>>  

    """

    bboxes = []

    for i in range(len(route_coordinates)-1):
        bbox = BoundingBox([route_coordinates[i],route_coordinates[i+1]])
        bbox = bbox.inflate(.002)
        bboxes.append(bbox)
        i += 1


    return bboxes



def query_tags(bboxes):
    """Returns list of landmark objects from database that fall within given bounding box."""

    all_tags = []

    for bbox in bboxes:

        min_lat = bbox.min_point[0]
        min_lng = bbox.min_point[1]
        max_lat = bbox.max_point[0]
        max_lng = bbox.max_point[1]

        tags = Tag.query.filter(Tag.latitude >= min_lat, 
                                        Tag.latitude <= max_lat,
                                        Tag.longitude >= min_lng,
                                        Tag.longitude <= max_lng).all()

        tags = Tag.query.filter(Tag.latitude >= min_lat, 
                                        Tag.latitude <= max_lat,
                                        Tag.longitude >= min_lng,
                                        Tag.longitude <= max_lng).order_by(Tag.tag_id.desc()).limit(4).all()
        all_tags += tags
    return all_tags



if __name__ == "__main__":

    from server import app
    connect_to_db(app)
    print "Connected to DB."

















