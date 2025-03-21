from dataclasses import dataclass
from copy import deepcopy
import uuid
import logging
from typing import Any
from nats import js
from nats.aio.client import Client
import nats.errors as nats_errors
from iap_messenger.data_decoder import decode

LOGGER = logging.getLogger("iap-messenger")
Error = ValueError | None

@dataclass(kw_only=True)
class Message:
    """Class for keeping track of messages."""
    Raw: bytes
    From: str
    To: str | list[str] | None = None
    Parameters: dict | None = None
    Reply: bytes | Any
    error: str | None = None
    decoded: Any = None
    is_decoded: bool = False
    uid: str
    _link: str = ""
    _source: str = ""
    _content_type: str = "application/json"
    _inputs: dict
    _nc: Client
    _js: js.JetStreamContext
    _error_queue: str = "error"
    _outputs: dict
    _encoders: dict
    _queue: str = "queue"
    _data_store: Any

    def decode(self) -> tuple[Any, Error]:
        """Decode the Raw data."""
        return decode(self.Raw, self._content_type, self._inputs)
    
    def copy(self):
        """Return a copy of the message."""
        return self.__copy__()
    
    def _new_msg(self):
        """Create a new instance of the class."""
        msg = type(self)(
            Raw=b"",
            From=self.From,
            To="",
            Parameters=None if self.Parameters is None else deepcopy(
                self.Parameters),
            Reply=None,
            error=None,
            decoded=None,
            is_decoded=self.is_decoded,
            uid=self.uid,
            _link=self._link,
            _source=self._source,
            _content_type=self._content_type,
            _inputs=self._inputs,
            _nc=self._nc,
            _js=self._js,
            _error_queue=self._error_queue,
            _outputs=self._outputs,
            _encoders=self._encoders,
            _queue=self._queue,
            _data_store=self._data_store
        )
        return msg
    
    def __copy__(self):
        """Return a copy of the message."""
        msg = self._new_msg()
        msg.Raw = self.Raw
        msg.To = self.To
        msg.Reply = None if self.Reply is None else deepcopy(self.Reply)
        msg.error = self.error
        msg.decoded = None if self.decoded is None else deepcopy(self.decoded),
        return msg
    
    def new_msg(self, reply: bytes | Any = None, to: str | list[str] | None = None):
        """Return a new message."""
        msg = self._new_msg()
        msg.Reply = reply
        msg.To = to
        return msg

    async def send(self, timeout: float = 0) -> Error:
        """Send the message.
        Args:
            timeout (float): Timeout in seconds for sending the message.
            If 0, the message will be sent without waiting for a response.
        Returns:
            Error: Error or None if no error.
                   If there is a timeout, the error will be "Timeout".
                   If there are no responders, the error will be "No responders".
                   For all other errors, the error will be "Error sending message".
        """
        if self.To is None:
            return ValueError("No recipient")
        if self.error is not None:
            self.To = self._error_queue
        if isinstance(self.To, list):
            for out in self.To:
                err = await self._send_msg(out, timeout)
                if err:
                    return err
            return None
        else:
            return await self._send_msg(self.To, timeout)

    async def _send_msg(self, out: str, timeout: float) -> Error:
        source = self._source
        if self.error is None:
            error = ""
        else:
            error = self.error
        _params = ""
        if self.Parameters:
            for k, v in self.Parameters.items():
                if len(_params) > 0:
                    _params += f",{k}={v}"
                else:
                    _params = f"{k}={v}"
        breply = "".encode()
        contentType = ""
        if out != self._error_queue:
            link_out = out
            for k, v in self._outputs.items():
                if v.name == out:
                    link_out = k
                    break
            _out = self._queue + "." + link_out + "." + self.uid
            # print("Sending reply to:", _out)
            source = self._outputs[link_out].type
            if self.Reply is not None:
                if isinstance(self.Reply, (bytes, bytearray)):
                    breply = self.Reply
                else:
                    breply, contentType, err = self._encoders[link_out].encode(
                        self.Reply)
                    source = contentType
                    if err:
                        _out = self._error_queue + "." + self.uid
                        breply = str(err).encode()
                        error = "Error encoding data"
                if len(breply) > 8388608:  # 8MB
                    store_uid = str(uuid.uuid4())
                    source = "object_store"
                    bdata = breply
                    breply = store_uid.encode()
                    try:
                        LOGGER.debug(f"Storing data in object store: {store_uid}")
                        await self._data_store.put(store_uid, bdata)
                        LOGGER.debug(f"Data stored in object store: {store_uid}")
                    except Exception as e:  # pylint: disable=W0703
                        LOGGER.error(
                            "Error storing data in object store: %s", str(e), exc_info=True)
                        _out = self._error_queue + "." + self.uid
                        breply = str(e).encode()
                        error = "Error storing data in object store"
        else:
            _out = self._error_queue + "." + self.uid
            breply = self.error.encode() if self.error else "".encode()
            source = "json"

        headers = {"ProcessError": error,
                   "ContentType": contentType,
                   "DataSource": source,
                   "Parameters": _params}

        if out != self._error_queue:
            if timeout > 0:
                try:
                    nc_out = "nc." + _out
                    await self._nc.request(nc_out, breply, timeout=timeout, headers=headers)
                    return None
                except nats_errors.NoRespondersError:
                    return ValueError("No responders")
                except nats_errors.TimeoutError:
                    return ValueError("Timeout")
                except Exception as e:  # pylint: disable=W0703
                    LOGGER.error(
                        "Error sending message on core NATS: %s", str(e), exc_info=True)
                    return ValueError("Error sending message")
            try:
                await self._js.publish(_out, breply, headers=headers)
            except Exception as e:  # pylint: disable=W0703
                LOGGER.error("Error sending message on core NATS: %s", str(e), exc_info=True)
                return ValueError("Error sending message")
        else:
            await self._js.publish(_out, breply, headers=headers)
        LOGGER.debug(f"Message sent to: {_out}")
        return None