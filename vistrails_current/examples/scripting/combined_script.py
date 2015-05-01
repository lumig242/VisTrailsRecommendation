import os
import sys

try:
    import vistrails
except:
    #try to append vistrails source dir relative to examples/scripting
    this_dir = os.path.split(__file__)[0]
    sys.path.append(os.path.join(this_dir, '../..'))
    import vistrails

import vistrails.core.application
import vistrails.core.db.action
import vistrails.core.db.locator
import vistrails.core.modules.module_registry


#init vistrails
vt_app = vistrails.core.application.init()
vt_app.new_vistrail()
controller = vt_app.get_controller()
registry = vistrails.core.modules.module_registry.get_module_registry()

#========================== convenience methods ================================
def newModule(package_name, module_name):
    descriptor = registry.get_descriptor_by_name(package_name, module_name)
    return controller.create_module_from_descriptor(descriptor)

def newConnection(source, source_port, target, target_port):
    c = controller.create_connection(source, source_port, target, target_port)
    return c

def setPortValue(module, port_name, value):
    function = controller.create_function(module, port_name, [str(value)])
    module.add_function(function)
    return

def addToPipeline(items, ops=[]):
    item_ops = [('add',item) for item in items]
    action = vistrails.core.db.action.create_action(item_ops + ops)
    controller.add_new_action(action)
    version = controller.perform_action(action)
    controller.change_selected_version(version)

def layoutAndAdd(module, connections):
    if not isinstance(connections, list):
        connections = [connections]
    ops = controller.layout_modules_ops(preserve_order=True,
                                        new_modules=[module],
                                        new_connections=connections)
    addToPipeline([module] + connections, ops)

#========================== package prefixes ===================================
httppkg = 'edu.utah.sci.vistrails.http'
vtkpkg = 'edu.utah.sci.vistrails.vtk'

#============================ start script =====================================

#start with http file module
httpFA = newModule(httppkg, 'HTTPFile')
url = 'http://www.vistrails.org/download/download.php?type=DATA&id=gktbhFA.vtk'
setPortValue(httpFA, 'url', url)

#add to pipeline
addToPipeline([httpFA])

#create data set reader module for the gktbhFA.vtk file
dataFA = newModule(vtkpkg, 'vtkDataSetReader')

#connect modules
http_dataFA = newConnection(httpFA, 'file', dataFA, 'SetFile')

#layout new modules before adding
layoutAndAdd(dataFA, http_dataFA)

#add contour filter
contour = newModule(vtkpkg, 'vtkContourFilter')
setPortValue(contour, 'SetValue', (0,0.6))
dataFA_contour = newConnection(dataFA, 'GetOutputPort0',
                               contour, 'SetInputConnection0')
layoutAndAdd(contour, dataFA_contour)

#add normals, stripper, and probe filter
normals = newModule(vtkpkg, 'vtkPolyDataNormals') #GetOutputPort0
setPortValue(normals, 'SetFeatureAngle', 60.0)
contour_normals = newConnection(contour, 'GetOutputPort0', 
                                normals, 'SetInputConnection0')
layoutAndAdd(normals, contour_normals)

stripper = newModule(vtkpkg, 'vtkStripper') #GetOutputPort0
normals_stripper = newConnection(normals, 'GetOutputPort0',
                                 stripper, 'SetInputConnection0')
layoutAndAdd(stripper, normals_stripper)

probe = newModule(vtkpkg, 'vtkProbeFilter') #same
stripper_probe = newConnection(stripper, 'GetOutputPort0',
                               probe, 'SetInputConnection0')
layoutAndAdd(probe, stripper_probe)

#build other branch in reverse
colors = newModule(vtkpkg, 'vtkImageMapToColors')
setPortValue(colors, 'SetOutputFormatToRGBA', True)
colors_probe = newConnection(colors, 'GetOutputPort0',
                             probe, 'SetInputConnection1')
layoutAndAdd(colors, colors_probe)

lookup = newModule(vtkpkg, 'vtkLookupTable')
setPortValue(lookup, 'SetHueRange', (0.0,0.8))
setPortValue(lookup, 'SetSaturationRange', (0.3,0.7))
setPortValue(lookup, 'SetValueRange', (1.0,1.0))
lookup_colors = newConnection(lookup, 'self',
                              colors, 'SetLookupTable')
layoutAndAdd(lookup, lookup_colors)

dataL123 = newModule(vtkpkg, 'vtkDataSetReader')
dataL123_colors = newConnection(dataL123, 'GetOutputPort0',
                                colors, 'SetInputConnection0')
layoutAndAdd(dataL123, dataL123_colors)

httpL123 = newModule(httppkg, 'HTTPFile')
url = 'http://www.vistrails.org/download/download.php?type=DATA&id=gktbhL123.vtk'
setPortValue(httpL123, 'url', url)
httpL123_dataL123 = newConnection(httpL123, 'file',
                                  dataL123, 'SetFile')
layoutAndAdd(httpL123, httpL123_dataL123)

#finish bottom section
mapper = newModule(vtkpkg, 'vtkPolyDataMapper')
setPortValue(mapper, 'ScalarVisibilityOn', True)
probe_mapper = newConnection(probe, 'GetOutputPort0',
                             mapper, 'SetInputConnection0')
layoutAndAdd(mapper, probe_mapper)

actor = newModule(vtkpkg, 'vtkActor')
mapper_actor = newConnection(mapper, 'self',
                             actor, 'SetMapper')
layoutAndAdd(actor, mapper_actor)

prop = newModule(vtkpkg, 'vtkProperty')
setPortValue(prop, 'SetDiffuseColor', (1.0,0.49,0.25))
setPortValue(prop, 'SetOpacity', 0.7)
setPortValue(prop, 'SetSpecular', 0.3)
setPortValue(prop, 'SetSpecularPower', 2.0)
prop_actor = newConnection(prop, 'self',
                           actor, 'SetProperty')
layoutAndAdd(prop, prop_actor)

renderer = newModule(vtkpkg, 'vtkRenderer')
setPortValue(renderer, 'SetBackgroundWidget', 'white')
actor_renderer = newConnection(actor, 'self',
                               renderer, 'AddActor')
layoutAndAdd(renderer, actor_renderer)

camera = newModule(vtkpkg, 'vtkCamera')
setPortValue(camera, 'SetFocalPoint', (15.666,40.421,39.991))
setPortValue(camera, 'SetPosition', (207.961,34.197,129.680))
setPortValue(camera, 'SetViewUp', (0.029, 1.0, 0.008))
camera_renderer = newConnection(camera, 'self',
                                renderer, 'SetActiveCamera')
layoutAndAdd(camera, camera_renderer)

#this is missing when running from script??
# cell = newModule(vtkpkg, 'VTKCell')
# cell = newModule(vtkpkg, 'vtkCell')
# renderer_cell = newConnection(renderer, 'self',
#                               cell, 'AddRenderer')
# layoutAndAdd(cell, renderer_cell)

#add book 3rd p189 example

qcActor = newModule(vtkpkg, 'vtkActor')
qcActor_renderer = newConnection(qcActor, 'self',
                                 renderer, 'AddActor')
layoutAndAdd(qcActor, qcActor_renderer)

qcMapper = newModule(vtkpkg, 'vtkPolyDataMapper')
qcMapper_actor = newConnection(qcMapper, 'self',
                               qcActor, 'SetMapper')
layoutAndAdd(qcMapper, qcMapper_actor)

qContour = newModule(vtkpkg, 'vtkContourFilter')
setPortValue(qContour, 'GenerateValues', (5,0,1.2))
qContour_mapper = newConnection(qContour, 'GetOutputPort0',
                                qcMapper, 'SetInputConnection0')
layoutAndAdd(qContour, qContour_mapper)

sample = newModule(vtkpkg, 'vtkSampleFunction')
setPortValue(sample, 'SetSampleDimensions', (50,50,50))
sample_qContour = newConnection(sample, 'GetOutputPort0',
                                qContour, 'SetInputConnection0')
layoutAndAdd(sample, sample_qContour)

quad = newModule(vtkpkg, 'vtkQuadric')
setPortValue(quad, 'SetCoefficients', (0.5,1,0.2,0,0.1,0,0,0.2,0,0))
quad_sample = newConnection(quad, 'self',
                            sample, 'SetImplicitFunction')
layoutAndAdd(quad, quad_sample)

oActor = newModule(vtkpkg, 'vtkActor')
oActor_renderer = newConnection(oActor, 'self',
                                renderer, 'AddActor')
layoutAndAdd(oActor, oActor_renderer)

oProp = newModule(vtkpkg, 'vtkProperty')
setPortValue(oProp, 'SetColor', (0,0,0))
oProp_actor = newConnection(oProp, 'self',
                            oActor, 'SetProperty')
layoutAndAdd(oProp, oProp_actor)

oMapper = newModule(vtkpkg, 'vtkPolyDataMapper')
oMapper_actor = newConnection(oMapper, 'self',
                              oActor, 'SetMapper')
layoutAndAdd(oMapper, oMapper_actor)

outline = newModule(vtkpkg, 'vtkOutlineFilter')
outline_mapper = newConnection(outline, 'GetOutputPort0',
                               oMapper, 'SetInputConnection0')
sample_outline = newConnection(sample, 'GetOutputPort0',
                               outline, 'SetInputConnection0')
layoutAndAdd(outline, [outline_mapper, sample_outline])

#write to file
locator = vistrails.core.db.locator.FileLocator('incremental_layout_combined.vt')
controller.write_vistrail(locator)
