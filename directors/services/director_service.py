from .position_service import PositionDataRetrieval
from ..models import Director


def director_context_data() -> dict:
    positions = PositionDataRetrieval().retrieve_all()
    print(positions)
    # staff = StaffDataRetrieval().retrieve_all()

    return {
        # "staff_records": staff,
        "positions":positions,
        "total_positions":positions.count(),
    }
