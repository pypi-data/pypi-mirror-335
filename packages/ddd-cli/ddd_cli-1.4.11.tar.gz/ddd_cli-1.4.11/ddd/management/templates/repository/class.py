from typing import List, Optional
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.db.models import Q

# importa las entidades utilizadas aqui
from ..models import [[ entity_name.capitalize() ]]
from .mappers import Mapper
from ..domain.entities import [[ entity_name.capitalize() ]]Entity

class [[ entity_name.capitalize() ]]Repository:
    """
    Repositorio para manejar la persistencia de datos de la entidad: [[ entity_name.lower() ]].
    
    Este repositorio incluye:
    - Validación de existencia de registros.
    - Control de unicidad.
    - Métodos básicos.
    """

    @staticmethod
    def get_all(filters: Optional[dict] = None) -> List[ [[ entity_name.capitalize() ]]Entity ]:
        """
        Obtiene todos los registros de la entidad.
        :return: Lista de registros de la entidad.
        """

        instance_list = [[ entity_name.capitalize() ]].objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])        

        # Convertir a entidades usando el Mapper genérico
        return [Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity) for instance in instance_list]        

    @staticmethod
    def get_by_id(id) -> [[ entity_name.capitalize() ]]Entity:
        """
        Obtiene un registro por su ID.
        
        :param id: ID del registro a recuperar.
        :return: El registro encontrado o None si no existe.
        """

        try:
            instance = [[ entity_name.capitalize() ]].objects.get(id=id)
            return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)

        except [[ entity_name.capitalize() ]].DoesNotExist:
            return None

    @staticmethod
    def exists_by_field(field_name, value) -> bool:
        """
        Verifica si existe un registro con un valor específico para un campo dado.

        :param field_name: Nombre del campo a buscar.
        :param value: Valor del campo a verificar.
        :return: True si existe un registro con el valor dado, False en caso contrario.
        """

        return [[ entity_name.capitalize() ]].objects.filter(**{field_name: value}).exists()

    @staticmethod
    def count_all(filters: Optional[dict] = None) -> int:
        """
        Cuenta registros que cumplen con ciertas condiciones.

        :param conditions: Condiciones de filtro como clave-valor.
        :return: Número de registros que cumplen las condiciones.
        """

        instance_list = [[ entity_name.capitalize() ]].objects.all()    

        # Aplicar filtros si se proporcionan
        if filters:
            if "nombre" in filters and filters["nombre"] != "":
                instance_list = instance_list.filter(nombre__icontains=filters["nombre"])            

        return instance_list.count()            

    @staticmethod
    def create(data) -> [[ entity_name.capitalize() ]]Entity:
        """
        Crea un nuevo registro.

        :param data: Diccionario con los datos necesarios para crear el registro.
        :return: La instancia creada.
        :raises ValidationError: Si los datos no son válidos.
        """

        # Eliminar las claves 'id' y 'uuid' si existen en el diccionario
        data.pop('id', None)
        data.pop('uuid', None)        

        # Crear el registro
        instance = [[ entity_name.capitalize() ]](**data)

        # Validar antes de guardar
        try:
            instance.full_clean()  # Validaciones del modelo
            instance.save()
        except ValidationError as e:
            raise ValidationError(f"Validation Error: {e.message_dict}")
        
        return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)

    @staticmethod
    def update(id, data) -> [[ entity_name.capitalize() ]]Entity:
        """
        Actualiza un registro existente.

        :param id: ID del registro a actualizar.
        :param data: Diccionario con los datos a actualizar.
        :return: La instancia actualizada.
        :raises ObjectDoesNotExist: Si no existe el registro con el ID dado.
        :raises ValidationError: Si los datos no son válidos.
        """

        # Eliminar las claves 'id' y 'uuid' si existen en el diccionario
        data.pop('id', None)
        data.pop('uuid', None)

        try:
            instance = [[ entity_name.capitalize() ]].objects.get(id=id)

            # Actualizar cada campo proporcionado en 'data'
            for key, value in data.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)

            # Validar la instancia antes de guardar
            instance.full_clean()  # Esto ejecuta las validaciones del modelo
            instance.save()  # Guarda los cambios en la base de datos
            
            return Mapper.model_to_entity(instance, [[ entity_name.capitalize() ]]Entity)

        except [[ entity_name.capitalize() ]].DoesNotExist:
            raise ObjectDoesNotExist(f"No [[ entity_name.lower() ]] found with ID {id}")

        except ValidationError as e:
            raise ValidationError(f"Validation Error: {e.message_dict}")

    @staticmethod
    def delete(id) -> bool:
        """
        Elimina un registro por su ID.

        :param id: ID del registro a eliminar.
        :raises ObjectDoesNotExist: Si no existe el registro con el ID dado.
        """

        try:
            instance = [[ entity_name.capitalize() ]].objects.get(id=id)
            instance.delete()
            return True

        except [[ entity_name.capitalize() ]].DoesNotExist:
            raise ObjectDoesNotExist(f"No [[ entity_name.lower() ]] found with ID {id}")


