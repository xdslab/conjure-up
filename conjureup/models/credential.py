""" Credential Module
"""
from conjureup.juju import get_cloud_types_by_name, get_credential


class BaseCredential:
    """ Base credential for all clouds
    """
    CLOUD_TYPE = None

    def __init__(self, cloud, credential_name):
        self.credential_name = credential_name
        self.cloud = cloud
        self.credential = None
        self.load()

    def load(self):
        try:
            self.credential = get_credential(self.cloud,
                                             self.credential_name)
        except:
            raise Exception(
                "Could not find credential({}) for cloud({})".format(
                    self.credential_name,
                    self.cloud))

    def to_dict(self):
        """ Returns dictionary of credentials
        """
        raise NotImplementedError

    @classmethod
    def check_cloud_type(cls, credential):
        return credential == cls.CLOUD_TYPE


class VSphereCredential(BaseCredential):
    CLOUD_TYPE = 'vsphere'

    def to_dict(self):
        return {'username': self.credential['user'],
                'password': self.credential['password']}


class CredentialManager:
    CREDENTIALS = [VSphereCredential]

    def __init__(self, cloud, credential_name):
        self.credential_name = credential_name
        self.cloud = cloud
        self.credential_obj = self._get_credential_object()

    def get_cloud_type(self, name):
        for name, cloud_type in get_cloud_types_by_name().items():
            if name == self.cloud:
                return cloud_type

    def _get_credential_object(self):
        cloud_type = self.get_cloud_type(self.cloud)
        for credential in self.CREDENTIALS:
            if credential.check_cloud_type(cloud_type):
                return credential(self.cloud,
                                  self.credential_name)

    def to_dict(self):
        return self.credential_obj.to_dict()