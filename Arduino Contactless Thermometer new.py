import warnings
import serial.tools.list_ports
import tkinter as tk
import datetime
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


matplotlib.use("TkAgg")

arduino_ports = [
    p.device
    for p in serial.tools.list_ports.comports()
    if 'Arduino' in p.description
    ]
if not arduino_ports:
    raise IOError("No Arduino found")
if len(arduino_ports) > 1:
    warnings.warn('Multiple Arduinos found - using the first')

print(arduino_ports[0])

ser = serial.Serial(arduino_ports[0], baudrate=9600, timeout=1)
dict = {
    'ObjTemp': [],
    'AmbTemp': [],
    't': [],
    'ObjTempp': [],
    'AmbTempp': [],
    'tp': [],
    'logflag': 0,
    'i': 0,

    'Tmin': 9999,
    'Tmax': 0,
    'Tavg': 0,
    'sum': 0,

    'TminA': 9999,
    'TmaxA': 0,
    'TavgA': 0,
    'sumA': 0,

    'TminDA': 9999,
    'TmaxDA': 0,
    'TavgDA': 0,
    'sumDA': 0,
    'TminDO': 9999,
    'TmaxDO': 0,
    'TavgDO': 0,
    'sumDO': 0,
    'f': open("temp.txt", "w+")
}


def start(dict):
    filename = '.\logs\\temperature log ' + \
                datetime.datetime.now().strftime("%d-%m-%Y_%H-%M-%S") + '.txt'
    dict['f'] = open(filename, 'w+')
    dict['logflag'] = 1
    Logind["bg"] = "green"
    Logind.delete(0.0, END)
    Logind.insert(END, "ON")


def stop(dict):
    dict['logflag'] = 0
    dict['f'].close()
    Logind["bg"] = "red"
    Logind.delete(0.0, END)
    Logind.insert(END, "OFF")


def browse():
    window.logfile = tk.filedialog.askopenfilename(initialdir=".\logs",
                                                   title="Select file",
                                                   filetypes=(("log files", "*.txt"), ("all files", "*.*")))
    e.delete(0, END)
    e.insert(END, window.logfile)


def plot_data(dict):
    i = 0
    fig2.clf()
    filename = e.get()
    plotfile = open(filename, 'r')
    data = plotfile.read().split('\n')
    for line in data:
        if len(line) > 1:
            i += 1
            x, T1, T2 = line.split("--")
            jt, y1 = T1.split(':')
            jt, y2 = T2.split(':')
            dict['ObjTempp'].append(float(y1))
            dict['AmbTempp'].append(float(y2))
            dict['tp'].append(i)
            if float(y1) > dict['TmaxDO']:
                dict['TmaxDO'] = float(y1)
            if float(y1) < dict['TminDO']:
                dict['TminDO'] = float(y1)
            dict['sumDO'] += float(y1)
            dict['TavgDO'] = dict['sumDO']/i
            if float(y2) > dict['TmaxDA']:
                dict['TmaxDA'] = float(y2)
            if float(y2) < dict['TminDA']:
                dict['TminDA'] = float(y2)
            dict['sumDA'] += float(y2)
            dict['TavgDA'] = dict['sumDA']/i
    ax2 = plt.plot(dict['tp'], dict['ObjTempp'], 'r')
    ax2 = plt.plot(dict['tp'], dict['AmbTempp'], 'b')
    MinD.delete(0.0, END)
    MinD.insert(END, "MinObj: " + str(dict['TminDO']) + "\nMinAmb: " + str(dict['TminDA']))
    MaxD.delete(0.0, END)
    MaxD.insert(END, "MaxObj: " + str(dict['TmaxDO']) + "\nMaxAmb: " + str(dict['TmaxDA']))
    AvgD.delete(0.0, END)
    AvgD.insert(END, "AvgObj: " + str(round(dict['TavgDO'], 2)) + "\nAvgAmb: " + str(round(dict['TavgDA'], 2)))
    dict['ObjTempp'] = []
    dict['AmbTempp'] = []
    dict['tp'] = []
    dict['sumDA'] = 0
    dict['sumDO'] = 0
    plt.show()
    plotfile.close()


def refresh_graph(dict):
    ser.flushInput()
    ser.flushOutput()
    x = ' '
    y = ' '
    if len(dict['t']) == 30:
        dict['t'].pop(0)
        dict['ObjTemp'].pop(0)
        dict['AmbTemp'].pop(0)
    graphData = ser.readline().decode('ascii')
    lines = graphData.split("\n")
    for line in lines:
        if len(line) > 1:
            x, y = line.split(",")
            dict['ObjTemp'].append(float(x))
            dict['AmbTemp'].append(float(y))
            dict['i'] += 1
            dict['t'].append(dict['i'])
            if float(x) > dict['Tmax']:
                dict['Tmax'] = float(x)
            if float(x) < dict['Tmin']:
                dict['Tmin'] = float(x)
            dict['sum'] += float(x)
            dict['Tavg'] = dict['sum']/dict['i']
            if float(y) > dict['TmaxA']:
                dict['TmaxA'] = float(y)
            if float(y) < dict['TminA']:
                dict['TminA'] = float(y)
            dict['sumA'] += float(y)
            dict['TavgA'] = dict['sumA']/dict['i']
    ax1.clear()
    ax1.plot(dict['t'], dict['ObjTemp'], 'r')
    ax1.plot(dict['t'], dict['AmbTemp'], 'b')
    ax1.set_xlim(left=max(0, dict['i']-30), right=dict['i']+10)
    ax1.set_ylim(bottom=0, top=100)
    if dict['logflag']:
        dict['f'].write(str(datetime.datetime.now().strftime("%H:%M:%S")) + "--Object temp:" + x + "--Ambient temp:" + y + "\n")
    output.delete(0.0, END)
    output.insert(END, "Object temp:" + x + "\nAmbient temp: " + y)
    Min.delete(0.0, END)
    Min.insert(END, "MinObj: " + str(dict['Tmin']) + "\nMinAmb: " + str(dict['TminA']))
    Max.delete(0.0, END)
    Max.insert(END, "MaxObj: " + str(dict['Tmax']) + "\nMaxAmb: " + str(dict['TmaxA']))
    Avg.delete(0.0, END)
    Avg.insert(END, "AvgObj: " + str(round(dict['Tavg'], 2)) + "\nAvgAmb: " + str(round(dict['TavgA'], 2)))


window = Tk()
window.title('Arduino contactless thermometer')
window.iconbitmap('icon.ico')

canvas = FigureCanvasTkAgg(fig, window)
canvas.draw()
canvas.get_tk_widget().grid(row=4, column=6, sticky=E, rowspan=14, columnspan=11)

output = Text(window, width=20, height=2, wrap=WORD, background="Grey")
output.grid(row=11, column=2, rowspan=2, columnspan=4, padx=15)

Logind = Text(window, width=3, height=1, background='red', fg='white')
Logind.grid(row=7, column=5)

Logind.insert(END, "OFF")

Min = Text(window, width=20, height=2, wrap=WORD, background="Grey")
Min.grid(row=2, column=7, pady=30)

Max = Text(window, width=20, height=2, wrap=WORD, background="Grey")
Max.grid(row=2, column=9, pady=30)

Avg = Text(window, width=20, height=2, wrap=WORD, background="Grey")
Avg.grid(row=2, column=11, pady=30)

MinD = Text(window, width=20, height=2, wrap=WORD, background="Grey")
MinD.grid(row=23, column=7, pady=30)

MaxD = Text(window, width=20, height=2, wrap=WORD, background="Grey")
MaxD.grid(row=23, column=9, pady=30)

AvgD = Text(window, width=20, height=2, wrap=WORD, background="Grey")
AvgD.grid(row=23, column=11, pady=30)

photo = PhotoImage(file="ferlogofinal.png")
Label(window, image=photo, bg="white").grid(row=0, column=0, rowspan=6, columnspan=4, padx=10, pady=10)

buttonSTART = tk.Button(window,
                        text="START LOGGING DATA",
                        background="Grey",
                        activebackground="White",
                        command=lambda: start(dict)).grid(row=7, column=2, columnspan=2)
buttonSTOP = tk.Button(window,
                       text="STOP LOGGING DATA",
                       background="Grey",
                       command=lambda: stop(dict)).grid(row=9, column=2, columnspan=2)
buttonBROWSE = tk.Button(window,
                         text="BROWSE LOG FILE",
                         background="Grey",
                         command=browse).grid(row=20, column=2, pady=10)
buttonPLOT = tk.Button(window,
                       text="PLOT FROM A LOG FILE",
                       background="Grey",
                       command=lambda: plot_data(dict)).grid(row=22, column=2, pady=(0, 20))
e = Entry(window, background="Grey", width=100)
e.grid(row=20, column=4, sticky=W, columnspan=17)

ani = animation.FuncAnimation(fig, lambda p: refreshGraph(dict), interval=500)
mainloop()
