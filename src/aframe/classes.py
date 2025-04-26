import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
import cv2.aruco as aruco
import os
import pickle
from random import randint
import time
import subprocess
import PySimpleGUI as sg

"""
TODO - 
	modify AFrame class-
		uses:
			m = Marker(rows=5, cols=5, cell_size=100)
		add function -
			addMarker(markerid, value, dtype(optional))
"""

def objtogltf(filepath):
	filepath2 = f"{os.path.splitext(filepath)[0]}.gltf"
	com = f"obj2gltf -i {filepath} -o {filepath2}"
	return subprocess.check_output(com, shell=True).decode().strip()

def parse_primitive(text):
	lines = f"""{text}""".replace('	', ',').splitlines()
	out = {}
	for line in lines:
		try:
			a, c, d = line.split(',')
		except:
			s = line.split(',')
			a, c, d = s[0], s[1], None
		out[a] = {}
		out[a]['mapping'] = c
		if d == '' or d == ' ':
			d = None
		out[a]['default'] = d
	return out

class Defaults():
	def __init__(self, element=None):
		if element is not None:
			if 'a-' in element:
				element = element.split('a-')[1]
			self.element = element
			self.defaults = self.get(element=element)
		else:
			self.element = None
			self.defaults = {}
	def box(self):
		return {'alpha-test': {'mapping': 'material.alphaTest', 'default': '0'}, 'ambient-occlusion-map': {'mapping': 'material.ambientOcclusionMap', 'default': 'None'}, 'ambient-occlusion-map-intensity': {'mapping': 'material.ambientOcclusionMapIntensity', 'default': '1'}, 'ambient-occlusion-texture-offset': {'mapping': 'material.ambientOcclusionTextureOffset', 'default': '0 0'}, 'ambient-occlusion-texture-repeat': {'mapping': 'material.ambientOcclusionTextureRepeat', 'default': '1 1'}, 'anisotropy': {'mapping': 'material.anisotropy', 'default': '0'}, 'blending': {'mapping': 'material.blending', 'default': 'normal'}, 'color': {'mapping': 'material.color', 'default': '#fc1c03'}, 'depth': {'mapping': 'geometry.depth', 'default': '1'}, 'depth-test': {'mapping': 'material.depthTest', 'default': 'true'}, 'depth-write': {'mapping': 'material.depthWrite', 'default': 'true'}, 'displacement-bias': {'mapping': 'material.displacementBias', 'default': '0.5'}, 'displacement-map': {'mapping': 'material.displacementMap', 'default': 'None'}, 'displacement-scale': {'mapping': 'material.displacementScale', 'default': '1'}, 'displacement-texture-offset': {'mapping': 'material.displacementTextureOffset', 'default': '0 0'}, 'displacement-texture-repeat': {'mapping': 'material.displacementTextureRepeat', 'default': '1 1'}, 'dithering': {'mapping': 'material.dithering', 'default': 'true'}, 'emissive': {'mapping': 'material.emissive', 'default': '#000'}, 'emissive-intensity': {'mapping': 'material.emissiveIntensity', 'default': '1'}, 'env-map': {'mapping': 'material.envMap', 'default': 'None'}, 'flat-shading': {'mapping': 'material.flatShading', 'default': 'false'}, 'height': {'mapping': 'geometry.height', 'default': '1'}, 'material-fog': {'mapping': 'material.fog', 'default': 'true'}, 'material-visible': {'mapping': 'material.visible', 'default': 'true'}, 'metalness': {'mapping': 'material.metalness', 'default': '0'}, 'metalness-map': {'mapping': 'material.metalnessMap', 'default': 'None'}, 'metalness-texture-offset': {'mapping': 'material.metalnessTextureOffset', 'default': '0 0'}, 'metalness-texture-repeat': {'mapping': 'material.metalnessTextureRepeat', 'default': '1 1'}, 'normal-map': {'mapping': 'material.normalMap', 'default': 'None'}, 'normal-scale': {'mapping': 'material.normalScale', 'default': '1 1'}, 'normal-texture-offset': {'mapping': 'material.normalTextureOffset', 'default': '0 0'}, 'normal-texture-repeat': {'mapping': 'material.normalTextureRepeat', 'default': '1 1'}, 'npot': {'mapping': 'material.npot', 'default': 'false'}, 'offset': {'mapping': 'material.offset', 'default': '0 0'}, 'opacity': {'mapping': 'material.opacity', 'default': '1'}, 'repeat': {'mapping': 'material.repeat', 'default': '1 1'}, 'roughness': {'mapping': 'material.roughness', 'default': '0.5'}, 'roughness-map': {'mapping': 'material.roughnessMap', 'default': 'None'}, 'roughness-texture-offset': {'mapping': 'material.roughnessTextureOffset', 'default': '0 0'}, 'roughness-texture-repeat': {'mapping': 'material.roughnessTextureRepeat', 'default': '1 1'}, 'segments-depth': {'mapping': 'geometry.segmentsDepth', 'default': '1'}, 'segments-height': {'mapping': 'geometry.segmentsHeight', 'default': '1'}, 'segments-width': {'mapping': 'geometry.segmentsWidth', 'default': '1'}, 'shader': {'mapping': 'material.shader', 'default': 'standard'}, 'side': {'mapping': 'material.side', 'default': 'front'}, 'spherical-env-map': {'mapping': 'material.sphericalEnvMap', 'default': 'None'}, 'src': {'mapping': 'material.src', 'default': 'None'}, 'transparent': {'mapping': 'material.transparent', 'default': 'false'}, 'vertex-colors-enabled': {'mapping': 'material.vertexColorsEnabled', 'default': 'false'}, 'width': {'mapping': 'geometry.width', 'default': '1'}, 'wireframe': {'mapping': 'material.wireframe', 'default': 'false'}, 'wireframe-linewidth': {'mapping': 'material.wireframeLinewidth', 'default': '2'}}
	def camera(self):
		return {'far': {'mapping': 'camera.far', 'default': '10000'}, 'fov': {'mapping': 'camera.fov', 'default': '80'}, 'look-controls-enabled': {'mapping': 'look-controls.enabled', 'default': 'true'}, 'near': {'mapping': 'camera.near', 'default': '0.5'}, 'reverse-mouse-drag': {'mapping': 'look-controls.reverseMouseDrag', 'default': 'false'}, 'wasd-controls-enabled': {'mapping': 'wasd-controls.enabled', 'default': 'true'}}
	def circle(self):
		return {'alpha-test': {'mapping': 'material.alphaTest', 'default': '0'}, 'ambient-occlusion-map': {'mapping': 'material.ambientOcclusionMap', 'default': 'None'}, 'ambient-occlusion-map-intensity': {'mapping': 'material.ambientOcclusionMapIntensity', 'default': '1'}, 'ambient-occlusion-texture-offset': {'mapping': 'material.ambientOcclusionTextureOffset', 'default': '0 0'}, 'ambient-occlusion-texture-repeat': {'mapping': 'material.ambientOcclusionTextureRepeat', 'default': '1 1'}, 'anisotropy': {'mapping': 'material.anisotropy', 'default': '0'}, 'blending': {'mapping': 'material.blending', 'default': 'normal'}, 'color': {'mapping': 'material.color', 'default': '#fc1c03'}, 'depth-test': {'mapping': 'material.depthTest', 'default': 'true'}, 'depth-write': {'mapping': 'material.depthWrite', 'default': 'true'}, 'displacement-bias': {'mapping': 'material.displacementBias', 'default': '0.5'}, 'displacement-map': {'mapping': 'material.displacementMap', 'default': 'None'}, 'displacement-scale': {'mapping': 'material.displacementScale', 'default': '1'}, 'displacement-texture-offset': {'mapping': 'material.displacementTextureOffset', 'default': '0 0'}, 'displacement-texture-repeat': {'mapping': 'material.displacementTextureRepeat', 'default': '1 1'}, 'dithering': {'mapping': 'material.dithering', 'default': 'true'}, 'emissive': {'mapping': 'material.emissive', 'default': '#000'}, 'emissive-intensity': {'mapping': 'material.emissiveIntensity', 'default': '1'}, 'env-map': {'mapping': 'material.envMap', 'default': 'None'}, 'flat-shading': {'mapping': 'material.flatShading', 'default': 'false'}, 'height': {'mapping': 'material.height', 'default': '256'}, 'material-fog': {'mapping': 'material.fog', 'default': 'true'}, 'material-visible': {'mapping': 'material.visible', 'default': 'true'}, 'metalness': {'mapping': 'material.metalness', 'default': '0'}, 'metalness-map': {'mapping': 'material.metalnessMap', 'default': 'None'}, 'metalness-texture-offset': {'mapping': 'material.metalnessTextureOffset', 'default': '0 0'}, 'metalness-texture-repeat': {'mapping': 'material.metalnessTextureRepeat', 'default': '1 1'}, 'normal-map': {'mapping': 'material.normalMap', 'default': 'None'}, 'normal-scale': {'mapping': 'material.normalScale', 'default': '1 1'}, 'normal-texture-offset': {'mapping': 'material.normalTextureOffset', 'default': '0 0'}, 'normal-texture-repeat': {'mapping': 'material.normalTextureRepeat', 'default': '1 1'}, 'npot': {'mapping': 'material.npot', 'default': 'false'}, 'offset': {'mapping': 'material.offset', 'default': '0 0'}, 'opacity': {'mapping': 'material.opacity', 'default': '1'}, 'radius': {'mapping': 'geometry.radius', 'default': '1'}, 'repeat': {'mapping': 'material.repeat', 'default': '1 1'}, 'roughness': {'mapping': 'material.roughness', 'default': '0.5'}, 'roughness-map': {'mapping': 'material.roughnessMap', 'default': 'None'}, 'roughness-texture-offset': {'mapping': 'material.roughnessTextureOffset', 'default': '0 0'}, 'roughness-texture-repeat': {'mapping': 'material.roughnessTextureRepeat', 'default': '1 1'}, 'segments': {'mapping': 'geometry.segments', 'default': '32'}, 'shader': {'mapping': 'material.shader', 'default': 'standard'}, 'side': {'mapping': 'material.side', 'default': 'front'}, 'spherical-env-map': {'mapping': 'material.sphericalEnvMap', 'default': 'None'}, 'src': {'mapping': 'material.src', 'default': 'None'}, 'theta-length': {'mapping': 'geometry.thetaLength', 'default': '360'}, 'theta-start': {'mapping': 'geometry.thetaStart', 'default': '0'}, 'transparent': {'mapping': 'material.transparent', 'default': 'false'}, 'vertex-colors-enabled': {'mapping': 'material.vertexColorsEnabled', 'default': 'false'}, 'width': {'mapping': 'material.width', 'default': '512'}, 'wireframe': {'mapping': 'material.wireframe', 'default': 'false'}, 'wireframe-linewidth': {'mapping': 'material.wireframeLinewidth', 'default': '2'}}
	def cone(self):
		return {'alpha-test': {'mapping': 'material.alphaTest', 'default': '0'}, 'ambient-occlusion-map': {'mapping': 'material.ambientOcclusionMap', 'default': 'None'}, 'ambient-occlusion-map-intensity': {'mapping': 'material.ambientOcclusionMapIntensity', 'default': '1'}, 'ambient-occlusion-texture-offset': {'mapping': 'material.ambientOcclusionTextureOffset', 'default': '0 0'}, 'ambient-occlusion-texture-repeat': {'mapping': 'material.ambientOcclusionTextureRepeat', 'default': '1 1'}, 'anisotropy': {'mapping': 'material.anisotropy', 'default': '0'}, 'blending': {'mapping': 'material.blending', 'default': 'normal'}, 'color': {'mapping': 'material.color', 'default': '#fc1c03'}, 'depth-test': {'mapping': 'material.depthTest', 'default': 'true'}, 'depth-write': {'mapping': 'material.depthWrite', 'default': 'true'}, 'displacement-bias': {'mapping': 'material.displacementBias', 'default': '0.5'}, 'displacement-map': {'mapping': 'material.displacementMap', 'default': 'None'}, 'displacement-scale': {'mapping': 'material.displacementScale', 'default': '1'}, 'displacement-texture-offset': {'mapping': 'material.displacementTextureOffset', 'default': '0 0'}, 'displacement-texture-repeat': {'mapping': 'material.displacementTextureRepeat', 'default': '1 1'}, 'dithering': {'mapping': 'material.dithering', 'default': 'true'}, 'emissive': {'mapping': 'material.emissive', 'default': '#000'}, 'emissive-intensity': {'mapping': 'material.emissiveIntensity', 'default': '1'}, 'env-map': {'mapping': 'material.envMap', 'default': 'None'}, 'flat-shading': {'mapping': 'material.flatShading', 'default': 'false'}, 'height': {'mapping': 'geometry.height', 'default': '1'}, 'material-fog': {'mapping': 'material.fog', 'default': 'true'}, 'material-visible': {'mapping': 'material.visible', 'default': 'true'}, 'metalness': {'mapping': 'material.metalness', 'default': '0'}, 'metalness-map': {'mapping': 'material.metalnessMap', 'default': 'None'}, 'metalness-texture-offset': {'mapping': 'material.metalnessTextureOffset', 'default': '0 0'}, 'metalness-texture-repeat': {'mapping': 'material.metalnessTextureRepeat', 'default': '1 1'}, 'normal-map': {'mapping': 'material.normalMap', 'default': 'None'}, 'normal-scale': {'mapping': 'material.normalScale', 'default': '1 1'}, 'normal-texture-offset': {'mapping': 'material.normalTextureOffset', 'default': '0 0'}, 'normal-texture-repeat': {'mapping': 'material.normalTextureRepeat', 'default': '1 1'}, 'npot': {'mapping': 'material.npot', 'default': 'false'}, 'offset': {'mapping': 'material.offset', 'default': '0 0'}, 'opacity': {'mapping': 'material.opacity', 'default': '1'}, 'open-ended': {'mapping': 'geometry.openEnded', 'default': 'false'}, 'radius-bottom': {'mapping': 'geometry.radiusBottom', 'default': '1'}, 'radius-top': {'mapping': 'geometry.radiusTop', 'default': '0.01'}, 'repeat': {'mapping': 'material.repeat', 'default': '1 1'}, 'roughness': {'mapping': 'material.roughness', 'default': '0.5'}, 'roughness-map': {'mapping': 'material.roughnessMap', 'default': 'None'}, 'roughness-texture-offset': {'mapping': 'material.roughnessTextureOffset', 'default': '0 0'}, 'roughness-texture-repeat': {'mapping': 'material.roughnessTextureRepeat', 'default': '1 1'}, 'segments-height': {'mapping': 'geometry.segmentsHeight', 'default': '18'}, 'segments-radial': {'mapping': 'geometry.segmentsRadial', 'default': '36'}, 'shader': {'mapping': 'material.shader', 'default': 'standard'}, 'side': {'mapping': 'material.side', 'default': 'front'}, 'spherical-env-map': {'mapping': 'material.sphericalEnvMap', 'default': 'None'}, 'src': {'mapping': 'material.src', 'default': 'None'}, 'theta-length': {'mapping': 'geometry.thetaLength', 'default': '360'}, 'theta-start': {'mapping': 'geometry.thetaStart', 'default': '0'}, 'transparent': {'mapping': 'material.transparent', 'default': 'false'}, 'vertex-colors-enabled': {'mapping': 'material.vertexColorsEnabled', 'default': 'false'}, 'width': {'mapping': 'material.width', 'default': '512'}, 'wireframe': {'mapping': 'material.wireframe', 'default': 'false'}, 'wireframe-linewidth': {'mapping': 'material.wireframeLinewidth', 'default': '2'}}
	def cubemap(self):
		return {}
	def cursor(self):
		return {'far': {'mapping': 'raycaster.far', 'default': '1000'}, 'fuse': {'mapping': 'cursor.fuse', 'default': 'false'}, 'fuse-timeout': {'mapping': 'cursor.fuseTimeout', 'default': '1500'}, 'interval': {'mapping': 'raycaster.interval', 'default': '100'}, 'objects': {'mapping': 'raycaster.objects', 'default': '100'}}
	def curvedimage(self):
		return {'color': {'mapping': 'material.color', 'default': '#fc1c03'}, 'height': {'mapping': 'geometry.height', 'default': '1'}, 'metalness': {'mapping': 'material.metalness', 'default': '0'}, 'opacity': {'mapping': 'material.opacity', 'default': '1'}, 'open-ended': {'mapping': 'geometry.openEnded', 'default': 'true'}, 'radius': {'mapping': 'geometry.radius', 'default': '2'}, 'repeat': {'mapping': 'material.repeat', 'default': 'None'}, 'roughness': {'mapping': 'material.roughness', 'default': '0.5'}, 'segments-height': {'mapping': 'geometry.segmentsHeight', 'default': '18'}, 'segments-radial': {'mapping': 'geometry.segmentsRadial', 'default': '48'}, 'shader': {'mapping': 'material.shader', 'default': 'flat'}, 'side': {'mapping': 'material.side', 'default': 'double'}, 'src': {'mapping': 'material.src', 'default': 'None'}, 'theta-length': {'mapping': 'geometry.thetaLength', 'default': '270'}, 'theta-start': {'mapping': 'geometry.thetaStart', 'default': '0'}, 'transparent': {'mapping': 'material.transparent', 'default': 'true'}}
	def cylinder(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'geometry.height ', 'default': '1'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'open-ended ': {'mapping': 'geometry.openEnded ', 'default': 'false'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '18'}, 'segments-radial ': {'mapping': 'geometry.segmentsRadial ', 'default': '36'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'theta-length ': {'mapping': 'geometry.thetaLength ', 'default': '360'}, 'theta-start ': {'mapping': 'geometry.thetaStart ', 'default': '0'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def dodecahedron(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'detail ': {'mapping': 'geometry.detail ', 'default': '0'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def gltf_model(self):
		return {'src': {'mapping': 'gltf-model.src', 'default': 'null'}}
	def icosahedron(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'detail ': {'mapping': 'geometry.detail ', 'default': '0'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}	
	def image(self):
		return {'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'height ': {'mapping': 'geometry.height ', 'default': '1'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': 'None'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '1'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'flat'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'true'}, 'width ': {'mapping': 'geometry.width ', 'default': '1'}}
	def light(self):
		return {'angle ': {'mapping': 'light.angle ', 'default': '60'}, 'color ': {'mapping': 'light.color ', 'default': '#fc1c03'}, 'decay ': {'mapping': 'light.decay ', 'default': '1'}, 'distance ': {'mapping': 'light.distance ', 'default': '0.0'}, 'envmap ': {'mapping': 'light.envMap ', 'default': 'null'}, 'ground-color ': {'mapping': 'light.groundColor ', 'default': '#fc1c03'}, 'intensity ': {'mapping': 'light.intensity ', 'default': '1.0'}, 'penumbra ': {'mapping': 'light.penumbra ', 'default': '0.0'}, 'type ': {'mapping': 'light.type ', 'default': 'directional'}, 'target ': {'mapping': 'light.target ', 'default': 'null'}}
	def link(self):
		return {'href ': {'mapping': 'link.href ', 'default': None}, 'title ': {'mapping': 'link.title ', 'default': None}}
	def obj_model(self):
		return {'mtl ': {'mapping': 'obj-model.mtl ', 'default': 'null'}, 'src ': {'mapping': 'obj-model.obj ', 'default': 'null'}}
	def octahedron(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'detail ': {'mapping': 'geometry.detail ', 'default': '0'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def plane(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'geometry.height ', 'default': '1'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '1'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'geometry.width ', 'default': '1'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def ring(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius-inner ': {'mapping': 'geometry.radiusInner ', 'default': '0.8'}, 'radius-outer ': {'mapping': 'geometry.radiusOuter ', 'default': '1.2'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-phi ': {'mapping': 'geometry.segmentsPhi ', 'default': '10'}, 'segments-theta ': {'mapping': 'geometry.segmentsTheta ', 'default': '32'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'theta-length ': {'mapping': 'geometry.thetaLength ', 'default': '360'}, 'theta-start ': {'mapping': 'geometry.thetaStart ', 'default': '0'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def sky(self):
		return {'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'phi-length ': {'mapping': 'geometry.phiLength ', 'default': '360'}, 'phi-start ': {'mapping': 'geometry.phiStart ', 'default': '0'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '500'}, 'repeat ': {'mapping': 'material.repeat ', 'default': 'None'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '32'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '64'}, 'shader ': {'mapping': 'material.shader ', 'default': 'flat'}, 'side ': {'mapping': 'material.side ', 'default': 'back'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'theta-length ': {'mapping': 'geometry.thetaLength ', 'default': '180'}, 'theta-start ': {'mapping': 'geometry.thetaStart ', 'default': '0'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}}
	def sound(self):
		return {'autoplay ': {'mapping': 'sound.autoplay ', 'default': 'false'}, 'loop ': {'mapping': 'sound.loop ', 'default': 'false'}, 'on ': {'mapping': 'sound.on ', 'default': 'null'}, 'src ': {'mapping': 'sound.src ', 'default': 'null'}, 'volume ': {'mapping': 'sound.volume ', 'default': '1'}}
	def sphere(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'phi-length ': {'mapping': 'geometry.phiLength ', 'default': '360'}, 'phi-start ': {'mapping': 'geometry.phiStart ', 'default': '0'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '18'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '36'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'theta-length ': {'mapping': 'geometry.thetaLength ', 'default': '180'}, 'theta-start ': {'mapping': 'geometry.thetaStart ', 'default': '0'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def tetrahedron(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'detail ': {'mapping': 'geometry.detail ', 'default': '0'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def text(self):
		return {'align ': {'mapping': 'text.align', 'default': None}, 'alpha-test ': {'mapping': 'text.alphaTest', 'default': None}, 'anchor ': {'mapping': 'text.anchor', 'default': None}, 'baseline ': {'mapping': 'text.baseline', 'default': None}, 'color ': {'mapping': 'text.color', 'default': None}, 'font ': {'mapping': 'text.font', 'default': None}, 'font-image ': {'mapping': 'text.fontImage', 'default': None}, 'height ': {'mapping': 'text.height', 'default': None}, 'letter-spacing ': {'mapping': 'text.letterSpacing', 'default': None}, 'line-height ': {'mapping': 'text.lineHeight', 'default': None}, 'opacity ': {'mapping': 'text.opacity', 'default': None}, 'shader ': {'mapping': 'text.shader', 'default': None}, 'side ': {'mapping': 'text.side', 'default': None}, 'tab-size ': {'mapping': 'text.tabSize', 'default': None}, 'transparent ': {'mapping': 'text.transparent', 'default': None}, 'value ': {'mapping': 'text.value', 'default': None}, 'white-space ': {'mapping': 'text.whiteSpace', 'default': None}, 'width ': {'mapping': 'text.width', 'default': None}, 'wrap-count ': {'mapping': 'text.wrapCount', 'default': None}, 'wrap-pixels ': {'mapping': 'text.wrapPixels', 'default': None}, 'z-offset ': {'mapping': 'text.zOffset', 'default': None}}
	def torus_knot(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'p ': {'mapping': 'geometry.p ', 'default': '2'}, 'q ': {'mapping': 'geometry.q ', 'default': '3'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'radius-tubular ': {'mapping': 'geometry.radiusTubular ', 'default': '0.2'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-radial ': {'mapping': 'geometry.segmentsRadial ', 'default': '8'}, 'segments-tubular ': {'mapping': 'geometry.segmentsTubular ', 'default': '100'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def torus(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'arc ': {'mapping': 'geometry.arc ', 'default': '360'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '1'}, 'radius-tubular ': {'mapping': 'geometry.radiusTubular ', 'default': '0.2'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'segments-radial ': {'mapping': 'geometry.segmentsRadial ', 'default': '36'}, 'segments-tubular ': {'mapping': 'geometry.segmentsTubular ', 'default': '32'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def triangle(self):
		return {'alpha-test ': {'mapping': 'material.alphaTest ', 'default': '0'}, 'ambient-occlusion-map ': {'mapping': 'material.ambientOcclusionMap ', 'default': 'None'}, 'ambient-occlusion-map-intensity ': {'mapping': 'material.ambientOcclusionMapIntensity ', 'default': '1'}, 'ambient-occlusion-texture-offset ': {'mapping': 'material.ambientOcclusionTextureOffset ', 'default': '0 0'}, 'ambient-occlusion-texture-repeat ': {'mapping': 'material.ambientOcclusionTextureRepeat ', 'default': '1 1'}, 'anisotropy ': {'mapping': 'material.anisotropy ', 'default': '0'}, 'blending ': {'mapping': 'material.blending ', 'default': 'normal'}, 'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'depth-test ': {'mapping': 'material.depthTest ', 'default': 'true'}, 'depth-write ': {'mapping': 'material.depthWrite ', 'default': 'true'}, 'displacement-bias ': {'mapping': 'material.displacementBias ', 'default': '0.5'}, 'displacement-map ': {'mapping': 'material.displacementMap ', 'default': 'None'}, 'displacement-scale ': {'mapping': 'material.displacementScale ', 'default': '1'}, 'displacement-texture-offset ': {'mapping': 'material.displacementTextureOffset ', 'default': '0 0'}, 'displacement-texture-repeat ': {'mapping': 'material.displacementTextureRepeat ', 'default': '1 1'}, 'dithering ': {'mapping': 'material.dithering ', 'default': 'true'}, 'emissive ': {'mapping': 'material.emissive ', 'default': '#000'}, 'emissive-intensity ': {'mapping': 'material.emissiveIntensity ', 'default': '1'}, 'env-map ': {'mapping': 'material.envMap ', 'default': 'None'}, 'flat-shading ': {'mapping': 'material.flatShading ', 'default': 'false'}, 'height ': {'mapping': 'material.height ', 'default': '256'}, 'material-fog ': {'mapping': 'material.fog ', 'default': 'true'}, 'material-visible ': {'mapping': 'material.visible ', 'default': 'true'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'metalness-map ': {'mapping': 'material.metalnessMap ', 'default': 'None'}, 'metalness-texture-offset ': {'mapping': 'material.metalnessTextureOffset ', 'default': '0 0'}, 'metalness-texture-repeat ': {'mapping': 'material.metalnessTextureRepeat ', 'default': '1 1'}, 'normal-map ': {'mapping': 'material.normalMap ', 'default': 'None'}, 'normal-scale ': {'mapping': 'material.normalScale ', 'default': '1 1'}, 'normal-texture-offset ': {'mapping': 'material.normalTextureOffset ', 'default': '0 0'}, 'normal-texture-repeat ': {'mapping': 'material.normalTextureRepeat ', 'default': '1 1'}, 'npot ': {'mapping': 'material.npot ', 'default': 'false'}, 'offset ': {'mapping': 'material.offset ', 'default': '0 0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': '1 1'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'roughness-map ': {'mapping': 'material.roughnessMap ', 'default': 'None'}, 'roughness-texture-offset ': {'mapping': 'material.roughnessTextureOffset ', 'default': '0 0'}, 'roughness-texture-repeat ': {'mapping': 'material.roughnessTextureRepeat ', 'default': '1 1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'standard'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'spherical-env-map ': {'mapping': 'material.sphericalEnvMap ', 'default': 'None'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'vertex-a ': {'mapping': 'geometry.vertexA ', 'default': '0 0.5 0'}, 'vertex-b ': {'mapping': 'geometry.vertexB ', 'default': '-0.5 -0.5 0'}, 'vertex-c ': {'mapping': 'geometry.vertexC ', 'default': '0.5 -0.5 0'}, 'vertex-colors-enabled ': {'mapping': 'material.vertexColorsEnabled ', 'default': 'false'}, 'width ': {'mapping': 'material.width ', 'default': '512'}, 'wireframe ': {'mapping': 'material.wireframe ', 'default': 'false'}, 'wireframe-linewidth ': {'mapping': 'material.wireframeLinewidth ', 'default': '2'}}
	def video(self):
		return {'color ': {'mapping': 'material.color ', 'default': '#fc1c03'}, 'height ': {'mapping': 'geometry.height ', 'default': '1.75'}, 'metalness ': {'mapping': 'material.metalness ', 'default': '0'}, 'opacity ': {'mapping': 'material.opacity ', 'default': '1'}, 'repeat ': {'mapping': 'material.repeat ', 'default': 'None'}, 'roughness ': {'mapping': 'material.roughness ', 'default': '0.5'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '1'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '1'}, 'shader ': {'mapping': 'material.shader ', 'default': 'flat'}, 'side ': {'mapping': 'material.side ', 'default': 'front'}, 'src ': {'mapping': 'material.src ', 'default': 'None'}, 'transparent ': {'mapping': 'material.transparent ', 'default': 'false'}, 'width ': {'mapping': 'geometry.width ', 'default': '3'}}
	def videosphere(self):
		return {'autoplay ': {'mapping': '<video>.autoplay ', 'default': 'true'}, 'crossOrigin ': {'mapping': '<video>.crossOrigin ', 'default': 'anonymous'}, 'loop ': {'mapping': '<video>.loop ', 'default': 'true'}, 'radius ': {'mapping': 'geometry.radius ', 'default': '5000'}, 'segments-height ': {'mapping': 'geometry.segmentsHeight ', 'default': '64'}, 'segments-width ': {'mapping': 'geometry.segmentsWidth ', 'default': '64'}}
	def get(self, element=None):
		if element is None:
			if self.element is not None:
				element = self.element
			else:
				raise Exception("Error - element must not be None!")
		else:
			self.element = element
		if 'a-' in element:
			element = element.split('a-')[1]
		if element == 'box':
			return self.box()
		elif element == 'camera':
			return self.camera()
		elif element == 'circle':
			return self.circle()
		elif element == 'cone':
			return self.cone()
		elif element == 'cubemap':
			return self.cubemap()
		elif element == 'cursor':
			return self.cursor()
		elif element == 'curvedimage':
			return self.curvedimage()
		elif element == 'cylinder':
			return self.cylinder()
		elif element == 'dodecahedron':
			return self.dodecahedron()
		elif element == 'gltf_model' or element == 'gltf-model':
			return self.gltf_model()
		elif element == 'icosahedron':
			return self.icosahedron()
		elif element == 'image':
			return self.image()
		elif element == 'light':
			return self.light()
		elif element == 'link':
			return self.link()
		elif element == 'obj_model' or element == 'obj-model':
			return self.obj_model()
		elif element == 'octahedron':
			return self.octahedron()
		elif element == 'plane':
			return self.plane()
		elif element == 'ring':
			return self.ring()
		elif element == 'sky':
			return self.sky()
		elif element == 'sound':
			return self.sound()
		elif element == 'sphere':
			return self.sphere()
		elif element == 'tetrahedron':
			return self.tetrahedron()
		elif element == 'text':
			return self.text()
		elif element == 'torus_knot' or element == 'torus-knot':
			return self.torus_knot()
		elif element == 'torus':
			return self.torus()
		elif element == 'triangle':
			return self.triangle()
		elif element == 'video':
			return self.video()
		elif element == 'videosphere':
			return self.videosphere()
	def __str__(self, element=None):
		if element is None:#if None, get from attribute, except on null value
			if self.element is not None:
				element = self.element
			else:
				raise Exception(f"Error - element cannot be None!")
		else:#if not None, set attribute
			self.element = element
		return str(self.get(element=element))
	def getElements(self):
		return ['box', 'camera', 'circle', 'cone', 'cubemap', 'cursor', 'curvedimage', 'cylinder', 'dodecahedron', 'gltf_model', 'icosahedron', 'image', 'light', 'link' 'obj_model', 'octahedron', 'plane', 'ring', 'sky', 'sound', 'tetrahedron', 'text', 'torus_knot', 'torus', 'triangle', 'video', 'videosphere']


class Marker():
	def __init__(self, marker_id=None, value=None, rows=5, cols=5, cell_size=100, dtype=None):
		"""
		Marker class
		Functions:
			generateMarker - create new marker by rows, cols, and cell_size. Optional: dictionary type (aruco standard)
				returns IMAGE numpy array if save flag not enabled.
				save flag turns on if fullpath of filename provided.
				if save flag:
					saves to disk instead of returning image, and returns saved image path instead.
				else:
					returns numpy ndarray (opencv)
			detectMarkers - detects markers in an image. TODO - pyimagesearch has script on determining marker type from unknown.
			Think I did that once too... FIND IT!
		Used for creating a new marker at request of parent classes/Main loop.
		"""
		if marker_id is None:
			marker_id = f"aruco_{dtype}"
		self.ID = marker_id
		self.ROWS = rows
		self.COLS = cols
		self.CELLSIZE = cell_size
		self.VALUE = value
		if dtype is None:
			self.DICTIONARY = self.getType(dtype=dtype)
			self.DETECTOR = self.get_detector(dic=self.DICTIONARY)
		else:
			self.DETECTOR = self.get_detector()
		self.IMAGE = self.generateMarker()
	def getType(self, dtype=None):
		"""
		return numerical type of dictionary if not known/specified by matching the closest params provided in init.
		"""
		if dtype is None:
			sizes = [50, 100, 250, 1000]
			if self.CELLSIZE not in sizes:
				old = self.CELLSIZE
				if self.CELLSIZE <= 50:
					self.CELLSIZE = 50
				elif self.CELLSIZE <= 100 and self.CELLSIZE >= 51:
					self.CELLSIZE = 100
				elif self.CELLSIZE <= 250 and self.CELLSIZE >= 100:
					self.CELLSIZE = 250
				elif self.CELLSIZE <= 1000 and self.CELLSIZE >= 250:
					self.CELLSIZE = 1000
				elif self.CELLSIZE > 1000:
					self.CELLSIZE = 1000
				print(f"Error - bad size argument! Correcting...({old} >> {self.CELLSIZE})!")
			try:
				return aruco.__dict__[f"DICT_{self.ROWS}X{self.COLS}_{self.CELLSIZE}"]
			except Exception as e:
				print(f"Error - {e}")
				return None
		else:
			try:
				return aruco.__dict__[dtype]
			except Exception as e:
				print(f"Error - {e}")
				return None
	def get_detector(self, dic=None):
		"""
		caller function to create dictionary for detector object
		"""
		if dic is None:
			self.DICTIONARY = self.getType()
			self.DICTIONARY = aruco.getPredefinedDictionary(self.DICTIONARY)
		else:
			self.DICTIONARY = dic
		return aruco.ArucoDetector(dictionary=self.DICTIONARY)


	def previewMarker(self, img):
		"""
		preview created marker in temporary opencv viewer window
		"""
		cv2.namedWindow('img', cv2.WINDOW_NORMAL)
		cv2.imshow('img', img)
		cv2.waitKey(0)
		cv2.destroyAllWindows()

	def generateMarker(self, save=True, show=False, filename=None, fullpath=None):
		"""
		generate a marker with the initialized attributes:
			ROWS, COLS, CELLSIZE, ID
		sets:
			IMAGE attribute of Marker class
		returns:
			numpy ndarray (IMAGE)
		"""
		img_size = int(self.CELLSIZE * SELF.ROWS), int(self.CELLSIZE * self.COLS)
		aruco_dict = aruco.getPredefinedDictionary(getType(rows=self.ROWS, cols=self.COLS, cell_size=int(self.CELLSIZE*self.ROWS)))
		#img = aruco.drawMarker(aruco_dict, marker_id, self.CELLSIZE)
		img = aruco.generateImageMarker(aruco_dict, self.ID, int(self.CELLSIZE*self.ROWS))
		if save:
			if fullpath is not None:
				fname = fullpath
			elif filename is not None:
				fname = filename
			else:
				fname = f"aruco_{self.ID}_{self.VALUE}.png"
				cv2.imwrite(fname, img)
			return fname#if save option, save to disk and return saved filename.
		if show:
			self.previewMarker(img)
		self.IMAGE = img
		print(f"Marker generated: {self.ROWS}X{self.COLS}-self.VALUE")
		return img#if not save, return image data after setting attribute.

	def detectMarkers(self, img='/media/monkey/usbhd/dev/python3/augmented_reality/images/test1.png', show_when_finished=False):
		"""
		detect markers in an image using opencv
		Unused at the moment in this project, think I just did this to learn about it.
		created from material learned from pyimagesearch
		"""
		if type(img) == str:
			img = cv2.imread(img)
		(corners, ids, rejected) = d.detectMarkers(img)
		print(corners, ids, rejected)
		if len(corners) > 0:
			ids = ids.flatten()
			for (markerCorner, markerID) in zip(corners, ids):
				corners = markerCorner.reshape((4, 2))
				(tl, tr, br, bl) = corners
				tr = (int(tr[0]), int(tr[1]))
				br= (int(br[0]), int(br[1]))
				bl = (int(bl[0]), int(bl[1]))
				tl = (int(tl[0]), int(tl[1]))
				cv2.line(img, tl, tr, (0, 255, 0), 2)
				cv2.line(img, tr, br, (0, 255, 0), 2)
				cv2.line(img, br, bl, (0, 255, 0), 2)
				cv2.line(img, bl, tl, (0, 255, 0), 2)
				cX = int((tl[0] + br[0]) / 2.0)
				cY = int((tl[1] + br[1]) / 2.0)
				cv2.circle(img, (cX, cY), 4, (0, 0, 255), -1)
				cv2.putText(img, str(markerID), (tl[0], tl[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
		self.IMAGE = img
		if show_when_finished:
			self.previewMarker(img)


class SQL():
	"""
	This class handles storage of data between the Aframe html builder, live view, and the UI.
	Manages/creates/adds/removes/modifies/exports/imports data from self.DATABASE
	Anything needing live data pulls from this, and any changes to live data write with this.
	"""
	def __init__(self, dbfile=None):
		if dbfile is None:
			dbfile = 'aframe_data.db'
		self.DATABASE = dbfile
		self.SQL_EXPORT_FILE = 'aframe_dbexport.sql'
	def _sh(self, com):
		"""
		base command to safely wrap shell access (command line injection prevention)
		"""
		return subprocess.check_output(com, shell=True).decode().strip().splitlines()
	def sqlite3(self, query, dbfile=None):
		"""
		this function uses user's shell and sqlite3 to manage the database at self.DATABASE
		main caller function.
		dbfile is an optional path to a sqllite3 database file. #if for .sql, use self.importData(sqlfile)
		"""
		if dbfile is not None:
			self.DATABASE = dbfile
			print(f"Database file provided: Setting DATABASED to '{self.DATABASE}'!")
		try:
			return self._sh(f"sqlite3 \"{dbfile}\" \"{query}\"")
		except Exception as e:
			print(f"sqlite3 error - {e}")
			return None

	def _get_schema(self):
		"""
		Uses sqlite3 .schema command to return database details/data.
		wrapped by getSchema()
		"""
		return self.sqlite3(".schema")

	def getSchema(self):
		"""
		Get databse details/data and parse into dictionary.
		structure:
			main keys:
				'elements'
				'scripts'
				'assets'
		#note - ensure 'id' and 'type' are in each child node's attributes.
		example:
			data['elements']['script1']['id'] = 'script1'
			data['elements']['element1']['type'] = 'a-sphere'
		"""
		cols = {}
		for line in self._get_schema():
			table = line.split('TABLE ')[1].split(' ')[0]
			cols[table] = {}
			#print("table:", table)
			chunks = line.split('(')[1].split(')')[0].split(', ')
			for chunk in chunks:
				attr = chunk.split(' ')[0]
				cols[table][attr] = {}
				cols[table][attr]['mime'] = chunk.split(f"{attr} ")[1].split(' ')[0]
				if 'PRIMARY KEY' in chunk:
					cols[table][attr]['primary'] = True
				else:
					cols[table][attr]['primary'] = False
		return cols

	def getColumns(self, table):
		"""
		returns current columns for table 'table'
		"""
		cols = self.getSchema()
		if len(cols) > 0:
			return list(cols[table].keys())
		else:
			return []

	def getTables(self):
		"""
		returns a list object of tables for database self.DATABASE
		"""
		return list(self.getSchema().keys())

	def createTable(self, table='elements'):
		"""
		Create 'table' in 'self.DATABASE'. initializes with 'id' and 'type' keys only.
		"""
		ret = self.sqlite3(f"CREATE TABLE IF NOT EXISTS {table} (id TEXT PRIMARY KEY, type TEXT);")
		print(ret)

	def addColumn(self, name, mime, table='elements'):
		"""
		Adds a column to table 'table' in self.DATABASE.
		args:
			name = Name of column to add (key)
			mime = Mime type of data stored under that key
			table = Table name in self.DATABASE in which to modify.
		"""
		ret = self.sqlite3(f"ALTER TABLE {table} ADD COLUMN {name} {mime} default null;")
		if ret == [] or ret is None:
			return True
		else:
			print(f"Error adding column '{name}' to table '{table}' with mime type '{mime}': {ret}")
			return False

	def testColumnExists(self, table, column):
		"""
		Test if a column exists in 'table'.
		returns True if yes, False if no.
		"""
		cols = self.getColumns(table=table)
		if column in cols:
			return True
		else:
			return False

	def testTableExists(self, table):
		"""
		test if table exists in database self.DATABASE
		returns True for yes, False for no
		"""
		tables = self.getTables()
		if table in tables:
			return True
		else:
			return False

	def dump(self):
		"""
		Executes ".dump" command using user shell and sqlite3
		Used in self.exportData
		"""
		return self.sqlite3(".dump")

	def testIdExists(self, id):
		"""
		tests and id throughout the ENTIRE DATABASE.
		looks at all tables and checks if 'id' exists.
		returns True if so and False if not.
		"""
		tables = self.getTables()
		for table in tables:
			ret = self.sqlite3(f"select id from {table} where id='{id}';")
			if ret != []:
				return True
		return False


	def addData(self, table, data=None, **args):
		"""
		Add data to databse.
		Data should be a dictionary with single element, script, or asset data only.
			-Main database data dictionry should be used only as self.addData(data['elements']['myelement1'])
			use importData to load the main dictionary.
		"""
		if data is not None:
			for k in data:
				args[k] = data[k]
		cols = self.getColumns(table=table)
		for attr in args:
			if attr not in cols:
				self.addColumn(table=table, name=attr, mime='TEXT')
		if not self.testIdExists(args['id']):
			keys = ", ".join([f"'{i}'" for i in list(args.keys())])
			vals = ", ".join([f"'{i}'" for i in list(args.values())])
			com = f"INSERT INTO {table} ({keys}) VALUES({vals});"
			try:
				return self.sqlite3(com)
			except Exception as e:
				print(f"Error adding: {e}")
				return False
		else:
			print("Id already exists! Skipping...", args)
			return False

	def delete(self, id, table='elements'):
		"""
		Delete data from databse.
		id = unique id of the element/script/asset to remove
		table = table name in self.DATABASE to modify.
		returns True on success, False on fail.
		"""
		ret = self.sqlite3(f"DELETE FROM {table} WHERE id=\"{id}\";")
		if ret == []:
			return True
		else:
			print(f"Error removing id {id} from table {table}: {ret}")
			return False

	def modify(self, table, id, data):
		"""
		Modify a single element/script/asset in database.
		data = dictionary containing a single element's attributes/values.
		id = id of the element to update
		table = table the target element resides on.
		returns True on success, False on fail.
		"""
		com = []
		com.append(f"UPDATE {table} SET")
		for key in data:
			val = data[key]
			com.append(f"{key} = '{val}'")
		com.append(f"WHERE id='{id}';")
		com = " ".join(com)
		ret = self.sqlite3(com)
		if ret == []:
			return True
		else:
			print(f"Error modifying id {id} in table {table}: {ret}. data={data}")
			return False

	def test_data(self):
		"""
		generates working test data for use with SQL, UI and HtmlBuilder classes.
		When generating your own, use this structure.
		"""
		d = {}
		d['elements'] = {}
		print("TODO - modify functions to get id from element/script/asset dictionary key if not included as attribute.")
		d['scripts'] = {}
		d['scripts']['main'] = {}
		d['scripts']['main']['src'] = 'https://aframe.io/releases/0.7.1/aframe.min.js'
		d['scripts']['main']['id'] = 'main'
		d['assets'] = {}
		d['elements']['box1'] = {}
		d['elements']['box1']['id'] = 'box1'
		d['elements']['box1']['type'] = 'a-box'
		d['elements']['box1']['color'] = '#4287f5'
		d['elements']['box1']['scale'] = 1
		d['elements']['box1']['position'] = [0, 0, -1]
		d['elements']['box1']['rotation'] = [0, 0, 0]
		d['elements']['text1'] = {}
		d['elements']['text1']['id'] = 'text1'
		d['elements']['text1']['color'] = '#fc1c03'
		d['elements']['text1']['scale'] = '2'
		d['elements']['text1']['rotation'] = '0 0 0'
		d['elements']['text1']['position'] = '0 0 -3'
		d['elements']['text1']['type'] = 'a-text'
		d['elements']['text1']['value'] = 'farts rule!'
		return d
	def exportData(self, data=None):
		"""
		creates a sql file containing data
		if not provided, grabs data using sqlite3 .dump
		Outputs a .sql file containing importable database contents in standard SQL statements.
		"""
		if data is None:
			print(f"Getting data from database ({self.DATABASE})...")
			data = self.dump()
			if type(data) == list:
				print("Data was list, joining.")
				data = "\n".join(data)
		else:
			print(f"Data provided! Exporting to '{self.SQL_EXPORT_FILE}'...")
		try:
			print("Data:", data)
			with open(self.SQL_EXPORT_FILE, 'w') as f:
				f.write(data)
				f.close()
			return True
		except Exception as e:
			print(f"Error exporting data to '{self.SQL_EXPORT_FILE}': {e}")
			return False
	def backupdb(self):
		"""
		simple helper function for backing up old database when overwriting.
		saves to <filename>.bak
		"""
		ret = self.sh(f"mv \"{self.DATFILE}\" \"{self.DATFILE}.bak\"")
		if ret == []:
			return True
		else:
			return False
	def importData(self, savefile=None):
		"""
		reads a raw/text .sql file into self.DATABASE
		savefile = path to file containing sql data.
		"""
		if savefile is None:
			print(f"Save file provided. Overriding class attribute with '{savefile}'...")
			self.SQL_EXPORT_FILE = savefile
		if not os.path.exists(self.SQL_EXPORT_FILE):#if export not found, abort.
			print(f"Couldn't import data from file '{self.SQL_EXPORT_FILE}': File not found!")
			return False
		try:
			if os.path.exists(self.DATABASE):
				self.backupdb()
			ret = self.sh(f"cat '{self.SQL_EXPORT_FILE}' | sqlite3 '{self.DATABASE}'")
			if ret != []:
				print(f"Failed to import from '{self.SQL_EXPORT_FILE}' to '{self.DATABASE}': {ret}")
				return False
			else:
				return True
			
			return data
		except Exception as e:
			print(f"Error importing data from '{self.SQL_EXPORT_FILE}': {e}")
			return None
	def dbToDict(self):
		"""
		Loads database into Aframe data dictionary with 'scripts', 'elements', and 'assets' keys.
		"""
		out = {}
		for table in self.getTables():
			out[table] = {}
			cols = self.getColumns(table=table)
			print("cols length:", len(cols))
			data = self.sqlite3(f"select * from {table};")
			for line in data:
				print("line:", line)
				chunks = line.split('|')
				print("chunks length:", len(chunks))
				for chunk in chunks:
					if chunk != '':
						key = cols[chunks.index(chunk)]
						if '[' in key and ']' in key and ', ' in key:#check for stringified list (x,y,z)
							chunk = [int(i) for i in chunk.split('[')[1].split(']')[0].split(', ')]
						out[table][key] = chunk
		return out
	def dictToDb(self, d):
		"""
		saves the contents of dictionary 'd' to self.DATABASE
		"""
		elements = d['elements']
		scripts = d['scripts']
		assets = d['assets']
		if not self.testTableExists('elements'):
			self.createTable(table='elements')
		if not self.testTableExists('scripts'):
			self.createTable(table='scripts')
		if not self.testTableExists('assets'):
			self.createTable(table='assets')
		for e in elements:
			d = elements[e]
			self.addData(table='elements', data=d)
		for s in scripts:
			d = scripts[s]
			self.addData(table='scripts', data=d)
		for a in assets:
			d = assets[a]
			self.addData(table='assets', data=d)
		print("Data added to database!")


def get_unique_id():
	out = []
	chars = 'abcdefghijklmnopqrstuvwxyz'
	ct = len(chars)
	nums = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
	for i in range(0, 7):
		i = randint(1, 2)
		if i == 1:
			l = list(chars)
		elif i == 2:
			l = nums
		i2 = randint(0, len(l)-1)
		out.append(l[i2])
	return "".join([str(i) for i in out])

class _string_builder():
	def __init__(self, data, indent_count=2):
		self.DATA = data
		self.indent = self._get_indent(count=indent_count)
		self.string = self._get_str()
	def _list_to_string(self, l):
		"""
		helper function to convert position/rotation (3d matrix) to
		space delemited string of integers (aframe js/html)
		[0, 0, -1] >> "0 0 -1"
		"""
		return " ".join([str(i) for i in l])
	def _string_to_list(self, l):
		"""
		helper function to convert integer string into list of integers.
		"0 0 -1" >> [0, 0, -1]
		"""
		return [int(i) for i in l.split(' ')]
	def __str__(self):
		return self._get_str()
	def _build_str(self, k, v):
		if v is None:
			v = True
		if str(v) == "True" or v == "true":
			string = f"{k}=\"\""
		else:
			string = f"{k}=\"{v}\""
		return string
	
	def _get_attrs(self, d):
		l = []
		for k in d:
			if k != 'type':
				l.append(self._build_str(k, d[k]))
		return " ".join(l)

	def _get_indent(self, count=2, char="\t"):
		l = []
		for i in range(count):
			l.append(char)
		return "".join(l)

	def _get_str(self, data=None, indent_count=None):
		if indent_count is not None:
			indent = self._get_indent(count=indent_count)
		else:
			indent = self.indent
		if data is None:
			data = self.DATA
		l = []
		l.append(f"{indent}<{data['type']}")
		l.append(self._get_attrs(data))
		l.append(f"></{data['type']}>")
		return " ".join(l).replace(' >', '>')
		
class htmlBuilder(_string_builder):
	def __init__(self, data):
		self.DATADIR = os.path.join(os.path.expanduser("~"), '.aframe')
		if not os.path.exists(self.DATADIR):
			os.makedirs(self.DATADIR, exist_ok=True)
		self.SAVEFILE = os.path.join(self.DATADIR, 'savefile.dat')
		self.DATA = self.setData(data=data)
		self.elements = self.DATA['elements']
		self.assets = self.DATA['assets']
		self.scripts = self.DATA['scripts']
		#self.write(data=self.DATA)
	def setData(self, data=None):
		"""
		Helper function to load if available or re-initialize data dictionary if not found.
		May need to restructure this, seems like it may be problematic for me. How???
		"""
		if data is None:
			try:
				self.DATA = self.load()
				if self.DATA is None or self.DATA == {}:
					print(f"Saved data is None. Re-Initializing...")
					self.DATA = self._init_data()
					self.save(self.DATA)
			except Exception as e:
				print(f"Couldn't load data - {e}. Re-initializing data...")
				self.DATA = self._init_data()
				self.save(self.DATA)
		else:
			print("Data provided!")
			self.DATA = data
			self.save(self.DATA)
		self.scripts = self.DATA['scripts']
		self.assets = self.DATA['assets']
		self.elements = self.DATA['elements']
		return self.DATA
	def _init_data(self):
		d = {}
		d['elements'] = {}
		d['scripts'] = []
		d['assets'] = {}
		self.DATA = d
		return d
	def save(self, data=None):
		if data is None:
			print("Data not provided! Using DATA attribute...")
			data = self.DATA
		with open(self.SAVEFILE, 'wb') as f:
			pickle.dump(data, f)
			f.close()
		print("Data saved:", self.DATA)
	def load(self):
		try:
			with open(self.SAVEFILE, 'rb') as f:
				self.DATA = pickle.load(f)
				f.close()
				print(f"Data loaded! {self.DATA}")
				return self.DATA
		except Exception as e:
			print(f"Error loading save file: {e}")
			return None
	def write(self, data=None, path='/var/www/html/aframe-index.html'):
		print(f"Building and writing to: {path}...")
		if data is not None:
			print(f"Data provided! Overwriting 'data' attrubte...")
			self.DATA = data
		self.html = self.build(self.DATA)
		with open(path, 'w') as f:
			f.write(self.html)
			f.close()
	def _get_indent(self, count=1, char="\t"):
		l = []
		for i in range(count):
			l.append(char)
		return "".join(l)
	def _compile_assets(self, indent_count=4):
		l = []
		l.append(f"{self._get_indent(indent_count)}<assets>")
		newindent = self._get_indent(indent_count+1)
		for asset_id in self.assets:
			l.append(_string_builder(data=self.assets[asset_id], indent_count=newindent)._get_str())
		l.append(f"{self._get_indent(indent_count)}</assets>")
		return "\n".join(l)
	def _compile_elements(self, indent_count=3):
		l = []
		newindent = self._get_indent(count=indent_count + 1)
		if len(self.assets) > 0:
			l.append(self._compile_assets())
		for element_id in self.elements:
			l.append(_string_builder(data=self.elements[element_id], indent_count=indent_count)._get_str())
		return "\n".join(l)
	def _compile_scripts(self, indent_count=2):
		l = []
		indent = self._get_indent(count=indent_count)
		l.append(f"{indent}<script src=\"https://aframe.io/releases/0.7.1/aframe.min.js\"></script>")
		for d in self.scripts:
			try:
				element_id = d['id']
			except Exception as e:
				print(f"Annoying message to remind me that 'id' still isn't included in UI output!", e)
				element_id = get_unique_id()
				d['id'] = element_id
				print(f"Auto generated id: {element_id}")
			path = d['attrs']['src']
			l.append(f"{indent}<script>src=\"{path}\"</script>")
		return "\n".join(l)
	def addAsset(self, **args):
		self.assets[args['id']] = args
		print(f"Asset added:", args['id'])
	def addElement(self, data=None, **args):
		if data is not None:
			for k in data:
				if k not in args:
					if k == 'rotation' or k == 'position':
						args[k] = self._list_to_string(data[k])
					else:
						#add data t o args if not None
						args[k] = data[k]
		if args['type'] == 'img' or args['type'] == 'video':
			#if medi type is image or video, add crossorigin: anonymous (CORS) 
			args['crossorigin'] = "anonymous"
		try:
			aid = args['id']
		except Exception as e:
			print("Id not provided in arguments. Auto generating...")
			aid = get_unique_id()
			args['id'] = aid
		print("id:", args['id'])
		self.elements[aid] = args
		print(f"Element added:", args['id'])
	def build(self, data=None):
		if data is None:
			data = self.DATA
		indent = self._get_indent(count=1)
		l = []
		l.append(f"<html>")
		l.append(f"{indent}<head>")
		#self.script(src="https://aframe.io/releases/1.6.0/aframe.min.js")#adds main aframe js script
		l.append(self._compile_scripts(indent_count=2))
		l.append(f"{indent}</head>")
		l.append(f"{indent}<body>")
		l.append(f"{indent}{indent}<a-scene>")
		l.append(f"{self._compile_elements(indent_count=3)}")
		l.append(f"{indent}{indent}</a-scene>")
		l.append(f"{indent}</body>")
		l.append("</html>")
		return "\n".join(l)

	def _get_script(self, src, script_id=None):
		if script_id is None:
			script_id = f"script{len(self.scripts)}"
		d = {}
		d['id'] = script_id
		d['type'] = 'script'
		d['attrs'] = {}
		d['attrs']['src'] = src
	def addScript(self, src, script_id=None):
		d = self._get_script(src=src, script_id=script_id)
		self.scripts.append(d)
		print(f"Script added: {script_id}")
	def _get_camera(self, cameraid='camera_1', user_height=0, **kwargs):
		data = {}
		data['type'] = 'a-camera'
		data['id'] = cameraid
		data['user_height'] = user_height
		for k in kwargs:
			data[k] = kwargs[k]
		return data

	def addCamera(self, cameraid='camera_1', user_height=0, position="0 0 -1", scale="1", rotation="0 180 0"):
		camera = self._get_camera(cameraid=cameraid, user_height=user_height, position=position, scale=scale, rotation=rotation)
		self.addElement(camera)
		print(f"Camera added: {cameraid}")
	def test_hasElement(self, element_id=None, element_type='camera'):
		if element_id is not None:
			els = list(self.elements.keys())
			if element_id in els:
				return True
			else:
				return False
		elif element_type is not None:
			els = [b.elements[i]['type'] for i in b.elements]
			if element_type in els:
				return True
			else:
				return False
		
	

class UI():
	"""Skeleton class for creating a self.UI.for various whatevers."""
	def __init__(self):
		self.LAYOUT = []
		self.ROW = []
		self.FRAMES = []
		self.WINDOW = None
		self.DEFAULTS = Defaults()
	def addElement(self, e):
		#if type(e) != list:
		#	self.ROW.append([e])
		#else:
		self.ROW.append(e)
	def addRow(self, row=None):
		if row is None:
			#if class attribute used, blank after.
			row = self.ROW
			self.ROW = []
		self.LAYOUT.append(row)
	def addToFrame(self, title='Test frame', layout=None, width=None, height=None, tooltip='test tooltip', expand_x=False, expand_y=False):
		if layout is None:
			if len(self.ROW) > 0:
				self.addRow()
			#since we're using an attribute, clear it and 
			#it's contributing ROWS attr.
			layout = self.LAYOUT
			self.LAYOUT = []
		key = f"-{title}-"
		frame = sg.Frame(title=title, layout=layout, title_location='n', size=(width, height), font=None, pad=1, border_width=1, key=key, tooltip=tooltip, expand_x=expand_x, expand_y=expand_y, element_justification="center", vertical_alignment='center') #t (top), c (center), r(bottom)
		self.FRAMES.append(frame)
		return frame
		print(time.ctime(), "Frame added!")
	def getWindow(self, title='Test Window', layout=None, grab_keyboard=True, width=900, height=600, expand_x=False, expand_y=False, pack_to_frame=True):
		self.GRAB_KEYBOARD = grab_keyboard
		#sets default for returning filtered keyboard events in the main remote menu
		key=f"-{title}-"
		if layout is None or len(layout) == 0:
			if pack_to_frame:
				self.addToFrame(title=title, layout=layout, width=width, height=height, expand_x=expand_x, expand_y=expand_y)
				self.LAYOUT.append(self.FRAMES)
				self.FRAMES = []
				#since we're using an attribute, clear it and 
				#it's contributing ROWS attr.
			else:
				print(self.LAYOUT)
			layout = self.LAYOUT
			self.LAYOUT = []
		elif len(layout) >= 1:
			if type(layout[0]) != list:
				layout = [layout]
		self.WINDOW = sg.Window(title=title, layout=layout, size=(width, height), return_keyboard_events=True, use_default_focus=False).finalize()
		return self.WINDOW
	def save(self, filepath=None, win=None):
		if win is None:
			win = self.WINDOW
		if filepath is None:
			filepath = os.path.join(os.path.expanduser("~"), f".{win.title}.dat")
		win.save_to_disk(filepath)

class WebEnginePage(QWebEnginePage):
	"""
	extends QTWebEngine webview class to override failure to load url on ssl invalid error. (self signed cert)
	"""
	def certificateError(self, error):
		error.ignoreCertificateError()
		return True

class Browser(QWidget):
	def __init__(self, url='https://192.168.1.151/aframe-index.html', run=True):
		"""
		Preview html content in (relatively) real-time.
		Added override for ssl error with WebEnginePage()
		"""
		self.URL = url
		if self.URL is not None:
			run = True
			print(f"Url provided! run flag set True. ({self.URL})")
		super().__init__()
		self.setWindowTitle("DIY Browser")
		self.setGeometry(300, 200, 800, 600)
		self.layout = QVBoxLayout()
		self.browser = QWebEngineView()
		self.layout.addWidget(self.browser)
		self.setLayout(self.layout)
		self.load_url(self.URL)
	def load_url(self, url=None):
		"""
		loads url in preview browser.
		Accepts:
			url as a string, sets with QUrl
		returns:
			None, live loads url in window.
		"""
		self.browser.setPage(WebEnginePage())#override the ssl error with WebEnginePage class
		if url is None:
			url = self.URL
		self.browser.load(QUrl(url))
		self.browser.show()




def Preview(url='http://127.0.0.1/aframe-index.html', run=True):
	"""
	caller function to be ran as script
	"""
	app = QApplication(sys.argv)
	browser = Browser(url=url)
	browser.show()
	sys.exit(app.exec_())


class Aframe(htmlBuilder):
	def __init__(self, data=None, preview=True):
		super().__init__(data=data)
		self.preview = Preview(run=preview)
		self.UI = UI()
	def getInput(self, data={}, title='Enter value:'):
		layout = []
		common = ['position', 'rotation', 'scale', 'color', 'visible']
		for c in common:
			if c not in data:
				data[c] = {}
				if c == 'position':
					data[c]['default'] = "0 0 -1"
				elif c == 'rotation':
					data[c]['default'] = "0 0 0"
				elif c == 'scale':
					data[c]['default'] = "1"
				elif c == 'color':
					data[c]['default'] = "#fc1c03"
				elif c == 'visible':
					data[c]['default'] = "true"
		for key in data:
			default_value = data[key]['default']
			k = f"-SET_{key.replace('-', '_')}-"
			layout.append([sg.Text(f"{key}:"), sg.Input(default_value, key=k, enable_events=True, change_submits=True, expand_x=True)])
		layout.append([sg.Button('Ok')])
		inwin = sg.Window(title=title, layout=layout)
		value = default_value
		out = {}
		while True:
			e, v = inwin.read()
			if e == sg.WINDOW_CLOSED:
				break
			elif '-SET_' in e:
				k = e.split('_')[1].split('-')[0]
				value = v[e]
				out[k] = value
				print(f"Value set ({k}): {data[k]}")
			elif e == 'Ok':
				for key in data:
					k = f"-SET_{key.replace('-', '_')}-"
					print(k, key, data[key])
					try:
						out[key] = inwin[k].get()
					except:
						out[key] = available[key]
				inwin.close()
		for key in out:
			value = out[key]
			if key == 'rotation' or key == 'position':
				v1, v2, v3 = value.split(" ")
				v1, v2, v3 = int(v1), int(v2), int(v3)
				out[key] = [v1, v2, v3]
			else:
				if value == "true" or value == "True":
					value = True
				elif value == "false" or value == 'False':
					value = False
				out[key] = value
		return out

	def new_element(self, element_type=None, data={}, **args):
		common = ['position', 'rotation', 'scale', 'color', 'visible']
		win = None
		for k in args:
			if k != 'type':
				data[k] = args[k]
		if element_type is None:
			element_type = self._element_picker()
		available = Defaults(element=element_type).get()
		for k in common:#cycle through common, if not in defaults, add with default value.
			if k not in available:
				available[k] = {}
				available[k]['mapping'] = None
				if k == 'position':
					available[k]['default'] = "0 0 -1"
				elif k == 'rotation':
					available[k]['default'] = "0 0 0"
				elif k == 'scale':
					available[k]['default'] = "1"
				elif k == 'color':
					available[k]['default'] = "#fc1c03"
				elif k == 'visible':
					available[k]['default'] = "true"
		total = list(available.keys())
		picked = list(data.keys())
		label = f"Add {element_type}:"
		self.UI.addElement(sg.Text(label))
		self.UI.addRow()
		self.UI.addElement(sg.Listbox(total, size=(20, 10), enable_events=True, change_submits=True, key='-AVAILABLE_ATTRS-'))
		self.UI.addRow()
		self.UI.addElement(sg.Listbox(picked, size=(20, 10), change_submits=True, select_mode='LISTBOX_SELECT_MODE_SINGLE', enable_events=True, key='-PICKED_ATTRS-', tooltip="Selected attributes for element.", expand_x=False, expand_y=False))
		self.UI.addRow()
		self.UI.addElement(sg.Button("Add!", key='-ADD-'))
		self.UI.addElement(sg.Button('Delete!', key='-DEL-'))
		self.UI.addRow()
		self.UI.addElement(sg.Button('Ok'))
		self.UI.addElement(sg.Button('Close'))
		self.UI.addRow()
		win2 = self.UI.getWindow(title='Assign attributes:', grab_keyboard=False)
		attr = None
		while True:
			e, v = win2.read(timeout=1)
			if e == '__TIMEOUT__':
				pass
			elif e == sg.WINDOW_CLOSED:
				break
			elif e == 'Close':
				win2.close()
				break
			elif e == '-AVAILABLE_ATTRS-':
				attr = v[e][0]
				print("Selected available attribute:", v[e])
			elif e == '-ADD-':
				print("Adding attribute:", attr)
				if attr in picked:
					print("Already in list:", attr)
				elif attr not in picked:
					picked.append(attr)
					data[attr] = {}
					data[attr]['mapping'] = None
					data[attr]['default'] = None
				if attr in total:
					_ = total.pop(total.index(attr))
				win2['-PICKED_ATTRS-'].update(picked)
				win2['-AVAILABLE_ATTRS-'].update(total)
			elif e == '-DEL-':
				print("Removing attribute:", attr)
				if attr in picked:
					_ = picked.pop(picked.index(attr))
					del data[attr]
				if attr not in total:
					total.append(attr)
				if attr not in data:
					data[attr] = {}
					data[attr]['mapping'] = None
					data[attr]['default'] = None
				win2['-PICKED_ATTRS-'].update(picked)
				win2['-AVAILABLE_ATTRS-'].update(total)
			elif e == 'Ok':
				for k in picked:
					try:
						data[k] = available[k]
					except:
						data[k] = None
				out = self.getInput(data=data)
				out['type'] = f"a-{element_type}"
				win2.close()
				break
			else:
				print(e, v)
		return out
	def _element_picker(self):
		elements = Defaults().getElements()
		self.UI.addElement(sg.Listbox(elements, change_submits=True, enable_events=True, size=(None, None), key='-ADD_OBJECT-', tooltip="Select an object:", expand_x=False, expand_y=True))
		self.UI.addRow()
		self.UI.addElement(sg.Button('Ok'))
		self.UI.addElement(sg.Button('Cancel'))
		win = self.UI.getWindow(title='Add Object', grab_keyboard=False)
		element = None
		while True:
			e, v = win.read()
			if e == sg.WINDOW_CLOSED:
				break
			elif e == 'Ok' or e == 'Cancel':
				win.close()
				win = None
				return element
			else:
				element = v[e][0]
				print("element set:", element)

	def get_menu_def(self):
		return 	[['Build', ['Compile', 'Write']], ['PreviewWindow', ['Open', 'Close', 'Refresh']], ['File', ['Save', 'Load', 'Import HTML', 'Write HTML', 'Exit']], ['Edit', ['Add Element', 'Edit Element', 'Remove Element', 'Globals']], ['Help', ['About']]]

	def main_menu(self):
		self.UI.addElement(sg.Menu(menu_definition=self.get_menu_def(), size=(None, None), key='-MENU-'))
		self.UI.addRow()
		self.UI.addElement(sg.Listbox(self.elements, change_submits=True, enable_events=True, size=(30, 10), key='-ELEMENT_SELECT-', tooltip="Select an Element:", expand_x=False, expand_y=True))
		self.UI.addRow()
		self.UI.addElement(sg.Listbox(self.assets, change_submits=True, enable_events=True, size=(30, 10), key='-ASSET_SELECT-', tooltip="Select an Asset:", expand_x=False, expand_y=True))
		self.UI.addRow()
		self.UI.addElement(sg.Listbox(self.scripts, change_submits=True, enable_events=True, size=(30, 10), key='-SCRIPT_SELECT-', tooltip="Select a Script:", expand_x=False, expand_y=True))
		self.UI.addRow()
		self.UI.addToFrame(title='Elements:', tooltip='Select an element:', expand_x=False, expand_y=False)
		win = self.UI.getWindow(title='Main Menu')
		while True:
			e, v = win.read()
			if e == sg.WINDOW_CLOSED:
				break
			else:
				print(e, v)
				if e == 'Save':
					print("Saving data....")
					self.save()
					print("Done!")
				elif e == 'Load':
					print("Loading data...")
					self.load()
				elif e == 'Import HTML':
					pass
				elif e == 'Write HTML':
					pass
				elif e == 'Exit':
					win.close()
					break
				elif e == 'Add Element':
					element_data = self.new_element()
					self.addElement(data=element_data)
					print(f"Element data added!:", element_data)
				elif e == 'Edit Element':
					pass
				elif e == 'Remove Element':
					pass
				elif e == 'Globals':
					pass
				elif e == 'About':
					pass
				elif e == 'Compile':
					print("Building...")
					self.build()
					print("Done!")
				elif e == 'Write':
					print("Writing...")
					self.write()
					print("Done!")
				elif e == 'Open':
					print("Opening preview window...")
					self.preview.runBrowser()
				elif e == 'Close':
					print(f"Closing preview window...")
					self.preview.killBrowser()
				elif e == 'Refresh':
					print(f"Refreshing...")
					self.preview.refresh()
				
				else:
					print(f"Unhandled event:", e)

if __name__ == "__main__":
	import sys
	print(sys.modules['__main__'].__file__)
	a = Aframe()
	a.main_menu()

	
