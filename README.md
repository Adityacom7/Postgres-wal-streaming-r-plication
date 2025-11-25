 aditya468-dev -- psql -U postgres -d postgres -c "SELECT * FROM replication_
test;"
adi@Adityas-MacBook-Pro TestApp % oc exec postgres-master-6db6584b9d-qg8nn -n a
ditya468-dev -- psql -U postgres -d postgres -c "SELECT * FROM replication_test
;"
 id |    data     |         created_at         
----+-------------+----------------------------
  1 | Test data 1 | 2025-11-25 06:34:28.443567
  2 | Test data 2 | 2025-11-25 06:34:28.443567
  3 | Test data 3 | 2025-11-25 06:34:28.443567
(3 rows)

adi@Adityas-MacBook-Pro TestApp % oc exec postgres-slave-6d5d8745c4-8c556 -n ad
itya468-dev -- psql -U postgres -d postgres -c "SELECT * FROM replication_test;
"
Defaulted container "postgres-slave" out of: postgres-slave, fix-permissions (init)
 id |    data     |         created_at         
----+-------------+----------------------------
  1 | Test data 1 | 2025-11-25 06:34:28.443567
  2 | Test data 2 | 2025-11-25 06:34:28.443567
  3 | Test data 3 | 2025-11-25 06:34:28.443567
(3 rows)

adi@Adityas-MacBook-Pro TestApp % oc exec postgres-master-6db6584b9d-qg8nn -n a
ditya468-dev -- psql -U postgres -d postgres -c "SELECT usename, application_na
me, state, sync_state FROM pg_stat_replication;"
  usename   | application_name |   state   | sync_state 
------------+------------------+-----------+------------
 replicator | walreceiver      | streaming | async
(1 row)

adi@Adityas-MacBook-Pro TestApp % 
adi@Adityas-MacBook-Pro TestApp % 
adi@Adityas-MacBook-Pro TestApp % 
adi@Adityas-MacBook-Pro TestApp % 
adi@Adityas-MacBook-Pro TestApp % ls
postgres-replication-test
adi@Adityas-MacBook-Pro TestApp % cd postgres-replication-test 

