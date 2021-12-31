# Flask_Dashboard-OracleSummary
I developed this dashboard to provide a high-level summary of a large Oracle environment: the characteristics, stats, and growth trends of multiple Oracle databases and database servers 

DEMO can be viewed here: (coming soon)

Tools used: Python, SQL, html, css, Flask Web framework

Database Tables Used to Populate Dashboard:

The Oracle Dashboard pulls its data from five different database tables in an Oracle database  : oracle_databases, oracle_servers, asmsize_trend, oracle_datafiles and oracle_tablespaces. Each of these tables are automatically populated by the following scripts, and refreshed once an hour: 

[it-reaches-out.sh](https://github.com/bculler17/Oracle_Bash_Scripts/blob/main/scripts/availability_monitor/it_reaches_out.sh)

                                        
[tablespace_growth_trender.sh](https://github.com/bculler17/Oracle_Bash_Scripts/blob/main/scripts/tablespace_growth_trender.sh)

					
How To Add New Servers to the Dashboard:

1. Insert the new database server information into the oracle_servers database table using the following syntax:

Note: status = 'ACTIVE'

If status does not = 'ACTIVE', it will not appear on the dashboard.


SQL> insert into oracle_servers (id, ipaddress, hostname, status, record_creator) VALUES (oracle_servers_id_seq.nextval, '<INSERT IP ADDRESS>', '<INSERT HOSTNAME>', 'ACTIVE', '<INSERT First_name Last_inital>');

EXAMPLE:

SQL> insert into oracle_servers (id, ipaddress, hostname, status, record_creator) VALUES (oracle_servers_id_seq.nextval, '0.0.0.0', 'bethscomputer', 'ACTIVE', 'Beth C.');

SQL> commit;

The new server will now be visible on the Oracle dashboard 

Some of the information may be missing, but what is missing on the homepage will be automatically populated the next time the bash script: it-reaches-out.sh executes.


How To Add New Databases to the Dashboard:
  
To add a new Oracle database to the dashboard, simply do the following:


1. Insert the new database information into oracle_databases database table using the following syntax:

Note: status = 'ACTIVE'

If status does not = 'ACTIVE', it will not appear on the dashboard.

2-NODE RAC:


insert into oracle_databases (id, name, node1, node2, status, application_name, record_creator) VALUES (oracle_databases_id_seq.nextval,'<INSERT DB NAME>', '<INSERT 1st node's hostname>', '<INSERT 2nd node's hostname>', 'ACTIVE', '<INSERT APPLICATION NAME THAT WILL BE USING THIS DATABASE*>', '<INSERT First_name Last_inital>';

SQL> commit;

1-NODE RAC or standalone:


insert into oracle_databases (id, name, node1, status, application_name, record_creator) VALUES (oracle_databases_id_seq.nextval,'<INSERT DB NAME>', '<INSERT NODE'S HOSTNAME>', 'ACTIVE', '<INSERT APPLICATION NAME THAT WILL BE USING THIS DATABASE*>', '<INSERT First_name Last_inital>';

SQL> commit;


The new database will now be visible on the Oracle dashboard 

Some of the information may be missing, but everything on the homepage that is missing will be automatically populated the next time the bash scripts: it-reaches-out.sh and tablespace_growth_trender.sh execute.

The Diskgroup information is automatically populated by a script that is not my own, so it is not listed here.


How to Remove a Server or Database from the Dashboard
To remove a server or database from the dashboard, simply set status='INACTIVE':

To Remove a Server:

EXAMPLE:


SQL> udpate oracle_servers set status='INACTIVE', record_updated_by='Beth C.', record_updated=sysdate where hostname='<SERVER HOSTNAME TO REMOVE>';

To Remove a Database:

EXAMPLE:


SQL> udpate oracle_databases set status='INACTIVE', record_updated_by='Beth C.', record_updated=sysdate where name='<DB NAME TO REMOVE>';



