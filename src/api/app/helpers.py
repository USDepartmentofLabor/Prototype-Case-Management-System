import functools
import sys
from datetime import datetime
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import flask
import flask_jwt_extended
import flask_babel
from py_metabase import metabase
from app import models


def bad_request(error_code):
    response = flask.jsonify(error_code.__getstate__())
    response.status_code = 400
    return response


def jwt_auth(fn):
    @functools.wraps(fn)
    @flask_jwt_extended.jwt_required
    def wrapped(*args, **kwargs):
        current_user = flask_jwt_extended.get_jwt_identity()
        request_user = models.User.query.filter_by(id=current_user).first()
        if request_user:
            flask.session['current_user_id'] = request_user.id
            flask.g.request_user = request_user
            request_user.ping()

            script_root = flask.request.script_root
            method = flask.request.method

            flask.current_app.logger.info(f'{script_root} {method} accessed by {request_user.email}')
        else:
            msg = flask_babel.gettext('Invalid token')
            return flask.jsonify({'message': msg}), 401

        return fn(*args, **kwargs)

    return wrapped


def role_restrict(roles, message=None, admin_allowed=True):
    def deco(fn):
        @functools.wraps(fn)
        def wrapped(*args, **kwargs):
            admin_perms = admin_allowed and flask.g.request_user.is_admin()
            if flask.g.request_user.can(roles) or admin_perms:
                return fn(*args, **kwargs)
            else:
                default_msg = flask_babel.gettext("You are not authorized to access this endpoint")
                return flask.jsonify({"message": message or default_msg}), 401

        return wrapped

    return deco


def get_metabase_connection():
    try:
        return metabase.Metabase(
            host=flask.current_app.config['METABASE_URL'],
            username=flask.current_app.config['METABASE_USERNAME'],
            password=flask.current_app.config['METABASE_PASSWORD'],
            auth_id=flask.current_app.config['METABASE_AUTH_ID']
        )
    except:
        e = sys.exc_info()[0]
        raise ConnectionError(f"The was an issue connecting to Metabase: {e}")


def get_metabase_database_id(metabase_connection, data_db_name):
    dbs = metabase_connection.get_all_databases()
    filtered_dbs = [db.id for db in dbs if db.dbname == data_db_name]
    return filtered_dbs[0] if len(filtered_dbs) > 0 else 0


def metabase_rescan():
    flask.current_app.logger.info('Triggering metabase rescan.')
    try:
        mb_conn = get_metabase_connection()
        database_id = get_metabase_database_id(mb_conn, flask.current_app.config['DATA_DB'])
        mb_conn.refresh_database(database_id)
    except:
        e = sys.exc_info()[0]
        flask.current_app.logger.error(f"Error trying to run Metabase rescan: {e}")


def is_number(value):
    if value is None:
        return False

    try:
        float(value)
        return True
    except ValueError:
        return False


def get_gps_value(json, key):
    gps_value = json.get(key, None)
    return gps_value if is_number(gps_value) else None


def parse_gps(json):
    latitude = get_gps_value(json, 'latitude')
    longitude = get_gps_value(json, 'longitude')
    position_accuracy = get_gps_value(json, 'position_accuracy')
    altitude = get_gps_value(json, 'altitude')
    altitude_accuracy = get_gps_value(json, 'altitude_accuracy')
    heading = get_gps_value(json, 'heading')
    speed = get_gps_value(json, 'speed')

    got_location_data = any([latitude is not None and longitude is not None, position_accuracy is not None,
                             altitude is not None, altitude_accuracy is not None, heading is not None,
                             speed is not None])
    location_dt = datetime.utcnow() if got_location_data else None

    return models.GeoLocation(latitude, longitude, position_accuracy, altitude, altitude_accuracy, heading, speed,
                              location_dt)


# functions for extracting Exif information from pictures

def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")

    geotagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geotagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geotagging[val] = exif[idx][key]

    return geotagging


def get_decimal_from_dms(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0

    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds

    return round(degrees + minutes + seconds, 5)


def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])

    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])

    return lat, lon
