"""
IA Parc Inference service
Support for inference of IA Parc models
"""
import os
import time
import asyncio
import uuid
from inspect import signature
import logging
import logging.config
import nats
import nats.errors as nats_errors
import json
from iap_messenger.config import Config, PipeInputOutput
from iap_messenger.data_decoder import decode
from iap_messenger.data_encoder import DataEncoder
from iap_messenger.subscription import BatchSubscription
from iap_messenger.message import Message
from iap_messenger.readme_handler import wait_readme

Error = ValueError | None

LEVEL = os.environ.get('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(
    level=LEVEL,
    force=True,
    format="%(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
LOGGER = logging.getLogger("iap-messenger")
LOGGER.propagate = True


class MsgListener():
    """
    Inference Listener class
    """

    def __init__(self,
                 callback,
                 decode=False,
                 batch:int=-1,
                 inputs:str = "",
                 outputs:str = "",
                 config_path:str= "/opt/pipeline/pipeline.json",
                 url:str="",
                 queue:str=""
                 ):
        """
        Constructor
        Arguments:
        - callback:     Callback function to proccess data
                        callback(data: Any | list[Any], parameters: Optional[dict])
        Optional arguments:
        - inputs:       Input queue name
        - outputs:      Output queue name
        - decode:       Set wether data should be decoded before calling the callback function (default: True)
        - batch:        Batch size for inference (default: -1)
                        If your model do not support batched input, set batch to 1
                        If set to -1, batch size will be determined by the IAP_BATCH_SIZE
                        environment variable
        - config_path:  Path to config file (default: /opt/pipeline/pipeline.json)
        - url:          Url of inference server (default: None)
                        By default determined by the NATS_URL environment variable,
                        however you can orverride it here
        - queue:        Name of queue (default: None)
                        By default determined by the NATS_QUEUE environment variable,
                        however you can orverride it here
        """
        # Init internal variables
        self.decode = decode
        self.timeout = 0.002
        self.exec_time = 0
        self._subs_in = []
        self._subs_out = []
        self.config = Config(config_path)
        if inputs:
            self.config.input_list = inputs.split(",")
        self.lock = asyncio.Lock()
        self.callback = callback
        sig = signature(callback)
        self.callback_args = sig.parameters
        nb_params = len(self.callback_args)
        if nb_params == 1:
            self.callback_has_parameters = False
        else:
            self.callback_has_parameters = True

        if url:
            self.url = url
        else:
            self.url = os.environ.get("NATS_URL", "nats://nats:4222")
        if queue:
            self.queue = queue.replace("/", "-")
        else:
            self.queue = os.environ.get("NATS_QUEUE", "").replace("/", "-")
            if self.queue == "":
                self.queue = os.environ.get("QUEUE", "iap-messenger").replace("/", "-")
        if batch > 0:
            self.batch = batch
        else:
            self.batch = int(os.environ.get("IAP_BATCH_SIZE", -1))
            if self.batch == -1:
                self.batch = int(os.environ.get("BATCH_SIZE", 1))
        if self.batch > 1:
            self.is_batch = True
        else:
            self.is_batch = False

        self.error_queue = self.queue + ".ERROR"
        self.parameters = {}
        self.inputs: dict[str, PipeInputOutput] =  self.config.Inputs
        self.outputs: dict[str, PipeInputOutput] = self.config.Outputs
        self.encoders: dict[str, DataEncoder] = self.config.encoders
        if len(self.config.input_list) == 0:
            print("No inputs defined")
            quit(1)
        for link in self.config.input_list:
            self.parameters[link] = self.inputs[link].parameters
            
    @property
    def inputs_name(self) -> list:
        """ Input property """
        return self.config.input_list

    def run(self):
        """
        Run inference service
        """
        asyncio.run(self.run_async())

    async def run_async(self):
        """ Start listening to NATS messages
        url: NATS server url
        batch_size: batch size
        """
        self.nc = await nats.connect(self.url)
        self.js = self.nc.jetstream()

        for q_name in self.inputs_name:
            #item = self.inputs[q_name]
            queue_in = self.queue + "." + q_name
            print("Listening on queue:", queue_in)
            js_in = await self.js.subscribe(queue_in+".>",
                                            queue=self.queue+"-"+q_name,
                                            stream=self.queue)
                
            self._subs_in.append((q_name, js_in))
            nc_in = await self.nc.subscribe("nc."+queue_in+".*.*", queue=self.queue+"-"+q_name)
            self._subs_in.append((q_name, nc_in))

        pos = os.environ.get('POSITION', '0')
        readme_nc = await self.nc.subscribe(f"nc.{self.queue}.readme-{pos}.*.*", queue=self.queue+"-readme")
        self._subs_in.append(("readme", readme_nc))

        print("Default queue out:", self.config.default_output)
        self.data_store = await self.js.object_store(bucket=self.queue+"-data")

        os.system("touch /tmp/running")
        tasks = []
        for link, sub_in in self._subs_in:
            if link == "readme":
                tasks.append(wait_readme(sub_in, self.send_msg))
            else:
                tasks.append(self.wait_msg(link, sub_in))
        await asyncio.gather(*tasks)
        await self.nc.close()

    async def wait_msg(self, link, sub_in):
        # Fetch and ack messagess from consumer.
        if sub_in.subject[:7] == "_INBOX.":
            subject = sub_in.subject[7:]
            is_js = True
        else:
            subject = sub_in.subject.replace(".*.*", "")
            is_js = False
        if self.is_batch:
            batch_sub = BatchSubscription(sub_in, self.batch)
        while True:
            if not self.is_batch:
                try:
                    msg = await sub_in.next_msg(timeout=600)
                except nats_errors.TimeoutError:
                    continue
                except TimeoutError:
                    continue
                except nats_errors.ConnectionClosedError:
                    LOGGER.error(
                        "Fatal error message handler: ConnectionClosedError")
                    break
                except asyncio.CancelledError:
                    LOGGER.error(
                        "Fatal error message handler: CancelledError")
                    break
                except Exception as e: # pylint: disable=W0703
                    LOGGER.error("Unknown error:", exc_info=True)
                    LOGGER.debug(e)
                    continue
                
                # Message received
                await asyncio.gather(
                    self.term_msg([msg], is_js),
                    self.handle_msg(subject, link, [msg])
                )
            else:
                msgs = []
                try:
                    msgs = await batch_sub.get_batch(self.timeout)
                except nats_errors.TimeoutError:
                    continue
                except TimeoutError:
                    continue
                except nats_errors.ConnectionClosedError:
                    LOGGER.error(
                        "Fatal error message handler: ConnectionClosedError")
                    break
                except asyncio.CancelledError:
                    LOGGER.error(
                        "Fatal error message handler: CancelledError")
                    break
                
                # Messages received
                t0 = time.time()
                await asyncio.gather(
                    self.term_msg(msgs, is_js),
                    self.handle_msg(subject, link, msgs)
                )
                t1 = time.time()
                if self.exec_time == 0:
                    self.exec_time = t1 - t0
                self.exec_time = (self.exec_time + t1 - t0) / 2
                if self.exec_time < 0.02:
                    self.timeout = 0.002
                elif self.exec_time > 0.35:
                    self.timeout = 0.05
                else:
                    self.timeout = self.exec_time * 0.15

    async def handle_msg(self, subject, link, msgs):
        async with self.lock:
            if self.is_batch:
                iap_msgs = [await self.get_data(subject, msg, link) for msg in msgs]
                await self._process_data(iap_msgs)
            else:
                for msg in msgs:
                    iap_msg = await self.get_data(subject, msg, link)
                    await self._process_data([iap_msg])
        return

    async def term_msg(self, msgs, is_js=False):
        if is_js:
            for msg in msgs:
                await msg.ack()
        else:
            ack = "".encode("utf8")
            for msg in msgs:
                await msg.respond(ack)

    async def get_data(self, subject, msg, link) -> Message:
        l_sub = len(subject) + 1
        uid = msg.subject[(l_sub):]
        source = msg.headers.get("DataSource", "")
        params_lst = msg.headers.get("Parameters", "")
        params = {}
        reply_to = self.outputs[self.config.default_output].name
        if self.inputs[link].output is not None:
            reply_to = self.inputs[link].output
            
        iap_msg = Message(
            Raw=msg.data,
            From=self.inputs[link].name,
            To=reply_to or "",
            Parameters=params,
            Reply=None,
            is_decoded=False,
            uid=uid,
            _link=link,
            _source=source,
            _inputs=self.inputs[link].data,
            _nc=self.nc,
            _js=self.js,
            _error_queue=self.error_queue,
            _outputs=self.outputs,
            _encoders=self.encoders,
            _queue=self.queue,
            _data_store=self.data_store
        )
        if params_lst:
            for p in params_lst.split(","):
                args = p.split("=")
                if len(args) == 2:
                    k, v = args
                    if v == "None":
                        params[k] = None
                    elif k in self.parameters[link]:
                        if v:
                            if self.parameters[link][k] == "float":
                                params[k] = float(v)
                            elif self.parameters[link][k] == "integer":
                                params[k] = int(v)
                            elif self.parameters[link][k] == "boolean":
                                params[k] = v.lower() in ("yes", "true", "True", "1")
                            elif self.parameters[link][k] == "json":
                                params[k] = json.loads(v)
                            else:
                                params[k] = v
                        else:
                            if self.parameters[link][k] != "string":
                                params[k] = None
                            else:
                                params[k] = ""
                    else:
                        # Unknown parameter
                        params[k] = v
            iap_msg.Parameters = params
        iap_msg._content_type = msg.headers.get("ContentType", "")
        data = ''.encode()
        if source == "object_store":
            obj_res = await self.data_store.get(msg.data.decode())
            if obj_res.data:
                data = obj_res.data
            else:
                data = ''.encode()
            asyncio.create_task(self.data_store.delete(msg.data.decode()))
        else:
            if isinstance(msg.data, bytes):
                data = msg.data
            else:
                data = str(msg.data).encode()
        iap_msg.Raw = data

        return iap_msg

    async def send_msg(self, out, uid, source, data, parameters={}, error=""):
        if error is None:
            error = ""
        _params = ""
        if parameters:
            for k,v in parameters.items():
                if len(_params) > 0:
                    _params += f",{k}={v}"
                else:
                    _params = f"{k}={v}"
        breply = "".encode()
        contentType = ""
        if out != self.error_queue:
            link_out = out
            for k, v in self.outputs.items():
                if v.name == out:
                    link_out = k
                    break
            _out = self.queue + "." + link_out + "." + uid
            #print("Sending reply to:", _out)
            if data is not None:
                if isinstance(data, (bytes, bytearray)):
                    breply = data
                else:
                    breply, contentType, err = self.encoders[link_out].encode(data)
                    if err:
                        _out = self.error_queue + "." + uid
                        breply = str(err).encode()
                        error = "Error encoding data"
                if len(breply) > 8388608: # 8MB
                    store_uid = str(uuid.uuid4())
                    source = "object_store"
                    bdata = breply
                    breply = store_uid.encode()
                    await self.data_store.put(store_uid, bdata)
        else:
            _out = self.error_queue + "." + uid
            breply = data.encode()
        
        headers = {"ProcessError": error,
                   "ContentType": contentType,
                   "DataSource": source,
                   "Parameters": _params}
        
        if out != self.error_queue:
            try:
                nc_out = "nc." + _out
                await self.nc.request(nc_out, breply, timeout=60, headers=headers)
                _sent = True
            except nats_errors.NoRespondersError:
                await self.js.publish(_out, breply, headers=headers)
            except Exception as e: # pylint: disable=W0703
                LOGGER.error("Error sending message on core NATS:", exc_info=True)
                LOGGER.debug(e)
        else:
            await self.js.publish(_out, breply, headers=headers)

    async def _process_data(self, msgs: list[Message]):
        """
        Process data
        Arguments:
        - requests:   list of data to process
        - is_batch:   is batched data
        """
        LOGGER.debug("handle request")
        has_data = False
        _uids = []
        if len(msgs) == 0:
            return
        for msg in msgs:
            _uids.append(msg.uid)
            if self.decode:
                data, error = decode(msg.Raw, msg._content_type, self.inputs[msg.From].data)
                if error:
                    msg.error = str(error)
                    asyncio.create_task(msg.send())
                    continue
                else:
                    msg.is_decoded = True
                    msg.decoded = data
                    has_data = True
            elif len(msg.Raw) > 0:
                has_data = True
        
        try_error = ""
        if has_data:
            try:
                error = ""
                if self.is_batch:
                    result = self.callback(msgs)
                    if result is None:
                        return
                    if not isinstance(result, list):
                        error = "batch reply is not a list"
                    if len(msgs) != len(result):
                        error = "batch reply has wrong size"
                    if error:
                        for msg in msgs:
                            msg.error = error
                            #asyncio.create_task(self.send_msg(self.error_queue, msg.uid, msg._source, error, msg.Parameters, error))
                            asyncio.create_task(msg.send())
                        return
                    
                    for i, reply in enumerate(result):
                        uid = self.return_reply(msgs[i], reply)
                        _uids.remove(uid)
                    # Handle remaining messages
                    for uid in _uids:
                        for msg in msgs:
                            if msg.uid == uid:
                                msg.error = "failed to process data"
                                asyncio.create_task(msg.send())
                                #asyncio.create_task(self.send_msg(self.error_queue, uid, msg._source, "failed to process data", msg.Parameters, "failed to process data"))
                else:
                    result = self.callback(msgs[0])
                    if result is None:
                        return
                    self.return_reply(msgs[0], result)
                
            except ValueError:
                LOGGER.error("Fatal error message handler", exc_info=True)
                try_error  = "Wrong input"
            except Exception as e: # pylint: disable=W0703
                LOGGER.error("Fatal error message handler", exc_info=True)
                try_error = f'Fatal error: {str(e)}'
            if try_error:
                for msg in msgs:
                    asyncio.create_task(self.send_msg(
                        self.error_queue, msg.uid, msg._source, try_error, "Wrong input"))

    def return_reply(self, request: Message, reply) -> str:
        """
        Return message
        Arguments:
        - msg:   Message to return
        """
        uid = ""
        if isinstance(reply, Message):
            if reply.To is None:
                return request.uid
            if not uid:
                uid = reply.uid
            if reply.error:
                #send_args = [self.error_queue, reply.uid, reply._source, reply.error, reply.Parameters, reply.error]
                asyncio.create_task(reply.send())
                return uid
            else:
                #send_args = [reply.To, reply.uid, reply._source, reply.Reply, reply.Parameters, ""]
                asyncio.create_task(reply.send())
                return uid

        elif isinstance(reply, list):
            for _msg in reply:
                if isinstance(_msg, Message):
                    if _msg.To is None:
                        continue
                    if not uid:
                        uid = _msg.uid
                    if _msg.error:
                        #send_args = [self.error_queue, _msg.uid, _msg._source, _msg.error, _msg.Parameters, _msg.error]
                        asyncio.create_task(_msg.send())
                        break
                    else:
                        #send_args = [_msg.To, _msg.uid, _msg._source, _msg.Reply, _msg.Parameters, ""]
                        asyncio.create_task(_msg.send())

                else:
                    #send_args = [request.To, request.uid, request._source, request.Reply, request.Parameters, "reply is not a Message"]
                    request.error = "reply is not a Message"
                    asyncio.create_task(request.send())
                    return uid
        else:
            #send_args = [request.To, request.uid, request._source, request.Reply, request.Parameters, "reply is not a Message"]
            request.error = "reply is not a Message"
            asyncio.create_task(request.send())
        return uid