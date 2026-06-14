## Arduino-Based-Environment-Monitoring-System
##Arduino-Based Environment Monitoring System consisting of Arduino Uno, DHT22 (3-pin) temperature and humidity sensor, LDR (for light level reading), and MySQL integration using Python.

##set up a database in MySQL before executing code, with 
##database name : env_monitor 
##table name : readings

import serial
import mysql.connector

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Gwakoyu99910",
    database="env_monitor"
)

cursor = db.cursor()

ser = serial.Serial("COM5", 9600)

while True:
    line = ser.readline().decode().strip()

    try:
        temp, humidity, light = line.split(",")

        cursor.execute(
            """
            INSERT INTO readings
            (temperature, humidity, light)
            VALUES (%s, %s, %s)
            """,
            (float(temp), float(humidity), int(light))
        )

        db.commit()

        print("Inserted:", line)

    except Exception as e:
        print("Error:", e)