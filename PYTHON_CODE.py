import serial
import mysql.connector
import threading
import time

# connecting to mysql database
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="env_monitor"
)

cursor = db.cursor()

# connecting to arduino
ser = serial.Serial("COM11", 9600, timeout=1)
time.sleep(2)

# EXTREME VALUE LIMITS
TEMP_LOW = 10
TEMP_HIGH = 32

HUMIDITY_LOW = 20
HUMIDITY_HIGH = 80

LIGHT_LOW = 100
LIGHT_HIGH = 900

latest_data = None
data_lock = threading.Lock()
running = True


# extreme values checking function
def check_extremes(temp, humidity, light):

    if temp < TEMP_LOW:
        print("ALERT: Temperature is extremely LOW!")

    elif temp > TEMP_HIGH:
        print("ALERT: Temperature is extremely HIGH!")

    if humidity < HUMIDITY_LOW:
        print("ALERT: Humidity is extremely LOW!")

    elif humidity > HUMIDITY_HIGH:
        print("ALERT: Humidity is extremely HIGH!")

    if light < LIGHT_LOW:
        print("ALERT: Light level is extremely DARK!")

    elif light > LIGHT_HIGH:
        print("ALERT: Light level is extremely BRIGHT!")


# reading arduino data
def collect_data():
    global latest_data, running

    while running:
        try:
            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            values = line.split(",")

            if len(values) != 3:
                continue

            temp = float(values[0])
            humidity = float(values[1])
            light = int(values[2])

            with data_lock:
                latest_data = (temp, humidity, light)

            # SAVE TO DATABASE
            cursor.execute(
                """
                INSERT INTO readings
                (temperature, humidity, light)
                VALUES (%s, %s, %s)
                """,
                (temp, humidity, light)
            )

            db.commit()

            # ALERT ONLY WHEN VALUES ARE EXTREME
            check_extremes(temp, humidity, light)

        except (ValueError, serial.SerialException) as e:
            print("Reading error:", e)

        except mysql.connector.Error as e:
            print("Database error:", e)


# interface for user commands
def command_interface():
    global running

    print("\nENVIRONMENT MONITOR STARTED")
    print("Commands:")
    print("DATA - Retrieve current readings")
    print("EXIT - Stop monitoring\n")

    while running:
        command = input("Enter command: ").strip().upper()

        if command == "DATA":

            with data_lock:
                data = latest_data

            if data is None:
                print("No readings available yet.")
            else:
                temp, humidity, light = data

                print("\n--- CURRENT ENVIRONMENT DATA ---")
                print(f"Temperature: {temp:.1f} °C")
                print(f"Humidity: {humidity:.1f} %")
                print(f"Light Level: {light}")
                print("--------------------------------\n")

        elif command == "EXIT":
            running = False
            print("Stopping environmental monitoring...")

        else:
            print("Unknown command. Use DATA or EXIT.")


# threads
reader = threading.Thread(target=collect_data, daemon=True)
reader.start()

command_interface()

# finalizing
running = False
reader.join(timeout=2)

ser.close()
cursor.close()
db.close()

print("System shut down.")
