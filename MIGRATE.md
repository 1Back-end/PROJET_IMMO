<!-- -- Adminer 4.8.1 PostgreSQL 16.2 (Debian 16.2-1.pgdg120+2) dump

DROP TABLE IF EXISTS "alembic_version";
CREATE TABLE "public"."alembic_version" (
    "version_num" character varying(32) NOT NULL,
    CONSTRAINT "alembic_version_pkc" PRIMARY KEY ("version_num")
) WITH (oids = false);

INSERT INTO "alembic_version" ("version_num") VALUES
('d4fc87b919b8');

DROP TABLE IF EXISTS "roles";
CREATE TABLE "public"."roles" (
    "uuid" character varying(255) NOT NULL,
    "title_fr" character varying(50),
    "title_en" character varying(50),
    "code" character varying(30) NOT NULL,
    "date_added" timestamp DEFAULT now(),
    "date_modified" timestamp DEFAULT now(),
    CONSTRAINT "roles_code_key" UNIQUE ("code"),
    CONSTRAINT "roles_pkey" PRIMARY KEY ("uuid"),
    CONSTRAINT "roles_title_en_key" UNIQUE ("title_en"),
    CONSTRAINT "roles_title_fr_key" UNIQUE ("title_fr"),
    CONSTRAINT "roles_uuid_key" UNIQUE ("uuid")
) WITH (oids = false);

INSERT INTO "roles" ("uuid", "title_fr", "title_en", "code", "date_added", "date_modified") VALUES
('7e1ba19d-5325-4a72-b511-b63a5b0f3486','Directeur Général','Directeur Général','dg','2024-03-08 09:23:45.403214','2024-03-08 09:23:45.403214'),
('a6403aba-a383-49e5-a5d5-136d0c64b007','Directeur Technique','Directeur Technique','cto','2024-03-08 09:23:45.412982','2024-03-08 09:23:45.412982'),
('6aec287c-de35-4c09-9a13-1f6d7554b16d','Développeur Logiciel','Software Developer','dev','2024-03-08 09:23:45.416822','2024-03-08 09:23:45.416822'),
('f3d3d26a-b513-4473-bbff-ba04a70b6ca0','Designer','Designer','ui/ux','2024-03-08 09:23:45.422727','2024-03-08 09:23:45.422727'),
('fd03fe03-d7aa-44d1-8ca4-b8d615aab8dd','Testeur QA','QA Tester','qa','2024-03-08 09:23:45.426897','2024-03-08 09:23:45.426897'),
('f444660b-a2df-420c-89d6-ccfa2a0f3f98','Stagiaire','Intern','sta','2024-03-08 09:23:45.430407','2024-03-08 09:23:45.430407'),
('88845d35-2701-4499-b92d-48cccb296017','Développeur Backend','Backend developer','backend','2024-03-15 16:08:44.047288','2024-03-15 16:08:44.047288'),
('4511dfa4-3aa5-4e91-a920-0e614672bb6f','Développeur Frontend','Frontend developer','frontend','2024-03-15 16:08:44.054919','2024-03-15 16:08:44.054919'),
('bdbfbfe3-11db-4a86-9e61-547b49541eee','Développeur Mobile','Mobile developer','mobile','2024-03-15 16:08:44.05882','2024-03-15 16:08:44.05882');

DROP TABLE IF EXISTS "sanction_categories";
CREATE TABLE "public"."sanction_categories" (
    "uuid" character varying(255) NOT NULL,
    "name" character varying(255) NOT NULL,
    "amount" double precision NOT NULL,
    "description" text NOT NULL,
    "date_added" timestamp DEFAULT now(),
    "date_modified" timestamp DEFAULT now(),
    CONSTRAINT "sanction_categories_name_key" UNIQUE ("name"),
    CONSTRAINT "sanction_categories_pkey" PRIMARY KEY ("uuid"),
    CONSTRAINT "sanction_categories_uuid_key" UNIQUE ("uuid")
) WITH (oids = false);

INSERT INTO "sanction_categories" ("uuid", "name", "amount", "description", "date_added", "date_modified") VALUES
('0069694e-1fe8-467c-a6be-a03fd414ef7b','Retard',500,'Le retard  est compte pour 30 minutes apres 8h30 min.','2024-03-08 09:44:52.053026','2024-03-08 09:44:52.053026'),
('1a56dfc8-4e51-4678-9ce6-ebd4cfb8a66d','Tache non livrees a temps',1000,'les taches sont attribuees avec des delais,passe,ce delais, il s''agit d''une tache en retard et par consequent non livree a temps.','2024-03-08 09:44:52.060527','2024-03-08 09:44:52.060527'),
('1958b728-3807-4acc-bddb-9d47e0f0bcf8','Bugs',800,'une fonctionnalite qui a ete livree et qui ne fonctionne pas come il fallait.','2024-03-08 09:44:52.065007','2024-03-08 09:44:52.065007'),
('cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','films,séries,animés ou YouTube pendant le travail.',2000,'Pendant le travail, il est proscrit de visionner des contenus qui ne concernent pas le travail.','2024-03-08 09:44:52.069722','2024-03-08 09:44:52.069722'),
('4511aef1-1239-47d0-bcb0-8b8f7979e798','insubordination.',2000,'le non respect de l''autorite etc......','2024-03-15 16:23:07.316136','2024-03-15 16:23:07.316136');

DROP TABLE IF EXISTS "sanctions";
CREATE TABLE "public"."sanctions" (
    "uuid" character varying(255) NOT NULL,
    "quantity" integer,
    "sanctioned_user_uuid" character varying NOT NULL,
    "sanction_category_uuid" character varying,
    "sanctioner_uuid" character varying,
    "amount" double precision NOT NULL,
    "description" character varying NOT NULL,
    "status" character varying NOT NULL,
    "sanction_date_added" timestamp DEFAULT now(),
    "date_added" timestamp DEFAULT now(),
    "date_modified" timestamp DEFAULT now(),
    CONSTRAINT "sanctions_pkey" PRIMARY KEY ("uuid"),
    CONSTRAINT "sanctions_uuid_key" UNIQUE ("uuid")
) WITH (oids = false);

INSERT INTO "sanctions" ("uuid", "quantity", "sanctioned_user_uuid", "sanction_category_uuid", "sanctioner_uuid", "amount", "description", "status", "sanction_date_added", "date_added", "date_modified") VALUES
('acd80b70-706f-4f25-be6d-b8fd0792d11b',1,'b7aa5aa4-34ab-437f-a90b-910f21e5fcac','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-05 00:00:00','2024-03-24 13:37:56.751209','2024-03-24 13:37:56.751209'),
('e4dedd1b-2872-43ca-a0f7-d0205cd11887',1,'b7aa5aa4-34ab-437f-a90b-910f21e5fcac','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-12 00:00:00','2024-03-24 13:37:56.763168','2024-03-24 13:37:56.763168'),
('ca4f3792-0d67-4bfd-9272-39a5b083332d',3,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1500,'','PENDING','2024-03-08 00:00:00','2024-03-24 13:37:56.771279','2024-03-24 13:37:56.771279'),
('be219888-622e-4876-ab06-0e394cdd4f7a',1,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',2000,'','PENDING','2024-03-05 00:00:00','2024-03-24 13:37:56.776241','2024-03-24 13:37:56.776241'),
('5c482d2b-32f2-40d0-a9c0-f93f4c1cfa95',1,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-29 00:00:00','2024-03-24 13:37:56.781344','2024-03-24 13:37:56.781344'),
('9bbc889d-db13-40f5-9944-020fdc0ad924',1,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-27 00:00:00','2024-03-24 13:37:56.786533','2024-03-24 13:37:56.786533'),
('2ddd6878-a91a-4dca-b19f-cea5cf7b790b',2,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-03-11 00:00:00','2024-03-24 13:37:56.791277','2024-03-24 13:37:56.791277'),
('e5ac95f4-039a-4b5d-8bbd-af779503af50',1,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-12 00:00:00','2024-03-24 13:37:56.795601','2024-03-24 13:37:56.795601'),
('51624b29-37e0-4f82-a67b-4560470a1b83',17,'6a6e0c00-0f79-4f71-b9c4-e443e214210e','1a56dfc8-4e51-4678-9ce6-ebd4cfb8a66d','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',17000,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.800961','2024-03-24 13:37:56.800961'),
('f7187ce1-6abe-4075-90d8-fcdaaddbebc0',1,'c3b0eb11-ef89-4a40-948b-ce10f4692ee5','1a56dfc8-4e51-4678-9ce6-ebd4cfb8a66d','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-03-07 00:00:00','2024-03-24 13:37:56.806048','2024-03-24 13:37:56.806048'),
('208778c4-344f-40bd-a2b0-f05913990544',1,'c3b0eb11-ef89-4a40-948b-ce10f4692ee5','1958b728-3807-4acc-bddb-9d47e0f0bcf8','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',800,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.810687','2024-03-24 13:37:56.810687'),
('4c76dc14-2225-45ad-96e9-148dba3179b5',1,'3e7aa514-329f-46e7-ab0e-223eabec1ee6','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-07 00:00:00','2024-03-24 13:37:56.815404','2024-03-24 13:37:56.815404'),
('0f8b5616-dfe6-46a7-875f-c33e90e55b8c',2,'3e7aa514-329f-46e7-ab0e-223eabec1ee6','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.820554','2024-03-24 13:37:56.820554'),
('ad7de0e5-8428-4f49-821c-2a0b76654422',1,'c0f34605-92d8-4cf1-938b-b3eaeb6eb79c','1958b728-3807-4acc-bddb-9d47e0f0bcf8','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',800,'','PENDING','2024-03-07 00:00:00','2024-03-24 13:37:56.825073','2024-03-24 13:37:56.825073'),
('2aa71b7b-6b0d-4e23-ae7f-9b08c1b04460',1,'c0f34605-92d8-4cf1-938b-b3eaeb6eb79c','4511aef1-1239-47d0-bcb0-8b8f7979e798','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',2000,'','PENDING','2024-03-12 00:00:00','2024-03-24 13:37:56.829726','2024-03-24 13:37:56.829726'),
('08859964-1f65-4899-8962-803505f40e38',1,'c5a7b921-0fb9-45bb-be97-ebe11d0b63e3','1958b728-3807-4acc-bddb-9d47e0f0bcf8','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',800,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.834594','2024-03-24 13:37:56.834594'),
('2f21b12f-4b99-4986-81f9-d1a52914a9e2',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-07 00:00:00','2024-03-24 13:37:56.839539','2024-03-24 13:37:56.839539'),
('fb9e49e3-1f7c-44fd-b773-6b08433c489f',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-08 00:00:00','2024-03-24 13:37:56.844262','2024-03-24 13:37:56.844262'),
('62f239d2-937f-4a8a-8bf5-54f43beb7b62',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-13 00:00:00','2024-03-24 13:37:56.848765','2024-03-24 13:37:56.848765'),
('1575e830-4003-4947-8c13-2a1df04dad11',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-19 00:00:00','2024-03-24 13:37:56.853856','2024-03-24 13:37:56.853856'),
('e61d050d-5e15-4816-aae9-2b48790f3ce4',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',2000,'','PENDING','2024-03-08 00:00:00','2024-03-24 13:37:56.858334','2024-03-24 13:37:56.858334'),
('26312f9f-803b-4808-b400-1917a50017ec',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',2000,'','PENDING','2024-02-23 00:00:00','2024-03-24 13:37:56.862678','2024-03-24 13:37:56.862678'),
('43f73c7c-e680-4c54-bdee-b7e574ffeb3f',4,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',8000,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.867813','2024-03-24 13:37:56.867813'),
('2bcc6f40-5433-4c9b-bb07-4a9c630e97a3',2,'f09d251e-9713-471e-a5c8-973d9fd96c21','cb5d1a1b-85e4-46a6-98b2-52aa42f1351e','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',4000,'','PENDING','2024-03-07 00:00:00','2024-03-24 13:37:56.873138','2024-03-24 13:37:56.873138'),
('69d7d93e-2a68-43b3-8e3d-350eb28c43ca',1,'38fb9069-be3a-4f1d-b40e-1fccd0769af0','1958b728-3807-4acc-bddb-9d47e0f0bcf8','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',800,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.877787','2024-03-24 13:37:56.877787'),
('8c763742-7f8c-4b4d-9f7c-6b88d83ec941',1,'09c8725f-ac00-4823-913e-a0554e3521f9','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-08 00:00:00','2024-03-24 13:37:56.883109','2024-03-24 13:37:56.883109'),
('47e38947-194f-4313-909e-d1047bd7239b',1,'09c8725f-ac00-4823-913e-a0554e3521f9','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-19 00:00:00','2024-03-24 13:37:56.887775','2024-03-24 13:37:56.887775'),
('e1c8e8f2-e988-4be1-a40e-3bed9f218915',1,'09c8725f-ac00-4823-913e-a0554e3521f9','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-19 00:00:00','2024-03-24 13:37:56.892175','2024-03-24 13:37:56.892175'),
('f2702633-d05f-40b1-b6a5-1f7bd9fc882a',1,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-08 00:00:00','2024-03-24 13:37:56.896593','2024-03-24 13:37:56.896593'),
('effd532b-c378-4b87-b262-c880043878c3',2,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-03-05 00:00:00','2024-03-24 13:37:56.901534','2024-03-24 13:37:56.901534'),
('47a9cd9e-e7de-422f-8d75-b5975dc8d823',1,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-03-19 00:00:00','2024-03-24 13:37:56.906182','2024-03-24 13:37:56.906182'),
('f52dae64-d5a4-4610-89bb-72575d1daa94',3,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1500,'','PENDING','2024-03-12 00:00:00','2024-03-24 13:37:56.910684','2024-03-24 13:37:56.910684'),
('8c07644f-5735-4d46-aa52-379e5983b017',3,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1500,'','PENDING','2024-02-29 00:00:00','2024-03-24 13:37:56.915448','2024-03-24 13:37:56.915448'),
('73434c99-5ad2-44ca-b119-852e045256b0',2,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-03-14 00:00:00','2024-03-24 13:37:56.92135','2024-03-24 13:37:56.92135'),
('19d82bca-e688-4c9c-a575-4d03d812314e',2,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-02-27 00:00:00','2024-03-24 13:37:56.925714','2024-03-24 13:37:56.925714'),
('d30077eb-b197-42d3-893f-0d53f13350f4',2,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',1000,'','PENDING','2024-02-13 00:00:00','2024-03-24 13:37:56.930426','2024-03-24 13:37:56.930426'),
('b95db7bb-02a5-46e4-96a2-8f5f3156cf53',1,'65f5afdc-a13d-45c2-8763-b425d7f7c6bc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-22 00:00:00','2024-03-24 13:37:56.936066','2024-03-24 13:37:56.936066'),
('fe1955d2-2b07-4d39-a094-8f3b0d2a7d8a',1,'c3b0eb11-ef89-4a40-948b-ce10f4692ee5','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-22 00:00:00','2024-03-24 13:37:56.941751','2024-03-24 13:37:56.941751'),
('d18abfb7-e8dd-49fc-88f7-30acf53fa129',1,'d9899003-f752-4647-a99d-19c00e682360','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-07 00:00:00','2024-03-24 13:37:56.946558','2024-03-24 13:37:56.946558'),
('aadb6d24-a93d-4ea9-9e00-0841dfb148a2',1,'f09d251e-9713-471e-a5c8-973d9fd96c21','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-26 00:00:00','2024-03-24 13:37:56.951899','2024-03-24 13:37:56.951899'),
('278b1ec7-2853-4eba-a82a-52bb6d51d920',1,'f09d251e-9713-471e-a5c8-973d9fd96c21','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-19 00:00:00','2024-03-24 13:37:56.956458','2024-03-24 13:37:56.956458'),
('f4490567-4990-4a4b-97fe-ee5f17cb0218',1,'f09d251e-9713-471e-a5c8-973d9fd96c21','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-19 00:00:00','2024-03-24 13:37:56.960464','2024-03-24 13:37:56.960464'),
('a7a61889-8d0e-4af6-bd66-ab3db74fd152',1,'c069a012-16b2-47a0-a324-77b0643ed2dc','0069694e-1fe8-467c-a6be-a03fd414ef7b','c5a7b921-0fb9-45bb-be97-ebe11d0b63e3',500,'','PENDING','2024-02-19 00:00:00','2024-03-24 13:37:56.965082','2024-03-24 13:37:56.965082');

DROP TABLE IF EXISTS "users";
CREATE TABLE "public"."users" (
    "uuid" character varying(255) NOT NULL,
    "email" character varying(255),
    "first_name" character varying(100),
    "last_name" character varying(100),
    "phone_number" character varying(100),
    "birthday" date NOT NULL,
    "gender" character varying NOT NULL,
    "role_uuid" character varying(255) NOT NULL,
    "status" character varying(30) NOT NULL,
    "hashed_password" character varying(255) NOT NULL,
    "date_added" timestamp DEFAULT now(),
    "date_modified" timestamp DEFAULT now(),
    CONSTRAINT "users_pkey" PRIMARY KEY ("uuid"),
    CONSTRAINT "users_uuid_key" UNIQUE ("uuid")
) WITH (oids = false);

CREATE INDEX "ix_users_birthday" ON "public"."users" USING btree ("birthday");

CREATE INDEX "ix_users_email" ON "public"."users" USING btree ("email");

CREATE INDEX "ix_users_first_name" ON "public"."users" USING btree ("first_name");

CREATE INDEX "ix_users_gender" ON "public"."users" USING btree ("gender");

CREATE INDEX "ix_users_last_name" ON "public"."users" USING btree ("last_name");

CREATE INDEX "ix_users_phone_number" ON "public"."users" USING btree ("phone_number");

INSERT INTO "users" ("uuid", "email", "first_name", "last_name", "phone_number", "birthday", "gender", "role_uuid", "status", "hashed_password", "date_added", "date_modified") VALUES
('54c6269c-574c-42cf-8ab4-e11433a2139d','kevin.wamba@kevmax.com','Kevin','Wamba Zoko','12345678','2024-03-07','M','7e1ba19d-5325-4a72-b511-b63a5b0f3486','ACTIVED','$2b$12$xOqblmx2309Q3BhKdffXGetArgEMb6NlB86IkJK4iSFVVDlPMSYs.','2024-03-15 16:07:49.439252','2024-03-15 16:07:49.439252'),
('d9899003-f752-4647-a99d-19c00e682360','leducnikos@gmail.com','Joel-Steve','Nikenoueba','12345678','2024-03-07','M','a6403aba-a383-49e5-a5d5-136d0c64b007','ACTIVED','$2b$12$xzQvBqsR26TscHW1o12xcerlDDtiYSy7xeSzCYQMap3dAl7gMgkfe','2024-03-15 16:07:49.791757','2024-03-15 16:07:49.791757'),
('c3b0eb11-ef89-4a40-948b-ce10f4692ee5','liditieng@gmail.com','Lidvine','Tientchieu','12345678','2024-03-07','F','88845d35-2701-4499-b92d-48cccb296017','ACTIVED','$2b$12$Drj/FJQWm8stWaJ2wh3EMeMcbS/afsRll/IV3F4RMRqR.DS1xB2OC','2024-03-15 16:10:19.415255','2024-03-15 16:10:19.415255'),
('c069a012-16b2-47a0-a324-77b0643ed2dc','ngassijordane2@gmail.com','Jordan','Ngassi','697877354','2024-03-07','M','f444660b-a2df-420c-89d6-ccfa2a0f3f98','ACTIVED','$2b$12$HRMMyiTLSbMKlqMn.0spruaPLwsFPuVg37jXCXvkZlzuHAmPZxbEC','2024-03-15 16:10:19.728999','2024-03-15 16:10:19.728999'),
('f09d251e-9713-471e-a5c8-973d9fd96c21','djantchengamo@gmail.com','David','Ngamo','12345678','2024-03-07','M','4511dfa4-3aa5-4e91-a920-0e614672bb6f','ACTIVED','$2b$12$YKhlnEmRpsl.9zMkVLX2peHAkrPcmz97jqBPO9m4ldJI2V7lrzZG2','2024-03-15 16:10:20.050648','2024-03-15 16:10:20.050648'),
('38fb9069-be3a-4f1d-b40e-1fccd0769af0','sonfacknelsonmandela@gmail.com','Nelson','Sonfack Mandela','12345678','2024-03-07','M','4511dfa4-3aa5-4e91-a920-0e614672bb6f','ACTIVED','$2b$12$RQuLkf3KfoptY17MzuRhGuXBAEDZL74pUGS6WsRo1sUVinHKwPr8y','2024-03-15 16:10:20.384705','2024-03-15 16:10:20.384705'),
('6a6e0c00-0f79-4f71-b9c4-e443e214210e','ndazoomessanga@gmail.com','Messanga Ndazo''o','Paul Yvan','12345678','2024-03-07','M','4511dfa4-3aa5-4e91-a920-0e614672bb6f','ACTIVED','$2b$12$ys.gAAcY7HQOh37rhYroB.bRMYgfS2U8DMKXPT2Pxl1Fd1TUUJUYe','2024-03-15 16:10:20.717343','2024-03-15 16:10:20.717343'),
('b7aa5aa4-34ab-437f-a90b-910f21e5fcac','mvondofernando7777@gmail.com','Tanga Mvondo','Severin Fernando','698288916','2000-11-20','M','88845d35-2701-4499-b92d-48cccb296017','ACTIVED','$2b$12$qDNZ8ybJHeLj0i6alUvoN.b4We8pkjEGJtPieR36twO3a71NeYXC.','2024-03-15 16:10:21.027796','2024-03-15 16:10:21.027796'),
('c0f34605-92d8-4cf1-938b-b3eaeb6eb79c','ramsesndame34@gmail.com','Ramses','Ndame','12345678','2024-03-07','M','4511dfa4-3aa5-4e91-a920-0e614672bb6f','ACTIVED','$2b$12$zIfZ0c28AkkP10yJGqIZT.IJ0RBM.dPAvoZF/ZSfiKUiyfGy2N6sa','2024-03-15 16:13:45.571177','2024-03-15 16:13:45.571177'),
('09c8725f-ac00-4823-913e-a0554e3521f9','stephanekamlo23@gmail.com','Stephane','mk','12345678','2024-03-07','M','bdbfbfe3-11db-4a86-9e61-547b49541eee','ACTIVED','$2b$12$wc4BTPQu4hGYSde07WkpjOP6ZBNowm9O5TIHu5A..YeVSWko7pRsG','2024-03-15 16:10:19.097843','2024-03-15 16:10:19.097843'),
('65f5afdc-a13d-45c2-8763-b425d7f7c6bc','nelsonkouogang@gmail.com','Nelson','Le Grand','12345678','2024-03-07','M','f444660b-a2df-420c-89d6-ccfa2a0f3f98','ACTIVED','$2b$12$j6IgVaqmRJQva2Am4lnAU.QUPJ/wCpjLdxnGPm2Ros0WRS6oQ9Ije','2024-03-15 16:58:03.146857','2024-03-15 16:58:03.146857'),
('c5a7b921-0fb9-45bb-be97-ebe11d0b63e3','signingvardo@gmail.com','Vardo','signing','12345678','2024-03-07','M','4511dfa4-3aa5-4e91-a920-0e614672bb6f','ACTIVED','$2b$12$EGuXRYUySke6cIm4xsZQ3OaRifatKhjTTixQqeAntYeenqJzIZK7u','2024-03-15 16:58:03.469026','2024-03-15 16:58:03.469026'),
('3e7aa514-329f-46e7-ab0e-223eabec1ee6','geo575mbeussi@gmail.com','Geovane','Mbeussi','12345678','2024-03-07','M','bdbfbfe3-11db-4a86-9e61-547b49541eee','ACTIVED','$2b$12$szmDT4gODs8.eQFrL9LAeO8yIGbjKL0I1kTmEiukNdkeNzuAaR1I.','2024-03-18 07:50:14.679846','2024-03-18 07:50:14.679846');

ALTER TABLE ONLY "public"."sanctions" ADD CONSTRAINT "sanctions_sanction_category_uuid_fkey" FOREIGN KEY (sanction_category_uuid) REFERENCES sanction_categories(uuid) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."sanctions" ADD CONSTRAINT "sanctions_sanctioned_user_uuid_fkey" FOREIGN KEY (sanctioned_user_uuid) REFERENCES users(uuid) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;
ALTER TABLE ONLY "public"."sanctions" ADD CONSTRAINT "sanctions_sanctioner_uuid_fkey" FOREIGN KEY (sanctioner_uuid) REFERENCES users(uuid) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;

ALTER TABLE ONLY "public"."users" ADD CONSTRAINT "users_role_uuid_fkey" FOREIGN KEY (role_uuid) REFERENCES roles(uuid) ON UPDATE CASCADE ON DELETE CASCADE NOT DEFERRABLE;

-- 2024-03-24 14:33:21.209712+00 -->