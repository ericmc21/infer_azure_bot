# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.schema import Attachment


class PatientDemographics:
    """
      This is our application state. Just a regular serializable Python class.
    """

    def __init__(self, gender_at_birth: str = None, transport: str = None, age: int = 0, age_unit: str = "years"):
        self.gender_at_birth = gender_at_birth
        self.transport = transport
        self.age = age
        self.age_unit = age_unit
