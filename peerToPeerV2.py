import socket
import time
import threading
import sys
import time
from random import randint
import json
from MerkelTree import*
from ellipticCurveCrypto import*
import dataset
import time

class Server:
    connections = []
    peers = []
    def __init__(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('0.0.0.0',10024))
        s.listen(1)
        while True:
            c , a = s.accept()
            ciThread = threading.Thread(target=self.sendServer , args=(c , ))
            ciThread.daemon = True
            ciThread.start()
            cThread = threading.Thread(target=self.handler , args=(c,a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            self.peers.append(a[0])
            print(str(a[0]) + ':' +str(a[1]))
        self.sendPeers()
    def sendServer(self,c):
        while True:
            self.prepareServer = PrepareTransactions()
            self.prepareServer.prepareTransactions()
            message = input("")
            if message == "y":
                m = self.prepareServer.finalBlock
                n = json.dumps(m).encode('utf-8')
                s.send(bytes(n))
            m = input("message to send")
            print("sent" + m )
            ni = json.dumps(m).encode('utf-8')
            for connection in self.connections:
                connection.send(bytes(ni)) 

    def handler(self,c,a):
        while True:
            data = c.recv(1024)
            if data != ' ':
                k= bytearray()
                k+=data
                print("received" + str(json.loads(k.decode('utf-8'))))
                for connection in self.connections:
                    connection.send(bytes(data))
            if not data:
                print(str(a[0]) + ':' +str(a[1]))
                self.connections.remove(c)
                self.peers.remove(a[0])
                c.close()
                self.sendPeers()
                break
    def sendPeers(self):
        p = ""
        for peer in self.peers:
            p = p + str(peer + ",")
        for connection in self.connections:
            connection.send(b'\x11' + str(p))
##Prepare the transactions to be sent-------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            
class PrepareTransactions:
            
    def prepareTransactions(self):
        self.transactions = {}
        self.transactionsHashes = []
        self.amount = input("Enter  amount of the transaction")
        self.beneficiary = input("Enter the name of the beneficiary")
        self.transactions[self.beneficiary] = self.amount
        for j in self.transactions:
            lineCode = str( self.transactions[j] + 'to:' + j).encode()
            hasher = hashlib.sha256(lineCode)
            self.transactionsHashes.append(hasher.hexdigest())
            merkelroot = MerkelRoot()
        self.root = merkelroot.find_merkel_tree(self.transactionsHashes)
        self.private, self.public = make_keypair()
##Connection to the database
        self.sender_address = self.get_bitcoin_address(self.public)
        self.totalAmount , self.previous = self.get_records(self.sender_address)
        if int(self.amount) > self.totalAmount:
            print("Your balance is not sufficient")
            self.prepareTransactions()
        else:
            self.change = self.totalAmount-int(self.amount)
            self.intermediate =   dict({'merkelRoot': self.root,
                    'publicKey': self.public,
                    'beneficiary': self.get_beneficiary_address(self.beneficiary),           
                    'previousBlock': self.previous,
                    'transactions': self.transactions,
                    'change': self.change,
                    'target':5,
                    'nonce':4
                           })
            self.intermediateString = (str('MerkelRoot:' + str(self.intermediate['merkelRoot']) + 'Public:' + str(self.intermediate['publicKey']) + 'previous:' + str(self.intermediate['previousBlock']) + 'Transactions:' + str(self.intermediate['transactions'])+ 'Target:' + str(self.intermediate['target']) + 'Nonce:' + str(self.intermediate['nonce']))).encode('utf-8')
            self.signed = sign_message(self.private, self.intermediateString)
            self.publicKey = {'public' : self.public}
            self.finalBlock = dict({'original': str(self.intermediateString),
                    'publicKey': self.publicKey,
                    'beneficiary': self.get_beneficiary_address(self.beneficiary),
                    'sender_address': self.sender_address,
                    'previousBlock': self.previous,
                    'change' : self.change,
                    'signed': self.signed,
                    'transactions': self.transactions,
                    'coinbase':' ',
                    'target':5,
                    'nonce':4
                           })
        
    def get_beneficiary_address(self,beneficiary):
        if self.beneficiary=="Tom":
            self.address = "67e518b95c263c72bf8c9df125e2b7262bfec2b495b8d6db49919333a0f0d169cbce4560d7ba99a8172aae38775d372de00a9d6edb9a26066ff0d4870a18c989" 

        if self.beneficiary=="Bob":
            self.address = "931da0c0a69d7ce04a00a878dbb799cf784491e77e9fc5ca4fa636fc4a6053ceb5e3451689efd6ea32eb96956af6d374533d0901234852dc6f3c44f0e18cbf21"

        if self.beneficiary=="Alice":
            self.address = "2bc9bfec736d7036c41ea104e4c89ed46acbd5e7fed149c9209ad492f5821d240f3273de7ce3da936b05f6b7e3e15939956a76e9a7cf710bbaf50db348ac0f2a"

        if self.beneficiary=="Nelson":
            self.address = "e2819fdfa8449ad4c37278d115681ff43d35652ac588bbe3a7b057d17441b512b7b2c57d84af26a6cf0d970f53c5ede108a6686b43349b578dcd1ad7dbf9da9d"

        if self.beneficiary=="Claus":
            self.address = "82fb387f5c0cbc703477b7398ec119876634641463e864f4011979723505ddbaef82656f89ba14c45fb01d7cfe65fa268c380e40724080b446e29c722c31db93"
        return self.address

    def get_bitcoin_address(self,public_key):

        self.x, self.y = public_key
        s = (hex(self.x),hex(self.y))
        self.string_to_decode =  ''.join(s)
        self.new_key = str(self.string_to_decode[2:]).encode()
        self.new_hash = hashlib.sha512(self.new_key)
        self.address= self.new_hash.hexdigest()

        return str(self.address)
        
    def get_records(self,sender):

        self.db = dataset.connect('sqlite:///mydatabase.db')

        self.table = self.db['blockchain']

        self.source = 'c90d64e0edbe4600b374ee677305482870ad596ea887a7233ef7822938717d38caa0396eeb2381dd1dd736914c40f8e3eca8e879ff9653919c25e90abe80fd99'

        self.result = self.db.query("SELECT* FROM blockchain WHERE (source = '"+self.source+"' OR source = '"+sender+"' ) AND beneficiary = '"+sender+"'")
        self.listId = []
        self.listPrevious_hash = []
        self.total = 0
        self.last_index = 0
        for row in self.result:
            self.listId.append(row['id'])
        if len(self.listId) == 1:
            self.last_index =  self.listId[0]
        else:
            largest = 0
            for i in range(0 , len(self.listId)):
                if i > i+1:
                    largest = i
                else:
                    largest = i+1
                
            self.last_index = largest

        self.queryRecords = self.db.query(" SELECT* FROM blockchain WHERE beneficiary = '"+sender+"'")

        for row in self.queryRecords:
            if row['id'] >= self.last_index and row['bitcoin'] > 0:
                self.total += row['bitcoin']
                line = str(str(row['source']) + str(row['beneficiary']) + str(row['previousHash']) + str(row['merkelRoot']) + str(row['timestamp']) + str(row['bitcoin']))
                hash_block = line.encode()
                block_hash = hashlib.sha512(hash_block)
                self.listPrevious_hash.append(block_hash.hexdigest())
            else:

                print("No records")
        return self.total , self.listPrevious_hash
            
            
##The client Class--------------------------------------------------------------------------------------------------------------------------------------------------------------------

class Client:
    def sendMsg(self,s):
        while True:
            self.prepare = PrepareTransactions()
            self.prepare.prepareTransactions()
            message = input("")
            if message == "y":
                m = self.prepare.finalBlock
                n = json.dumps(m).encode('utf-8')
                s.send(bytes(n))
    def __init__(self,address):
       s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
       s.connect((address,10024))
       iThread = threading.Thread(target=self.sendMsg , args=(s, ))
       iThread.deamon =True
       iThread.start()
       while True:
           data = s.recv(1024)
           if not data:
               break
           if data[0:1] == b'\x11':
               self.updatePeers(data[1:])
           else:
##               d = json.loads(data.decode('utf-8'))
               b= bytearray() 
               b+= data
               print(str(json.loads(b.decode('utf-8'))))

    def updatePeers(self,peerData):
        p2p.peers = str(peerData).split(",")[:-1]

class p2p:
    peers = ['127.0.0.1']

while True:
    try:
        
        print("Trying to connect")
        time.sleep(randint(1,5))
        for peer in p2p.peers:
            
            try:
                client = Client(peer)
            except KeyboardInterrupt:
                sys.exit(0)
            except:
                pass
            if randint(1,20)==1:
                
                try:
                    server = Server()
                except KeyboardInterrupt:
                    sys.exit(0)
                except:
                    print("Couldnt connect to server")
  
    except KeyboardInterrupt:
                   sys.exit(0)
    
               
