# Real Estate Finder

***Idiomas***
- **🇪🇸 - Español**
- [🇺🇸 - English](./README.en.md)
---

Este proyecto busca crear un buscador de propiedades con el objetivo de proporcionar a los usuarios una herramienta eficiente y fácil de usar para encontrar propiedades que se ajusten a sus necesidades y preferencias.

Con este buscador, los usuarios podrán realizar búsquedas personalizadas basadas en diferentes criterios, como ubicación, tipo de propiedad, precio, tamaño, y más.

---


## Tecnologías Utilizadas
- **Python** será el lenguaje principal de programación para desarrollar los microservicios del backend. Además, utilizaré los siguientes paquetes y bibliotecas: `unittest` para escribir y ejecutar pruebas, `mysql-connector-python` para la conexión a la base de datos MySQL, `Pydantic` para la validación de datos y `Uvicorn` para el servidor web ASGI.
- **Docker** para facilitar la creación y despliegue de los microservicios en un entorno aislado.

---


## Enfoque de Desarrollo
En este proyecto, seguiré una metodología de Desarrollo Dirigido por Pruebas (TDD). Esto implica que comenzaré creando pruebas unitarias que cubran diferentes aspectos de los microservicios, desde la conexión a la base de datos hasta la respuesta esperada de los endpoints. Utilizaré PEP8 como guía de estilo de codificación para mantener un código limpio y legible.

Además, tendré en cuenta las condiciones y la información que no se debe mostrar en los endpoints, asegurándome de implementar los métodos correspondientes para manejar estos casos.

---


## API Endpoint

- **/real-estates**

	*Método* (GET)

	*Parámetros soportados* (Query string)

	|Parámetro|Tipo|Ejemplo|
	|---|---|---|
	|status|`str`|pre_venta|
	|city|`str`|bogota|
	|year|`int`|2000|

	```bash
	curl -i -X GET http://127.0.0.1:5000/real-estates?status=pre_venta\&city=bogota\&year=2000
	```

- **/real-estates/{id}/likes**

	*Método* (POST)

	```bash
	curl -i -X POST -H "Authorization: Basic dGVzdF91c2VyOnRlc3RwYXNzMTIz" http://127.0.0.1:5000/real-estates/1/likes
	```

---


## Como ejecutarlo
1. Configura las credenciales de la base de datos en el archivo `.env` en el directorio backend, guíate en el archivo [.env-sample](./backend/.env-sample) que se encuentra en el mismo directorio
2. Para ejecutar las pruebas unitarias, ejecute el siguiente comando
	```bash
	docker compose -f docker-compose.yml -f dockerfiles/compose/docker-compose.test.yml run --rm backend
	```
3. Para ejecutar el microservicio, ejecute el siguiente comando
	```bash
	docker compose -f docker-compose.yml -f dockerfiles/compose/docker-compose.local.yml up backend
	```

---


## Base de datos
- Se crea la tabla de `property_likes` para el manejo del me gusta de los usuarios, no creo una llave única del usuario con la propiedad para que el usuario le puede darle me gusta más de una vez

	![property_likes](property_likes.png "Modelo entidad relación")
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
	> Esta tabla fue creada para el endpoint `/real-estates/{id}/likes`

- Mejoras sugeridas a la base de datos:
	- En la tabla de property normalizar la columna city, year
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
	- En la tabla de property agregar columna status y asi dejar la tabla status_history solo para consulta del historial
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
	- En la tabla auth_user la columna password se debe encriptar para cumplir con la norma
