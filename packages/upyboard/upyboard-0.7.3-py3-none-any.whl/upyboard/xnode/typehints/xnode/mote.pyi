import utime
import ustruct
import machine
 
from micropython import const

            
class Led():
    """
    The Led object is used to control the state of the LED.
    """
    
    def on(self) -> None:
        """
        light on the LED.
        """
        
    def off(self) -> None:
        """
        light off the LED.
        """
 
    def toggle(self) -> None:
        """
        Toggle the LED state.
        """
    
    def state(self) -> bool:
        """
        Return the state of the LED.
        
        :return: ``True`` if the LED is on, ``False`` if the LED is off.
        """
 

class SupplyVoltage(machine.ADC):
    """
    The supply voltage sensor is an analog sensor that measures the supply voltage.
    """

    def read(self) -> float:
        """
        Reads the supply voltage.
        
        :return: The supply voltage.
        """


class Illuminance:
    """
    The illuminance sensor is a digital sensor that measures the illuminance in lux.
    """
    
    CONTINUOUS_MODE = const(0x10)
    ONE_TIME_MODE = const(0x20)
    
    def __init__(self, scale_factor=2.8):
        """
        Initializes the illuminance sensor.
        
        :param scale_factor: The scale factor.
        """ 
        
    def read(self, continuous=True):            
        """
        Reads the illuminance value.
        
        :param continuous: If ``True`` the sensor is in continuous mode.
        
        :return: The illuminance value.
        """

class Tphg:
    """
    This object is used to read temperature, pressure, humidity and gas values.
    or to calculate the altitude and sea level pressure.
    and to calculate the IAQ index.
    """
    
    def __init__(self, temp_weighting:float=0.10, pressure_weighting:float=0.05, humi_weighting:float=0.20, gas_weighting:float=0.65, gas_ema_alpha:float=0.1, temp_baseline:float=23.0, pressure_baseline:float=1013.25, humi_baseline:float=45.0, gas_baseline:int=450_000) :
        """
        Initializes the Tphg sensor.        
              
        :param temp_weighting: Temperature weighting.
        :param pressure_weighting: Pressure weighting.        
        :param humi_weighting: Humidity weighting.
        :param gas_weighting: Gas weighting.
        :param gas_ema_alpha: Gas EMA alpha.
        :param temp_baseline: Temperature baseline.
        :param pressure_baseline: Pressure baseline.
        :param humi_baseline: Humidity baseline.
        :param gas_baseline: Gas baseline.
        """ 
        
    def set_temperature_correction(self, value:float) -> None:
        """
        Compensates for temperature.
        
        :param value: Temperature compensation value
        """


    def read(self, gas: bool=False) -> tuple:
        """
        Reads the temperature, pressure, humidity and gas values.
        
        :param gas: If ``True`` reads the gas value.
        
        :return: A tuple with temperature, pressure, and humidity values. However, if the parameter gas is True, gas is added.    
        """

        
    def sealevel(self, altitude:float) -> float:
        """
        calculates the pressure at sea level based on the altitude
        
        :param altitude: Altitude in meters.
        
        :return: The pressure at sea
        """
        
    def altitude(self, sealevel:float) -> float: 
        """
        calclates the altitude based on the sealevel pressure
        
        :param sealevel: Pressure at sea level.
        
        :return: The altitude in meters.
        """

    def iaq(self) -> tuple:
        """
        Reads the IAQ index.
        
        :return: Tuple with the IAQ index, temperature, pressure, humidity and gas.
        """

    def burnIn(self, threshold: float=0.01, count: int=10, timeout_sec: int=180) -> tuple:
        """
        Performs stabilization operations required for gas measurements.
        
        :param threshold: The threshold value.
        :param count: The number of measurements.
        :param timeout_sec: The timeout in seconds.
        
        :return: Tuple with the state, gas, deviation.
        """