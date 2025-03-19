# luke_logger

## how to use :
```bash
pip install luke-logger
```

#### Basic logger :

```python
from logs_operations.logger_setup import setup_logger

logger1 = setup_logger(log_file="logs/logfile_name", log_handler='logger1', backup=15)

logger2 = setup_logger(log_file="logs/logfile2_name", log_handler='logger2', backup=15)

logger1.info("this is written to logfile_name")
logger2.info("this is in logfile2_name")
```

#### Logger with bugsnag : 
```python
from logs_operations.logger_setup import setup_logger

bugsnag_logger = setup_logger(
    log_file="app/logs/app.log",
    log_handler="app-logger",
    bugsnag_config={
        "api_key": "your-bugsnag-api-key",
        "project_root": "app"
    },
    bugsnag_level=logging.WARNING  # Send warning and above to Bugsnag
)
```

#### Add bugsnag handler to other logger : 
```python
from logs_operations.logger_setup import add_bugsnag_to_logger
existing_logger = logger1 ## from above
enhanced_logger = add_bugsnag_to_logger(
    existing_logger,
    bugsnag_config={"api_key": "your-bugsnag-api-key"}
)
```


