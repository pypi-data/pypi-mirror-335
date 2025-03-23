@dataclass
class [[ entity_name.capitalize() ]]Entity:
    """
    Entidad del dominio para [[ entity_name.lower() ]].

    Esta clase representa la lógica de negocio central y las reglas asociadas 
    con [[ entity_name.lower() ]] en el sistema.
    """
    #campos id
    id: Optional[int] = None  # ID relacionado con la base de datos
    uuid: Optional[UUID] = None

    name: str  # Nombre obligatorio
    description: Optional[str] = None  # Descripción opcional
    created_at: Optional[str] = None  # Fecha de creación (puede ser ISO 8601)

    def __post_init__(self):
        self.validate()   

    def validate(self) -> None:
        """
        Valida la entidad antes de guardar o procesar.
        Lanza excepciones si las reglas de negocio no se cumplen.
        - Consistencia interna de los atributos
        - Validaciones intrínsecas al momento de creación/modificación
        """
        if not self.name or len(self.name) < 3:
            raise ValueError("El nombre debe tener al menos 3 caracteres.")
        if self.description and len(self.description) > 500:
            raise ValueError("La descripción no puede superar los 500 caracteres.")

    def update(self, data:dict) -> None:
        """
        Actualiza los atributos de la entidad con valores nuevos.
        """
        # Actualizar cada campo proporcionado en 'data'
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)

        self.validate()

    def to_dict(self) -> dict:
        """
        Convierte la entidad a un diccionario.
        """
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> "[[ entity_name.capitalize() ]]Entity":
        """
        Crea una instancia de la entidad a partir de un diccionario.
        """
        return [[ entity_name.capitalize() ]]Entity(**data)
