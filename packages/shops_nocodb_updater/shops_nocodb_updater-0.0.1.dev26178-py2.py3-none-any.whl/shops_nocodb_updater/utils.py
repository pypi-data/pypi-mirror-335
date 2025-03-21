import logging


from shops_nocodb_updater.models.base import AttachmentObject

logger = logging.getLogger(__name__)


async def get_language_from_project(client) -> str:
    """
    Determine the language of the NocoDB project by looking at the table names.
    
    Args:
        client: NocoDB client
        
    Returns:
        Language code ("EN" or "RU")
    """
    table_names = []
    project_metadata = await client.get_project_metadata()
    for table in project_metadata["list"]:
        table_names.append(table["title"])
    if "Категории" in table_names:
        return "RU"
    elif "Categories" in table_names:
        return "EN"
    else:
        raise Exception(f"No language found in project {client.project_id}")

def needs_update(client, existing_record, new_data, schema, skip_update_column_names):
    """
    Check if a record needs to be updated.
    
    Args:
        existing_record: Existing record
        new_data: New data
        
    Returns:
        True if update is needed, False otherwise
    """
    for key, value in new_data.items():
        value_target_type = schema.get(key)
        if key in skip_update_column_names:
            continue
        elif not value_target_type:
            raise ValueError(f"Field {key} not found in schema! -> {schema}")
        elif key in existing_record:
            if value_target_type == AttachmentObject:
                logger.debug(f"Update attachment {existing_record[key]} -> {value} ???")
                if existing_record[key] and not value:
                    logger.debug(f"Update attachment {key} {existing_record[key]} -> {value}")
                    return True
                for i, attachment in enumerate(value):
                    if not client.is_duplicate_attachment(
                        existing_record[key][i],
                        attachment
                    ):
                        logger.debug(f"Update attachment {key} {existing_record[key]} -> {value}")
                        return True
                logger.debug(f"Duplicate attachment found for {key}, skipping update")
            elif key in existing_record and existing_record[key] != value:
                logger.debug(f"Record needs to be updated for {key} {existing_record[key]} -> {value}")
                return True
    return False 