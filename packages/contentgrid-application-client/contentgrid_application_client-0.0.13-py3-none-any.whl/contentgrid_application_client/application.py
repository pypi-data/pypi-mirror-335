from typing import List, Optional, Self, Sequence, cast
import requests
import os
import logging
import mimetypes

from contentgrid_hal_client.exceptions import BadRequest, IncorrectAttributeType, MissingRequiredAttribute, NotFound
from contentgrid_hal_client.hal import CurieRegistry, HALFormsClient, HALLink, HALResponse, InteractiveHALResponse
from contentgrid_hal_client.security import ApplicationAuthenticationManager
from datetime import datetime
from email.header import decode_header

logging.basicConfig(level=logging.DEBUG)

hal_form_type_check = {
    "text" : (lambda value : isinstance(value, str)),
    "datetime" : (lambda value : is_valid_date_format(value)),
    "checkbox" : (lambda value : isinstance(value, bool)),
    "number" : (lambda value : isinstance(value, (int, float))),
    "url" : (lambda value : value.startswith("http://") or value.startswith("https://"))
}

def is_valid_date_format(date_string):
    try:
        datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")
        return True
    except ValueError:
        return False

hal_form_types = {
    "text" : "string",
    "datetime" : "date (e.g.:2024-03-20T16:48:59.904Z)",
    "checkbox" : "boolean",
    "number" : "int/float",
    "url" : "url"
}

class InteractiveApplicationResponse(InteractiveHALResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        assert isinstance(client, ContentGridApplicationClient)
        super().__init__(data, client, curie_registry)
        self.client : ContentGridApplicationClient = client

class EntityCollection(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.page_info: Optional[PageInfo] = None
        if "page" in data.keys():
            self.page_info = PageInfo(
                size=data["page"]["size"],
                number=data["page"]["number"],
                total_elements=data["page"].get("totalElements", None),
                total_pages=data["page"].get("totalPages", None),
                total_items_exact=data["page"].get("total_items_exact", None),
                total_items_estimate=data["page"].get("total_items_estimate", None),
            )

    def get_entities(self) -> Optional[List["EntityObject"]]:
        return self.get_embedded_objects_by_key("item", infer_type=EntityObject)

    def get_entity_profile_link(self) -> HALLink:
        return cast(HALLink, self.get_link("profile"))

    def create_entity(self, attributes : dict, attribute_validation=True) -> "EntityObject":
        self.client._transform_hal_links_to_uris(attributes=attributes)
        if attribute_validation:
            entity_profile = self.client.follow_link(self.get_entity_profile_link(), infer_type=EntityProfile)
            self.client._validate_params(entity_profile.templates["create-form"], attributes=attributes)
        response = self.client.post(self.get_self_link().uri, json=attributes, headers={"Content-Type" : "application/json"})
        data = self.client._validate_json_response(response)
        return EntityObject(data=data, client=self.client)

    def first(self):
        if not self.has_link("first"):
            raise Exception(f"Collection {self.get_self_link()} has no first page")
        self.__init__(data=self.client.follow_link(self.get_link("first"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def last(self):
        if not self.has_link("last"):
            raise Exception(f"Collection {self.get_self_link()} has no last page")
        self.__init__(data=self.client.follow_link(self.get_link("last"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def next(self):
        if not self.has_link("next"):
            raise Exception(f"Collection {self.get_self_link()} has no next page")
        self.__init__(data=self.client.follow_link(self.get_link("next"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)

    def prev(self):
        if not self.has_link("prev"):
            raise Exception(f"Collection {self.get_self_link()} has no prev page")
        self.__init__(data=self.client.follow_link(self.get_link("prev"), infer_type=EntityCollection).data, client=self.client, curie_registry=self.curie_registry)


class EntityObject(InteractiveApplicationResponse):
    def __init__(self, data: dict, client: "ContentGridApplicationClient", curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)
        self.id = data["id"]

    def get_content_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/content")

    def get_relation_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/relation")

    def get_relation_link(self, relation_name: str) -> HALLink:
        relation_links = self.get_relation_links()
        for relation_link in relation_links:
            if relation_link.name == relation_name:
                return relation_link
        # If relation not found, raise exception.
        raise NotFound(f"Relation {relation_name} not found on entity {self.get_self_link().uri}")

    def get_relation_collection(self, relation_name : str, page: int = 0, size: int = 20, params: dict = {}):
        params = self.client._add_page_and_size_to_params(page=page, size=size, params=params)
        relation_link = self.get_relation_link(relation_name=relation_name)
        return self.client.follow_link(relation_link, infer_type=EntityCollection, params=params)

    def put_relation(self, relation_name: str, related_entity_links : List[str | HALLink | Self]) -> None:
        relation_link = self.get_relation_link(relation_name=relation_name)
        relation_payload = self._create_text_uri_list_payload(links=related_entity_links)
        response = self.client.put(relation_link.uri, headers={"Accept" : "*/*", "Content-Type" : "text/uri-list"}, data=relation_payload)
        self.client._validate_non_json_response(response)

    def post_relation(self, relation_name: str, related_entity_links : List[str | HALLink | Self]) -> None:
        relation_link = self.get_relation_link(relation_name=relation_name)
        relation_payload = self._create_text_uri_list_payload(links=related_entity_links)
        response = self.client.post(relation_link.uri, headers={"Accept" : "*/*", "Content-Type" : "text/uri-list"}, data=relation_payload)
        self.client._validate_non_json_response(response)

    def put_data(self, data: dict, attribute_validation=True) -> None:
        self.client._transform_hal_links_to_uris(attributes=data)
        if attribute_validation:
            self.client._validate_params(self.get_template("default"), attributes=data)
        return super().put_data(data)

    def patch_data(self, data : dict, attribute_validation=True ) -> None:
        self.client._transform_hal_links_to_uris(attributes=data)
        if attribute_validation:
            self.client._validate_params(self.get_template("default"), attributes=data)
        return super().patch_data(data)

    def put_content_attribute(self, content_attribute_name : str, filepath : str) -> HALLink:
        content_links = self.get_content_links()
        if len(content_links) > 0:
            for content_link in content_links:
                if content_link.name == content_attribute_name:
                    return self.client.put_on_content_link(content_link=content_link, filepath=filepath)
        raise NotFound(f"Content Attribute {content_attribute_name} not found on entity {self.get_self_link().uri}")

    def fetch_content_attribute_by_name(self, content_attribute_name : str) -> tuple[str, bytes]:
        content_links = self.get_content_links()
        if len(content_links) > 0:
            for content_link in content_links:
                if content_link.name == content_attribute_name:
                    return self.client.fetch_content_attribute(content_link=content_link)
        raise NotFound(f"Content Attribute {content_attribute_name} not found on entity {self.get_self_link().uri}")

    def fetch_all_content_attributes(self) -> List[tuple[str, bytes]]:
        files = []
        for hal_content_link in self.get_content_links():
            if self.metadata[hal_content_link.name] is not None:
                files.append(self.client.fetch_content_attribute(hal_content_link))
        return files

    def _create_text_uri_list_payload(self, links : Sequence[str | HALLink | HALResponse]) -> str:
        uri_list = []
        for link in links:
            if isinstance(link, HALLink):
                uri_list.append(link.uri)
            elif isinstance(link, HALResponse):
                uri_list.append(link.get_self_link().uri)
            elif isinstance(link, str):
                uri_list.append(link)
            else:
                raise BadRequest(f"Incorrect Link type {type(link)} in uri list payload, allowed types: HALLink, HALResponse or str")
        return "\n".join(uri_list)

class Profile(InteractiveHALResponse):
    def __init__(self, data: dict, client: HALFormsClient, curie_registry: CurieRegistry = None) -> None:
        super().__init__(data, client, curie_registry)

    def get_entity_links(self) -> List[HALLink]:
        return self.get_links("https://contentgrid.cloud/rels/contentgrid/entity")

    def get_entity_profile(self, pluralized_entity_name: str) -> "EntityProfile": # type: ignore
        pluralized_entity_names = [entityprofile.name for entityprofile in self.get_entity_links()]
        if pluralized_entity_name in pluralized_entity_names:
            for entity_profile_link in self.get_entity_links():
                if entity_profile_link.name == pluralized_entity_name:
                    return self.client.follow_link(entity_profile_link, infer_type=EntityProfile)
        else:
            raise NotFound(f"Entity {pluralized_entity_name} does not exist.")

class RelationProfile(InteractiveApplicationResponse):
    def __init__(self, data : dict, client : "ContentGridApplicationClient", curie_registry : CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name = data["name"]
        self.title = data.get("title", self.name)
        self.description = data.get("description", "")
        self.required = data["required"]
        self.many_source_per_target = data["many_source_per_target"]
        self.many_target_per_source = data["many_target_per_source"]

    def get_related_entity_profile(self) -> "EntityProfile":
        return self.client.follow_link(self.get_link("https://contentgrid.cloud/rels/blueprint/target-entity"), infer_type=EntityProfile)

class SearchParameter(InteractiveApplicationResponse):
    def __init__(self, data : dict, client : "ContentGridApplicationClient", curie_registry : CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]
        self.title: str = data.get("title", self.name)
        self.type: str = data["type"]

class AttributeConstraint(InteractiveApplicationResponse):
    def __init__(self, data : dict, client : "ContentGridApplicationClient", curie_registry : CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.type: str = data["type"]
        self.values: List[str] = data.get("values", [])

class AttributeProfile(InteractiveApplicationResponse):
    def __init__(self, data : dict, client : "ContentGridApplicationClient", curie_registry : CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]
        self.title: str = data.get("title", self.name)
        self.type: str = data["type"]
        self.description: str = data["description"]
        self.read_only: bool = data["readOnly"]
        self.required: bool = data["required"]

        # Using get_embedded_objects_by_key for all embedded objects
        self.nested_attributes : List[AttributeProfile] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/attribute", infer_type=AttributeProfile)
        self.search_params : List[SearchParameter] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/search-param", infer_type=SearchParameter)
        self.constraints : List[AttributeConstraint] = self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/constraint", infer_type=AttributeConstraint)

    def get_nested_attributes(self) -> List["AttributeProfile"]:
        return self.nested_attributes

    def is_content_attribute(self) -> bool:
        return self.type == "object" and any(
            attr.name in ["length", "mimetype", "filename"]
            for attr in self.nested_attributes
        )

    def get_search_parameters(self) -> List[SearchParameter]:
        return self.search_params

    def get_constraints(self) -> List[AttributeConstraint]:
        return self.constraints

    def get_constraint(self, constraint_type: str) -> Optional[AttributeConstraint]:
        for constraint in self.constraints:
            if constraint.type == constraint_type:
                return constraint
        return None

    def has_required_constraint(self) -> bool:
        return self.get_constraint("required") is not None

    def has_constrained_values(self) -> bool:
        return self.get_constraint("allowed-values") is not None

    def get_allowed_values(self) -> Optional[List[str]]:
        if self.has_constrained_values():
            return self.get_constraint("allowed-values").values # type: ignore
        return None

    def has_search_capability(self) -> bool:
        return len(self.search_params) > 0

    def get_nested_attribute_by_name(self, name: str) -> Optional["AttributeProfile"]:
        for attr in self.nested_attributes:
            if attr.name == name:
                return attr
        return None

class EntityProfile(InteractiveApplicationResponse):
    def __init__(self, data : dict, client : "ContentGridApplicationClient", curie_registry : CurieRegistry = None):
        super().__init__(data, client, curie_registry)
        self.name: str = data["name"]
        self.title: str = data.get("title", self.name)
        self.description : str = data.get("description", "")

    def get_attribute_profiles(self) -> List[AttributeProfile]:
        return self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/attribute", infer_type=AttributeProfile)

    def get_attribute_profile(self, attribute_name: str) -> Optional[AttributeProfile]:
        attribute_profiles = self.get_attribute_profiles()
        for attribute_profile in attribute_profiles:
            if attribute_profile.name == attribute_name:
                return attribute_profile
        raise ValueError(f"Attribute {attribute_name} not found in entity {self.name}")

    def get_relation_profiles(self) -> List[RelationProfile]:
        return self.get_embedded_objects_by_key("https://contentgrid.cloud/rels/blueprint/relation", infer_type=RelationProfile)

    def get_relation_profile(self, relation_name: str) -> Optional[RelationProfile]:
        relation_profiles = self.get_relation_profiles()
        for relation_profile in relation_profiles:
            if relation_profile.name == relation_name:
                return relation_profile
        raise ValueError(f"Relation {relation_name} not found in entity {self.name}")

class PageInfo:
    def __init__(self, size : int, total_elements : int, total_pages : int, number : int, total_items_exact: int, total_items_estimate: int) -> None:
        self.size : int = size
        self.number : int = number

        self.total_elements : Optional[int] = total_elements
        self.total_pages : Optional[int] = total_pages
        self.total_items_exact : Optional[int] = total_items_exact
        self.total_items_estimate : Optional[int] = total_items_estimate

class ContentGridApplicationClient(HALFormsClient):
    def __init__(self,
        client_endpoint: str,
        auth_uri: str = None,
        auth_manager: ApplicationAuthenticationManager = None,
        client_id: str = None,
        client_secret: str = None,
        token: str = None,
        attribute_validation : bool = True,
        session_cookie: str = None,
        pool_maxsize : int = 10,
    ) -> None:
        logging.info("Initializing ContentGridApplicationClient...")
        super().__init__(client_endpoint=client_endpoint, auth_uri=auth_uri, auth_manager=auth_manager, client_id=client_id, client_secret=client_secret, token=token, session_cookie=session_cookie, pool_maxsize=pool_maxsize)
        self.attribute_validation = attribute_validation

    def get_profile(self) -> Profile:
        response = self.get("/profile", headers={"Accept": "application/json"})
        data = self._validate_json_response(response)
        return Profile(data, client=self)

    def get_entity_profile(self, pluralized_entity_name : str) -> EntityProfile:
        return self.get_profile().get_entity_profile(pluralized_entity_name=pluralized_entity_name)

    def fetch_openapi_yaml(self) -> tuple[str, bytes]:
        res = self.get("/openapi.yml")
        self._validate_non_json_response(res)
        return ("openapi.yml", res.content)

    def get_entity_collection(self, plural_entity_name: str, page: int = 0, size: int = 20, params: dict = {}) -> EntityCollection:
        params = self._add_page_and_size_to_params(page=page, size=size, params=params)
        response = self.get(plural_entity_name, params=params)
        data = self._validate_json_response(response)
        return EntityCollection(data, client=self)

    def create_entity(self, pluralized_entity_name: str, attributes:dict) -> EntityObject:
        return self.get_entity_collection(plural_entity_name=pluralized_entity_name).create_entity(attributes=attributes, attribute_validation=self.attribute_validation)

    def get_entity_instance(self, entity_link: HALLink | EntityObject) -> EntityObject:
        if isinstance(entity_link, EntityObject):
            return self.follow_link(entity_link.get_self_link(), infer_type=EntityObject)
        elif isinstance(entity_link, HALLink):
            return self.follow_link(entity_link, infer_type=EntityObject)
        else:
            raise BadRequest(f"entity_link should be of type EntityObject or HALLink. was type {type(entity_link)}")

    def get_entity_relation_collection(self, entity_link: HALLink, relation_name : str, page: int = 0, size: int = 20, params: dict = {}) -> EntityCollection:
        return self.get_entity_instance(entity_link=entity_link).get_relation_collection(relation_name=relation_name, page=page, size=size, params=params)

    def put_entity_relation(self, entity_link: HALLink, relation_name: str, related_entity_links : List[str | HALLink | EntityObject]) -> None:
        return self.get_entity_instance(entity_link=entity_link).put_relation(relation_name=relation_name, related_entity_links=related_entity_links)

    def post_entity_relation(self, entity_link: HALLink, relation_name: str, related_entity_links : List[str | HALLink | EntityObject]) -> None:
        return self.get_entity_instance(entity_link=entity_link).post_relation(relation_name=relation_name, related_entity_links=related_entity_links)

    def put_entity_attributes(self, entity_link: HALLink, attributes: dict) -> EntityObject:
        entity = self.get_entity_instance(entity_link=entity_link)
        entity.put_data(data=attributes, attribute_validation=self.attribute_validation)
        return entity

    def patch_entity_attributes(self, entity_link: HALLink, attributes: dict) -> EntityObject:
        entity = self.get_entity_instance(entity_link=entity_link)
        entity.patch_data(data=attributes, attribute_validation=self.attribute_validation)
        return entity

    def put_content_attribute(self, entity_link: HALLink, content_attribute_name : str, filepath : str) -> HALLink:
        return self.get_entity_instance(entity_link=entity_link).put_content_attribute(content_attribute_name=content_attribute_name, filepath=filepath)

    def put_on_content_link(self, content_link:HALLink, filepath: str) -> HALLink:
        if os.path.exists(filepath):
            filename = filepath.split('/')[-1]
            files = {'file': (filename, open(filepath, 'rb'), mimetypes.guess_type(filepath)[0])}
        else:
            raise BadRequest(f"Provided content not found {filepath}")
        response = self.put(content_link.uri, files=files) # type: ignore
        self._validate_non_json_response(response=response)
        return content_link

    def fetch_content_attribute(self, content_link : HALLink) -> tuple[str, bytes]:
        response = self.get(content_link.uri, headers={"Accept" : "*/*"})
        self._validate_non_json_response(response=response)
        content_disposition = response.headers.get('content-disposition')

        if content_disposition and content_disposition != "attachment":
            filename = decode_header(content_disposition)[1][0].decode("utf-8")
        else:
            # If content-disposition header is not present, try to extract filename from URL
            filename = os.path.basename(content_link.name) # type: ignore
        return (filename, response.content)

    def fetch_all_content_attributes_from_entity_link(self, entity_link: HALLink) -> List[tuple[str, bytes]]:
        return self.get_entity_instance(entity_link=entity_link).fetch_all_content_attributes()

    def delete_link(self, link: HALLink) -> requests.Response:
        response = self.delete(link.uri)
        self._validate_non_json_response(response)
        return response

    def _validate_params(self, create_form : dict, attributes : dict, check_requirements : bool = True) -> None:
        # Type checking
        for attribute, value in attributes.items():
            attribute_specs = list(filter(lambda spec : spec["name"] == attribute, create_form["properties"]))
            if len(attribute_specs) == 1:
                attribute_spec = attribute_specs[0]
                multi_valued = False
                if attribute_spec.get("options"):
                    if "minItems" in attribute_spec["options"].keys() and attribute_spec["options"]["minItems"] == 0:
                        if "maxItems" in attribute_spec["options"].keys() and attribute_spec["options"]["maxItems"] == 1:
                            multi_valued = False
                        else:
                            multi_valued = True
                if multi_valued:
                    if isinstance(value, list):
                        for v in value:
                            if not hal_form_type_check[attribute_spec["type"]](v):
                                raise IncorrectAttributeType(f"Attribute {attribute} has an incorrect type {type(value)} in its list value. {v} is not of type {hal_form_types[attribute_spec['type']]}")
                    else:
                        raise IncorrectAttributeType(f"Attribute {attribute} has an incorrect type {type(value)}. Should be of type list")
                else:
                    if not hal_form_type_check[attribute_spec["type"]](value):
                        raise IncorrectAttributeType(f"Attribute {attribute} has an incorrect type {type(value)}. Should be of type {hal_form_types[attribute_spec['type']]}")
            else:
                logging.warning(f"Attribute {attribute} does not in exist in the entity hal forms specification")
                #raise NonExistantAttribute(f"Attribute {attribute} does not in exist in the entity specification")

        if check_requirements:
            # Check for required properties is not needed when patching an entity
            for attribute_spec in create_form["properties"]:
                if attribute_spec.get("required"):
                    if attribute_spec["name"] not in attributes.keys():
                        raise MissingRequiredAttribute(f"Required attribute {attribute_spec['name']} not present in payload.")

