-- id data hora credito debito saldo descricao 

CREATE TABLE IF NOT EXISTS `dashgastos`.`registos` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `data` TEXT NOT NULL,
    `hora` TEXT NOT NULL,
    `credito` FLOAT NULL DEFAULT '0.0',
    `debito` FLOAT NULL DEFAULT '0.0',
    `saldo` FLOAT NULL DEFAULT '0.0',
    `descricao` TEXT NOT NULL,
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;
