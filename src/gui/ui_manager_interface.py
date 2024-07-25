from gui.ui_element_interface import UIElementInterface
from pygame.event import Event
from abc import abstractmethod, ABCMeta

class UIManagerInterface(metaclass=ABCMeta):
    @abstractmethod
    def get_window_size(self) -> tuple[int, int]:
        pass
    
    @abstractmethod
    def add_element(self, element: UIElementInterface) -> None:
        pass
    
    @abstractmethod
    def remove_element(self, element: UIElementInterface) -> None:
        pass

    @abstractmethod
    def clear_elements_list(self) -> None:
        pass

    @abstractmethod
    def ask_refresh(self, element: UIElementInterface|None=None) -> None:
        pass

    @abstractmethod
    def display(self) -> None:
        pass
    
    @abstractmethod
    def get_hovered_element(self) -> UIElementInterface|None:
        pass

    @abstractmethod
    def process_event(self, event: Event) -> None:
        pass         

    @abstractmethod
    def update(self) -> None:
        """
        Refresh the window if needed and creates events (click, hover)
        """
        pass
