---
title:  "Database Encryption Pt1 - Column Encryption"
date:   2024-04-15 12:00:00 -0700
categories: [article, tech, database, security, spring, jdbc, r2dbc]
author: paulushc
permalink: /articles/database-encryption-pt1
header:
    teaser: /assets/2024/04/articles/dbcrypt-01-cover.png
    overlay_image: /assets/2024/04/articles/dbcrypt-01-cover.png
    overlay_filter: 0.5
    show_overlay_excerpt: false
---
In today's digital landscape, safeguarding sensitive data is paramount. As cyber threats continue to evolve, organizations must adopt robust measures to protect their information assets from unauthorized access and malicious attacks. One such measure is database encryption, a fundamental technique for securing data at rest. By encrypting data within the database itself, organizations can ensure that even if unauthorized access occurs, the data remains indecipherable and thus protected from prying eyes.

<!--more-->

In this article, we embark on a journey to explore the realm of database encryption using PostgreSQL in conjunction with Spring Boot, a popular Java framework for building enterprise-grade applications. Our mission is twofold: first, to demystify the process of implementing database encryption within a PostgreSQL environment, and second, to showcase how Spring Boot empowers developers to seamlessly integrate encrypted data into their applications using both blocking and reactive approaches.

By the end of this article, readers will have gained a comprehensive understanding of the principles behind database encryption, as well as practical insights into how to incorporate encryption seamlessly into their Spring Boot projects. Armed with this knowledge, developers will be better equipped to fortify their applications against data breaches and uphold the highest standards of data security. To keep the article concise, I will split it into 3 parts, the first one (this article) will deal with column encryption, the second one with connection encryption and the last one with data at rest encryption.

All code can be found on [GitHub](https://github.com/paulushcgcj/article-database-encryption) so don't worry about copying it from here if you don't want to. The main branch contains the starting point, so you can checkout and start fresh along with this article, and in case you get stuck, check the referenced tags on each step.
Let's dive in and unlock the secrets of database encryption with PostgreSQL and Spring Boot!


---

# Getting started
>  By the end of this section, you should have something like [the content of tag v1.0.0](https://github.com/paulushcgcj/article-database-encryption/releases/tag/v1.0.0)

To get started, we will need a Postgres database instance, some data and some code. We're going to start by defining a Postgres instance. Notice that we are not doing anything special here with this image, just defining a healthcheck.

```dockerfile
FROM postgres:16.2-alpine3.19

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres
```

We're going to control the database version through the use of [Flyway](https://flywaydb.org/) but to keep the explanation as clear as possible, we will keep the SQL script files here for clarity. We're going to start with a simple structure, defining a new schema called `secure` just to keep the code segregated from any other example data you have. We will then create a simple `person` table to persist some randomly generated data.

```sql
create schema if not exists secure;  
  
create table if not exists secure.person (  
  id SERIAL NOT NULL,  
  first_name VARCHAR(50) NOT NULL,  
  last_name VARCHAR(50) NOT NULL,  
  email VARCHAR(50) NOT NULL,  
  gender VARCHAR(50) NOT NULL,  
  CONSTRAINT person_email_key UNIQUE (email),  
  CONSTRAINT person_pk PRIMARY KEY (id)  
);
```

The above table is pretty simple, but contains a lot of information that we consider PII (Personal Identifiable Information), and if you don't know what PII is, check this link on  [Province of British Columbia (gov.bc.ca)](https://www2.gov.bc.ca/assets/gov/business/business-management/protecting-personal-information/pipa-guide.pdf) website. 

> Simply put, personal information is any recorded information about an identifiable individual other than their business contact information. Personal information includes information that can be used to identify an individual through association or inference.

Let's insert some information into the database so we can have something to be consumed by our API. The simple plain text example below represents the great majority of databases around the globe that persists PII. Depending on how you handle the database security (and to be frank, if you already handle database security and PII data, you would probably not be reading this article) you can keep the content as text and secure the database using another approach, but nothing prevents you from adding multiple layers of security one on top of the other.

```sql
insert into secure.person (first_name, last_name, email, gender) values ('Ulrich', 'Setterfield', 'usetterfield0@scientificamerican.com', 'Male') on conflict (email) do nothing;  
  
insert into secure.person (first_name, last_name, email, gender) values ('Kira', 'Bagnal', 'kbagnal1@opensource.org', 'Female') on conflict (email) do nothing;  
  
insert into secure.person (first_name, last_name, email, gender) values ('Jesus', 'Sabate', 'jsabate2@loc.gov', 'Male') on conflict (email) do nothing;  
  
insert into secure.person (first_name, last_name, email, gender) values ('Tyrone', 'Wragge', 'twragge3@aboutads.info', 'Male') on conflict (email) do nothing;  
  
insert into secure.person (first_name, last_name, email, gender) values ('Imogene', 'Simmill', 'isimmill4@e-recht24.de', 'Female') on conflict (email) do nothing;
```

# The code
>  By the end of this section, you should have something like [the content of tag v1.0.0](https://github.com/paulushcgcj/article-database-encryption/releases/tag/v1.0.0)

The initial code is super simple. There's nothing fancy here that requires any mention, so checkout the repository and start playing with it.

As this article is meant to help reactive and non-reactive users, you will find two folders inside the repository, one for the reactive and one for the non-reactive. Use the one you're more comfortable with, and if you want, compare with the other approach.

# Securing data with pgcrypto
>  By the end of this section, you should have something like [the content of tag v1.1.0](https://github.com/paulushcgcj/article-database-encryption/releases/tag/v1.1.0)


To allow the usage of the pgcrypto extension, we need to enable the pgcrypto extension in our database. To allow for encryption, we need to enable pgcrypto first:

```sql
CREATE EXTENSION IF NOT EXISTS pgcrypto;
```

We can add it as part of the initialization of our database in our dockerfile like this:

```dockerfile
# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" >> /docker-entrypoint-initdb.d/init.sql
```

So we will end-up with a dockerfile exactly like this one:

```dockerfile
FROM postgres:16.2-alpine3.19

# Enable the pgcrypto extension
RUN echo "CREATE EXTENSION IF NOT EXISTS pgcrypto;" >> /docker-entrypoint-initdb.d/init.sql

# Basic health check
HEALTHCHECK --interval=35s --timeout=4s CMD pg_isready -d db_prod

# Non-privileged user
USER postgres
```


With the extension enabled, we can then start changing a few data related things. We will take a safer approach here to prevent business continuity problems and allow us to migrate data using database versioning with flyway. For that, we will create the same table but now with different field formats, instead of text based fields (varchar) we will use a binary based field (bytea) so we can store the encrypted data as binary. We will apply it to every single field we want to secure, so in our example we will migrate all text fields.

Let's create the table again with a temporary name, so we can keep both tables at once to migrate data into the new one.

```sql
create table if not exists secure.person_tmp (  
    id SERIAL  NOT NULL,  
    first_name BYTEA NOT NULL,  
    last_name BYTEA NOT NULL,  
    email BYTEA NOT NULL,  
    gender BYTEA NOT NULL,  
    CONSTRAINT person_email_key UNIQUE (email),  
    CONSTRAINT person_pk PRIMARY KEY (id)  
);
```

As you can see, the new temporary table is based on our existing table, with a temporary name but with bytea fields. Those fields will hold encrypted data into it, and if you want to test it, you can insert encrypted data into it with the below script.

```sql
insert into secure.person_tmp (first_name, last_name, email, gender) values (pgp_sym_encrypt('Ulrich', 'AES_KEY'), pgp_sym_encrypt('Setterfield', 'AES_KEY'), pgp_sym_encrypt('usetterfield0@scientificamerican.com', 'AES_KEY'), pgp_sym_encrypt('Male', 'AES_KEY'));

insert into secure.person_tmp (first_name, last_name, email, gender) values (pgp_sym_encrypt('Kira', 'AES_KEY'), pgp_sym_encrypt('Bagnal', 'AES_KEY'), pgp_sym_encrypt('kbagnal1@opensource.org', 'AES_KEY'), pgp_sym_encrypt('Female', 'AES_KEY'));

insert into secure.person_tmp (first_name, last_name, email, gender) values (pgp_sym_encrypt('Jesus', 'AES_KEY'), pgp_sym_encrypt('Sabate', 'AES_KEY'), pgp_sym_encrypt('jsabate2@loc.gov', 'AES_KEY'), pgp_sym_encrypt('Male', 'AES_KEY'));

insert into secure.person_tmp (first_name, last_name, email, gender) values (pgp_sym_encrypt('Tyrone', 'AES_KEY'), pgp_sym_encrypt('Wragge', 'AES_KEY'), pgp_sym_encrypt('twragge3@aboutads.info', 'AES_KEY'), pgp_sym_encrypt('Male', 'AES_KEY'));

insert into secure.person_tmp (first_name, last_name, email, gender) values (pgp_sym_encrypt('Imogene', 'AES_KEY'), pgp_sym_encrypt('Simmill', 'AES_KEY'), pgp_sym_encrypt('isimmill4@e-recht24.de', 'AES_KEY'), pgp_sym_encrypt('Female', 'AES_KEY'));
```

This will insert the same entries we had insert before into our non-encrypted table. This will allow us to have a fair comparison between both tables. Noticed that we are using the `gpg_sym_encrypt` function from `pgcrypto` in order to encrypt the data being passed with the provided key. The `AES_KEY` is the key we will use to encrypt the data. According to the documentation, it can be a text or an encryption key. Keep in mind that for the purpose of this example, I will use as a value and refer to it as the `AES_KEY`, but make sure to use a proper and secure key and handle it with care.

# Consuming the secured data

If you check the encrypted data using the database UI or through SQL, you will notice that it will return some gibberish binary data that makes zero-sense. To properly read the data, we will need to use the `AES_KEY` we used to encrypt the data when inserted and use the corresponding reverse function to decrypt the data like:

```sql
SELECT
	id,
	pgp_sym_decrypt(first_name, 'AES_KEY') AS first_name,
	pgp_sym_decrypt(last_name, 'AES_KEY') AS last_name,
	pgp_sym_decrypt(email, 'AES_KEY') AS email,
	pgp_sym_decrypt(gender, 'AES_KEY') AS gender
FROM
	secure.person_tmp;
```

This should return the same result as the original table with the original data on it. Play around with it for now to get used to it.

# Migrating existing table

My approach is more reasonable and safer. I would start by creating a temporary table with the correct structure as mentioned on [[#Secure data]] topic, with a random name.
Then I would do an insert from a select that encrypts the data into the new temp table

```sql
INSERT INTO secure.person_tmp (id, first_name, last_name, email, gender)

SELECT
	id,
	pgp_sym_encrypt(first_name::text, 'AES_KEY')::bytea AS first_name,
	pgp_sym_encrypt(last_name::text, 'AES_KEY')::bytea AS last_name,
	pgp_sym_encrypt(email::text, 'AES_KEY')::bytea AS email,
	pgp_sym_encrypt(gender::text, 'AES_KEY')::bytea AS gender
FROM
	secure.person  
ON CONFLICT (ID) DO NOTHING;
```

Once the data is migrated, we can check if everything is ok by comparing some of the data between the original (unencrypted) table and the new secure (encrypted) table. If it matches, it will return `true`. Notice that we are doing this with on conflict as well to prevent inserting data that already exists.

```sql
SELECT
	CASE
		WHEN
			(p.first_name = pgp_sym_decrypt(pe.first_name, 'AES_KEY')::text) AND
			(p.last_name = pgp_sym_decrypt(pe.last_name, 'AES_KEY')::text) AND
			(p.email = pgp_sym_decrypt(pe.email, 'AES_KEY')::text) AND
			(p.gender = pgp_sym_decrypt(pe.gender, 'AES_KEY')::text)
		THEN
			TRUE
		ELSE
			FALSE
	END AS all_columns_match
FROM
	secure.person p
JOIN
	secure.person_tmp pe ON p.id = pe.id
limit 2;
```

Keep in mind that the limit is here just to get a sample of the data instead of all entries. We expect that a small sample should be enough to verify the effectiveness of the migration. With this query in mind, we can put it into a stored procedure and do the migration check and the database renaming part like the following:

```sql
CREATE OR REPLACE FUNCTION compare_and_replace_table()
RETURNS VOID AS
$$
DECLARE
	all_columns_match BOOLEAN;
BEGIN  

	SELECT
		CASE
			WHEN
				(p.first_name = pgp_sym_decrypt(pe.first_name, 'AES_KEY')::text) AND
				(p.last_name = pgp_sym_decrypt(pe.last_name, 'AES_KEY')::text) AND
				(p.email = pgp_sym_decrypt(pe.email, 'AES_KEY')::text) AND
				(p.gender = pgp_sym_decrypt(pe.gender, 'AES_KEY')::text)
			THEN
				TRUE
			ELSE
				FALSE
		END AS all_columns_match
	INTO
		all_columns_match
	FROM
		secure.person p
	JOIN
		secure.person_tmp pe ON p.id = pe.id
	limit 2;

	 IF all_columns_match THEN
		DROP TABLE secure.person;
		ALTER TABLE secure.person_tmp RENAME TO person2;
	END IF;
END;
$$
LANGUAGE plpgsql;
```

Again, bear in mind that the `AES_KEY` value should be replaced, along with the table names and fields.

# Migrating existing code

Now it's time to change the existing code to allow us to read and write using the encrypted data. I will guide you through the steps required to make your application read and write using the encryption/decryption key in the most simple and efficient way possible. Keep in mind that the non-reactive approach, using JDBC is simpler than the reactive counterpart, but both have its own merits and caveats.

If you spin up your application right now and try to list all entries, you'll notice that the field content is returning some gibberish text, that represents some binary data that makes zero-sense. This is because we're not decrypting the content when reading. Let's see how we can fix this.

## Traditional JDBC non-reactive

Hibernate and Spring Data got a few annotations available to help you speed up your setup. This makes the approach to setup encryption and decryption a walk in the park. Let's start with a simple approach, test it and then make it solid and secure (as much as possible).

Assuming that our entity class is originally like this:

```java
@Entity  
@Table(name = "person", schema = "secure")  
@NoArgsConstructor  
@AllArgsConstructor  
@Data  
@With  
@Builder  
public class PersonEntity {  
  
  @Id  
  @GeneratedValue(strategy = GenerationType.IDENTITY)  
  private Long id;  
  
  @Column(name = "first_name", length = 50)
  private String firstName;
// ... other properties
}
```

The only change required to make the fields decrypt the data (and encrypt it when inserting) is a simple annotation from the hibernate dependency, `org.hibernate.annotations.ColumnTransformer`. This annotation allow us to specify how a column should be transformed when reading and writing, and it contains 3 parameters, but we're using only 2, called `read` and `write`, and they're self-explanatory. Now, let's add it to the field:
 
```java
@Column(name = "first_name", length = 50)  
@ColumnTransformer(  
    read = "pgp_sym_decrypt(first_name, 'AES_KEY')",  
    write = "pgp_sym_encrypt(?, 'AES_KEY')"  
)  
private String firstName;
```

Can't be simpler than that right? Right! But notice that we are providing the encryption key as plain text to be persisted in our repository, exposing our secret key to the world, let's figure a way to make it more secure.

One approach is to add it to the Postgres configuration file and read it using the `current_setting` function, but this requires you to bake the key into the database load, exposing it for possible attacks. More info on [PostgreSQL: Documentation: 16: 20.1. Setting Parameters](https://www.postgresql.org/docs/current/config-setting.html). Instead, we will make use of the `current_setting` as before but we will read it from the current session, and we will set the value in the session using the JDBC connection string. 

Postgres support an options argument where it can receive some arguments that are then passed down to the current session, check [Initializing the Driver | pgJDBC (postgresql.org)](https://jdbc.postgresql.org/documentation/use/#connection-parameters) for more information. This approach is better as it will not expose the parameter to the entire database, making whoever is connection to your database using other session unaware of the available values being passed, but at the same time exposes the value as part of the connection string, so make sure to not expose it during your application execution. Make sure to read the value from a secure place though.

First let's change our connection string. Originally it was like this:

```yaml
spring:
	datasource:  
		  url: jdbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}
```

We use those variables to be able to store the data somewhere else and replace it. The only addition we have to do to this connection string is to add the options parameter with the key-value pair we need, like:

```yaml
spring:
	datasource:  
		url: jdbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?options=-c%20cryptic.key=${io.github.paulushcgcj.database.key}
io:  
  github:  
    paulushcgcj:  
      database:          
        key: ${DB_KEY:AES_KEY}
```

Here we used the key called `cryptic.key` and we can fetch it when using it in our queries. Let's update our entity again to change the hardcoded value with the key from the connection string.

```java
@Column(name = "first_name", length = 50)  
@ColumnTransformer(  
    read = "pgp_sym_decrypt(first_name, current_setting('cryptic.key'))",  
    write = "pgp_sym_encrypt(?, current_setting('cryptic.key'))"  
)  
private String firstName;
```

We just replace the hardcoded key value with the parameter reading from the session. You can add the same annotation to all the other fields and test and you'll see that the results are being returned perfectly. Easy right?

## Reactive connection with r2dbc

Reactive programming has its own set of challenges and benefits. One of the challenges is the lack of compatibility with some libraries and even some basic annotations. Spring uses [Project Reactor](https://projectreactor.io/) as its base for reactive programming, and it relies on `Mono` and `Flux` as base. Due to that, some standard libraries, such as [Hibernate](https://hibernate.org/) are not compatible with it, as it makes use of [Eclipse Vert.x](https://vertx.io/) as its base instead of reactor. This mean that some of the default annotations are not present, and some joins becomes kinda cumbersome, but worry not, I'm here to help.

First, we will need to change the field type of our encrypted data. We can keep using string if we want, but we will have to convert it back when decrypting it, so it's easier to just keep it as byte array.

```java
@Column(value = "first_name")  
private byte[] firstName;
```

This will make things kinda hard to managed on the entity level, in case we want to change some data directly on the entity, forcing us to add some extra hops in order to deal with the data itself. This is due to the lack of support that hibernate adds as can be seen in the [previous section](#Traditional JDBC non-reactive) with the `@ColumnTransformer` annotation.

Next, we will have to manually call the encrypt and decrypt query in order to encrypt/decrypt the data. We have a lot of options when it comes to data conversion using r2dbc, but the problem is the lifecycle. The converter lives as part of the r2dbc instantiation lifecycle, so if we inject the database connection (it can be straight with the `R2dbcEntityTemplate` or by injecting a `Repository`) it will create a circular dependency, and even though there are ways to remediate this, it's not a clean solution.

We decided to use an individual component that can be injected into our service class and deal with the conversion there. Keep in mind that the code organization used throughout this article is just a suggestion based on what I'm used to use, so take the names and organization with a grain of salt. This specific component will handle encryption/decryption by itself, and it can be as generic as receiving just the byte array and returning a string or as specialized as  receiving the actual entity and returning it with some `@Transient` field filled with the data, it's up to you.

```java
@Component  
@RequiredArgsConstructor  
public class DatabaseCryptoUtil {  
  
  private final R2dbcEntityTemplate template;  
  
  public Mono<byte[]> decrypt(byte[] data) {  
    return decryptAsString(data)  
        .map(s -> s.getBytes(StandardCharsets.UTF_8));  
  }  
  
  public Mono<String> decryptAsString(byte[] data) {  
    return template  
        .getDatabaseClient()  
        .sql("SELECT pgp_sym_decrypt(:data, current_setting('cryptic.key')) AS decrypted_data")  
        .bind("data", data)  
        .map((row, rowMetadata) -> row.get("decrypted_data", String.class))  
        .first();  
  }  
  
  public Mono<byte[]> encrypt(byte[] data) {  
    return encryptFromString(new String(data, StandardCharsets.UTF_8));  
  }  
  
  public Mono<byte[]> encryptFromString(String data) {  
    return template  
        .getDatabaseClient()  
        .sql("SELECT pgp_sym_encrypt(:data, current_setting('cryptic.key')) AS encrypted_data")  
        .bind("data", data)  
        .map((row, rowMetadata) -> row.get("encrypted_data", byte[].class))  
        .first();  
  }  
  
}
```

In my case, I went with the generic approach and came up with the above example. This will call the database function to encrypt the data, and as we did before with the JDBC version, we will read the key from the connection session. With that, we just have to add some encryption and decryption methods in our service class to make things easier.

```java
private Mono<PersonEntity> decrypt(PersonEntity personEntity) {  
  return  
      databaseCryptoUtil  
          .decrypt(personEntity.getFirstName())  
          .map(personEntity::withFirstName)  
          .flatMap(entity -> databaseCryptoUtil  
              .decrypt(entity.getLastName())  
              .map(entity::withLastName)  
          )  
          .flatMap(entity -> databaseCryptoUtil  
              .decrypt(entity.getEmail())  
              .map(entity::withEmail)  
          )  
          .flatMap(entity -> databaseCryptoUtil  
              .decrypt(entity.getGender())  
              .map(entity::withGender)  
          );  
}  
  
private Mono<PersonEntity> encrypt(PersonEntity personEntity) {  
  return  
      databaseCryptoUtil  
          .encrypt(personEntity.getFirstName())  
          .map(personEntity::withFirstName)  
          .flatMap(entity -> databaseCryptoUtil  
              .encrypt(entity.getLastName())  
              .map(entity::withLastName)  
          )  
          .flatMap(entity -> databaseCryptoUtil  
              .encrypt(entity.getEmail())  
              .map(entity::withEmail)  
          )  
          .flatMap(entity -> databaseCryptoUtil  
              .encrypt(entity.getGender())  
              .map(entity::withGender)  
          );  
}
```

Then it's just a matter of using those methods when required, like this:

```java
public Mono<PersonDto> findById(Long id) {  
  log.info("Finding person by id: {}", id);  
  return personRepository  
      .findById(id)  
      .flatMap(this::decrypt)  //Called the decrypt method before the conversion to DTO
      .map(this::convertToDto);  
}
```

Not as simple as the JDBC version, but not so complicated too. This makes the encryption and decryption a breeze, even though it makes some of our entities less legible as we will be dealing with byte arrays, but that's not a big deal in terms of code being added. Keep in mind also that we are trying to avoid adding any extra dependency or library into the equation to make this example as easier as possible to understand. You could be using a different library set that can or cannot already add some functionality that makes this process easier.

Now as the last required change, we will set the key into the connection session as we did with the JDBC version. This time we will have to change it twice, as flyway still uses jdbc connections behind the scene.

```yaml
spring:
  r2dbc:  
    url: r2dbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?options=cryptic.key=${io.github.paulushcgcj.database.key}
  flyway:      
    url: jdbc:postgresql://${io.github.paulushcgcj.database.host}/${io.github.paulushcgcj.database.name}?options=-c%20cryptic.key=${io.github.paulushcgcj.database.key}  
io:  
  github:  
    paulushcgcj:  
      database:          
        key: ${DB_KEY:AES_KEY}
```

The key difference here is the way we pass the options to the connection. When dealing with JDBC, we use the `-c key=value` param while with R2DBC, we can simply pass the `key=value` pair straight to the options parameter.

# Considerations

With this we are done securing some fields with a little bit of encryption. In this article we used `pgp_sym_encrypt` and `pgp_sym_decrypt` functions that uses the PGP symmetric key to encrypt the data, but Postgres provides some other methods to encrypt data as well.

In conclusion, we've embarked on a journey to fortify our applications against potential security threats by implementing column-level encryption in PostgreSQL with Spring Boot. Through a meticulous exploration of both reactive and non-reactive approaches, we've demonstrated how to encrypt and decrypt sensitive data, ensuring its confidentiality and integrity within the database. By harnessing the power of Spring Boot and R2DBC for reactive applications and JDBC for non-reactive ones, we've equipped ourselves with versatile tools to safeguard our data against unauthorized access and malicious attacks.

As we conclude this chapter of our exploration into database encryption, we recognize that our journey is far from over. In our next instalment, we will delve into the realm of connection encryption, where we'll focus on securing the communication channel between our Spring Boot application and the PostgreSQL database. By extending our security measures to encompass encryption in transit, we continue to reinforce the resilience of our applications and uphold the highest standards of data protection. Join us as we embark on the next phase of our quest for data security, where we'll explore the intricacies of connection encryption and further fortify our applications against modern threats.