---
title:  "Database Encryption Pt2 - Connection Encryption"
date:   2024-04-26 09:30:00 -0700
categories: [article, tech, database, security, spring, jdbc, r2dbc]
author: paulushc
permalink: /articles/database-encryption-pt2
header:
    teaser: /assets/2024/04/articles/dbcrypt-02-cover.jpg
    overlay_image: /assets/2024/04/articles/dbcrypt-02-cover.jpg
    overlay_filter: 0.5
    show_overlay_excerpt: false
---
Welcome back to the second instalment of our journey into the realm of database encryption with PostgreSQL and Spring Boot. In this continuation of our multipart series, we delve deeper into the realm of data security, shifting our focus from column-level encryption to the crucial aspect of connection encryption. As we strive to fortify our applications against potential security threats, ensuring secure communication between our Spring Boot application and the PostgreSQL database becomes paramount.

<!--more-->

In this instalment, we embark on a mission to explore the intricacies of connection encryption, a critical component in safeguarding sensitive data as it traverses the network. By encrypting the communication channel between our application and the database, we aim to thwart potential eavesdropping and tampering attempts, thus preserving the confidentiality and integrity of our data. Through a step-by-step approach, we will demonstrate how to enable encryption in the database connection and configure the necessary certificates to establish a secure channel for data transmission.

As we journey through this chapter, readers will gain invaluable insights into the practical implementation of connection encryption in a Spring Boot application interacting with PostgreSQL. By the end of this article, readers will be equipped with the knowledge and tools necessary to bolster the security of their database interactions, laying a solid foundation for building robust and resilient applications in today's ever-evolving threat landscape.

Let's embark on this adventure into connection encryption, as we continue our quest to fortify our applications against security vulnerabilities and uphold the highest standards of data protection. All code can be found on [GitHub](https://github.com/paulushcgcj/article-database-encryption) so don't worry about copying it from here if you don't want to. The main branch contains the starting point, so you can checkout and start fresh along with this article, and in case you get stuck, check the referenced tags on each step.
Let's dive in and unlock the secrets of database encryption with PostgreSQL and Spring Boot!

# Securing the database connection with certificate
>  By the end of this section, you should have something like [the content of tag v1.2.0](https://github.com/paulushcgcj/article-database-encryption/releases/tag/v1.2.0)

Now let's focus on securing the data in transit with SSL certificate. This tutorial (and this repository) will not provide a certificate file for you, and we expect you to already have a certificate to be used. I'll show an example on how to generate a self-signed certificate just for the sake of local test and validation only.

> Heads-up, localhost test and validation to make sure the certificate connection works is kind of finicky as the database will probably detect the connection as local and will fallback to the insecure connection.

Let's begin with a self-signed certificate to use during our example, and keep in mind that this is only for **EDUCATIONAL PURPOSE**, so don't use it in production or any deployed environment.  To generate the certificate, simply run the following command:

```bash
openssl req -x509 -nodes -newkey rsa:4096 -keyout server.key -out server.crt -days 365
```

This will generate two files, `server.key` and `server.crt` files. Those files will be used in our Postgres server. Let's continue from the previous article dockerfile. This is what we had when we left the last article:

```dockerfile
FROM postgres:16.2-alpine3.19

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" >> /docker-entrypoint-initdb.d/init.sql

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres
```

Nothing new here. What we're going to do is restructure the Dockerfile and add the certificates into it. This is not the safest approach, but worry not, we will fix this later. Once we add the certificates to the Dockerfile, we need to change the the initialization instruction to enable SSL connection. The default approach for it would be to add the configuration parameters into `postgres.conf ` but as we are using a docker, and some of the files are generated during container startup, we can't add or modify the configuration file beforehand.

```dockerfile
# Copy SSL certificates to the container
COPY server.crt /certs/server.crt
COPY server.key /certs/server.key

# Change the owner of the certificates
RUN chown postgres:postgres /certs/server.crt /certs/server.key
RUN chmod 0600 /certs/server.key /certs/server.crt
```

We copied both files into the container and changed the the owner and permission of the file to allow postgres to use it. We're copying it to a random folder so we don't interfere with the server initialization. Now let's initialize the server with some extra parameters. Those parameter will enable SSL and pass the certificate files.

```dockerfile
# Start the database setting the SSL certificates
CMD [ "postgres","-c","ssl=on", "-c","ssl_cert_file=/certs/server.crt","-c","ssl_key_file=/certs/server.key" ]
```

With that, we can start the server and this will allow us to connect to the server without any issues. We can now move to the application to set the SSL connection and allow a secure connection. So, just to recap, this is what we have as our current `Dockerfile`.

```dockerfile
FROM postgres:16.2-alpine3.19

# Creates the directory for the certificates
RUN mkdir -p /certs/

# Copy SSL certificates to the container
COPY server.crt /certs/server.crt
COPY server.key /certs/server.key

# Change the owner of the certificates
RUN chown postgres:postgres /certs/server.crt /certs/server.key
RUN chmod 0600 /certs/server.key /certs/server.crt

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > /docker-entrypoint-initdb.d/pgcrypto.sql

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres

# Start the database setting the SSL certificates
CMD [ "postgres","-c","ssl=on", "-c","ssl_cert_file=/certs/server.crt","-c","ssl_key_file=/certs/server.key" ]

```

# Securing the application connection

Securing the application connection is pretty simples. We just need to enable the SSL through the connection string, so this part is pretty simple. Let's begin with the JDBC version first:

```yaml
spring:  
  datasource:  
    url: jdbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?ssl=true&sslmode=require&options=-c%20cryptic.key=${io.github.paulushcgcj.database.key}
```

As you can see, it's super simple, we just added two parameters, one called `ssl` and we set it as true, so we can exchange messages using the SSL connection. The second parameter is the `sslmode` and this dictates the way the certificate will be used. In our case we set it as require to notify the driver that we will only talk to the server using the secure connection.
Seems simple, and it is. There's no code change required to allow the JDBC connection to be secure. Now let's move to the R2DBC connection:

```yaml
spring:  
  datasource:  
    url: r2dbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?sslmode=require&options=cryptic.key=${io.github.paulushcgcj.database.key}
```

Simple as well. On R2DBC, we only need to set the `sslmode` as require and this is enough to enable the secure connection. Remember that when dealing with R2DBC, we usually set the flyway URL as well, and we will need to configure it based on the JDBC configuration above.

```yaml
spring:  
  flyway:  
    url: jdbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?ssl=true&sslmode=require&options=-c%20cryptic.key=${io.github.paulushcgcj.database.key}
```

If we run the application now, nothing will change. As a matter of fact, even without enabling the SSL connection, we will be able to connect to the database. This is due to the fact that by default, Postgres will still enable insecure connection to the database, so we will need to make sure that we will only allow secure connections to the database.

# Restricting database access

To restrict database access, we need to update the `pg_hba.conf` file, where the database sets the access configuration. This file needs to be updated in order to allow or restrict access to the database. In our case we need to set the connections to allow only ssl connections and block insecure connections. This is how we are going to setup the file:

```configuration
hostnossl all all all reject
hostssl all all all scram-sha-256
local all all scram-sha-256
hostssl all all 127.0.0.1/32 scram-sha-256
hostssl all all ::1/128 scram-sha-256
```

First thing, we set connections without SSL (by setting `hostnossl`) connection to any database, any IP and any user to be rejected. As Postgres uses a top-down approach, once it finds a match it will stop processing, that's the reason we set the reject first. Then we set the hostssl connection to be allowed, and the third one allow for local connection to be secured by password. This local connection is usually used by initialization scripts and such, but can be used when connection to the database.

> Due to the local connection configuration, the database can detect some localhost test and validation to be local, ignoring some of the other parameters.

With this configuration in mind, we need a way to set it. Problem is, if we just map the new file to the folder where it is supposed to be, the container will not initialize properly. We need to set the entries using the init scripts. Let's do this then by setting a temporary file that we will then use it to replace the existing one then.

```dockerfile
# Set the pg_hba.conf file and add the permissions
RUN echo "hostnossl all all all reject" > /certs/pg_hba.conf
RUN echo "hostssl all all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "local all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all 127.0.0.1/32 scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all ::1/128 scram-sha-256" >> /certs/pg_hba.conf
RUN chown postgres:postgres /certs/pg_hba.conf
RUN chmod 0600 /certs/pg_hba.conf
```

Then, we need to do the dance move, where we replace one file with the other. For this we will create a new file inside the init folder, but this time it will be a shell script.

```dockerfile
# Copy the pg_hba.conf file to the container
RUN echo "cp /certs/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf" > /docker-entrypoint-initdb.d/01-pg_hba.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-pg_hba.sh
```

With those changes, we are now able to to limit the access to the database to SSL secure connections only. Now our dockerfile should look like this.

```dockerfile
FROM postgres:16.2-alpine3.19

# Creates the directory for the certificates
RUN mkdir -p /certs/

# Copy SSL certificates to the container
COPY server.crt /certs/server.crt
COPY server.key /certs/server.key

# Change the owner of the certificates
RUN chown postgres:postgres /certs/server.crt /certs/server.key
RUN chmod 0600 /certs/server.key /certs/server.crt

# Set the pg_hba.conf file and add the permissions
RUN echo "hostnossl all all all reject" > /certs/pg_hba.conf
RUN echo "hostssl all all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "local all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all 127.0.0.1/32 scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all ::1/128 scram-sha-256" >> /certs/pg_hba.conf
RUN chown postgres:postgres /certs/pg_hba.conf
RUN chmod 0600 /certs/pg_hba.conf

# Copy the pg_hba.conf file to the container
RUN echo "cp /certs/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf" > /docker-entrypoint-initdb.d/01-pg_hba.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-pg_hba.sh

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > /docker-entrypoint-initdb.d/pgcrypto.sql

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres

# Start the database setting the SSL certificates
CMD [ "postgres","-c","ssl=on", "-c","ssl_cert_file=/certs/server.crt","-c","ssl_key_file=/certs/server.key" ]

```

# Securing the certificate

The way we pass the certificate files to the image is pretty straightforward, but it's also extremely insecure, as anyone with access to our image will be able to copy our certificate files and use it for malicious activities using our key. To prevent that we will instead of bake it into the image, we will expect it to be received as a volume mapping, but not straight to the final folder. First, let's remove the copy commands and the other related ones from the file. We should end up with a dockerfile like this.

```dockerfile
FROM postgres:16.2-alpine3.19

# Creates the directory for the certificates
RUN mkdir -p /certs/

# Set the pg_hba.conf file and add the permissions
RUN echo "hostnossl all all all reject" > /certs/pg_hba.conf
RUN echo "hostssl all all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "local all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all 127.0.0.1/32 scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all ::1/128 scram-sha-256" >> /certs/pg_hba.conf
RUN chown postgres:postgres /certs/pg_hba.conf
RUN chmod 0600 /certs/pg_hba.conf

# Copy the pg_hba.conf file to the container
RUN echo "cp /certs/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf" > /docker-entrypoint-initdb.d/01-pg_hba.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-pg_hba.sh

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > /docker-entrypoint-initdb.d/pgcrypto.sql

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres

# Start the database setting the SSL certificates
CMD [ "postgres","-c","ssl=on", "-c","ssl_cert_file=/certs/server.crt","-c","ssl_key_file=/certs/server.key" ]

```

Now we will expect (and instruct) the image users to provide the certificate by mapping the certificate to the same place we used to copy the certificate files to. Let me show how to pass the certificate files to the container through volume mapping using both the CLI or a compose file.

```bash
docker run -it -v /path/to/server.crt:/certs/server.crt -v /path/to/server.key:/certs/server.key -p 5432:5432 ourpostgresimage
```
```yaml
services:
	database:
		environment:
			POSTGRES_USER: user
			POSTGRES_PASSWORD: password
			POSTGRES_DB: database			
		image: ourpostgresimage
		ports: [5432:5432]
		volumes:
			- ./database/server.crt:/certs/server.crt
			- ./database/server.key:/certs/server.key
```

Now that the user is providing the certificate files, we need to have a way to use it in our application. In the past, we just provided the certificate file path during application boot, but with the certificates being provided externally, the files now are not owner by the database user. To fix that, we will instead of providing the file, we will instead copy them to the default place where the certificates are expected.

```dockerfile
# Copy the certificates to the container
RUN echo "cp /certs/server.crt /var/lib/postgresql/data/server.crt" > /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "cp /certs/server.key /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.crt" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN chmod +x /docker-entrypoint-initdb.d/04-certificate.sh
```

With this script in place, our application will copy the certificate files to the expected place, making the parameters `ssl_cert_file=/certs/server.crt` and `ssl_key_file=/certs/server.key` irrelevant. Another point is, as we have set previously the `CMD` instruction, now our database will try to spin up enabling the SSL certificates before we have properly set them up. This will then cause problems and the database will not be initialize because:

1 - The certificates are now owned by the database user until the init script is executed
2 - The SSL will be turned on during initial initialization of the database, and the certificate files are not yet present.

This could be quite challenging to fix, but we can do that one step at a time. First we need to remove the `CMD` instruction and this will give us the following dockerfile.

```dockerfile
FROM postgres:16.2-alpine3.19

# Creates the directory for the certificates
RUN mkdir -p /certs/

# Set the pg_hba.conf file and add the permissions
RUN echo "hostnossl all all all reject" > /certs/pg_hba.conf
RUN echo "hostssl all all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "local all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all 127.0.0.1/32 scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all ::1/128 scram-sha-256" >> /certs/pg_hba.conf
RUN chown postgres:postgres /certs/pg_hba.conf
RUN chmod 0600 /certs/pg_hba.conf

# Copy the pg_hba.conf file to the container
RUN echo "cp /certs/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf" > /docker-entrypoint-initdb.d/01-pg_hba.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-pg_hba.sh

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > /docker-entrypoint-initdb.d/pgcrypto.sql

# Copy the certificates to the container
RUN echo "cp /certs/server.crt /var/lib/postgresql/data/server.crt" > /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "cp /certs/server.key /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.crt" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN chmod +x /docker-entrypoint-initdb.d/04-certificate.sh

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres

```

Now that we removed the `CMD` instruction, we're also not enabling the SSL configuration. We need to enable it somehow. As we don't have access to the configuration file until the database is online, and the fact that there's no other way for us to provide a partial configuration file without altering the actual configuration file, and this time, we can't use the same tactic we used before, as the files are not yet generated when the init is executed. To circumvent this issue, we can set the configuration using SQL instructions. Let's add this instruction as well as part of our init scripts. Let's see how we can achieve this.

```dockerfile
# Reload the configuration
RUN echo "ALTER SYSTEM SET ssl = 'on';" > /docker-entrypoint-initdb.d/02-reload.sql
RUN echo "SELECT pg_reload_conf();" >> /docker-entrypoint-initdb.d/02-reload.sql
```

With this, we can enable the SSL configuration, and as we are copying the certificates into the correct folder, postgres should be able to figure it out by itself and set everything required. Now, let's just tidy things up and show here what's the expected final dockerfile format.

```dockerfile
FROM postgres:16.2-alpine3.19

# Creates the directory for the certificates
RUN mkdir -p /certs/

# Set the pg_hba.conf file and add the permissions
RUN echo "hostnossl all all all reject" > /certs/pg_hba.conf
RUN echo "hostssl all all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "local all all scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all 127.0.0.1/32 scram-sha-256" >> /certs/pg_hba.conf
RUN echo "hostssl all all ::1/128 scram-sha-256" >> /certs/pg_hba.conf
RUN chown postgres:postgres /certs/pg_hba.conf
RUN chmod 0600 /certs/pg_hba.conf

# Copy the pg_hba.conf file to the container
RUN echo "cp /certs/pg_hba.conf /var/lib/postgresql/data/pg_hba.conf" > /docker-entrypoint-initdb.d/01-pg_hba.sh
RUN chmod +x /docker-entrypoint-initdb.d/01-pg_hba.sh

# Reload the configuration
RUN echo "ALTER SYSTEM SET ssl = 'on';" > /docker-entrypoint-initdb.d/02-reload.sql
RUN echo "SELECT pg_reload_conf();" >> /docker-entrypoint-initdb.d/02-reload.sql

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" > /docker-entrypoint-initdb.d/03-pgcrypto.sql

# Copy the certificates to the container
RUN echo "cp /certs/server.crt /var/lib/postgresql/data/server.crt" > /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "cp /certs/server.key /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.crt" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN echo "chown postgres:postgres /var/lib/postgresql/data/server.key" >> /docker-entrypoint-initdb.d/04-certificate.sh
RUN chmod +x /docker-entrypoint-initdb.d/04-certificate.sh

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres
```

I've named all scripts into an order, to make the execution more predictable, as the init scripts run in order based on name, so nothing easier than setting a numeric order for our files. The second script is the one we use to enable SSL and reload the configuration. Is the reload required? No is not, as the database will shut down and restart after that, but it's a good sanity check nonetheless. This solve our problem of not being able to change the files manually or having to manually change it after the database is started.

# Passing the certificates

Now, for the final piece of this puzzle, we can pass the certificate files in both cases. It's simple and straightforward. Let's begin with the JDBC one.

```yaml
spring:    
  datasource:      
    ssl: true  
    ssl-root-cert: /path/to/server.crt
```

Super simple. We will reuse it in our flyway R2DBC configuration, so let's move to it and set the configuration.

```yaml
spring:  
	r2dbc:  
		url: r2dbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?sslmode=require&sslrootcert=file:${io.github.paulushcgcj.database.ssl-path}&options=cryptic.key=${io.github.paulushcgcj.database.key}  
	flyway:    
		ssl: true  
		ssl-root-cert: ${io.github.paulushcgcj.database.ssl-path}
io:  
  github:  
    paulushcgcj:  
      database:  
        ssl-path: ${SSL_PATH}
```

As you can see, I moved the cert file into a specific configuration so I can pass it as an environment variable as well. It's pretty hard to see, but we've added a new parameter to our R2DBC configuration called `sslrootcert` and we're passing a file with the certificate using our new variable like `file:${io.github.paulushcgcj.database.ssl-path}` and this is all we need to set the certificates into the R2DBC connection.

# Recap

Well, folks, we've reached the end of another chapter in our quest for data security. In this instalment, we've rolled up our sleeves and tackled the vital task of securing our database connections with PostgreSQL. By configuring PostgreSQL to utilize a secure connection and updating our connection strings to leverage SSL, we've added another layer of defence to our data fortress. With each keystroke and configuration tweak, we're locking down our applications tighter than a vault.

But hey, the journey's not over yet! In our next adventure, we'll dive headfirst into the realm of encryption at rest. Yep, you heard it right – we're taking our data security game to the next level by encrypting the database itself. So grab your encryption keys and buckle up, because things are about to get even more secure around here. Until next time, stay curious and keep coding securely!
