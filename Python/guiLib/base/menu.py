import pymel.core as pm

try:
    lib_menu.delete()
    print 'deleted'
except:
    lib_menu = pm.menu(label='Test3', tearOff=True)
    it4 = pm.menuItem('test1', parent=lib_menu.name())
    it5 = pm.menuItem('test2', parent=lib_menu.name())
    it6 = pm.menuItem('test3', parent=lib_menu.name())
    print 'added'


