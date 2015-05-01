import contextlib

from vistrails.core.modules.vistrails_module import Module


def execute(modules, connections=[], add_port_specs=[], enable_pkg=True):
    """Build a pipeline and execute it.

    This is useful to simply build a pipeline in a test case, and run it. When
    doing that, intercept_result() can be used to check the results of each
    module.

    modules is a list of module tuples describing the modules to be created,
    with the following format:
        [('ModuleName', 'package.identifier', [
            # Functions
            ('port_name', [
                # Function parameters
                ('Signature', 'value-as-string'),
            ]),
        ])]

    connections is a list of tuples describing the connections to make, with
    the following format:
        [
            (source_module_index, 'source_port_name',
             dest_module_index, 'dest_module_name'),
         ]

    add_port_specs is a list of specs to add to modules, with the following
    format:
        [
            (mod_id, 'input'/'output', 'portname',
             '(port_sig)'),
        ]
    It is useful to test modules that can have custom ports through a
    configuration widget.

    The function returns the 'errors' dict it gets from the interpreter, so you
    should use a construct like self.assertFalse(execute(...)) if the execution
    is not supposed to fail.


    For example, this creates (and runs) an Integer module with its value set
    to 44, connected to a PythonCalc module, connected to a StandardOutput:

    self.assertFalse(execute([
            ('Float', 'org.vistrails.vistrails.basic', [
                ('value', [('Float', '44.0')]),
            ]),
            ('PythonCalc', 'org.vistrails.vistrails.pythoncalc', [
                ('value2', [('Float', '2.0')]),
                ('op', [('String', '-')]),
            ]),
            ('StandardOutput', 'org.vistrails.vistrails.basic', []),
        ],
        [
            (0, 'value', 1, 'value1'),
            (1, 'value', 2, 'value'),
        ]))
    """
    from vistrails.core.db.locator import XMLFileLocator
    from vistrails.core.modules.module_registry import MissingPackage
    from vistrails.core.packagemanager import get_package_manager
    from vistrails.core.utils import DummyView
    from vistrails.core.vistrail.connection import Connection
    from vistrails.core.vistrail.module import Module
    from vistrails.core.vistrail.module_function import ModuleFunction
    from vistrails.core.vistrail.module_param import ModuleParam
    from vistrails.core.vistrail.pipeline import Pipeline
    from vistrails.core.vistrail.port import Port
    from vistrails.core.vistrail.port_spec import PortSpec
    from vistrails.core.interpreter.noncached import Interpreter

    pm = get_package_manager()

    port_spec_per_module = {} # mod_id -> [portspec: PortSpec]
    j = 0
    for i, (mod_id, inout, name, sig) in enumerate(add_port_specs):
        mod_specs = port_spec_per_module.setdefault(mod_id, [])
        ps = PortSpec(id=i,
                      name=name,
                      type=inout,
                      sigstring=sig,
                      sort_key=-1)
        for psi in ps.port_spec_items:
            psi.id = j
            j += 1
        mod_specs.append(ps)

    pipeline = Pipeline()
    module_list = []
    for i, (name, identifier, functions) in enumerate(modules):
        function_list = []
        try:
            pkg = pm.get_package(identifier)
        except MissingPackage:
            if not enable_pkg:
                raise
            pkg = pm.identifier_is_available(identifier)
            if pkg:
                pm.late_enable_package(pkg.codepath)
                pkg = pm.get_package(identifier)

        for func_name, params in functions:
            param_list = []
            for j, (param_type, param_val) in enumerate(params):
                param_list.append(ModuleParam(pos=j,
                                              type=param_type,
                                              val=param_val))
            function_list.append(ModuleFunction(name=func_name,
                                                parameters=param_list))
        name = name.rsplit('|', 1)
        if len(name) == 2:
            namespace, name = name
        else:
            namespace = None
            name, = name
        module = Module(name=name,
                        namespace=namespace,
                        package=identifier,
                        version=pkg.version,
                        id=i,
                        functions=function_list)
        for port_spec in port_spec_per_module.get(i, []):
            module.add_port_spec(port_spec)
        pipeline.add_module(module)
        module_list.append(module)

    for i, (sid, sport, did, dport) in enumerate(connections):
        s_sig = module_list[sid].get_port_spec(sport, 'output').sigstring
        d_sig = module_list[did].get_port_spec(dport, 'input').sigstring
        pipeline.add_connection(Connection(
                id=i,
                ports=[
                    Port(id=i*2,
                         type='source',
                         moduleId=sid,
                         name=sport,
                         signature=s_sig),
                    Port(id=i*2+1,
                         type='destination',
                         moduleId=did,
                         name=dport,
                         signature=d_sig),
                ]))

    interpreter = Interpreter.get()
    result = interpreter.execute(
            pipeline,
            locator=XMLFileLocator('foo.xml'),
            current_version=1,
            view=DummyView())
    return result.errors


@contextlib.contextmanager
def intercept_result(module, output_name):
    """This temporarily hooks a module to intercept its results.

    It is used as a context manager, for instance:
    class MyModule(Module):
        def compute(self):
            self.setResult('res', 42)
        ...
    with intercept_result(MyModule, 'res') as results:
        self.assertFalse(execute(...))
    self.assertEqual(results, [42])
    """
    actual_setResult = module.setResult
    old_setResult = module.__dict__.get('setResult', None)
    results = []
    modules_index = {}  # Maps a Module to an index in the list, so a module
            # can change its result
    def new_setResult(self, name, value):
        if name == output_name:
            if self in modules_index:
                results[modules_index[self]] = value
            else:
                modules_index[self] = len(results)
                results.append(value)
        actual_setResult(self, name, value)
    module.setResult = new_setResult
    try:
        yield results
    finally:
        if old_setResult is not None:
            module.setResult = old_setResult
        else:
            del module.setResult


def intercept_results(*args):
    """This calls intercept_result() several times.

    You can pass it multiple modules and port names and it will nest the
    managers, for instance:
    with intercept_results(ModOne, 'one1', 'one2', ModTwo, 'two1', 'two2') as (
            one1, one2, two1, two2):
        self.assertFalse(execute(...))
    """
    ctx = []
    current_module = None
    for arg in args:
        if isinstance(arg, type) and issubclass(arg, Module):
            current_module = arg
        elif isinstance(arg, basestring):
            if current_module is None:
                raise ValueError
            ctx.append(intercept_result(current_module, arg))
        else:
            raise TypeError
    return contextlib.nested(*ctx)
