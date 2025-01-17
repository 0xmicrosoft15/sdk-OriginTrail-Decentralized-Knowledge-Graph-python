from dkg.modules.module import Module
from dkg.managers.manager import RequestManager


class BlockchainService(Module):
    def __init__(self, manager: RequestManager):
        self.manager = manager
