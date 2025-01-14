"""
Faraday Penetration Test IDE
Copyright (C) 2013  Infobyte LLC (http://www.infobytesec.com/)
See the file 'doc/LICENSE' for the license information

"""
import socket

import sqlalchemy
from colorama import init
from colorama import Fore

import faraday.server.config
from faraday.server.web import get_app
from faraday.server.models import db
from faraday.server.config import CONST_FARADAY_HOME_PATH
from faraday.server.utils.daemonize import is_server_running
import faraday_plugins

init()


def check_server_running():
    port = int(faraday.server.config.faraday_server.port)
    pid = is_server_running(port)
    return pid


def check_open_ports():
    address = faraday.server.config.faraday_server.bind_address
    port = int(faraday.server.config.faraday_server.port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((address, port))
    if result == 0:
        return True
    else:
        return False


def check_postgres():
    with get_app().app_context():
        try:
            result = (
                db.session.query("version()").one(), db.session.query("current_setting('server_version_num')").one())
            return result
        except sqlalchemy.exc.OperationalError:
            return False
        except sqlalchemy.exc.ArgumentError:
            return None


def check_locks_postgresql():
    with get_app().app_context():
        psql_status = check_postgres()
        if psql_status:
            result = db.engine.execute("""SELECT blocked_locks.pid     AS blocked_pid,
                                            blocked_activity.usename  AS blocked_user,
                                            blocking_locks.pid     AS blocking_pid,
                                            blocking_activity.usename AS blocking_user,
                                            blocked_activity.query    AS blocked_statement,
                                            blocking_activity.query   AS current_statement_in_blocking_process
                                        FROM  pg_catalog.pg_locks         blocked_locks
                                            JOIN pg_catalog.pg_stat_activity blocked_activity  ON blocked_activity.pid = blocked_locks.pid
                                        JOIN pg_catalog.pg_locks         blocking_locks
                                            ON blocking_locks.locktype = blocked_locks.locktype
                                            AND blocking_locks.DATABASE IS NOT DISTINCT FROM blocked_locks.DATABASE
                                            AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
                                            AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
                                            AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
                                            AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
                                            AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
                                            AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
                                            AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
                                            AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
                                            AND blocking_locks.pid != blocked_locks.pid
                                        JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
                                            WHERE NOT blocked_locks.GRANTED;""")
            fetch = result.fetchall()
            if fetch:
                return True
            else:
                return False

        else:
            return None


def check_postgresql_encoding():
    with get_app().app_context():
        psql_status = check_postgres()
        if psql_status:
            encoding = db.engine.execute("SHOW SERVER_ENCODING").first()[0]
            return encoding
        else:
            return None


def check_storage_permission():
    path = CONST_FARADAY_HOME_PATH / 'storage' / 'test'

    try:
        path.mkdir()
        path.rmdir()
        return True
    except OSError:
        return None


def print_config_info():
    print(f'\n{Fore.WHITE}Showing faraday server configuration')
    print(f"{Fore.BLUE} version: {Fore.WHITE}{faraday.__version__}")

    data_keys = ['bind_address', 'port', 'websocket_port', 'debug']
    for key in data_keys:
        print('{blue} {KEY}: {white}{VALUE}'.
              format(KEY=key, VALUE=getattr(faraday.server.config.faraday_server, key), white=Fore.WHITE,
                     blue=Fore.BLUE))

    print(f'\n{Fore.WHITE}Showing faraday plugins data')
    print(f"{Fore.BLUE} version: {Fore.WHITE}{faraday_plugins.__version__}")

    print(f'\n{Fore.WHITE}Showing dashboard configuration')
    data_keys = ['show_vulns_by_price']
    for key in data_keys:
        print('{blue} {KEY}: {white}{VALUE}'.
              format(KEY=key, VALUE=getattr(faraday.server.config.dashboard, key), white=Fore.WHITE, blue=Fore.BLUE))

    print(f'\n{Fore.WHITE}Showing storage configuration')
    data_keys = ['path']
    for key in data_keys:
        print('{blue} {KEY}: {white}{VALUE}'.
              format(KEY=key, VALUE=getattr(faraday.server.config.storage, key), white=Fore.WHITE, blue=Fore.BLUE))


def print_postgresql_status():
    """Prints the status of PostgreSQL using check_postgres()"""
    exit_code = 0
    result = check_postgres()

    if not result:
        print('[{red}-{white}] Could not connect to PostgreSQL, please check if database is running'
              .format(red=Fore.RED, white=Fore.WHITE))
        exit_code = 1
        return exit_code
    elif result is None:
        print('[{red}-{white}] Database not initialized. Execute: faraday-manage initdb'
              .format(red=Fore.RED, white=Fore.WHITE))
        exit_code = 1
        return exit_code
    elif int(result[1][0]) < 90400:
        print('[{red}-{white}] PostgreSQL is running, but needs to be 9.4 or newer, please update PostgreSQL'
              .format(red=Fore.RED, white=Fore.WHITE))
    elif result:
        print(f'[{Fore.GREEN}+{Fore.WHITE}] PostgreSQL is running and up to date')
        return exit_code


def print_postgresql_other_status():
    """Prints the status of locks in Postgresql using check_locks_postgresql() and
    prints Postgresql encoding using check_postgresql_encoding()"""

    lock_status = check_locks_postgresql()
    if lock_status:
        print(f'[{Fore.YELLOW}-{Fore.WHITE}] Warning: PostgreSQL lock detected.')
    elif not lock_status:
        print(f'[{Fore.GREEN}+{Fore.WHITE}] PostgreSQL lock not detected. ')
    elif lock_status is None:
        pass

    encoding = check_postgresql_encoding()
    if encoding:
        print(f'[{Fore.GREEN}+{Fore.WHITE}] PostgreSQL encoding: {encoding}')
    elif encoding is None:
        pass


def print_faraday_status():
    """Prints Status of farday using check_server_running() """

    # Prints Status of the server using check_server_running()
    pid = check_server_running()
    if pid is not None:
        print('[{green}+{white}] Faraday Server is running. PID:{PID} \
        '.format(green=Fore.GREEN, PID=pid, white=Fore.WHITE))
    else:
        print('[{red}-{white}] Faraday Server is not running {white} \
        '.format(red=Fore.RED, white=Fore.WHITE))


def print_config_status():
    """Prints Status of the configuration using check_credentials(), check_storage_permission() and check_open_ports()"""

    check_server_running()
    check_postgres()

    if check_storage_permission():
        print(f'[{Fore.GREEN}+{Fore.WHITE}] /.faraday/storage -> Permission accepted')
    else:
        print(f'[{Fore.RED}-{Fore.WHITE}] /.faraday/storage -> Permission denied')

    if check_open_ports():
        print("[{green}+{white}] Port {PORT} in {ad} is open"
              .format(PORT=faraday.server.config.faraday_server.port,
                      green=Fore.GREEN, white=Fore.WHITE, ad=faraday.server.config.faraday_server.bind_address))
    else:
        print("[{red}-{white}] Port {PORT} in {ad} is not open"
              .format(PORT=faraday.server.config.faraday_server.port,
                      red=Fore.RED, white=Fore.WHITE, ad=faraday.server.config.faraday_server.bind_address))


def full_status_check():
    print_config_info()

    print(f'\n{Fore.WHITE}Checking if postgreSQL is running...')
    print_postgresql_status()
    print_postgresql_other_status()

    print(f'\n{Fore.WHITE}Checking if Faraday is running...')
    print_faraday_status()

    print('\n{white}Checking Faraday config...{white}'.format(white=Fore.WHITE))
    print_config_status()
