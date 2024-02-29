from PyP100 import PyP100
import Adafruit_DHT
import time
import logging

TEMP_FIRST_STAGE = 49 # one hour on 49C
TEMP_SND_STAGE = 30   # and then few hours on 30
light_stateON = "ON"
light_stateOFF = "OFF"

Log_Format = "%(levelname)s %(asctime)s - %(message)s"
logging.basicConfig(filename="yogurt.log",
                    filemode="w",
                    format=Log_Format,
                    level=logging.INFO)

logger = logging.getLogger()


def lightLightOn(p100):
    try:
        p100.turnOn()
    except Exception:
        logger.info("Trying to connect again to wall socket.")
        try:
            p100 = connectToLampPlug()
            p100.turnOn()
        except Exception as e:
            logger.info("Didnt manage to change state of light. Sleeping 30s")
            time.sleep(30.0)
            return light_stateOFF
    logger.info("Light ON")
    return light_stateON

def lightLightOff(p100):
    try:
        p100.turnOff()
        logger.info("Light OFF")
    except Exception:
        logger.info("Trying to connect again to wall socket.")
        p100 = connectToLampPlug()
        p100.turnOff()
        try:
            p100 = connectToLampPlug()
            p100.turnOff()
        except Exception as e:
            logger.info("Didnt manage to change state of light. Sleeping 30s")
            time.sleep(30.0)
            return light_stateON
    logger.info("Light OFF")
    return light_stateOFF

def returnBana():
    from  Adafruit_DHT import Bananapi_Sunxi
    return Bananapi_Sunxi

def durationSecs(start_time):
    duration = time.perf_counter() - start_time
    return duration

def makeSomeYogurt(p100):
    sensor = 11 # Set sensor type : Options are DHT11,DHT22 or AM2302
    gpio = 65 # find this number on 'gpio readall' on column BCM
    Adafruit_DHT.common.get_platform = lambda : returnBana()
    light_state = light_stateOFF
    start_time = time.perf_counter()

    #second phase
    while durationSecs(start_time) < 11000:
        try:
            humidity, temperature = Adafruit_DHT.read_retry(sensor, gpio)
            if humidity is not None and temperature is not None:
                logger.info('Current temperature: %s' % temperature)
                light_state = controlTemperature(int(temperature), light_state, p100, TEMP_SND_STAGE)
            else:
                logger.info('Failed to get reading. Try again!')
        finally:
            time.sleep(6.0)


def controlTemperature(current_temp, light_state, p100, ideal_temp):
    if (current_temp > ideal_temp ):
        if (light_state == light_stateON):
            light_state = lightLightOff(p100)
            logger.info("Current temp bigger than %s so light goes off." % ideal_temp)
    if (current_temp < ideal_temp):
        if (light_state != light_stateON):
            light_state = lightLightOn(p100)
            logger.info("Current temp lower than %s so light goes ON." % ideal_temp)
            time.sleep(40.0) # give some margin to warm up
    logger.info(" juhu !")
    return light_state


def connectToLampPlug():
    global p100
    p100 = PyP100.P100("192.168.0.9", "lucija@pavelic.biz", "Dvakonjanapasi1")  # Creating a P100 plug object
    p100.handshake()  # Creates the cookies required for further methods
    p100.login()  # Sends credentials to the plug and creates AES Key and IV for further methods
    return p100

if __name__ == '__main__':


    logger.info ("Let's make some yogurt !")

    while True:
        try:
            p100 = connectToLampPlug()
            break
        except Exception as e:
            logger.info("Dint manage to setup connection to the plug. %s " % e)

    try:
        makeSomeYogurt(p100)
        p100.turnOff()
    except Exception as e:
        logger.error("Something happened. Failed with  %s" % e )
        p100.turnOff()

    logger.info("Yogurt done done !")


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
