import os
import time
import subprocess
from flask import Blueprint, current_app, request
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import ddmail_validators.validators as validators

bp = Blueprint("application", __name__, url_prefix="/")


@bp.route("/", methods=["POST"])
def main():
    if request.method == 'POST':
        ph = PasswordHasher()

        password = request.form.get('password')
        domain = request.form.get('domain')
        email = request.form.get('email')

        # Validate password.
        if validators.is_password_allowed(password) is not True:
            current_app.logger.error("password validation failed")
            return "error: password validation failed"

        # Validate domain.
        if validators.is_domain_allowed(domain) is not True:
            current_app.logger.error("domain validation failed")
            return "error: domain validation failed"

        # Validate email.
        if validators.is_email_allowed(email) is not True:
            current_app.logger.error("domain validation failed")
            return "error: email validation failed"

        # Check if password is correct.
        try:
            if ph.verify(current_app.config["PASSWORD_HASH"], password) is not True:
                time.sleep(1)
                current_app.logger.error("wrong password")
                return "error: wrong password"
        except VerifyMismatchError:
            time.sleep(1)
            current_app.logger.error("VerifyMismatchError, wrong password")
            return "error: wrong password"
        time.sleep(1)

        # Split email and verify domain.
        splitted_email_domain = email.split('@')
        if splitted_email_domain[1] != domain:
            current_app.logger.error("email address domain do no match domain")
            return "error: email adress domain do not match domain"

        # Path to email folder on disc.
        email_path = current_app.config["EMAIL_ACCOUNT_PATH"] + "/" + domain + "/" + splitted_email_domain[0]

        # location of rm binary.
        rm = "/usr/bin/rm"

        # Check that rm exist.
        if os.path.exists(rm) is not True:
            current_app.logger.error("rm binary location is wrong")
            return "error: rm binary location is wrong"

        # Remove email folder from hdd.
        try:
            output = subprocess.run(
                    ["/usr/bin/doas", "-u", "vmail", rm, "-rf", email_path],
                    check=True
                    )
            if output.returncode != 0:
                current_app.logger.error("returncode of cmd rm is non zero")
                return "error: returncode of cmd rm is non zero"
        except subprocess.CalledProcessError:
            current_app.logger.error("returncode of cmd rm is non zero")
            return "error: returncode of cmd rm is non zero"

        current_app.logger.info("done")
        return "done"
