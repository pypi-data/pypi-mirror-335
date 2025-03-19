import json
import requests
import base64
import urllib3
import warnings

from .util import get_uppercase_extension
from .content_config import ContentConfig

# Disable https warnings if the http certificate is not valid
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)

class ContentArchive:

    def __init__(self, content_config):

        if isinstance(content_config, ContentConfig):
            self.repo_url = content_config.repo_url
            self.repo_id = content_config.repo_id
            self.logger = content_config.logger
            self.encoded_credentials = content_config.encoded_credentials
            self.authorization_repo = content_config.authorization_repo
        else:
            raise TypeError("ContentConfig class object expected")

    #--------------------------------------------------------------
    def archive_metadata(self, file_path, metadata):
        """
        Creates and sends a multipart/mixed HTTP POST request with metadata and a base64 encoded file using ArchiveMetadataBuilder.

        Args:
            file_path (str): The path to the image, pdf, etc. file.
            metadata (ArchiveMetadataBuilder): ArchiveMetadataBuilder object containing the metadata.
        """

        boundary_string = "boundaryString"

        try:           
            if isinstance(metadata, ArchiveMetadataBuilder):
                extension = get_uppercase_extension(file_path)
                metadata.set_type(extension)
            else:
                self.logger.error("The parameter is not ArchiveMetadataBuilder object.")
                raise Exception("The parameter is not ArchiveMetadataBuilder object.")

            metadata_json = metadata.to_json() # se utiliza el objeto metadata pasado como parametro
            
            try:       
                if metadata.mime_type != "text/plain":
                    # If the file is not a text file, read it in binary mode and convert it to base64
                    with open(file_path, "rb") as image_file:
                       encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
                    #--------------------------------------------------------------
                    # BODY
                    body_parts = [
                                f"--{boundary_string}",
                                "Content-Type: application/vnd.asg-mobius-archive-write-metadata.v2+json",
                                "",
                                metadata_json,
                                f"--{boundary_string}",
                                f"Content-Type: {metadata.mime_type}",
                                "Content-Transfer-Encoding: base64",
                                "",
                                encoded_image,
                                f"--{boundary_string}--",
                            ]

                    body = "\n".join(body_parts)
        
                    # END BODY
                    #--------------------------------------------------------------  
                    #                     
                else:
                      with open(file_path, 'r', encoding='utf-8') as txt_file:     
                          txt_file_contents = txt_file.read()
                      #--------------------------------------------------------------
                      # BODY
                      body_parts = [
                                    f"--{boundary_string}",
                                    "Content-Type: application/vnd.asg-mobius-archive-write-metadata.v2+json",
                                    "",
                                    metadata_json,
                                    f"--{boundary_string}",
                                    "Content-Type: text/plain; charset=utf-8",
                                    "",
                                    txt_file_contents,
                                    f"--{boundary_string}--",
                                ]

                      body = "\n".join(body_parts)
            
                      # END BODY
                      #--------------------------------------------------------------  
                                                  
            except FileNotFoundError:
                    self.logger.error(f"File not found :'{file_path}'.")
                    raise FileNotFoundError(f"File not found :'{file_path}'.")
            except Exception as e:
                    self.logger.error(f"Reading file : {e}")
                    raise Exception(f"File not found :'{file_path}'.")


            archive_write_url= self.repo_url + "/repositories/" + self.repo_id + "/documents?returnids=true"
    
            headers = {
                'Accept': 'application/vnd.asg-mobius-archive-write-status.v2+json',
                'Content-Type': f'multipart/mixed; TYPE=metadata; boundary={boundary_string}',
                 self.authorization_repo: f'Basic {self.encoded_credentials}'
                }

            self.logger.info("--------------------------------")
            self.logger.debug("Method : archive_metadata")
            self.logger.info(f"Archive Write URL : {archive_write_url}")
            self.logger.debug(f"Headers : {json.dumps(headers)}")
            self.logger.debug(f"Body : \n{body}")
                
            # Send the request
            response = requests.post(archive_write_url, headers=headers, data=body, verify=False)
            
            self.logger.debug(response.text)

            return response.status_code

        except Exception as e:
            self.logger.error(f"An error occurred: {e}")

    
    #--------------------------------------------------------------
    # Archive based on policy
    def archive_policy(self, file_path, policy_name):

        type = get_uppercase_extension(file_path)

        boundary_string = "boundaryString"
            
        metadata_json = {
                            "objects": [
                                {
                                    "policies": [f"{policy_name}"]
                                }
                            ]
                        }
        
        metadata_str =  json.dumps(metadata_json, indent=4)

        try:       
            if type == "TXT":
                    
                with open(file_path, 'r', encoding='utf-8') as txt_file:     
                    txt_file_contents = txt_file.read()

                body_parts = [
                            f"--{boundary_string}",
                            "Content-Type: application/vnd.asg-mobius-archive-write-policy.v2+json",
                            "",
                            metadata_str,
                            f"--{boundary_string}",
                            "Content-Type: archive/file",
                            "",
                            txt_file_contents,
                            "",
                            f"--{boundary_string}--",
                        ]

                body = "\n".join(body_parts)

            elif type == "PDF":
                # If the file is not a text file, read it in binary mode and convert it to base64
                with open(file_path, "rb") as image_file:
                    encoded_image = base64.b64encode(image_file.read()).decode("utf-8")

                body_parts = [
                            f"--{boundary_string}",
                            "Content-Type: application/vnd.asg-mobius-archive-write-policy.v2+json",
                            "",
                            metadata_str,
                            f"--{boundary_string}",
                            "Content-Type: application/pdf",
                            "Content-Transfer-Encoding: base64",
                            "",
                            encoded_image,
                            "",
                            f"--{boundary_string}--",
                        ]

                body = "\n".join(body_parts)

            else:
                self.logger.error(f"File extension not valid :'{file_path}'. Only PDF, and TXT allowed") 
                raise ValueError(f"File extension not valid :'{file_path}'. Only PDF, and TXT allowed")    
                                                    
        except FileNotFoundError:
                self.logger.error(f"File not found :'{file_path}'.")
                raise FileNotFoundError(f"File not found :'{file_path}'.")
        except Exception as e:
                self.logger.error(f"Reading file : {e}")
                raise ValueError(f"Reading file : {e}")

        archive_write_url= self.repo_url + "/repositories/" + self.repo_id + "/documents?returnids=true"

        headers = {
            'Accept': 'application/vnd.asg-mobius-archive-write-status.v2+json',
            'Content-Type': f'multipart/mixed; TYPE=policy; boundary={boundary_string}',
                self.authorization_repo: f'Basic {self.encoded_credentials}'
            }

        self.logger.info("--------------------------------")
        self.logger.debug("Method : archive_policy")
        self.logger.info(f"Archive Write URL : {archive_write_url}")
        self.logger.debug(f"Headers : {json.dumps(headers)}")
        self.logger.debug(f"Body : \n{body}")
            
        # Send the request
        response = requests.post(archive_write_url, headers=headers, data=body, verify=False)
        
        self.logger.debug(response.text)

        return response.status_code

class ArchiveMetadataBuilder:
    def __init__(self, document_class_id="LISTFILE", type="PDF"):
        """
        Inicializa el MetadataBuilder con documentClassId y tipo (por defecto PNG).
        """
        self.document_class_id = document_class_id
        self.type = type
        self.metadata = []
        self.section_set = False  # Track if SECTION has been set

        if self.type == "PNG":
            self.mime_type = "image/png"
        elif self.type == "PDF":
            self.mime_type = "application/pdf"
        elif self.type == "JPG":
            self.mime_type = "image/jpeg"
        elif self.type == "TXT":
            self.mime_type = "text/plain"    
        else:
            raise ValueError("Unsupported type. Supported types are PNG, PDF, and JPG.")

    def set_type(self, file_extension):
        """
        Sets and validate file type with file extension
        """
        self.type = file_extension

        if self.type == "PNG":
            self.mime_type = "image/png"
        elif self.type == "PDF":
            self.mime_type = "application/pdf"
        elif self.type == "JPG":
            self.mime_type = "image/jpeg"
        elif self.type == "TXT":
            self.mime_type = "text/plain"    
        else:
            raise ValueError("Unsupported file extension. Supported types are: .")

    def set_section(self, section_value):
        """
        Establece o actualiza el valor de la sección.
        """
        section_value = section_value[:20]
        for item in self.metadata:
            if item.get("name") == "SECTION":
                item["value"] = section_value
                self.section_set = True
                return
        # If SECTION doesn't exist, add it
        self.metadata.append({"name": "SECTION", "value": section_value})
        self.section_set = True

    def add(self, name, value):
        """
        Adds a new name-value pair to the metadata, only if the name does not already exist.
        """
        if name == "SECTION":
            self.set_section(value)  # Use set_section for "SECTION"
        else:
            # Check if the name already exists in the metadata list
            if not any(item["name"] == name for item in self.metadata):
                self.metadata.append({"name": name, "value": value})
            else:
                raise ValueError(f"The index name '{name}' already exists in the metadata.")

    def to_dict(self):
        """
        Convierte la instancia de la clase a un diccionario serializable.
        """
        if not self.section_set:
            raise ValueError("SECTION must be set before generating JSON.")

        return {
            "objects": [
                {
                    "documentClassId": self.document_class_id,
                    "type": self.type,
                    "metadata": self.metadata,
                }
            ]
        }

    def to_json(self, indent=4):
        """
        Devuelve el JSON de metadatos construido con doble comillas.
        """
        return json.dumps(self.to_dict(), indent=indent)