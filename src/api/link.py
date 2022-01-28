def create(local_host: str,
           remote_host: str,
           local_interface: str,
           remote_interface: str,
           local_trigger: str,
           remote_trigger: str) -> dict:

    return {
        "selementid1": local_host,
        "selementid2": remote_host,
        "label": "{} - {}".format(local_interface, remote_interface),
        "linktriggers": [
            {
                "triggerid": local_trigger,
                "color": "DD0000"
            },
            {
                "triggerid": remote_trigger,
                "color": "DD0000"
            }
        ],
        "color": "00CC00"
    }