import inspect
from functools import wraps
import copy
from warnings import warn


def show_source(f):
    def get_fn_name(f):
        return f.__code__.co_name

    def get_source_for_lambda(s):
        fst = s.index("lambda")
        if "(" in s:
            nxt = s.index("(")
            if nxt < fst:
                fst = nxt
        else:
            fst = 0

        def cpar_index(s):
            p = 0
            for n, c in enumerate(s):
                if c == "(":
                    p += 1
                elif c == ")":
                    p -= 1
                    assert p >= 0
                    if p == 0:
                        break
            return n

        lst = cpar_index(s[fst:]) + fst
        assert fst < lst
        in_par = s[fst:lst]
        fst = s.index("lambda", fst)
        fst = s.index(":", fst) + 1
        assert fst < lst
        return s[fst:lst].strip()

    s = inspect.getsource(f)
    if s.lstrip().startswith("def "):
        return get_fn_name(f)
    elif "lambda" in s:
        return get_source_for_lambda(s)
    else:  # pragma: no cover
        # Not reachable?
        raise Exception(f"impossible to parse source {s}")


def get_wraparound(f):
    if hasattr(f, "dbc_wraparound"):
        result = f.dbc_wraparound, f.dbc_preconditions, f.dbc_postconditions
    else:
        result = f, [], []
    return result


def set_wraparound(f, original_call, preconditions, postconditions):
    f.dbc_wraparound = original_call
    f.dbc_preconditions = preconditions
    f.dbc_postconditions = postconditions


def assert_argspec_and_kw_match(argspec, kw, ignore=None):
    assert all(
        a in kw for a in argspec.args if not ignore or a not in ignore
    ), f"missing arg in {list(kw)} for {argspec.args}"


def get_kw_from_call(f, a, kw):
    argspec = inspect.getfullargspec(f)

    kw2 = kw.copy()
    # kwargs
    for i, nm in enumerate(argspec.args):
        # positionals
        if len(a) > i:
            v = a[i]
            kw2[nm] = v

    for i, nm in enumerate(a for a in argspec.args if a not in kw2):
        # defaults
        if argspec.defaults is not None and len(argspec.defaults) > i:
            kw2[nm] = argspec.defaults[i]
        else:
            # that's an error, but from the caller, let python handle that
            warn("wrong arguments provided during call, not checking contracts")
            return {}

    assert_argspec_and_kw_match(argspec, kw2)
    return kw2


def format_kw(kw):
    def brief_repr(o, length):
        r = repr(o)
        if len(r) > length:
            half = 1 + ((length - 5 + 1) // 2)
            r = f"{r[:half]}[...]{r[-half:]}"
        return r

    return ", ".join(f"{k} = {brief_repr(kw[k], 30)}" for k in sorted(kw))


class OldHolder:
    def __init__(self, d):
        self.d = copy.deepcopy(d)

    def __getattr__(self, name):
        return self.d[name]

    def __repr__(self):
        return repr(self.d)


PRE, PRE_INIT, POST = 1, 2, 3

checked = {PRE, POST}


def is_checked(cond_type):
    assert cond_type in (PRE, POST)
    return __debug__ and cond_type in checked


def check(cond_type):
    assert cond_type in (PRE, POST)
    assert not is_checked(cond_type), f"{cond_type} is already checked"
    checked.add(cond_type)


def ignore(cond_type):
    assert cond_type in (PRE, POST)
    assert is_checked(cond_type), f"{cond_type} is already ignored"
    checked.remove(cond_type)


def ignore_preconditions():
    ignore(PRE)


def check_preconditions():
    check(PRE)


def ignore_postconditions():
    ignore(POST)


def check_postconditions():
    check(POST)


def get_kw_for_conditional_before(cond_type, conditional, in_kw):
    assert cond_type in (PRE, PRE_INIT, POST)
    assert callable(conditional)
    out_kw = {}
    argspec = inspect.getfullargspec(conditional)
    for nm in argspec.args:
        if nm == "result":
            assert cond_type == POST, f"only postconditions can use {nm!r}"
        elif nm == "old":
            assert cond_type == POST, f"only postconditions can use {nm!r}"
            out_kw[nm] = OldHolder(in_kw)
        else:
            if nm == "self":
                assert (
                    cond_type != PRE_INIT
                ), f"precondition of a constructor cannot use {nm!r}"
            out_kw[nm] = in_kw[nm]
    assert_argspec_and_kw_match(argspec, out_kw, ("result",))
    return out_kw


def get_kw_for_postcondition_after(result, conditional, in_kw):
    assert callable(conditional)
    out_kw = {}
    argspec = inspect.getfullargspec(conditional)
    if "result" in argspec.args:
        out_kw["result"] = result
    assert ("result" in out_kw) == ("result" in argspec.args)
    return out_kw


def condition_decorator(is_precondition, conditional, message=None):
    def deco(f):
        original_call, preconditions, postconditions = get_wraparound(f)

        if is_precondition:
            preconditions.insert(0, (conditional, message))
        else:
            postconditions.insert(0, (conditional, message))

        def rejects_call_kw(call_kw, stop_at_first_rejection: bool = False) -> list:
            rejection_reasons = []
            for precondition, message in preconditions:
                cond_type = PRE_INIT if original_call.__name__ == "__init__" else PRE
                cond_kw = get_kw_for_conditional_before(
                    cond_type, precondition, call_kw
                )
                if not precondition(**cond_kw):
                    cond_kw_str = format_kw(cond_kw)
                    src = show_source(precondition)
                    if message is None:
                        rejection_reasons.append(
                            f"**caller** of {original_call.__name__}() bug: precondition {src!r} failed: {cond_kw_str}"
                        )
                    else:
                        rejection_reasons.append(
                            f"**caller** of {original_call.__name__}() bug: precondition {message!r} failed: {cond_kw_str}"
                        )

                    if stop_at_first_rejection:
                        break

            return rejection_reasons

        def rejects(*a, **kw) -> bool:
            call_kw = get_kw_from_call(original_call, a, kw)
            return bool(rejects_call_kw(call_kw, stop_at_first_rejection=True))

        def accepts(*a, **kw) -> bool:
            call_kw = get_kw_from_call(original_call, a, kw)
            return not rejects_call_kw(call_kw, stop_at_first_rejection=True)

        @wraps(f)
        def call_and_run_contracts(*a, **kw):
            call_kw = get_kw_from_call(original_call, a, kw)

            if is_checked(PRE):
                reasons = rejects_call_kw(call_kw, stop_at_first_rejection=False)
                if reasons:
                    raise AssertionError(reasons[0])

            if is_checked(POST):
                post_kw = []
                for postcondition, _ in postconditions:
                    cond_kw = get_kw_for_conditional_before(
                        POST, postcondition, call_kw
                    )
                    post_kw.append(cond_kw)

            result = original_call(*a, **kw)

            if is_checked(POST):
                for i, (postcondition, message) in enumerate(postconditions):
                    cond_kw = post_kw[i]
                    cond_kw.update(
                        get_kw_for_postcondition_after(result, postcondition, call_kw)
                    )
                    if not postcondition(**cond_kw):
                        cond_kw_str = format_kw(cond_kw)
                        src = show_source(postcondition)
                        if message is None:
                            raise AssertionError(
                                f"{original_call.__name__}() bug: postcondition {src!r} failed: {cond_kw_str}"
                            )
                        else:
                            raise AssertionError(
                                f"{original_call.__name__}() bug: postcondition {message!r} failed: {cond_kw_str}"
                            )

            return result

        set_wraparound(
            call_and_run_contracts, original_call, preconditions, postconditions
        )
        call_and_run_contracts.accepts = accepts
        call_and_run_contracts.rejects = rejects
        return call_and_run_contracts

    return deco


def precondition(conditional, message=None):
    return condition_decorator(True, conditional, message)


def postcondition(conditional, message=None):
    return condition_decorator(False, conditional, message)


never_returns = postcondition(lambda: False, "should never return")
