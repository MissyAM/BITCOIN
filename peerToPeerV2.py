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
from sha256 import*

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
            self.address = "14889ac1693947cc8cad59cec310560b57a77dc6b755319a51c670a063a49b1f" 

        if self.beneficiary=="Bob":
            self.address = "19691aa608398c56e64468b069004b3c543eb78d7756ef4d1a575e58cda97905"

        if self.beneficiary=="Alice":
            self.address = "020d4ef48c4af43a76963d77b96618942c81871a3db7447780251286869d2aed"

        if self.beneficiary=="Nelson":
            self.address = "3eab8ab3a49ca1e5cf28ee110e349b58c7ff53548ff529bef985480c51ea3a9b"

        if self.beneficiary=="Claus":
            self.address = "e13a1a83809475513524ef90b5394bda1ddfad0245cf42e24457a34f440ee8c4"
        return self.address

    def get_bitcoin_address(self,public_key):

        self.x, self.y = public_key
        s = (str(hex(self.x)),str(hex(self.y)))
        self.string_to_decode =  ''.join(s)
        self.address= sha256_algorithm( self.string_to_decode)

        return str(self.address)
        
    def get_records(self,sender):

        self.db = dataset.connect('sqlite:///mydatabase.db')

        self.table = self.db['blockchain']

        self.source = '5dce3d13150c34cd4d06678a0e66e21141a365f5da4082da0b913c9fe275710a'

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
    
               
