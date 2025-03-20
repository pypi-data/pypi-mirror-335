from enum import Enum, auto
from lark import Tree, Token, Discard, Lark
from dataclasses import dataclass, field
from functools import cache
from importlib.resources import files
import re
import codecs
import dill


class BaseTopic:
    _name: str

    @classmethod
    def as_list_arg(B, value, kw=''):
        A = value
        if A:
            return f"<{kw}[{A}]>"
        return ''

    @classmethod
    def as_simple_arg(B, value, kw=''):
        A = value
        if A:
            return f"<{kw}:{A}:>"
        return ''

    @classmethod
    def extract_args(J, value):
        A = value
        G = '(<(\\w*)[\\[:].*?[:\\]]>)'
        C = re.split(G, A)
        D = []
        E = {}
        D.append(C.pop(0))
        for (I, F) in enumerate(C):
            if F.endswith(':>'):
                B = C[I+1]
                H = len(B)
                A = F[H+2:-2]
                E.update({B: A})if B else D.append(A)
            elif F.endswith(']>'):
                B = C[I+1]
                H = len(B)
                G = '\\s*::\\s*'
                A = list(filter(lambda v: v, re.split(G, F[H+2:-2])))
                E.update({B: A})if B else D.append(A)
        E.pop('hints', None)
        return D, E

    @classmethod
    def from_string(A, input_text): B = A.extract_args(
        input_text); return A(*B[0], **B[1])


@dataclass
class Integral(BaseTopic):
    _name = "main_integrate"
    expr: str

    def to_string(self):
        return self.expr


@dataclass
class Limit(BaseTopic):
    _name = "main_limit"
    expr: str

    def to_string(self):
        return self.expr


@dataclass
class Simplify(BaseTopic):
    _name = "main_simplify"
    expr: str

    def to_string(self):
        return self.expr


@dataclass
class Summation(BaseTopic):
    _name = "main_summation"
    expr: str

    def to_string(self):
        return self.expr


@dataclass
class Derivative(BaseTopic):
    _name = "main_derivative"
    expr: str
    solve_for: list[str] = field(default_factory=list)

    def to_string(self):
        return f'{self.expr} {self.as_list_arg("::".join(self.solve_for))}'.strip()


@dataclass
class SolveFor(BaseTopic):
    _name = "main_solve_for_var"
    expr: str
    solve_for: list[str]

    def to_string(self):
        return f'{self.expr} {self.as_list_arg("::".join(self.solve_for))}'.strip()


@dataclass
class Substitute(BaseTopic):
    _name = "main_substitute"
    expr: str
    subs: list[str]

    def to_string(self):
        return f'{self.expr} {self.as_list_arg("::".join(self.subs))}'.strip()


@dataclass
class Matrix(BaseTopic):
    _name = "main_tensor"
    expr: str

    def to_string(self):
        return f'{self.expr}'.strip()


@dataclass(frozen=True)
class Topic:
    SIMPLIFY = Simplify
    SUMMATION = Summation
    INTEGRAL = Integral
    DERIVATIVE = Derivative
    LIMIT = Limit
    SUBSTITUTE = Substitute
    SOLVE_FOR = SolveFor
    MATRIX = Matrix


SUP_MAP = {'⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4',
           '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9'}
SUB_MAP = {'₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4',
           '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9'}
GREEK_UNICODE_MAP = {'α': '\\alpha', 'β': '\\beta', 'γ': '\\gamma', 'θ': '\\theta',
                     'Θ': '\\Theta', 'κ': '\\kappa', 'λ': '\\lambda', 'π': '\\pi', 'φ': '\\phi', 'ϕ': '\\phi', "σ": "\\sigma"}
OTHER_MAP = {'√': '\\sqrt', '∞': '\\infty',
             '×': '\\times', '\\to': '->', "∫": "\\int"}
PAREN_MAP = {'\\left(': '(', '\\right)': ')', '\\lparen': '(', '\\rparen': ')', '\\left[': '[', '\\right]': ']', '{': '(', '}': ')',
             '\\{': '(', '\\}': ')', '\\lbrace': '(', '\\rbrace': ')', '\\left|': '|', '\\right|': '|', '\\lvert': '|', '\\rvert': '|'}


def filter_rule_name(value): return value.split('__')[-1]


def get_tks(t, type):
    def A(v):
        if not isinstance(v, Token):
            return False
        if not type:
            return True
        return filter_rule_name(v.type) == type
    if isinstance(t, list):
        return list(Tree('__formatted__', t).scan_values(A))
    elif isinstance(t, Tree):
        return list(t.scan_values(A))
    return [t.value]


def is_variable_type(value):
    A = value
    if isinstance(A, Tree) and any(filter_rule_name(A.data) == B for B in VarName):
        return True
    return False


def is_num_type(value):
    A = value
    if isinstance(A, Token) and any(filter_rule_name(A.type) == B for B in NumName):
        return True
    return False


def get_identifier(item):
    A = item
    if isinstance(A, Tree):
        return filter_rule_name(A.data)
    elif A:
        return filter_rule_name(A.type)


def get_print_value(item):
    A = item
    if isinstance(A, Tree):
        return print_tree(A)
    elif isinstance(A, Token):
        return A.value
    return ''


def replace_from(tree, cb):
    B = tree
    for (C, D) in enumerate(B.children):
        if isinstance(D, Tree):
            A = cb(D)
            if A is None:
                replace_from(D, cb)
            elif A is Discard:
                B.children[C] = None
            else:
                B.children[C] = A
        else:
            A = cb(D)
            if A is not None:
                B.children[C] = A
            elif A is Discard:
                B.children[C] = None
    return B


def find_from(value, data):
    B = data
    A = value
    C = []
    if isinstance(A, Tree):
        if isinstance(B, str):
            C.extend(A.find_pred(lambda t: filter_rule_name(t.data) == B))
        elif isinstance(B, list):
            C.extend(A.find_pred(lambda v: v in B))
        else:
            C.extend(A.find_pred(B))
    elif isinstance(A, list):
        for D in A:
            C.extend(find_from(D, B))
    return C


def print_tree(value): A = []; A.extend(value.scan_values(
    lambda v: isinstance(v, Token))); return ''.join(A)


class Simple_T:
    def __init__(A, visit_tokens=True): A.__visit_tokens__ = visit_tokens

    def _call_userfunc(B, tree, new_children=None):
        C = new_children
        A = tree
        D = C if C is not None else A.children
        try:
            E = filter_rule_name(A.data)
            F = getattr(B, E)
        except AttributeError:
            return B.__default__(A.data, D, A.meta)
        else:
            try:
                return F(D)
            except Exception:
                raise ValueError('Failed!')

    def _call_userfunc_token(B, token):
        A = token
        try:
            C = filter_rule_name(A.type)
            D = getattr(B, C)
        except AttributeError:
            return B.__default_token__(A)
        else:
            try:
                return D(A)
            except Exception:
                raise ValueError('Failed!')

    def _t_children(C, children):
        for A in children:
            if isinstance(A, Tree):
                B = C._t_tree(A)
            elif C.__visit_tokens__ and isinstance(A, Token):
                B = C._call_userfunc_token(A)
            else:
                B = A
            if B is not Discard:
                yield B

    def _t_tree(A, tree): B = list(A._t_children(
        tree.children)); return A._call_userfunc(tree, B)

    def t(B, tree):
        A = list(B._t_children([tree]))
        if not A:
            return
        return A[0]

    def __default__(A, data, children, meta): return Tree(data, children, meta)
    def __default_token__(A, token): return token


class Pre_T(Simple_T):
    def with_paren(A, t): return replace_from(
        Tree('with_paren', t), _nb)

    def with_forced_paren(A, t): return Tree(
        'with_paren', [Token('LPAR', '(')]+t+[Token('RPAR', ')')])

    def with_forced_backslash(A, _): return Tree(
        '__formatted__', [Token('BACKSLASH', '\\')])

    def with_hard_paren(A, t): return replace_from(
        Tree('with_hard_paren', t), _nb)

    def with_brace(A, t): return replace_from(
        Tree('with_brace', t), _nb)

    def with_single_bar(B, t): A = replace_from(Tree('with_single_bar', t), _nb); A.children.insert(
        0, Token('LPAR', '(')); A.children.append(Token('RPAR', ')')); return A

    def with_multi_bar_trap(A, _): raise ValueError('Failed!')

    def frac(D, t):
        A = t[1]
        B = t[2]
        for C in (A, B):
            C.children[0] = Token('LPAR', '(')
            C.children[-1] = Token('RPAR', ')')
        return Tree('__formatted__', [Token('LPAR', '('), A, Token('SLASH', '/'), B, Token('RPAR', ')')])

    def vector_frac(A, t): return A.vector_div(A.frac(t).children[1:-1])
    def vector_div(C, t): A = t.pop(2); t.pop(1); B = t.pop(); return Tree('__formatted__', [
        Token('LPAR', '('), Token('NUMBER', '1'), Token('RPAR', ')'), Token('SLASH', '/'), A, B])

    def ambi_char(A, t): return Token('__formatted__', f"{t[0]}_({t[1]})")
    def matrix_wrapper(A, t): return Tree('__formatted__', [
        Token('LSQB', '['), t[2], Token('RSQB', ']')])

    def matrix_column_sep(A, _): return Token('COMMA', ',')
    def matrix_column_sep_end(A, _): return Discard

    def matrix_row_ltx(C, t):
        A = [Token('LSQB', '[')]
        for B in find_from(t, 'matrix_expr_atom'):
            A.append(B)
            A.append(Token('COMMA', ','))
        A[-1] = Token('RSQB', ']')
        return Tree('__formatted__', A)

    def matrix_content_single_sbqt(C, t):
        A = []
        for B in find_from(t, 'matrix_expr_atom'):
            A.append(Token('LSQB', '['))
            A.append(B)
            A.append(Token('RSQB', ']'))
            A.append(Token('COMMA', ','))
        A.pop()
        return Tree('__formatted__', A)

    def binom_fn(A, t):
        B = get_tks(t, NumName.INT)
        if len(B) != 2:
            raise ValueError('Failed!')
        C = f"(({B[0]}!)/({B[1]}!({B[0]}-{B[1]})!))"
        return Token('__formatted__', C)

    def binom_ex(A, t): B = t[2]; C = t[3]; return Tree('__formatted__', [Token('LPAR', '('), Token('LPAR', '('), B, Token('EXCLAMATION', '!'), Token('RPAR', ')'), Token(
        'SLASH', '/'), Token('LPAR', '('), C, Token('EXCLAMATION', '!'), Token('LPAR', '('), B, Token('MINUS', '-'), C, Token('RPAR', ')'), Token('EXCLAMATION', '!'), Token('RPAR', ')'), Token('RPAR', ')')])

    def degree_symbol(A, _): return Token('__formatted__', '\\deg')

    def SUP_UNICODE_NUMBER(B, t): A = SUP_MAP[t.value]; return Tree('__formatted__', [
        Token('CIRCUMFLEX', '^'), Token('LPAR', '('), Token('DIGIT', A), Token('RPAR', ')')])
    def SUB_UNICODE_NUMBER(B, t): A = SUB_MAP[t.value]; return Tree('__formatted__', [
        Token('UNDERSCORE', '_'), Token('LPAR', '('), Token('DIGIT', A), Token('RPAR', ')')])

    def BACKSLASH(A, _): return Token('BACKSLASH', '\\')

    def CIRC_SYMBOL(A, _): return Token('__formatted__', 'o')

    def TO_SYMBOL(A, _): return Token('TO', '->')

    def LEQ_SYMBOL(A, _): return Token('__formatted__', '<=')
    def GEQ_SYMBOL(A, _): return Token('__formatted__', '>=')
    def NE_SYMBOL(A, _): return Token('__formatted__', '!=')
    def LT_SYMBOL(A, _): return Token('__formatted__', '<')
    def GT_SYMBOL(A, _): return Token('__formatted__', '>')

    def __default_token__(D, t):
        A = t.value
        if is_num_type(t):
            C = ''
            if '{' in t.value:
                C = t.value.split('{')[1].removesuffix('}')
            A = t.value.split('\\')[0]+C
            B = re.split('[eE]', A)
            if len(B) > 1:
                A = f"{B[0]}*10^({B[1]})"
        if A in OTHER_MAP:
            A = OTHER_MAP[A]
        if A in GREEK_UNICODE_MAP:
            A = GREEK_UNICODE_MAP[A]
        if A != t.value:
            return Token(t.type, A)
        return t


def _nb(item):
    A = item
    if isinstance(A, Tree) and A.data == 'with_bracket_backslash' or isinstance(A, Token) and A.value in PAREN_MAP:
        C = get_print_value(A)
        if C in PAREN_MAP:
            B = PAREN_MAP[C]
            return {'(': Token('LPAR', B), ')': Token('RPAR', B), '[': Token('LSQB', B), ']': Token('RSQB', B), "|": Token("VBAR", B)}.get(B)


def _remove_paren(c):
    if isinstance(c, Tree) and c.data == 'with_paren':
        return Discard


class VarName(str, Enum):
    ANY_VAR = 'any_var'
    CHAR_VAR = 'char_var'


class NumName(str, Enum):
    def _generate_next_value_(A, *B): return A
    SIGNED_NUMBER = auto()
    NUMBER = auto()
    INT = auto()
    DECIMAL = auto()
    SIGNED_DECIMAL = auto()


@dataclass
class TS:
    node: Tree
    in_rule_scope: bool = False
    in_fn: bool = False
    def next_state(A, node, is_rule_match, is_fnm): return TS(
        node=node, in_rule_scope=A.in_rule_scope or is_rule_match, in_fn=A.in_fn or is_fnm)


@dataclass
class ED:
    fn_names: set = field(default_factory=set)
    vars: set = field(default_factory=set)

    def merge(A, other):
        B = other
        if isinstance(B, list):
            for C in B:
                A.fn_names.update(C.fn_names)
                A.vars.update(C.vars)
        else:
            A.fn_names.update(B.fn_names)
            A.vars.update(B.vars)


class Extractor:
    def _cvb(J, item, rules, is_em):
        B = item
        A = ED()
        if B is None:
            return A
        if is_variable_type(B):
            A.vars.add(get_print_value(B))
            return A
        if isinstance(B, Token):
            return A
        E = [TS(B)]
        while E:
            C = E.pop()
            D = C.node
            F = filter_rule_name(D.data) in rules
            G = filter_rule_name(D.data) == 'func_name'
            if (F or C.in_rule_scope) != is_em:
                for H in D.children:
                    if is_variable_type(H):
                        if G or C.in_fn:
                            I = A.fn_names
                        else:
                            I = A.vars
                        I.add(get_print_value(H))
            E.extend(C.next_state(A, F, G)
                     for A in reversed(D.children)if isinstance(A, Tree))
        return A

    def cve(B, value, exr=[]):
        C = exr
        A = value
        if isinstance(A, list):
            D = ED()
            for E in A:
                D.merge(B._cvb(E, C, is_em=True))
            return D
        return B._cvb(A, C, is_em=True)

    def cvi(D, value, irs=None):
        B = value
        A = irs
        C = False
        if A is None:
            A = []
            C = True
        if isinstance(B, list):
            E = ED()
            for F in B:
                E.merge(D._cvb(F, A, C))
            return E
        return D._cvb(B, A, C)

    def lazy_v(A, tree):
        for B in tree.iter_subtrees_topdown():
            C = filter_rule_name(B.data)
            if hasattr(A, C):
                getattr(A, C)(B)
                break

    def fmt_vars(B, tree):
        if B.inferred is None:
            raise ValueError('Failed!')
        D = {}

        def A(c):
            if is_variable_type(c):
                for E in B.inferred:
                    if get_print_value(c) == E[0]:
                        A = []
                        for C in E[1]:
                            D[C] = s2c(C)
                            A.append(Token(VarName.ANY_VAR, s2c(C)))
                            A.append(Token('__formatted__', '*'))
                        A.pop()
                        return Tree('__formatted__', A)
        replace_from(tree, A)
        B.inferred_vars = D

    def derivative_func(B, tree):
        A = tree
        vars = set()
        C = set()
        D = B.cvi(A.children[0])
        C.update(D.vars)
        E = B.cvi(A.children[2])
        vars.update(E.vars)
        F = B.cvi(A.children[3])
        C.update(F.vars)
        G = B.cvi(A.children[4])
        C.update(G.vars)
        if len(D.vars) > 1:
            H = D.fn_names.pop()
            A.children[0] = Token('__formatted__', H)
        A.children.pop(4)
        B.inferred = ivg(vars, C)
        B.fmt_vars(A)

    def derivative_equality(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(B.children[0]); vars.update(D.vars); E = A.cvi(B.children[2]); vars.update(
        E.vars); F = A.cvi(B.children[3]); C.update(F.vars); G = A.cvi(B.children[4]); C.update(G.vars); B.children.pop(4); A.inferred = ivg(vars, C); A.fmt_vars(B)

    def derivative_regular(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(B.children[0]); vars.update(D.vars); E = A.cvi(
        B.children[1]); C.update(E.vars); F = A.cvi(B.children[2]); C.update(F.vars); B.children.pop(2); A.inferred = ivg(vars, C); A.fmt_vars(B)

    def integral_indefinite(B, tree):
        A = tree
        vars = set()
        C = set()
        E = B.cvi(A.children[1])
        C.update(E.vars)
        F = B.cvi(A.children[3])
        vars.update(F.vars)
        G = B.cvi(A.children[4])
        C.update(G.vars)
        H = B.cvi(A.children[5])
        C.update(H.vars)
        A.children[0] = Token('__formatted__', '\\int ')
        A.children.pop(5)
        B.inferred = ivg(vars, C)
        B.fmt_vars(A)
        if A.children[4]:
            A.children[4].children.pop(0)
        D = get_print_value(A.children[4])
        if D:
            A.children[4] = Token('__formatted__', f" {D}")
        A.children.pop(2)
        A.children.pop(1)

    def integral_definite(B, tree):
        A = tree
        vars = set()
        C = set()
        F = B.cvi(
            find_from(A.children[0], 'integral_range_content'))
        vars.update(F.vars)
        G = B.cvi(A.children[1])
        vars.update(G.vars)
        H = B.cvi(A.children[2])
        C.update(H.vars)
        I = B.cvi(A.children[3])
        C.update(I.vars)
        for D in vars:
            if len(D) > 1 and D.startswith('d'):
                raise ValueError('Failed!')
        A.children.pop(3)
        B.inferred = ivg(vars, C)
        B.fmt_vars(A)
        if A.children[2]:
            A.children[2].children.pop(0)
        E = get_print_value(A.children[2])
        if E:
            A.children[2] = Token('__formatted__', f" {E}")

    def substitute(A, tree):
        B = tree
        vars = set()
        E = set()
        I = A.cvi(
            find_from(B.children[3], 'substitute_assignee_value'))
        vars.update(I.vars)
        J = A.cvi(
            find_from(B.children[3], 'substitute_assignee'))
        E.update(J.vars)
        K = A.cvi(
            find_from(B.children[3], 'substitute_var_algeb'))
        vars.update(K.vars)
        F = set()
        L = find_from(B.children[3], 'func_simple_vars')
        for C in L:
            D = A.cvi(C)
            F.update(D.fn_names)
            E.update(D.vars)
            replace_from(C, _remove_paren)
        G = A.cvi(B.children[0])
        vars.update(G.vars)
        if not G.fn_names.issubset(F):
            if len(G.fn_names) != 1 or len(G.vars) != 1:
                raise ValueError('Failed!')
        H = A.cvi(B.children[2])
        vars.update(H.vars)
        if not H.fn_names.issubset(F):
            raise ValueError('Failed!')
        M = A.cvi(B.children[4])
        E.update(M.vars)
        for C in find_from(B.children[0], 'func_simple_vars'):
            D = A.cvi(C)
            E.update(D.vars)
            if D.fn_names.intersection(F):
                replace_from(C, _remove_paren)
        for C in find_from(B.children[2], 'func_simple_vars'):
            D = A.cvi(C)
            E.update(D.vars)
            replace_from(C, _remove_paren)
        B.children.pop(4)
        A.inferred = ivg(vars, E)
        A.fmt_vars(B)

    def simplify(B, tree):
        A = tree
        vars = set()
        C = set()
        D = B.cvi(A.children[0])
        if get_identifier(A.children[0]) == 'simplify_fn':
            C.update(D.vars)
            A.children[0:2] = [None]*2
        else:
            vars.update(D.vars)
        E = B.cvi(A.children[2])
        vars.update(E.vars)
        F = B.cvi(A.children[3])
        C.update(F.vars)
        A.children.pop(3)
        B.inferred = ivg(vars, C)
        B.fmt_vars(A)

    def summation(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(find_from(B.children, 'summation_sub_assignee')); C.update(D.vars); E = A.cvi(
        B.children); vars.update(E.vars); F = A.cvi(B.children[-1]); C.update(F.vars); B.children.pop(-1); A.inferred = ivg(vars, C); A.fmt_vars(B)

    def limit(B, tree): A = tree; vars = set(); C = set(); D = B.cvi(A.children[2], ['limit_to_var']); C.update(D.vars); E = B.cvi(A.children[3]); vars.update(E.vars); F = B.cvi(
        A.children[5]); vars.update(F.vars); G = B.cvi(A.children[6]); C.update(G.vars); A.children.pop(6); B.inferred = ivg(vars, C); B.fmt_vars(A); A.children.pop(4); A.children.pop(3)

    def solve_for_var_reg(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(B.children[0]); vars.update(D.vars); E = A.cvi(B.children[2]); vars.update(
        E.vars); F = A.cvi(B.children[3]); C.update(F.vars); G = A.cvi(B.children[4]); C.update(G.vars); B.children.pop(4); A.inferred = ivg(vars, C); A.fmt_vars(B)

    def solve_for_var_range(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(B.children[0]); vars.update(D.vars); E = A.cvi(B.children[2]); vars.update(E.vars); F = A.cvi(
        B.children[4]); vars.update(F.vars); G = A.cvi(B.children[5]); C.update(G.vars); H = A.cvi(B.children[6]); C.update(H.vars); B.children.pop(6); A.inferred = ivg(vars, C); A.fmt_vars(B)

    def vector_algebra(A, tree): B = tree; vars = set(); C = set(); D = A.cvi(B.children[0]); vars.update(
        D.vars); E = A.cvi(B.children[1]); C.update(E.vars); B.children.pop(1); A.inferred = ivg(vars, C); A.fmt_vars(B)


@cache
def load_parser():
    with files('algeb_parser').joinpath('parser').open('rb')as B:
        A = dill.load(B)
        return Lark(A[0], **A[1]).parse


def format_topic(topic, variable_hints=[]):
    E = variable_hints
    B = topic
    C = B.to_string()
    try:
        if E:
            F = BaseTopic.as_list_arg('::'.join(map(str, E)), 'hints')
            C = f"{C}{F}"
        D = C.replace('\n', '').replace('\\,', '')+'\n'

        def G(m):
            A = m.group(2)
            if A:
                return A
            return codecs.decode(f"\\{m.group(1)}", 'unicode-escape')
        D = re.sub('\\\\{1,}(?:(u[0-9a-fA-F]{4})|([\\u0080-\\uffff]))', G, D)
        H = load_parser()
        A = H(D, B._name)
        A = Pre_T().t(A)
        I = Extractor()
        I.lazy_v(A)
        return B.from_string(rr_paren(print_tree(A)))
    except:
        return


def ivg(ambi_vars, rev_vars): return VG(
    ambi_vars, rev_vars).group_variables()


def s2c(s):
    if len(s) <= 1:
        return s
    A = s.split('_')
    if len(A) == 1:
        B = A[0]
    elif len(A) == 2 and len(A[0]) == 1:
        return f"{A[0]}_({A[1]})"
    else:
        B = A[0].lower()+''.join(A.capitalize()for A in A[1:])
    return f"v_({B})"


def pre_filter_vars_fn(s): return not (
    len(s) > 3 and s[1:3] in ['_{', '_('] or s.startswith('\\'))


class VG:
    def __init__(A, ambi_vars, rev_vars):
        C = rev_vars
        B = ambi_vars
        B = set(filter(pre_filter_vars_fn, B))
        C = set(filter(pre_filter_vars_fn, C))
        E = []
        for D in B:
            if len(D) == 1 or '_' in D:
                E.append(D)
        A.ambi_vars = set(B)
        A.rev_vars = set(C)
        A.rev_vars.update(E)
        A.rev_vars = sorted(list(A.rev_vars), key=len, reverse=True)

    def _find_intervals(E, t):
        C = []
        for B in E.rev_vars:
            D = 0
            while True:
                A = t.find(B, D)
                if A == -1:
                    break
                F = A + len(B)
                if A == 0 and F == len(t):
                    return [(A, F, B)]
                C.append((A, F, B))
                D = A+1
        return sorted(C, key=lambda x: (x[0], x[1]))

    def _has_overlaps(F, intervals):
        C = False
        A = intervals
        if not A:
            return C
        B = A[0][1]
        for (D, E, G) in A[1:]:
            if D < B:
                return True
            B = E
        return C

    def _partition_string(F, var, sorted_intervals):
        G = []
        A = list(var)
        for (B, C, D) in sorted_intervals:
            A[B:C] = [None]*(C-B)
            A[B] = D
        E = [A for A in A if A is not None]
        return E

    def _collect_intervals(A):
        B = {}
        for C in A.ambi_vars:
            B[C] = A._find_intervals(C)
            if A._has_overlaps(B[C]):
                return {}
        return B

    def group_variables(B):
        if not B.ambi_vars:
            return []
        F = B._collect_intervals()
        if not F:
            return
        G = []
        H = []
        for (A, I) in F.items():
            if I:
                G.append((A, B._partition_string(A, I)))
            else:
                H.append(A)
        if H:
            return
        D = []
        J = set()
        for (E, C) in G:
            if len(E) > 1:
                for (K, L) in enumerate(C):
                    C[K] = L
                if len(C) > 1:
                    D.append((E, C))
                    J.add(E)
        for A in B.rev_vars:
            if len(A) > 1 and A not in J:
                M = A
                D.append((A, [M]))
        return D


def rr_paren(expression):
    def B(text, start, end):
        C = start
        A = text
        if A[C] != '(' or A[end] != ')':
            return False
        B = 0
        for D in range(C+1, end):
            if A[D] == '(':
                B += 1
            elif A[D] == ')':
                if B == 0:
                    return False
                B -= 1
        return B == 0

    def A(text):
        A = text
        if len(A) <= 1:
            return A
        while len(A) >= 2 and B(A, 0, len(A)-1):
            A = A[1:-1]
        return A
    return A(expression)
