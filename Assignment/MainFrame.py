import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import QStringListModel
from PyQt5 import QtWidgets
from cityTemperature import Ui_Form
from process_data import getCityName, resource_path
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.dates as mdates
from datetime import datetime

filePath = './dataset/'


class Figure_Canvas(FigureCanvas):
	def __init__(self, parent=None, width=11, height=11, dpi=70): 
		fig = Figure(figsize=(width, height), dpi=70)

		FigureCanvas.__init__(self,fig)
		self.setParent(parent)

		self.ax = fig.add_subplot(111)

	def generate(self, xs, ys, num, c, thresold=''):
		if(num == 1):
			self.ax.cla()
			self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%dT%H%M'))
			self.ax.xaxis.set_major_locator(mdates.DayLocator())
			x = range(len(xs))
			self.ax.set_title('Temperature over time of %s'%c[0])
			self.ax.set_xlabel('Time')
			self.ax.set_ylabel('Temperature(F)')
			self.ax.set_xticks(x[::8])
			self.ax.set_xticklabels(xs[::8], rotation=70)
			self.ax.plot(x, ys, label='%s'%c[0])
			self.ax.legend(loc='upper right')
			if thresold is not '':
				x, y_sc = self.pointsFilter(thresold, xs, ys, num)
				self.ax.scatter(x, y_sc, s=40, alpha=0.7)

		else:
			self.ax.cla()
			self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%dT%H%M'))
			self.ax.xaxis.set_major_locator(mdates.DayLocator())
			x = range(len(xs[0]))
			self.ax.set_title('Temperature trend among multiple cities')
			self.ax.set_xlabel('Time')
			self.ax.set_ylabel('Temperature(F)')
			self.ax.set_xticks(x[::8])
			self.ax.set_xticklabels(xs[0][::8], rotation=70)
			for i in range(num):
				self.ax.plot(x, ys[i], label='%s'%c[i])
			self.ax.legend(loc='upper right')
			if thresold is not '':
				x, y_sc = self.pointsFilter(thresold, xs, ys, num)
				for i in range(num):
					self.ax.scatter(x[i], y_sc[i], s=40, alpha=0.7)


	def pointsFilter(self, thresold, xs, ys, num):
		x_sc = []
		y_sc = []
		if (num == 1):
			for i in range(len(ys)):
				if ys[i] < float(thresold):
					y_sc.append(ys[i])
					x_sc.append(i)
		else:
			for i in range(num):
				x_tmp = []
				y_tmp = []
				for j in range(len(ys[i])):
					if ys[i][j] < float(thresold):
						x_tmp.append(j)
						y_tmp.append(ys[i][j])
				x_sc.append(x_tmp)
				y_sc.append(y_tmp)
		return x_sc, y_sc

class MyMainForm(QMainWindow, Ui_Form):
	def __init__(self, parent=None):
		super(MyMainForm, self).__init__(parent)
		self.setupUi(self)
		self.setWindowTitle("city_game")
		self.initStuff()

		self.alpha_button.clicked.connect(self.display_a)
		self.reverse_button.clicked.connect(self.display_r)

		self.city_list.clicked.connect(self.listClicked)
		self.Plot_button.clicked.connect(self.plotClicked)


	def display_a(self):
		self.cityList.sort()

		self.slm.setStringList(self.cityList)
		self.city_list.setModel(self.slm)

	def display_r(self):
		self.cityList.sort(reverse=True)

		self.slm.setStringList(self.cityList)
		self.city_list.setModel(self.slm)

	def initStuff(self):
		self.cityList, self.city_data = getCityName(resource_path(filePath))


		# init List
		self.slm = QStringListModel()
		self.slm.setStringList(self.cityList)
		self.city_list.setModel(self.slm)




		self.display_a()

	def listClicked(self, qModelIndex):
		self.city_info_text.clear()
		city_chosed = self.cityList[qModelIndex.row()]
		city_info = self.city_data[city_chosed]
		i = 0
		for key in city_info:
			i = i + 1
			if(i == 10):
				break
			self.city_info_text.append(key + " : " + city_info[key])

	def plotClicked(self):
		thresold = self.threshold_line.text()
		print(type(thresold))
		num, time, temperature, c = self.CheckBox_check()
		### sanity check ###
		if not thresold.isdigit() and thresold != '':
			QMessageBox.warning(self,'Warning', 'Please enter a valid number')
			return
		### end check ###
		### plot begin ###
		if (num == 1):
			self.dr = Figure_Canvas()
			xs = [datetime.strptime(d, '%Y%m%dT%H%M').date() for d in time[0]]
			ys = []
			for y in temperature[0]:
				ys.append(float(y.split('.')[0] + '.' + y.split('.')[1][:2]))
			self.dr.generate(xs, ys, num, c, thresold)
			graphicscene = QtWidgets.QGraphicsScene()
			graphicscene.addWidget(self.dr)
			self.graphics_View.setScene(graphicscene)
			self.graphics_View.show()
		if(num > 1):
			self.dr = Figure_Canvas()
			xs = []
			ys = []
			for i in range(num):
				xs.append([datetime.strptime(d, '%Y%m%dT%H%M').date() for d in time[i]])
				tmp = []
				for y in temperature[i]:
					tmp.append(float(y.split('.')[0] + '.' + y.split('.')[1][:2]))
				ys.append(tmp)
			self.dr.generate(xs, ys, num, c, thresold)
			graphicscene = QtWidgets.QGraphicsScene()
			graphicscene.addWidget(self.dr)
			self.graphics_View.setScene(graphicscene)
			self.graphics_View.show()

		### end plot ###



	def CheckBox_check(self):
		num = 0
		time = []
		temperature = []
		c = []

		checkbox_state= []
		for i in range(1, 14):
			temp = getattr(self, "checkBox_%d"%i)
			if temp.checkState():
				checkbox_state.append(1)
				num = num + 1
			else:
				checkbox_state.append(0)

		self.cityList.sort()
		city_dict = {}
		i = 0
		for city in self.cityList:
			city_dict[i] = city
			i = i + 1
		for i in range(0, 13):
			if(checkbox_state[i] == 1):
				# get city data
				city_info = self.city_data[city_dict[i]]
				j = 0
				keyset = []     # time
				valueset = []   # temperature
				for key in city_info:
					j = j + 1
					if(j < 11):
						continue
					keyset.append(key)
					valueset.append(city_info[key])
				time.append(keyset)
				temperature.append(valueset)
				c.append(self.cityList[i])


		return num, time, temperature, c




if __name__ =="__main__":
	app = QApplication(sys.argv)
	myWin = MyMainForm()

	myWin.show()

	sys.exit(app.exec_())
