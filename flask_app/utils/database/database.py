import mysql.connector
import glob
import json
import csv
from io import StringIO
import itertools
import hashlib
import os
import cryptography
from cryptography.fernet import Fernet
from math import pow

class database:

    def __init__(self, purge = False):

        # Grab information from the configuration file
        self.database       = 'db'
        self.host           = '127.0.0.1'
        self.user           = 'master'
        self.port           = 3306
        self.password       = 'master'
        self.tables         = ['users', 'boards', 'board_members', 'tasks']
        
        # NEW IN HW 3-----------------------------------------------------------------
        self.encryption     =  {   'oneway': {'salt' : b'redacted',
                                                 'n' : int(pow(2,5)),
                                                 'r' : 9,
                                                 'p' : 1
                                             },
                                'reversible': { 'key' : 'redacted'}
                                }
        #-----------------------------------------------------------------------------

    def query(self, query = "SELECT * FROM users", parameters = None):

        cnx = mysql.connector.connect(host     = self.host,
                                      user     = self.user,
                                      password = self.password,
                                      port     = self.port,
                                      database = self.database,
                                      charset  = 'latin1'
                                     )


        if parameters is not None:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query, parameters)
        else:
            cur = cnx.cursor(dictionary=True)
            cur.execute(query)

        # Fetch one result
        row = cur.fetchall()
        cnx.commit()

        if "INSERT" in query:
            cur.execute("SELECT LAST_INSERT_ID()")
            row = cur.fetchall()
            cnx.commit()
        cur.close()
        cnx.close()
        return row

    def createTables(self, purge=False, data_path = 'flask_app/database/'):
        if purge:
            for table in reversed(self.tables):
                self.query("DROP TABLE IF EXISTS " + table)

        for table in self.tables:
            path_to_table = data_path + 'create_tables' + os.path.sep + table + '.sql'
            path_to_data  = data_path + 'initial_data' + os.path.sep + table + '.csv'

            try:
                table_file = open(path_to_table, 'r')
            except:
                print('Couldn\'t find SQL file for ' + table + ' table')
            else:
                with table_file: 
                    self.query(table_file.read())
                    try:
                        data_file = open(path_to_data, 'r')
                    except:
                        print('Couldn\'t load initial data for ' + table + ' table from path ' + path_to_data)
                    else:
                        with data_file:   
                            header = data_file.readline()
                            columns = [s[1:-1] for s in header.strip().split(',')]
                            
                            reader = csv.reader(data_file)
                            for row in reader:
                                row = [None if s == 'NULL' else s for s in row]
                                self.insertRows(table, columns, [row])            
            
    def insertRows(self, table='table', columns=['x','y'], parameters=[['v11','v12'],['v21','v22']]):
        # Check if there are multiple rows present in the parameters
        has_multiple_rows = any(isinstance(el, list) for el in parameters)
        keys, values      = ','.join(columns), ','.join(['%s' for x in columns])
        
        # Construct the query we will execute to insert the row(s)
        query = f"""INSERT IGNORE INTO {table} ({keys}) VALUES """
        if has_multiple_rows:
            for p in parameters:
                query += f"""({values}),"""
            query     = query[:-1] 
            parameters = list(itertools.chain(*parameters))
        else:
            query += f"""({values}) """                      
        
        insert_id = self.query(query,parameters)[0]['LAST_INSERT_ID()']         
        return insert_id

    def createBoard(self, board_name, owner, board_members):
        # Check if the board name is already in use
        board = self.query("SELECT * FROM boards WHERE board_name = %s", [board_name])
        if(len(board) > 0):
            return {'success': 0, 'message': 'The name ' + board_name + ' is already in use'}
        
        # Get the user_id of the owner user
        owner_id = self.query("SELECT user_id FROM users WHERE email = %s", [owner])[0]['user_id']
        board_id = self.insertRows('boards', ['board_name', 'owner_id'], [[board_name, owner_id]])

        # Always add the owner to the board
        self.insertRows('board_members', ['board_id', 'user_id'], [[board_id, owner_id]])

        # Add the rest of the members to the board
        for member in board_members:
            # Get the user_id of the member
            member_q = self.query("SELECT user_id FROM users WHERE email = %s", [member])
            if(len(member_q) == 0):
                print(member + " not found in users table, can't add to board")

                # Since there was an error, delete the board we just created, and return
                self.deleteBoard(board_id, self.getBoard(board_id)['owner'])
                return {'success': 0, 'message': 'User ' + member + ' not found'}

            # Don't double add the owner
            member_id = member_q[0]['user_id']
            if(member_id == owner_id):
                continue
            
            self.insertRows('board_members', ['board_id', 'user_id'], [[board_id, member_id]])

        return {"success": 1, "board_id": board_id }

    def getBoard(self, board_id):
        name = self.query("SELECT board_name FROM boards WHERE board_id = %s", [board_id])[0]['board_name']
        users = self.query("SELECT users.email FROM board_members INNER JOIN users ON users.user_id = board_members.user_id WHERE board_members.board_id = %s", [board_id])
        owner = self.query("SELECT users.email FROM boards INNER JOIN users ON users.user_id = boards.owner_id WHERE boards.board_id = %s", [board_id])[0]['email']
        todo_tasks = self.query("SELECT * FROM tasks WHERE board_id = %s AND status=%s", [board_id, "todo"])
        in_progress_tasks = self.query("SELECT * FROM tasks WHERE board_id = %s AND status=%s", [board_id, "in-progress"])
        done_tasks = self.query("SELECT * FROM tasks WHERE board_id = %s AND status=%s", [board_id, "done"])
        
        return {'board_id': board_id, 'name': name, 'owner': owner, 'users': users, 'todo_tasks': todo_tasks, 'in_progress_tasks': in_progress_tasks, 'done_tasks': done_tasks}

    def deleteBoard(self, board_id, user):
        if self.getBoard(board_id)['owner'] == user:
            self.query("DELETE FROM tasks WHERE board_id = %s", [board_id])
            self.query("DELETE FROM board_members WHERE board_id = %s", [board_id])
            self.query("DELETE FROM boards WHERE board_id = %s", [board_id])
            return {"success": 1}
        else:
            return {"success": 0, "message": "You are not authorized to delete this board"}

    def getUserBoards(self, user):
        user_id = self.query("SELECT user_id FROM users WHERE email = %s", [user])[0]['user_id']
        board_ids = self.query("SELECT board_id FROM board_members WHERE user_id = %s", [user_id])
        board_ids = [board_id['board_id'] for board_id in board_ids]

        return { board_id: self.getBoard(board_id) for board_id in board_ids }
    
    def is_board_member(self, user, board_id):
        user_id = self.query("SELECT user_id FROM users WHERE email = %s", [user])[0]['user_id']
        matching = self.query("SELECT * FROM board_members WHERE user_id = %s AND board_id = %s", [user_id, board_id])
        
        return len(matching) > 0    

    def createTask(self, board_id, task_name, task_description, task_status):
        task_id = self.insertRows('tasks', ['board_id', 'name', 'description', 'status'], [[board_id, task_name, task_description, task_status]])
        return {"success": 1, "task_id": task_id}

    def updateTask(self, task_id, task_name = None, task_description = None):
        if task_name is not None:
            self.query("UPDATE tasks SET name = %s WHERE task_id = %s", [task_name, task_id])
        if task_description is not None:
            self.query("UPDATE tasks SET description = %s WHERE task_id = %s", [task_description, task_id])

    def moveTask(self, task_id, new_status = None, after_task_id = None):
        if new_status is not None:
            self.query("UPDATE tasks SET status = %s WHERE task_id = %s", [new_status, task_id])

    def deleteTask(self, task_id):
        self.query("DELETE FROM tasks WHERE task_id = %s", [task_id])

#######################################################################################
# AUTHENTICATION RELATED
#######################################################################################
    def createUser(self, email='me@email.com', password='password', role='user'):
        # Check if user is already in the database
        user = self.query("SELECT * FROM users WHERE email = %s", [email])
        if user:
            return {'success': 0, 'message': 'User already exists'}
        else:
            self.insertRows(table='users', columns=['role', 'email', 'password'], parameters=[[role, email, self.onewayEncrypt(password)]])
            return {'success': 1}

    def authenticate(self, email='me@email.com', password='password'):
        user = self.query("SELECT * FROM users WHERE email = %s", [email])
        if not user:
            return {'success': 0, 'message': 'User does not exist'}

        user = self.query("SELECT * FROM users WHERE email = %s AND password = %s", (email, self.onewayEncrypt(password)))
        if not user:
            return {'success': 0, 'message': 'Incorrect password'}

        return {'success': 1}

    def onewayEncrypt(self, string):
        encrypted_string = hashlib.scrypt(string.encode('utf-8'),
                                          salt = self.encryption['oneway']['salt'],
                                          n    = self.encryption['oneway']['n'],
                                          r    = self.encryption['oneway']['r'],
                                          p    = self.encryption['oneway']['p']
                                          ).hex()
        return encrypted_string

    def reversibleEncrypt(self, type, message):
        fernet = Fernet(self.encryption['reversible']['key'])
        
        if type == 'encrypt':
            message = fernet.encrypt(message.encode())
        elif type == 'decrypt':
            message = fernet.decrypt(message).decode()

        return message


