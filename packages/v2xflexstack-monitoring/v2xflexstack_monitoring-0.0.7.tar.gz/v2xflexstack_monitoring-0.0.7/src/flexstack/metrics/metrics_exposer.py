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
from ..facilities.ca_basic_service.cam_transmission_management import GenerationDeltaTime

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
        self.generation_delta_time = GenerationDeltaTime()
        self.prometheus = PrometheusClientPull()
        self.__register_to_ldm(ldm, location)
        self.__subscribe_to_ldm(ldm)

        self.logging.info("Metrics Exposer initialized!")

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

    def __current_its_time(self) -> float:
        """
        Get the current ITS time.

        Returns
        -------
        float
            Current ITS time.
        """
        self.generation_delta_time.set_in_normal_timestamp(time() * 1000)
        return self.generation_delta_time.msec

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
        latency = self.__current_its_time() - data_object["timeStamp"]
        self.prometheus.send_latency(latency)
        self.prometheus.send_ldm_map(
            data_object["header"]["stationId"],
            data_object["cam"]["camParameters"]["basicContainer"]["stationType"],
            self.its_station_name,
            data_object["cam"]["camParameters"]["basicContainer"]["referencePosition"]["latitude"] / 10000000,
            data_object["cam"]["camParameters"]["basicContainer"]["referencePosition"]["longitude"] / 10000000,
        )
        self.logging.debug(
            f"Sending CAM latency and LDM map data to Prometheus, with values latency: {latency}, LDM map, "
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
        latency = self.__current_its_time() - data_object["timeStamp"]
        self.prometheus.send_latency(latency)
        self.prometheus.send_ldm_map(
            data_object["dataObject"]["header"]["stationId"],
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["stationType"],
            self.its_station_name,
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["referencePosition"]["latitude"]
            / 10000000,
            data_object["dataObject"]["vam"]["vamParameters"]["basicContainer"]["referencePosition"]["longitude"]
            / 10000000,
        )

        self.logging.debug(
            f"Sending VAM latency and LDM map data to Prometheus, with values latency: {latency}, LDM map, "
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
                notify_time=0.5,
                multiplicity=None,
                order=None,
            ),
            self.__ldm_subscription_callback,
        )
        if subscribe_data_consumer_response.result.result != 0:
            raise Exception(f"Failed to subscribe to data objects: {str(subscribe_data_consumer_response.result)}")

        self.logging.debug(f"Subscribed to LDM with response: {str(subscribe_data_consumer_response)}")
