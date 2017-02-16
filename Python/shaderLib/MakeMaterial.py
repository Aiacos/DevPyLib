__author__ = 'Lorenzo Argentieri'

import maya.cmds as cmds
import pymel.core as pm

## Variables ##

shaderName = ''

path = cmds.workspace(q=True, dir=True) + '/sourceimages/'

imgFormat = '.exr'

diffuse = '_Diffuse' + imgFormat  # Color
backlighting = '_Backlighting' + imgFormat  # Kb
specularColor = '_Reflection' + imgFormat  # KsColor
specularWeight = '_SpecularWeight' + imgFormat  # Ks
specularRoughness = '_Roughness' + imgFormat  # specularRoughness
fresnel = '_f0' + imgFormat  # Ksn
normal = '_Normal' + imgFormat  # normalCamera

# Settings

singlePlaceNode = True
specularW = False
useGammaCorrect = True


# Function

def connectPlacement(place_node, file_node):
    cmds.connectAttr('%s.coverage' % place_node, '%s.coverage' % file_node)
    cmds.connectAttr('%s.translateFrame' % place_node, '%s.translateFrame' % file_node)
    cmds.connectAttr('%s.rotateFrame' % place_node, '%s.rotateFrame' % file_node)
    cmds.connectAttr('%s.mirrorU' % place_node, '%s.mirrorU' % file_node)
    cmds.connectAttr('%s.mirrorV' % place_node, '%s.mirrorV' % file_node)
    cmds.connectAttr('%s.stagger' % place_node, '%s.stagger' % file_node)
    cmds.connectAttr('%s.wrapU' % place_node, '%s.wrapU' % file_node)
    cmds.connectAttr('%s.wrapV' % place_node, '%s.wrapV' % file_node)
    cmds.connectAttr('%s.repeatUV' % place_node, '%s.repeatUV' % file_node)
    cmds.connectAttr('%s.offset' % place_node, '%s.offset' % file_node)
    cmds.connectAttr('%s.rotateUV' % place_node, '%s.rotateUV' % file_node)
    cmds.connectAttr('%s.noiseUV' % place_node, '%s.noiseUV' % file_node)
    cmds.connectAttr('%s.vertexUvOne' % place_node, '%s.vertexUvOne' % file_node)
    cmds.connectAttr('%s.vertexUvTwo' % place_node, '%s.vertexUvTwo' % file_node)
    cmds.connectAttr('%s.vertexUvThree' % place_node, '%s.vertexUvThree' % file_node)
    cmds.connectAttr('%s.vertexCameraOne' % place_node, '%s.vertexCameraOne' % file_node)
    cmds.connectAttr('%s.outUV' % place_node, '%s.uv' % file_node)
    cmds.connectAttr('%s.outUvFilterSize' % place_node, '%s.uvFilterSize' % file_node)


def gammaNode(gammaName):
    gamma = cmds.shadingNode("gammaCorrect", asUtility=True, name=gammaName)
    cmds.setAttr(gamma + '.gammaX', 0.454)
    cmds.setAttr(gamma + '.gammaY', 0.454)
    cmds.setAttr(gamma + '.gammaZ', 0.454)
    return gamma


def makeShader(shaderName):
    # create a shader
    shader = cmds.shadingNode("aiStandard", asShader=True, name=shaderName)

    # a file texture node
    # diffuse
    file_node_diffuse = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_diffuse + '.fileTextureName', path + shaderName + diffuse, type='string')
    # specularColor
    file_node_specularColor = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_specularColor + '.fileTextureName', path + shaderName + specularColor, type='string')
    # specularWeight
    if specularW:
        cmds.setAttr('%s.Ks' % shader, 1)
    else:
        file_node_specularWeight = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node_specularWeight + '.fileTextureName', path + shaderName + specularWeight, type='string')
        cmds.setAttr(file_node_specularWeight + '.alphaIsLuminance', True)
    # specularRoughness
    file_node_specularRoughness = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_specularRoughness + '.fileTextureName', path + shaderName + specularRoughness, type='string')
    cmds.setAttr(file_node_specularRoughness + '.alphaIsLuminance', True)
    # fresnel
    file_node_fresnel = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_fresnel + '.fileTextureName', path + shaderName + fresnel, type='string')
    cmds.setAttr(file_node_fresnel + '.alphaIsLuminance', True)
    cmds.setAttr(shader + '.specularFresnel', True)
    # normal
    bump_node = cmds.shadingNode("bump2d", asUtility=True)
    cmds.setAttr(bump_node + '.bumpInterp', 1)
    cmds.setAttr(bump_node + '.aiFlipR', 0)
    cmds.setAttr(bump_node + '.aiFlipG', 0)
    file_node_normal = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_normal + '.fileTextureName', path + shaderName + normal, type='string')
    cmds.setAttr(file_node_normal + '.alphaIsLuminance', True)

    # a shading group
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)

    # connect file texture node to shader's slot
    ## Color Node:
    if useGammaCorrect:
        colorGamma = gammaNode('colorGamma')
        cmds.connectAttr('%s.outColor' % file_node_diffuse, '%s.value' % colorGamma)
        cmds.connectAttr('%s.value' % colorGamma, '%s.color' % shader)

        ksColorGamma = gammaNode('ksColorGamma')
        cmds.connectAttr('%s.outColor' % file_node_specularColor, '%s.value' % ksColorGamma)
        cmds.connectAttr('%s.value' % ksColorGamma, '%s.KsColor' % shader)
    else:
        cmds.connectAttr('%s.outColor' % file_node_diffuse, '%s.color' % shader)
        cmds.connectAttr('%s.outColor' % file_node_specularColor, '%s.KsColor' % shader)
    ##
    if specularW == False:
        cmds.connectAttr('%s.outAlpha' % file_node_specularWeight, '%s.Ks' % shader)
    cmds.connectAttr('%s.outAlpha' % file_node_specularRoughness, '%s.specularRoughness' % shader)
    cmds.connectAttr('%s.outAlpha' % file_node_fresnel, '%s.Ksn' % shader)
    cmds.connectAttr('%s.outNormal' % bump_node, '%s.normalCamera' % shader)
    cmds.connectAttr('%s.outAlpha' % file_node_normal, '%s.bumpValue' % bump_node)

    ## place node connect
    if singlePlaceNode:
        place_node = cmds.shadingNode('place2dTexture', asUtility=True)
        connectPlacement(place_node, file_node_diffuse)
        connectPlacement(place_node, file_node_specularColor)
        if specularW == False:
            connectPlacement(place_node, file_node_specularWeight)
        connectPlacement(place_node, file_node_specularRoughness)
        connectPlacement(place_node, file_node_fresnel)
        connectPlacement(place_node, file_node_normal)
    else:
        place_node_diffuse = cmds.shadingNode('place2dTexture', asUtility=True)
        place_node_specularColor = cmds.shadingNode('place2dTexture', asUtility=True)
        if specularW == False:
            place_node_specularWeight = cmds.shadingNode('place2dTexture', asUtility=True)
        place_node_specularRoughness = cmds.shadingNode('place2dTexture', asUtility=True)
        place_node_fresnel = cmds.shadingNode('place2dTexture', asUtility=True)
        place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)

        connectPlacement(place_node_diffuse, file_node_diffuse)
        connectPlacement(place_node_specularColor, file_node_specularColor)
        if specularW == False:
            connectPlacement(place_node_specularWeight, file_node_specularWeight)
        connectPlacement(place_node_specularRoughness, file_node_specularRoughness)
        connectPlacement(place_node_fresnel, file_node_fresnel)
        connectPlacement(place_node_normal, file_node_normal)


### --- Nuove Funzioni --- ###

def connect_diffuse(shader, path, ShaderName, diffuse, outSocket, gammaCorrect=False, singlePlaceNode=False):
    # creation node
    file_node_diffuse = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_diffuse + '.fileTextureName', path + shaderName + diffuse, type='string')

    # connection node
    if gammaCorrect:
        colorGamma = gammaNode('colorGamma')
        cmds.connectAttr('%s.outColor' % file_node_diffuse, '%s.value' % colorGamma)
        cmds.connectAttr('%s.value' % colorGamma, '%s.' + outSocket % shader)
    else:
        cmds.connectAttr('%s.outColor' % file_node_diffuse, shader + '.' + outSocket)
    ##

    ## place node connect
    if singlePlaceNode:
        connectPlacement(singlePlaceNode, file_node_diffuse)
    else:
        place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
        connectPlacement(place_node_normal, file_node_diffuse)

    return file_node_diffuse


def connect_backlighting(shader, path, ShaderName, backlighting, outSocket, gammaCorrect=False, singlePlaceNode=False):
    # creation node
    file_node_backlighting = ''
    # creation node
    try:
        file_node_backlighting = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node_backlighting + '.fileTextureName', path + shaderName + specularWeight, type='string')
        cmds.setAttr(file_node_backlighting + '.alphaIsLuminance', True)

        # connection node
        cmds.connectAttr('%s.outAlpha' % file_node_backlighting, shader + '.' + outSocket)

        ## place node connect
        if singlePlaceNode:
            connectPlacement(singlePlaceNode, file_node_backlighting)
        else:
            place_node_backlighting = cmds.shadingNode('place2dTexture', asUtility=True)
            connectPlacement(place_node_backlighting, file_node_backlighting)
    except:  ##specularW:
        pass

    return file_node_backlighting


def connect_specularColor(shader, path, ShaderName, specularColor, outSocket, gammaCorrect=False,
                          singlePlaceNode=False):
    # creation node
    try:
        file_node_specularColor = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node_specularColor + '.fileTextureName', path + shaderName + specularColor, type='string')

        # connection node
        if gammaCorrect:
            ksColorGamma = gammaNode('ksColorGamma')
            cmds.connectAttr('%s.outColor' % file_node_specularColor, '%s.value' % ksColorGamma)
            cmds.connectAttr('%s.value' % ksColorGamma, '%s.' + outSocket % shader)
        else:
            cmds.connectAttr('%s.outColor' % file_node_specularColor, shader + '.' + outSocket)

        ## place node connect
        if singlePlaceNode:
            connectPlacement(singlePlaceNode, file_node_specularColor)
        else:
            place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
            connectPlacement(place_node_normal, file_node_specularColor)
    except:
        pass

    return file_node_specularColor


def connect_specularWeight(shader, path, ShaderName, specularWeight, outSocket, outValue=1, gammaCorrect=False,
                           singlePlaceNode=False):
    # creation node
    try:
        file_node_specularWeight = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node_specularWeight + '.fileTextureName', path + shaderName + specularWeight, type='string')
        cmds.setAttr(file_node_specularWeight + '.alphaIsLuminance', True)

        # connection node
        cmds.connectAttr('%s.outAlpha' % file_node_specularWeight, shader + '.' + outSocket)

        ## place node connect
        if singlePlaceNode:
            connectPlacement(singlePlaceNode, file_node_specularWeight)
        else:
            place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
            connectPlacement(place_node_normal, file_node_specularWeight)
    except:  ##specularW:
        cmds.setAttr('%s.' + outSocket % shader, outValue)

    return file_node_specularWeight


def connect_specularRoughness(shader, path, ShaderName, specularRoughness, outSocket, gammaCorrect=False,
                              singlePlaceNode=False):
    # creation node
    file_node_specularRoughness = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_specularRoughness + '.fileTextureName', path + shaderName + specularRoughness, type='string')
    cmds.setAttr(file_node_specularRoughness + '.alphaIsLuminance', True)

    # connection node
    cmds.connectAttr('%s.outAlpha' % file_node_specularRoughness, shader + '.' + outSocket)

    ## place node connect
    if singlePlaceNode:
        connectPlacement(singlePlaceNode, file_node_specularRoughness)
    else:
        place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
        connectPlacement(place_node_normal, file_node_specularRoughness)

    return file_node_specularRoughness


def connect_fresnel(shader, path, ShaderName, fresnel, outSocket, outValue=0.039, gammaCorrect=False,
                    singlePlaceNode=False):
    # creation node
    try:
        file_node_fresnel = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
        cmds.setAttr(file_node_fresnel + '.fileTextureName', path + shaderName + fresnel, type='string')
        cmds.setAttr(file_node_fresnel + '.alphaIsLuminance', True)
        cmds.setAttr(shader + '.specularFresnel', True)  ##diverso in MentalRay, utilizza '.refl_is_metal'

        # connection node
        cmds.connectAttr('%s.outAlpha' % file_node_fresnel, shader + '.' + outSocket)

        ## place node connect
        if singlePlaceNode:
            connectPlacement(singlePlaceNode, file_node_fresnel)
        else:
            place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
            connectPlacement(place_node_normal, file_node_fresnel)
    except:
        cmds.setAttr('%s.' + outSocket % shader, outValue)

    return file_node_fresnel


def connect_normal(shader, path, ShaderName, normal, outSocket, gammaCorrect=False, singlePlaceNode=False):
    # creation node
    bump_node = cmds.shadingNode("bump2d", asUtility=True)
    cmds.setAttr(bump_node + '.bumpInterp', 1)
    cmds.setAttr(bump_node + '.aiFlipR', 0)
    cmds.setAttr(bump_node + '.aiFlipG', 0)
    file_node_normal = cmds.shadingNode("file", asTexture=True, isColorManaged=True)
    cmds.setAttr(file_node_normal + '.fileTextureName', path + shaderName + normal, type='string')
    cmds.setAttr(file_node_normal + '.alphaIsLuminance', True)

    # connection node
    cmds.connectAttr('%s.outNormal' % bump_node, shader + '.' + outSocket)
    cmds.connectAttr('%s.outAlpha' % file_node_normal, '%s.bumpValue' % bump_node)

    ## place node connect
    if singlePlaceNode:
        connectPlacement(singlePlaceNode, file_node_normal)
    else:
        place_node_normal = cmds.shadingNode('place2dTexture', asUtility=True)
        connectPlacement(place_node_normal, file_node_normal)

    return bump_node


# shader type
def makeAiStandard(path, ShaderName, singlePlaceNode=True):
    # create a shader
    shader = cmds.shadingNode("aiStandard", asShader=True, name=shaderName)

    if singlePlaceNode:
        place_node = cmds.shadingNode('place2dTexture', asUtility=True)
    else:
        place_node = False

    ####
    connect_diffuse(shader, path, ShaderName, diffuse, outSocket='color', gammaCorrect=True, singlePlaceNode=place_node)
    connect_backlighting(shader, path, ShaderName, backlighting, outSocket='Kb', gammaCorrect=False,
                         singlePlaceNode=place_node)
    connect_specularColor(shader, path, ShaderName, specularColor, outSocket='KsColor', gammaCorrect=True,
                          singlePlaceNode=place_node)
    connect_specularWeight(shader, path, ShaderName, specularWeight, outSocket='Ks', gammaCorrect=False,
                           singlePlaceNode=place_node)
    connect_specularRoughness(shader, path, ShaderName, specularRoughness, outSocket='specularRoughness',
                              gammaCorrect=False, singlePlaceNode=place_node)
    connect_fresnel(shader, path, ShaderName, fresnel, outSocket='Ksn', gammaCorrect=False, singlePlaceNode=place_node)
    connect_normal(shader, path, ShaderName, normal, outSocket='normalCamera', gammaCorrect=False,
                   singlePlaceNode=place_node)

    return shader


def makeMia_Material_X(path, ShaderName, singlePlaceNode=True):  ## Not tested
    # create a shader
    shader = cmds.shadingNode("aiStandard", asShader=True, name=shaderName)

    if singlePlaceNode:
        place_node = cmds.shadingNode('place2dTexture', asUtility=True)
    else:
        place_node = False

    ####
    connect_diffuse(shader, path, ShaderName, diffuse, outSocket='diffuse', gammaCorrect=False,
                    singlePlaceNode=place_node)  # ok
    connect_backlighting(shader, path, ShaderName, backlighting, outSocket='Kb', gammaCorrect=False,
                         singlePlaceNode=place_node)  # non esiste
    connect_specularColor(shader, path, ShaderName, specularColor, outSocket='refl_color', gammaCorrect=False,
                          singlePlaceNode=place_node)  # ok
    connect_specularWeight(shader, path, ShaderName, specularWeight, outSocket='reflectivity', gammaCorrect=False,
                           singlePlaceNode=place_node)  # ok
    connect_specularRoughness(shader, path, ShaderName, specularRoughness, outSocket='refl_gloss', gammaCorrect=False,
                              singlePlaceNode=place_node)  # ok
    connect_fresnel(shader, path, ShaderName, fresnel, outSocket='brdf_0_degree_refl', gammaCorrect=False,
                    singlePlaceNode=place_node)  # fallirebbe, check non presente
    connect_normal(shader, path, ShaderName, normal, outSocket='standard_bump', gammaCorrect=False,
                   singlePlaceNode=place_node)  # ok

    return shader


def makeShader2(ShaderName):  ##add shader type (in parameters)
    # set other path
    # add ricerca texture

    # See active Renderer
    renderer = cmds.getAttr('defaultRenderGlobals.currentRenderer')
    if renderer == 'arnold':
        shader = makeAiStandard(path, ShaderName)
    elif renderer == 'mentalRay':
        shader = makeMia_Material_X(path, ShaderName)
    elif renderer == 'renderman':
        print 'Not configured yet!'
    elif renderer == 'vray':
        print 'Not configured yet!'
    else:
        print 'Renderer not exist!'

    # a shading group
    shading_group = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name=shaderName)
    # connect shader to sg surface shader
    cmds.connectAttr('%s.outColor' % shader, '%s.surfaceShader' % shading_group)


# -----------------------------------------------------------------------------------------------------------------------
## Main ##
## Gui ##

result = cmds.promptDialog(
    title='makeShader',
    message='Enter Name:',
    button=['OK', 'Cancel'],
    defaultButton='OK',
    cancelButton='Cancel',
    dismissString='Cancel')

if result == 'OK':
    shaderName = cmds.promptDialog(query=True, text=True)
    makeShader2(shaderName)

    # -----------------------------------------------------------------------------------------------------------------------

    # -toDo
    # ricerca texture
    # interfaccia Qt
    # emission function
