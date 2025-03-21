
import threading
import socket
import json
from pyperclip import copy,paste
import argparse

import os

"""
For clipboard:
On Linux, install xclip, xsel, or wl-clipboard (for "wayland" sessions) via package manager.
For example, in Debian:
    sudo apt-get install xclip
    sudo apt-get install xsel
    sudo apt-get install wl-clipboard
"""
try:
    os.system('title g++')
except Exception as e:
    print('Error occured while setting title: ', e)
    pass

def get_clipboard():
    try:
        return paste()
    except Exception as e:
        print("Clipboard paste failed: ", e)
        return None
    
def set_clipboard(data):
    try:
        copy(data)
    except Exception as e:
        print("Clipboard copy failed: ", e)

class MesssageType:
    JOIN = 1
    LEAVE = 2
    TEXT = 3
    FILE = 4
    PARTIAL_FILE = 5
    END_FILE = 6


snippets = {
    # keys should be in lowercase
}


class Message:
    def __init__(self, sender, content, message_type: MesssageType,file_name=None,seq=0) -> None:
        self.sender = sender
        self.content = content
        self.message_type = message_type
        self.file_name = file_name
        self.seq = seq

    def __str__(self) -> str:
        return f'{self.sender} - {self.content}'

    def __repr__(self) -> str:
        return f'{self.sender} - {self.content}'

    def to_json(self):
        return json.dumps({
            'sender': self.sender,
            'content': self.content,
            'message_type': self.message_type,
            'file_name': self.file_name,
            'seq': self.seq
        })

    @staticmethod
    def from_json(data):
        data = json.loads(data)
        return Message(data['sender'], data['content'], data['message_type'], data.get('file_name', None), data.get('seq', 0))

class Peer:
    def __init__(self, host = '0.0.0.0', port = 12345) -> None:
        self.peerlist = dict()
        self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.port = port
        self.server.bind((host, self.port))
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        # Increase the send buffer size
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
        
        # Increase the receive buffer size
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        self.Sender_thread = threading.Thread(target=self.Sender,daemon=True)
        self.name = input('Enter your name: ')
        self.send_data(self.name, MesssageType.JOIN)
        self.run = True
        #Get address of the peer
        self.ip = socket.gethostbyname(socket.gethostname())
        print(f'Your IP Address is: {self.ip}')
        self.Sender_thread.start()
        self.listen()

    def Sender(self):
        while self.run:
            try:
                msg = input(':> ')
            except:
                print('Error occured while sending message')
                self.run = False
                break
            if msg == 'exit':
                self.send_data(self.name, MesssageType.LEAVE)
                self.server.close()
                break
            if msg == 'list':
                print(self.peerlist)
            elif msg in ['paste', 'p']:
                data = get_clipboard()
                if data:
                    self.send_data(data, MesssageType.TEXT)
            elif msg == 'cls':
                os.system('cls')
            elif msg in ['snippets', 's']:
                snippet_indexing = {i: key for i, key in enumerate(snippets.keys())}
                for i, key in snippet_indexing.items():
                    print(f'{i}. {key}')
                try:
                    required_snippet = int(input('Enter the snippet number: '))
                except:
                    print('Invalid input')
                    continue
                try:
                    snippet = snippets[snippet_indexing[required_snippet]]
                    print(snippet)
                except:
                    print('Invalid snippet number')

            elif msg.startswith('file'):
                filename = msg.split(' ')[1]
                self.send_data(filename, MesssageType.FILE)
            elif msg in ('help', 'h'):
                print("""
Commands:
1. list: List all the peers
2. paste - p: Send clipboard data
3. cls: Clear the screen
4. snippets - s: List all the snippets
5. file <filename>: Send file (alpha)
                """
                )
            else:
                self.send_data(msg, MesssageType.TEXT)
            


    def listen(self):
        file_data = dict()
        while self.run:
            try:
                data, addr = self.server.recvfrom(65536)
            except socket.error as e:
                print(e)
                break
            except KeyboardInterrupt:
                print('Keyboard Interrupt')
                self.run = False
                break
            message = Message.from_json(data)
            
            if addr[0] == self.ip:
                continue
            
            elif message.message_type == MesssageType.JOIN:
                name = message.content
                if addr not in self.peerlist:
                #self.server.sendto(f'join:{self.name}'.encode(), addr)
                    print(f'{name} joined the chat')
                    self.send_data(self.name, MesssageType.JOIN)
                    self.peerlist[addr] = name
            elif message.message_type == MesssageType.PARTIAL_FILE:
                if message.file_name not in file_data:
                    file_data[message.file_name] = dict()
                file_data[message.file_name][message.seq] = message.content
                
            elif message.message_type == MesssageType.END_FILE:
                keys = list(file_data[message.file_name].keys())
                keys.sort()
                with open(self.name+message.file_name, 'w') as file:
                    for key in keys:
                        file.write(file_data[message.file_name][key])
                    
                print(f'File {message.file_name} received')
            elif message.message_type == MesssageType.LEAVE:
                name = message.content
                print(f'{name} left the chat')
                self.peerlist.pop(addr)
            else:
                print(f"{message.sender}:{message.content}")

    def send_msg(self, data):
        self.server.sendto(data.encode(), ('255.255.255.255', 12345))
        

    def send_data(self, content, message_type: MesssageType):
        
        if message_type == MesssageType.TEXT:
            message = Message(self.name, content, message_type)
        elif message_type == MesssageType.FILE:
            with open(content, 'r') as file:
                seq = 0
                data = file.read(100)
                while data:
                    message = Message(self.name, data, MesssageType.PARTIAL_FILE, content,seq)
                    seq+=1
                    self.send_msg(message.to_json())
                    data = file.read(100)

                message = Message(self.name, '', MesssageType.END_FILE, content)
                
        else:
            message = Message(self.name, content, message_type)
        self.send_msg(message.to_json())
        
        
        





snippets['tcp multithreaded'] = r"""
# server.py
import socket
import threading

def handle_client(client_socket, address):
   
    print(f"New connection from {address}")
    try:
        # Receive first number
        num1 = int(client_socket.recv(1024).decode())
        # Send acknowledgment
        client_socket.send("Received first number".encode())
        
        # Receive second number
        num2 = int(client_socket.recv(1024).decode())
        
        # Process the numbers (in this case, add them and multiply them)
        sum_result = num1 + num2
        product_result = num1 * num2
        
        # Send back the results
        response = f"Sum: {sum_result}, Product: {product_result}"
        client_socket.send(response.encode())
        
    except Exception as e:
        print(f"Error handling client {address}: {e}")
    finally:
        client_socket.close()
        print(f"Connection from {address} closed")

def start_server():
    
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Allow port reuse
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    # Bind to localhost port 5555
    server_socket.bind(('localhost', 5555))
    
    # Listen for incoming connections
    server_socket.listen(5)
    print("Server is listening on localhost:5555")
    
    try:
        while True:
            # Accept new connection
            client_socket, address = server_socket.accept()
            
            # Create new thread to handle client
            client_thread = threading.Thread(
                target=handle_client,
                args=(client_socket, address)
            )
            client_thread.daemon = True
            client_thread.start()
            
    except KeyboardInterrupt:
        print("\nShutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()

# client.py
import socket

def start_client():
   
    # Create client socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to server
        client_socket.connect(('localhost', 5555))
        
        # Get first number from user
        num1 = input("Enter first number: ")
        client_socket.send(num1.encode())
        
        # Wait for server acknowledgment
        print(client_socket.recv(1024).decode())
        
        # Get second number from user
        num2 = input("Enter second number: ")
        client_socket.send(num2.encode())
        
        # Receive and print results
        result = client_socket.recv(1024).decode()
        print("Server response:", result)
        
    except ConnectionRefusedError:
        print("Could not connect to server. Is it running?")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()
"""

snippets ['DFS'] = r"""" \
def dfs(graph, start, goal, path=None, visited=None):
    if path is None:
        path = [start]
    if visited is None:
        visited = set()
    visited.add(start)
    
    if start == goal:
        return path

    for neighbor in graph.get(start, []):
        if neighbor not in visited:
            result = dfs(graph, neighbor, goal, path + [neighbor], visited)
            if result is not None:
                return result
    return None

# Example graph as an adjacency list
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}

print("DFS path:", dfs(graph, 'A', 'F'))

""" \

snippets['BFS'] = r"""" \

from collections import deque

def bfs(graph, start, goal):
    queue = deque([[start]])
    visited = set([start])
    
    while queue:
        path = queue.popleft()
        node = path[-1]
        if node == goal:
            return path
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                visited.add(neighbor)
                new_path = list(path)
                new_path.append(neighbor)
                queue.append(new_path)
    return None

print("BFS path:", bfs(graph, 'A', 'F'))

""" \

snippets['Iterative IDS'] = r"""" \" \
    def depth_limited_search(graph, current, goal, limit, path):
    if current == goal:
        return path
    if limit <= 0:
        return None
    for neighbor in graph.get(current, []):
        if neighbor not in path:  # avoid cycles
            result = depth_limited_search(graph, neighbor, goal, limit - 1, path + [neighbor])
            if result is not None:
                return result
    return None

def ids(graph, start, goal, max_depth=10):
    for depth in range(max_depth):
        result = depth_limited_search(graph, start, goal, depth, [start])
        if result is not None:
            return result
    return None

print("IDS path:", ids(graph, 'A', 'F'))
" 
""" \

snippets ['uniform cost search'] = r"""" \" \
    import heapq

def ucs(graph, start, goal):
    # Priority queue holds tuples of (cost, path)
    queue = [(0, [start])]
    visited = {}
    
    while queue:
        cost, path = heapq.heappop(queue)
        node = path[-1]
        if node == goal:
            return path, cost
        if node in visited and visited[node] <= cost:
            continue
        visited[node] = cost
        
        for neighbor, weight in graph.get(node, []):
            new_cost = cost + weight
            new_path = path + [neighbor]
            heapq.heappush(queue, (new_cost, new_path))
    return None

# Example weighted graph (each neighbor is (node, weight))
weighted_graph = {
    'A': [('B', 1), ('C', 4)],
    'B': [('D', 2), ('E', 5)],
    'C': [('E', 1)],
    'D': [('F', 3)],
    'E': [('F', 1)],
    'F': []
}

result = ucs(weighted_graph, 'A', 'F')
if result:
    path, cost = result
    print("UCS path:", path, "with total cost:", cost)
   """ \

snippets ['hill climbing Search'] = r""" \
def hill_climbing(start_state, get_neighbors, evaluate):
    current = start_state
    while True:
        neighbors = get_neighbors(current)
        # Choose the neighbor with the best evaluation (assume higher is better)
        next_state = max(neighbors, key=evaluate, default=None)
        if next_state is None or evaluate(next_state) <= evaluate(current):
            break  # No improvement found
        current = next_state
    return current

# Example: maximizing a simple function f(x) = -(x-5)^2 + 25
def get_neighbors(x):
    return [x - 1, x + 1]

def evaluate(x):
    return -(x - 5) ** 2 + 25

start = 0
result = hill_climbing(start, get_neighbors, evaluate)
print("Hill Climbing result:", result, "with value:", evaluate(result))" \
"""\

snippets ['Best First Search'] = r"""" \
    
def best_first_search(start, goal, get_neighbors, heuristic):
    # Priority queue ordered by heuristic value (lower is better)
    from heapq import heappush, heappop
    queue = []
    heappush(queue, (heuristic(start, goal), [start]))
    visited = set()
    
    while queue:
        h_val, path = heappop(queue)
        current = path[-1]
        if current == goal:
            return path
        if current in visited:
            continue
        visited.add(current)
        for neighbor in get_neighbors(current):
            if neighbor not in visited:
                new_path = path + [neighbor]
                heappush(queue, (heuristic(neighbor, goal), new_path))
    return None

# Example heuristic: straight-line distance in a 1D space (absolute difference)
def heuristic(node, goal):
    return abs(goal - node)

def get_neighbors_1d(x):
    return [x - 1, x + 1]

print("Best First Search path:", best_first_search(0, 10, get_neighbors_1d, heuristic))
"""\

snippets ['A* algo'] = r"""" \
def a_star_search(start, goal, get_neighbors, heuristic, cost_function):
    from heapq import heappush, heappop
    # Each element in the queue: (f, g, path) where f = g + h
    queue = []
    heappush(queue, (heuristic(start, goal), 0, [start]))
    visited = {}
    
    while queue:
        f, g, path = heappop(queue)
        current = path[-1]
        if current == goal:
            return path, g
        if current in visited and visited[current] <= g:
            continue
        visited[current] = g
        for neighbor in get_neighbors(current):
            step_cost = cost_function(current, neighbor)
            new_g = g + step_cost
            new_f = new_g + heuristic(neighbor, goal)
            heappush(queue, (new_f, new_g, path + [neighbor]))
    return None

# Example: 1D search with cost = 1 per step and heuristic = absolute difference
def get_neighbors_1d(x):
    return [x - 1, x + 1]

def cost_function(a, b):
    return 1

print("A* Search path:", a_star_search(0, 10, get_neighbors_1d, heuristic, cost_function))
"""\


snippets ['AlphaBeta Purning'] = r"""\
    "import math

# A sample game tree node definition
class GameNode:
    def __init__(self, state, children=None, score=None):
        self.state = state
        self.children = children if children is not None else []
        self.score = score  # score is defined for terminal nodes

def minimax(node, depth, maximizingPlayer):
    # Terminal condition: if node is a leaf or depth is 0
    if depth == 0 or not node.children:
        return node.score
    
    if maximizingPlayer:
        maxEval = -math.inf
        for child in node.children:
            eval = minimax(child, depth - 1, False)
            maxEval = max(maxEval, eval)
        return maxEval
    else:
        minEval = math.inf
        for child in node.children:
            eval = minimax(child, depth - 1, True)
            minEval = min(minEval, eval)
        return minEval

def alphabeta(node, depth, alpha, beta, maximizingPlayer):
    if depth == 0 or not node.children:
        return node.score
    
    if maximizingPlayer:
        value = -math.inf
        for child in node.children:
            value = max(value, alphabeta(child, depth-1, alpha, beta, False))
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # beta cutoff
        return value
    else:
        value = math.inf
        for child in node.children:
            value = min(value, alphabeta(child, depth-1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break  # alpha cutoff
        return value

# Example game tree construction:
#       Root
#      /    \
#   Node1  Node2
#   /  \     /  \
#  3    5   2    9

leaf1 = GameNode(state="L1", score=3)
leaf2 = GameNode(state="L2", score=5)
leaf3 = GameNode(state="L3", score=2)
leaf4 = GameNode(state="L4", score=9)

node1 = GameNode(state="N1", children=[leaf1, leaf2])
node2 = GameNode(state="N2", children=[leaf3, leaf4])
root = GameNode(state="Root", children=[node1, node2])

print("Minimax value at root:", minimax(root, depth=3, maximizingPlayer=True))
print("Alpha-Beta value at root:", alphabeta(root, depth=3, alpha=-math.inf, beta=math.inf, maximizingPlayer=True))
"""\

snippets['generate moves'] = r"""\" \

    def generate_moves(state):
   
    return [state - 1, state + 1]

def evaluate_state(state):

    return -abs(state)

def adversarial_search(state, depth, maximizingPlayer):
    # Terminal condition: depth 0 or state is a terminal state (for simplicity, when |state| > 10)
    if depth == 0 or abs(state) > 10:
        return evaluate_state(state)
    
    moves = generate_moves(state)
    if maximizingPlayer:
        best_value = -math.inf
        for move in moves:
            value = adversarial_search(move, depth - 1, False)
            best_value = max(best_value, value)
        return best_value
    else:
        best_value = math.inf
        for move in moves:
            value = adversarial_search(move, depth - 1, True)
            best_value = min(best_value, value)
        return best_value

initial_state = 0
print("Adversarial search evaluation:", adversarial_search(initial_state, depth=4, maximizingPlayer=True))
"""\

snippets['Lab 5'] = r"""\" def initial_state():
    
   # Returns the starting state of the board.
  # The board is represented as a 3x3 list of lists.
   # Empty cells are denoted by None.
    
    return [[None, None, None],
            [None, None, None],
            [None, None, None]]


def player(board):
    
    #Returns the player who has the next turn.
    #'X' starts first. If the counts of X's and O's are equal, then it is X's turn;
    #otherwise, it's O's turn.
    
    countX = sum(row.count("X") for row in board)
    countO = sum(row.count("O") for row in board)
    return "X" if countX <= countO else "O"


def actions(board):
    
    #Returns a set of all possible actions (i, j) available on the board,
    #where a move is possible if the cell is empty (None).
    
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] is None}


def result(board, action):
    
    #Returns the board that results from making move (i, j) on the board.
    #Raises an exception if the move is invalid.
    
    i, j = action
    if board[i][j] is not None:
        raise Exception("Invalid move")
    new_board = [row.copy() for row in board]
    new_board[i][j] = player(board)
    return new_board


def winner(board):
    
    #Returns the winner of the game, if there is one.
    #Checks rows, columns, and both diagonals.
    
    # Check rows
    for i in range(3):
        if board[i][0] is not None and board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    # Check columns
    for j in range(3):
        if board[0][j] is not None and board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    # Check diagonals
    if board[0][0] is not None and board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    if board[0][2] is not None and board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None


def terminal(board):
    
    #Returns True if the game is over (i.e., if there is a winner or the board is full).
    
    if winner(board) is not None:
        return True
    # If no empty cell exists, the game is a draw
    if all(cell is not None for row in board for cell in row):
        return True
    return False


def utility(board):
    
    #Returns the utility of the board:
    #  1 if X has won,
    # -1 if O has won,
    #  0 otherwise.
    
    win = winner(board)
    if win == "X":
        return 1
    elif win == "O":
        return -1
    else:
        return 0


def minimax_ab(board, alpha, beta):
    
    #A helper function implementing minimax search with alpha-beta pruning.
    #Returns the minimax value of the board.
    
    if terminal(board):
        return utility(board)
    
    current = player(board)
    
    # Maximizing player: 'X'
    if current == "X":
        value = float("-inf")
        for action in actions(board):
            value = max(value, minimax_ab(result(board, action), alpha, beta))
            alpha = max(alpha, value)
            if alpha >= beta:
                break  # Beta cutoff
        return value
    # Minimizing player: 'O'
    else:
        value = float("inf")
        for action in actions(board):
            value = min(value, minimax_ab(result(board, action), alpha, beta))
            beta = min(beta, value)
            if alpha >= beta:
                break  # Alpha cutoff
        return value


def alpha_beta_pruining(board):
    
    #Returns the optimal action for the current player on the board,
    #using minimax search with alpha-beta pruning.
    #If the game is over (terminal state), returns None.
    
    if terminal(board):
        return None
    
    current = player(board)
    best_move = None
    
    if current == "X":
        best_value = float("-inf")
        alpha = float("-inf")
        beta = float("inf")
        for action in actions(board):
            move_value = minimax_ab(result(board, action), alpha, beta)
            if move_value > best_value:
                best_value = move_value
                best_move = action
            alpha = max(alpha, best_value)
    else:
        best_value = float("inf")
        alpha = float("-inf")
        beta = float("inf")
        for action in actions(board):
            move_value = minimax_ab(result(board, action), alpha, beta)
            if move_value < best_value:
                best_value = move_value
                best_move = action
            beta = min(beta, best_value)
    return best_move


# For testing the alpha_beta_pruining function:
if __name__ == "__main__":
    board = initial_state()
    print("Initial Board:")
    for row in board:
        print(row)
    
    move = alpha_beta_pruining(board)
    print("\nAI recommends move:", move)
    
    board = result(board, move)
    print("\nBoard after AI move:")
    for row in board:
        print(row)

""" \

snippets['GA'] = r"""\" \" \

import random

POP_SIZE = 500
MUT_RATE = 0.1
TARGET = 'abdullah aqeel'
GENES = ' abcdefghijklmnopqrstuvwxyz'

def initialize_pop(TARGET):
    population = list()
    tar_len = len(TARGET)

    for i in range(POP_SIZE):
        temp = list()
        for j in range(tar_len):
            temp.append(random.choice(GENES))
        population.append(temp)

    return population

def crossover(selected_chromo, CHROMO_LEN, population):
    offspring_cross = []
    for i in range(int(POP_SIZE)):
        parent1 = random.choice(selected_chromo)
        parent2 = random.choice(population[:int(POP_SIZE*50)])

        p1 = parent1[0]
        p2 = parent2[0]

        crossover_point = random.randint(1, CHROMO_LEN-1)
        child =  p1[:crossover_point] + p2[crossover_point:]
        offspring_cross.extend([child])
    return offspring_cross

def mutate(offspring, MUT_RATE):
    mutated_offspring = []

    for arr in offspring:
        for i in range(len(arr)):
            if random.random() < MUT_RATE:
                arr[i] = random.choice(GENES)
        mutated_offspring.append(arr)
    return mutated_offspring

def selection(population, TARGET):
    sorted_chromo_pop = sorted(population, key= lambda x: x[1])
    return sorted_chromo_pop[:int(0.5*POP_SIZE)]

def fitness_cal(TARGET, chromo_from_pop):
    difference = 0
    for tar_char, chromo_char in zip(TARGET, chromo_from_pop):
        if tar_char != chromo_char:
            difference+=1
    
    return [chromo_from_pop, difference]

def replace(new_gen, population):
    for _ in range(len(population)):
        if population[_][1] > new_gen[_][1]:
          population[_][0] = new_gen[_][0]
          population[_][1] = new_gen[_][1]
    return population

def main(POP_SIZE, MUT_RATE, TARGET, GENES):
    # 1) initialize population
    initial_population = initialize_pop(TARGET)
    found = False
    population = []
    generation = 1

    # 2) Calculating the fitness for the current population
    for _ in range(len(initial_population)):
        population.append(fitness_cal(TARGET, initial_population[_]))

    # now population has 2 things, [chromosome, fitness]
    # 3) now we loop until TARGET is found
    while not found:

      # 3.1) select best people from current population
      selected = selection(population, TARGET)

      # 3.2) mate parents to make new generation
      population = sorted(population, key= lambda x:x[1])
      crossovered = crossover(selected, len(TARGET), population)
            
      # 3.3) mutating the childeren to diversfy the new generation
      mutated = mutate(crossovered, MUT_RATE)

      new_gen = []
      for _ in mutated:
          new_gen.append(fitness_cal(TARGET, _))

      # 3.4) replacement of bad population with new generation
      # we sort here first to compare the least fit population with the most fit new_gen

      population = replace(new_gen, population)

      
      if (population[0][1] == 0):
        print('Target found')
        print('String: ' + str(population[0][0]) + ' Generation: ' + str(generation) + ' Fitness: ' + str(population[0][1]))
        break
      print('String: ' + str(population[0][0]) + ' Generation: ' + str(generation) + ' Fitness: ' + str(population[0][1]))
      generation+=1

main(POP_SIZE, MUT_RATE, TARGET,GENES)


    """
if __name__ == '__main__':

    peer=Peer()

