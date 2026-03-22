from tsuro import Player, State, Action
import time
import random
import math


# A node in the search tree. Each node represents a game state reached by a specific action.
class Node:
    def __init__(self, state: State, parent=None, action : Action=None, is_chance=False):
        self.parent = parent
        self.action = action       # the action that led to this node
        self.is_chance = is_chance # True when the next step is drawing a tile (random, not a player decision)

        self.children : list[Node] = []
        self.visits = 0  # how many times this node has been visited
        self.wins = 0    # how many of those visits ended in a win

        self.untried_actions = state.actions()


class MCTSPlayer(Player):
    def __init__(self, time_limit=1):
        super().__init__()
        self.time_limit = time_limit
        self.name += f" - {time_limit}s MonteCarlo"

    def choose_action(self, state: State):

        root = Node(state)
        start = time.time()

        nodes = 0
        chance_nodes = 0

        # repeat until the time budget runs out
        while time.time() - start < self.time_limit:

            node = root
            sim_state = state.copy()

            # 1. SELECTION
            # Walk down the tree, picking the most promising child at each step,
            # until we reach a node that still has untried actions or a leaf.
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
                    # UCB1: balance exploitation (win rate) with exploration (less-visited nodes).
                    node = max(
                        node.children,
                        key=lambda n: (n.wins / n.visits) +
                        1.4 * math.sqrt(math.log(node.visits) / n.visits)
                    )
                    sim_state.apply(node.action)

            # 2. EXPANSION
            # Pick one untried action and add it as a new child of the current node.
            if node.untried_actions:
                action = random.choice(node.untried_actions)
                node.untried_actions.remove(action)

                sim_state.apply(action)

                child = Node(sim_state, parent=node, action=action, is_chance=sim_state.has_played)
                nodes += 1
                node.children.append(child)

                node = child

            # 3. SIMULATION (rollout)
            # Play randomly until the game ends to get an outcome estimate.
            while not sim_state.is_terminal():
                actions = sim_state.actions()
                if not actions:
                    break
                action = random.choice(actions)
                sim_state.apply(action)

            result = sim_state.get_result(self)

            # 4. BACKPROPAGATION
            # Propagate the result up to the root so every ancestor is updated.
            while node is not None:
                node.visits += 1
                node.wins += result
                node = node.parent

        # Return the action whose child was visited most — the most reliable estimate.
        best_child = max(root.children, key=lambda n: n.visits)

        print(f"Explored {nodes} nodes and {chance_nodes} chance nodes")

        return best_child.action
