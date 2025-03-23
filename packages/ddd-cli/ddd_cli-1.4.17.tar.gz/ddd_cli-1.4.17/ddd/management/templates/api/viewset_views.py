from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status

# Importar servicios que encapsulan la lógica de negocio
from [[ app_name.lower() ]].domain.services import (
    create_[[ entity_name.lower() ]],
    retrieve_[[ entity_name.lower() ]],
    update_[[ entity_name.lower() ]],
    delete_[[ entity_name.lower() ]]
)

# Importar el repositorio para interactuar con la infraestructura
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository

class [[ entity_name.capitalize() ]]ViewSet(ViewSet):
    """
    ViewSet para manejar operaciones CRUD relacionadas con [[ entity_name.lower() ]].
    
    Este ViewSet interactúa con:
    - Los servicios del dominio para manejar la lógica de negocio.
    - Los repositorios para acceder a la capa de persistencia.
    """

    def list(self, request):
        """
        Endpoint para obtener una lista de todos los [[ entity_name.lower() ]].
        
        - Se valida y adapta la solicitud.
        - Se utiliza el servicio `retrieve_[[ entity_name.lower() ]]` para manejar la lógica.
        """
        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio para recuperar todos los registros
            result = retrieve_[[ entity_name.lower() ]](repository=repository)

            # Retornar los datos serializados con un estado HTTP 200 OK
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            # Manejar errores de lógica de negocio
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def retrieve(self, request, pk=None):
        """
        Endpoint para obtener un [[ entity_name.lower() ]] específico por su ID (pk).
        
        - Valida y adapta la solicitud al dominio.
        - Utiliza el servicio `retrieve_[[ entity_name.lower() ]]` para manejar la lógica.
        """
        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio para recuperar un registro específico
            result = retrieve_[[ entity_name.lower() ]](repository=repository, id=pk)

            # Retornar el resultado con un estado HTTP 200 OK
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            # Manejar errores si el registro no existe
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        """
        Endpoint para crear un nuevo [[ entity_name.lower() ]].
        
        - Valida y adapta los datos entrantes.
        - Llama al servicio `create_[[ entity_name.lower() ]]` para manejar la creación.
        """
        data = request.data  # Obtener los datos del cuerpo de la solicitud

        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio para crear el registro
            result = create_[[ entity_name.lower() ]](repository=repository, **data)

            # Retornar el resultado con un estado HTTP 201 CREATED
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            # Manejar errores en las reglas de negocio o validación
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """
        Endpoint para actualizar un [[ entity_name.lower() ]] existente.
        
        - Valida y adapta los datos entrantes.
        - Llama al servicio `update_[[ entity_name.lower() ]]` para manejar la actualización.
        """
        data = request.data  # Obtener los datos del cuerpo de la solicitud

        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio para actualizar el registro
            result = update_[[ entity_name.lower() ]](repository=repository, id=pk, **data)

            # Retornar el resultado con un estado HTTP 200 OK
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            # Manejar errores en las reglas de negocio o validación
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """
        Endpoint para eliminar un [[ entity_name.lower() ]] existente.
        
        - Valida y adapta la solicitud.
        - Llama al servicio `delete_[[ entity_name.lower() ]]` para manejar la eliminación.
        """
        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio para eliminar el registro
            result = delete_[[ entity_name.lower() ]](repository=repository, id=pk)

            # Retornar un estado HTTP 204 NO CONTENT para confirmar la eliminación
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            # Manejar errores si el registro no existe o no se puede eliminar
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

