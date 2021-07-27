from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.editor_camera import EditorCamera
import numpy as np

app = Ursina()

time_stamp = 1; time_now = 0
run = False

def CountNeighbours(theInputMatrix,countRadius=1,borderValue=0.):
    heightFP,widthFP = theInputMatrix.shape
    withBorders = np.ones((heightFP+(2*countRadius),widthFP+(2*countRadius)))*borderValue
    withBorders[countRadius:heightFP+countRadius,countRadius:widthFP+countRadius]=theInputMatrix
    resultMatrix = np.zeros((heightFP,widthFP)) 
    minRow,minCol = 0,0
    maxRow,maxCol = 2.*countRadius,2.*countRadius
    rowVal,colVal = 0,0

    for i in range(4*countRadius):
        while colVal<maxCol: #move right along top of spiral
            resultMatrix = resultMatrix + withBorders[rowVal:heightFP+rowVal,colVal:widthFP+colVal]
            colVal += 1
 
        while rowVal<maxRow: #move down right hand side of spiral
            resultMatrix = resultMatrix + withBorders[rowVal:heightFP+rowVal,colVal:widthFP+colVal]
            rowVal += 1
 
        while colVal>minCol: #move left along base of spiral
            resultMatrix = resultMatrix + withBorders[rowVal:heightFP+rowVal,colVal:widthFP+colVal]
            colVal -= 1
        minRow += 1
        maxCol -= 1
        while rowVal > minRow: #move up left hand side of spiral
            resultMatrix = resultMatrix + withBorders[rowVal:heightFP+rowVal,colVal:widthFP+colVal]
            rowVal -= 1
        minCol += 1
        maxRow -= 1

    return resultMatrix

def update():
	global time_now, time_stamp, run
	time_now += time.dt
	if time_now > time_stamp:
		if run:
			vox_neigh_array = CountNeighbours(voxel_array)
			for cord1 in range(len(voxel_array)):
				for cord2 in range(len(voxel_array[cord1])):
					if voxel_array[cord1, cord2] == 1 and vox_neigh_array[cord1,cord2] < 2:
						vox = voxel_names[cord1][cord2]
						globals()[vox].alive = False
						globals()[vox].texture = 'black_cube'
						voxel_array[cord1,cord2] = 0
					elif voxel_array[cord1, cord2] == 1 and vox_neigh_array[cord1,cord2] > 3:
						vox = voxel_names[cord1][cord2]
						globals()[vox].alive = False
						globals()[vox].texture = 'black_cube'
						voxel_array[cord1,cord2] = 0
					elif voxel_array[cord1, cord2] == 0 and vox_neigh_array[cord1,cord2] == 3:
						vox = voxel_names[cord1][cord2]
						globals()[vox].alive = True
						globals()[vox].texture = 'hover_black_cube'
						voxel_array[cord1,cord2] = 1
			print(f"Frame processed (Time: {time_stamp}s)")
		else:
			print(f"Paused (Time: {time_stamp}s)")
		time_stamp += 1

def input(key):
	global camera_mode, run
	
	if key == 'c':
		if camera_mode:
			player = FirstPersonController()
			camera_mode = False
		else:
			player = EditorCamera()
			player.position = (1,1,1)
			camera_mode = True
	if key == 'r':
		if run:
			run = False
		else:
			run = True

class Voxel(Button):
	def __init__(self, position = (0,0,0)):
		super().__init__(
			alive = False,
			parent = scene,
			position = position,
			model = 'quad',
			texture = 'black_cube',
			origin_y = 0.5,
			rotation = Vec3(90, 0, 0),
			color = color.color(0,0,random.uniform(0.9,1)),
			scale = 0.5)

	def input(self,key):
		if self.hovered:
			global voxel_array
			if key == 'left mouse down':
				self.alive = True
				self.texture = 'hover_black_cube'
				cord1 = int(self.position[0]*2)
				cord2 = int(self.position[2]*2)
				voxel_array[cord1, cord2] = 1
				print(f"You've given {cord1},{cord2} life!")

			elif key == 'right mouse down':
				self.alive = False
				self.texture = 'black_cube'
				cord1 = int(self.position[0]*2)
				cord2 = int(self.position[2]*2)
				voxel_array[cord1, cord2] = 0
				print(f"You just killed {cord1},{cord2}!")

grid_dimensions = [20, 20]
voxel_array= [[] for dim in range(2*grid_dimensions[0])]
voxel_names = [[] for dim in range(2*grid_dimensions[0])]

for z in range(grid_dimensions[1]*2):
	for x in range(grid_dimensions[0]*2):
		globals()[f"voxel_{x}_{z}"] = Voxel(position = (x/2,0,z/2))
		voxel_names[x].append(f"voxel_{x}_{z}")
		voxel_array[x].append(0)

voxel_array = np.array(voxel_array)
vox_neigh_array = CountNeighbours(voxel_array)

print(voxel_array)
print(vox_neigh_array)
print(voxel_names)

camera_mode = False

player = FirstPersonController()

app.run()
