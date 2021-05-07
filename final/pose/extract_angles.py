import cv2
import numpy as np

class ExtractAngles(object):
    
    def __init__(self, topology, bones):
        self.topology = topology
        self.bones = bones

    def __call__(self, image, object_counts, objects, normalized_peaks, sample):
        topology = self.topology
        bones = self.bones
        height = image.shape[0]
        width = image.shape[1]
        
        K = topology.shape[0]
        count = int(object_counts[0])
        K = topology.shape[0]
        for i in range(count):
            obj = objects[0][i]

            for k in range(K):
                c_a = topology[k][2]
                c_b = topology[k][3]
                if obj[c_a] >= 0 and obj[c_b] >= 0:
                    #print("c_a="+str(c_a.item())+"\tc_b="+str(c_b.item()))
                    peak0 = normalized_peaks[0][c_a][obj[c_a]]
                    peak1 = normalized_peaks[0][c_b][obj[c_b]]

                    # c_a
                    x0 = round(float(peak0[1]) * width)
                    y0 = round(float(peak0[0]) * height)
                    
                    # c_b
                    x1 = round(float(peak1[1]) * width)
                    y1 = round(float(peak1[0]) * height)

                    a = c_a.item()
                    b = c_b.item()
                    p0 = complex(x0,y0)
                    p1 = complex(x1,y1)

                    if (a,b) in bones:
                        angle = np.angle(p1-p0)
                        sample[bones.index((a,b))] = angle
                    elif (b,a) in bones:
                        angle = np.angle(p0-p1)
                        sample[bones.index((b,a))] = angle
                    
                        
                    

                    
