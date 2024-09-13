import sys
import re
import subprocess
import psycopg2
import cx_Oracle
import os
from threading import *
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel,
    QLineEdit, QPushButton, QComboBox, QTextEdit, QMessageBox,QMainWindow
)
from PyQt5.QtGui import QIcon
from basics import *

oracon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\RunEDBToolkit_OLD\netcoreapp3.1\OraCon.txt'
pgcon_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\RunEDBToolkit_OLD\netcoreapp3.1\pgCon.txt'
toolkit_path = r'C:\Program Files\edb\mtk\etc\toolkit.properties'
connection_json_path = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\Connection.json'
audit_path = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1'
patch_drill_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_drill.sql'
patch_live_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_live.sql'
job_patch_path = r'C:\Program Files\edb\prodmig\PostMigPatches\patch_jobs.sql'
migrationapp_path = r'C:\Program Files\edb\prodmig\RunCMDEdb_New\RunEDBToolkit_OLD\netcoreapp3.1\RunEDBCommand.exe'
audittriggerapp_path = r'C:\Program Files\edb\prodmig\AuditTriggerCMDNew\netcoreapp3.1\TriggerConstraintViewCreationForAuditPostMigration.exe'
comparetoolapp_path = r'C:\Program Files\edb\prodmig\Ora2PGCompToolKit\Debug\OraPostGreSqlComp.exe'

class UpdateConnectionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
    def initUI(self):
        self.setWindowTitle('Ginesys Migration Application')
        self.resize(1000,400)
        # self.setWindowIcon(QIcon(r'app\data-migration.ico'))  # Set a custom icon for the window
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        
        # Top Layout for credentials
        form_layout = QGridLayout()

        # Define CSS styling
        label_style = "font-size: 14px; font-weight: regular; color: #2c3e50;"
        input_style = "background-color: white; border: 1px solid #bdc3c7; border-radius: 5px; padding: 5px; font-size: 14px; color: #34495e;"

        # Oracle credentials
        self.oraHostLabel = QLabel('Oracle Host:')
        self.oraHostLabel.setStyleSheet(label_style)
        self.oraHostInput = QLineEdit()
        self.oraHostInput.setStyleSheet(input_style)
        
        self.oraPortLabel = QLabel('Oracle Port:')
        self.oraPortLabel.setStyleSheet(label_style)
        self.oraPortInput = QLineEdit()
        self.oraPortInput.setStyleSheet(input_style)
        
        self.oraSchemaLabel = QLabel('Oracle Schema:')
        self.oraSchemaLabel.setStyleSheet(label_style)
        self.oraSchemaInput = QLineEdit()
        self.oraSchemaInput.setStyleSheet(input_style)
        
        self.oraPassLabel = QLabel('Oracle Password:')
        self.oraPassLabel.setStyleSheet(label_style)
        self.oraPassInput = QLineEdit()
        self.oraPassInput.setStyleSheet(input_style)
        # self.oraPassInput.setEchoMode(QLineEdit)  # Hide password input
        # self.oraPassInput.setEchoMode(QLineEdit.Password)  # Hide password input
        
        self.oraServiceLabel = QLabel('Oracle Service:')
        self.oraServiceLabel.setStyleSheet(label_style)
        self.oraServiceInput = QLineEdit()
        self.oraServiceInput.setStyleSheet(input_style)

        # PostgreSQL credentials
        self.pgHostLabel = QLabel('PostgreSQL Host:')
        self.pgHostLabel.setStyleSheet(label_style)
        self.pgHostInput = QLineEdit()
        self.pgHostInput.setStyleSheet(input_style)
        
        self.pgPortLabel = QLabel('PostgreSQL Port:')
        self.pgPortLabel.setStyleSheet(label_style)
        self.pgPortInput = QLineEdit()
        self.pgPortInput.setStyleSheet(input_style)
        
        self.pgUserLabel = QLabel('PostgreSQL Username:')
        self.pgUserLabel.setStyleSheet(label_style)
        self.pgUserInput = QLineEdit()
        self.pgUserInput.setStyleSheet(input_style)
        
        self.pgPassLabel = QLabel('PostgreSQL Password:')
        self.pgPassLabel.setStyleSheet(label_style)
        self.pgPassInput = QLineEdit()
        self.pgPassInput.setStyleSheet(input_style)
        # self.pgPassInput.setEchoMode(QLineEdit)  # Hide password input
        
        self.pgDbNameLabel = QLabel('PostgreSQL Database Name:')
        self.pgDbNameLabel.setStyleSheet(label_style)
        self.pgDbNameInput = QLineEdit()
        self.pgDbNameInput.setStyleSheet(input_style)


        # Adding widgets to grid layout
        form_layout.addWidget(self.oraHostLabel, 0, 0)
        form_layout.addWidget(self.oraHostInput, 0, 1)
        form_layout.addWidget(self.pgHostLabel, 0, 2)
        form_layout.addWidget(self.pgHostInput, 0, 3)

        form_layout.addWidget(self.oraPortLabel, 1, 0)
        form_layout.addWidget(self.oraPortInput, 1, 1)
        form_layout.addWidget(self.pgPortLabel, 1, 2)
        form_layout.addWidget(self.pgPortInput, 1, 3)

        form_layout.addWidget(self.oraSchemaLabel, 2, 0)
        form_layout.addWidget(self.oraSchemaInput, 2, 1)
        form_layout.addWidget(self.pgUserLabel, 2, 2)
        form_layout.addWidget(self.pgUserInput, 2, 3)

        form_layout.addWidget(self.oraPassLabel, 3, 0)
        form_layout.addWidget(self.oraPassInput, 3, 1)
        form_layout.addWidget(self.pgPassLabel, 3, 2)
        form_layout.addWidget(self.pgPassInput, 3, 3)

        form_layout.addWidget(self.oraServiceLabel, 4, 0)
        form_layout.addWidget(self.oraServiceInput, 4, 1)
        form_layout.addWidget(self.pgDbNameLabel, 4, 2)
        form_layout.addWidget(self.pgDbNameInput, 4, 3)

        # Sidebar Layout for buttons
        sidebar_layout = QVBoxLayout()
        # sidebar_layout.setSpacing(10)
        
        # Define buttons with icons and CSS styling

        # New button for checking and applying updates
        self.update_app_button = QPushButton("Check for Updates")
        self.update_app_button.setStyleSheet("QPushButton {background-color: black; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: grey;}")
        self.update_app_button.clicked.connect(self.checkAndApplyUpdates)
        sidebar_layout.addWidget(self.update_app_button)
        
        self.updateButton = QPushButton('Update Connections')
        self.updateButton.setStyleSheet("QPushButton {background-color: #2980b9; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #00416b;}")
        self.updateButton.clicked.connect(self.updateConnections)
        sidebar_layout.addWidget(self.updateButton)

        self.compareButton = QPushButton('Compare Version')
        self.compareButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.compareButton.clicked.connect(self.compareVersions)
        sidebar_layout.addWidget(self.compareButton)
        
        self.migrationButton = QPushButton('Run Migration App')
        self.migrationButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.migrationButton.clicked.connect(self.runMigrationApp)
        sidebar_layout.addWidget(self.migrationButton)
        
        self.auditButton = QPushButton('Run Audit App')
        self.auditButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.auditButton.clicked.connect(self.runAuditApp)
        sidebar_layout.addWidget(self.auditButton)
        
        self.compareButton = QPushButton('Run Compare Tool')
        self.compareButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.compareButton.clicked.connect(self.runCompareToolApp)
        sidebar_layout.addWidget(self.compareButton)
        
        self.patchComboBox = QComboBox()
        self.patchComboBox.addItem("Live")
        self.patchComboBox.addItem("Drill")

        # Applying CSS to the QComboBox
        self.patchComboBox.setStyleSheet("padding: 5px;")
        # self.patchComboBox.setStyleSheet("background-color: #dedcdc; color: black; font-weight: regular; border-radius: 1px; padding: 10px;")
        sidebar_layout.addWidget(self.patchComboBox)
        
        self.patchButton = QPushButton('Execute PostMig SQL')
        self.patchButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.patchButton.clicked.connect(self.executeSQLPatch)
        sidebar_layout.addWidget(self.patchButton)
        
        self.cubePopulationButton = QPushButton(QIcon('icons/cube.png'), 'Cube Data Population')
        self.cubePopulationButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.cubePopulationButton.clicked.connect(self.cubeDataPopulationThread)
        sidebar_layout.addWidget(self.cubePopulationButton)
        
        self.createJobsButton = QPushButton(QIcon('icons/jobs.png'), 'Create Jobs')
        self.createJobsButton.setStyleSheet("QPushButton {background-color: #404040; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #000000;}")
        self.createJobsButton.clicked.connect(self.createJobsThread)
        sidebar_layout.addWidget(self.createJobsButton)
        
        self.exitButton = QPushButton(QIcon('icons/exit.png'), 'Exit')
        self.exitButton.setStyleSheet("QPushButton {background-color: #c0392b; color: white; font-weight: bold; border-radius: 5px; padding: 10px;} QPushButton:hover {background-color: #570500;}")
        self.exitButton.clicked.connect(self.closeApplication)
        sidebar_layout.addWidget(self.exitButton) #700700 c0392b

        # Log Window
        self.logWindow = QTextEdit()
        self.logWindow.setReadOnly(True)
        self.logWindow.setStyleSheet("background-color: white; border-radius: 8px; border: 1px solid #ddd; padding: 10px; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-size: 14px;")

        # Main Layout setup
        top_layout = QVBoxLayout()
        top_layout.addLayout(form_layout)
        
        # Adding Sidebar and Log Window to Main Layout
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.logWindow, 1)  # Log window should be stretched to fill the remaining space

        # Create a container layout to hold the sidebar and log window
        container_layout = QHBoxLayout()
        container_layout.addLayout(sidebar_layout)
        container_layout.addLayout(main_layout)
        
        central_widget.setLayout(container_layout)
        # Load initial credentials from configuration files
        self.loadCredentialsFromFiles()

    def checkAndApplyUpdates(self):
        result = checkForUpdates(self.logWindow)
        version_path = os.getcwd()
        if result == 0:
            QMessageBox.critical(self,'Updated!',f'Now close this application! Run the latest Verison!\n Check the latest version in directory: {version_path}')
    def loadCredentialsFromFiles(self):
        self.logWindow.append("[log window]\n")
        try:
            # Pre-specified file paths
            global oracon_path
            global pgcon_path

            with open(oracon_path, 'r') as f1:
                content = f1.read()
            schema_match = re.search(r'User Id=([^;]+);', content)
            host_match = re.search(r'HOST=([^)]+)', content)
            port_match = re.search(r'PORT=([^)]+)', content)
            pass_match = re.search(r'Password=([^;]+)', content)
            service_match = re.search(r'SERVICE_NAME=([^)]+)',content)
            if schema_match and host_match and port_match and pass_match and service_match:
                self.oraSchemaInput.setText(schema_match.group(1))
                self.oraHostInput.setText(host_match.group(1))
                self.oraPortInput.setText(port_match.group(1))
                self.oraPassInput.setText(pass_match.group(1))
                self.oraServiceInput.setText(service_match.group(1))
                self.logWindow.append("Oracle Credentials successfully loaded from oracon.txt")
            else:
                self.logWindow.append("Error: Oracle credentials not found in OraCon.txt")

            with open(pgcon_path, 'r') as f1:
                content = f1.read()
            dbname_match = re.search(r'Database=([^;]+);', content)
            pghost_match = re.search(r'Server=([^;]+);', content)
            pgport_match = re.search(r'Port=([^;]+);', content)
            pgpass_match = re.search(r'Password=([^;]+);', content)
            pguser_match = re.search(r'User Id=([^;]+);', content)
            if dbname_match and pghost_match and pgport_match and pguser_match and pgpass_match:
                self.pgDbNameInput.setText(dbname_match.group(1))
                self.pgHostInput.setText(pghost_match.group(1))
                self.pgPortInput.setText(pgport_match.group(1))
                self.pgPassInput.setText(pgpass_match.group(1))
                self.pgUserInput.setText(pguser_match.group(1))
                self.logWindow.append("PostgreSQL Credentials successfully loaded from pgcon.txt")
            else:
                self.logWindow.append("Error: PostgreSQL Credentials not found in pgCon.txt")

        except Exception as e:
            self.logWindow.append(f'Error loading credentials from files: {e}')

    def updateConnections(self):
        OraSchema = self.oraSchemaInput.text()
        OraHost = self.oraHostInput.text()
        OraPort = self.oraPortInput.text()
        OraPass = self.oraPassInput.text()
        OraService = self.oraServiceInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()
        pgUser = self.pgUserInput.text()
        pgDbName = self.pgDbNameInput.text()

        if not OraSchema or not OraHost or not OraPort or not OraPass or not OraService or not pgHost or not pgPass or not pgUser or not pgDbName or not pgPort:
            QMessageBox.warning(self, 'Input Error', 'Please fill in all fields.')
            return
        try:
            # Pre-specified file paths
            global oracon_path
            global pgcon_path
            global toolkit_path
            global connection_json_path
            global audit_path

            updateOraCon(OraSchema, OraHost,OraPort,OraPass,OraService, oracon_path, self.logWindow)
            updatepgCon(pgHost,pgPort, pgUser,pgPass,pgDbName, pgcon_path, self.logWindow)
            updateToolkit(OraSchema, OraHost,OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, toolkit_path, self.logWindow)
            updateConnectionJson(OraSchema, OraHost, OraPort, OraPass, OraService, pgHost,pgPort, pgUser, pgPass, pgDbName, connection_json_path, self.logWindow)

            # Copy the files to the destination directory
            success = copyFiles(audit_path, self.logWindow)
            if success:
                QMessageBox.information(self, 'Success', 'Connections updated and files copied successfully.')
            else:
                QMessageBox.critical(self, 'Error', 'An error occurred while copying files.')

        except Exception as e:
            QMessageBox.critical(self, 'Error', f'An error occurred: {e}')
            self.logWindow.append(f'\nError updating connections: {e}')

    def compareVersions(self):
        OraSchema = self.oraSchemaInput.text()
        OraHost = self.oraHostInput.text()
        OraPort = self.oraPortInput.text()
        OraPass = self.oraPassInput.text()
        OraService = self.oraServiceInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()
        pgUser = self.pgUserInput.text()
        pgDbName = self.pgDbNameInput.text()
        try:
            oracon = cx_Oracle.connect(f'{OraSchema}/{OraPass}@{OraHost}:{OraPort}/{OraService}')
            cur = oracon.cursor()
            cur.execute('select db_version from gateway.packdef')
            ora_version = cur.fetchone()[0]
            cur.close()
            oracon.close()
            
        except cx_Oracle.DatabaseError as e:
            QMessageBox.critical(self, 'Error', f'Failed to connect to Oracle database.\nError: {str(e)}')
            self.logWindow.append(f'Failed to connect to Oracle database.\nError: {str(e)}')
            return
        try:
            pgcon = psycopg2.connect(database=pgDbName, user=pgUser, password=pgPass, host=pgHost, port=pgPort)
            cur = pgcon.cursor()
            cur.execute('select db_version from gateway.packdef')
            pg_version = cur.fetchone()[0]
            cur.close()
            pgcon.close()
        except psycopg2.DatabaseError as e:
            QMessageBox.critical(self,'Error',f'Failed to connect to postgres database.\nError: {str(e)}')
            self.logWindow.append(f'Failed to connect to postgres database.\nError: {str(e)}')
            return

        if ora_version == pg_version:
            QMessageBox.information(self,f'Success!', f'Great, Version Matched!\nOracle({ora_version}) and Postgres({pg_version}) Version are the same,now you can proceed with migration!')
            self.logWindow.append(f'Great, Version Matched!\nOracle({ora_version}) and Postgres({pg_version}) Version are the same,now you can proceed with migration!')
        else:
            self.logWindow.append(f'Version Mismatch!\nOracle Version : {ora_version} and PostgreSQL Version: {pg_version}')
            QMessageBox.critical(self,'Error',f'Version Mismatch!\nOracle Version : {ora_version} and PostgreSQL Version: {pg_version}')

    def executeSQLPatch(self):
        patch_choice = self.patchComboBox.currentText()
        global pgcon_path
        global patch_drill_path
        global patch_live_path
        pgDbname = self.pgDbNameInput.text()
        pgUserName = self.pgUserInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()

        if pgDbname:
            if patch_choice == "Drill":
                updatePatchDrill(pgDbname, patch_drill_path, self.logWindow)
                executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_drill_path, self.logWindow)  # Example execution after update
            elif patch_choice == "Live":
                updatePatchLive(pgDbname, patch_live_path, self.logWindow)
                executePatch(pgHost,pgPort,pgUserName,pgPass,pgDbname, patch_live_path, self.logWindow)  # Example execution after update
        else:
            QMessageBox.warning(self, 'Database not found', 'Unable to determine database name from pgCon.txt.')
    
    # def cubeDataPopulationThread(self):
    #     t1 = Thread(target=self.cubeDataPopulation)
    #     t1.start()
        
    def cubeDataPopulationThread(self):
        pgDbname = self.pgDbNameInput.text()
        pgUserName = self.pgUserInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()
        cubeDataPopulation(self,pgHost, pgUserName, pgPort, pgPass, pgDbname, self.logWindow)

    def displayresult(self):
        QMessageBox.information(self,'Success','Cube data successfully populated')

    def createJobsThread(self):
        t1 = Thread(target=self.createJobs)
        t1.start()

    def createJobs(self):
        pgDbname = self.pgDbNameInput.text()
        pgUserName = self.pgUserInput.text()
        pgHost = self.pgHostInput.text()
        pgPort = self.pgPortInput.text()
        pgPass = self.pgPassInput.text()

        createJobs(pgHost, pgUserName, pgPort, pgPass, pgDbname, self.logWindow)

    def runMigrationApp(self):
        global migrationapp_path
        self.runExternalApp(migrationapp_path)

    def runAuditApp(self):
        global audittriggerapp_path
        self.runExternalApp(audittriggerapp_path)

    def runCompareToolApp(self):
        global comparetoolapp_path
        self.runExternalApp(comparetoolapp_path)

    def runExternalApp(self, app_path):
        try:
            if sys.platform.startswith('win'):
                subprocess.Popen(f'start cmd /c "{app_path}"', shell=True)
            else:
                self.logWindow.append('Unsupported OS.')
                QMessageBox.critical(self, 'Error', 'Unsupported OS.')
                return

            self.logWindow.append(f'\n{app_path} executed successfully.')
        except Exception as e:
            self.logWindow.append(f'\nError running {app_path}: {e}')
            QMessageBox.critical(self, 'Error', f'Error running {app_path}: {e}')

    def closeApplication(self):
        self.close()

# Entry point for the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    update_app = UpdateConnectionApp()
    update_app.show()
    sys.exit(app.exec_())