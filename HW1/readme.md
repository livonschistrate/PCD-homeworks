# PCD - Homework 1

## Syntax

For server:

        server.py --protocol PROTOCOL

The protocol option has two values: 0 for TCP, 1 for UDP

For client:

        client.py --protocol PROTOCOL --size SIZE --saw SAW --filename FILENAME

Like the protocol option, the stop-and-wait procedure (SAW in short) can be enabled/disabled by pressing y or n 

## Stats

I've tested these mechanisms using three files, along with various chunk sizes introduced on the command line on the local machine (and also using the virtual one)
and extracted the results below. We can observe that the UDP server's time transmission is shorter than the TCP one when there are large amounts of content.

![Results of testing three files and using various chunk sizes](https://github.com/livonschistrate/PCD-homeworks/blob/main/HW1/files/stats.png)


## Sources

1. https://www.javatpoint.com/stop-and-wait-protocol
2. https://pythontic.com/modules/socket/send -> for implementing the servers
3. https://www.digitalocean.com/community/tutorials/python-struct-pack-unpack -> for sending bytes properly using multiple variables when sending from client to server
4. https://stackoverflow.com/questions/20063/whats-the-best-way-to-parse-command-line-arguments -> for command line parsing
