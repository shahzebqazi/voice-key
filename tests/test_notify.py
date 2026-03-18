from unittest.mock import MagicMock, patch

from app.notify import FREEDESKTOP_MESSAGE_SOUND, NotificationSound, send_desktop_notification


def test_prefers_canberra_when_available():
    sound = NotificationSound(
        which=lambda name: "/usr/bin/canberra-gtk-play" if name == "canberra-gtk-play" else None
    )

    assert sound.backend == "canberra"
    assert sound.command == ["canberra-gtk-play", "-i", "message"]


def test_uses_paplay_when_system_sound_exists():
    sound = NotificationSound(
        which=lambda name: "/usr/bin/paplay" if name == "paplay" else None,
        sound_exists=lambda: True,
    )

    assert sound.backend == "paplay"
    assert sound.command == ["paplay", str(FREEDESKTOP_MESSAGE_SOUND)]


def test_falls_back_to_generated_chime_without_system_backend():
    sound = NotificationSound(which=lambda name: None)

    assert sound.backend == "generated"
    assert sound.command is None


def test_play_async_dispatches_background_thread():
    sound = NotificationSound(which=lambda name: None)
    thread = MagicMock()

    with patch("app.notify.threading.Thread", return_value=thread) as thread_cls:
        sound.play_async()

    thread_cls.assert_called_once()
    thread.start.assert_called_once()


def test_send_desktop_notification_uses_notify_send():
    run = MagicMock()

    sent = send_desktop_notification(
        "Voice Key",
        "Copied to clipboard.",
        which=lambda name: "/usr/bin/notify-send" if name == "notify-send" else None,
        run=run,
    )

    assert sent is True
    run.assert_called_once()
