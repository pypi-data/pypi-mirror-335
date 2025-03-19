from typing import Any, Dict, List, Optional, Tuple, AsyncIterator, Iterator, cast
import json
import time
import uuid
import logging
from datetime import datetime
import copy
import os
from dotenv import load_dotenv

from google.cloud import firestore
from google.cloud.exceptions import GoogleCloudError
from google.oauth2 import service_account

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.serde.base import SerializerProtocol
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.pregel.types import StateSnapshot

from botrun_flow_lang.constants import CHECKPOINTER_STORE_NAME
from botrun_flow_lang.services.base.firestore_base import FirestoreBase

load_dotenv()

# Set up logger
logger = logging.getLogger("FirestoreCheckpointer")
logger.setLevel(logging.INFO)
# Create console handler if it doesn't exist
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    logger.addHandler(ch)


class FirestoreCheckpointer(BaseCheckpointSaver):
    """Checkpointer implementation that uses Firestore for storage.

    This implementation provides both synchronous and asynchronous methods.
    """

    def __init__(
        self,
        env_name: str,
        serializer: Optional[SerializerProtocol] = None,
        collection_name: Optional[str] = None,
    ):
        """Initialize the Firestore checkpointer.

        Args:
            env_name: Environment name to be used as prefix for collection.
            serializer: Optional serializer to use for converting values to storable format.
            collection_name: Optional custom collection name. If not provided,
                             it will use {env_name}-{CHECKPOINTER_STORE_NAME}.
            credential_path: Optional path to the Google Cloud credentials JSON file.
                             If not provided, will use the default authentication method.
        """
        logger.info(f"Initializing FirestoreCheckpointer with env_name={env_name}")
        self.serializer = serializer or JsonPlusSerializer()
        self._collection_name = (
            collection_name or f"{env_name}-{CHECKPOINTER_STORE_NAME}"
        )
        logger.info(f"Using collection: {self._collection_name}")

        try:
            # 嘗試初始化 Firestore 客戶端
            google_service_account_key_path = os.getenv(
                "GOOGLE_APPLICATION_CREDENTIALS_FOR_FASTAPI",
                "/app/keys/scoop-386004-d22d99a7afd9.json",
            )
            credentials = service_account.Credentials.from_service_account_file(
                google_service_account_key_path,
                scopes=["https://www.googleapis.com/auth/datastore"],
            )

            # 直接从环境变量获取项目 ID
            project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
            if project_id:
                self.db = firestore.Client(project=project_id, credentials=credentials)
            else:
                self.db = firestore.Client(credentials=credentials)

            self.collection = self.db.collection(self._collection_name)

            logger.info("Firestore client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Firestore client: {e}", exc_info=True)
            raise
