from flask import Flask
from flask import Flask, render_template, Response, redirect, request, session, abort, url_for
import os
import base64
from PIL import Image
from datetime import datetime
from datetime import date
import datetime
import random
from random import seed
from random import randint

import cv2
import PIL.Image
from PIL import Image
from flask import send_file
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import csv
import threading
import time
import shutil
import hashlib
import urllib.request
import urllib.parse
from urllib.request import urlopen
import webbrowser
import json
import mysql.connector
from werkzeug.utils import secure_filename
import tensorflow as tf
from sklearn.metrics.pairwise import cosine_similarity

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  passwd="",
  charset="utf8",
  database="poisoning_attack"
)


app = Flask(__name__)
##session key
app.secret_key = 'abcdef'
UPLOAD_FOLDER = 'static/upload'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
#####

@app.route('/',methods=['POST','GET'])
def index():
    msg=""


    return render_template('index.html',msg=msg)

@app.route('/login',methods=['POST','GET'])
def login():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM pa_admin where username=%s && password=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('admin')) 
        else:
            msg="You are logged in fail!!!"
        

    return render_template('login.html',msg=msg,act=act)

@app.route('/login_user',methods=['POST','GET'])
def login_user():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM pa_user where uname=%s && pass=%s",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('userhome')) 
        else:
            msg="You are logged in fail!!!"
        

    return render_template('login_user.html',msg=msg,act=act)

@app.route('/login_trainer',methods=['POST','GET'])
def login_trainer():
    cnt=0
    act=""
    msg=""
    if request.method == 'POST':
        
        username1 = request.form['uname']
        password1 = request.form['pass']
        mycursor = mydb.cursor()
        mycursor.execute("SELECT count(*) FROM pa_trainer where uname=%s && pass=%s && dstatus<2",(username1,password1))
        myresult = mycursor.fetchone()[0]
        if myresult>0:
            session['username'] = username1

            ff=open("user.txt","w")
            ff.write(username1)
            ff.close()
            #result=" Your Logged in sucessfully**"
            return redirect(url_for('tr_home')) 
        else:
            msg="You are logged in fail!!!"
        

    return render_template('login_trainer.html',msg=msg,act=act)


#Blockchain
class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.chain = []
        self.nodes = set()

        # Create the genesis block
        self.new_block(previous_hash='1', proof=100)

    def register_node(self, address):
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')


    def valid_chain(self, chain):
        """
        Determine if a given blockchain is valid

        :param chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            last_block_hash = self.hash(last_block)
            if block['previous_hash'] != last_block_hash:
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof'], last_block_hash):
                return False

            last_block = block
            current_index += 1

        return True

    def resolve_conflicts(self):
        """
        This is our consensus algorithm, it resolves conflicts
        by replacing our chain with the longest one in the network.

        :return: True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    def new_block(self, proof, previous_hash):
        """
        Create a new Block in the Blockchain

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.chain[-1]),
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.chain.append(block)
        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined Block

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_block['index'] + 1

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a Block

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def proof_of_work(self, last_block):
        """
        Simple Proof of Work Algorithm:

         - Find a number p' such that hash(pp') contains leading 4 zeroes
         - Where p is the previous proof, and p' is the new proof
         
        :param last_block: <dict> last Block
        :return: <int>
        """

        last_proof = last_block['proof']
        last_hash = self.hash(last_block)

        proof = 0
        while self.valid_proof(last_proof, proof, last_hash) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof, last_hash):
        """
        Validates the Proof

        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Proof
        :param last_hash: <str> The hash of the Previous Block
        :return: <bool> True if correct, False if not.

        """

        guess = f'{last_proof}{proof}{last_hash}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

def mine():
    # We run the proof of work algorithm to get the next proof...
    last_block = blockchain.last_block
    proof = blockchain.proof_of_work(last_block)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the chain
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': "New Block Forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash'],
    }
    return jsonify(response), 200


def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201

def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200



def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201

def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200

def modelchain(uid,uname,bcdata,utype):
    ############

    now = datetime.datetime.now()
    yr=now.strftime("%Y")
    mon=now.strftime("%m")
    rdate=now.strftime("%d-%m-%Y")
    rtime=now.strftime("%H:%M:%S")
    
    ff=open("static/key.txt","r")
    k=ff.read()
    ff.close()
    
    #bcdata="CID:"+uname+",Time:"+val1+",Unit:"+val2
    dtime=rdate+","+rtime

    ff1=open("static/web/assets/js/d1.txt","r")
    bc1=ff1.read()
    ff1.close()
    
    px=""
    if k=="1":
        px=""
        result = hashlib.md5(bcdata.encode())
        key=result.hexdigest()
        print(key)
        v=k+"##"+key+"##"+bcdata+"##"+dtime

        ff1=open("static/web/assets/js/d1.txt","w")
        ff1.write(v)
        ff1.close()
        
        dictionary = {
            "ID": "1",
            "Pre-hash": "00000000000000000000000000000000",
            "Hash": key,
            "utype": utype,
            "Date/Time": dtime
        }

        k1=int(k)
        k2=k1+1
        k3=str(k2)
        ff1=open("static/key.txt","w")
        ff1.write(k3)
        ff1.close()

        ff1=open("static/prehash.txt","w")
        ff1.write(key)
        ff1.close()
        
    else:
        px=","
        pre_k=""
        k1=int(k)
        k2=k1-1
        k4=str(k2)

        ff1=open("static/prehash.txt","r")
        pre_hash=ff1.read()
        ff1.close()
        
        g1=bc1.split("#|")
        for g2 in g1:
            g3=g2.split("##")
            if k4==g3[0]:
                pre_k=g3[1]
                break

        
        result = hashlib.md5(bcdata.encode())
        key=result.hexdigest()
        

        v="#|"+k+"##"+key+"##"+bcdata+"##"+dtime

        k3=str(k2)
        ff1=open("static/key.txt","w")
        ff1.write(k3)
        ff1.close()

        ff1=open("static/web/assets/js/d1.txt","a")
        ff1.write(v)
        ff1.close()

        
        
        dictionary = {
            "ID": k,
            "Pre-hash": pre_hash,
            "Hash": key,
            "utype:": utype,
            "Date/Time": dtime
        }
        k21=int(k)+1
        k3=str(k21)
        ff1=open("static/key.txt","w")
        ff1.write(k3)
        ff1.close()

        ff1=open("static/prehash.txt","w")
        ff1.write(key)
        ff1.close()

    m=""
    if k=="1":
        m="w"
    else:
        m="a"
    # Serializing json
    
    json_object = json.dumps(dictionary, indent=4)
     
    # Writing to sample.json
    with open("static/modelchain.json", m) as outfile:
        outfile.write(json_object)
    ##########

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    msg=""
    mid=""
    mst=""
    mdata=[]
    mess=""
    act=request.args.get("act")
    mycursor = mydb.cursor(buffered=True)
    
    
    if request.method == 'POST':
        
        model = request.form['model']
        file = request.files['file']
        
        

        directory="static/dataset/"+model
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Directory '{directory}' created successfully.")
        else:
            print(f"Directory '{directory}' already exists.")


        mycursor.execute("SELECT max(id)+1 FROM pa_model")        
        maxid = mycursor.fetchone()[0]
        if maxid is None:
            maxid=1
        mid=str(maxid)
        fnn=secure_filename(file.filename)
        fn1="M"+str(maxid)+fnn
        file.save(os.path.join("static/dataset/"+model+"/", fn1))
        
        
        sql = "INSERT INTO pa_model(id,model,model_file) VALUES (%s, %s, %s)"
        val = (maxid,model,fn1)
        
        mycursor.execute(sql, val)
        mydb.commit()
        bcdata="ID:"+str(maxid)+", Model:"+model+", New model created, Model File:"+fn1
        modelchain(str(maxid),'admin',bcdata,'admin')
        msg="success"

    mycursor.execute("SELECT count(*) FROM pa_model")
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        mst="1"
        mycursor.execute("SELECT * FROM pa_model")
        mdata = mycursor.fetchall()
   
        
    return render_template('web/admin.html',msg=msg,mid=mid,mdata=mdata,mst=mst)

@app.route('/admin2', methods=['GET', 'POST'])
def admin2():
    msg=""
    mid=request.args.get("mid")
    bdata=[]
    mess=""
    mst=""
    act=request.args.get("act")
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM pa_model where id=%s",(mid,))
    mdata = mycursor.fetchone()
    model=mdata[1]

    lab_count=0
    mycursor.execute("SELECT count(*) FROM pa_label where mid=%s",(mid,))
    lab_count = mycursor.fetchone()[0]
    
    if request.method == 'POST':
      
        num_label=request.form['num_label']
        textbox_values = request.form.getlist('textboxes[]')
        
        vlen=len(textbox_values)

        num_label1=int(num_label)
        tot_lab=lab_count+num_label1
        bcdata="ID:"+mid+", Model:"+model+", Total Label Count:"+str(tot_lab)
        modelchain(mid,'admin',bcdata,'admin')
        j=1
        i=0
        while i<vlen:
            label_n=textbox_values[i]
            '''directory="static/dataset/"+model+"/"+label_n
            if not os.path.exists(directory):
                os.makedirs(directory)
                print(f"Directory '{directory}' created successfully.")
            else:
                print(f"Directory '{directory}' already exists.")'''

            mycursor.execute("SELECT max(id)+1 FROM pa_label")        
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            uid=str(maxid)
        
            sql = "INSERT INTO pa_label(id,mid,label_name) VALUES (%s, %s, %s)"
            val = (maxid,mid,textbox_values[i])
            
            mycursor.execute(sql, val)
            mydb.commit()

            lcc=lab_count+j
            
            bcdata="ID:"+str(maxid)+", Model:"+model+", Label created, Label("+str(lcc)+"):"+textbox_values[i]
            modelchain(str(maxid),'admin',bcdata,'admin')
            j+=1
            i+=1
        msg="success"

    mycursor.execute("SELECT count(*) FROM pa_label where mid=%s",(mid,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        mst="1"
        mycursor.execute("SELECT * FROM pa_label where mid=%s",(mid,))
        bdata = mycursor.fetchall()
        

    return render_template('web/admin2.html',msg=msg,mdata=mdata,bdata=bdata,mst=mst,mid=mid)

def calculate_hash(file_path):
    # Calculate the hash value of a file
    hasher = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while True:
            data = f.read(65536)  # Read the file in chunks to avoid loading it entirely into memory
            if not data:
                break
            hasher.update(data)
    return hasher.hexdigest()

@app.route('/admin3', methods=['GET', 'POST'])
def admin3():
    msg=""
    mid=request.args.get("mid")
    bid=request.args.get("bid")
    bdata=[]
    cdata=[]
    label_n=""
    
    mess=""
    mst=""
    act=request.args.get("act")
    mycursor = mydb.cursor(buffered=True)

    mycursor.execute("SELECT * FROM pa_model where id=%s",(mid,))
    mdata = mycursor.fetchone()
    model=mdata[1]

    mycursor.execute("SELECT * FROM pa_label where id=%s",(bid,))
    bb = mycursor.fetchone()
    label_n=bb[2]

    mycursor.execute("SELECT * FROM pa_label where mid=%s",(mid,))
    bdata = mycursor.fetchall()

    mycursor.execute("SELECT count(*) FROM pa_data where label_name=%s",(label_n,))
    ns1 = mycursor.fetchone()[0]
    
    
    if request.method == 'POST':
      
        #file = request.files['file']
        files = request.files.getlist('images')
        directory="static/dataset/"+model

        for file in files:
            
            if file and file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                mycursor.execute("SELECT max(id)+1 FROM pa_data")        
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1
                mmid=str(maxid)
                fnn=secure_filename(file.filename)
                fn1="F"+str(maxid)+fnn

                
                
                file.save(os.path.join("static/dataset/"+model, fn1))

                hash1 = calculate_hash("static/dataset/"+model+"/"+fn1)
                
                sql = "INSERT INTO pa_data(id,mid,bid,image_file,model,label_name,hash1,uname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)"
                val = (maxid,mid,bid,fn1,model,label_n,hash1,'admin')
                
                mycursor.execute(sql, val)
                mydb.commit()

                ns2=ns1+1
                bcdata="ID:"+str(maxid)+", Model:"+model+", Label:"+label_n+", Image("+str(ns2)+"):"+fn1+",Hash: "+hash1+", upload by Admin"
                modelchain(str(maxid),'admin',bcdata,'admin')
        msg="success"
        

    mycursor.execute("SELECT count(*) FROM pa_data where bid=%s",(bid,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        mst="1"
        mycursor.execute("SELECT * FROM pa_data where bid=%s",(bid,))
        cdata = mycursor.fetchall()
        

    return render_template('web/admin3.html',msg=msg,mdata=mdata,bdata=bdata,mst=mst,mid=mid,bid=bid,label_n=label_n,model=model,cdata=cdata)


#Self-Purified FL (SPFL) - (Label-Flipping Attacks)
def flip_labels(labels, num_classes=10):
    return (labels + 1) % num_classes

def create_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(10,)),
        tf.keras.layers.Dense(10, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Get model weights as a flat vector
def get_flat_weights(model):
    return np.concatenate([w.numpy().flatten() for w in model.trainable_weights])

# Set flat weights to a model
def set_flat_weights(model, flat_weights):
    shapes = [w.shape for w in model.trainable_weights]
    new_weights = []
    idx = 0
    for shape in shapes:
        size = np.prod(shape)
        new_weights.append(flat_weights[idx:idx + size].reshape(shape))
        idx += size
    model.set_weights(new_weights)

# SPFL: Filter
def detect_benign_clients(client_updates, threshold=0.85):
    reference = np.mean(client_updates, axis=0).reshape(1, -1)
    similarities = cosine_similarity(reference, client_updates)[0]
    return [i for i, sim in enumerate(similarities) if sim >= threshold]

def detection():
    # Parameters
    num_clients = 5
    num_malicious = 2
    rounds = 1

    # Federated Learning Rounds
    for r in range(rounds):
        client_updates = []

        for client_id in range(num_clients):
            # Simulate data
            x = np.random.rand(200, 10)
            y = np.random.randint(0, 10, size=(200,))

            if client_id < num_malicious:
                y = flip_labels(y)

            model = create_model()
            model.fit(x, y, epochs=1, verbose=0)

            update = get_flat_weights(model)
            client_updates.append(update)

        client_updates = np.array(client_updates)

        # SPFL Filtering
        benign_indices = detect_benign_clients(client_updates)
        print(f"Round {r+1} | Benign Trainer Detected: {benign_indices}")

        # Aggregate only benign updates
        if benign_indices:
            global_weights = np.mean(client_updates[benign_indices], axis=0)
            global_model = create_model()
            set_flat_weights(global_model, global_weights)

            # Optionally evaluate or save the model
            print("Global model updated using SPFL.")
        else:
            print("Warning: No benign trainer found!")

@app.route('/tr_home', methods=['GET', 'POST'])
def tr_home():
    msg=""
    mid=""
    mst=""
    st=""
    label=""
    mdata=[]
    mess=""
    bid=0
    wr_img=[]
    x=0
    act=request.args.get("act")
    model=request.args.get("model")
    mid=request.args.get("mid")
    mycursor = mydb.cursor()
    mid2=""
    label2=""
    
    uname=""
    if 'username' in session:
        uname = session['username']

    ff=open("user.txt","r")
    uname=ff.read()
    ff.close()
            
    mycursor.execute("SELECT * FROM pa_trainer where uname=%s",(uname,))
    usr = mycursor.fetchone()
    
    
    if request.method == 'POST':
      
        label=request.form['label']
        files = request.files.getlist('images')

        mycursor.execute("SELECT count(*) FROM pa_label where mid=%s && label_name=%s",(mid,label))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM pa_label")        
            maxid2 = mycursor.fetchone()[0]
            if maxid2 is None:
                maxid2=1
            maxid2=str(maxid2)
            bid=maxid2
            sql = "INSERT INTO pa_label(id,mid,label_name,uname) VALUES (%s, %s, %s,%s)"
            val = (maxid2,mid,label,uname)
            
            mycursor.execute(sql, val)
            mydb.commit()
        else:
            mycursor.execute("SELECT * FROM pa_label where mid=%s && label_name=%s",(mid,label))
            bd = mycursor.fetchone()
            bid=bd[0]
            
        
        for file in files:
            
            if file and file.filename.endswith(('.png', '.jpg', '.jpeg', '.gif')):
                #file_path = os.path.join(directory, file.filename)
                #os.makedirs(os.path.dirname(file_path), exist_ok=True)

                mycursor.execute("SELECT max(id)+1 FROM pa_data")        
                maxid = mycursor.fetchone()[0]
                if maxid is None:
                    maxid=1
                mmid=str(maxid)
                fnn=secure_filename(file.filename)
                fn1="F"+str(maxid)+fnn

                file.save(os.path.join("static/temp", fn1))
                hash1 = calculate_hash("static/temp/"+fn1)
                
                mycursor.execute("SELECT count(*) FROM pa_data where hash1=%s",(hash1,))
                cnt = mycursor.fetchone()[0]

                if cnt>0:
                    mycursor.execute("SELECT * FROM pa_data where hash1=%s",(hash1,))
                    dd3 = mycursor.fetchall()
                    for dd33 in dd3:
                        mid2=str(dd33[1])
                        label2=dd33[5]

                    print("#####")
                    print(mid)
                    print(label)

                    print("*****")
                    print(mid2)
                    print(label2)
                    
                    if mid==mid2 and label==label2:
                        st="1"
                    else:
                        x+=1
                        wr_img.append(fn1)
                        bcdata="ID:"+str(maxid)+", Model:"+model+", Label:"+label+",Label-Flipping Attack("+str(fn1)+"), Hash: "+hash1+", upload by "+uname
                        modelchain(str(maxid),uname,bcdata,'Attack')
                        st="2"
                        

                
                if x==0:
                    st="1"
                    shutil.copy("static/temp/"+fn1,"static/dataset/"+model+"/"+fn1)
                    os.remove("static/temp/"+fn1)
                    
                    sql = "INSERT INTO pa_data(id,mid,bid,image_file,model,label_name,hash1,uname) VALUES (%s, %s, %s,%s,%s,%s,%s,%s)"
                    val = (maxid,mid,bid,fn1,model,label,hash1,uname)
                    
                    mycursor.execute(sql, val)
                    mydb.commit()

                    bcdata="ID:"+str(maxid)+", Model:"+model+", Label:"+label+", Image:"+fn1+",Hash: "+hash1+", upload by "+uname
                    modelchain(str(maxid),uname,bcdata,'trainer')
                
                    
        if x>0:

            wrmg=",".join(wr_img)
            ff=open("static/wrong.txt","w")
            ff.write(wrmg)
            ff.close()

            msg="fail"
            
            '''mycursor.execute("update pa_trainer set dstatus=dstatus+1 where uname=%s",(uname,))
            mydb.commit()
            if usr[9]<2:
            
                if x>1:
                    msg="wrongs"
                else:
                    msg="wrong"
            else:
                bcdata="ID:"+str(usr[0])+", Model Trainer: "+uname+", Eliminated"
                modelchain(str(usr[0]),uname,bcdata,'trainer')
                msg="fail"'''
        else:
            msg="success"
    

    mycursor.execute("SELECT count(*) FROM pa_model")
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        mst="1"
        mycursor.execute("SELECT * FROM pa_model")
        mdata = mycursor.fetchall()
   
        
    return render_template('web/tr_home.html',msg=msg,act=act,mid=mid,mdata=mdata,mst=mst,model=model,label=label,st=st,wr_img=wr_img,uname=uname)


@app.route('/tr_home3', methods=['GET', 'POST'])
def tr_home3():
    msg=""
   
    mst=""
    st=""
    label=""
    mdata=[]
    mess=""
    bid=0
    data1=[]
    x=0
    act=request.args.get("act")
    model=request.args.get("model")
    label=request.args.get("label")
    mid=request.args.get("mid")
    mycursor = mydb.cursor()

    uname=""
    if 'username' in session:
        uname = session['username']

    ff=open("user.txt","r")
    uname=ff.read()
    ff.close()
    
    mycursor.execute("SELECT * FROM pa_trainer where uname=%s",(uname,))
    usr = mycursor.fetchone()

    mycursor.execute("SELECT * FROM pa_data where status=0 && uname=%s",(uname,))
    data1 = mycursor.fetchall()

    if request.method == 'POST':
        msg="train"

        mycursor.execute("update pa_data set status=1 where status=0 && uname=%s",(uname,))
        mydb.commit()

    
    
    
    return render_template('web/tr_home3.html',msg=msg,act=act,mid=mid,mdata=mdata,mst=mst,model=model,label=label,st=st,data1=data1)


@app.route('/tr_home4', methods=['GET', 'POST'])
def tr_home4():
    msg=""
   
    mst=""
    st=""
    label=""
    mdata=[]
    mess=""
    bid=0
    data1=[]
    x=0
    act=request.args.get("act")
    model=request.args.get("model")
    label=request.args.get("label")
    mid=request.args.get("mid")
    mycursor = mydb.cursor()

    uname=""
    if 'username' in session:
        uname = session['username']

    ff=open("user.txt","r")
    uname=ff.read()
    ff.close()
    
    mycursor.execute("SELECT * FROM pa_trainer where uname=%s",(uname,))
    usr = mycursor.fetchone()
    ds=usr[9]

    mycursor.execute("SELECT * FROM pa_data where status=0 && uname=%s",(uname,))
    data1 = mycursor.fetchall()

    ff=open("static/wrong.txt","r")
    ss=ff.read()
    ff.close()

    

    if act=="2":
        if ds==0:
            msg="f1"
            mycursor.execute("update pa_trainer set dstatus=dstatus+1 where uname=%s",(uname,))
            mydb.commit()
        elif ds==1:
            msg="f2"

            mycursor.execute("update pa_trainer set dstatus=dstatus+1 where uname=%s",(uname,))
            mydb.commit()
            bcdata="ID:"+str(usr[0])+", Model Trainer: "+uname+", Eliminated"
            modelchain(str(usr[0]),uname,bcdata,'Eliminated')
        

    data1=ss.split(",")
    
    return render_template('web/tr_home4.html',msg=msg,act=act,mid=mid,mdata=mdata,mst=mst,model=model,label=label,st=st,data1=data1)


@app.route('/tr_home2', methods=['GET', 'POST'])
def tr_home2():
    msg=""
    mid=""
    mst=""
    st=""
    model=request.args.get("model")
    label=request.args.get("label")
    mdata=[]
    mess=""
    bid=0
    adata=[]
    x=0
    act=request.args.get("act")
    mid=request.args.get("mid")
    mycursor = mydb.cursor()

    uname=""
    if 'username' in session:
        uname = session['username']

    ff=open("user.txt","r")
    uname=ff.read()
    ff.close()
    
    mycursor.execute("SELECT * FROM pa_trainer where uname=%s",(uname,))
    usr = mycursor.fetchone()
    
    
 
    mycursor.execute("SELECT count(*) FROM pa_data where uname=%s",(uname,))
    cnt = mycursor.fetchone()[0]
    if cnt>0:
        mst="1"

        mycursor.execute("SELECT * FROM pa_model")
        m1 = mycursor.fetchall()
        for m11 in m1:
            dt=[]
            dtt=[]
            mycursor.execute("SELECT count(*) FROM pa_data where model=%s && uname=%s",(m11[1],uname))
            m2 = mycursor.fetchone()[0]
            if m2>0:
                dt.append(m11[1])

                mycursor.execute("SELECT count(*) FROM pa_label where mid=%s",(m11[0],))
                m3 = mycursor.fetchone()[0]
                if m3>0:
                
                    mycursor.execute("SELECT * FROM pa_label where mid=%s",(m11[0],))
                    m4 = mycursor.fetchall()
                    for m44 in m4:
                        
                        mycursor.execute("SELECT count(*) FROM pa_data where model=%s && label_name=%s && uname=%s",(m11[1],m44[2],uname))
                        m5 = mycursor.fetchone()[0]
                        if m5>0:
                            dtt.append(m44[2])
                dt.append(dtt)
                mdata.append(dt)
                
    if act=="model":
        mycursor.execute("SELECT * FROM pa_data where model=%s && label_name=%s && uname=%s",(model,label,uname))
        adata = mycursor.fetchall()
   
        
    return render_template('web/tr_home2.html',msg=msg,act=act,mid=mid,mdata=mdata,mst=mst,model=model,st=st,adata=adata,label=label)


@app.route('/userhome', methods=['GET', 'POST'])
def userhome():
    msg=""
    mid=""
    mst=""
    st=""
    fnn=""
    model=request.args.get("model")
    label=""
    mdata=[]
    mess=""
    bid=0
    adata=[]
    x=0
    act=request.args.get("act")
    mid=request.args.get("mid")
    mycursor = mydb.cursor()

    uname=""
    if 'username' in session:
        uname = session['username']

    mycursor.execute("SELECT * FROM pa_user where uname=%s",(uname,))
    usr = mycursor.fetchone()
    
    if request.method == 'POST':
      
        file = request.files['file']
        fnn=secure_filename(file.filename)
        file.save(os.path.join("static/test", fnn))

        hash1 = calculate_hash("static/test/"+fnn)

        mycursor.execute("SELECT count(*) FROM pa_data where hash1=%s",(hash1,))
        cnt = mycursor.fetchone()[0]

        if cnt>0:
            st="1"
            msg="success"
            mycursor.execute("SELECT * FROM pa_data where hash1=%s",(hash1,))
            dd = mycursor.fetchall()
            for d1 in dd:
                label=d1[5]

            bcdata="ID:"+str(usr[0])+", Username:"+uname+",File:"+fnn+", Hash:"+hash1+", Predicted Label: "+label
            modelchain(str(usr[0]),'admin',bcdata,'trainer')
        else:
            st="1"
            bcdata="ID:"+str(usr[0])+", Username:"+uname+",File:"+fnn+", Hash:"+hash1+", Not Predicted"
            modelchain(str(usr[0]),'admin',bcdata,'trainer')
            msg="fail"
                
                        
    return render_template('web/userhome.html',msg=msg,act=act,mid=mid,mdata=mdata,label=label,st=st,fnn=fnn,uname=uname)





@app.route('/view_user', methods=['GET', 'POST'])
def view_user():
    value=[]
    mycursor = mydb.cursor()
    mycursor.execute("SELECT * FROM cc_register")
    data = mycursor.fetchall()

    
    return render_template('view_user.html', data=data)



@app.route('/reg_trainer',methods=['POST','GET'])
def reg_trainer():
    msg=""
    act=""
    mycursor = mydb.cursor()
    name=""
    mobile=""
    mess=""
    uid=""

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    if request.method=='POST':
        
        uname=request.form['uname']
        name=request.form['name']     
        mobile=request.form['mobile']
        email=request.form['email']
        location=request.form['location']
        pass1=request.form['pass']

        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM pa_trainer where uname=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM pa_trainer")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            
            uid=str(maxid)
            sql = "INSERT INTO pa_trainer(id, name, mobile, email, location,uname, pass,create_date) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
            val = (maxid, name, mobile, email, location, uname, pass1,rdate)
            msg="success"
            mycursor.execute(sql, val)
            mydb.commit()            
            #print(mycursor.rowcount, "record inserted.")
            bcdata="ID:"+str(maxid)+", Username:"+uname+", New Model Trainer Registered"
            modelchain(str(maxid),'admin',bcdata,'trainer')
           
        else:
            msg="fail"
            
    return render_template('reg_trainer.html',msg=msg,mobile=mobile,name=name,mess=mess,uid=uid)



@app.route('/register',methods=['POST','GET'])
def register():
    msg=""
    act=""
    mycursor = mydb.cursor()
    name=""
    mobile=""
    mess=""
    uid=""

    now = datetime.datetime.now()
    rdate=now.strftime("%d-%m-%Y")
        
    if request.method=='POST':
        
        uname=request.form['uname']
        name=request.form['name']     
        mobile=request.form['mobile']
        email=request.form['email']
        location=request.form['location']
        pass1=request.form['pass']

        
        now = datetime.datetime.now()
        rdate=now.strftime("%d-%m-%Y")
        mycursor = mydb.cursor()

        mycursor.execute("SELECT count(*) FROM pa_user where uname=%s",(uname, ))
        cnt = mycursor.fetchone()[0]
        if cnt==0:
            mycursor.execute("SELECT max(id)+1 FROM pa_user")
            maxid = mycursor.fetchone()[0]
            if maxid is None:
                maxid=1
            
            uid=str(maxid)
            sql = "INSERT INTO pa_user(id, name, mobile, email, location,uname, pass,create_date) VALUES (%s, %s, %s, %s, %s, %s, %s,%s)"
            val = (maxid, name, mobile, email, location, uname, pass1,rdate)
            msg="success"
            mycursor.execute(sql, val)
            mydb.commit()            
            print(mycursor.rowcount, "record inserted.")
            bcdata="ID:"+str(maxid)+", Username:"+uname+", New Model User Registered"
            modelchain(str(maxid),'admin',bcdata,'user')
        else:
            msg="fail"
            
    return render_template('register.html',msg=msg,mobile=mobile,name=name,mess=mess,uid=uid)


@app.route('/view_block', methods=['GET', 'POST'])
def view_block():
    msg=""
    cnt=0
    uname=""
    data1=[]
    mess=""
    act=request.args.get("act")

    if act=="1":
        ff=open("static/modelchain.json","r")
        fj=ff.read()
        ff.close()

        fjj=fj.split('}')

        nn=len(fjj)
        nn2=nn-2
        i=0
        fsn=""
        while i<nn-1:
            if i==nn2:
                fsn+=fjj[i]+"}"
            else:
                fsn+=fjj[i]+"},"
            i+=1
            
        #fjj1='},'.join(fjj)
        
        fj1="["+fsn+"]"
        

       

    ################
    
    if act=="11":
        if request.method=='POST':
            
            fname=request.form['getval']

            s1="1"
            ff=open("static/web/assets/js/d1.txt","r")
            ds=ff.read()
            ff.close()

            drow=ds.split("#|")
            
            i=0
            for dr in drow:
                
                dr1=dr.split("##")
                dt=[]

                if fname in dr1[2]:
                    dt.append(dr1[0])
                    dt.append(dr1[1])
                    dt.append(dr1[2])
                    dt.append(dr1[3])
                    #dt.append(dr1[4])
                    if "File Modified" in dr1[2] or "File Deleted" in dr1[2] or "File Moved" in dr1[2] or "File Created" in dr1[2]:
                        dt.append("2")
                    elif "File Accessed" in dr1[2]:
                        dt.append("3")
                    else:
                        dt.append("1")
                    data1.append(dt)

        else:
            s1="1"
            ff=open("static/web/assets/js/d1.txt","r")
            ds=ff.read()
            ff.close()

            drow=ds.split("#|")
            
            i=0
            for dr in drow:
                
                dr1=dr.split("##")
                dt=[]
                #if "Register" in dr1[2]:
                
                    
                    
                dt.append(dr1[0])
                dt.append(dr1[1])
                dt.append(dr1[2])
                dt.append(dr1[3])
                #dt.append(dr1[4])
                if "Attack" in dr1[2] or "Eliminated" in dr1[2]:
                    dt.append("2")
                elif "File Accessed" in dr1[2]:
                    dt.append("3")
                else:
                    dt.append("1")
                data1.append(dt)
    else:
        ff=open("static/web/assets/js/d1.txt","r")
        ds=ff.read()
        ff.close()

        drow=ds.split("#|")
        
        i=0
        for dr in drow:
            
            dr1=dr.split("##")
            dt=[]
            #if "Register" in dr1[2]:
                
            dt.append(dr1[0])
            dt.append(dr1[1])
            dt.append(dr1[2])
            dt.append(dr1[3])
            #dt.append(dr1[4])
            data1.append(dt)
        
    
    return render_template('web/view_block.html',msg=msg,act=act,data1=data1)


@app.route('/down', methods=['GET', 'POST'])
def down():
    fn = request.args.get('fname')
    path="static/upload/"+fn
    return send_file(path, as_attachment=True)

@app.route('/logout')
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True,host='0.0.0.0', port=5000)
