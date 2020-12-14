
import flask_babel
from flask import jsonify, request, g
from app import models, db


def post(model_id, model_name):

    note = request.json.get('note', '')

    new_note = models.Note(
        note=note,
        model_name=model_name,
        model_id=model_id,
        created_by=g.request_user,
        updated_by=g.request_user
    )
    db.session.add(new_note)
    db.session.commit()

    return jsonify(new_note.__getstate__()), 200


def get(note_id):
    note = models.Note.query.get_or_404(note_id)
    return jsonify(note.__getstate__()), 200


def put(note_id):
    note = models.Note.query.get_or_404(note_id)

    new_note = request.json.get('note', None)

    if note and new_note is not None:
        note.note = new_note
        note.updated_by = g.request_user
        db.session.commit()

    return jsonify(note.__getstate__()), 200


def delete(note_id):
    note = models.Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()

    msg = flask_babel.gettext("Note successfully deleted.")
    return jsonify({"message": msg}), 200
