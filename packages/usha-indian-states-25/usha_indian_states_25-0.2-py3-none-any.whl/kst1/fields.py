from django.db import models
from .states import INDIAN_STATES

class StateField(models.CharField):
    def __init__(self,*args,**kwargs):
        kwargs["max_length"] = 2  
        kwargs["choices"] = INDIAN_STATES
        super().__init__(*args,**kwargs)  
