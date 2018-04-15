import builtins

import models
builtins.models = models

from models.candidate import Candidate

__all__ = [Candidate]
