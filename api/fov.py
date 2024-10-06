import math 

# Player variables assuming positive z direction 
xpos = 0 
ypos = 0 
zpos = 0 
renderdistance = 256
"""
Main Function to return points that the NPC can see 
Leftx = positive 
Rightx = negative
Visionlayers look like this:
visionlayers[layer[height[width[block]]]]
"""
def generate_vision_layers(xpos, ypos, zpos, xdeg, ydeg, renderdistance):
    visionlayers = []
    
    def compute_layers(depth, x_offset, y_offset, z_offset):
        heightlayer = []
        for height in range(0, (depth*2) + 1):
            widthlayer = []
            for width in range(0, (depth*2) + 1):
                x = xpos + x_offset(depth, width)
                y = ypos + y_offset(depth, height)
                z = zpos + z_offset(depth, height)
                widthlayer.append([x, y, z])
            heightlayer.append(widthlayer)
        return heightlayer

    if ydeg == -90:
        for depth in range(0, renderdistance):
            visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: -d, lambda d, h: -d + h))

    elif ydeg == 90:
        for depth in range(0, renderdistance):
            visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: d, lambda d, h: -d + h))

    elif xdeg == 0:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: -d + h, lambda d, h: d))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos-1, ypos-1, zpos], [xpos, ypos-1, zpos], [xpos+1, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: -d + h, lambda d, h: d))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos-1, ypos-1, zpos], [xpos, ypos-1, zpos], [xpos+1, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: h, lambda d, h: d))
                
    elif xdeg == 45:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: -d + h, lambda d, h: w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: -d + h, lambda d, h: w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: h, lambda d, h: d))
    
    elif xdeg == -45:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: -d + h, lambda d, h: w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: -d + h, lambda d, h: w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: d - w, lambda d, h: h, lambda d, h: d))
    
    elif xdeg == 90:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: -d, lambda d, h: -d + h, lambda d, h: d - w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos-1], [xpos, ypos-1, zpos], [xpos, ypos-1, zpos+1]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d, lambda d, h: -d + h, lambda d, h: d - w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos-1], [xpos, ypos+1, zpos], [xpos, ypos+1, zpos+1]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d, lambda d, h: h, lambda d, h: d - w))
                
    elif xdeg == -90:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: d, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos-1], [xpos, ypos-1, zpos], [xpos, ypos-1, zpos+1]])
                visionlayers.append(compute_layers(depth, lambda d, w: d, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos-1], [xpos, ypos+1, zpos], [xpos, ypos+1, zpos+1]])
                visionlayers.append(compute_layers(depth, lambda d, w: d, lambda d, h: h, lambda d, h: -d + w))

    elif xdeg == 135:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: -w, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -w, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -w, lambda d, h: h, lambda d, h: -d + w))
            
    elif xdeg == -135:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: w, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: w, lambda d, h: -d + h, lambda d, h: -d + w))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos, ypos+1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: w, lambda d, h: h, lambda d, h: -d + w))
    
    elif xdeg == 0:
        if ydeg == 0:
            for depth in range(0, renderdistance):
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: -d + h, lambda d, h: -d))
                
        elif ydeg == -45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos-1, ypos-1, zpos], [xpos, ypos-1, zpos], [xpos+1, ypos-1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: -d + h, lambda d, h: -d))
                
        elif ydeg == 45:
            for depth in range(0, renderdistance):
                visionlayers.append([[xpos-1, ypos+1, zpos], [xpos, ypos+1, zpos], [xpos+1, ypos+1, zpos]])
                visionlayers.append(compute_layers(depth, lambda d, w: -d + w, lambda d, h: h, lambda d, h: -d))
            
    return visionlayers

"""
Pseudo-code for block checking to generate a canvas 
Visionlayers look like this:
visionlayers[layer[height[width[block]]]]
"""
def generate_canvas(visionlayers, xpos, ypos, zpos, xdeg, ydeg, renderdistance):
    blocklist = []
    if xdeg == 45 or xdeg == -45 or xdeg == 135 or xdeg == -135:
        layerindex = 0 
        widthindex = 0 
        heightindex = 0
        for height in visionlayers: # For each layer
            for width in height: # For each width stacked 
                for block in width: # For each block in the width
                    if block[4] != 0: # Make sure after adding block it never appears again
                        blocklist.append([renderdistance - (len(width)/2)+(widthindex*2)-1,renderdistance - math.ceil(len(height)/2)+heightindex,block[4]]) # [canvas x, canvas y, block id]
                        for i in range(0, len(visionlayers) - layerindex):  # how many layers are left
                            visionlayers[layerindex + i][heightindex][widthindex + i][4] = 0
                        if widthindex == 0 or widthindex == len(width) - 1: # if width edge exclude all blocks to left or right
                            for i in range(0, len(visionlayers) - layerindex):  
                                for r in range(0, i):
                                    visionlayers[layerindex + i][heightindex][widthindex + r][4] = 0
                        if heightindex == 0 or heightindex == len(height) - 1: # if height edge exclude all blocks to top or bottom
                            for i in range(0, len(visionlayers) - layerindex):  
                                for r in range(0, i):
                                    visionlayers[layerindex + i][heightindex + r][widthindex][4] = 0
                    widthindex += 1
                heightindex += 1
            layerindex += 1
    else: 
        layerindex = 0 
        widthindex = 0 
        heightindex = 0
        for height in visionlayers: # For each layer
            for width in height: # For each width stacked 
                for block in width: # For each block in the width
                    if block[4] != 0: # Make sure after adding block it never appears again
                        blocklist.append([renderdistance - math.ceil(len(width)/2)+widthindex,renderdistance - math.ceil(len(height)/2)+heightindex,block[4]]) # [canvas x, canvas y, block id]
                        for i in range(0, len(visionlayers) - layerindex):  # how many layers are left
                            visionlayers[layerindex + i][heightindex][widthindex + i][4] = 0
                        if widthindex == 0 or widthindex == len(width) - 1: # if width edge exclude all blocks to left or right
                            for i in range(0, len(visionlayers) - layerindex):  
                                for r in range(0, i):
                                    visionlayers[layerindex + i][heightindex][widthindex + r][4] = 0
                        if heightindex == 0 or heightindex == len(height) - 1: # if height edge exclude all blocks to top or bottom
                            for i in range(0, len(visionlayers) - layerindex):  
                                for r in range(0, i):
                                    visionlayers[layerindex + i][heightindex + r][widthindex][4] = 0
                    widthindex += 1
                heightindex += 1
            layerindex += 1


