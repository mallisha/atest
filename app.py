from flask import Flask,render_template, request
import pyodbc 
import math


app = Flask(__name__)

driver = '{ODBC Driver 18 for SQL Server}'
server_name = 'assgnsql'
db_name = 'Assignment2'
#connection string
connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:assgnsql.database.windows.net,1433;Database=Assignment2;Uid=malli01;Pwd=Mallisha01;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'


def exe_query(query,param = None):
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    if param is not None:
        cursor.execute(query,param)
    else:
        cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results



@app.route('/',methods=['GET','POST'])
def index():
    message = ''

    # query = "select * from all_month "
#To find out earthquakes below a certain magnitude:
    if request.method == 'POST' and request.form.get('ans') == 'Submit':
        magni = request.form.get('mag')
        query = "select * from all_month where mag > ?"
        parameter = (magni,)
        res = exe_query(query,parameter)
        return render_template('results.html', results=res)

# To search for earthquakes within a magnitude range and within certain days:
    elif request.method == 'POST' and (request.form.get('sub') == 'Submit'):

        Strt_range = float(request.form.get('magnitude_strt'))
        End_range = float(request.form.get('magnitude_end'))
        date_from = request.form.get('date_frm')
        date_to = request.form.get('date_to')
        query = " select * from all_month where time >= ? and time <= ? and mag between ? and ?"
        parameters = (date_from,date_to,Strt_range,End_range)
        res = exe_query(query,parameters)
        return render_template('results.html', results=res)

 # To find out earthquakes within a distance of a specified location and to find clusters based on location
    elif request.method == 'POST' and request.form.get('submit') == 'earthquakes within area' or (request.form.get('submit') == 'Clusters on area'):

        lat = float(request.form.get('lat'))
        longi = float(request.form.get('longi'))
        lat_distance = float(request.form.get('dist')) / 111
        log_distance = float(request.form.get('dist')) / (111*math.cos(math.radians(lat)))
        

        if (request.form.get('submit') == 'Clusters on area'):
            query += "and latitude >= ? and latitude <= ? and longitude >= ? and longitude <=? and type = 'earthquake' and (select count(*) from all_month WHERE latitude >= ? and latitude <= ? and (longitude >= ? and longitude <= ?)and type = 'earthquake') >4"
            parameters = (lat-lat_distance,lat+lat_distance,longi-lat_distance,longi+lat_distance,lat-lat_distance,lat+lat_distance,longi-lat_distance,longi+lat_distance)
            results = exe_query(query,parameters)
            if len(results) == 0:
                return "No records to display"
        elif request.form.get('submit') == 'earthquakes within area':
             query += "and latitude >= ? and latitude <= ? and longitude >= ? and longitude <=?"
             parameters = (lat-lat_distance,lat+lat_distance,longi-log_distance,longi+log_distance)
             results = exe_query(query,parameters)
        return render_template('index.html', results=results)

# to find the earthqueake with mag occur at night or not:
    elif request.method == 'POST' and request.form.get('submit') == 'day or night':
        mag = request.form.get('mag')
        n_query = "SELECT DATEPART(hour,time) as hour_time ,count(*) as high_count from all_month where mag > ? and (DATEPART(hour,time) <6 or DATEPART(hour,time) >=20) group by DATEPART(hour,time) order by high_count desc"
        parameters = (mag,)
        results_night = exe_query(n_query, parameters)
        return render_template('daynigh.html', night=results_night, message=message)
    return render_template('index.html')



if __name__ == '__main__':
    app.run(debug=True)


