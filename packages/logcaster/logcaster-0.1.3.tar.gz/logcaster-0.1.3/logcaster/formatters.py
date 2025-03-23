import logging


class BaseFormatter(logging.Formatter):
    def __init__(self, include_fields: list[str] = None, exclude_fields: list[str] = None, *args, **kwargs):
        assert not (include_fields and exclude_fields), "`include_fields` and `exclude_fields` are exclusionary"

        super().__init__(*args, **kwargs)
        self.include_fields = include_fields or ['__all__']
        self.exclude_fields = exclude_fields or []
        

    def _get_fields(self, record: logging.LogRecord) -> dict:
        record.message = record.getMessage()
        record.asctime = self.formatTime(record, self.datefmt)
        
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)

        record_dict = record.__dict__

        if self.include_fields == ['__all__']:
            self.include_fields = [k for k in record.__dict__.keys() if k not in self.exclude_fields]
        
        elif self.include_fields:
            return {key: value for key, value in record_dict.items() if key in self.include_fields}
        
        return {key: value for key, value in record_dict.items() if key not in self.exclude_fields}


__all__ = ['BaseFormatter']
