-- id data hora credito debito saldo descricao 
CREATE TABLE IF NOT EXISTS `dashgastos`.`registos` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `data` TEXT NOT NULL,
    `valor` FLOAT NOT NULL DEFAULT '0.0',
    `tipo` FLOAT NOT NULL DEFAULT '0.0',
    `descricao` TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (`id`)
) ENGINE = InnoDB;

-- get saldo
SELECT ROUND(ABS(SUM(CASE WHEN tipo = 1 THEN valor ELSE 0 END) - SUM(CASE WHEN tipo = 2 THEN valor ELSE 0 END)), 2) AS saldo FROM registos;

-- alter AUTO_INCREMENT of id
ALTER TABLE `registos`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;
COMMIT;