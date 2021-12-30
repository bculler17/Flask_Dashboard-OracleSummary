import os
import cx_Oracle
from datetime import datetime
from flask import *
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='*******'
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass


    @app.route('/Oracle')
    def environment_overview(): 
        con = cx_Oracle.connect('<username/password>')
        cursor = con.cursor()
        cursor.execute("select ipaddress, hostname, os_version, online_status, up_time from oracle_servers where status in ('ACTIVE', 'HMA') order by hostname")
        data = cursor.fetchall()
        cursor.execute("select application_name, name, node1, node2, version, online_status, dbtype, up_time1, up_time2, current_size from oracle_databases where status in ('ACTIVE', 'HMA') order by application_name, name")
        dbdata = cursor.fetchall()
        cursor.execute("select to_char(max(RECORD_UPDATED), 'Mon ddth, yyyy HH24:MI:SS') from oracle_servers where status in ('ACTIVE', 'HMA')")
        rfdate = cursor.fetchone()
        if cursor:
            cursor.close()
        if con:
            con.close()
        return render_template('base.html', data=data, data2=dbdata, data3=rfdate)

    @app.route('/Oracle/please_wait/<string:dbname>')
    def please_wait(dbname):
            return render_template('please-wait.html', dbname=dbname)

    @app.route('/Oracle/database-overview/<string:dbname>')
    def get_db_info(dbname):
        dbname = dbname
        con = cx_Oracle.connect('<username/password>')
        cursor = con.cursor()
        cursor.execute("with tme as (select max(event_date) MX, (max(event_date) - 1/24) SMX from oracle_tablespaces where UPPER(database_name)=UPPER('" + dbname + "')) SELECT distinct to_char(MX, 'Mon ddth, yyyy HH24:MI:SS'), tablespace_name, to_char(total_allocated_size, '999,999,999.99'), to_char(total_used_size, '999,999,999.99'),percent_used from oracle_tablespaces, tme where UPPER(database_name)=UPPER('" + dbname + "') and event_date between SMX and MX order by 5 desc")
        tbdata = cursor.fetchall()
        cursor.execute("with tme as (select max(event_date) MX, (max(event_date) - 0.5/24) SMX from asmsize_trend where UPPER(dg_dbname)=UPPER('" + dbname + "')) SELECT distinct to_char(MX, 'Mon ddth, yyyy HH24:MI:SS'), dg_name, to_char(dg_tot_size,'999,999,999.99') TOTAL, to_char(dg_use_size, '999,999,999.99') USED, ROUND((dg_use_size / dg_tot_size)*100, 2)  pct_used FROM asmsize_trend, tme where UPPER(dg_dbname)=UPPER('" + dbname + "') and event_date between SMX and MX ORDER BY pct_used desc")
        dgdata = cursor.fetchall()
        cursor.execute("select distinct dg_name from asmsize_trend where UPPER(dg_dbname)=UPPER('" + dbname + "')")
        diskgroups = cursor.fetchall()
        for dgrp in diskgroups:
            string = "select event_date, dg_use_size from asmsize_trend where dg_name='" + dgrp[0] + "' and UPPER(dg_dbname)=UPPER('" + dbname + "') and event_date > sysdate-30 order by event_date"
            query = pd.read_sql_query(string, con)
            df = pd.DataFrame(query)
            isempty = df.empty
            if isempty == False:
                df.plot.line("EVENT_DATE")
                plt.xlabel("Date")
                plt.ylabel("Used Size (GB)")
                picloc = './oracle_dashboard/static/' + dgrp[0] + '.jpg'
                plt.savefig(picloc)
        cursor.execute("select distinct tablespace_name from oracle_tablespaces where UPPER(database_name)=UPPER('" + dbname + "')")
        tablespaces = cursor.fetchall()
        for tbsp in tablespaces:
            string2 = "SELECT event_date, total_used_size from oracle_tablespaces where tablespace_name='" + tbsp[0] + "' and UPPER(database_name)=UPPER('" + dbname + "') and event_date > sysdate-30 order by event_date"
            query2 = pd.read_sql_query(string2, con)
            df2 = pd.DataFrame(query2)
            isempty = df2.empty
            if isempty == False:
                df2.plot.line("EVENT_DATE")
                plt.xlabel("Date")
                plt.ylabel("Used Size (GB)")
                picloc = './oracle_dashboard/static/' + dbname + '_' + tbsp[0] + '.jpg'
                plt.savefig(picloc)
        cursor.execute("select MAX_DB_FILES, TOTAL_DB_FILES from oracle_databases where UPPER(name)=UPPER('" + dbname + "')")
        dbfiles = cursor.fetchone()
        cursor.execute("select TS_NAME, DF_NAME, TO_CHAR(CREATION_DATE, 'DD-MON-YYYY HH24:MI:SS') from oracle_datafiles where UPPER(DB_NAME)=UPPER('" + dbname + "') order by CREATION_DATE")
        datafiles = cursor.fetchall()
        if cursor:
            cursor.close()
        if con:
            con.close()
        return render_template('database-overview.html', data=tbdata, data1=dgdata, dbname=dbname, dbfiles=dbfiles, datafiles=datafiles)

    @app.route('/Oracle/dg_historical/<string:dg_name>, <string:dbname>')
    def get_dg_history(dg_name, dbname):
        con = cx_Oracle.connect('<username/password>')
        cursor = con.cursor()
        string = "select event_date, dg_use_size from asmsize_trend where event_date > sysdate-60 and dg_name='" + dg_name + "' and UPPER(dg_dbname)=UPPER('" + dbname + "') order by event_date"
        query = pd.read_sql_query(string, con)
        df = pd.DataFrame(query)
        df.plot.line(x="EVENT_DATE")
        plt.xlabel("Date")
        plt.ylabel("Used Size (GB)")
        picloc = './oracle_dashboard/static/' + dg_name + '_60day.jpg'
        plt.savefig(picloc)
        string2 = "select event_date, dg_use_size from asmsize_trend where event_date > sysdate-90 and dg_name='" + dg_name + "' and UPPER(dg_dbname)=UPPER('" + dbname + "') order by event_date"
        query2 = pd.read_sql_query(string2, con) 
        df2 = pd.DataFrame(query2)
        df2.plot.line(x="EVENT_DATE")
        plt.xlabel("Date")
        plt.ylabel("Used Size (GB)")
        picloc = './oracle_dashboard/static/' + dg_name + '_90day.jpg'
        plt.savefig(picloc)
        if cursor:
            cursor.close()
        if con:
            con.close()
        return render_template('dg_historical.html', dg=dg_name, dbname=dbname)

    @app.route('/Oracle/tb_historical/<string:tb_name>, <string:dbname>')
    def get_tb_history(tb_name, dbname):
        con = cx_Oracle.connect('<username/password>')
        cursor = con.cursor()
        string = "SELECT event_date, total_used_size from oracle_tablespaces where tablespace_name='" + tb_name + "' and database_name='" + dbname + "' and event_date > sysdate-60 order by event_date"
        query = pd.read_sql_query(string, con)
        df = pd.DataFrame(query)
        df.plot.line(x="EVENT_DATE")
        plt.xlabel("Date")
        plt.ylabel("Used Size (GB)")
        picloc = './oracle_dashboard/static/' + dbname + '_' + tb_name + '_60day.jpg'
        plt.savefig(picloc)
        string2 = "SELECT event_date, total_used_size from oracle_tablespaces where tablespace_name='" + tb_name + "' and database_name='" + dbname + "' and event_date > sysdate-90 order by event_date"
        query2 = pd.read_sql_query(string2, con)
        df2 = pd.DataFrame(query2)
        df2.plot.line(x="EVENT_DATE")
        plt.xlabel("Date")
        plt.ylabel("Used Size (GB)")
        picloc = './oracle_dashboard/static/' + dbname + '_' + tb_name + '_90day.jpg'
        plt.savefig(picloc)
        if cursor:
            cursor.close()
        if con:
            con.close()
        return render_template('tb_historical.html', tb=tb_name, dbname=dbname)

    @app.errorhandler(Exception)
    def server_error(err):
        return render_template('not_found.html') 
 
    return app
