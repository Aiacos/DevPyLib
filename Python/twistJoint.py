import pymel.core as pm

head_jnt = pm.ls(sl=True)[0]
head_t = pm.xform(q=True, t=True)
pm.pickWalk(d='down')
tail_jnt = pm.ls(sl=True)[0]
tail_t = pm.xform(q=True, t=True)

head_loc = pm.spaceLocator(p=head_t)
tail_loc = pm.spaceLocator(p=tail_t)
distance = pm.distanceDimension(head_loc, tail_loc)

print distance
