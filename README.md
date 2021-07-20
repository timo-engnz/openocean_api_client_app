# Initialization
    - Get the APIKEY, CLIENTID and ACCESSKEY from portal.openocean.co.ke
    - copy .env.example to .env
    - copy config.yml.example to config.example
    - Replace the credentials and mysql config
    - install python packages
    
# To Start
- Docker
```.env
docker-compose up -d --build multiprocessor
```
- Run on your python environment
```
pip install -r requirements.txt
RUN pip install omit_helpers --extra-index-url https://__token__:LRxH2wewi7UxyzEt6U7m@gitlab.com/api/v4/projects/24065691/packages/pypi/simple

```
# To Run all applications,
   ```.env
python3 multiprocessor.py
```

# To Run Single,
   ```.env
python3 flaskApp.py
python3 va_transaction_worker.py

ngrok http 5000 #To publicly set the callbackurl
```


# Table: 
```.env
-- va_transactions definition

CREATE TABLE `va_transactions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `trx_type` enum('AIRTIME','KPLC_TOKENS') NOT NULL,
  `msisdn` varchar(20) NOT NULL,
  `member_id` varchar(20) NOT NULL,
  `account_no` varchar(20) NOT NULL,
  `amount` double NOT NULL,
  `status` int DEFAULT '0',
  `request` text,
  `retry_count` int DEFAULT '0',
  `response` json DEFAULT NULL,
  `response_id` varchar(100) DEFAULT NULL,
  `idepodency_key` int DEFAULT '0',
  `callback_data` json DEFAULT NULL,
  `processDate` datetime DEFAULT NULL,
  `date_created` datetime DEFAULT CURRENT_TIMESTAMP,
  `date_updated` datetime DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `va_transactions_msisdn_IDX` (`msisdn`) USING BTREE,
  KEY `va_transactions_status_IDX` (`status`) USING BTREE,
  KEY `va_transactions_trx_type_IDX` (`trx_type`) USING BTREE,
  KEY `va_transactions_response_id_IDX` (`response_id`) USING BTREE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
```

# To add  Record:
```.env

#
    INSERT INTO va_transactions (trx_type,msisdn,member_id,account_no,amount)
        VALUES ('AIRTIME','254705126329','10','254705126329',10.0);
    
    INSERT INTO va_transactions (trx_type,msisdn,member_id,account_no,amount)
        VALUES ('KPLC_TOKENS','254705126329','10','54602512110',50.0);



```

# When to after recon
- When column `idepodency_key' is updated to '1', means the callback is success.