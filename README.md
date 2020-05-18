# RabbitMQ Python Wrapper

RabbitMQ Python Wrapper is a library whose aim is to reduce the complexity of working with Advanced Message Queueing Protocol (AMQP) and allow common users to build applications that use this protocol as main channel for communication.

The core of this library is [RabbitMQ](https://www.rabbitmq.com/) - one of the most commonly used AMQP brokers. Client libraries to interface with the broker are available for all major programming languages. For the Python programming language, there are two main client libraries: [pika](https://pika.readthedocs.io/en/stable/) and [rabbitpy](https://rabbitpy.readthedocs.io/en/latest/). These two libraries, expose an API of classes and methods that can be used to interact with the broker and create communication between clients.

 The configuration required to establish a communication between clients using either of those libraries can be difficult to set and adds overhead to any project no matter how simple or difficult it is. Users can however use the "RabbitMQ Python Wrapper" to overcome this problem, having to chose between 4 main entities provided by the library depending on their needs.

 We'll talk more about this wrapper, but first I want to introduce you a few key concepts about the RabbitMQ broker.

 ## RabbitMQ Working Principle

 The RabbitMQ defines two main entities that communicate with the use of a broker, both being seen as clients. The first entity is called "Publisher" because it mainly sends messages to other clients if any. The second entity is the "Consumer" and as the name suggests, it "ingests" messages coming from one or multiple publishers.

 You may be wondering by now, how the heck do these clients actually communicate with each other... Well, this is where RabbitMQ comes into play.

 The broker running on a server, is a mediator that routes the messages between clients based on a set of rules. These messages travel through a TCP channel from a publisher to the server where they arrive in an exchange. There, based on the exchange's definition, the messages can be sent to exactly one consumer, many consumers or all consumers that are bound to that exchange. Furthermore, consumers are able to retrieve messages from the exchange through a queue. This ensures that messages are not lost if the consumer's busy and that they are treated sequentially.

 A graphic illustration of the working principle explained earlier can be seen in the image below.

 ![alt text](https://www.rabbitmq.com/img/tutorials/intro/hello-world-example-routing.png)

 Exchanges can be of many types allowing for different configurations. Also, the queues can have a considerable set of parameters to configure and nonetheless, the messages themselves allow for complex configs like time-to-live (TTL) and message headers, replyTo, etc.

 As you can easily notice, things can get pretty messy and for someone who has never used AMQP and RabbitMQ specifically in the past, the learning curve can be pretty steep with lots of information to ingest and many things to consider when trying to integrate this as a mean of communication for their app. This is why RabbitMQ Python wrapper was created, its main purpose being to reduce the complexity of working with RabbitMQ and allowing developers to integrate it in their apps without having little to no knowledge of AMQP.

 ## What is the RabbitMQ Python Wrapper?
 
 Name explanation:

 **RabbitMQ** - because it is built for the RabbitMQ broker
 
 **Python** - because it is written in python
 
 **Wrapper** - because it is not actually a conventional library, but more of an abstraction layer. The core library that was used is rabbitpy, winner over the pika library thanks to the thread safe features.

 RabbitMQ Python Wrapper provides the user with 4 main entities, that can be used depending on the use-case. These entities are:
 - Event Publisher
 - Event Subscriber
 - Client
 - Server

 The first two are used for sending and receiving asynchronous event messages between clients. The message routing is topic based, meaning that a messages sent with a routing key will be received by all the clients that are subscribed to that topic.

 The last two are used for communication between only two clients, where one of them is a client (the one who request a task) and the other is the server (the one who executes that task and usually return a response). This methodology is similar to REST calls, but in fact it is actually RPC (Remote Procedure Call).

 In the following paragraphs, the Wrapper's components are explained in more detail in order to actually understand what's happening under the hood.

 ## Rabbit Connection

 This class must be instantiated before everything else. It creates a new AMQP connection to the RabbitMQ broker on the specified host and port. That connection is held as a private attribute and can be retrieved whenever a new opperation is necessary with the _connection()_ getter.

 ## Events

 The events are a way of sending messages between clients and subscribers that don't need a response back. This mechanism can be useful for synchronizing different parts of the application, or spreading a message to multiple consumers at once.

 ### **Event Publisher**

 The _EventPublisher_ class allows the user to create a new publisher instance by only providing the previously instantiated connection and an exchange name (usually the publisher's name, or the publisher's functionality), to the constructor. This class then exposes a _publish()_ method that receives 2 parameters. The first one is the actual message body that will be received by the consumer and the second one is the topic, which is the key to by which the message will be routed to the subscribers.

 ### **Event Subscriber**

 Messages sent by event publishers will eventually be discarded if no consumer has received them. This is why, one must also create at least one subscriber that will consume messages from one or multiple publishers. Creating a new event subscriber is a little more complicated but fear not because I've got you covered.

 When creating a new instance of the _EventSubscriber_ class, the user must provide a the previously instantiated connection, a standard name for the subscriber, an exchange name, the routing key (topic) that must match the one to where the publisher sends the message and last but not least, a callback method that can be dispatch to handle the data on each received message. It is recommended to use the _subscribe()_ method in a separate thread in order not to block the main thread waiting for incoming messages:

 ```python
threading.Thread(target=sub.subscribe).start()
 ```

## Remote Procedure Call (RPC)

This is the second group of entities that the wrapper provides and the focus here is full duplex communication between two clients. The way it is supposed to work is: a client playing a server role waits for tasks from other clients. When a new job is requested, the server will handle it and after the work's done, it will return a response (usually with the result of the task) to the client that requested the job. Afterwards, the client can handle the response that was received from the server.

### **Server**

The _Server_ class instance can be created by providing the previously instantiated connection, a generic name for the server, a routing key (topic) on which the server will listen for jobs (can be seen as a REST API endpoint) and a callback method that is supposed to do all the work.

If ran from the main thread, the _wait_for_job()_ method should also be dispatched in a new thread to prevent hanging, waiting for incoming jobs:

```python
my_worker = threading.Thread(target=server.wait_for_job)
my_worker.start()
my_worker.join()
```

### **Client**

The _Client_ class can be easily instantiated by providing the exact same parameters as for the _Server_ class, with the only mention being that the callback method should be defined to handle the response received from the server, after finishing the execution of the requested job. 

For this class, the user must decide if they want to run the _request_job()_ method in a separate thread (should be chosen if the server has long processing time or undefined) or call the method directly and hang the current thread's execution until a response is received from the server. 


# Conclusions

The RabbitMQ Python Wrapper, as the name suggests, is just a wrapper over the rabbitpy Python library with the only intention being to simplify the work of a developer and reduce considerably the time and effort required to work with AMQP. Keep in mind that by no means it was designed to replace a standard library even more it uses one as a backbone.

May you find yourself in need of a more advanced configuration or you just want to have more freedom in tweaking with the RabbitMQ features like TTL, exchange and queues types, parameters and more, feel free to use one of the existing libraries like pika or rabbitpy and extend the wrapper's functionality to best fit your needs, as it is an open source project and has the capability to receive extensions.

Before you dive into your work, please spare some time to look over the examples for each entity presented above, in the _testing_ package. There you will find some basic usage for the wrapper's classes presented above.