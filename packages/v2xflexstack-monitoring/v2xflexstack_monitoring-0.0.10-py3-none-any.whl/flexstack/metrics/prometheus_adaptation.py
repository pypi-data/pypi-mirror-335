import os

from prometheus_client import Histogram, Gauge, CollectorRegistry, start_http_server

PROMETHEUS_PORT = int(os.getenv("PROMETHEUS_CLIENT_PORT", 8000))


class PrometheusClientPull:
    def __init__(self) -> None:
        self.registry = CollectorRegistry()

        self.latency = Histogram("latency", "Average latency of recieved V2X packets in ms", registry=self.registry)
        self.v2x_uplink_bandwidth = Histogram(
            "v2x_uplink_bandwidth", "Uplink bandwidth used to recieve V2X packets in Bps", registry=self.registry
        )
        self.v2x_downlink_bandwidth = Histogram(
            "v2x_downlink_bandwidth", "Downlink bandwidth used to send V2X packets in Bps", registry=self.registry
        )
        self.ldm_size = Histogram("ldm_size", "Size of Local Dynamic Maps in Bytes", registry=self.registry)
        self.ldm_map = Gauge(
            "ldm_map",
            "Vehicle Geolocation Data",
            ["station_id", "station_type", "detected_by", "latitude", "longitude"],
            registry=self.registry,
        )
        self.number_of_messages_sent = Gauge(
            "number_of_messages_sent", "Number of messages sent", registry=self.registry
        )
        self.number_of_messages_recieved = Gauge(
            "number_of_messages_recieved", "Number of messages recieved", registry=self.registry
        )

        start_http_server(PROMETHEUS_PORT, registry=self.registry)

    def send_number_of_messages_sent(self) -> None:
        """
        Function to send the number of messages sent to the Prometheus Gateway.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.number_of_messages_sent.inc()

    def send_number_of_messages_recieved(self) -> None:
        """
        Function to send the number of messages recieved to the Prometheus Gateway.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self.number_of_messages_recieved.inc()

    def send_ldm_map(self, station_id: str, station_type: str, detected_by: str, latitude: str, longitude: str) -> None:
        """
        Function to expose LDM Map data. It must be called once per LDM Data Object received.

        Parameters
        ----------
        station_id: str
            The ID of the station
        station_type: str
            The type of the station
        detected_by: str
            The device that detected the station
        latitude: str
            The latitude of the station
        longitude: str
            The longitude of the station

        Returns
        ----------
        None
        """
        self.ldm_map.labels(
            station_id=station_id,
            station_type=station_type,
            detected_by=detected_by,
            latitude=str(latitude),
            longitude=str(longitude),
        ).set(1)

    def send_latency(self, value: float) -> None:
        """
        Function to send the latency to the Prometheus Gateway.

        Parameters
        ----------
        value: float
            The value to send to the Prometheus Gateway

        Returns
        -------
        None
        """
        self.latency.observe(value)

    def send_v2x_uplink_bandwidth(self, value: float) -> None:
        """
        Function to send the Uplink V2X bandwidth to the Prometheus Gateway.

        Parameters
        ----------
        value: float
            The value to send to the Prometheus Gateway

        Returns
        -------
        None
        """
        self.v2x_uplink_bandwidth.observe(value)
    
    def send_v2x_downlink_bandwidth(self, value: float) -> None:
        """
        Function to send the Downlink V2X bandwidth to the Prometheus Gateway.

        Parameters
        ----------
        value: float
            The value to send to the Prometheus Gateway

        Returns
        -------
        None
        """
        self.v2x_downlink_bandwidth.observe(value)

    def send_ldm_size(self, value: float) -> None:
        """
        Function to send the LDM size to the Prometheus Gateway.

        Parameters
        ----------
        value: float
            The value to send to the Prometheus Gateway

        Returns
        -------
        None
        """
        self.ldm_size.observe(value)
