# Birth date
# Name
# Diagnosis
# Symptops
# Triggers
# Emergency contacts
# What is calming

import datetime
import simplejson

class EmergencyContact:
    def __init__(self):
        self._phone_numbers = []
        self._name = []
    @property
    def phone_numbers(self):
        return self._phone_numbers
    @property
    def name(self):
        return self._name
    def set_name(self, name: str):
        assert type(name) == str
    def set_numbers(self, numbers: list[str]):
        assert type(numbers) == list
    @property
    def asdict(self):
        return {
            "phone_numbers": self._phone_numbers,
            "name": self._name
        }

class JsonLData:
    def __init__(self):
        self._birthdate = None
        self._name = ""
        self._diagnosis = ""
        self._symptoms = []
        self._guardians = []
        self._e_contacts = []
        self._techniques = []   

    @property
    def birthdate(self):
        return self._birthdate
    @property
    def name(self):
        return self._name
    @property
    def diagnosis(self):
        return self._diagnosis
    @property
    def symptoms(self):
        return self._symptoms
    @property
    def guardians(self):
        return self._guardians
    @property
    def e_contacts(self):
        return self._e_contacts
    @property
    def techniques(self):
        return self._techniques
    @property
    def asdict(self):
        return {
            "dateofbirth": self._birthdate,
            "name": self._name,
            "diagnosis": self._diagnosis,
            "guardians": self._guardians,
            "symptoms": self._symptoms,
            "emergency_contacts": [i.asdict for i in self._e_contacts],
            "working_calming_techniques": self.techniques
        }
    
    def set_birthdate(self, birthdate: datetime.date):
        assert type(birthdate) == datetime.date
        self._birthdate = birthdate
    
    def set_name(self, name: str):
        assert type(name) == str
        self._name = name
    
    def set_diagnosis(self, diagnosis: str):
        assert type(diagnosis) == str
        self._diagnosis = diagnosis
    
    def set_symptoms(self, symptoms: list[str]):
        assert type(symptoms) == list
        self._symptoms = symptoms
    
    def set_e_contacts(self, e_contacts: list[EmergencyContact]):
        assert type(e_contacts) == list
        self._e_contacts = e_contacts
    
    def set_techniques(self, techniques: list[str]):
        assert type(techniques) == list
        self._techniques = techniques
    
    def set_guardians(self, guardians: list[str]):
        assert type(guardians) == list
        self._guardians = guardians

    def save(self, filename: str):
        with open(filename, "w+")as f:
            simplejson.dump(self.__repr__(), f)

    def __repr__(self):
        simplejson.dumps(self.asdict)

    def __str__(self):
        return self.__repr__()