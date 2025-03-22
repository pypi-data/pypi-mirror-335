# region Import Packages

from Models.BaseModel.BaseModel import *
from Logix.DbManager.DbManager import db

# endregion

# region TestUnits Table

class TestUnits(BaseModel, db.Model):

    __tablename__ = "TestUnits"

    Id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UnitId = db.Column(db.String(300), unique=True)
    UnitName = db.Column(db.String(300), unique=True)
    UserId = db.Column(db.String(300))
    Description = db.Column(db.String(1000))
    CreatedBy = db.Column(db.String(300))
    CreatedAt = db.Column(db.String(30))
    ChangedBy = db.Column(db.String(300))
    ChangedAt = db.Column(db.String(30))
    Revision = db.Column(db.Integer)
    DeleteFlag = db.Column(db.Integer)

    def __init__(self, UserId, UnitId, UnitName, Description, CreatedBy, CreatedAt, ChangedBy, ChangedAt, Revision, DeleteFlag):

        self.UserId = UserId
        self.UnitId = UnitId
        self.UnitName = UnitName
        self.Description = Description
        self.CreatedBy = CreatedBy
        self.CreatedAt = CreatedAt
        self.ChangedBy = ChangedBy
        self.ChangedAt = ChangedAt
        self.Revision = Revision
        self.DeleteFlag = DeleteFlag
    
    def to_dict(self):
        
        return {prop: getattr(self, prop) for prop in dir(self) if not prop.startswith('_') and not callable(getattr(self, prop))}

# endregion
