import asyncio
import uuid
from typing import Dict, Union, Tuple, Callable, Optional, Any
from weakref import WeakKeyDictionary, WeakValueDictionary

from pret.manager import get_manager


def get_untracked(obj):
    return obj


class ProxyState:
    VERSION = 0
    CHECK_VERSION = 0

    def __init__(self, target, base_object=None):
        self.target = target
        self.base_object = base_object
        self.snap_cache = None
        self.check_version = ProxyState.CHECK_VERSION
        self.version = ProxyState.VERSION
        self.listeners = []
        self.child_proxy_states: Dict[Union[str, int], Tuple[ProxyState, Optional[Callable]]] = dict()

    def ensure_version(self, next_check_version=None):
        if next_check_version is None:
            ProxyState.CHECK_VERSION += 1
            next_check_version = ProxyState.CHECK_VERSION
        if len(self.listeners) == 0 and next_check_version != self.check_version:
            self.check_version = next_check_version
            for child_proxy_state, _ in self.child_proxy_states.values():
                child_version = child_proxy_state.ensure_version(next_check_version)
                if child_version > self.version:
                    self.version = child_version
        return self.version

    def notify_update(self, op, next_version=None):
        if next_version is None:
            ProxyState.VERSION += 1
            next_version = ProxyState.VERSION
        if self.version != next_version:
            self.version = next_version
            for listener in self.listeners:
                listener(op, next_version)

    def create_prop_listener(self, prop):
        def listener(op, next_version):
            new_op = list(op)
            new_op[1] = [prop, *new_op[1]]
            self.notify_update(new_op, next_version)
        return listener

    def add_prop_listener(self, prop, child_proxy_state):
        if prop in self.child_proxy_states:
            raise ValueError('prop listener already exists')
        if len(self.listeners) > 0:
            remove = child_proxy_state.add_listener(self.create_prop_listener(prop))
            self.child_proxy_states[prop] = (child_proxy_state, remove)
        else:
            self.child_proxy_states[prop] = (child_proxy_state, None)

    def remove_prop_listener(self, prop):
        entry = self.child_proxy_states.pop(prop, None)
        if entry is not None:
            entry[1]()

    def add_listener(self, listener: Callable):
        self.listeners.append(listener)

        # If this is the first listener, add prop listeners to all child proxy states
        # Otherwise, this means that the child proxy states already have prop listeners
        # that will trigger us to update, so we don't need to add these again
        if len(self.listeners) == 1:
            for prop, (child_proxy_state, _) in self.child_proxy_states.items():
                remove = child_proxy_state.add_listener(self.create_prop_listener(prop))
                self.child_proxy_states[prop] = (child_proxy_state, remove)

        def remove_listener():
            self.listeners.remove(listener)
            if len(self.listeners) == 0:
                for prop, (child_proxy_state, remove) in self.child_proxy_states.items():
                    if remove is not None:
                        remove()
                        self.child_proxy_states[prop] = (child_proxy_state, None)
        return remove_listener

    def create_snapshot(self):
        self.ensure_version()
        if self.snap_cache is not None and self.snap_cache[0] == self.version:
            return self.snap_cache[1]

        # self.mark_to_track(snap, True)

        if isinstance(self.target, list):
            raise NotImplementedError('TODO: implement create_snapshot for list')
        elif isinstance(self.target, dict):
            snap = {}
            self.snap_cache = (self.version, snap)
            for key, value in self.target.items():
                snap[key] = snapshot(value)
        else:
            raise ValueError('target should be list or dict')

        return snap


class DictProxy(dict):
    def __init__(self, mapping):
        super().__init__()
        self.proxy_state = ProxyState(self, mapping)
        proxy_state_map[self] = self.proxy_state
        for key, value in mapping.items():
            self[key] = value

    def __setitem__(self, key, value):
        has_prev_value = key in self
        prev_value = self.get(key)
        if (
          has_prev_value and (
            value is prev_value
            or (
                  isinstance(value, dict)
                  and value in proxy_cache
                  and prev_value is proxy_cache[value]
            )
          )
        ):
            return

        # Re-assign prop listener
        proxy_state = proxy_state_map[self]
        proxy_state.remove_prop_listener(key)

        if isinstance(value, dict):
            value = get_untracked(value) or value

        # Ensure that the value is proxied
        if value not in proxy_state_map:  # and proxied not in ref_set:
            proxied = _proxy(value)
            is_builtin = value is proxied
        else:
            is_builtin = False
            proxied = value

        # If a proxy was created (nested object), add a prop listener to it
        if not is_builtin:
            child_proxy_state = proxy_state_map.get(proxied)
            if child_proxy_state:
                proxy_state.add_prop_listener(key, child_proxy_state)

        super().__setitem__(key, proxied)
        proxy_state.notify_update(['__setitem__', [key], value])

    def __delitem__(self, key):
        super().__delitem__(key)
        self.proxy_state.remove_prop_listener(key)
        self.proxy_state.notify_update(['__delitem__', [key], None])

    def clear(self) -> None:
        for key in self:
            self.proxy_state.remove_prop_listener(key)
        super().clear()
        self.proxy_state.notify_update(['clear', [], None])

    def pop(self, key, default=None):
        self.proxy_state.remove_prop_listener(key)
        value = super().pop(key, default)
        self.proxy_state.notify_update(['__delitem__', [key], None])
        return value

    def popitem(self):
        key, value = super().popitem()
        self.proxy_state.remove_prop_listener(key)
        self.proxy_state.notify_update(['__delitem__', [key], None])
        return key, value

    def setdefault(self, key, default=None):
        if key not in self:
            self[key] = default
        return self[key]

    def update(self, other=None, **kwargs):
        if other is not None:
            for key, value in other.items():
                self[key] = value
        for key, value in kwargs.items():
            self[key] = value

    def __hash__(self):
        return id(self)


proxy_cache = WeakValueDictionary()
proxy_state_map: WeakKeyDictionary[Any, ProxyState] = WeakKeyDictionary()


def _proxy(value):
    if isinstance(value, (int, float, str, bool, type(None))):
        return value

    weak_handle = id(value)
    proxied = proxy_cache.get(weak_handle)
    if proxied and proxy_state_map[proxied].base_object is value:
        return proxied

    if isinstance(value, dict):
        proxied = DictProxy(value)
    else:
        raise NotImplementedError(f'Cannot proxy {type(value)}')

    proxy_cache[weak_handle] = proxied

    return proxied


def proxy(value, remote_sync=False, notify_in_sync=False):
    proxied = _proxy(value, notify_in_sync=notify_in_sync)
    if not isinstance(proxied, DictProxy):
        return proxied
    if remote_sync:
        if remote_sync is True:
            sync_id = uuid.uuid4()
        else:
            sync_id = remote_sync
        proxied._sync_id = sync_id
        manager = get_manager()
        subscribe(proxied, lambda ops: manager.on_state_change(ops, sync_id))


def subscribe(proxy_object, callback, notify_in_sync=False):
    proxy_state = proxy_state_map.get(proxy_object)
    if not proxy_state:
        raise ValueError('Please use proxy object')

    ops = []
    future = None
    is_listener_active = False

    def listener(op, next_version=None):
        nonlocal future
        ops.append(op)
        if notify_in_sync:
            callback(list(ops))
            ops.clear()
            return

        if not future:
            def callback_and_clear_future():
                nonlocal future
                future = None
                if is_listener_active:
                    callback(list(ops))
                    ops.clear()
            future = asyncio.get_running_loop().call_soon(callback_and_clear_future)

    def unsubscribe():
        nonlocal is_listener_active
        is_listener_active = False
        remove_listener()

    remove_listener = proxy_state.add_listener(listener)

    return unsubscribe


def snapshot(value):
    if isinstance(value, DictProxy):
        proxy_state = proxy_state_map[value]
        return proxy_state.create_snapshot()
    return value
