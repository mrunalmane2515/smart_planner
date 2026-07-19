import os

from flask import (
    Blueprint,
    redirect,
    send_from_directory,
    url_for,
    flash
)

from flask_login import (
    login_required,
    current_user
)

from models import db
from models.attachment import Attachment

attachment = Blueprint("attachment", __name__)

UPLOAD_FOLDER = "static/uploads"


@attachment.route("/attachment/download/<int:attachment_id>")
@login_required
def download_attachment(attachment_id):

    file = Attachment.query.get_or_404(attachment_id)

    return send_from_directory(
        UPLOAD_FOLDER,
        file.filename,
        as_attachment=True,
        download_name=file.original_filename
    )


@attachment.route("/attachment/preview/<int:attachment_id>")
@login_required
def preview_attachment(attachment_id):

    file = Attachment.query.get_or_404(attachment_id)

    return send_from_directory(
        UPLOAD_FOLDER,
        file.filename
    )


@attachment.route("/attachment/delete/<int:attachment_id>")
@login_required
def delete_attachment(attachment_id):

    file = Attachment.query.get_or_404(attachment_id)

    try:

        path = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        if os.path.exists(path):

            os.remove(path)

        db.session.delete(file)

        db.session.commit()

        flash(
            "Attachment deleted successfully.",
            "success"
        )

    except Exception:

        flash(
            "Unable to delete attachment.",
            "danger"
        )

    return redirect(request.referrer or "/")