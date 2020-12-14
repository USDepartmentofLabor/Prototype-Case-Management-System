from datetime import datetime

import flask_babel
import flask_cloudy
from PIL import UnidentifiedImageError
from flask import jsonify, current_app, g, request
import app
from app import helpers, models


def post(model_id, model_name):
    file = request.files.get('file')

    current_app.logger.info(f'Files: {request.files}')

    if not file:
        msg = flask_babel.gettext('No file uploaded')
        return jsonify({'message': msg}), 400

    try:
        upload = app.storage.upload(file,
                                    acl=None)  # ACL set to none to avoid libcloud bug in generating invalid signature
    except flask_cloudy.InvalidExtensionError as error:
        msg = flask_babel.gettext('Invalid file extension for upload')
        return jsonify({'message': msg}), 400

    document_id = request.form.get('document_id') or None

    if document_id:
        document_id = document_id

        files = models.UploadedFile.query.filter_by(document_id=document_id).all()

        for f in files:
            remote_file = app.storage.get(f.remote_filename)
            remote_file.delete()

            app.db.session.delete(f)

    # TODO: get uploaded location details from form
    uploaded_location_latitude = helpers.get_gps_value(request.form, 'uploaded_location_latitude')
    uploaded_location_longitude = helpers.get_gps_value(request.form, 'uploaded_location_longitude')
    uploaded_location_position_accuracy = helpers.get_gps_value(request.form, 'uploaded_location_position_accuracy')
    uploaded_location_altitude = helpers.get_gps_value(request.form, 'uploaded_location_altitude')
    uploaded_location_altitude_accuracy = helpers.get_gps_value(request.form, 'uploaded_location_altitude_accuracy')
    uploaded_location_heading = helpers.get_gps_value(request.form, 'uploaded_location_heading')
    uploaded_location_speed = helpers.get_gps_value(request.form, 'uploaded_location_speed')
    got_uploaded_location_data = any([uploaded_location_latitude is not None and
                                      uploaded_location_longitude is not None,
                                      uploaded_location_position_accuracy is not None,
                                      uploaded_location_altitude is not None,
                                      uploaded_location_altitude_accuracy is not None,
                                      uploaded_location_heading is not None,
                                      uploaded_location_speed is not None])
    if got_uploaded_location_data:
        coordinates = f"POINT({uploaded_location_longitude} {uploaded_location_latitude})"
        uploaded_location = models.Location(coordinates=coordinates,
                                            position_accuracy=uploaded_location_position_accuracy,
                                            altitude=uploaded_location_altitude,
                                            altitude_accuracy=uploaded_location_altitude_accuracy,
                                            heading=uploaded_location_heading,
                                            location_speed=uploaded_location_speed,
                                            location_dt=datetime.utcnow())
    else:
        uploaded_location = None

    # TODO: get taken location details from form
    taken_location_latitude = helpers.get_gps_value(request.form, 'taken_location_latitude')
    taken_location_longitude = helpers.get_gps_value(request.form, 'taken_location_longitude')
    taken_location_position_accuracy = helpers.get_gps_value(request.form, 'taken_location_position_accuracy')
    taken_location_altitude = helpers.get_gps_value(request.form, 'taken_location_altitude')
    taken_location_altitude_accuracy = helpers.get_gps_value(request.form, 'taken_location_accuracy')
    taken_location_heading = helpers.get_gps_value(request.form, 'taken_location_heading')
    taken_location_speed = helpers.get_gps_value(request.form, 'taken_location_speed')
    got_taken_location_data = any([taken_location_latitude is not None and
                                   taken_location_longitude is not None,
                                   taken_location_position_accuracy is not None,
                                   taken_location_altitude is not None,
                                   taken_location_altitude_accuracy is not None,
                                   taken_location_heading is not None,
                                   taken_location_speed is not None])
    if got_taken_location_data:
        coordinates = f"POINT({taken_location_longitude} {taken_location_latitude})"
        taken_location = models.Location(coordinates=coordinates,
                                         position_accuracy=taken_location_position_accuracy,
                                         altitude=taken_location_altitude,
                                         altitude_accuracy=taken_location_altitude_accuracy,
                                         heading=taken_location_heading,
                                         location_speed=taken_location_speed,
                                         location_dt=datetime.utcnow())
    else:
        taken_location = None

    try:
        exif = helpers.get_exif(file)
        geotags = helpers.get_geotagging(exif)
        extracted_latitude, extracted_longitude = helpers.get_coordinates(geotags)
        current_app.logger.error(f"{file.filename} extracted location ({extracted_latitude}, {extracted_longitude})")
        coordinates = f"POINT({extracted_longitude} {extracted_latitude})"
        extracted_location = models.Location(coordinates=coordinates, location_dt=datetime.utcnow())
    except ValueError:
        extracted_location = None
        current_app.logger.info(f"{file.filename} did not contain location information")
    except UnidentifiedImageError as uie:
        extracted_location = None
        current_app.logger.info(uie)
    except Exception as ex:
        extracted_location = None
        current_app.logger.exception(f"Error trying to extract location information from {file.filename}")

    uploaded_file = models.UploadedFile(
        model_name=model_name,
        model_id=model_id,
        document_id=document_id,
        original_filename=file.filename,
        remote_filename=upload.name,
        uploaded_location=uploaded_location,
        taken_location=taken_location,
        extracted_location=extracted_location,
        created_by=g.request_user,
    )

    app.db.session.add(uploaded_file)
    app.db.session.commit()

    return jsonify(uploaded_file.__getstate__()), 200


def get(file_id):
    file = models.UploadedFile.query.get_or_404(file_id)
    return jsonify(file.__getstate__()), 200


def delete(file_id):
    activity_file = models.UploadedFile.query.get_or_404(file_id)

    file = app.storage.get(activity_file.remote_filename)
    if file:
        file.delete()

    app.db.session.delete(activity_file)

    if activity_file.uploaded_location:
        app.db.session.delete(activity_file.uploaded_location)
    if activity_file.taken_location:
        app.db.session.delete(activity_file.taken_location)
    if activity_file.extracted_location:
        app.db.session.delete(activity_file.extracted_location)

    app.db.session.commit()

    msg = flask_babel.gettext('File successfully deleted')
    return jsonify({'message': msg}), 200


def download(file_id):
    activity_file = models.UploadedFile.query.get_or_404(file_id)
    file = app.storage.get(activity_file.remote_filename)
    url = file.download_url(timeout=60)
    return jsonify({'url': url}), 200
