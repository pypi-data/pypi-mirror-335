from __future__ import annotations

import os
import logging
from copy import deepcopy
from typing import Any, Callable, Dict
from urllib.parse import urlparse

from kedro.io.core import AbstractDataset, DataSetError, parse_dataset_definition
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential

logger = logging.getLogger(__name__)

class PartitionedSharepointDataset(AbstractDataset[dict[str, Any], dict[str, Callable[[], Any]]]):
    """
    Dataset particionado para SharePoint.
    
    Este dataset lista os arquivos (partições) em uma pasta do SharePoint que possuem
    um sufixo específico e, para cada partição, instancia um dataset subjacente (por exemplo,
    um dataset de PDF) para realizar as operações de load/save.

    Exemplo de uso:

    >>> dataset = PartitionedSharepointDataset(
    ...     path="https://tenant.sharepoint.com/sites/MySite/Shared Documents/MinhaPasta",
    ...     dataset=PDFDataSet,  # ou {"type": PDFDataSet, ...}
    ...     filename_suffix=".pdf",
    ...     credentials={"username": "usuario@dominio.com", "password": "segredo"},
    ...     overwrite=True,
    ... )
    >>>
    >>> # Carrega de forma lazy todas as partições
    >>> partitions = dataset.load()
    >>> for partition_id, load_func in partitions.items():
    ...     data = load_func()
    ...     # processa os dados de cada partição
    ...
    >>> # Para salvar, passe um dicionário onde a chave identifica a partição
    >>> dataset.save({"fatura_001": pdf_data1, "fatura_002": pdf_data2})
    """

    def __init__(
        self,
        *,
        path: str,
        dataset: str | type | Dict[str, Any],
        filename_suffix: str = "",
        credentials: Dict[str, Any],
        overwrite: bool = False,
        load_args: Dict[str, Any] = None,
        save_args: Dict[str, Any] = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        self._path = path.rstrip("/")
        self._filename_suffix = filename_suffix
        self._overwrite = overwrite
        self._credentials = deepcopy(credentials) or {}
        self._load_args = load_args or {}
        self._save_args = save_args or {}
        self.metadata = metadata

        if isinstance(dataset, dict):
            self._dataset_type, self._dataset_config = parse_dataset_definition(dataset)
        else:
            self._dataset_type = dataset
            self._dataset_config = {}

        # logger.info("PartitionedSharepointDataset criado com path: %s", self._path)
        logger.debug("Dataset subjacente: %s, config: %s", self._dataset_type, self._dataset_config)

    def _parse_sharepoint_path(self) -> tuple[str, str]:
        """
        Separa a URL completa da pasta em:
        - site_url: ex: "https://vedraapoio.sharepoint.com/sites/Rede"
        - relative_folder: ex: "/sites/Rede/Documentos Compartilhados/MinhaPasta"
        """
        parsed = urlparse(self._path)
        scheme = parsed.scheme
        netloc = parsed.netloc
        parts = parsed.path.strip("/").split("/")
        if len(parts) >= 2 and parts[0].lower() == "sites":
            site_url = f"{scheme}://{netloc}/sites/{parts[1]}"
            relative_folder = "/" + "/".join(parts)
        else:
            site_url = f"{scheme}://{netloc}"
            relative_folder = parsed.path
        logger.debug("Parsed SharePoint path: site_url=%s, relative_folder=%s", site_url, relative_folder)
        return site_url, relative_folder

    def _get_ctx(self) -> ClientContext:
        """
        Cria e retorna um ClientContext autenticado com as credenciais fornecidas.
        """
        site_url, _ = self._parse_sharepoint_path()
        user_credentials = UserCredential(self._credentials["username"], self._credentials["password"])
        ctx = ClientContext(site_url).with_credentials(user_credentials)
        logger.debug("ClientContext criado para site: %s", site_url)
        return ctx

    def _list_partitions(self) -> list[str]:
        site_url, folder_relative_url = self._parse_sharepoint_path()
        ctx = self._get_ctx()
        folder = ctx.web.get_folder_by_server_relative_url(folder_relative_url)
        files = folder.files
        ctx.load(files)
        ctx.execute_query()
        partition_files = []
        logger.info("Listando arquivos na pasta: %s", folder_relative_url)
        for file in files:
            file_name = file.properties.get("Name")
            if self._filename_suffix and not file_name.endswith(self._filename_suffix):
                continue
            server_relative_url = file.properties.get("ServerRelativeUrl")
            parsed = urlparse(self._path)
            base_url = f"{parsed.scheme}://{parsed.netloc}"
            full_url = f"{base_url}{server_relative_url}"
            logger.debug("Arquivo encontrado: %s", full_url)
            partition_files.append(full_url)
        logger.info("Total de partições encontradas: %d", len(partition_files))
        return partition_files

    def _load(self) -> dict[str, Callable[[], Any]]:
        """
        Para cada partição encontrada, instancia o dataset subjacente com o respectivo
        caminho do arquivo e retorna um dicionário em que a chave é o ID da partição e
        o valor é uma função que, quando chamada, carrega os dados daquela partição.
        """
        partitions: dict[str, Callable[[], Any]] = {}
        partition_files = self._list_partitions()
        if not partition_files:
            raise DataSetError(
                f"Nenhuma partição encontrada em '{self._path}' com o sufixo '{self._filename_suffix}'"
            )
        for file_url in partition_files:
            file_name = os.path.basename(file_url)
            partition_id = file_name[:-len(self._filename_suffix)] if file_name.endswith(self._filename_suffix) else file_name
            
            ds_config = deepcopy(self._dataset_config)

            for key in ["path", "layer"]:
                if key in ds_config:
                    logger.debug("Removendo '%s' herdado da configuração: %s", key, ds_config.pop(key))

            ds_config["filepath"] = file_url
            if self._load_args:
                ds_config.setdefault("load_args", {}).update(self._load_args)
            try:
                dataset_instance = self._dataset_type(**ds_config)
                partitions[partition_id] = dataset_instance.load
                logger.debug("Partição %s configurada com dataset: %s", partition_id, dataset_instance)
            except Exception as e:
                logger.error("Erro ao instanciar dataset para partição %s: %s", partition_id, e)
                raise DataSetError(f"Erro ao instanciar dataset para partição {partition_id}") from e
        return partitions

    def _save(self, data: dict[str, Any]) -> None:
        """
        Para cada partição do dicionário `data`, salva os dados usando o dataset subjacente.
        O processo é:
          1. Salvar o dado em um arquivo local temporário;
          2. Ler o conteúdo salvo;
          3. Fazer o upload do conteúdo para a pasta SharePoint com o nome definido.
        Se `overwrite` estiver True, apaga os arquivos existentes na pasta.
        """
        site_url, folder_relative_url = self._parse_sharepoint_path()
        ctx = self._get_ctx()

        folder = ctx.web.get_folder_by_server_relative_url(folder_relative_url)
        ctx.load(folder)
        ctx.execute_query()
        server_relative_folder = folder.properties.get("ServerRelativeUrl")
        logger.debug("Server relative folder obtida: %s", server_relative_folder)

        if self._overwrite:
            existing_files = self._list_partitions()
            for file_url in existing_files:
                try:
                    parsed_file_url = urlparse(file_url)
                    file_server_relative = parsed_file_url.path
                    file_to_delete = ctx.web.get_file_by_server_relative_url(file_server_relative)
                    file_to_delete.delete_object()
                    ctx.execute_query()
                    logger.info("Arquivo deletado: %s", file_server_relative)
                except Exception as e:
                    logger.warning("Erro ao deletar arquivo %s: %s", file_url, e)

        for partition_id, partition_data in sorted(data.items()):
            target_filename = f"{partition_id}{self._filename_suffix}"

            if callable(partition_data):
                try:
                    logger.debug("Executando partition_data() para a partição %s", partition_id)
                    partition_data = partition_data()
                    logger.debug("Conteúdo obtido para a partição %s (tipo: %s)", partition_id, type(partition_data))
                except Exception as e:
                    logger.exception("Erro ao executar partition_data() para a partição %s", partition_id)
                    raise DataSetError("Erro ao executar a função lazy partition_data()") from e
            
            if not isinstance(partition_data, bytes):
                try:
                    with open(partition_data, "rb") as f:
                        partition_data = f.read()
                    logger.debug("Conteúdo do PDF lido a partir do caminho local para a partição %s", partition_id)
                except Exception as e:
                    logger.exception("Não foi possível converter partition_data para bytes para a partição %s", partition_id)
                    raise DataSetError(f"Erro ao converter partition_data para bytes para a partição {partition_id}") from e

            try:
                folder.upload_file(target_filename, partition_data)
                ctx.execute_query()
                logger.info("Partição %s enviada para o SharePoint como %s", partition_id, f"{server_relative_folder}/{target_filename}")
            except Exception as e:
                logger.exception("Erro ao fazer upload da partição %s", partition_id)
                raise DataSetError(f"Erro ao fazer upload da partição {partition_id}") from e

    def _describe(self) -> dict[str, Any]:
        return {
            "path": self._path,
            "dataset_type": self._dataset_type.__name__ if hasattr(self._dataset_type, "__name__") else str(self._dataset_type),
            "dataset_config": self._dataset_config,
        }

    def _exists(self) -> bool:
        try:
            return bool(self._list_partitions())
        except Exception:
            return False
