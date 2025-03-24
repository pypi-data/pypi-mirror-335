import datetime
import typing
from unittest.mock import MagicMock

import aiogram
import aiogram.utils.formatting as fmt
import loguru
import pytest
from freezegun import freeze_time
from loguru import logger

from aiogram_loguru.aiogramsink import AiogramSink

TEST_CHAT_ID = 1
TEST_DATETIME = datetime.datetime.now()


@pytest.fixture(autouse=True)
def setup_loguru(sink: AiogramSink) -> None:
    logger.remove()


@pytest.fixture()
def bot_mock() -> MagicMock:
    return MagicMock(spec=aiogram.Bot)


@pytest.fixture()
def sink(bot_mock: MagicMock) -> AiogramSink:
    return AiogramSink(bot=bot_mock, chat_id=TEST_CHAT_ID)


@pytest.fixture()
def applied_sink(sink: AiogramSink) -> typing.Generator[AiogramSink, None, None]:
    handler_id = logger.add(sink)
    try:
        yield sink
    finally:
        logger.remove(handler_id)


def get_logged_message(*args, **kwargs) -> "loguru.Message":  # type: ignore #
    captured_message = None

    def capture_message(message: "loguru.Message") -> None:
        nonlocal captured_message
        captured_message = message

    handler_id = logger.add(capture_message, level="ERROR", colorize=False)
    try:
        logger.opt(depth=1).error(*args, **kwargs)
    finally:
        logger.remove(handler_id)

    return typing.cast("loguru.Message", captured_message)


@freeze_time(TEST_DATETIME)
async def test_simple_error_message(sink: AiogramSink) -> None:
    message = get_logged_message("test")

    actual_text = sink.create_tg_message(message)
    expected_text = fmt.as_list(
        fmt.as_key_value(
            "At", fmt.Code(TEST_DATETIME.isoformat(timespec="milliseconds"))
        ),
        fmt.as_key_value("Level", fmt.Code("ERROR")),
        fmt.as_key_value(
            "Location", fmt.Code(__name__, ":", test_simple_error_message.__name__)
        ),
        fmt.as_key_value("Message", fmt.Code("test")),
    )
    assert actual_text.as_kwargs() == expected_text.as_kwargs()


@freeze_time(TEST_DATETIME)
async def test_long_error_message(sink: AiogramSink) -> None:
    message = get_logged_message("a" * 1000)

    actual_text = sink.create_tg_message(message)
    expected_text = fmt.as_list(
        fmt.as_key_value(
            "At", fmt.Code(TEST_DATETIME.isoformat(timespec="milliseconds"))
        ),
        fmt.as_key_value("Level", fmt.Code("ERROR")),
        fmt.as_key_value(
            "Location", fmt.Code(__name__, ":", test_long_error_message.__name__)
        ),
        fmt.as_key_value(
            "Message",
            fmt.Code("a" * (AiogramSink.MAX_MESSAGE_ATTRIBUTE_LENGTH - 3) + "..."),
        ),
    )
    assert actual_text.as_kwargs() == expected_text.as_kwargs()


@freeze_time(TEST_DATETIME)
async def test_error_message_with_templates(sink: AiogramSink) -> None:
    message = get_logged_message("{}", "substituted")

    actual_text = sink.create_tg_message(message)
    expected_text = fmt.as_list(
        fmt.as_key_value(
            "At", fmt.Code(TEST_DATETIME.isoformat(timespec="milliseconds"))
        ),
        fmt.as_key_value("Level", fmt.Code("ERROR")),
        fmt.as_key_value(
            "Location",
            fmt.Code(__name__, ":", test_error_message_with_templates.__name__),
        ),
        fmt.as_key_value(
            "Message",
            fmt.Code("substituted"),
        ),
    )
    assert actual_text.as_kwargs() == expected_text.as_kwargs()


def test_full_log_file_being_created(sink: AiogramSink) -> None:
    message = get_logged_message("test")

    file = typing.cast(
        aiogram.types.BufferedInputFile, sink.create_tg_document(message)
    )
    assert file.data == message.encode("utf-8")


async def test_tg_message_being_send(
    bot_mock: MagicMock, applied_sink: AiogramSink
) -> None:
    expected_text = fmt.Text("test")
    expected_file = aiogram.types.BufferedInputFile(file=b"test", filename="log.txt")

    def patched_create_tg_message(message: "loguru.Message") -> fmt.Text:
        return expected_text

    def patched_create_tg_document(
        message: "loguru.Message",
    ) -> aiogram.types.InputFile:
        return expected_file

    applied_sink.create_tg_message = patched_create_tg_message  # type: ignore
    applied_sink.create_tg_document = patched_create_tg_document  # type: ignore

    logger.error("test")
    await logger.complete()  # to await the sink call

    bot_mock.send_document.assert_awaited_once_with(
        chat_id=TEST_CHAT_ID,
        document=expected_file,
        **expected_text.as_kwargs(text_key="caption", entities_key="caption_entities"),
    )
