# Real Estate Finder

***Languages***
- **🇺🇸 - English**
- [🇪🇸 - Español](./README.md)
---

This project seeks to create a real estate search engine with the objective of providing users with an efficient and user-friendly tool to find real estate that fit their needs and preferences.

With this search engine, users will be able to perform customized searches based on different criteria, such as location, property type, price, size and more.

---


## Technologies Used
- **Python** will be the primary programming language to develop the backend microservices. Also, I will be using the following packages and libraries: `unittest` for writing and running tests, `mysql-connector-python` for connecting to MySQL database, `Pydantic` for data validation and `Uvicorn` as the ASGI web server.
- **Docker** to facilitate the creation and deployment of microservices in an isolated environment.

---


## Development Approach
In this project, I will follow a Test-Driven Development (TDD) methodology. This means that I will start by creating unit tests that cover different aspects of the microservices, from the database connection to the expected response of the endpoints. I will adhere to the PEP8 coding style guide to maintain clean and readable code.

Additionally, I will consider conditions and information that should not be exposed in the endpoints, ensuring that I implement the corresponding methods to handle these cases.

---


## API Endpoint

- **/real-estates**

	*Method* (GET)

	*Supported parameters* (Query string)

	|Parameter|Type|Example|
	|---|---|---|
	|status|`str`|pre_venta|
	|city|`str`|bogota|
	|year|`int`|2000|

	```bash
	curl -i -X GET http://127.0.0.1:5000/real-estates?status=pre_venta\&city=bogota\&year=2000
	```

- **/real-estates/{id}/likes**

	*Method* (POST)

	```bash
	curl -i -X POST -H "Authorization: Basic dGVzdF91c2VyOnRlc3RwYXNzMTIz" http://127.0.0.1:5000/real-estates/1/likes
	```

---


## How to run it
1. Set the database credentials in the `.env` file in the backend directory, based on the [.env-sample](./backend/.env-sample) file found in the same directory
2. To run the unit tests run the following command
	```bash
	docker compose -f docker-compose.yml -f dockerfiles/compose/docker-compose.test.yml run --rm backend
	```
3. To run the microservice, execute the following command
	```bash
	docker compose -f docker-compose.yml -f dockerfiles/compose/docker-compose.local.yml up backend
	```

---


## Database
- Create the `property_likes` table to handle user likes, I don't create a unique user key with the property so the user can like it more than once

	![property_likes](property_likes.png "Entity relation model")
	```sql
	CREATE TABLE `property_likes` (
		`id` int(11) NOT NULL AUTO_INCREMENT,
		`property_id` int(11) NOT NULL,
		`user_id` int(11) NOT NULL,
		`create_date` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
		PRIMARY KEY (`id`),
		CONSTRAINT `property_likes_property_id_fk` FOREIGN KEY (`property_id`) REFERENCES `property` (`id`),
		CONSTRAINT `property_likes_user_id_fk` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
	) ENGINE=InnoDB DEFAULT CHARSET=latin1;
	```
	> This table has been created for the endpoint `/real-estates/{id}/likes`

- Suggested improvements to the database:
	- In the property table normalize the column city, year
		```sql
		CREATE TABLE `property_city` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`name` varchar(32) NOT NULL,
			PRIMARY KEY (`id`)
		) ENGINE=InnoDB DEFAULT CHARSET=latin1
		AS
		SELECT NULL AS id, city AS name
		FROM property
		WHERE city!=''
		GROUP BY 2
		ORDER BY 2 ASC;

		ALTER TABLE `property` MODIFY COLUMN city varchar(32) CHARACTER SET latin1 COLLATE latin1_swedish_ci DEFAULT NULL NULL;

		CREATE TABLE `property_year` (
			`id` int(11) NOT NULL AUTO_INCREMENT,
			`year` int(4) NOT NULL,
			PRIMARY KEY (`id`)
		) ENGINE=InnoDB DEFAULT CHARSET=latin1
		AS
		SELECT NULL AS id, `year`
		FROM property
		WHERE `year` IS NOT NULL
		GROUP BY 2
		ORDER BY 2 ASC;

		UPDATE `property` p LEFT JOIN `property_city` pc ON p.city = pc.name SET p.city = pc.id;
		UPDATE `property` p INNER JOIN `property_year` py ON p.`year` = py.`year` SET p.`year` = py.id;

		ALTER TABLE `property` MODIFY COLUMN city INT(11) NULL;
		```
	- In the property table, add the status column and thus leave the status_history table only for history consultation
		```sql
		ALTER TABLE `property` ADD status int(11) NULL;

		UPDATE property p
		INNER JOIN (
			SELECT property_id, status_id
			FROM (
				SELECT
				a.property_id, a.status_id,
				@r := (
					CASE
						WHEN a.property_id = @prev_property_id THEN @r + 1
						WHEN (@prev_property_id := a.property_id) = NULL THEN NULL
						ELSE 1
					END
				) AS row_number
				FROM (
					SELECT id, property_id, status_id
					FROM status_history
					ORDER BY property_id, id DESC
					LIMIT 18446744073709551615
				) a,
				(SELECT @r := 0, @prev_property_id := NULL) X
				ORDER BY a.property_id, a.id DESC
			) a
			WHERE a.row_number=1
		) property_last_status ON p.id=property_last_status.property_id
		INNER JOIN status s ON property_last_status.status_id=s.id
		SET p.status = s.id;
		```
	- In the auth_user table, the password column must be encrypted to comply with the standard
