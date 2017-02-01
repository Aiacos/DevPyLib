import pymel.core as pm

jiggle = 0.2

selection = pm.ls('iControlMid*')
print selection

for item in selection:
    #print item.name()
    str =  item.name().encode('utf8')
    if '_crossSection' not in item.name().encode('utf8'):
        if 'Constraint' not in item.name().encode('utf8'):
            print item.name().encode('utf8')
            item.jiggle.set(jiggle)