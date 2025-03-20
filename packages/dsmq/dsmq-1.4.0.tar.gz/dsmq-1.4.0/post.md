# dsmq

I'd like to introduce [dsmq](https://github.com/brohrer/dsmq),
the Dead Simple Message Queue, to the world.

Part mail room, part bulletin board, dsmq is a central location for sharing messages
between processes, even when they are running on different computers.

Its defining characteristic is bare-bones simplicity.

![
A screenshot of the dsmq GitHub repository:
src/dsmq,
.python-version,
LICENSE,
README.md,
pyproject.toml,
README,
MIT license,
Dead Simple Message Queue
What it does
Part mail room, part bulletin board, dsmq is a central location
for sharing messages between processes, even when they are running
on computers scattered around the world.
Its defining characteristic is bare-bones simplicity.
](https://brandonrohrer.com/images/dsmq/dsmq_00.png)

## What dsmq does

A message queue lets different processes talk to each other, within or across machines.
Message queues are a waystation, a place to publish messages and hold them until
they get picked up by the process that needs them.

In dsmq, a program running the message queue starts up first (the server).
It handles all the
receiving, delivering, sorting, and storing of messages.

Other programs (the clients) connect to the server. They add messages to a queue
or read messages from a queue. Each queue is a separate topic. 

## Why message queues?
Message queues are invaluable for distributed systems of all sorts,
but my favorite application is robotics.
Robots typically have several (or many) processes doing different things at different
speeds. Communication between processes is a fundamental part of any moderately
complex automated system.
When [ROS](https://www.ros.org) (the Robot Operating System) was
released, one of the big gifts it gave to robot builders was a reliable way to
pass messages.

## Why another message queue?

There are lots of [message queues](https://en.wikipedia.org/wiki/Message_queue)
in the world, and some are quite well known--Amazon SQS,
RabbitMQ, Apache Kafka to name a few. It's fair to ask why this one was created.

The official reason for dsmq's existence is that all the other available options
are pretty heavy. Take RabbitMQ for instance, a popular open source message queue.
It has hundreds of associated repositories and it's core
[rabbitmq-server](https://github.com/rabbitmq/rabbitmq-server) repo has many thousands
of lines of code. It's a heavy lift to import this to support a small robotics project,
and code running on small edge devices may struggle to run it at all.

RabbitMQ is also mature and optimized and dockerized and multi-platform
and fully featured and a lot of other things a robot doesn't need. It would
be out of balance to use it for a small project.

![https://brandonrohrer.com/images/dsmq/dsmq_01.png]("""
Screenshot of the RabbitMQ-server GitHub repo showing that it
is many times larger than dsmq""")

dsmq is only about 200 lines of Python, including client and server code. It's *tiny*.
Good for reading and understanding front-to-back when you're integrating it with
your project.

But the real reason is that I wanted to understand how a message queue might work
and the best way I know to learn this is to build one.

## How to use dsmq

### Install it

```
pip install dsmq
```
or
```
uv add dsmq
```

### Spin up a dsmq server

```python
from dsmq import dsmq
dsmq.start_server(host="127.0.0.1", port=12345)
```

### Connect a client to a dsmq server

```python
mq = dsmq.connect_to_server(host="127.0.0.1", port=12345)
```

### Add a message to a topic queue

```python
topic = "greetings"
msg = "hello world!"
mq.put(topic, msg)
```

### Read a message from a topic queue

```python
topic = "greetings"
msg = mq.get(topic)
```

### Run a demo

0. Open 3 separate terminal windows.
1. In the first, run `src/dsmq/dsmq.py`.
2. In the second, run `src/dsmq/example_put_client.py`.
3. In the third, run `src/dsmq/example_get_client.py`.

Alternatively, if you're on Linux just run `src/dsmq/demo_linux.py`.
(Linux has some process forking capabilities that Windows doesn't and
that macOS forbids. It makes for a nice self-contained multiprocess demo.)

## How it works

- Many clients can read messages from the same topic queue. dsmq uses a one-to-many
publication model.

- A client will get the oldest message available on a requested topic.
Queues are first-in-first-out.

- Clients will only be able to get messages that were added to a queue after the
time they connected to the server. Any messages older that that won't be visible.

- dsmq is asyncronous. There are no guarantees about how soon a message will arrive
at its intended client.

- dsmq is backed by an in-memory SQLite database. If your message volumes
get larger than your RAM, you will reach an out-of-memory condition.
```python
sqlite_conn = sqlite3.connect("file:mem1?mode=memory&cache=shared")
```
- `put()` and `get()` operations are fairly quick--less than 100 $`\mu`$s of processing
time plus any network latency--so it can comfortably handle requests at rates of
hundreds of times per second. But if you have several clients reading and writing
at 1 kHz or more, you may overload the queue.

- A client will not be able to read any of the messages that were put into
a queue before it connected.

- Messages older than 600 seconds will be deleted from the queue.
- In case of contention for the lock on the database, failed queries will be
retried several times, with exponential backoff. None of this is visible to
the clients, but it helps keep the internal operations reliable.

```python
for i_retry in range(_n_retries):
    try:
        cursor.execute("""...
```

- To keep things bare bones, the connections are all implemented in the
socket layer, rather than WebSockets or http in the application layer.
```python
self.dsmq_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
self.dsmq_conn.connect((host, port))
```
- ...however, working on this lower level meant dsmq had to reinvent the wheel of
message headers. Each dsmq message is sent with a header that tells it exactly
how many bytes to expect in it. The header format is simplistic--a message
with one million plus the number of byes in the following message. Doing it this
way means that the header is
exactly 23 bytes long every time. (As long as the message is less than nine million
bytes long.)

- Every time a new client connects to the server, a new thread is created.
That thread listens for any `get()` or `put()` requests the client might make
and handles them immediately.
```python
Thread(target=_handle_client_connection, args=(socket_conn,)).start()
```

- dsmq retrieves the oldest eligible message from the queue. If a client wants
to ensure it is getting the most recent message from the queue, it will need
to iteratively get messages until there are no more left to be gotten.
```python
msg_str = "<no response>"
response = None
while response != "":
    msg_str = response
    response = self.mq.get("<topic>")
```

- dsmq messages are text fields, but Python dictionaries are a very convenient and
common format for passing structured messages. Use the `json` library to convert
from dictionaries to strings and back.
```python
topic = "update"
msg_dict = {"timestep": 374, "value": 3.897}
msg_str = json.dumps(msg_dict)
dsmq.put(topic, msg_str)

msg_str = dsmq.get(topic)
msg_dict = json.loads(msg_str)
```

- dsmq is opinionated. Parameters for controlling behavior are set to reasonable
defaults and not exposed to the user. The additional complexity in the API is
not worth the value of making them user-controlled.
However they are also clearly labeled and very easy to find. If anyone cares enough to
play with them, they are strongly encouraged to fork dsmq and make it their own.

```python
_message_length_offset = 1_000_000
_header_length = 23
_n_retries = 5
_first_retry = 0.01  # seconds
_time_to_live = 600.0  # seconds
```

- dsmq is deliberately built to have as few dependencies as it can get away with.
As of this writing, it doesn't depend on any third party packages and just a handful
of core packages: `json`, `socket`, `sqlite3`, `sys`, and `threading`.

# Dead Simple

Dead simple is an aesthetic.
It says that the ideal is achieved not when nothing more can be added,
but when nothing more can be taken away.
It is the aims to follow the apocryphal advice of Albert Einstein, to make
a thing as simple as possible, but no simpler.

Dead simple is like keystroke golfing, but instead of minimizing the number of
characters, it minimizes the number of concepts a developer or a user
has to hold in their head.

I've tried to embody it in dsmq.
dsmq has fewer lines of code than RabbitMQ has *repositories*. And that tickles me. 
