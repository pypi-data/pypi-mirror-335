import logging
from pathlib import Path

import esgvoc.core.constants
from esgvoc.core.data_handler import JsonLdResource
from esgvoc.core.db.connection import DBConnection
from esgvoc.core.service.data_merger import DataMerger
from esgvoc.core.db.models.mixins import TermKind
from pydantic import BaseModel

import esgvoc.core.db.connection as db
from esgvoc.core.db.connection import read_json_file
from esgvoc.core.db.models.project import Collection, Project, PTerm
import  esgvoc.core.service as service


_LOGGER = logging.getLogger("project_ingestion")

def infer_term_kind(json_specs: dict) -> TermKind:
    if esgvoc.core.constants.PATTERN_JSON_KEY in json_specs:
        return TermKind.PATTERN
    elif esgvoc.core.constants.COMPOSITE_PARTS_JSON_KEY in json_specs:
        return TermKind.COMPOSITE
    else:
        return TermKind.PLAIN


def ingest_metadata_project(connection:DBConnection,git_hash):
    with connection.create_session() as session:
        project = Project(id=str(connection.file_path.stem), git_hash=git_hash,specs={})
        session.add(project)    
        session.commit()

###############################
def get_data_descriptor_id_from_context(collection_context: dict) -> str:
    data_descriptor_url = collection_context[esgvoc.core.constants.CONTEXT_JSON_KEY][esgvoc.core.constants.DATA_DESCRIPTOR_JSON_KEY]
    return Path(data_descriptor_url).name


def instantiate_project_term(universe_term_json_specs: dict,
                             project_term_json_specs_update: dict,
                             pydantic_class: type[BaseModel]) -> dict:
    term_from_universe = pydantic_class(**universe_term_json_specs)
    updated_term = term_from_universe.model_copy(
        update=project_term_json_specs_update, deep=True
    )
    return updated_term.model_dump()


def ingest_collection(collection_dir_path: Path,
                      project: Project,
                      project_db_session) -> None:


    collection_id = collection_dir_path.name
    collection_context_file_path = collection_dir_path.joinpath(esgvoc.core.constants.CONTEXT_FILENAME)
    try:
        collection_context = read_json_file(collection_context_file_path)
        data_descriptor_id = get_data_descriptor_id_from_context(collection_context)
    except Exception as e:
        msg = f'Unable to read project context file {collection_context_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
    # [KEEP]
    collection = Collection(
        id=collection_id,
        context=collection_context,
        project=project,
        data_descriptor_id=data_descriptor_id,
        term_kind="") # we ll know it only when we ll add a term (hypothesis all term have the same kind in a collection
    term_kind_collection = None

    for term_file_path in collection_dir_path.iterdir():
        _LOGGER.debug(f"found term path : {term_file_path}")
        if term_file_path.is_file() and term_file_path.suffix==".json": 
            try:
                json_specs = DataMerger(data=JsonLdResource(uri =str(term_file_path)),
                                        # locally_available={"https://espri-mod.github.io/mip-cmor-tables":".cache/repos/WCRP-universe"}).merge_linked_json()[-1]
                                        locally_available={"https://espri-mod.github.io/mip-cmor-tables":service.current_state.universe.local_path}).merge_linked_json()[-1]

                term_kind = infer_term_kind(json_specs)
                term_id = json_specs["id"]

                if term_kind_collection is None:
                    term_kind_collection = term_kind
                
            except Exception as e:
                _LOGGER.warning(f'Unable to read term {term_file_path}. Skip.\n{str(e)}')
                continue
            try:
                term = PTerm(
                    id=term_id,
                    specs=json_specs,
                    collection=collection,
                    kind=term_kind,
                )
                project_db_session.add(term)
            except Exception as e:
                _LOGGER.error(
                    f"fail to find term {term_id} in data descriptor {data_descriptor_id} "
                    + f"for the collection {collection_id} of the project {project.id}. Skip {term_id}.\n{str(e)}"
                )
                continue
    if term_kind_collection:
        collection.term_kind = term_kind_collection
    project_db_session.add(collection)

def ingest_project(project_dir_path: Path,
                   project_db_file_path: Path,
                   git_hash : str
                   ):
    try:
        project_connection = db.DBConnection(project_db_file_path)
    except Exception as e:
        msg = f'Unable to read project SQLite file at {project_db_file_path}. Abort.'
        _LOGGER.fatal(msg)
        raise RuntimeError(msg) from e
        
    with project_connection.create_session() as project_db_session:
        try:
            project_specs_file_path = project_dir_path.joinpath(esgvoc.core.constants.PROJECT_SPECS_FILENAME)
            project_json_specs = read_json_file(project_specs_file_path)
            project_id = project_json_specs[esgvoc.core.constants.PROJECT_ID_JSON_KEY]
        except Exception as e:
            msg = f'Unable to read project specs file  {project_specs_file_path}. Abort.'
            _LOGGER.fatal(msg)
            raise RuntimeError(msg) from e
        
        project = Project(id=project_id, specs=project_json_specs,git_hash=git_hash)
        project_db_session.add(project)
        

        for collection_dir_path in project_dir_path.iterdir():
            if collection_dir_path.is_dir() and (collection_dir_path / "000_context.jsonld").exists(): #TODO maybe put that in settings
                _LOGGER.debug(f"found collection dir : {collection_dir_path}")
                try:
                    ingest_collection(collection_dir_path,
                                      project,
                                      project_db_session)
                except Exception as e:
                    msg = f'Unexpected error while ingesting collection {collection_dir_path}. Abort.'
                    _LOGGER.fatal(msg)
                    raise RuntimeError(msg) from e
        project_db_session.commit()











