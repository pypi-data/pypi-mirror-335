
def list_[[ entity_name.lower() ]](repository, filters: Optional[dict] = None) -> List[dict]:
    """
    Lista instancias de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :return: Lista de la entidad.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """

    entity_list = repository.get_all(filters)

    return [entity.to_dict() for entity in entity_list]  


def create_[[ entity_name.lower() ]](repository, data) -> dict:
    """
    Crea una nueva instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param data: Diccionario o DTO con los datos necesarios para crear la instancia.
    :return: La entidad creada.
    :raises ValueError: Si las reglas de negocio no se cumplen.
    """
    # Validación de reglas de negocio (opcional)
    if repository.exists_by_field("email", data['email']):
        raise ValueError("An instance with this email already exists.")

    # Creación en el repositorio
    entity = repository.create(data)
    return entity.to_dict()


def retrieve_[[ entity_name.lower() ]](repository, entity_id) -> dict:
    """
    Recupera una instancia de [[ entity_name.lower() ]] por su ID.

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a recuperar.
    :return: La entidad recuperada.
    :raises ValueError: Si no se encuentra la instancia.
    """
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}.")
    return entity.to_dict()


def update_[[ entity_name.lower() ]](repository, entity_id, data) -> dict:
    """
    Actualiza una instancia existente de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a actualizar.
    :param data: Diccionario o DTO con los datos a actualizar.
    :return: La entidad actualizada.
    :raises ValueError: Si no se encuentra la instancia o las reglas de negocio no se cumplen.
    """
    # Recuperar la entidad
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}.")

    # Actualización en el repositorio
    updated_entity = repository.update(entity_id, data)
    return updated_entity.to_dict()


def delete_[[ entity_name.lower() ]](repository, entity_id) -> bool:
    """
    Elimina una instancia de [[ entity_name.lower() ]].

    :param repository: Repositorio que maneja la persistencia de [[ entity_name.lower() ]].
    :param entity_id: ID de la instancia a eliminar.
    :return: Ninguno.
    :raises ValueError: Si no se encuentra la instancia.
    """
    # Recuperar la entidad
    entity = repository.get_by_id(entity_id)
    if not entity:
        raise ValueError(f"No [[ entity_name.lower() ]] found with ID {entity_id}.")

    # Eliminación en el repositorio
    repository.delete(entity_id)

    return True