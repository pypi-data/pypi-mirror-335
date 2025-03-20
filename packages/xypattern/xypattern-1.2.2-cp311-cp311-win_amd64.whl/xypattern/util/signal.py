# -*- coding: utf-8 -*-
# Dioptas - GUI program for fast processing of 2D X-ray diffraction data
# Principal author: Clemens Prescher (clemens.prescher@gmail.com)
# Copyright (C) 2014-2019 GSECARS, University of Chicago, USA
# Copyright (C) 2015-2018 Institute for Geology and Mineralogy, University of Cologne, Germany
# Copyright (C) 2019-2020 DESY, Hamburg, Germany
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Implementation of a signal-slot mechanism for event handling.

This module provides a simple implementation of the observer pattern,
allowing objects to emit signals that other objects can listen for and
respond to. It uses weak references to avoid memory leaks when listeners
are deleted.
"""

import inspect
import weakref

__export__ = ["Signal"]


class Signal:
    """
    A simple implementation of the observer pattern for event handling.
    
    Signal objects can be connected to callback functions (listeners) that will
    be called when the signal is emitted. The Signal class uses weak references
    to avoid memory leaks when listeners are deleted.
    
    Example:
        >>> # Create a signal
        >>> data_changed = Signal()
        >>> 
        >>> # Connect a listener
        >>> def on_data_changed(data):
        >>>     print(f"Data changed: {data}")
        >>> 
        >>> data_changed.connect(on_data_changed)
        >>> 
        >>> # Emit the signal
        >>> data_changed.emit("new data")  # Prints: Data changed: new data
    """
    
    def __init__(self, *_):
        """
        Initialize a new Signal object.
        
        The Signal maintains two lists of listeners:
        - Regular listeners: Called after priority listeners
        - Priority listeners: Called first when the signal is emitted
        """
        self.listeners = WeakRefList()
        self.priority_listeners = WeakRefList()
        self.blocked = False

    def connect(self, handle, priority=False):
        """
        Connect a callback function to the signal.
        
        When the signal is emitted, all connected callback functions will be called
        in the order they were connected (unless priority is set).
        
        :param handle: Function or method to be called when the signal is emitted
        :param priority: If True, the callback will be called before regular callbacks.
                        Priority callbacks are called in reverse order of connection
                        (last connected priority callback is called first).
        
        Example:
            >>> signal = Signal()
            >>> def callback(value):
            >>>     print(f"Signal received: {value}")
            >>> 
            >>> signal.connect(callback)
            >>> signal.emit("test")  # Prints: Signal received: test
        """
        if priority:
            self.priority_listeners.insert(0, handle)
        else:
            self.listeners.append(handle)

    def disconnect(self, handle):
        """
        Disconnect a callback function from the signal.
        
        After disconnection, the callback will no longer be called when the signal
        is emitted.
        
        :param handle: Function or method to be disconnected from the signal
        
        Example:
            >>> signal = Signal()
            >>> def callback():
            >>>     print("Signal received")
            >>> 
            >>> signal.connect(callback)
            >>> signal.emit()  # Prints: Signal received
            >>> 
            >>> signal.disconnect(callback)
            >>> signal.emit()  # Nothing happens
        """
        try:
            self.listeners.remove(handle)
        except ValueError:
            pass

        try:
            self.priority_listeners.remove(handle)
        except ValueError:
            pass

    def emit(self, *args):
        """
        Emit the signal, calling all connected callbacks.
        
        Priority callbacks are called first, followed by regular callbacks.
        If the signal is blocked, no callbacks will be called.
        
        :param args: Arguments to pass to the callback functions
        
        Example:
            >>> signal = Signal()
            >>> def callback(value):
            >>>     print(f"Received: {value}")
            >>> 
            >>> signal.connect(callback)
            >>> signal.emit("hello")  # Prints: Received: hello
        """
        if self.blocked:
            return
        self._serve_listeners(self.priority_listeners, *args)
        self._serve_listeners(self.listeners, *args)

    @staticmethod
    def _serve_listeners(listeners, *args):
        """
        Call all listeners in the given list with the provided arguments.
        
        :param listeners: List of weak references to callback functions
        :param args: Arguments to pass to the callback functions
        """
        for ref in listeners:
            handle = ref()
            if type(handle) == Signal:
                handle.emit(*args)
            else:
                try:
                    handle(*args)
                except (AttributeError, TypeError):
                    handle()

    def clear(self):
        """
        Remove all listeners from the signal.
        
        After clearing, no callbacks will be called when the signal is emitted
        until new callbacks are connected.
        
        Example:
            >>> signal = Signal()
            >>> def callback():
            >>>     print("Signal received")
            >>> 
            >>> signal.connect(callback)
            >>> signal.emit()  # Prints: Signal received
            >>> 
            >>> signal.clear()
            >>> signal.emit()  # Nothing happens
        """
        self.listeners = WeakRefList()
        self.priority_listeners = WeakRefList()


class WeakRefList(list):
    """
    A list that holds weak references to its items.
    
    When an item is garbage collected, its reference is automatically removed
    from the list. This prevents memory leaks when using signals and slots.
    
    This implementation supports both object methods and regular objects.
    Only the methods used by the Signal class are implemented: append, remove,
    and insert.
    
    Example:
        >>> class Example:
        >>>     def method(self):
        >>>         return "Hello"
        >>>
        >>> example = Example()
        >>> weak_list = WeakRefList()
        >>> weak_list.append(example.method)
        >>> 
        >>> # To access the original item:
        >>> original_method = weak_list[0]()
        >>> original_method()  # Returns: "Hello"
    """
    
    def append(self, item):
        """
        Add an item to the end of the list as a weak reference.
        
        :param item: Item to add to the list
        """
        super(WeakRefList, self).append(self._ref(item))

    def remove(self, item):
        """
        Remove the first occurrence of an item from the list.
        
        :param item: Item to remove from the list
        :raises ValueError: If the item is not in the list
        """
        super(WeakRefList, self).remove(self._ref(item))

    def insert(self, index, item):
        """
        Insert an item at a given position as a weak reference.
        
        :param index: Position to insert the item
        :param item: Item to insert
        """
        super(WeakRefList, self).insert(index, self._ref(item))

    def _remove_ref(self, ref):
        """
        Callback function called when a referenced object is garbage collected.
        Removes the weak reference from the list.
        
        :param ref: Weak reference to remove
        """
        super(WeakRefList, self).remove(ref)

    def _ref(self, item):
        """
        Create a weak reference to an item.
        
        For methods, creates a WeakMethod reference.
        For other objects, creates a standard weak reference.
        
        :param item: Item to create a weak reference to
        :return: Weak reference to the item
        """
        if inspect.ismethod(item):
            return weakref.WeakMethod(item, self._remove_ref)
        else:
            return weakref.ref(item, self._remove_ref)
