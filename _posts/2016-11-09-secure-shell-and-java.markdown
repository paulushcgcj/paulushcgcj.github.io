---
title:  "Secure Shell (SSH) and Java"
date:   2016-11-09 15:00:00 -0300
categories: [article, tech, java, ssh]
author: paulushc
permalink: /articles/secure-shell-and-java
header:
    teaser: /assets/2016-11-09-secure-shell-and-java-cover.jpeg
    overlay_image: /assets/2016-11-09-secure-shell-and-java-cover.jpeg
    overlay_filter: 0.5
    show_overlay_excerpt: false
---
Some time ago, I was debating with some friends about writing an article for the comunity,but I never thought on what is be interesting, so I decided to write about a subject that we use a lot at my company, but using Java code, Secure Shell, or SSH.

<!--more-->

Secure Shell (SSH) is a criptografic network protocol, used in network service operations on a secure way over an unsecure network. It’s kind of a tunnel that you and the remote server (don’t need to be a remote machine, can be your local machine), but with a security guard at the front that don’t let anyone pass. So you ask me, “but Paulo, what’s the real utility of this on my app?”, so let’s get started.



## The Problem

In some point of our application lifecycle, we noticed that we had a need for uploading files to the server, a common thing in a lot of applications, but our problem is that we have a distributed server structure, so, an uploaded file could end on a different server than our client could be at that time, so we got a big problem at our hands. Out client can click on a link, calling an URL that don’t exist on that server, so we used a centralized static server structure. So far, so good, but, how can we send the file from server A (app server) to server B (static content server)?

At principle, we used some TCP socket transfer solution, to send content from server A to B, but we created a huge unnecessari dependency, where we need a client at the other side, on server B, listening all the time, ready to receive a package to be saved on the content server machine. Every developer knows that a dependency could end as a huge headache, and another layer of complexity for our application. How to solve it? We exchange a big dependency for a small one.

How come? Hold your horses buddy, better a small and more avaliable dependency than something big. That’s when SSH comes into play, because we already used a *nix Structure, and SSH was something that we already used at daily basis to manage our servers anyway, it became logical to manage this situation using SSH connections.

## JCraft jsch

At my research for a SSH solution, I’ve found some implementations, but one in special that got my attention was jsch from [Jcraft](http://www.jcraft.com/jsch/), a library that was really very good and could make everything that i needed, but at the time, I don’t seem to understand very well how to use it, all the examples was not that self explanatory or direct as I would like it to be, so my test round has begin.

Basicly, with jsch, you use a communication channel, to execute commands and make some data transfer using SCP/SFTP between servers, and this had managed to eliminate a client application dependency, saving us from an important limitation. But enough of this cheap chat, let’s get our hands dirty.

## Recipe for Success

We implemented a group of classes that we used to help on the library use, in a much simple and pratical way, with some methods and simple behaviours that we can consume, so let’s build it a connection class (ShellConnectionStream) and a static calling class (SSHUtils) so we can consume on a more direct and simple way.

### ShellConnectionStream

This class is responsible for organizing all the jsch code in a single place, on a simple way and making it easy to maintain, so during our construction, we will learn a lot about the library. The first step, is making a constructor, so we can pass our connection data, like user name, password, host and port. This way, we already have all the data needed during all the process, and we aliminate all the need of being asking all the time the connection data.

{% gist feec315ce5c0c8bf2f1d1f8514dbf06e %}

On the next step, we create a way to start and end a connection with the server, because, we want a flexibility level, so we can open a connection, execute a lot of stuff and close only at the very end, so we can save some of the handshake time.

{% gist ae3cd558f0ac381b10b12f41b761d8a3 %}

Now it’s the show time. Basicly, we want to build a lib that we can achieve 2 things at principle, upload/download and command execution. But why “only” these 2 functionalities? Because they are the very base of almost anything and they are enough for what we wanna do.

{% gist 73bf109c21db0a9c6e014e5e7b0a6ede %}

The way we implemented, the command is executed, and return something that we forward to the user (as you can see, it’s just a string that is returned at the end of the execution). This way, the user can execute a listing command like ‘ls’ and process the return of this command, or execute a command to move a file, that will not return anything, but he didn’t expect anything at all, so no problem.

Next, we will download and upload files, because this is one of the main factors to use this library anyway, as you can see at the begining, our main motivation was to exchange files with our server, so let’s get it on.

{% gist c1c223cc19f0b4da612d8775c826f91b %}

As you can see, it’s not hard, it’s just a put call to sftp, which have a lot of overloads, but we prefer to use an exemple where we first change to the directory and then we send the file, using it’s full path just to be sure that we will save the file at the correct place. At the same time, we replace all the whithespaces with other valid character, because it can be a problem if we have a whitespace at our path. You can use this time to replace other special characters as well. Another point that need some atention, is that we used a string with the file path, but we can use an inputstream or a file, but we stick with the string path, because this way,we don’t neet to read the file before the library, if the library itself could do it for you before sending. The user feedback is given as a boolean value, so he can check if it was a success.

{% gist f4e16d906517bbc97dd2eb264da12c92 %}

Same logic is used to download a file, it’s like a reverse upload, changing only the put method with get, the library will save the remote file on the given path, and we return a boolean to the user on the same fashion.

Simple, isn’t if? But belive me, this library could save us a lot of time and give us a lot of flexibility on executing tasks, like checking if a remote file exist, exchange files between servers, start and stop and application or a service, check disk usage on a raw way, execute system updates and so on. Can you measure the flexibility that we gain with this simple lib?

## Building an usable lib

Now, on the next step, we will create a simple way of consuming this class, unifying some repeated code on a single place, creating key functionalities to our dayli use. Let’s start with something simple, like creating a directory.

{% gist dd291dd07e5b10b90fa4028c993e6739 %}

Simple right? And how we sill consume it?

{% gist c3ebb8e41567001da001d70672179c0d %}

Wow, now that’s something. Now we can create some remote directories right? What more can we do? How about, check if a file exist?

{% gist 3be5cd3b2f13f576670ebe8d53375d2e %}

Now we are talking Paulo, now I can see what you are talking about. Now, how about… move files?

{% gist c343771e51f88b7521fc5335f341c605 %}

So… how about upload? And if I want to send more than one file at time?

{% gist 26e000fac86d99a0d54fbf0d977ffc41 %}

The possibilities are endless, this is just the tip of the iceberg.You can make some task execute automatically, using code, like cleaning temporary files, manage servers on a centralized manner, or maybe, like myself, you need a Swiss Army knife, that will save you from trouble and from unecessary dependencies.

Do you liked? This was my first article, and my first on english as well, as you may notice or not, I’m from Brasil and english is “just” my second language, so sorry if i made any mistake writing this article, and I hope this article could be useful for you on creating an autonomous application you your company or at home, share with your friends and your collegues.

You can check all the source code at my [GitHub](https://github.com/paulushcgcj/sshutil) if you prefer.

See you next time.