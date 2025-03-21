# File cleanup

With the exception for some globally defined file_patterns (e.g. debug images, log rotation files) every service is responsible for the cleanup of its files.
The helper function `schedule_file_cleanup` schedules a file cleanup at 2:xx local time, where xx is service name dependent to avoid that all services delete at the same time.
Important notes:
* only files will be deleted, directories are kept
* files are only deleted once per day
* files are deleted based on modified timestamp
* a scheduler must be used which does `.run_pending()` regularly
* as glob is only inclusive, an exclude regex can be specified for special cases


## Examples

```python
import time
import re
import schedule
from datetime import timedelta
from openmodule.utils.cleanup import schedule_file_cleanup

scheduler = schedule.Scheduler()

# delete specific file after 30 days
schedule_file_cleanup(scheduler, "/data/file_to_keep_30_days.txt", timedelta(days=30))

# delete png files in folder after 1 day
schedule_file_cleanup(scheduler, "/data/images/*.png", timedelta(days=1))

# delete jpg files in subfolders after 30 days
schedule_file_cleanup(scheduler, "/data/*/*.jpg", timedelta(days=30))

# delete jpg files in subfolders recursively after 30 days (e.g. /data/a.jpg, /data/d1/a.jpg, /data/d1/d2/a.jpg)
schedule_file_cleanup(scheduler, "/data/**/*.jpg", timedelta(days=30))

# delete jpg files in subfolders, except if regex matches, recursively after 30 days (e.g. /data/d1/a.jpg, but not /data/vehicle_images/a.jpg)
schedule_file_cleanup(scheduler, "/data/**/*.jpg", timedelta(days=30), re.compile('.*/vehicle_images/.*'))

while True:
    scheduler.run_pending()
    time.sleep(1.0)
```
