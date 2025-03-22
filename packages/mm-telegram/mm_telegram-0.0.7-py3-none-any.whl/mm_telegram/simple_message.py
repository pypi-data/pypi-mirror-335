import time

import anyio
import pydash
from mm_std import Err, Ok, Result, ahr, hr


def send_message(bot_token: str, chat_id: int, message: str, long_message_delay: int = 3) -> Result[list[int]]:
    messages = _split_string(message, 4096)
    responses = []
    result = []
    while True:
        text = messages.pop(0)
        params = {"chat_id": chat_id, "text": text}
        res = hr(f"https://api.telegram.org/bot{bot_token}/sendMessage", method="post", params=params)
        responses.append(res.json)
        if res.error is not None:
            return Err(res.error, data={"last_res": res.to_dict(), "responses": responses})

        message_id = pydash.get(res.json, "result.message_id")
        if message_id:
            result.append(message_id)
        else:
            return Err("unknown_response", data={"last_res": res.to_dict(), "responses": responses})

        if len(messages):
            time.sleep(long_message_delay)
        else:
            break
    return Ok(result, data={"responses": responses})


async def async_send_message(bot_token: str, chat_id: int, message: str, long_message_delay: int = 3) -> Result[list[int]]:
    messages = _split_string(message, 4096)
    responses = []
    result = []
    while True:
        text = messages.pop(0)
        params = {"chat_id": chat_id, "text": text}
        res = await ahr(f"https://api.telegram.org/bot{bot_token}/sendMessage", method="post", params=params)
        responses.append(res.json)
        if res.error is not None:
            return Err(res.error, data={"last_res": res.to_dict(), "responses": responses})

        message_id = pydash.get(res.json, "result.message_id")
        if message_id:
            result.append(message_id)
        else:
            return Err("unknown_response", data={"last_res": res.to_dict(), "responses": responses})

        if len(messages):
            await anyio.sleep(long_message_delay)
        else:
            break
    return Ok(result, data={"responses": responses})


def _split_string(text: str, chars_per_string: int) -> list[str]:
    return [text[i : i + chars_per_string] for i in range(0, len(text), chars_per_string)]
