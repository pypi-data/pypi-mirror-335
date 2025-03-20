from ..models import BaseTransfers

def generate(
    page_number:int,
    limit:int,
    data_count:int,
    total_data:int
) -> BaseTransfers.Payload.Pagination:
    pagination = BaseTransfers.Payload.Pagination(
        page_number=page_number,
        data_count=data_count,
        total_data=total_data,
        total_pages=(total_data // limit) + (1 if total_data % limit > 0 else 0)
    )
    return pagination