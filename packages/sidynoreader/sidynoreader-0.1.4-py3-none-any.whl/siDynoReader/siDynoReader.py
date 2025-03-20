from enum import Enum
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Channel():
    def __init__(self, name=""):
        self.name = name
        self.unit = ""
        self.data: list[float] = []
        self.measure_points: list[MeasurePoint] = []
        self.metric: dict[MetricType, float] = {}
    
    def __repr__(self):
        if len(self.data) > 5:
            return f'{self.name} [{self.unit}] - {self.data[0:5]}'
        else:
            return f'{self.name} [{self.unit}] - [ empty ]'

class MeasurePoint():
    def __init__(self):
        self.data: list[float] = []
        self.metric: dict[MetricType, float] = {}

class MetricType(Enum):
    MEAN = 0
    MEDIAN = 1
    MIN = 2
    MAX = 3
    RANGE = 4
    VARIANCE = 5
    STD_DEV = 6

class DynoDataSet():
    """
    This Object contains all data of a Tornado measurement file

    Args:
        filepath (str): Path to the measurement file
        test_state_channel_name (str): If present, name of the channel how contain if it is a measure point
        test_state_threshold (float): Threshold from when it is a measuring point
        time_channel_name (str): Name of the time channel
        time_to_zero (boolean): if set to true, the time channel values start at zero
    """
    def __init__(self, 
                 filepath: str, 
                 test_state_channel_name="test_state",
                 test_state_threshold=50.0,
                 time_channel_name="time",
                 time_to_zero=True):
        self.test_id = filepath.replace("\\", "/").split("/")[-1].split("-")[-1].split(".")[0]
        self.dyno = filepath.replace("\\", "/").split("/")[-1].split("-")[0]
        self.project = filepath.split(".")[-1]
        self.channels = self.__load_data(filepath)
        if time_to_zero:
            self.__set_start_time_to_zero(time_channel_name)
        self.__extract_measure_points(test_state_channel_name, test_state_threshold)
        self.__calculate_metric_for_channel()

    def get_channels(self):
        """ 
        Get all channel names as list

        Returns:
            list[str]: list of channel names
        """
        key_list = list(self.channels.keys())
        channel_list = []

        for key in key_list:
            channel_list.append(self.channels[key.lower()].name)
        return channel_list
    
    def get_description(self, channel_name: str):
        """
        Return the name and the unit of a channel in the following format: "<ChannelName> [<Unit>]"

        Returns:
            str: name and unit of channel
        """
        return f'{self.channels[channel_name.lower()].name} [{self.channels[channel_name.lower()].unit}]'.replace("_", " ")

    def get_data(self, channel_name: str, type=None):
        try:
            if type is None:
                return self.channels[channel_name.lower()].data
            else:
                return float(self.channels[channel_name.lower()].metric[type])
        except Exception as e:
            logger.error(f"Can't find channel name \"{channel_name}\"")
            
    def get_measure_point(self, channel_name: str, type=MetricType.MEAN) -> list[float]:
        measure_point_data = []
        for i in range(len(self.channels[channel_name.lower()].measure_points)):
            measure_point_data.append(float(self.channels[channel_name.lower()].measure_points[i].metric[type]))
        return measure_point_data
    
    def get_measure_point_data(self, channel_name: str) -> list[list[float]]:
        measure_point_data = []
        for measure_point in self.channels[channel_name.lower()].measure_points:
            measure_point_data.append(measure_point.data)
        return measure_point_data
        
    def __load_data(self, filepath: str) -> dict[str, Channel]:
        CHANNEL_NAME_INDEX = 0
        UNIT_NAME_INDEX = 1

        channel_list: list[Channel] = []

        with open(filepath, "r", encoding="latin-1") as file:
            raw = file.readlines()

        for i, row in enumerate(raw):
            for j, channel_data in enumerate(row.split("\t")):
                if i == CHANNEL_NAME_INDEX:
                    channel = Channel(channel_data.replace("\n", ""))
                    channel_list.append(channel)
                elif i == UNIT_NAME_INDEX:
                    channel_list[j].unit = channel_data
                else:
                    try:
                        value = float(channel_data.strip())
                    except ValueError:
                        value = -1

                    channel_list[j].data.append(value)

        return self.__convert_list_to_dict(channel_list)

    def __convert_list_to_dict(self, list: list[Channel]) -> dict[str, Channel]:
        dictionary: dict[str, Channel] = {}
        for channel in list:
            dictionary[channel.name.lower()] = channel

        return dictionary
    
    def __calculate_metric_of_list(self, data = list[float]) -> dict[MetricType, list[float]]:
            metric: dict[MetricType, list[float]] = {}

            metric[MetricType.MEAN] = np.mean(data)
            metric[MetricType.MEDIAN] = np.median(data)
            metric[MetricType.MIN] = np.min(data)
            metric[MetricType.MAX] = np.max(data)
            metric[MetricType.RANGE] = metric[MetricType.MAX]-metric[MetricType.MIN]
            metric[MetricType.STD_DEV] = np.std(data)
            metric[MetricType.VARIANCE] = np.var(data)

            return metric

    def __calculate_metric_for_channel(self):
        for channel in self.channels.values():
            channel.metric = self.__calculate_metric_of_list(channel.data)
            for measurement_point in channel.measure_points:
                measurement_point.metric = self.__calculate_metric_of_list(measurement_point.data)    

    def __extract_measure_points(self, test_state_channel_name: str, test_state_threshold: float):
        is_measure_point = False
        for i, state_value in enumerate(self.channels[test_state_channel_name.lower()].data):

            if not is_measure_point and state_value >= test_state_threshold:
                for channel in self.channels.values():
                    measure_point = MeasurePoint()
                    channel.measure_points.append(measure_point)
                    is_measure_point = True
            
            if is_measure_point:
                for channel in self.channels.values():
                    channel.measure_points[-1].data.append(channel.data[i])

            if state_value < test_state_threshold:
                is_measure_point = False

    def __set_start_time_to_zero(self, time_channel_name: str):
        min_value = np.min(self.channels[time_channel_name.lower()].data)
        self.channels[time_channel_name.lower()].data -= min_value