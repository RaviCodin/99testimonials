from abc import ABC, abstractmethod


class Crawler(ABC):

    @abstractmethod
    def get_info_and_create_testimonial(self):
        pass
