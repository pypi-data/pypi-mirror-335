from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Importar servicios del dominio que contienen la lógica de negocio
from [[ app_name.lower() ]].domain.services import (
    create_[[ entity_name.lower() ]],
    retrieve_[[ entity_name.lower() ]],
    update_[[ entity_name.lower() ]],
    delete_[[ entity_name.lower() ]]
)

# Importar el repositorio que maneja la interacción con la infraestructura
from [[ app_name.lower() ]].infrastructure.[[ entity_name.lower() ]]_repository import [[ entity_name.capitalize() ]]Repository

class [[ entity_name.capitalize() ]]APIView(APIView):
    """
    API para manejar operaciones CRUD relacionadas con [[ entity_name.lower() ]].

    Este APIView interactúa con:
    - Servicios del dominio que encapsulan la lógica de negocio.
    - Repositorios que interactúan con la capa de persistencia.
    """

    def get(self, request, id=None):
        """
        Maneja solicitudes GET para recuperar uno o todos los registros.

        - Si se proporciona `id`, recupera un registro específico.
        - Si no se proporciona `id`, recupera todos los registros.
        """
        if id:
            # Recuperar un registro específico por ID
            try:
                # Instanciar el repositorio para acceder a los datos
                repository = [[ entity_name.capitalize() ]]Repository()

                # Llamar al servicio de recuperación para una entidad específica
                result = retrieve_[[ entity_name.lower() ]](repository=repository, id=id)

                # Retornar la respuesta con un estado HTTP 200 OK
                return Response(result, status=status.HTTP_200_OK)
            except ValueError as e:
                # Manejar errores si no se encuentra el registro
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Recuperar todos los registros
            try:
                repository = [[ entity_name.capitalize() ]]Repository()

                # Llamar al servicio para listar todas las entidades
                result = retrieve_[[ entity_name.lower() ]](repository=repository)

                # Retornar la respuesta con un estado HTTP 200 OK
                return Response(result, status=status.HTTP_200_OK)
            except ValueError as e:
                # Manejar errores si no se encuentran registros
                return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    def post(self, request):
        """
        Maneja solicitudes POST para crear un nuevo registro.

        - Valida los datos entrantes.
        - Llama al servicio de creación para manejar la lógica de negocio.
        """
        data = request.data  # Datos enviados en el cuerpo de la solicitud

        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio de creación con los datos proporcionados
            result = create_[[ entity_name.lower() ]](repository=repository, **data)

            # Retornar la respuesta con un estado HTTP 201 CREATED
            return Response(result, status=status.HTTP_201_CREATED)
        except ValueError as e:
            # Manejar errores relacionados con las reglas de negocio
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, id):
        """
        Maneja solicitudes PUT para actualizar un registro existente.

        - Valida los datos entrantes.
        - Llama al servicio de actualización para manejar la lógica de negocio.
        """
        data = request.data  # Datos enviados en el cuerpo de la solicitud

        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio de actualización con el ID y los nuevos datos
            result = update_[[ entity_name.lower() ]](repository=repository, id=id, **data)

            # Retornar la respuesta con un estado HTTP 200 OK
            return Response(result, status=status.HTTP_200_OK)
        except ValueError as e:
            # Manejar errores relacionados con las reglas de negocio
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        """
        Maneja solicitudes DELETE para eliminar un registro existente.

        - Valida el ID proporcionado.
        - Llama al servicio de eliminación para manejar la lógica de negocio.
        """
        try:
            # Instanciar el repositorio
            repository = [[ entity_name.capitalize() ]]Repository()

            # Llamar al servicio de eliminación con el ID proporcionado
            result = delete_[[ entity_name.lower() ]](repository=repository, id=id)

            # Retornar una respuesta sin contenido con estado HTTP 204 NO CONTENT
            return Response(result, status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            # Manejar errores relacionados con las reglas de negocio o ID inexistente
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
