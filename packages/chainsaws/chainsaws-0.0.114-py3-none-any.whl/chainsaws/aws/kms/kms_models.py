from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, List, TypedDict, Literal

from chainsaws.aws.shared.config import APIConfig


# Key usage types for KMS keys
KeyUsage = Literal['ENCRYPT_DECRYPT', 'SIGN_VERIFY', 'GENERATE_VERIFY_MAC']

# Customer master key specifications
CustomerMasterKeySpec = Literal[
    'SYMMETRIC_DEFAULT',
    'RSA_2048',
    'RSA_3072',
    'RSA_4096',
    'ECC_NIST_P256',
    'ECC_NIST_P384',
    'ECC_NIST_P521',
    'ECC_SECG_P256K1'
]

# KMS key states
KeyState = Literal['Enabled', 'Disabled',
                   'PendingDeletion', 'PendingImport', 'Unavailable']

# Key manager types
KeyManager = Literal['AWS', 'CUSTOMER']

# Key origin types
OriginType = Literal['AWS_KMS', 'EXTERNAL', 'AWS_CLOUDHSM']


@dataclass
class KMSAPIConfig(APIConfig):
    """KMS API configuration."""
    pass


class EncryptResponse(TypedDict):
    """Response type for encrypt operation."""
    CiphertextBlob: bytes
    KeyId: str
    EncryptionAlgorithm: str


class DecryptResponse(TypedDict):
    """Response type for decrypt operation."""
    Plaintext: bytes
    KeyId: str
    EncryptionAlgorithm: str


class ListKeysResponse(TypedDict):
    """Response type for list_keys operation."""
    Keys: List[Dict]
    NextMarker: Optional[str]


class GenerateDataKeyResponse(TypedDict):
    """Response type for generate_data_key operation."""
    Plaintext: bytes
    CiphertextBlob: bytes
    KeyId: str
    EncryptionAlgorithm: str


class GenerateRandomResponse(TypedDict):
    """Response type for generate_random operation."""
    Plaintext: bytes
    EncryptionAlgorithm: str


@dataclass
class KMSKeyMetadata:
    """Metadata for a KMS key."""
    key_id: str
    arn: str
    creation_date: datetime
    description: Optional[str] = None
    enabled: bool = True
    key_state: KeyState = 'Enabled'
    deletion_date: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    origin: OriginType = 'AWS_KMS'
    key_manager: KeyManager = 'CUSTOMER'
    customer_master_key_spec: CustomerMasterKeySpec = 'SYMMETRIC_DEFAULT'
    key_usage: KeyUsage = 'ENCRYPT_DECRYPT'
    encryption_algorithms: List[str] = None

    @classmethod
    def from_response(cls, response: Dict) -> 'KMSKeyMetadata':
        """Create a KMSKeyMetadata instance from an API response.

        Args:
            response: API response containing key metadata

        Returns:
            KMSKeyMetadata instance
        """
        metadata = response['KeyMetadata']
        return cls(
            key_id=metadata['KeyId'],
            arn=metadata['Arn'],
            creation_date=metadata['CreationDate'],
            description=metadata.get('Description'),
            enabled=metadata.get('Enabled', True),
            key_state=metadata.get('KeyState', 'Enabled'),
            deletion_date=metadata.get('DeletionDate'),
            valid_to=metadata.get('ValidTo'),
            origin=metadata.get('Origin', 'AWS_KMS'),
            key_manager=metadata.get('KeyManager', 'CUSTOMER'),
            customer_master_key_spec=metadata.get(
                'CustomerMasterKeySpec', 'SYMMETRIC_DEFAULT'),
            key_usage=metadata.get('KeyUsage', 'ENCRYPT_DECRYPT'),
            encryption_algorithms=metadata.get('EncryptionAlgorithms')
        )


@dataclass
class EncryptionContext:
    """Encryption context for KMS operations."""
    context: Dict[str, str]

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the encryption context
        """
        return self.context


@dataclass
class GrantConstraints:
    """Constraints for KMS grants."""
    encryption_context_subset: Optional[Dict[str, str]] = None
    encryption_context_equals: Optional[Dict[str, str]] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the grant constraints
        """
        constraints = {}
        if self.encryption_context_subset:
            constraints['EncryptionContextSubset'] = self.encryption_context_subset
        if self.encryption_context_equals:
            constraints['EncryptionContextEquals'] = self.encryption_context_equals
        return constraints


@dataclass
class Tag:
    """Tag for KMS resources."""
    key: str
    value: str

    def to_dict(self) -> Dict[str, str]:
        """Convert to dictionary format for API calls.

        Returns:
            Dictionary representation of the tag
        """
        return {
            'TagKey': self.key,
            'TagValue': self.value
        }
