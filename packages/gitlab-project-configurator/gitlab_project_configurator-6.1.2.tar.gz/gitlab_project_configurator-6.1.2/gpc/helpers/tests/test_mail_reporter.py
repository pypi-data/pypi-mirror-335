# Third Party Libraries
import pytest

# Gitlab-Project-Configurator Modules
from gpc.helpers.mail_reporter import send_email


@pytest.mark.parametrize("to", [["guigui", "gaetan"], "guigui"])
def test_send_email(mocker, to):
    send_mail_mock = mocker.patch("smtplib.SMTP", mocker.MagicMock())

    toutou = to
    if isinstance(to, list):
        to = to.copy()
    else:
        toutou = [toutou]

    send_email(
        sender="fufu",
        to=to,
        subject="remarque",
        body="il faut utester son code !",
        cc=["BigBoss"],
        bcc=["shameOnYou"],
        smtp_server=mocker.Mock(),
        smtp_port=666,
    )

    assert send_mail_mock.called
    # kwargs
    send_message_args = send_mail_mock.mock_calls[2][2]
    assert send_message_args["from_addr"] == "fufu"
    assert send_message_args["to_addrs"] == toutou + ["BigBoss", "shameOnYou"]
    assert "remarque" in str(send_message_args["msg"])
    assert "il faut utester son code !" in str(send_message_args["msg"])
