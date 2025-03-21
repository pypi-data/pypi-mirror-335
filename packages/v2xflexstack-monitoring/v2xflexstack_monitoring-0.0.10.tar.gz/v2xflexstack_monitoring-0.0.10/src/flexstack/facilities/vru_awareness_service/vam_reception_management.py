import logging
from time import time

from .vam_coder import VAMCoder
from ...btp.service_access_point import BTPDataIndication
from ...btp.router import Router as BTPRouter
from ..ca_basic_service.cam_transmission_management import GenerationDeltaTime

from .vam_ldm_adaptation import VRUBasicServiceLDM


class VAMReceptionManagement:
    """
    This class is responsible for the vam reception management.

    Attributes
    ----------
    vam_coder : vamCoder
        vam Coder object.

    """

    def __init__(
        self,
        vam_coder: VAMCoder,
        btp_router: BTPRouter,
        vru_basic_service_ldm: VRUBasicServiceLDM = None,
    ) -> None:
        """
        Initialize the vam Reception Management.

        Parameters
        ----------
        vam_coder : vamCoder
            vam Coder object.
        btp_router : BTPRouter
            BTP Router.
        ldm_facility : LDMFacility
            LDM Facility.
        """
        self.logging = logging.getLogger("vru_basic_service")
        self.vam_coder = vam_coder
        self.btp_router = btp_router
        self.btp_router.register_indication_callback_btp(port=2018, callback=self.reception_callback)
        self.vru_basic_service_ldm = vru_basic_service_ldm
        self.metrics_callback = None

    def add_metrics_callback(self, metrics_callback) -> None:
        """
        Method created in order to add a metrics callback.

        Parameters
        ----------
        metrics_callback : Callable[]
        """
        self.metrics_callback = metrics_callback

    def reception_callback(self, btp_indication: BTPDataIndication) -> None:
        """
        Callback for the reception of a vam. Connected to LDM Facility in order to feed data.

        Parameters
        ----------
        btp_indication : BTPDataIndication
            BTP Data Indication.
        """
        vam = self.vam_coder.decode(btp_indication.data)
        if self.vru_basic_service_ldm is not None:
            self.vru_basic_service_ldm.add_provider_data_to_ldm(vam)

        if self.metrics_callback is not None:
            self.__attend_metrics_callback(vam)

        self.logging.debug("Recieved message; %s", vam)
        self.logging.info(
            "Recieved VAM message with timestamp: %s, station_id: %s",
            vam["vam"]["generationDeltaTime"],
            vam["header"]["stationId"],
        )

    def __attend_metrics_callback(self, vam: dict) -> None:
        """
        Method created in order to attend the metrics callback.

        Parameters
        ----------
        vam : dict

        Returns
        -------
        None
        """
        generation_delta_time = GenerationDeltaTime()
        current_its_time = generation_delta_time.as_timestamp_in_certain_point(time())
        latency = current_its_time - vam["vam"]["generationDeltaTime"]
        self.metrics_callback(latency)
