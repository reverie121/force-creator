from app import app, db
from models import SavedList, PdfGeneration, UsageEvent, ArtilleryComponent, CharacterComponent, ShipComponent, UnitComponent, CustomComponent
import logging
import sys

# Configure logging
logging.basicConfig(filename='cleanup.log', level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

def cleanup_temp_lists():
    """Remove temporary SavedList records with list_status='pdf' that are not referenced."""
    with app.app_context():
        try:
            temp_lists = SavedList.query.filter_by(list_status='pdf').all()
            logging.info(f"Found {len(temp_lists)} temporary lists with list_status='pdf'")
            print(f"Found {len(temp_lists)} temporary lists with list_status='pdf'")
            
            deleted_count = 0
            for temp_list in temp_lists:
                pdf_ref = PdfGeneration.query.filter_by(list_uuid=temp_list.uuid).first()
                usage_ref = UsageEvent.query.filter_by(list_uuid=temp_list.uuid).first()
                
                if not pdf_ref and not usage_ref:
                    logging.info(f"Deleting temporary list: {temp_list.uuid}")
                    print(f"Deleting temporary list: {temp_list.uuid}")
                    
                    ArtilleryComponent.query.filter_by(list_uuid=temp_list.uuid).delete()
                    CharacterComponent.query.filter_by(list_uuid=temp_list.uuid).delete()
                    ShipComponent.query.filter_by(list_uuid=temp_list.uuid).delete()
                    UnitComponent.query.filter_by(list_uuid=temp_list.uuid).delete()
                    CustomComponent.query.filter_by(list_uuid=temp_list.uuid).delete()
                    
                    db.session.delete(temp_list)
                    deleted_count += 1
                else:
                    logging.info(f"Skipping list {temp_list.uuid} - still referenced (pdf_ref: {bool(pdf_ref)}, usage_ref: {bool(usage_ref)})")
                    print(f"Skipping list {temp_list.uuid} - still referenced (pdf_ref: {bool(pdf_ref)}, usage_ref: {bool(usage_ref)})")
            
            db.session.commit()
            logging.info(f"Cleanup completed successfully. Deleted {deleted_count} temporary lists.")
            print(f"Cleanup completed successfully. Deleted {deleted_count} temporary lists.")
        except Exception as e:
            db.session.rollback()
            logging.error(f"Error during cleanup: {str(e)}")
            print(f"Error during cleanup: {str(e)}")
            sys.exit(1)

if __name__ == "__main__":
    cleanup_temp_lists()