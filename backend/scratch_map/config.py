import os


# Resolution 10 is a walking-scale cell. It is intentionally configured in
# one place so changing it never requires changing discovery business logic.
H3_RESOLUTION = int(os.getenv('SCRATCH_MAP_H3_RESOLUTION', '10'))
