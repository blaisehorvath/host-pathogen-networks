DROP TABLE IF EXISTS "uniprot";
DROP TABLE IF EXISTS `foreign_ids`;

CREATE TABLE "uniprot" (
	`id`	INTEGER PRIMARY KEY,
	`accession`	TEXT NOT NULL,
	`is_primary`	INTEGER,
	`length`	INTEGER,
	`is_swissprot`	INTEGER NOT NULL,
	`primary_id` INTEGER,
	`tax_id` INTEGER NOT NULL,
	FOREIGN KEY (`primary_id`) REFERENCES uniprot ( `id` ) ON UPDATE NO ACTION ON DELETE CASCADE
);
CREATE TABLE `foreign_ids` (
	`id`	INTEGER PRIMARY KEY,
	`uniprot_id` INTEGER NOT NULL,
	`accession`	TEXT NOT NULL,
	`type`	TEXT,
	FOREIGN KEY(`uniprot_id`) REFERENCES uniprot ( `id` ) ON UPDATE NO ACTION ON DELETE CASCADE
);