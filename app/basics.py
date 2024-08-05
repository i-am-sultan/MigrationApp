import requests
import subprocess
import re
import os
import psycopg2
import zipfile
from io import BytesIO
import json
import shutil

oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\OraCon.txt'
pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\netcoreapp3.1\pgCon.txt'

def get_latest_release_info(repo):
    api_url = f"https://api.github.com/repos/{repo}/releases/latest"
    headers = {
        'Accept': 'application/vnd.github.v3+json'
    }
    response = requests.get(api_url, headers=headers)

    if response.status_code == 200:
        release_info = response.json()
        return release_info
    else:
        print(f"Failed to fetch release information. Status code: {response.status_code}")
        return None

def checkForUpdates(log_window):
    log_window.append('Checking for updates...')
    try:
        repo = "i-am-sultan/MigrationApp"
        latest_release = get_latest_release_info(repo)

        if latest_release:
            latest_version = latest_release['tag_name']
            assets = latest_release['assets']

            if assets:
                update_asset = assets[0]  # Assuming the first asset is the one you want to download
                update_url = update_asset['browser_download_url']
                os.chdir('..')  # Now in MigrationApp folder
                version_path = os.path.join(os.getcwd(), 'app', 'version.txt')

                # Read the current version from a file
                try:
                    with open(version_path, 'r') as f:
                        current_version = f.read().strip()
                except Exception as e:
                    log_window.append(f'Failed to read the current version. Error: {e}')
                    return 1

                log_window.append(f'Current version: {current_version}')
                log_window.append(f'Latest version: {latest_version}')

                # Compare versions
                if latest_version != current_version:
                    log_window.append('New version available. Downloading and applying update...')

                    # Download the update
                    response = requests.get(update_url)
                    if response.status_code == 200:
                        update_dir_path = os.getcwd()  # cwd: MigrationApp

                        try:
                            # Extract the zip file into the new directory
                            with zipfile.ZipFile(BytesIO(response.content)) as zip_ref:
                                zip_ref.extractall(update_dir_path)

                            log_window.append('Update downloaded and extracted successfully.')
                            log_window.append('Update applied successfully.')
                            icon_path = os.path.join(update_dir_path, 'app', 'data-migration.ico')
                            file_path = os.path.join(update_dir_path, 'app', 'main.py')
                            # Create the exe
                            command_to_exe = f"pyinstaller --name MigrationApp_{latest_version} --onefile --windowed --icon={icon_path} {file_path}"

                            # Execute the command
                            log_window.append('Creating executable...')
                            log_window.append(f'command_to_exe: {command_to_exe}')
                            result = subprocess.run(command_to_exe, shell=True, capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                log_window.append('Executable created successfully.')
                                return 0
                            else:
                                log_window.append(f"Failed to create executable. Error: {result.stderr}")
                                return 1
                        except Exception as e:
                            log_window.append(f'Failed to extract and apply update. Error: {e}')
                            return 1
                    else:
                        log_window.append(f"Failed to download update. Status code: {response.status_code}")
                        return 1
                else:
                    log_window.append('You are already using the latest version.')
                    return 1
            else:
                log_window.append('No assets found in the latest release.')
                return 1
        else:
            log_window.append('Failed to fetch latest release information.')
            return 1

    except Exception as e:
        log_window.append(f'Error checking and applying updates: {e}')
        return 1

def updateOraCon(OraSchema, OraHost,oraPort, OraPass,OraService, filepath, log_window):
    content = (
            f"User Id={OraSchema};Password={OraPass};"
            f"Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={OraHost})(PORT={oraPort}))"
            f"(CONNECT_DATA=(SERVICE_NAME={OraService})))"
        )
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('OraCon updated successfully...')

def updatepgCon(pgHost,pgPort, pgUser,pgPass, pgDbName, filepath, log_window):
    content = (f"Server={pgHost};Port={pgPort};Database={pgDbName};User Id={pgUser};Password={pgPass};ApplicationName=w3wp.exe;Ssl Mode=Require;")
    with open(filepath, 'w') as f1:
        f1.write(content)
    log_window.append('\npgCon updated successfully... ')

def updateToolkit(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost, pgPort,pgUser, pgPass, pgDbName, filepath, log_window):
    # Prepare the new properties
    oracle_url = f"jdbc:oracle:thin:@{OraHost}:{OraPort}:{OraService}"
    postgres_url = f"jdbc:postgresql://{pgHost}:{pgPort}/{pgDbName}"
    
    content = (
        f"SRC_DB_URL={oracle_url}\n"
        f"SRC_DB_USER={OraSchema}\n"
        f"SRC_DB_PASSWORD={OraPass}\n\n"
        f"TARGET_DB_URL={postgres_url}\n"
        f"TARGET_DB_USER={pgUser}\n"
        f"TARGET_DB_PASSWORD={pgPass}\n"
    )   
    try: 
        with open(filepath, 'w') as f1:
            f1.write(content)
    except FileNotFoundError:
        log_window.append(f'\nError: file {filepath} not found.')
    except Exception as e:
        log_window.append(f'\nError: updating file toolkit.properties: {str(e)}')
    log_window.append('\ntoolkit.properties updated successfully...')
    log_window.append('\nPlease check the credentials of toolkit.properties in below logwindow before proceed...')
    log_window.append(content)

def updateConnectionJson(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            connections = json.load(f)
        # Update the Oracle connection string
        connections["Connection_1"] = f"Data Source=(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={OraHost})(PORT={OraPort}))(CONNECT_DATA=(SERVICE_NAME={OraService})));User Id={OraSchema};Password={OraPass};DatabaseType=ORACLE"
        # Update the PostgreSQL connection string
        connections["Connection_2"] = f"Server={pgHost};Port={pgPort};Database={pgDbName};User Id={pgUser};Password={pgPass};ApplicationName=w3wp.exe;Ssl Mode=Require;DatabaseType=POSTGRES"
        with open(filepath, 'w') as f:
            json.dump(connections, f, indent=4)
        log_window.append('\nconnection.json updated successfully...')
        # log_window.append(json.dumps(connections, indent=4))
    except FileNotFoundError:
        log_window.append(f'Error: File {filepath} not found.')
    except json.JSONDecodeError as e:
        log_window.append(f'Error: Failed to decode JSON from {filepath}. Details: {str(e)}')
    except Exception as e:
        log_window.append(f'Error updating connection.json: {str(e)}')

def updatePatchDrill(pgDbname, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Modify the content to replace dbname with pgDbname
        content = re.sub(r"OPTIONS \(dbname '[^']+\'", f"OPTIONS (dbname '{pgDbname}'", content)
        content = re.sub(r'REVOKE ALL ON DATABASE "[^"]+',f'REVOKE ALL ON DATABASE "{pgDbname}',content)
        content = re.sub(r'GRANT CONNECT ON DATABASE "[^"]+',f'GRANT CONNECT ON DATABASE "{pgDbname}',content)

        with open(filepath, 'w') as f:
            f.write(content)

        log_window.append(f'\nSuccessfully updated patch_drill.sql for database {pgDbname}.')
    except Exception as e:
        log_window.append(f'\nError updating patch_drill.sql: {e}')

def updatePatchLive(pgDbname, filepath, log_window):
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Modify the content to replace dbname with pgDbname
        content = re.sub(r"OPTIONS \(dbname '[^']+\'", f"OPTIONS (dbname '{pgDbname}'", content)
        content = re.sub(r'REVOKE ALL ON DATABASE "[^"]+',f'REVOKE ALL ON DATABASE "{pgDbname}',content)
        content = re.sub(r'GRANT CONNECT ON DATABASE "[^"]+',f'GRANT CONNECT ON DATABASE "{pgDbname}',content)

        with open(filepath, 'w') as f:
            f.write(content)

        log_window.append(f'\nSuccessfully updated patch_live.sql for database {pgDbname}.')
    except Exception as e:
        log_window.append(f'\nError updating patch_live.sql: {e}')

def copyFiles(destination_dir, log_window):
    try:
        # Pre-specified file paths

        shutil.copy(oracon_path, destination_dir)
        shutil.copy(pgcon_path, destination_dir)
        
        log_window.append('\nOraCon.txt and pgCon.txt copied and pasted successfully...')
        # log_window.append(f'OraCon.txt and pgCon.txt copied from {oracon_path} and {pgcon_path} to {destination_dir}')
        return True
    except Exception as e:
        log_window.append(f'Error copying files: {e}')
        return False

def executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_path, log_window):
    connection = None
    cursor = None
    try:
        # Read the SQL patch file
        with open(patch_path, 'r') as f1:
            content = f1.read()
        content = re.sub(r"dbname [^,]+", f"dbname '{pgDbname}'", content)
        with open(patch_path, 'w') as f1:
            f1.write(content)
        # Connect to the PostgreSQL database
        connection = psycopg2.connect(database=pgDbname, user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(content)
        connection.commit()
        log_window.append(f'\nSuccess: Executed patch {patch_path} on database {pgDbname}.')
    except psycopg2.Error as e:
        # Log any psycopg2 database errors
        log_window.append(f'\nError: Failed to execute patch {patch_path} on database {pgDbname}. Error: {e}')
    except Exception as e:
        # Log any other unexpected errors
        log_window.append(f'\nError: Failed to execute patch {patch_path} on database {pgDbname}. Unexpected error: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def cubeDataPopulation(self,pgHost, pgUserName, pgPort, pgPass,pgDbname,log_window):
    try:
        connection = psycopg2.connect(database=pgDbname, user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        connection.autocommit = True
        cursor = connection.cursor()
        log_window.append(f'\nCube intial data population is started...')
        cursor.execute('CALL populate_first_time_migdata()')
        # Commit the transaction
        connection.commit()
        connection.close()
        # Log successful execution
        log_window.append(f'\nSuccess: Intial cube data populatino is done.')
        return 1
    except Exception as e:
        log_window.append(f'\nError: Failed to populate cube initial data. Unexpected error: {e}')
        return 0
    
def createJobs(pgHost, pgUserName, pgPort, pgPass, pgDbname, log_window):
    connection = None
    cursor = None
    try:
        # Connect to the PostgreSQL database and execute the job creation procedure.
        connection = psycopg2.connect(database='postgres', user=pgUserName, password=pgPass, host=pgHost, port=pgPort)
        cursor = connection.cursor()
        cursor.execute('call schedule_jobs_in_postgres()')
        connection.commit()
        log_window.append(f'\nSuccessfully created jobs on database {pgDbname}.')
    except psycopg2.Error as e:
        log_window.append(f'\nError creating jobs on database {pgDbname}: {e}')
    except Exception as e:
        log_window.append(f'\nUnexpected error while creating jobs on database {pgDbname}: {e}')
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()