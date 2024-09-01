# ELT-Project
This repository contains a custom Extract, Load, Transform (ELT) project that utilizes Docker and PostgreSQL to demonstrate a simple ELT process.


configuration for dbt 
~/.dbt/profiles.yml 


  1 dbt_project:
  2   outputs:
  3     dev:
  4       dbname: destination_db
  5       host: host.docker.internal
  6       pass: postgres
  7       port: 5434
  8       schema: public
  9       threads: 1
 10       type: postgres
 11       user: postgres
 12   target: dev
~                                                                                                                                                                                  
~                                                                                                                                                                                  
~                   