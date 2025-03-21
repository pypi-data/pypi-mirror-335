import json
from typing import List, Dict, Any


class ControlItem:
    def __init__(
        self,
        create_date: str,
        control: Dict[str, Any],
        tag: str,
        rule: Dict[str, Any],
        config_id: str,
        endpoint_type: str,
        enable: bool,
        application_id: str,
        monitor_endpoint_list: List[str]
    ):
        """
        Represents a single control configuration item.
        
        Args:
            create_date (str): The creation date in ISO format.
            control (dict): A dictionary containing control details (e.g., controlCommand and controlEndpointId).
            tag (str): A tag or name for the control config.
            rule (dict): A dictionary containing rule details (e.g., sensingItem, condition, etc.).
            config_id (str): A unique identifier for the config.
            endpoint_type (str): The endpoint type identifier.
            enable (bool): Flag to indicate if the config is enabled.
            application_id (str): The application ID.
            monitor_endpoint_list (list): A list of monitor endpoints.
        """
        self.create_date = create_date
        self.control = control
        self.tag = tag
        self.rule = rule
        self.config_id = config_id
        self.endpoint_type = endpoint_type
        self.enable = enable
        self.application_id = application_id
        self.monitor_endpoint_list = monitor_endpoint_list

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ControlItem instance to a dictionary.
        
        Returns:
            dict: A dictionary representation of the control configuration item.
        """
        return {
            "createDate": self.create_date,
            "control": self.control,
            "tag": self.tag,
            "rule": self.rule,
            "configId": self.config_id,
            "endpointType": self.endpoint_type,
            "enable": self.enable,
            "applicationId": self.application_id,
            "monitorEndpointList": self.monitor_endpoint_list,
        }

class ControlConfig:
    def __init__(self, json_payload: List[Dict[str, Any]] = None):
        """
        Initializes the ControlConfig object by converting the provided JSON payload into
        a list of ControlItem objects.
        
        Args:
            json_payload (list): A list of dictionaries containing control configuration details.
        """
        self.control_items: List[ControlItem] = []
        if json_payload is None:
            return

        for item in json_payload:
            control_item = ControlItem(
                create_date=item.get("createDate"),
                control=item.get("control", {}),
                tag=item.get("tag"),
                rule=item.get("rule", {}),
                config_id=item.get("configId"),
                endpoint_type=item.get("endpointType"),
                enable=item.get("enable"),
                application_id=item.get("applicationId"),
                monitor_endpoint_list=item.get("monitorEndpointList", []),
            )
            self.control_items.append(control_item)

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the entire ControlConfig instance to a dictionary.
        
        Returns:
            dict: A dictionary representation of the ControlConfig instance.
        """
        return {"control_items": [item.to_dict() for item in self.control_items]}

    @classmethod
    def from_file(cls, file_path: str) -> 'ControlConfig':
        """
        Alternative constructor that loads a JSON file and creates a ControlConfig instance.
        
        Args:
            file_path (str): The path to the JSON file.
        
        Returns:
            ControlConfig: An instance of ControlConfig initialized with data from the file.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)