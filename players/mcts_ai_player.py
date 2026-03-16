from tsuro import Player, State, Action
import time
import random
import math


class Node:
    def __init__(self, state: State, parent=None, action : Action=None, is_chance=False):
        self.parent = parent
        self.action = action
        self.is_chance = is_chance

        self.children : list[Node] = []
        self.visits = 0
        self.wins = 0

        self.untried_actions = state.actions()


class MCTSPlayer(Player):

    def choose_action(self, state: State, time_limit=1.0):

        root = Node(state)
        start = time.time()

        nodes = 0
        chance_nodes = 0

        while time.time() - start < time_limit:

            node = root
            sim_state = state.copy()

            # 1. SELECTION
            while not node.untried_actions and node.children:
                if node.is_chance:
                    action = sim_state.actions()[0]
                    sim_state.apply(action)
                    found = False
                    for child in node.children:
                        if child.action == action:
                            node = child
                            found = True
                            break
                    if not found:
                        child = Node(sim_state, parent=node, action=action, is_chance=sim_state.has_played)
                        chance_nodes += 1
                        node.children.append(child)
                        node = child

                else:
                    node = max(
                        node.children,
                        key=lambda n: (n.wins / n.visits) +
                        1.4 * math.sqrt(math.log(node.visits) / n.visits)
                    )
                    sim_state.apply(node.action)

            # 2. EXPANSION
            if node.untried_actions:
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)

                sim_state.apply(action)

                child = Node(sim_state, parent=node, action=action, is_chance=sim_state.has_played)
                nodes += 1
                node.children.append(child)

                node = child

            # 3. SIMULATION
            while not sim_state.is_terminal():
                actions = sim_state.actions()
                if not actions:
                    print("should not be here")
                    break
                action = random.choice(actions)
                sim_state.apply(action)

            result = sim_state.get_result(self)

            # 4. BACKPROPAGATION
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent

        # choose the most visited child
        best_child = max(root.children, key=lambda n: n.visits)

        
        print(f"Explored {nodes} nodes and {chance_nodes} chance nodes")

        return best_child.action
