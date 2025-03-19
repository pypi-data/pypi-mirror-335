from typing import overload, TypeVar
from datetime import datetime
import json
import os
import uuid

from promptlab.enums import AssetType
from promptlab.db.sql import SQLQuery
from promptlab.tracer.tracer import Tracer
from promptlab.types import Dataset, PromptTemplate
from promptlab.utils import Utils

T = TypeVar('T', Dataset, PromptTemplate)

class Asset:

    def __init__(self, tracer: Tracer):        
        self.tracer = tracer
    
    @overload
    def create_or_update(self, asset: Dataset) -> Dataset:
        ...
    
    @overload
    def create_or_update(self, asset: PromptTemplate) -> PromptTemplate:
        ...

    @overload
    def deploy(self, asset: PromptTemplate, target_dir: str):
        ...
    
    def create_or_update(self, asset: T) -> T:

        if isinstance(asset, Dataset):
            return self._handle_dataset(asset)
        elif isinstance(asset, PromptTemplate):
            return self._handle_prompt_template(asset)
        else:
            raise TypeError(f"Unsupported asset type: {type(asset)}")
    
    def _handle_dataset(self, dataset: Dataset) -> Dataset:

        timestamp = datetime.now().isoformat()
        if dataset.id is not None:
            dataset_record = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_BY_ID_QUERY, (dataset.id,dataset.id))[0]

            dataset.name = dataset_record['asset_name']
            dataset.description = dataset_record['asset_description'] if dataset.description is None else dataset.description           
            dataset.version = dataset_record['asset_version'] + 1

            binary = dataset_record['asset_binary'] if dataset.file_path is None else {"file_path": dataset.file_path}

            self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (dataset.id, dataset.name, dataset.description, dataset.version, AssetType.DATASET.value, json.dumps(binary), timestamp))
        else:        
            dataset.id = str(uuid.uuid4())
            dataset.version = 0

            binary = {
                "file_path": dataset.file_path
            }

            self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (dataset.id, dataset.name, dataset.description, dataset.version, AssetType.DATASET.value, json.dumps(binary), timestamp))

        return dataset
    
    def _handle_prompt_template(self, template: PromptTemplate) -> PromptTemplate:

        timestamp = datetime.now().isoformat()

        if template.id is not None:
            prompt_template = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_BY_ID_QUERY, (template.id,template.id))[0]
            system_prompt, user_prompt, prompt_template_variables = Utils.split_prompt_template(prompt_template['asset_binary'])

            template.name = prompt_template['asset_name']
            template.description = prompt_template['asset_description'] if template.description is None else template.description
            template.system_prompt = system_prompt if template.system_prompt is None else template.system_prompt
            template.user_prompt = user_prompt if template.user_prompt is None else template.user_prompt
            template.version = prompt_template['asset_version'] + 1
            binary = f'''
                <<system>>
                    {template.system_prompt}
                <<user>>
                    {template.user_prompt}
            '''

            self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (template.id, template.name, template.description, template.version, AssetType.PROMPT_TEMPLATE.value,  binary, timestamp))
        else:
            template.id = str(uuid.uuid4())
            template.version = 0

            binary = f'''
                <<system>>
                    {template.system_prompt}
                <<user>>
                    {template.user_prompt}
            '''
            
            self.tracer.db_client.execute_query(SQLQuery.INSERT_ASSETS_QUERY, (template.id, template.name, template.description, template.version, AssetType.PROMPT_TEMPLATE.value,  binary, timestamp))
            
        return template
    
    def deploy(self, asset: T, target_dir: str) -> T:

        if isinstance(asset, PromptTemplate):
            return self._handle_prompt_template_deploy(asset, target_dir)
        else:
            raise TypeError(f"Unsupported asset type: {type(asset)}")
        
    def _handle_prompt_template_deploy(self, template: PromptTemplate, target_dir: str):

        prompt_template = self.tracer.db_client.fetch_data(SQLQuery.SELECT_ASSET_QUERY, (template.id, template.version))[0]

        prompt_template_name = prompt_template['asset_name']
        prompt_template_binary = prompt_template['asset_binary']

        prompt_template_path = os.path.join(target_dir, prompt_template_name)
        
        with open(prompt_template_path, 'w', encoding='utf-8') as file:
            file.write(prompt_template_binary)

        self.tracer.db_client.execute_query(SQLQuery.DEPLOY_ASSET_QUERY, (template.id, template.version))
