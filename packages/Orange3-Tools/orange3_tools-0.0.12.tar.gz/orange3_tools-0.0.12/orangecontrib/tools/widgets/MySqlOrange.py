import Orange
from orangewidget import settings
from orangewidget.widget import OWBaseWidget, Input, Message
from orangewidget import gui
from Orange.widgets.widget import Output, Msg
from Orange.data import Table, Domain, ContinuousVariable, DiscreteVariable, TimeVariable, StringVariable
from AnyQt.QtWidgets import QTextEdit

# Otros imports
from dataclasses import field
import mysql.connector
from mysql.connector import FieldType

class MySqlOrange(OWBaseWidget):
    # Nombre del widget como se verá en el lienzo
    name = 'MySql Query'
    icon = 'icons/mysql-orange.svg'
    keywords = ["widget", "tools"]
    # category = 'Data'
    category = 'Tools'
    
    # Parámetros del widget
    host = settings.Setting('kaos.unizar.es')
    port = settings.Setting(31766)
    user = settings.Setting('aire')
    password = settings.Setting('CirceEolicos')
    database = settings.Setting('curva')
#    query = settings.Setting('select TIMESTAMP, RecNbr, Vel1_Avg, Vel1_Std, Vel1_Max, Vel1_Min from datalogger;')
    query = settings.Setting('select id,t,N_datos,Pot,Pot_std,Pot_max,Pot_min,VT1,VT1_std,VT1_max,VT1_min,VT2,VT2_std,VT2_max,VT2_min,Dir,Temp,Temp_std,Temp_max,Temp_min, Pres,Pres_std,Pres_max,Pres_min,Hum, Hum_std,Hum_min,Hum_max,Disp1,Disp2 from curva_promediada;')

    class Outputs:
        data = Output('Data', Table)

    def open_query(self):
    # clase para guardar los campos de la consulta y sus tipos
        class Campo:
            def __init__(self, nombre = '', tipo = -1):
                self.nombre = nombre
                self.tipo = tipo
        
        list_global = [] # lista final. Contendrá los datos de salida
        list_temp = [] # lista temporal, usada sólo para conversión
        list_domain = [] # lista en la que se guardarán los tipos de datos Orange que corresponden a cada columna
        list_campos = [] # lista de campos y tipo de datos de cada campo

        self.conn = mysql.connector.connect(user=self.user, password=self.password, host=self.host, port=self.port, db=self.database)
        cur = self.conn.cursor() 
        cur.execute(self.query)
        rows = cur.fetchall()

        # guardar los nombres y tipos de campo
        for desc in cur.description:
            colname = desc[0]
            coltype = desc[1]
            campo = Campo(colname, FieldType.get_info(coltype))
            list_campos.append(campo)

        self.conn.close()

        # Además hay que especificar el tipo de valor para el domain para cada fila
        single_row = rows[0]
        for i in range(len(single_row)):
            # se asigna el tipo de datos de la salida a list_domain según los valores de la lista list_campos
            # y se van añadiendo los valores devueltos por MySql a la lista list_temp
            nombre_campo = list_campos[i].nombre
            tipo_datos = list_campos[i].tipo
            if tipo_datos in ['VAR_STRING', 'STRING', 'BLOB','SET'] :
                list_domain.append(StringVariable(nombre_campo))
            elif tipo_datos in ['DATETIME', 'TIMESTAMP', 'TIME', 'DATE']:
                list_domain.append(TimeVariable(nombre_campo))
            elif tipo_datos in ['DECIMAL', 'NEWDECIMAL', 'LONG', 'INT', 'FLOAT', 'DOUBLE','BIT', 'YEAR']:
                list_domain.append(ContinuousVariable(nombre_campo))
            else:  
                raise Exception('Error: Tipo de valor no reconocido: ' + tipo_datos)

        # A continuación las filas (recibidas como tuplas) se convierten a una lista, que
        # es el formato que debe tener el output del witget

        # para cada fila recibida de la bd
        for single_row in rows :
            # para cada campo en la fila
            for i in range(len(single_row)):
                # se asigna el tipo de datos de la salida a list_domain según los valores de la lista list_campos
                # y se van añadiendo los valores devueltos por MySql a la lista list_temp
                valor_guardar = single_row[i]
                nombre_campo = list_campos[i].nombre
                if tipo_datos in ['VAR_STRING', 'STRING','BLOB','SET'] :
                    # list_temp.append(str(valor_guardar))
                    list_temp.append(str(valor_guardar))
                elif tipo_datos in ['DATETIME', 'TIMESTAMP', 'TIME', 'DATE']:
                    # list_temp.append(valor_guardar)
                    list_temp.append(str(valor_guardar))
                elif tipo_datos in ['DECIMAL', 'NEWDECIMAL', 'LONG', 'INT', 'FLOAT', 'DOUBLE','BIT', 'YEAR']:
                    # list_temp.append(int(valor_guardar))
                    list_temp.append(str(valor_guardar))
                    # list_temp.append(valor_guardar)
                else:  
                    print(tipo_datos)
                    raise Exception('Error: Tipo de valor no reconocido' + tipo_datos)
            list_global.append(list_temp)
            list_temp = []

        # data = self.get_table()
        # self.data_desc_table = data
        # self.Outputs.data.send(data)
        try:
            dominio = Domain(list_domain)
            out_data = Table.from_list(dominio, list_global)
            self.Outputs.data.send(out_data)
            # self.message_bar.clear()
            # self.warning('Query OK')
        except Exception as err:
            self.error('Error: ' + err)

    # class Outputs:
    #     data = Output('Data', Table, doc='Attribute-valued dataset read from the query.')

    want_main_area = False

    def __init__(self):
        super().__init__()

        self.data = None
        # self.proportions = 30
        box = gui.widgetBox(self.controlArea, 'Parameters')
        gui.lineEdit(box, self, 'host', 'Host',  valueType=str)
        gui.lineEdit(box, self, 'port', 'Port',  valueType=int)
        gui.lineEdit(box, self, 'user', 'User',  valueType=str) # TODO: password
        pw=gui.lineEdit(box, self, 'password', 'Password',  valueType=str)
        pw.setEchoMode(pw.Password)
        pw.show()
        gui.lineEdit(box, self, 'database', 'Database',  valueType=str)
        gui.lineEdit(box, self, 'query', 'Query' , valueType=str)
        gui.button(box, self, 'Ok', callback=self.ok_button)


    # @Inputs.data
    # def set_data(self, data):
    #     self.Data = data

    def commit(self):
        self.open_query()

    def ok_button(self):
        self.open_query()

        return
              
    
if __name__ == '__main__':
    from Orange.widgets.utils.widgetpreview import WidgetPreview  # since Orange 3.20.0
    WidgetPreview(MySqlOrange).run()