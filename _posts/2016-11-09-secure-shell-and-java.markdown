---
title:  "Secure Shell (SSH) and Java"
date:   2016-11-09 15:00:00 -0300
categories: [article, tech, java, ssh]
author: paulushc
license: CC-BY-4.0
permalink: /articles/secure-shell-and-java
header:
    teaser: /assets/2016/11/articles/secure-shell-and-java-cover.jpeg
    overlay_image: /assets/2016/11/articles/secure-shell-and-java-cover.jpeg
    overlay_filter: 0.5
    show_overlay_excerpt: false
resources:
    - title: "Source Code"
      url: "https://github.com/paulushcgcj/sshutil"
      icon: "code"
---
Some time ago, I was debating with some friends about writing an article for the community, but I never thought about what would be interesting, so I decided to write about a subject that we use a lot at my company, but using Java code, Secure Shell, or SSH.

<!--more-->

Secure Shell (SSH) is a cryptographic network protocol, used in network service operations in a secure way over an unsecure network. It’s kind of a tunnel between you and the remote server (doesn’t need to be a remote machine, can be your local machine), but with a security guard at the front that doesn’t let anyone pass. So you ask me, “but Paulo, what’s the real utility of this on my app?”, so let’s get started.



## The Problem

In some point of our application lifecycle, we noticed that we had a need for uploading files to the server, a common thing in a lot of applications, but our problem is that we have a distributed server structure, so, an uploaded file could end on a different server than our client could be at that time, so we got a big problem at our hands. Our client can click on a link, calling a URL that doesn’t exist on that server, so we used a centralized static server structure. So far, so good, but, how can we send the file from server A (app server) to server B (static content server)?

In principle, we used some TCP socket transfer solution, to send content from server A to B, but we created a huge unnecessary dependency, where we need a client at the other side, on server B, listening all the time, ready to receive a package to be saved on the content server machine. Every developer knows that a dependency could end as a huge headache, and another layer of complexity for our application. How to solve it? We exchange a big dependency for a small one.

How come? Hold your horses buddy, better a small and more available dependency than something big. That’s when SSH comes into play, because we already used a *nix Structure, and SSH was something that we already used on a daily basis to manage our servers anyway, it became logical to manage this situation using SSH connections.

## JCraft jsch

At my research for a SSH solution, I’ve found some implementations, but one in particular that got my attention was jsch from [Jcraft](http://www.jcraft.com/jsch/), a library that was really very good and could make everything that i needed, but at the time, I don’t seem to understand very well how to use it, all the examples were not that self explanatory or direct as I would like it to be, so my test round began.

Basically, with jsch, you use a communication channel, to execute commands and make some data transfer using SCP/SFTP between servers, and this managed to eliminate a client application dependency, saving us from an important limitation. But enough of this cheap chat, let’s get our hands dirty.

## Recipe for Success

We implemented a group of classes that we used to help on the library use, in a much simpler and more practical way, with some methods and simple behaviours that we can consume, so let’s build it a connection class (ShellConnectionStream) and a static calling class (SSHUtils) so we can consume on a more direct and simple way.

### ShellConnectionStream

This class is responsible for organizing all the jsch code in a single place, on a simple way and making it easy to maintain, so during our construction, we will learn a lot about the library. The first step, is making a constructor, so we can pass our connection data, like user name, password, host and port. This way, we already have all the data needed during all the process, and we eliminate all the need of being asking all the time the connection data.

```java
public ShellConnectionStream(String usuario,String senha, String host, int porta) {

		try {
			ssh = new JSch();			
			this.usuario = usuario;
			this.senha = senha;
			this.porta = porta;
			this.host = host;
			
		} catch (Exception e) {
			e.printStackTrace();
		}

}
```

On the next step, we create a way to start and end a connection with the server, because, we want a flexibility level, so we can open a connection, execute a lot of stuff and close only at the very end, so we can save some of the handshake time.

```java
public boolean connect() throws JSchException {

		try {
			
			session = ssh.getSession(this.usuario, this.host, this.porta);			
			session.setPassword(this.senha);
			session.setConfig("StrictHostKeyChecking", "no");
			session.connect(30000);
			setSession(session);
			setReady(true);
			
			return true;
		} catch (Exception e) {
			setReady(false);
		}		
		return false;
	}
  
  public void close() {

		if (channel != null)
			channel.disconnect();

		if (session != null)
			session.disconnect();
		
		setReady(false);
	}
```

Now it’s the show time. Basicly, we want to build a lib that we can achieve 2 things at principle, upload/download and command execution. But why “only” these 2 functionalities? Because they are the very base of almost anything and they are enough for what we wanna do.

```java
public String write(String comando) {

		try {			
			
			channel = session.openChannel("exec");						
			((ChannelExec) channel).setCommand(comando);			
			setCommandOutput(channel.getInputStream());			
			channel.connect(30000);

			StringBuilder sBuilder = new StringBuilder();
			String lido = reader.readLine();
			
			while (lido != null) {				
				sBuilder.append(lido);				
				sBuilder.append("\n");
				lido = reader.readLine();
			}

			return sBuilder.toString();

		} catch (Exception e) {
			e.printStackTrace();
		}
		return null;
	}
```

The way we implemented, the command is executed, and return something that we forward to the user (as you can see, it’s just a string that is returned at the end of the execution). This way, the user can execute a listing command like ‘ls’ and process the return of this command, or execute a command to move a file, that will not return anything, but he didn’t expect anything at all, so no problem.

Next, we will download and upload files, because this is one of the main factors to use this library anyway, as you can see at the beginning, our main motivation was to exchange files with our server, so let’s get it on.

```java
public boolean upload(String origem,String dirDestino) {

		try {
			File origem_ = new File(origem);			
			dirDestino = dirDestino.replace(" ", "_");
			String destino = dirDestino.concat("/").concat(origem_.getName());						
			return upload(origem, destino, dirDestino);			
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}
	
	public boolean upload(String origem,String destino,String dirDestino) {

		try {			
			ChannelSftp sftp = (ChannelSftp) session.openChannel("sftp");			
			sftp.connect();			
			dirDestino = dirDestino.replace(" ", "_");									
			sftp.cd(dirDestino);
			sftp.put(origem, destino);			
			sftp.disconnect();
			return true;
			
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}
```

As you can see, it’s not hard, it’s just a put call to sftp, which have a lot of overloads, but we prefer to use an example where we first change to the directory and then we send the file, using it’s full path just to be sure that we will save the file at the correct place. At the same time, we replace all the whitespaces with other valid character, because it can be a problem if we have a whitespace at our path. You can use this time to replace other special characters as well. Another point that need some attention, is that we used a string with the file path, but we can use an inputstream or a file, but we stick with the string path, because this way, we don’t need to read the file before the library, if the library itself could do it for you before sending. The user feedback is given as a boolean value, so he can check if it was a success.

```java
public boolean download(String arquivoRemoto, String arquivoLocal){
		
		try {			
			ChannelSftp sftp = (ChannelSftp) session.openChannel("sftp");			
			sftp.connect();						
			sftp.get(arquivoRemoto, arquivoLocal);			
			sftp.disconnect();
			return true;
				
		} catch (Exception e) {
			e.printStackTrace();
		}
		return false;
	}
```

Same logic is used to download a file, it’s like a reverse upload, changing only the put method with get, the library will save the remote file on the given path, and we return a boolean to the user on the same fashion.

Simple, isn’t it? But believe me, this library could save us a lot of time and give us a lot of flexibility on executing tasks, like checking if a remote file exist, exchange files between servers, start and stop and application or a service, check disk usage on a raw way, execute system updates and so on. Can you measure the flexibility that we gain with this simple lib?

## Building a usable lib

Now, on the next step, we will create a simple way of consuming this class, unifying some repeated code on a single place, creating key functionalities to our daily use. Let’s start with something simple, like creating a directory.

```java
public static void criaDir(String usuario,String senha, String host, int porta, String dirDestino) {
		ShellConnectionStream ssh = new ShellConnectionStream(usuario, senha, host, porta);
		try{
			ssh.connect();
			if(ssh.isReady()) {
				ssh.write("mkdir -p " + dirDestino);
				ssh.close();
			}
		}catch(Exception e){ e.printStackTrace(); }		
		
	}
```

Simple right? And how we will consume it?

```java
package org.paulushc.ssh;

import java.util.Arrays;

public class SSHUso {

	private static String usuario = "usuario";
	private static String senha = "senha";
	private static String host = "127.0.0.1";
	private static int porta = 22;
	
	public static void main(String[] args){		
				
		SSHUtils.criaDir(usuario,senha,host,porta,"/home/desenv/200/");
			
	}
	
	
}
```

Wow, now that’s something. Now we can create some remote directories right? What more can we do? How about, check if a file exist?

```java
public static boolean existFile(String usuario,String senha, String host, int porta,String destino){

		ShellConnectionStream ssh = new ShellConnectionStream(usuario, senha, host, porta);
		try{
			ssh.connect();
			if(ssh.isReady()) {
				String retorno = ssh.write("[ -f " + destino +" ]  && echo 1 || echo 0 ");
				ssh.close();
				if(retorno != null){
					retorno = retorno.replace("\n", "");
					return  Long.parseLong(retorno) > 0;
				}
				return false;
			}
		}catch(Exception e){ e.printStackTrace(); }		
		return false;
	}
```

Now we are talking Paulo, now I can see what you are talking about. Now, how about… move files?

```java
public static void renameFile(String usuario,String senha, String host, int porta, String dirArquivoOriginal, String dirArquivoNovo) {
		ShellConnectionStream ssh = new ShellConnectionStream(usuario, senha, host, porta);
		try{
			ssh.connect();
			if(ssh.isReady()) {
				dirArquivoOriginal =  dirArquivoOriginal.replace(" ", "\\ ");
				ssh.write("mv " + dirArquivoOriginal + " " + dirArquivoNovo);
				ssh.close();
			}
		}catch(Exception e){ e.printStackTrace(); }		
		
	}
```

So… how about upload? And if I want to send more than one file at time?

```java
public static boolean uploadTo(String usuario,String senha, String host, int porta,String destino,String dirDestino, String arquivo){
  criaDir(usuario, senha, host, porta, dirDestino);
	ShellConnectionStream ssh = new ShellConnectionStream(usuario, senha, host, porta);
	try{
		ssh.connect();
		if(ssh.isReady()) {
			if(ssh.upload(arquivo,destino, dirDestino)){
				ssh.close();
				return true;				
			}
		}
	} catch(Exception e){ e.printStackTrace(); }		
	return false;
}

public static boolean uploadTo(String usuario,String senha, String host, int porta,String dirDestino, List<String> arquivos){
	criaDir(usuario, senha, host, porta, dirDestino);
	ShellConnectionStream ssh = new ShellConnectionStream(usuario, senha, host, porta);
	try{
		ssh.connect();
		if(ssh.isReady()) {
			for(String arquivo : arquivos){
				if(!ssh.upload(arquivo, dirDestino)){
					ssh.close();
					return false;
				}
			}
			ssh.close();
			return true;
		}
	} catch(Exception e){ e.printStackTrace(); }		
	return false;
}
```

The possibilities are endless, this is just the tip of the iceberg. You can make some task execute automatically, using code, like cleaning temporary files, manage servers on a centralized manner, or maybe, like myself, you need a Swiss Army knife, that will save you from trouble and from unnecessary dependencies.

Did you like? This was my first article, and my first in English as well, as you may notice or not, I’m from Brazil and english is “just” my second language, so sorry if i made any mistake writing this article, and I hope this article could be useful for you on creating an autonomous application your company or at home, share with your friends and your colleagues.

You can check all the source code at my [GitHub](https://github.com/paulushcgcj/sshutil) if you prefer.

See you next time.