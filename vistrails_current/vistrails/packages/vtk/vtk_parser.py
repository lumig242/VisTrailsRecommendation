###############################################################################
##
## Copyright (C) 2011-2014, NYU-Poly.
## Copyright (C) 2006-2011, University of Utah. 
## All rights reserved.
## Contact: contact@vistrails.org
##
## This file is part of VisTrails.
##
## "Redistribution and use in source and binary forms, with or without 
## modification, are permitted provided that the following conditions are met:
##
##  - Redistributions of source code must retain the above copyright notice, 
##    this list of conditions and the following disclaimer.
##  - Redistributions in binary form must reproduce the above copyright 
##    notice, this list of conditions and the following disclaimer in the 
##    documentation and/or other materials provided with the distribution.
##  - Neither the name of the University of Utah nor the names of its 
##    contributors may be used to endorse or promote products derived from 
##    this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" 
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, 
## THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR 
## PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR 
## CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, 
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, 
## PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; 
## OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, 
## WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR 
## OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF 
## ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
##
###############################################################################

# Author: Prabhu Ramachandran
# Copyright (c) 2004, Enthought, Inc.
# License: BSD Style.

# Modified for VisTrails by the VisTrails team.

"""This module parses the VTK methods, obtains the argument and return
type information, and organizes them.

"""
import re
import vtk
import class_tree
import vistrails.core.debug

log      = vistrails.core.debug.log
warning  = vistrails.core.debug.warning
critical = vistrails.core.debug.critical
debug    = vistrails.core.debug.debug

class VTKMethodParser(object):
    """This class provides useful methods for parsing methods of a VTK
    class or instance.

    The class allows one to categorize the methods of the VTK class
    and also obtain the method signatures in a form that is easy to
    use.  When the `parse` method is called, it in turn calls the
    `_organize_methods` method.  This method organizes the VTK methods
    into different instance variables described in the following.
    `self.toggle_meths` contains a dictionary of all the boolean
    methods of the form <Value>On/Off.  The dictionary keys are
    strings with the <Value>'s and the value of each item is the
    default value (0/1) of the item (the example below will clarify
    this).  `self.state_meths` contains a dictionary which collects
    the Set<Prop>To<Value> type of methods.  The key is the <Prop> and
    the value is a list containing the different string <Value>'s and
    their corresponding mapped value.  The first value in these is the
    default value of the <Prop>.  `self.get_set_meths` will contain a
    dictionary which collects all the methods of the form
    Set/Get<Prop> that are not already specified in
    `self.toggle_meths` or `self.state_meths`.  The default value of
    the Get<Prop> is stored.  If the value accepted by the method has
    a range (via the methods `Get<Prop>MinValue` and
    `Get<Prop>MaxValue`), then that range is computed and stored.
    `self.get_meths` stores the methods that are of the form
    `Get<Prop>`.  `self.other_meths` stores the remaining methods.
    The parsing is quite fast.  Parsing every class in the VTK API
    takes a couple of seconds (on a Pentium III @ 450Mhz).

    Here is an example::
        
       >>> import vtk
       >>> p = VTKMethodParser()
       >>> p.parse(vtk.vtkProperty)
       >>> print p.get_toggle_methods()
       {'EdgeVisibility': 0, 'BackfaceCulling': 0, 'FrontfaceCulling': 0}
       >>> print p.get_state_methods()['Representation']
       [['Surface', 2], ['Points', 0], ['Surface', 2], ['Wireframe', 1]]
       >>> print p.get_get_set_methods()['Opacity']
       (1.0, (0.0, 1.0))
       >>> print p.get_get_methods()
       ['GetClassName']
       >>> print p.get_other_methods()[:3]
       ['BackfaceRender', 'DeepCopy', 'IsA']


    The class also provides a method called `get_method_signature`
    that obtains the Python method signature given the VTK method
    object.  Here is an example::
    
       >>> import vtk
       >>> p = VTKMethodParser()
       >>> o = vtk.vtkProperty
       >>> print p.get_method_signature(o.GetClassName)
       [(['string'], None)]
       >>> print p.get_method_signature(o.GetColor)[0]
       ([('float', 'float', 'float')], None)
       >>> print p.get_method_signature(o.GetColor)[1]
       ([None], (('float', 'float', 'float'),))

    The `get_method_signature` is fairly efficient and obtaining the
    signature for every method in every class in the VTK API takes
    around 6 seconds (on a Pentium III @ 450Mhz).

    """

    def __init__(self, use_tree=True):
        """Initializes the object.

        Parameters
        ----------

        - use_tree : `bool`

          If True (default), use a ClassTree instance to obtain a
          concrete subclass for an abstract base class.  This is used
          only to find the range and default values for some of the
          methods.  If False, no ClassTree instance is created.

          This is optional because, creating a ClassTree is expensive.
          The parser functionality can be very useful even without the
          use of a ClassTree.  For example, if one wants to save the
          state of a VTK object one only needs to know the names of
          the methods and not their default values, ranges etc.  In
          that case using a parser should be cheap.

        """
        # The ClassTree is needed to find an instantiable child class
        # for an abstract VTK parent class.  This instance is used to
        # obtain the state values and the ranges of the arguments
        # accepted by the Get/Set methods that have a
        # Get<Prop>{MaxValue,MinValue} method.
        if use_tree:
            self._tree = class_tree.ClassTree(vtk)
            self._tree.create()
        else:
            self._tree = None
        self._state_patn = re.compile('To[A-Z0-9]')
        self._initialize()

    #################################################################
    # 'VTKMethodParser' interface.
    #################################################################

    def parse(self, obj, no_warn=True):
        """Parse the methods for a given VTK object/class.

        Given a VTK class or object, this method parses the methods
        and orgaizes them into useful categories.  The categories and
        their usage is documented in the documentation for the class.

        Parameters
        ----------

        - obj : VTK class or instance

        - no_warn : `bool` (default: True)

          If True (default), it suppresses any warnings generated by
          the VTK object when parsing the methods.  This is safe to
          use.
        
        """
        if not hasattr(obj, '__bases__'):
            klass = obj.__class__
        else:
            klass = obj

        methods = self.get_methods(klass)

        if no_warn:
            # Save warning setting and shut it off before parsing.
            warn = vtk.vtkObject.GetGlobalWarningDisplay()
            if klass.__name__ <> 'vtkObject':
                vtk.vtkObject.GlobalWarningDisplayOff()

        self._organize_methods(klass, methods)

        if no_warn:
            # Reset warning status.
            vtk.vtkObject.SetGlobalWarningDisplay(warn)

    def get_methods(self, klass):
        """Returns all the relevant methods of the given VTK class."""
        methods = dir(klass)[:]
        if hasattr(klass, '__members__'):
            # Only VTK versions < 4.5 have these.
            for m in klass.__members__:
                methods.remove(m)

        return methods

    def get_toggle_methods(self):        
        """Returns a dictionary of the parsed <Value>On/Off methods
        along with the default value.

        """
        return self.toggle_meths
    
    def get_state_methods(self):
        """Returns a dict of the parsed Set<Prop>To<Value>.

        The keys are the <Prop> string with a list of the different
        <Value> strings along with their corresponding value (if
        obtainable).  The first value is the default value of the
        state.
        
        """
        return self.state_meths

    def get_get_set_methods(self):
        """Returns a dict of the parsed Get/Set<Value> methods.

        The keys of the dict are the <Value> strings and contain a
        two-tuple containing the default value (or None if it is not
        obtainable for some reason) and a pair of numbers specifying
        an acceptable range of values (or None if not obtainable).

        """
        return self.get_set_meths
    
    def get_get_methods(self):
        """Return a list of parsed Get<Value> methods.

        All of these methods do NOT have a corresponding Set<Value>.

        """
        return self.get_meths
    
    def get_other_methods(self):
        """Return list of all other methods, that are not
        categorizable.

        """
        return self.other_meths    

    def get_method_signature(self, method):
        """Returns information on the Python method signature given
        the VTK method.

        The doc string of the given method object to get the method
        signature.  The method returns a list of tuples, each of which
        contains 2 items, the first is a list representing the return
        value the second represents the arguments to be passed to the
        function.  If the method supports different return values and
        arguments, this function returns all of their signatures.

        Parameters
        ----------

        - method : `method`

          A VTK method object.

        """
        doc = method.__doc__
        doc = doc[:doc.find('\n\n')]
        sig = doc.split('\n')
        sig = [x.strip() for x in sig]

        # Remove all the C++ function signatures.
        for i in sig[:]:
            if i[:4] == 'C++:':
                sig.remove(i)

        # Remove the V.<method_name>
        sig = [x.replace('V.' + method.__name__, '') for x in sig]

        pat = re.compile(r'\b')

        # Split into [return_value, arguments] after processing them.
        tmp = list(sig)
        sig = []
        for i in tmp:
            # Split to get return values.
            x = i.split('->')
            # Strip each part.
            x = [y.strip() for y in x]

            if len(x) == 1: # No return value
                x = [None, x[0]]
            else:
                x.reverse()

            ret, arg = x        

            # Remove leading and trailing parens for arguments.
            arg = arg[1:-1]
            if not arg:
                arg = None
            if arg and arg[-1] == ')':
                arg = arg + ','

            # Now quote the args and eval them.  Easy!
            if ret:
                ret = eval(pat.sub('\"', ret))
            if arg:
                arg = eval(pat.sub('\"', arg))
                if isinstance(arg, basestring):
                    arg = [arg]

            sig.append(([ret], arg))

        return sig

    def get_tree(self):
        """Return the ClassTree instance used by this class."""
        return self._tree

    #################################################################
    # Non-public interface.
    #################################################################

    def _initialize(self):
        """Initializes the method categories."""
        # Collects the <Value>On/Off methods.
        self.toggle_meths = {}
        # Collects the Set<Prop>To<Value> methods.
        self.state_meths = {}
        # Collects the Set/Get<Value> pairs.
        self.get_set_meths = {}
        # Collects the Get<Value> methods.
        self.get_meths = []
        # Collects all the remaining methods.
        self.other_meths = []

    def _organize_methods(self, klass, methods):
        """Organizes the given methods of a VTK class into different
        categories.

        Parameters
        ----------

        - klass : A VTK class

        - methods : `list` of `str`

          A list of the methods to be categorized.

        """
        self._initialize()
        meths = methods[:]
        meths = self._find_toggle_methods(klass, meths)
        meths = self._find_state_methods(klass, meths)
        meths = self._find_get_set_methods(klass, meths)
        meths = self._find_get_methods(klass, meths)
        self.other_meths = [x for x in meths if '__' not in x]

    def _remove_method(self, meths, method):
        try:
            meths.remove(method)
        except ValueError:
            pass

    def _find_toggle_methods(self, klass, methods):
        """Find/store methods of the form <Value>{On,Off} in the given
        `methods`.  Returns the remaining list of methods.

        """
        meths = methods[:]
        tm = self.toggle_meths
        for method in meths[:]:
            if method[-2:] == 'On':
                key = method[:-2]
                if (key + 'Off') in meths and ('Get' + key) in meths:
                    tm[key] = None
                    meths.remove(method)
                    meths.remove(key + 'Off')
                    self._remove_method(meths, 'Set' + key)
                    self._remove_method(meths, 'Get' + key)
        # get defaults
        if tm:
            obj = self._get_instance(klass)
            if obj:
                for key in tm:
                    try:
                        tm[key] = getattr(obj, 'Get%s'%key)()
                    except TypeError, e:
                        log("Type error during parsing: class %s will not expose method %s " % (klass.__name__, key))
                    except AttributeError, e:
                        log("Attribute error during parsing: class %s will not expose method %s " % (klass.__name__, key))
        return meths

    def _find_state_methods(self, klass, methods):
        """Find/store methods of the form Set<Prop>To<Value> in the
        given `methods`.  Returns the remaining list of methods.  The
        method also computes the mapped value of the different
        <Values>.

        """
        # These ignored ones are really not state methods.
        ignore = ['SetUpdateExtentToWholeExtent']
        meths = methods[:]
        sm = self.state_meths
        for method in meths[:]:
            if method not in ignore and method[:3] == 'Set':
                # Methods of form Set<Prop>To<Value>
                match = self._state_patn.search(method)
                # Second cond. ensures that this is not an accident.
                if match and (('Get'+method[3:]) not in meths):
                    key = method[3:match.start()] # The <Prop> part.
                    if (('Get' + key) in methods):
                        val = method[match.start()+2:] # <Value> part.
                        meths.remove(method)
                        if sm.has_key(key):
                            sm[key].append([val, None])
                        else:
                            sm[key] = [[val, None]]
                            meths.remove('Get'+ key)
                            self._remove_method(meths, 'Set'+ key)
                            if ('Get' + key + 'MaxValue') in meths:
                                meths.remove('Get' + key + 'MaxValue')
                                meths.remove('Get' + key + 'MinValue')
                            try:
                                meths.remove('Get' + key + 'AsString')
                            except ValueError:
                                pass

        # Find the values for each of the states, i.e. find that
        # vtkProperty.SetRepresentationToWireframe() corresponds to
        # vtkProperty.SetRepresentation(1).
        if sm:
            obj = self._get_instance(klass)
            if obj:
                for key, values in sm.items():
                    default = getattr(obj, 'Get%s'%key)()
                    for x in values[:]:
                        try:
                            getattr(obj, 'Set%sTo%s'%(key, x[0]))()
                        except:
                            continue
                        val = getattr(obj, 'Get%s'%key)()
                        x[1] = val
                        if val == default:
                            values.insert(0, [x[0], val])
        return meths

    def _find_get_set_methods(self, klass, methods):
        """Find/store methods of the form {Get,Set}Prop in the given
        `methods` and returns the remaining list of methods.

        Note that it makes sense to call this *after*
        `_find_state_methods` is called in order to avoid incorrect
        duplication.  This method also computes the default value and
        the ranges of the arguments (when possible) by using the
        Get<Prop>{MaxValue,MinValue} methods.

        """
        meths = methods[:]
        gsm = self.get_set_meths
        
        for method in meths[:]:
            # Methods of the Set/Get form.
            if method in ['Get', 'Set']:
                # This occurs with the vtkInformation class.
                continue
            elif (method[:3] == 'Set') and ('Get' + method[3:]) in methods:
                key = method[3:]
                meths.remove('Set' + key)
                meths.remove('Get' + key)                    
                if ('Get' + key + 'MaxValue') in meths:
                    meths.remove('Get' + key + 'MaxValue')
                    meths.remove('Get' + key + 'MinValue')
                    gsm[key] = 1
                else:
                    gsm[key] = None

        # Find the default and range of the values.
        if gsm:
            obj = self._get_instance(klass)
            if obj:
                klass_name = klass.__name__
                for key, value in gsm.items():
                    if klass_name == 'vtkPolyData':
                        # Evil hack, this class segfaults!
                        default = None
                    else:
                        try:
                            default = getattr(obj, 'Get%s'%key)()
                        except TypeError:
                            default = None
                    if value:
                        low = getattr(obj, 'Get%sMinValue'%key)()
                        high = getattr(obj, 'Get%sMaxValue'%key)()
                        gsm[key] = (default, (low, high))
                    else:
                        gsm[key] = (default, None)
            else:
                # We still might have methods that have a default range.
                for key, value in gsm.items():
                    if value == 1:
                        gsm[key] = None
        
        return meths

    def _find_get_methods(self, klass, methods):
        """Find/store methods of the form Get<Value> in the given
        `methods` and returns the remaining list of methods.

        """
        meths = methods[:]
        gm = self.get_meths
        for method in meths[:]:
            if method == 'Get':
                # Occurs with vtkInformation
                continue
            elif method[:3] == 'Get':        
                gm.append(method)
                meths.remove(method)
        return meths

    def _get_instance(self, klass):
        """Given a VTK class, `klass`, returns an instance of the
        class.

        If the class is abstract, it uses the class tree to return an
        instantiable subclass.  This is necessary to get the values of
        the 'state' methods and the ranges for the Get/Set methods.
        
        """
        obj = None
        try:
            obj = klass()
        except (TypeError, NotImplementedError):
            if self._tree:
                t = self._tree
                n = t.get_node(klass.__name__)
                for c in n.children:
                    obj = self._get_instance(t.get_class(c.name))
                    if obj:
                        break
        return obj

