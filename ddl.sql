CREATE TABLE partners (
  id SERIAL PRIMARY KEY,
  partner_name TEXT NOT NULL
);
COMMENT ON COLUMN partners.id IS 'id партнёра';
COMMENT ON COLUMN partners.partner_name IS 'Человекочитаемое наименование партнёра';


-- таблица с валютами на текущий день; предполагаем, что курс валюты меняется каждый день, поэтому в operations мы пишем не только буквенный код валюты, но и её курс на момент транзакции
CREATE TABLE currencies (
    code INT PRIMARY KEY,
    currency_name TEXT NOT NULL,
    rur_exchange_rate DECIMAL NOT NULL
);
COMMENT ON COLUMN currencies.code IS 'Код валюты в соответствии с ISO 4217';
COMMENT ON COLUMN currencies.currency_name IS 'Буквенный код валюты';
COMMENT ON COLUMN currencies.rur_exchange_rate IS 'Обменный курс по отношению к RUR';
-- заполняем тестовую таблицу по валютам
INSERT INTO currencies (code, currency_name, rur_exchange_rate) VALUES (643, 'RUR', 1);
INSERT INTO currencies (code, currency_name, rur_exchange_rate) VALUES (840, 'USD', 58.24);
INSERT INTO currencies (code, currency_name, rur_exchange_rate) VALUES (978, 'EUR', 62.49);
INSERT INTO currencies (code, currency_name, rur_exchange_rate) VALUES (826, 'GBP', 71.46);


CREATE TABLE operations (
  id SERIAL PRIMARY KEY,
  op_val DECIMAL(10,2) NOT NULL,
  curr_code INT NOT NULL DEFAULT 643,
  rur_exc_rate DECIMAL NOT NULL DEFAULT 1,
  rur_amount DECIMAL(10,2) NOT NULL,
  partner_id INT NOT NULL REFERENCES partners (id),
  ts TIMESTAMP DEFAULT NOW()
);
CREATE INDEX op_pid_ts_ix ON operations (partner_id , ts DESC);
COMMENT ON COLUMN operations.id IS 'Уникальный идентификатор транзакции(операции)';
COMMENT ON COLUMN operations.op_val IS 'Сумма транзакции: +Х -> поступление, -Х -> списание.';
COMMENT ON COLUMN operations.curr_code IS 'Буквенный код валюты из currencies';
COMMENT ON COLUMN operations.rur_exc_rate IS 'Обменный курс по отношению к рублю на момент транзакции';
COMMENT ON COLUMN operations.rur_amount IS 'Рублёвый эквивалент транзакции';
COMMENT ON COLUMN operations.partner_id IS 'id партнёра, совершившего транзакцию из таблицы partners';
COMMENT ON COLUMN operations.ts IS 'Дата и время совершения транзакции. С таймзонами пока тоже не заморачиваемся.';

-- партиционируем таблицу по месяцам для более быстрого поиска данных по timestamp'ам
CREATE TABLE operations_2017_01 ( CHECK (ts >= DATE '2017-01-01' AND ts < DATE '2017-02-01') ) INHERITS (operations);
CREATE INDEX operations_2017_01_comp_idx ON operations_2017_01 (partner_id, ts DESC);
CREATE TABLE operations_2017_02 ( CHECK (ts >= DATE '2017-02-01' AND ts < DATE '2017-03-01') ) INHERITS (operations);
CREATE INDEX operations_2017_02_comp_idx ON operations_2017_02 (partner_id, ts DESC);
CREATE TABLE operations_2017_03 ( CHECK (ts >= DATE '2017-03-01' AND ts < DATE '2017-04-01') ) INHERITS (operations);
CREATE INDEX operations_2017_03_comp_idx ON operations_2017_03 (partner_id, ts DESC);
CREATE TABLE operations_2017_04 ( CHECK (ts >= DATE '2017-04-01' AND ts < DATE '2017-05-01') ) INHERITS (operations);
CREATE INDEX operations_2017_04_comp_idx ON operations_2017_04 (partner_id, ts DESC);
CREATE TABLE operations_2017_05 ( CHECK (ts >= DATE '2017-05-01' AND ts < DATE '2017-06-01') ) INHERITS (operations);
CREATE INDEX operations_2017_05_comp_idx ON operations_2017_05 (partner_id, ts DESC);
CREATE TABLE operations_2017_06 ( CHECK (ts >= DATE '2017-06-01' AND ts < DATE '2017-07-01') ) INHERITS (operations);
CREATE INDEX operations_2017_06_comp_idx ON operations_2017_06 (partner_id, ts DESC);
-- ...

-- заводим тестовых партнёров
INSERT INTO partners (partner_name) VALUES ('ivan');
INSERT INTO partners (partner_name) VALUES ('anton');
INSERT INTO partners (partner_name) VALUES ('maria');
INSERT INTO partners (partner_name) VALUES ('alex');
INSERT INTO partners (partner_name) VALUES ('gennady');
INSERT INTO partners (partner_name) VALUES ('denis');
