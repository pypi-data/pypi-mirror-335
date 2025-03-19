from enum import Enum
import json
import time
import random
import uuid
from fastapi import Request
from neoaria.commons import CommonBusiness, BusinessParameter
from neoaria.models.rms import ElementStatus, DeployStatus, gen_v1_cid, gen_v2_cid
from typing import Dict, Optional
from pydantic import BaseModel, Field
from pymongo import ReturnDocument
import requests
import yaml

class EventOperation(Enum):
    CREATE = "CREATE"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    CHANGE = "CHANGE"
    DEPLOY = "DEPLOY"

class SearchEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = Field(default_factory=lambda: int(time.time()))
    operation: EventOperation
    application: str = ""
    core: str = ""
    targetDocument: Dict
    payload: Optional[Dict] = None
    config_yaml: Dict = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def create(cls, operation: EventOperation, core: str, targetDocument: dict):
        instance = cls(operation=operation, core=core, targetDocument=targetDocument)
        instance.__load_config_yaml__()
        instance.application = instance.config_yaml['service']['name']
        return instance

    def __load_config_yaml__(self):
        with open('config/source.yaml', 'r') as file:
            self.config_yaml = yaml.safe_load(file)

    def set_payload(self, payload: dict):
        self.payload = payload

class MetaEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: int = Field(default_factory=lambda: int(time.time() * 1000))
    operation: EventOperation
    application: str = ""
    core: str = ""
    cid: str
    payload: Optional[Dict] = None
    config_yaml: Dict = Field(default_factory=dict)

    @classmethod
    def create(cls, operation: EventOperation, cid: str, core: str):
        instance = cls(operation=operation, cid = cid, core=core)
        instance.__load_config_yaml__()
        instance.application = instance.config_yaml['service']['name']
        return instance
    
    def __load_config_yaml__(self):
        with open('config/source.yaml', 'r') as file:
            self.config_yaml = yaml.safe_load(file)

class ProcessBusiness(CommonBusiness):
    """
    컨텐츠 모델의 프로세스 관련 공통 기능을 제공하는 추상 클래스.
    각 컨텐츠 모델별 비즈니스 클래스는 이 클래스를 상속받아 모델별 구현을 제공합니다.
    """
    
    def __init__(self, config):
        super().__init__(config)
        self.service_id = config.config_yaml['service']['id']
        self.service_name = config.config_yaml['service']['name']
        
        # 하위 클래스에서 설정해야 하는 속성들
        self.contents_collection = None   # 모델별 컨텐츠 컬렉션
        self.approval_phase_collection = None  # 모델별 승인 단계 컬렉션
        self.solr_base_core_name_prefix = None   # 모델별 Solr 코어명 prefix (예: 코어명은 {base_core_name_prefix}_{lang_code}로 구성돼있음. "tourist_destination_ko")
        self.contents_type = None # 컨텐츠 타입 (DB형 : FormalContents, 기사형 : CasualContents, 이미지 : ImageContents)
        
        # 토픽 인덱스 (카프카 토픽 선택에 사용)
        self.search_topic_index = None    # 검색 토픽 인덱스
        self.meta_topic_index = None      # 메타 토픽 인덱스
        self.history_topic_index = None   # 히스토리 토픽 인덱스 
        self.deployment_topic_index = None  # 배포 토픽 인덱스
        
        # API 관련 설정
        self.model_name = None            # 모델(템플릿) 이름 (예: "관광지", "음식점")
        self.meta_url = None              # 메타 데이터 API URL
        self.temp_doc_url = None          # 임시 문서 API URL
        self.delete_temp_doc_url = None   # 임시 문서 삭제 API URL
        self.gen_v1_cid_url = None        # v1 cid 채번 url
        self.gen_v1_cid_params = None     # v1 cid 채번 요청 params
    
    # 모델별 코어명 반환 메소드 (언어코드 포함)
    def get_core_name(self, lang_code="ko"):
        """
        모델별 Solr 코어명을 반환합니다. (언어코드 포함)
        
        Args:
            lang_code (str): 언어 코드 (기본값: "ko")
            
        Returns:
            str: 언어 코드가 포함된 코어 이름 (예: "tourist_destination_ko")
        """
        return f"{self.solr_base_core_name_prefix}_{lang_code}"
    
    # 하위 클래스에서 반드시 구현해야 하는 팩토리 메소드들
    def create_meta_event(self, operation: EventOperation, cid: str, core: str):
        """
        메타 이벤트 객체를 생성합니다.
        하위 클래스에서 구현해야 합니다.
        """
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    def create_contents_schema(self, contents):
        """
        콘텐츠 스키마 객체를 생성합니다.
        하위 클래스에서 구현해야 합니다.
        """
        raise NotImplementedError("하위 클래스에서 구현해야 합니다")
    
    # 컨텐츠 생성
    def create(self, request: Request, data: BusinessParameter):
        try:
            cid_v1_response = gen_v1_cid(url=self.gen_v1_cid_url, params=self.gen_v1_cid_params)

            if cid_v1_response['success'] is False:
                raise Exception(cid_v1_response['message'])
            
            cid_v1 = cid_v1_response['data']
            cid_v2 = gen_v2_cid()
            
            if not data.body['template']['cid']['value']['v1']['value']:
                data.body['template']['cid']['value']['v1']['value'] = cid_v1
            if not data.body['template']['cid']['value']['v2']['value']:
                data.body['template']['cid']['value']['v2']['value'] = cid_v2
            if not data.body['template']['cid']['value']['v3']['value']:
                data.body['template']['cid']['value']['v3']['value'] = data.body['doc_id']
            
            createTime = int(time.time() * 1000)
            data.body['template']['base']['value']['time']['value']['create']['value'] = createTime
            data.body['template']['base']['value']['information']['value']['type']['value'] = self.contents_type
            core_lang = data.body['template']['base']['value']['language']['value']['code']['value']

            # DB 저장
            self.contents_collection.insert_one(data.body['template'])
            
            # 승인 단계 생성
            status = {
                "id": str(uuid.uuid4()),
                "phase": ElementStatus.APPROVALREQUESTPROCESSING.value,
                "cid": {
                    "v1": cid_v1,
                    "v2": cid_v2,
                    "v3": data.body['doc_id']
                },
                "services": {
                    "meta": False,
                    "search": False
                },
                "owner": request.state.account.id,
                "created_at": int(time.time() * 1000),
                "modificated_at": 0
            }
            self.approval_phase_collection.insert_one(status)

            # 메타 정보 설정
            data.body['meta']['systemInformation']['approvalStatus'] = ElementStatus.APPROVALREQUESTED.value

            # 이벤트 발행
            self.produce_to_meta(EventOperation.CREATE, cid_v2, self.get_core_name(core_lang), createTime, request.state.account.name, data.body['meta'])
            data.body = data.body['template']
            self.produce_to_search(EventOperation.CREATE, data, request.state.account.name, ElementStatus.APPROVALREQUESTPROCESSING.value)

            return {"status": "success", "message": "Process Start"}   
          
        except Exception as e:
            print(str(e))
            return {"status": "fail", "message": str(e)}

    # 컨텐츠 상태 변경
    def change(self, request: Request, data: BusinessParameter):
        try:
            cid = data.body['cid.value.v2.value']
            approvalStatus = data.change['status']

            doc = self.contents_collection.find_one(data.body)
            core_lang = doc['base']['value']['language']['value']['code']['value']

            changeTime = int(time.time() * 1000)

            if approvalStatus == ElementStatus.APPROVED.value:
                # 승인 프로세스 작업
                status = {
                    "id": str(uuid.uuid4()),
                    "phase": ElementStatus.APPROVALPROCESSING.value, 
                    "cid": {
                        "v1": doc['cid']['value']['v1']['value'],
                        "v2": cid,
                        "v3": doc['cid']['value']['v3']['value']
                    },
                    "services": {
                        "history": False,
                        "deployment": False
                    },
                    "owner": request.state.account.id,
                    "created_at": int(time.time() * 1000),
                    "modificated_at": 0
                }
                self.approval_phase_collection.insert_one(status)

                message = {
                    'id': str(uuid.uuid4()),
                    'timestamp': int(time.time() * 1000),
                    'operation': 'UPDATE',
                    'application': self.service_name,
                    'core': self.get_core_name(core_lang),
                    'targetDocument': {
                        'cid_v1': doc['cid']['value']['v1']['value'],
                        'cid_v2': cid,
                        'cid_v3': doc['cid']['value']['v3']['value']
                    },
                    'payload': {
                        'information_type': self.contents_type,
                        'approvalStatus': ElementStatus.APPROVALPROCESSING.value
                    }
                }
                
                # 이벤트 발행
                self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)

                meta = {
                    "approvalStatus": ElementStatus.APPROVALPROCESSING.value,
                    "message": data.change.get("message", None)
                }

                self.produce_to_meta(EventOperation.CHANGE, cid, self.get_core_name(core_lang), changeTime, request.state.account.name, meta)
                
                # 추가 이벤트 발행
                self.producer_send_message(self.history_topic_index, json.dumps(message), self.producer_meesage_callback)
                self.producer_send_message(self.deployment_topic_index, json.dumps(message), self.producer_meesage_callback)

                return {"status": "success", "message": "Process Start"}
            
            else:
                # 다른 상태 변경
                meta = {
                    "approvalStatus": approvalStatus,
                    "message": data.change.get("message", None)
                }

                message = {
                    'id': str(uuid.uuid4()),
                    'timestamp': int(time.time() * 1000),
                    'operation': 'UPDATE',
                    'application': self.service_name,
                    'core': self.get_core_name(core_lang),
                    'targetDocument': {
                        'cid_v1': doc['cid']['value']['v1']['value'],
                        'cid_v2': cid,
                        'cid_v3': doc['cid']['value']['v3']['value']
                    },
                    'payload': {
                        'information_type': self.contents_type,
                        'approvalStatus': approvalStatus
                    }
                }

                # 이벤트 발행
                self.produce_to_meta(EventOperation.CHANGE, cid, self.get_core_name(core_lang), changeTime, request.state.account.name, meta)
                self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)
                return {"status": "success", "message": "Process Start"}
        
        except Exception as e:
            print(str(e))
            return {"status": "fail", "message": str(e)}

    # 컨텐츠 상세 조회
    def detail(self, request: Request, data: BusinessParameter):
        try:
            # 컨텐츠 조회
            contents = self.contents_collection.find_one(data.body)
            del contents['_id']

            # 메타 정보 조회 - 하드코딩 URL 대신 속성 사용
            if self.meta_url is None:
                raise ValueError("meta_url이 설정되지 않았습니다. 하위 클래스에서 설정해주세요.")
                
            params_meta = {
                "cid": data.body['cid.value.v2.value']
            }
            response_meta = requests.get(self.meta_url, params_meta)
            meta = response_meta.json()['body']['result']

            # 편집 중인 경우 임시 문서 정보 조회
            if meta['systemInformation']['approvalStatus'] == ElementStatus.EDITING.value:
                if self.temp_doc_url is None:
                    raise ValueError("temp_doc_url이 설정되지 않았습니다. 하위 클래스에서 설정해주세요.")
                    
                # 임시 문서 조회 요청
                payload_temp = {
                    "body": {
                        'id': contents['cid']['value']['v3']['value'],
                        'model': self.model_name,
                        'template': contents,
                        'meta': meta
                    }
                }
                headers = dict(request.headers)
                response_temp = requests.get(url=self.temp_doc_url, json=payload_temp, headers=headers)
                return response_temp.json()['body']
            else:
                return {"template": contents, "meta": meta}
            
        except Exception as e:
            return {"status": "Fail", "message": str(e)}
        
    # 컨텐츠 수정
    def update(self, request: Request, data: BusinessParameter):
        try:
            cid_v2 = data.body['template']['cid']['value']['v2']['value']
            
            updateTime = int(time.time() * 1000)
            data.body['template']['base']['value']['time']['value']['modified']['value'] = updateTime
            core_lang = data.body['template']['base']['value']['language']['value']['code']['value']
            # 컨텐츠 업데이트
            self.contents_collection.update_one(
                {'cid.value.v2.value': cid_v2},
                {'$set': data.body['template']}
            )

            # 승인 단계 생성
            status = {
                "id": str(uuid.uuid4()),
                "phase": ElementStatus.APPROVALREQUESTPROCESSING.value,
                "cid": {
                    "v1": "",
                    "v2": cid_v2,
                    "v3": data.body['template']['cid']['value']['v3']['value']
                },
                "services": {
                    "meta": False,
                    "search": False
                },
                "owner": request.state.account.id,
                "created_at": int(time.time() * 1000),
                "modificated_at": 0
            }
            self.approval_phase_collection.insert_one(status)

            # 메타 정보 업데이트 및 이벤트 발행
            data.body['meta']['systemInformation']['approvalStatus'] = ElementStatus.APPROVALREQUESTPROCESSING.value
            self.produce_to_meta(EventOperation.UPDATE, cid_v2, self.get_core_name(core_lang), updateTime, request.state.account.name, data.body['meta'])
            
            data.body = data.body['template']
            # 검색 이벤트 발행
            self.produce_to_search(EventOperation.UPDATE, data, None, ElementStatus.APPROVALREQUESTPROCESSING.value)

            return {"status": "success", "message": "Process Start"}   
          
        except Exception as e:
            print(str(e))
            return {"status": "fail", "message": str(e)}

    # 컨텐츠 배포
    def deployments(self, request: Request, data: BusinessParameter):
        try:
            cid = data.body['cid.value.v2.value']
            currentStatus = data.change['status']

            deployTime = int(time.time() * 1000)

            # 배포 상태 업데이트
            doc = self.contents_collection.find_one_and_update(
                data.body, 
                {"$set": {"base.value.status.value.currentStatus.value": data.change['status']}}, 
                return_document=ReturnDocument.AFTER
            )
            core_lang = doc['base']['value']['language']['value']['code']['value']
            
            message = {
                'id': str(uuid.uuid4()),
                'timestamp': int(time.time() * 1000),
                'operation': 'UPDATE',
                'application': self.service_name,
                'core': self.get_core_name(core_lang),
                'targetDocument': {
                    'cid_v1': doc['cid']['value']['v1']['value'],
                    'cid_v2': cid,
                    'cid_v3': doc['cid']['value']['v3']['value']
                },
                'payload': {
                    'information_type': self.contents_type,
                    'currentStatus': currentStatus,
                    'deployed_at': deployTime
                }
            }

            # 이벤트 발행
            self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)
            self.producer_send_message(self.deployment_topic_index, json.dumps(message), self.producer_meesage_callback)

            meta = {
               "deployStatus": currentStatus,
               "message": data.change.get("message", None)
            }

            self.produce_to_meta(EventOperation.DEPLOY, cid, self.get_core_name(core_lang), deployTime, request.state.account.name, meta)

            return {"status": "success", "message": "Document Deployed"}
            
        except Exception as e:
            print(str(e))
            return {"status": "fail", "message": str(e)}
    
    # 컨텐츠 삭제
    def delete(self, request: Request, data: BusinessParameter):
        try:
            doc = self.contents_collection.find_one(data.body)
            cid = doc['cid']['value']['v2']['value']

            deleteTime = int(time.time() * 1000)
            core_lang = doc['base']['value']['language']['value']['code']['value']
            
            message = {
                'id': str(uuid.uuid4()),
                'timestamp': deleteTime,
                'operation': 'DELETE',
                'application': self.service_name,
                'core': self.get_core_name(core_lang),
                'targetDocument': {
                    'cid_v1': doc['cid']['value']['v1']['value'],
                    'cid_v2': cid,
                    'cid_v3': doc['cid']['value']['v3']['value']
                },
                'payload': {
                    'information_type': self.contents_type
                }
            }

            # 이벤트 발행
            self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)

            meta = {
                "message": data.change.get("message", None)
            }

            self.produce_to_meta(EventOperation.DELETE, cid, self.get_core_name(core_lang), deleteTime, "SYSTEM", meta)
            
            return {"status": "success", "message": "Document deleted"}
            
        except Exception as e:
            return {"status": "fail", "message": f"{e}"}
    
    # 컨텐츠 승인 단계 처리
    def update_phase(self, data: BusinessParameter):
        try:
            target = data.body['cid']
            service = data.body['service']
            status = data.body['status']

            updateTime = int(time.time() * 1000)

            # 시작 시 문서를 조회하여 언어 코드 확인
            # 언어 코드를 미리 확인하여 예외 처리에서도 사용할 수 있게 함
            core_lang = "ko"  # 기본값
            try:
                doc = self.contents_collection.find_one({"cid.value.v2.value": target})
                if doc and 'base' in doc and 'value' in doc['base'] and 'language' in doc['base']['value'] and 'code' in doc['base']['value']['language']['value']:
                    core_lang = doc['base']['value']['language']['value']['code']['value']
            except Exception as lookup_error:
                print(f"언어 코드 조회 중 오류: {lookup_error}")
                # 기본값 사용

            if status == "success":
                # 승인 단계 업데이트
                approval_phase = self.approval_phase_collection.find_one_and_update(
                    {"cid.v2": target}, 
                    {"$set": {f"services.{service}": True, "modificated_at": updateTime}}, 
                    return_document=ReturnDocument.AFTER
                )

                # 모든 서비스가 완료되었는지 확인
                if approval_phase and "services" in approval_phase and all(value is True for value in approval_phase["services"].values()):
                    # 승인 요청 처리 중인 경우
                    if approval_phase['phase'] == ElementStatus.APPROVALREQUESTPROCESSING.value:
                        message = {
                            'id': str(uuid.uuid4()),
                            'timestamp': int(time.time() * 1000),
                            'operation': 'UPDATE',
                            'application': self.service_name,
                            'core': self.get_core_name(core_lang),
                            'targetDocument': {
                                'cid_v1': '',
                                'cid_v2': target,
                                'cid_v3': ''
                            },
                            'payload': {
                                'information_type': self.contents_type,
                                'approvalStatus': ElementStatus.APPROVALREQUESTED.value
                            }
                        }

                        self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)

                        # 임시 문서 삭제
                        if self.delete_temp_doc_url is None:
                            raise ValueError("delete_temp_doc_url이 설정되지 않았습니다. 하위 클래스에서 설정해주세요.")
                            
                        payload = {
                            "body": {
                                'user_id': approval_phase['owner'],
                                'doc_id': approval_phase['cid']['v3']
                            }
                        }

                        response = requests.post(self.delete_temp_doc_url, json=payload)
                        if response.status_code != 200:
                            raise Exception('임시 저장 문서 삭제에 실패했습니다.')

                    # 승인 처리 중인 경우
                    elif approval_phase['phase'] == ElementStatus.APPROVALPROCESSING.value:
                        self.contents_collection.update_one(
                            {"cid.value.v2.value": target}, 
                            {"$set": {"base.value.status.value.currentStatus.value": DeployStatus.DEPLOYED.value}}
                        )
                        meta = {
                            "approvalStatus": ElementStatus.APPROVED.value,
                            "message": None
                        }
                        self.produce_to_meta(EventOperation.CHANGE, target, self.get_core_name(core_lang), int(time.time() * 1000), "SYSTEM", meta)
                        
                    # 승인 단계 레코드 삭제
                    self.approval_phase_collection.delete_one({"cid.v2": target})

            else: # 오류 메세지
                raise Exception('처리 중 오류가 발생했습니다.')

            return {"status": "success", "message": "Phase Updated"}
        
        except Exception as e:
            # 오류 처리
            meta = {
                "approvalStatus": ElementStatus.APPROVALREQUESTERROR.value,
                "message": str(e)
            }

            self.produce_to_meta(EventOperation.CHANGE, target, self.get_core_name(core_lang), updateTime, "SYSTEM", meta)

            message = {
                'id': str(uuid.uuid4()),
                'timestamp': int(time.time() * 1000),
                'operation': 'UPDATE',
                'application': self.service_name,
                'core': self.get_core_name(core_lang),
                'targetDocument': {
                    'cid_v1': '',
                    'cid_v2': target,
                    'cid_v3': ''
                },
                'payload': {
                    'information_type': self.contents_type,
                    'approvalStatus': ElementStatus.APPROVALREQUESTERROR.value
                }
            }

            self.producer_send_message(self.search_topic_index, json.dumps(message), self.producer_meesage_callback)
            print(str(e))
            return {"status": "fail", "message": str(e)}

    def produce_to_meta(self, operation: EventOperation, cid, core, Time, Changer, meta = None):
        ## CREATE일 땐 임시 저장 문서에서 가져온 meta와, 상태 변경자, 상태 변경시간
        ## UPDATE일 땐 상태 변경자, 상태 변경시간, 변화한 meta 값
        ## DELETE일 땐 상태 변경자, 상태 변경시간
        payload = {
            'changer': Changer,
            'time': Time,
            'meta': meta
        }

        # 하위 클래스에서 구현한 팩토리 메소드 사용
        metaEvent: MetaEvent = self.create_meta_event(operation.value, cid, core)
        metaEvent.payload = payload

        self.producer_send_message(self.meta_topic_index, metaEvent.model_dump_json(exclude='config_yaml'), self.producer_meesage_callback)

    def produce_to_search(self, operation: EventOperation, data: BusinessParameter, changer = None, approval_status: str = None):
        try:
            # 검색 이벤트 발행 공통 로직
            if '_id' in data.body and data.body['_id']:
                del data.body['_id']

            # 하위 클래스에서 구현한 팩토리 메소드 사용
            contentsSchema = self.create_contents_schema(data.body)

            target_lang = contentsSchema.get_item('base.language.code', None)
            core_name = f"{self.solr_base_core_name_prefix}_{target_lang}"

            target_document = {
                'cid_v1': contentsSchema.get_item('cid.v1', None),
                'cid_v2': contentsSchema.get_item('cid.v2', None),
                'cid_v3': contentsSchema.get_item('cid.v3', None)
            }

            if operation == EventOperation.CREATE:
                contentsSchema.json_schema['writer'] = changer
                # contentsSchema.json_schema['department'] = payload['departmentId'] # TODO 현재는 토큰에 departmentId만 저장되고 있어 department의 name을 알고 싶으면 department 서비스에 요청해서 받아와야 함 시간이 오래 걸릴 수도 있으니 토큰에 departmentName을 추가하는 방법도 고려 했으면 좋겠음

            contentsSchema.json_schema['approvalStatus'] = approval_status

            searchEvent = SearchEvent.create(operation, core_name, target_document)
            searchEvent.set_payload(contentsSchema.json_schema)
            
            self.producer_send_message(self.search_topic_index, searchEvent.model_dump_json(exclude='config_yaml'), self.producer_meesage_callback)
        
        except Exception as e:
            print(e)