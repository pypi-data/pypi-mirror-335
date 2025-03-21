from time import time
import logging

from ..facilities.local_dynamic_map.ldm_facility import LDMFacility
from ..facilities.local_dynamic_map.ldm_classes import (
    SubscribeDataObjectsResp,
    SubscribeDataobjectsReq,
    RequestDataObjectsResp,
    RegisterDataConsumerReq,
    RegisterDataConsumerResp,
)
from ..facilities.local_dynamic_map.ldm_constants import SPATEM, CAM, VAM, DENM

from ..utils.static_location_service import ThreadStaticLocationService as Location

from .prometheus_adaptation import PrometheusClientPull


class MetricsExposer:
    def __init__(self, its_station_name: str, ldm: LDMFacility, location: Location) -> None:
        """
        Initialization class for MetricsExposer
        """
        self.logging = logging.getLogger("metrics")

        self.its_station_name = its_station_name
        self.ldm = ldm
        self.monitored_its_stations = []
        self.prometheus = PrometheusClientPull()
        self.__register_to_ldm(ldm, location)
        self.__subscribe_to_ldm(ldm)

        self.logging.info("Metrics Exposer initialized!")

    def btp_level_callback(self, args) -> None:
        """
        Callback function for the BTP level. This function will be called when the BTP recieves or sends a message.
        It will be used to send BTP-specific metrics to the Prometheus Gateway.

        Parameters
        ----------
        args : Any
            Arguments passed to the callback function.

        Returns
        -------
        None
        """
        pass

    def gn_level_callback(self, recieved_bytes: int = 0, send_bytes: int = 0) -> None:
        """
        Callback function for the Geonet level. This function will be called when the Geonet recieves or
        sends a message. It will be used to send Geonet-specific metrics to the Prometheus Gateway.

        Parameters
        ----------
        recievied_bytes : int
            Number of bytes recieved by the Geonet.
        send_bytes : int
            Number of bytes sent by the Geonet.

        Returns
        -------
        None
        """
        self.logging.debug(
            f"Monitoring V2X Bandwidth metrics from the GN-level. Recieved Bytes: {recieved_bytes}, Send Bytes: {send_bytes}"
        )

        if recieved_bytes > 0:
            self.prometheus.send_v2x_uplink_bandwidth(recieved_bytes)
        if send_bytes > 0:
            self.prometheus.send_v2x_downlink_bandwidth(send_bytes)

    def ldm_callback(self, ldm_size: int, oldest_message: int = 0) -> None:
        """
        Callback function for the LDM. This function will be called when the LDM recieves or sends a message.
        It will be used to send LDM-specific metrics to the Prometheus Gateway.

        Parameters
        ----------
        ldm_size : int
            Size of the Local Dynamic Map in bytes.
        oldest_message : int
            Time of the oldest message in the LDM.

        Returns
        -------
        None
        """
        self.logging.debug(f"Monitoring LDM size metrics from the LDM. Size: {ldm_size}")

        self.prometheus.send_ldm_size(ldm_size)

    def facility_level_callback(self, latency: int) -> None:
        """
        Callback function for the Facilities level. This function will be called when the Facilities recieves or
        sends a message. It will be used to send Facilities-specific metrics to the Prometheus Gateway.

        Parameters
        ----------
        latency : int
            Latency calculated by the Facilities.

        Returns
        -------
        None
        """
        self.logging.debug("Monitoring latency metrics from the Facilities level")

        self.prometheus.send_latency(latency)
        self.prometheus.send_number_of_messages_recieved()

    def application_level_callback(self, data: bytes) -> None:
        """
        Callback function for the Application level. This function will be called when the Application recieves or
        sends a message. It will be used to send Application-specific metrics to the Prometheus Gateway.

        Parameters
        ----------
        data : bytes
            Data recieved by the Application.

        Returns
        -------
        None
        """
        pass

    def __register_to_ldm(self, ldm: LDMFacility, location: Location) -> None:
        """
        Register to the Local Data Manager (LDM) facility for sending the data.

        Parameters
        ----------
        ldm : LDMFacility
            Local Data Manager (LDM) facility object.

        Returns
        -------
        None
        """
        register_data_consumer_reponse: RegisterDataConsumerResp = ldm.if_ldm_4.register_data_consumer(
            RegisterDataConsumerReq(
                application_id=SPATEM,  # TODO: Allow application to sign up!!
                access_permisions=[VAM, CAM],
                area_of_interest=location,
            )
        )
        if register_data_consumer_reponse.result == 2:
            raise Exception(f"Failed to register data consumer: {str(register_data_consumer_reponse)}")
        self.logging.debug(f"Registered to LDM with response: {str(register_data_consumer_reponse)}")

    def __handle_cam_data_object(self, data_object: dict) -> None:
        """
        Handle the CAM data object received from the Local Data Manager (LDM).

        Parameters
        ----------
        data_object : DataObject
            Data object received from the LDM.

        Returns
        -------
        None
        """
        station_id = data_object["dataObject"]["header"]["stationId"]
        if station_id in self.monitored_its_stations:
            return
        self.monitored_its_stations.append(station_id)
        self.prometheus.send_ldm_map(
            data_object["dataObject"]["header"]["stationId"],
            data_object["dataObject"]["cam"]["camParameters"]["basicContainer"]["stationType"],
            self.its_station_name,
            data_object["dataObject"]["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"]
            / 10000000,
            data_object["dataObject"]["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"]
            / 10000000,
        )

        self.logging.debug(
            "Sending CAM latency and LDM map data to Prometheus, with LDM map, "
            + f"lat: {data_object['cam']['camParameters']['basicContainer']['referencePosition']['latitude'] / 10000000}, "
            + f"lon: {data_object['cam']['camParameters']['basicContainer']['referencePosition']['longitude'] / 10000000}"
        )

    def __handle_vam_data_object(self, data_object: dict) -> None:
        """
        Handle the VAM data object received from the Local Data Manager (LDM).

        Parameters
        ----------
        data_object : DataObject
            Data object received from the LDM.

        Returns
        -------
        None
        """
        station_id = data_object["dataObject"]["header"]["stationId"]
        if station_id in self.monitored_its_stations:
            return
        self.monitored_its_stations.append(station_id)
        self.prometheus.send_ldm_map(
            station_id,
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["stationType"],
            self.its_station_name,
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["referencePosition"]["latitude"]
            / 10000000,
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["referencePosition"]["longitude"]
            / 10000000,
        )

        self.logging.debug(
            "Sending VAM latency and LDM map data to Prometheus, with LDM map, "
            + f"lat: {data_object['dataObject']['vam']['vamParameters']['basicContainer']['referencePosition']['latitude'] / 10000000}, "
            + f"lon: {data_object['dataObject']['vam']['vamParameters']['basicContainer']['referencePosition']['longitude'] / 10000000}"
        )

    def __handle_data_object(self, data_object: dict) -> None:
        """
        Handle the data object received from the Local Data Manager (LDM).

        Parameters
        ----------
        data_object : DataObject
            Data object received from the LDM.

        Returns
        -------
        None
        """
        self.monitored_its_stations = []
        if data_object["application_id"] == CAM:
            self.__handle_cam_data_object(data_object)
        elif data_object["application_id"] == VAM:
            self.__handle_vam_data_object(data_object)
        else:
            print(f"Unknown data object type: {data_object.data_object}")

    def __ldm_subscription_callback(self, data_object: RequestDataObjectsResp) -> None:
        """
        Callback function for receiving the data objects from the Local Data Manager (LDM).

        Parameters
        ----------
        data_object : DataObject
            Data object received from the LDM.

        Returns
        -------
        None
        """
        if data_object.application_id == SPATEM:
            for data in data_object.data_objects:
                self.__handle_data_object(data)
        else:
            raise Exception(f"Unknown data object type: {data_object.data_object_type}")

    def __subscribe_to_ldm(self, ldm: LDMFacility) -> None:
        """
        Subscribe to the Local Data Manager (LDM) facility for receiving the data.

        Parameters
        ----------
        ldm : LDMFacility
            Local Data Manager (LDM) facility object.

        Returns
        -------
        None
        """
        subscribe_data_consumer_response: SubscribeDataObjectsResp = ldm.if_ldm_4.subscribe_data_consumer(
            SubscribeDataobjectsReq(
                application_id=SPATEM,
                data_object_type=[CAM, VAM, DENM],
                priority=None,
                filter=None,
                notify_time=1,
                multiplicity=None,
                order=None,
            ),
            self.__ldm_subscription_callback,
        )
        if subscribe_data_consumer_response.result.result != 0:
            raise Exception(f"Failed to subscribe to data objects: {str(subscribe_data_consumer_response.result)}")

        self.logging.debug(f"Subscribed to LDM with response: {str(subscribe_data_consumer_response)}")
