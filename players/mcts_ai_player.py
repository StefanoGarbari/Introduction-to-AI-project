from tsuro import Player, State, Action
import time
import random
import math


class Node:
    def __init__(self, state: State, parent = None, action : Action = None):
        self.parent = parent
        self.action = action

        self.children : list[Node] = []
        self.visits = 0
        self.wins = 0

        self.untried_actions = state.actions()


class MCTSPlayer(Player):

    def choose_action(self, state: State, time_limit=1.0):

        root = Node(state.copy())
        start = time.time()

        while time.time() - start < time_limit:

            node = root
            sim_state = state.copy()

            # 1. SELECTION
            while not node.untried_actions and node.children:
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

                child = Node(sim_state.copy(), parent=node, action=action)
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


        return best_child.action
