"""Initializes the NFA from the specified regular expression"""
# pylint: disable=invalid-name

from AlgsSedgewickWayne.digraph_dvk import Digraph
from AlgsSedgewickWayne.directed_dfs import DirectedDFS


class ReferenceItNFA:
    """Initializes the NFA from the specified regular expression"""

    def __init__(self, regexp):
        self.regexp = regexp
        self.len_regexp = len(regexp)    # M
        # Epsilon transition digraph (does not include
        self.digraph = self._init_digraph(regexp)
        # print(self.digraph)

    def _init_digraph(self, regexp):
        """Build epsilon transition digraph"""
        # Use stack to remember '(' to implement '*' and '|'
        ops = []
        len_regexp = self.len_regexp
        digraph = Digraph(len_regexp+1)
        exp_operations = {'(', '|'}
        exp_edgechr = {'(', '*', ')'}
        for reg_i, reg_chr in enumerate(regexp):
            # self._prt_color_regex(reg_i, reg_chr)
            left_paren = reg_i
            if reg_chr in exp_operations:
                ops.append(reg_i)
            elif reg_chr == ')':
                tmpor = ops.pop()
                # 2-way or operator
                if regexp[tmpor] == '|':
                    left_paren = ops.pop()
                    digraph.add_edge(left_paren, tmpor+1)
                    digraph.add_edge(tmpor, reg_i)
                elif regexp[tmpor] == '(':
                    left_paren = tmpor
                else:
                    assert False

            # closure operator (uses 1-character lookahead)
            reg_i_plus1 = reg_i + 1
            if reg_i < len_regexp-1 and regexp[reg_i_plus1] == '*':
                # print(f'************ {left_paren} {reg_i_plus1}')
                # print(f'************ {reg_i_plus1} {left_paren}')
                digraph.add_edge(left_paren, reg_i_plus1)
                digraph.add_edge(reg_i_plus1, left_paren)
            if reg_chr in exp_edgechr:
                digraph.add_edge(reg_i, reg_i_plus1)
        return digraph

    def _prt_color_regex(self, reg_i, reg_chr):
        regex = list(self.regexp)
        regex[reg_i] = '\x1b[48;5;0;{FGBG};5;{COLOR};1;3;4m{ABC}\x1b[0m'.format(
            FGBG=38, COLOR=13, ABC=regex[reg_i])
        print(f'REGEX {reg_i:2}) {reg_chr} {"".join(regex)}')

    def recognizes(self, txt):
        """Does the NFA recognize txt?"""
        # Get states reachable from start by epsilon-transitions
        # program counter holds set of all program possible states for given regex
        # Build a DFS for all states that can be reached from state 0 by epsilon edges
        reachable_states = DirectedDFS.from_state0(self.digraph).get_reachable_states()
        print(f'\n{len(reachable_states)} REACHABLE INIT STATES: {reachable_states}')

        # Compute possible NFA states for txt[i+1]
        regexp = self.regexp + 'Z'
        len_regexp = self.len_regexp
        digraph = self.digraph
        for idx, txt_chr in enumerate(txt):
            print(f'{txt_chr}')
            matched = set()
            for vertex in reachable_states:
                # If accept-state is reached, nothing left to do
                if vertex == len_regexp:
                    print(f'continue vertex({vertex})')
                    #continue
                # Get all states matchable after matching a text character
                elif (regexp[vertex] == txt_chr or regexp[vertex] == '.'):
                    print(f'matched.add({vertex+1})')
                    matched.add(vertex+1)

            # Follow epsilon-transitions after a character match
            reachable_states = DirectedDFS.from_sources(digraph, matched).get_reachable_states()
            states = [regexp[i] for i in sorted(reachable_states)]
            print(f'txt[{idx}]({txt_chr}): reachable_states({states})')

            # optimization if no states reachable
            if not reachable_states:
                print('False: Optimization if no states reachable')
                #return False

        # Accept if can end in state len_regexp
        print(f'ACCEPT({len_regexp in reachable_states})')
        return len_regexp in reachable_states
