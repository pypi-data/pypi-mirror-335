import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from generic_crud import GenericCRUD
from generic_crud_ml import GenericCRUDML
DEFAULT_LIMIT = 5
DEFAULT_ORDER_BY = "updated_timestamp DESC"
LOGGER_MINIMUM_SEVERITY="Info"

class MergeEntities (GenericCRUDML):
    def merge_entities(self, entity_id1: int, entity_id2: int, main_entity_ml_id: int = None):
        gcrml = GenericCRUDML(default_schema_name='location', default_ml_table_name='city_ml_table',is_test_data=True, default_table_name='city_table', default_ml_view_table_name='city_ml_view', )
        # establish which id is being merged/ended and which one it is being merged into
        end_id = entity_id1
        main_id = entity_id2



        # look for the former in id of city_ml_table and replace it with the latter

        # Data to update
        old_id = end_id
        new_id = main_id
        mlids = gcrml.get_all_ml_ids_by_id(table_id=old_id,ml_column_name='city_ml_id',order_by=DEFAULT_ORDER_BY, ml_table_name='city_ml_table', column_name='city_id', compare_view_name='city_ml_view')
                # Set the main id
        if main_entity_ml_id is not None:
            gcrml.update_by_column_and_value(
                table_name='city_ml_table',
                column_name='city_ml_id',
                column_value=main_entity_ml_id,
                data_dict={'is_main': True },)
        for id in mlids:
            name = gcrml.select_one_value_by_column_and_value(
                select_clause_value = 'title',
                schema_name='location',
                view_table_name='city_ml_view',
                column_name='city_ml_id',
                column_value=id,

            )
            gcrml.update_by_column_and_value(
                table_name='city_ml_table',
                column_name='city_ml_id',
                column_value=id,
                data_dict={"city_id": new_id,}
            )

        gcrml.update_by_column_and_value(
        table_name="city_table",
        column_name="city_id",
        column_value=old_id,
        data_dict={"end_timestamp": datetime.datetime.now()},
    )














