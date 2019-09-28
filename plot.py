import os
import shutil
import sys
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.animation as animation

milliseconds = True # If true, time is in milliseconds

try:
    save_var = sys.argv[1]

    plot_dir = "plots/" + save_var
    save_file = "saves/" + save_var + ".save"

    try:
        animate = sys.argv[2] == "-animate"
        static = sys.argv[2] == "-static"

        if animate:
            try:
                FPS = int(sys.argv[3])
            except:
                print("fps is missing or invalid, animating at 60 fps")

                FPS = 60
        elif static:
            try:
                invert = sys.argv[3]
            except:
                invert = False
    except:
        animate = False
        static = False
except:
    raise Exception("Variable name to be plotted is missing")

if not os.path.exists('plots'):
    os.mkdir('plots')

time_m = 0
time_M = 0
dt = 0.0

with open("plot_parameters.txt", "r") as plot_parameters:
    i = 0
    for line in plot_parameters:
        i += 1
        line = line.strip()

        if i % 2 == 1:
            name = line
        else:
            value = line

            if name == "dt":
                dt = float(value)

                if milliseconds:
                    dt = dt * 0.001

try:
    frameskip = 1 / (dt * FPS)
except:
    frameskip = 1

if os.path.exists(save_file):
    if os.path.isdir(plot_dir):
        shutil.rmtree(plot_dir)
    
    os.mkdir(plot_dir)

    with open(save_file, "rb") as save:
        shape = [int(i) for i in save.readline().decode("utf-8").strip().split(" ")]
        var = np.fromfile(save, dtype=np.float32).reshape(shape)
        dims = len(shape)

        print("Total number of snaps is " + str(shape[0]))

        if dims == 2:
            if static == True:
                figure = plt.figure()

                Y, X = np.linspace(0, 1, shape[0]), np.linspace(0, 1, shape[1])

                if invert:
                    plt.gca().invert_yaxis()

                plt.pcolor(X, Y, var, vmin = -5, vmax = 5, cmap = mpl.cm.gray)
                plt.colorbar()

                plt.show()
        elif dims == 3:
            if static == False:
                cdict = {
                    'red'  :  ( (0.0, 0.25, .25), (0.02, .59, .59), (1., 1., 1.)),
                    'green':  ( (0.0, 0.0, 0.0), (0.02, .45, .45), (1., .97, .97)),
                    'blue' :  ( (0.0, 1.0, 1.0), (0.02, .75, .75), (1., 0.45, 0.45))
                }

                cm = mpl.colors.LinearSegmentedColormap('my_colormap', cdict, 1024)

                figure = plt.figure()

                X, Y = np.meshgrid(np.arange(0, shape[1], 1.0), np.arange(0, shape[2], 1.0))
                Y = np.flipud(Y)

                if animate:
                    mesh = plt.pcolormesh(X, Y, var[0], cmap = cm, vmin = -1, vmax = 1)
                    plt.colorbar()

                    def plot(frame):
                        frame = int(frame * frameskip)
                        if frame < shape[0]:
                            data = var[frame]
                        else:
                            data = var[-1]
                        
                        mesh.set_array(data[:-1, :-1].ravel())
                        
                        return mesh,

                    def init():
                        mesh.set_array([])

                        return mesh,

                    anim = animation.FuncAnimation(figure, plot, int(shape[0] / frameskip), init, interval = 1, blit = True)

                    try:
                        anim.save(plot_dir + "/animation.mp4", animation.FFMpegWriter(fps = FPS, extra_args = ['-vcodec', 'libx264']))
                    except Exception as exception:
                        print("\n\'ffmpeg\' error, have you downloaded it?\n")
                        print(exception)
                else:
                    for t in range(shape[0]):
                        plt.pcolormesh(X, Y, var[t], cmap = cm, vmin = -1, vmax = 1)
                        plt.colorbar()

                        plt.savefig(plot_dir + "/plot%s.png" % t)
                        plt.clf()
        else:
            raise Exception("Plotting not implemented for " + str(dims) + " dimensions")
else:
    raise Exception("Could not find \"" + save_file + "\" file")
