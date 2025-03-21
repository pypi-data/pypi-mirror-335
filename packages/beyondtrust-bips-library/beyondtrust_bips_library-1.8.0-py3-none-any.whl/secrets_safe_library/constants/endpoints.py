"""
Endpoints list used in Integration Library (verb:endpoint)
"""

# Secrets
GET_SECRETS_SAFE_SECRETS = "get:secrets-safe/secrets"
GET_SECRETS_SAFE_SECRETS_SECRETID = "get:secrets-safe/secrets/{secretid}"
GET_SECRETS_SAFE_SECRETS_SECRETID_TEXT = "get:secrets-safe/secrets/{secretid}/text"
GET_SECRETS_SAFE_SECRETS_SECRETID_FILE = "get:secrets-safe/secrets/{secretid}/file"
GET_SECRETS_SAFE_FOLDERS_FOLDERID_SECRETS = (
    "get:secrets-safe/folders/{folderid}/secrets"
)
GET_SECRETS_SAFE_FOLDERS_FOLDERID_TEXT = "get:secrets-safe/folders/{folderid}/text"
GET_SECRETS_SAFE_FOLDERS_FOLDERID_FILE = "get:secrets-safe/folders/{folderid}/file"
POST_SECRETS_SAFE_FOLDERS_FOLDERID = "post:secrets-safe/folders/{folderid}/secrets"
POST_SECRETS_SAFE_FOLDERS_FOLDERID_TEXT = (
    "post:secrets-safe/folders/{folderid}/secrets/text"
)
POST_SECRETS_SAFE_FOLDERS_FOLDERID_FILE = (
    "post:secrets-safe/folders/{folderid}/secrets/file"
)
PUT_SECRETS_SAFE_SECRETS_SECRETID = "put:secrets-safe/secrets/{secretid}"
PUT_SECRETS_SAFE_SECRETS_SECRETID_TEXT = "put:secrets-safe/secrets/{secretid}/text"
PUT_SECRETS_SAFE_SECRETS_SECRETID_FILE = "put:secrets-safe/secrets/{secretid}/file"

# Folders
GET_SECRETS_SAFE_FOLDERS = "get:secrets-safe/folders"
GET_SECRETS_SAFE_FOLDERS_FOLDERID = "get:secrets-safe/folders/{folderid}"

# Managed Systems
GET_MANAGED_SYSTEMS = "get:managedsystems"
GET_MANAGED_SYSTEMS_MANAGEDSYSTEMID = "get:managedsystems/managedsystemid"
GET_MANAGED_SYSTEMS_ASSETID = "get:assets/assetid/managedsystems"
GET_MANAGED_SYSTEMS_DATABASEID = "get:databases/databaseid/managedsystems"
GET_MANAGED_SYSTEMS_FUNCTIONALACCOUNTID = (
    "get:functionalaccounts/functionalaccountid/managedsystems"
)
GET_MANAGED_SYSTEMS_WORKGROUPID = "get:workgroups/workgroupid/managedsystems"

# Safes
GET_SECRETS_SAFE_SAFES = "get:secrets-safe/safes"
GET_SECRETS_SAFE_SAFES_ID = "get:secrets-safe/safes/{ID}"
