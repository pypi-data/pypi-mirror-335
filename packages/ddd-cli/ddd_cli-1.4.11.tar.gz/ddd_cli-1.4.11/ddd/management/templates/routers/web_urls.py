from django.urls import path

from . import [[ entity_name.lower() ]]_views

urlpatterns = [
    
    path('[[ entity_name.lower() ]]-list/', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_list, name="[[ entity_name.lower() ]]_list"),
    path('[[ entity_name.lower() ]]-create/', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_create, name="[[ entity_name.lower() ]]_create"),
    path('[[ entity_name.lower() ]]-edit/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_edit, name="[[ entity_name.lower() ]]_edit"),    
    path('[[ entity_name.lower() ]]-save/', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_save, name="[[ entity_name.lower() ]]_save"),
    path('[[ entity_name.lower() ]]-edit-save/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_edit_save, name="[[ entity_name.lower() ]]_edit_save"),
    path('[[ entity_name.lower() ]]-detail/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_detail, name="[[ entity_name.lower() ]]_detail"),
    path('[[ entity_name.lower() ]]-delete/<int:id>', [[ entity_name.lower() ]]_views.[[ entity_name.lower() ]]_delete, name="[[ entity_name.lower() ]]_delete"),    

]
