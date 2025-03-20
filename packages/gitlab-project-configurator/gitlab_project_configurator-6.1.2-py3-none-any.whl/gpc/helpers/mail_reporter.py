# Third Party Libraries
# Standard Library
import os
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

# Third Party Libraries
from jinja2 import Environment
from jinja2 import PackageLoader
from structlog import get_logger


log = get_logger()

Email = str


def send_email(
    sender: str,
    to: Union[str, List[str]],
    subject: str,
    body: str,
    cc: Optional[List[str]] = None,
    bcc: Optional[List[str]] = None,
    smtp_server=None,
    smtp_port=None,
):
    if isinstance(to, str):
        to_list = [to]  # type: List[str]
    else:
        to_list = to
    if cc:
        to_list += cc
    if bcc:
        to_list += bcc
    to_list = [x for x in to_list if x]

    msg = MIMEMultipart("alternative")
    msg["From"] = sender
    msg["Subject"] = subject
    msg["To"] = ",".join(to_list)
    if cc:
        msg["Cc"] = ",".join(cc)
    if bcc:
        msg["Bcc"] = ",".join(bcc)
    msg.attach(MIMEText(body, "html"))
    log.debug(
        "Sending email",
        smtp_server=smtp_server,
        smtp_port=smtp_port,
        sender=sender,
        to_list=to_list,
        body=body[:15] + "...",
    )
    if not smtp_server or not smtp_port:
        return
    with smtplib.SMTP(smtp_server, port=int(smtp_port)) as server:
        server.send_message(msg=msg, from_addr=sender, to_addrs=to_list)


def send_change_event_email(
    gitlab,
    changes: Dict,
    errors: List[Dict],
    emails_to_notify: List[str],
    email_author: str,
    all_changes=True,
    smtp_server=None,
    smtp_port=None,
):
    env = Environment(
        loader=PackageLoader("gpc.templates", "mail"),
        autoescape=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    rendered_html = env.get_template("change-event-email.html.j2").render(
        gitlab_server_url=gitlab.url,
        event=changes,
        errors=errors,
        title="GPC Notification Email",
        pipeline_url=os.getenv("CI_PIPELINE_URL"),
        all_changes=all_changes,
    )

    # Only for development:
    send_email(
        sender=email_author,
        to=emails_to_notify,
        body=rendered_html,
        subject="A change has been made by gpc from project ...",
        smtp_server=smtp_server,
        smtp_port=smtp_port,
    )
