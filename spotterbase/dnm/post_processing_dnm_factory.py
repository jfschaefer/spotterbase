from typing import Callable

from spotterbase.dnm.dnm import DnmFactory, DnmMeta, Dnm


class PostProcessingDnmFactory(DnmFactory):
    def __init__(self, main_factory: DnmFactory, post_processor: Callable[[Dnm], Dnm]):
        self.main_factory = main_factory
        self.post_processor = post_processor

    def make_dnm_from_meta(self, dnm_meta: DnmMeta) -> Dnm:
        return self.post_processor(self.main_factory.make_dnm_from_meta(dnm_meta))
