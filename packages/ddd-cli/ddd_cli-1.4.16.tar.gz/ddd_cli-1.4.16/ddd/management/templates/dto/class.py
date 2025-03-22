@dataclass
class [[ dto_name.capitalize() ]]Dto:
    """
    Data Transfer Object para [[ dto_name.lower() ]].

    Este DTO se utiliza para transferir datos entre capas del sistema, 
    como entre la capa de dominio y la capa de infraestructura o vistas.
    """

    # Ejemplo de atributos. Personaliza según tus necesidades.
    id: Optional[int] = None  # ID es opcional al crear un nuevo objeto
    name: str  # Nombre obligatorio
    description: Optional[str] = None  # Descripción opcional

    def __post_init__(self):
        self.validate()       

    def validate(self) -> None:
        """
        Valida los datos del DTO.
        Transporte y validación básica de datos
        - Validaciones centradas en un conjunto específico de datos (integridad de datos)
        - Ejemplo: campos no nulos, longitud mínima
        """

    def to_dict(self) -> dict:
        """
        Convierte el DTO a un diccionario.
        Ideal para serialización.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> "[[ dto_name.capitalize() ]]Dto":
        """
        Crea una instancia del DTO a partir de un diccionario.
        """
        return [[ dto_name.capitalize() ]]Dto(**data)
